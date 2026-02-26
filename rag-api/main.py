import os, io, httpx, pdfplumber
from datetime import datetime, timezone, timedelta
from typing import List, Optional
from fastapi import FastAPI, UploadFile, File, Header, HTTPException, Form
from fastapi.responses import JSONResponse
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams, PointStruct
from docx import Document as DocxDocument
from tinydb import TinyDB, Query
import uuid

# ─── Config ───────────────────────────────────────────────────────────────────
ADMIN_TOKEN   = os.getenv("ADMIN_TOKEN", "")
QDRANT_HOST   = os.getenv("QDRANT_HOST", "qdrant")
QDRANT_PORT   = int(os.getenv("QDRANT_PORT", 6333))
OLLAMA_HOST   = os.getenv("OLLAMA_HOST", "ollama")
OLLAMA_PORT   = os.getenv("OLLAMA_PORT", "11434")
EMBED_MODEL   = os.getenv("EMBED_MODEL", "nomic-embed-text")
EMBED_DIM     = 768
TZ_EC         = timezone(timedelta(hours=-5))
DEFAULT_LIMIT = 40

# ─── Clientes ─────────────────────────────────────────────────────────────────
qdrant = QdrantClient(host=QDRANT_HOST, port=QDRANT_PORT)
db     = TinyDB("/app/uploads/clients.json")
Client = Query()

app = FastAPI(title="RAG API — DA-TICA")

# ─── Helpers ──────────────────────────────────────────────────────────────────

def check_admin(token: str):
    if token != f"Bearer {ADMIN_TOKEN}":
        raise HTTPException(status_code=401, detail="Token de admin inválido")

def today_ec() -> str:
    return datetime.now(TZ_EC).strftime("%Y-%m-%d")

def get_client(telegram_id: str) -> Optional[dict]:
    res = db.search(Client.telegram_id == telegram_id)
    if not res:
        return None
    c = res[0]
    # Reset diario automático
    if c.get("ultima_actualizacion") != today_ec():
        db.update({"consultas_hoy": 0, "ultima_actualizacion": today_ec()},
                  Client.telegram_id == telegram_id)
        c["consultas_hoy"] = 0
        c["ultima_actualizacion"] = today_ec()
    return c

async def embed(text: str) -> List[float]:
    async with httpx.AsyncClient(timeout=60) as h:
        r = await h.post(
            f"http://{OLLAMA_HOST}:{OLLAMA_PORT}/api/embeddings",
            json={"model": EMBED_MODEL, "prompt": text}
        )
        r.raise_for_status()
        return r.json()["embedding"]

def ensure_collection(name: str):
    cols = [c.name for c in qdrant.get_collections().collections]
    if name not in cols:
        qdrant.create_collection(
            collection_name=name,
            vectors_config=VectorParams(size=EMBED_DIM, distance=Distance.COSINE)
        )

def extract_text(file: UploadFile) -> str:
    content = file.file.read()
    name = (file.filename or "").lower()
    if name.endswith(".pdf"):
        with pdfplumber.open(io.BytesIO(content)) as pdf:
            return "\n".join(p.extract_text() or "" for p in pdf.pages)
    elif name.endswith(".docx"):
        doc = DocxDocument(io.BytesIO(content))
        return "\n".join(p.text for p in doc.paragraphs)
    else:
        return content.decode("utf-8", errors="ignore")

def chunk_text(text: str, size: int = 500, overlap: int = 50) -> List[str]:
    words, chunks, i = text.split(), [], 0
    while i < len(words):
        chunks.append(" ".join(words[i:i+size]))
        i += size - overlap
    return chunks

# ─── ADMIN endpoints ──────────────────────────────────────────────────────────

@app.post("/admin/upload")
async def upload_document(
    collection: str = Form(...),
    file: UploadFile = File(...),
    authorization: str = Header(...)
):
    check_admin(authorization)
    ensure_collection(collection)
    text   = extract_text(file)
    chunks = chunk_text(text)
    points = []
    for chunk in chunks:
        vec = await embed(chunk)
        points.append(PointStruct(
            id=str(uuid.uuid4()),
            vector=vec,
            payload={"text": chunk, "source": file.filename, "collection": collection}
        ))
    qdrant.upsert(collection_name=collection, points=points)
    return {"ok": True, "coleccion": collection, "fragmentos": len(points)}


