import io
import os
import re
import uuid
from contextlib import asynccontextmanager
from pathlib import Path
from time import perf_counter
from typing import Any

import httpx
import pdfplumber
from docx import Document as DocxDocument
from fastapi import FastAPI, File, Form, HTTPException, Request, UploadFile
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, PointStruct, VectorParams

# ─── Config ───────────────────────────────────────────────────────────────────
QDRANT_HOST = os.getenv("QDRANT_HOST", "qdrant")
QDRANT_PORT = int(os.getenv("QDRANT_PORT", "6333"))
OLLAMA_HOST = os.getenv("OLLAMA_HOST", "ollama")
OLLAMA_PORT = os.getenv("OLLAMA_PORT", "11434")
CHAT_MODEL  = os.getenv("CHAT_MODEL", "llama3.1:8b")
EMBED_MODEL = os.getenv("EMBED_MODEL", "bge-m3")
EMBED_DIM   = int(os.getenv("EMBED_DIM", "1024"))
TOP_K       = int(os.getenv("RAG_TOP_K", "10"))
OLLAMA_BASE = f"http://{OLLAMA_HOST}:{OLLAMA_PORT}"

BASE_DIR   = Path(__file__).resolve().parent
STATIC_DIR = BASE_DIR / "static"

qdrant = QdrantClient(host=QDRANT_HOST, port=QDRANT_PORT)

# ─── Cliente HTTP compartido ──────────────────────────────────────────────────
@asynccontextmanager
async def lifespan(app: FastAPI):
    app.state.http = httpx.AsyncClient(timeout=180)
    yield
    await app.state.http.aclose()

app = FastAPI(title="DA-TICA RAG Web", lifespan=lifespan)
app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")

# ─── Modelos Pydantic ─────────────────────────────────────────────────────────
class CreateCollectionPayload(BaseModel):
    name: str = Field(min_length=2, max_length=64)

class TextUploadPayload(BaseModel):
    collection: str = Field(min_length=2, max_length=64)
    text: str = Field(min_length=1)
    source: str | None = None

class ChatPayload(BaseModel):
    question: str = Field(min_length=1)
    collections: list[str] = Field(default_factory=list)
    model: str | None = None

# ─── Helpers ──────────────────────────────────────────────────────────────────
def normalize_collection_name(raw_name: str) -> str:
    normalized = re.sub(r"[^a-z0-9-]+", "-", raw_name.strip().lower())
    normalized = re.sub(r"-{2,}", "-", normalized).strip("-")
    if len(normalized) < 2:
        raise HTTPException(status_code=400, detail="Nombre de coleccion invalido")
    return normalized


def list_collection_names() -> list[str]:
    return sorted(item.name for item in qdrant.get_collections().collections)


def ensure_collection(name: str) -> str:
    collection = normalize_collection_name(name)
    if collection not in list_collection_names():
        qdrant.create_collection(
            collection_name=collection,
            vectors_config=VectorParams(size=EMBED_DIM, distance=Distance.COSINE),
        )
    return collection


async def embed_text(http: httpx.AsyncClient, text: str) -> list[float]:
    r = await http.post(
        f"{OLLAMA_BASE}/api/embeddings",
        json={"model": EMBED_MODEL, "prompt": text},
        timeout=120,
    )
    r.raise_for_status()
    return r.json()["embedding"]


def is_vague_question(question: str) -> bool:
    cleaned = re.sub(r"\s+", " ", question.strip().lower())
    if len(cleaned) < 18:
        return True
    short_prompts = {"awr", "oracle", "sql", "esperas", "cpu", "memoria", "rendimiento"}
    if cleaned in short_prompts:
        return True
    return len(cleaned.split()) <= 4


async def rewrite_question(http: httpx.AsyncClient, question: str) -> str:
    r = await http.post(
        f"{OLLAMA_BASE}/api/chat",
        json={
            "model": CHAT_MODEL,
            "stream": False,
            "messages": [
                {
                    "role": "system",
                    "content": (
                        "Reescribe preguntas vagas para mejorar busquedas RAG. "
                        "Manten la intencion original. No respondas la pregunta. "
                        "Devuelve una sola pregunta en espanol claro, mas precisa y rica en contexto tecnico. "
                        "No uses comillas, listas ni explicaciones."
                    ),
                },
                {"role": "user", "content": question},
            ],
        },
        timeout=60,
    )
    r.raise_for_status()
    rewritten = r.json()["message"]["content"].strip()
    # FIX: elimina bloques <think> que genera deepseek-r1
    rewritten = re.sub(r"<think>.*?</think>", "", rewritten, flags=re.DOTALL).strip()
    return rewritten or question


