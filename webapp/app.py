import io
import os
import re
import uuid
from contextlib import asynccontextmanager
from pathlib import Path
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


QDRANT_HOST = os.getenv("QDRANT_HOST", "qdrant")
QDRANT_PORT = int(os.getenv("QDRANT_PORT", "6333"))
OLLAMA_HOST = os.getenv("OLLAMA_HOST", "ollama")
OLLAMA_PORT = os.getenv("OLLAMA_PORT", "11434")
CHAT_MODEL = os.getenv("CHAT_MODEL", "llama3.2:3b")
EMBED_MODEL = os.getenv("EMBED_MODEL", "bge-m3")
EMBED_DIM = int(os.getenv("EMBED_DIM", "1024"))
TOP_K = int(os.getenv("RAG_TOP_K", "6"))
OLLAMA_BASE = f"http://{OLLAMA_HOST}:{OLLAMA_PORT}"

BASE_DIR = Path(__file__).resolve().parent
STATIC_DIR = BASE_DIR / "static"

qdrant = QdrantClient(host=QDRANT_HOST, port=QDRANT_PORT)


@asynccontextmanager
async def lifespan(app: FastAPI):
    app.state.http = httpx.AsyncClient(timeout=180)
    yield
    await app.state.http.aclose()


app = FastAPI(title="DA-TICA RAG Web", lifespan=lifespan)
app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")


class CreateCollectionPayload(BaseModel):
    name: str = Field(min_length=2, max_length=64)


class ChatPayload(BaseModel):
    question: str = Field(min_length=1)
    collections: list[str] = Field(default_factory=list)
    model: str | None = None


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
    response = await http.post(
        f"{OLLAMA_BASE}/api/embeddings",
        json={"model": EMBED_MODEL, "prompt": text},
        timeout=120,
    )
    response.raise_for_status()
    return response.json()["embedding"]


async def call_llm(
    http: httpx.AsyncClient,
    question: str,
    context_blocks: list[dict[str, Any]],
    model: str | None,
) -> str:
    selected_model = CHAT_MODEL

    snippets = []
    for index, block in enumerate(context_blocks, start=1):
        snippets.append(
            f"[{index}] Coleccion: {block['collection']} | Fuente: {block['source']}\n{block['text']}"
        )

    system_prompt = (
        "Responde en espanol de forma clara y directa. "
        "Usa solo el contexto recuperado. "
        "Si el contexto no alcanza, dilo explicitamente."
    )
    user_prompt = (
        "Contexto recuperado:\n\n"
        + "\n\n".join(snippets)
        + f"\n\nPregunta del usuario:\n{question}"
    )

    response = await http.post(
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
    response.raise_for_status()
    return response.json()["message"]["content"].strip()


def extract_text(file: UploadFile) -> str:
    content = file.file.read()
    filename = (file.filename or "").lower()
    if filename.endswith(".pdf"):
        with pdfplumber.open(io.BytesIO(content)) as pdf:
            return "\n".join(page.extract_text() or "" for page in pdf.pages)
    if filename.endswith(".docx"):
        doc = DocxDocument(io.BytesIO(content))
        return "\n".join(paragraph.text for paragraph in doc.paragraphs)
    return content.decode("utf-8", errors="ignore")


def chunk_text(text: str, size: int = 220, overlap: int = 40) -> list[str]:
    words = text.split()
    if not words:
        return []
    chunks: list[str] = []
    index = 0
    while index < len(words):
        chunks.append(" ".join(words[index : index + size]))
        index += size - overlap
    return chunks


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
        points.append(
            PointStruct(
                id=str(uuid.uuid4()),
                vector=vector,
                payload={
                    "text": chunk,
                    "source": file.filename or "archivo",
                    "collection": collection_name,
                },
            )
        )

    qdrant.upsert(collection_name=collection_name, points=points)
    return {
        "ok": True,
        "collection": collection_name,
        "file": file.filename,
        "chunks": len(points),
    }


@app.post("/api/chat")
async def chat(request: Request, payload: ChatPayload) -> dict[str, Any]:
    http: httpx.AsyncClient = request.app.state.http
    available_collections = list_collection_names()
    target_collections = [
        collection for collection in (payload.collections or available_collections)
        if collection in available_collections
    ]
    if not target_collections:
        raise HTTPException(status_code=400, detail="No hay colecciones disponibles")

    question = payload.question.strip()
    if not question:
        raise HTTPException(status_code=400, detail="Pregunta vacia")

    vector = await embed_text(http, question)
    matches: list[dict[str, Any]] = []
    for collection in target_collections:
        hits = qdrant.search(collection_name=collection, query_vector=vector, limit=TOP_K)
        for hit in hits:
            payload_data = hit.payload or {}
            matches.append(
                {
                    "score": hit.score,
                    "collection": payload_data.get("collection", collection),
                    "source": payload_data.get("source", "sin-fuente"),
                    "text": payload_data.get("text", ""),
                }
            )

    matches = [item for item in matches if item["text"]]
    matches.sort(key=lambda item: item["score"], reverse=True)
    top_matches = matches[:TOP_K]

    if not top_matches:
        return {
            "answer": "No encontre informacion relacionada en los documentos cargados.",
            "sources": [],
        }

    answer = await call_llm(http, question, top_matches, payload.model)
    return {
        "answer": answer,
        "sources": top_matches,
    }