@app.post("/admin/collection")
def create_collection(
    name: str,
    authorization: str = Header(...)
):
    check_admin(authorization)
    ensure_collection(name)
    return {"ok": True, "coleccion": name}


@app.get("/admin/collections")
def list_collections(authorization: str = Header(...)):
    check_admin(authorization)
    cols = qdrant.get_collections().collections
    return {"colecciones": [c.name for c in cols]}


@app.post("/admin/client")
def upsert_client(
    telegram_id: str,
    colecciones: str = "",          # "juridico,contratos"
    limite_diario: int = DEFAULT_LIMIT,
    authorization: str = Header(...)
):
    check_admin(authorization)
    cols = [c.strip() for c in colecciones.split(",") if c.strip()]
    existing = db.search(Client.telegram_id == telegram_id)
    if existing:
        db.update({"colecciones": cols, "limite_diario": limite_diario},
                  Client.telegram_id == telegram_id)
    else:
        db.insert({
            "telegram_id": telegram_id,
            "colecciones": cols,
            "limite_diario": limite_diario,
            "consultas_hoy": 0,
            "ultima_actualizacion": today_ec()
        })
    return {"ok": True, "telegram_id": telegram_id, "colecciones": cols, "limite_diario": limite_diario}


@app.get("/admin/client/{telegram_id}")
def admin_get_client(telegram_id: str, authorization: str = Header(...)):
    check_admin(authorization)
    c = get_client(telegram_id)
    if not c:
        raise HTTPException(status_code=404, detail="Cliente no encontrado")
    return c


@app.get("/admin/clients")
def list_clients(authorization: str = Header(...)):
    check_admin(authorization)
    return {"clientes": db.all()}


# ─── CLIENT endpoints ─────────────────────────────────────────────────────────

@app.post("/query")
async def query(
    telegram_id: str = Form(...),
    tema: str = Form(...),
    pregunta: str = Form(...)
):
    c = get_client(telegram_id)
    if not c:
        return JSONResponse({"error": "no_registrado",
                             "mensaje": "No estás registrado. Contacta al administrador."})

    cols_permitidas = c.get("colecciones", [])
    cols_pedidas    = [t.strip().lower() for t in tema.split(",")]
    cols_validas    = [col for col in cols_pedidas if col in cols_permitidas]

    if not cols_validas:
        return JSONResponse({"error": "sin_acceso",
                             "mensaje": f"No tienes acceso a: {', '.join(cols_pedidas)}"})

    limite = c.get("limite_diario", DEFAULT_LIMIT)
    usadas = c.get("consultas_hoy", 0)
    if usadas >= limite:
        return JSONResponse({"error": "limite_alcanzado",
                             "mensaje": f"Alcanzaste tu límite de {limite} consultas diarias. Se renueva mañana."})

    # Buscar en Qdrant
    vec       = await embed(pregunta)
    fragmentos = []
    for col in cols_validas:
        hits = qdrant.search(collection_name=col, query_vector=vec, limit=5)
        fragmentos.extend([h.payload.get("text", "") for h in hits])

    # Descontar consulta
    db.update({"consultas_hoy": usadas + 1}, Client.telegram_id == telegram_id)

    return {
        "ok": True,
        "fragmentos": fragmentos,
        "consultas_restantes": limite - (usadas + 1),
        "colecciones_consultadas": cols_validas
    }


@app.get("/client/{telegram_id}/status")
def client_status(telegram_id: str):
    c = get_client(telegram_id)
    if not c:
        raise HTTPException(status_code=404, detail="Cliente no encontrado")
    limite = c.get("limite_diario", DEFAULT_LIMIT)
    usadas = c.get("consultas_hoy", 0)
    return {
        "telegram_id": telegram_id,
        "colecciones": c.get("colecciones", []),
        "limite_diario": limite,
        "consultas_hoy": usadas,
        "consultas_restantes": max(0, limite - usadas)
    }


@app.get("/health")
def health():
    return {"status": "ok"}