def clean_answer_text(text: str) -> str:
    # FIX: elimina bloques <think>...</think> de deepseek-r1
    cleaned = re.sub(r"<think>.*?</think>", "", text, flags=re.DOTALL).strip()
    cleaned = cleaned.replace("\r\n", "\n").replace("\r", "\n")
    cleaned = re.sub(r"[\u2500-\u257F\u4E00-\u9FFF\u3400-\u4DBF]+", "", cleaned)
    cleaned = re.sub(r"[^\S\n]+", " ", cleaned)
    cleaned = re.sub(r"\n{3,}", "\n\n", cleaned)
    return cleaned.strip()


async def call_llm(
    http: httpx.AsyncClient,
    question: str,
    context_blocks: list[dict[str, Any]],
    model: str | None,
) -> str:
    # FIX: respeta el modelo seleccionado en la UI
    selected_model = model or CHAT_MODEL

    snippets = [
        f"[{i}] Coleccion: {b['collection']} | Fuente: {b['source']}\n{b['text']}"
        for i, b in enumerate(context_blocks, 1)
    ]

    # FIX: system prompt especializado en derecho constitucional ecuatoriano
    system_prompt = (
        "Eres un asistente juridico especializado en derecho constitucional ecuatoriano "
        "y derecho internacional de derechos humanos. "
        "Responde SIEMPRE en espanol con precision tecnica y terminologia juridica correcta. "
        "Cita articulos constitucionales, tratados internacionales y jurisprudencia interamericana "
        "que aparezcan en el contexto recuperado. "
        "Da una respuesta extensa, bien desarrollada y util, organizada en parrafos claros. "
        "Si el contexto no contiene informacion suficiente, indicalo claramente "
        "en lugar de generalizar o inventar. "
        "No uses caracteres chinos, simbolos raros, iconos, emojis ni decoracion visual."
    )
    user_prompt = (
        "Contexto recuperado:\n\n"
        + "\n\n".join(snippets)
        + f"\n\nPregunta del usuario:\n{question}"
    )

    r = await http.post(
        f"{OLLAMA_BASE}/api/chat",
        json={
            "model": selected_model,
            "stream": False,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
        },
        timeout=180,
    )
    if r.status_code == 400:
        raise HTTPException(
            status_code=400,
            detail=f"Modelo '{selected_model}' no disponible. Recarga la pagina.",
        )
    r.raise_for_status()
    return clean_answer_text(r.json()["message"]["content"])


def extract_text(file: UploadFile) -> str:
    content = file.file.read()
    filename = (file.filename or "").lower()
    if filename.endswith(".pdf"):
        with pdfplumber.open(io.BytesIO(content)) as pdf:
            return "\n".join(page.extract_text() or "" for page in pdf.pages)
    if filename.endswith(".docx"):
        doc = DocxDocument(io.BytesIO(content))
        return "\n".join(p.text for p in doc.paragraphs)
    return content.decode("utf-8", errors="ignore")


# FIX: chunk size 400/80 para textos juridicos con articulos completos
def chunk_text(text: str, size: int = 400, overlap: int = 80) -> list[str]:
    words = text.split()
    if not words:
        return []
    chunks, i = [], 0
    while i < len(words):
        chunks.append(" ".join(words[i : i + size]))
        i += size - overlap
    return chunks

# ─── Rutas ────────────────────────────────────────────────────────────────────
@app.get("/")
def index() -> FileResponse:
    return FileResponse(STATIC_DIR / "index.html")


@app.get("/api/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.get("/api/models")
async def models(request: Request) -> dict[str, Any]:
    return {"models": [CHAT_MODEL], "default": CHAT_MODEL}


@app.get("/api/collections")
def collections() -> dict[str, list[str]]:
    return {"collections": list_collection_names()}


@app.post("/api/collections")
def create_collection(payload: CreateCollectionPayload) -> dict[str, str]:
    collection = ensure_collection(payload.name)
    return {"ok": "true", "collection": collection}


@app.post("/api/upload")
async def upload_document(
    request: Request,
    collection: str = Form(...),
    file: UploadFile = File(...),
) -> dict[str, Any]:
    http: httpx.AsyncClient = request.app.state.http
    collection_name = ensure_collection(collection)
    text = extract_text(file).strip()
    if not text:
        raise HTTPException(status_code=400, detail="No se pudo extraer texto del archivo")
    chunks = chunk_text(text)
    if not chunks:
        raise HTTPException(status_code=400, detail="El archivo no contiene texto util")

    points: list[PointStruct] = []
    for chunk in chunks:
        vector = await embed_text(http, chunk)
        points.append(PointStruct(
            id=str(uuid.uuid4()),
            vector=vector,
            payload={"text": chunk, "source": file.filename or "archivo", "collection": collection_name},
        ))

    qdrant.upsert(collection_name=collection_name, points=points)
    return {"ok": True, "collection": collection_name, "file": file.filename, "chunks": len(points)}


@app.post("/api/upload-text")
async def upload_text(request: Request, payload: TextUploadPayload) -> dict[str, Any]:
    http: httpx.AsyncClient = request.app.state.http
    collection_name = ensure_collection(payload.collection)
    text = payload.text.strip()
    if not text:
        raise HTTPException(status_code=400, detail="No se recibio texto util")
    chunks = chunk_text(text)
    if not chunks:
        raise HTTPException(status_code=400, detail="El texto no contiene contenido util")

    source_name = (payload.source or "texto-manual").strip() or "texto-manual"
    points: list[PointStruct] = []
    for chunk in chunks:
        vector = await embed_text(http, chunk)
        points.append(PointStruct(
            id=str(uuid.uuid4()),
            vector=vector,
            payload={"text": chunk, "source": source_name, "collection": collection_name},
        ))

    qdrant.upsert(collection_name=collection_name, points=points)
    return {"ok": True, "collection": collection_name, "source": source_name, "chunks": len(points)}


@app.post("/api/chat")
async def chat(request: Request, payload: ChatPayload) -> dict[str, Any]:
    t0 = perf_counter()
    http: httpx.AsyncClient = request.app.state.http

    available = list_collection_names()
    targets = [c for c in (payload.collections or available) if c in available]
    if not targets:
        raise HTTPException(status_code=400, detail="No hay colecciones disponibles")

    question = payload.question.strip()
    if not question:
        raise HTTPException(status_code=400, detail="Pregunta vacia")

    rewrite_ms = 0.0
    retrieval_question = question
    if is_vague_question(question):
        t1 = perf_counter()
        retrieval_question = await rewrite_question(http, question)
        rewrite_ms = round((perf_counter() - t1) * 1000, 2)

    t2 = perf_counter()
    vector = await embed_text(http, retrieval_question)
    embed_ms = round((perf_counter() - t2) * 1000, 2)

    t3 = perf_counter()
    matches: list[dict[str, Any]] = []
    for col in targets:
        for hit in qdrant.search(collection_name=col, query_vector=vector, limit=TOP_K):
            pd = hit.payload or {}
            if pd.get("text"):
                matches.append({
                    "score": hit.score,
                    "collection": pd.get("collection", col),
                    "source": pd.get("source", "sin-fuente"),
                    "text": pd["text"],
                })
    search_ms = round((perf_counter() - t3) * 1000, 2)

    matches.sort(key=lambda x: x["score"], reverse=True)
    top_matches = matches[:TOP_K]

    if not top_matches:
        return {
            "answer": "No encontre informacion relacionada en los documentos cargados.",
            "sources": [],
            "timings_ms": {"rewrite": rewrite_ms, "embed": embed_ms, "search": search_ms, "llm": 0.0, "total": round((perf_counter() - t0) * 1000, 2)},
        }

    t4 = perf_counter()
    answer = await call_llm(http, question, top_matches, payload.model)
    llm_ms = round((perf_counter() - t4) * 1000, 2)

    return {
        "answer": answer,
        "sources": top_matches,
        "timings_ms": {"rewrite": rewrite_ms, "embed": embed_ms, "search": search_ms, "llm": llm_ms, "total": round((perf_counter() - t0) * 1000, 2)},
    }
