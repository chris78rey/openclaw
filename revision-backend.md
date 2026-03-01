# Contexto Consolidado Para Revision LLM

- Raiz: `G:\opencode\openclaw`
- Generado: `2026-03-01 21:43:15 UTC`
- Archivos incluidos: `6`

## Archivos incluidos

- `AGENTS.md`
- `docker-compose.yml`
- `rag-api/main.py`
- `webapp/app.py`
- `webapp/static/app.js`
- `webapp/static/index.html`

## Arbol resumido

```text
+-- AGENTS.md
+-- docker-compose.yml
+-- rag-api
|   \-- main.py
\-- webapp
    +-- app.py
    \-- static
        +-- app.js
        \-- index.html
```

## Contenido

### AGENTS.md

- Bytes leidos: `2195`
- Lineas aproximadas: `46`

```markdown
# Repository Guidelines

## Project Structure & Module Organization
This repository currently hosts Codex skills.

- `.agents/skills/`: skill folders recognized by Codex.
- `.agents/skills/suma-numeros/`: active example skill.
- `.agents/skills/<skill>/SKILL.md`: required skill definition (frontmatter + instructions).
- `.agents/skills/<skill>/agents/openai.yaml`: UI metadata for skill chips/lists.
- `.agents/skills/<skill>/scripts/`: executable helpers (Python, shell, etc.).
- `instr.md`: local notes/instructions (not part of skill runtime).

When adding a new skill, follow the same folder layout and keep each skill self-contained.

## Build, Test, and Development Commands
There is no global build system yet. Work at skill level.

- `python .agents/skills/suma-numeros/scripts/sumar_numeros.py 1 2 3.5`
  Runs the skill script with CLI args.
- `echo "1, 2; 3" | python .agents/skills/suma-numeros/scripts/sumar_numeros.py`
  Runs the same script via `stdin`.
- `python C:\Users\crrb\.codex\skills\.system\skill-creator\scripts\quick_validate.py .agents/skills/suma-numeros`
  Validates skill structure and frontmatter.

## Coding Style & Naming Conventions
- Use Python 3 with 4-space indentation and readable, small functions.
- Prefer ASCII in files unless a clear reason requires Unicode.
- Skill folder names: lowercase hyphen-case (example: `suma-numeros`).
- Script names: snake_case (example: `sumar_numeros.py`).
- Keep `SKILL.md` concise and imperative; put only trigger criteria in frontmatter `description`.

## Testing Guidelines
- Test scripts with representative valid and invalid inputs.
- For numeric parsers, include decimals, separators (space/comma/semicolon), and ignored tokens.
- Re-run `quick_validate.py` after any `SKILL.md` or metadata update.

## Commit & Pull Request Guidelines
No commit history exists yet, so use this baseline:

- Commit style: `type(scope): short summary` (e.g., `feat(skill): add suma-numeros parser`).
- Keep commits focused (one skill or one behavior change per commit).
- PRs should include:
  - What changed and why
  - Paths touched (for example, `.agents/skills/suma-numeros/...`)
  - Validation evidence (command run + result)
```

### docker-compose.yml

- Bytes leidos: `4063`
- Lineas aproximadas: `151`

```yaml
version: "3.8"

services:
  rag-api:
    build:
      context: ./rag-api
      dockerfile: Dockerfile
    image: datica-rag-api:latest
    restart: unless-stopped
    init: true
    logging: &default-logging
      driver: json-file
      options:
        max-size: "10m"
        max-file: "3"
    environment:
      ADMIN_TOKEN: ${ADMIN_TOKEN:-}
      QDRANT_HOST: qdrant
      QDRANT_PORT: 6333
      OLLAMA_HOST: ollama
      OLLAMA_PORT: 11434
      EMBED_MODEL: ${EMBED_MODEL:-bge-m3}
      EMBED_DIM: ${EMBED_DIM:-1024}
      CLIENTS_DB_PATH: /app/uploads/clients.json
    volumes:
      - rag_api_uploads:/app/uploads
    expose:
      - "8000"
    networks:
      - app_net
    depends_on:
      qdrant:
        condition: service_started
      ollama:
        condition: service_healthy
    healthcheck:
      test: ["CMD-SHELL", "python -c \"import urllib.request; urllib.request.urlopen('http://localhost:8000/health')\""]
      interval: 15s
      timeout: 5s
      retries: 5
      start_period: 20s

  webapp:
    build:
      context: ./webapp
      dockerfile: Dockerfile
    image: datica-rag-web:latest
    restart: unless-stopped
    init: true
    logging: *default-logging
    environment:
      QDRANT_HOST: qdrant
      QDRANT_PORT: 6333
      OLLAMA_HOST: ollama
      OLLAMA_PORT: 11434
      CHAT_MODEL: ${CHAT_MODEL:-deepseek-r1:8b}
      EMBED_MODEL: ${EMBED_MODEL:-bge-m3}
      EMBED_DIM: ${EMBED_DIM:-1024}
      RAG_TOP_K: ${RAG_TOP_K:-10}
    expose:
      - "8080"
    networks:
      - app_net
    depends_on:
      qdrant:
        condition: service_started
      ollama:
        condition: service_healthy
    healthcheck:
      test: ["CMD-SHELL", "python -c \"import urllib.request; urllib.request.urlopen('http://localhost:8080/api/health')\""]
      interval: 15s
      timeout: 5s
      retries: 5
      start_period: 20s
    labels:
      - traefik.enable=true
      - traefik.docker.network=coolify
      - traefik.http.routers.datica-rag-web.rule=Host(`bot.da-tica.com`)
      - traefik.http.routers.datica-rag-web.entrypoints=https
      - traefik.http.routers.datica-rag-web.tls=true
      - traefik.http.routers.datica-rag-web.tls.certresolver=letsencrypt
      - traefik.http.services.datica-rag-web.loadbalancer.server.port=8080
      - traefik.http.routers.datica-rag-web-http.rule=Host(`bot.da-tica.com`)
      - traefik.http.routers.datica-rag-web-http.entrypoints=http
      - traefik.http.routers.datica-rag-web-http.middlewares=datica-rag-redirect
      - traefik.http.middlewares.datica-rag-redirect.redirectscheme.scheme=https
      - traefik.http.middlewares.datica-rag-redirect.redirectscheme.permanent=true

  qdrant:
    image: qdrant/qdrant:latest
    restart: unless-stopped
    logging: *default-logging
    volumes:
      - qdrant_data:/qdrant/storage
    expose:
      - "6333"
      - "6334"
    networks:
      - app_net

  ollama:
    image: ollama/ollama:latest
    restart: unless-stopped
    logging: *default-logging
    environment:
      OLLAMA_KEEP_ALIVE: "-1"
      OLLAMA_MAX_LOADED_MODELS: "2"
    volumes:
      - ollama_data:/root/.ollama
    expose:
      - "11434"
    networks:
      - app_net
    entrypoint: >
      sh -c "
        ollama serve &
        OLLAMA_PID=$$!
        echo '[init] Esperando que Ollama arranque...'
        for i in $$(seq 1 30); do
          ollama list >/dev/null 2>&1 && break
          sleep 2
        done
        echo '[init] Lanzando descarga de modelos en background...'
        (
          ollama pull ${CHAT_MODEL:-deepseek-r1:8b}
          ollama pull ${EMBED_MODEL:-bge-m3}
          echo '[init] Modelos listos'
        ) &
        wait $$OLLAMA_PID
      "
    healthcheck:
      test: ["CMD-SHELL", "ollama list >/dev/null 2>&1"]
      interval: 15s
      timeout: 10s
      retries: 20
      start_period: 120s
    deploy:
      resources:
        limits:
          memory: ${OLLAMA_MEM_LIMIT:-8G}

volumes:
  rag_api_uploads:
  qdrant_data:
  ollama_data:

networks:
  app_net:
    name: ${DOCKER_NETWORK:-coolify}
    external: true
```

### rag-api/main.py

- Bytes leidos: `8961`
- Lineas aproximadas: `234`

```python
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
EMBED_DIM     = int(os.getenv("EMBED_DIM", "1024"))
CLIENTS_DB_PATH = os.getenv("CLIENTS_DB_PATH", "/app/uploads/clients.json")
TZ_EC         = timezone(timedelta(hours=-5))
DEFAULT_LIMIT = 40

# ─── Clientes ─────────────────────────────────────────────────────────────────
qdrant = QdrantClient(host=QDRANT_HOST, port=QDRANT_PORT)
os.makedirs(os.path.dirname(CLIENTS_DB_PATH), exist_ok=True)
db     = TinyDB(CLIENTS_DB_PATH)
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
```

### webapp/app.py

- Bytes leidos: `12832`
- Lineas aproximadas: `400`

```python
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


class TextUploadPayload(BaseModel):
    collection: str = Field(min_length=2, max_length=64)
    text: str = Field(min_length=1)
    source: str | None = None


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


def is_vague_question(question: str) -> bool:
    cleaned = re.sub(r"\s+", " ", question.strip().lower())
    if len(cleaned) < 18:
        return True
    short_prompts = {
        "awr",
        "oracle",
        "sql",
        "esperas",
        "cpu",
        "memoria",
        "rendimiento",
    }
    if cleaned in short_prompts:
        return True
    words = cleaned.split()
    return len(words) <= 4


async def rewrite_question(http: httpx.AsyncClient, question: str) -> str:
    response = await http.post(
        f"{OLLAMA_BASE}/api/chat",
        json={
            "model": CHAT_MODEL,
            "stream": False,
            "messages": [
                {
                    "role": "system",
                    "content": (
                        "Reescribe preguntas vagas para mejorar busquedas RAG. "
                        "Manten la intencion original. "
                        "No respondas la pregunta. "
                        "Devuelve una sola pregunta en espanol claro, mas precisa y rica en contexto tecnico. "
                        "No uses comillas, listas ni explicaciones."
                    ),
                },
                {
                    "role": "user",
                    "content": question,
                },
            ],
        },
        timeout=60,
    )
    response.raise_for_status()
    rewritten = response.json()["message"]["content"].strip()
    return rewritten or question


def clean_answer_text(text: str) -> str:
    cleaned = text.replace("\r\n", "\n").replace("\r", "\n")
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
    selected_model = CHAT_MODEL

    snippets = []
    for index, block in enumerate(context_blocks, start=1):
        snippets.append(
            f"[{index}] Coleccion: {block['collection']} | Fuente: {block['source']}\n{block['text']}"
        )

    system_prompt = (
        "Responde en espanol claro, natural y profesional. "
        "Usa solo el contexto recuperado. "
        "Si el contexto no alcanza, dilo explicitamente. "
        "Da una respuesta extensa, bien desarrollada y util. "
        "Organiza la respuesta en parrafos claros o secciones simples cuando ayude. "
        "No uses caracteres chinos, simbolos raros, iconos, emojis ni decoracion visual."
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
    return clean_answer_text(response.json()["message"]["content"])


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
        points.append(
            PointStruct(
                id=str(uuid.uuid4()),
                vector=vector,
                payload={
                    "text": chunk,
                    "source": source_name,
                    "collection": collection_name,
                },
            )
        )

    qdrant.upsert(collection_name=collection_name, points=points)
    return {
        "ok": True,
        "collection": collection_name,
        "source": source_name,
        "chunks": len(points),
    }


@app.post("/api/chat")
async def chat(request: Request, payload: ChatPayload) -> dict[str, Any]:
    total_started = perf_counter()
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

    rewrite_ms = 0.0
    retrieval_question = question
    if is_vague_question(question):
        rewrite_started = perf_counter()
        retrieval_question = await rewrite_question(http, question)
        rewrite_ms = round((perf_counter() - rewrite_started) * 1000, 2)

    embed_started = perf_counter()
    vector = await embed_text(http, retrieval_question)
    embed_ms = round((perf_counter() - embed_started) * 1000, 2)

    search_started = perf_counter()
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
    search_ms = round((perf_counter() - search_started) * 1000, 2)

    matches = [item for item in matches if item["text"]]
    matches.sort(key=lambda item: item["score"], reverse=True)
    top_matches = matches[:TOP_K]

    if not top_matches:
        total_ms = round((perf_counter() - total_started) * 1000, 2)
        return {
            "answer": "No encontre informacion relacionada en los documentos cargados.",
            "sources": [],
            "timings_ms": {
                "rewrite": rewrite_ms,
                "embed": embed_ms,
                "search": search_ms,
                "llm": 0.0,
                "total": total_ms,
            },
        }

    llm_started = perf_counter()
    answer = await call_llm(http, question, top_matches, payload.model)
    llm_ms = round((perf_counter() - llm_started) * 1000, 2)
    total_ms = round((perf_counter() - total_started) * 1000, 2)
    return {
        "answer": answer,
        "sources": top_matches,
        "timings_ms": {
            "rewrite": rewrite_ms,
            "embed": embed_ms,
            "search": search_ms,
            "llm": llm_ms,
            "total": total_ms,
        },
    }
```

### webapp/static/app.js

- Bytes leidos: `6818`
- Lineas aproximadas: `228`

```javascript
const collectionList = document.getElementById("collection-list");
const chatCollections = document.getElementById("chat-collections");
const uploadCollection = document.getElementById("upload-collection");
const modelSelect = document.getElementById("model-select");
const uploadStatus = document.getElementById("upload-status");
const chatStatus = document.getElementById("chat-status");
const messages = document.getElementById("messages");
const chatForm = document.getElementById("chat-form");
const chatInput = document.getElementById("chat-input");
const chatSubmit = chatForm.querySelector("button[type='submit']");
const pasteForm = document.getElementById("paste-form");
const pasteSource = document.getElementById("paste-source");
const pasteText = document.getElementById("paste-text");

const selectedCollections = new Set();

function setStatus(node, text) {
  node.textContent = text;
}

function addMessage(role, text) {
  const article = document.createElement("article");
  article.className = `message ${role}`;
  const paragraph = document.createElement("p");
  paragraph.textContent = text;
  article.appendChild(paragraph);
  messages.appendChild(article);
  messages.scrollTop = messages.scrollHeight;
}

function renderCollections(collections) {
  collectionList.innerHTML = "";
  chatCollections.innerHTML = "";
  uploadCollection.innerHTML = "";

  if (!collections.length) {
    collectionList.innerHTML = '<span class="tag">Sin colecciones</span>';
    chatCollections.innerHTML = '<span class="tag">Sube un documento primero</span>';
    return;
  }

  for (const collection of collections) {
    const option = document.createElement("option");
    option.value = collection;
    option.textContent = collection;
    uploadCollection.appendChild(option);

    const summaryTag = document.createElement("span");
    summaryTag.className = "tag";
    summaryTag.textContent = collection;
    collectionList.appendChild(summaryTag);

    const pickerTag = document.createElement("button");
    pickerTag.type = "button";
    pickerTag.className = "tag selectable";
    pickerTag.textContent = collection;
    pickerTag.addEventListener("click", () => {
      if (selectedCollections.has(collection)) {
        selectedCollections.delete(collection);
        pickerTag.classList.remove("active");
      } else {
        selectedCollections.add(collection);
        pickerTag.classList.add("active");
      }
    });
    chatCollections.appendChild(pickerTag);
  }
}

function setChatBusy(isBusy) {
  chatInput.disabled = isBusy;
  chatSubmit.disabled = isBusy;
  chatSubmit.textContent = isBusy ? "Consultando..." : "Preguntar";
}

async function loadCollections() {
  const response = await fetch("/api/collections");
  const payload = await response.json();
  renderCollections(payload.collections || []);
}

async function loadModels() {
  const response = await fetch("/api/models");
  const payload = await response.json();
  modelSelect.innerHTML = "";

  for (const model of payload.models || []) {
    const option = document.createElement("option");
    option.value = model;
    option.textContent = model;
    if (model === payload.default) {
      option.selected = true;
    }
    modelSelect.appendChild(option);
  }
}

document.getElementById("collection-form").addEventListener("submit", async (event) => {
  event.preventDefault();
  const input = document.getElementById("collection-name");
  const name = input.value.trim();
  if (!name) return;

  setStatus(uploadStatus, "Creando...");
  const response = await fetch("/api/collections", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ name }),
  });

  if (!response.ok) {
    setStatus(uploadStatus, "Error");
    return;
  }

  input.value = "";
  await loadCollections();
  setStatus(uploadStatus, "Coleccion creada");
});

document.getElementById("upload-form").addEventListener("submit", async (event) => {
  event.preventDefault();
  const fileInput = document.getElementById("upload-file");
  const file = fileInput.files[0];
  const collection = uploadCollection.value;
  if (!file || !collection) return;

  const formData = new FormData();
  formData.append("collection", collection);
  formData.append("file", file);

  setStatus(uploadStatus, "Subiendo...");
  const response = await fetch("/api/upload", {
    method: "POST",
    body: formData,
  });

  const payload = await response.json();
  if (!response.ok) {
    setStatus(uploadStatus, payload.detail || "Error");
    return;
  }

  fileInput.value = "";
  setStatus(uploadStatus, `Listo: ${payload.chunks} fragmentos`);
  await loadCollections();
});

pasteForm.addEventListener("submit", async (event) => {
  event.preventDefault();
  const collection = uploadCollection.value;
  const text = pasteText.value.trim();
  const source = pasteSource.value.trim();
  if (!collection || !text) return;

  setStatus(uploadStatus, "Guardando texto...");
  const response = await fetch("/api/upload-text", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      collection,
      text,
      source: source || "texto-manual",
    }),
  });

  const payload = await response.json();
  if (!response.ok) {
    setStatus(uploadStatus, payload.detail || "Error");
    return;
  }

  pasteSource.value = "";
  pasteText.value = "";
  setStatus(uploadStatus, `Texto guardado: ${payload.chunks} fragmentos`);
  await loadCollections();
});

chatInput.addEventListener("keydown", (event) => {
  if (event.key === "Enter" && !event.shiftKey) {
    event.preventDefault();
    chatForm.requestSubmit();
  }
});

chatForm.addEventListener("submit", async (event) => {
  event.preventDefault();
  const question = chatInput.value.trim();
  if (!question) return;

  addMessage("user", question);
  chatInput.value = "";
  setStatus(chatStatus, "Consultando...");
  setChatBusy(true);

  const response = await fetch("/api/chat", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      question,
      collections: Array.from(selectedCollections),
      model: modelSelect.value || null,
    }),
  });

  const payload = await response.json();
  if (!response.ok) {
    addMessage("assistant", payload.detail || "No pude responder.");
    setStatus(chatStatus, "Error");
    setChatBusy(false);
    chatInput.focus();
    return;
  }

  addMessage("assistant", payload.answer);
  setStatus(chatStatus, "Listo para otra pregunta");
  chatInput.placeholder = "Haz otra pregunta sobre los mismos documentos...";
  setChatBusy(false);
  chatInput.focus();
});

Promise.all([loadCollections(), loadModels()]).catch(() => {
  setStatus(chatStatus, "Error");
  setStatus(uploadStatus, "Error");
});

chatInput.focus();
```

### webapp/static/index.html

- Bytes leidos: `3592`
- Lineas aproximadas: `112`

```html
<!DOCTYPE html>
<html lang="es">
  <head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0" />
    <title>DA-TICA RAG</title>
    <link rel="stylesheet" href="/static/styles.css" />
  </head>
  <body>
    <div class="page-shell">
      <header class="hero">
        <p class="eyebrow">DA-TICA</p>
        <h1>RAG web simple</h1>
        <p class="hero-copy">
          Sube documentos, organiza colecciones y pregunta directo sobre tu base.
        </p>
      </header>

      <main class="grid">
        <section class="panel">
          <div class="panel-head">
            <h2>Documentos</h2>
            <span id="upload-status" class="status-pill">Listo</span>
          </div>

          <form id="collection-form" class="stack-form">
            <label>
              Nueva coleccion
              <div class="inline-row">
                <input id="collection-name" type="text" placeholder="ej: contratos-2026" />
                <button type="submit">Crear</button>
              </div>
            </label>
          </form>

          <form id="upload-form" class="stack-form">
            <label>
              Coleccion
              <select id="upload-collection"></select>
            </label>
            <label>
              Archivo
              <input id="upload-file" type="file" accept=".pdf,.docx,.txt,.md" />
            </label>
            <button type="submit">Subir al RAG</button>
          </form>

          <form id="paste-form" class="stack-form">
            <label>
              Fuente manual
              <input id="paste-source" type="text" placeholder="ej: awr-prod-2026-03-01" />
            </label>
            <label>
              Texto pegado
              <textarea
                id="paste-text"
                rows="8"
                placeholder="Pega aqui un AWR, una salida SQL, notas tecnicas o cualquier texto fuente..."
              ></textarea>
            </label>
            <button type="submit">Guardar texto como fuente</button>
          </form>

          <div class="collections-block">
            <div class="panel-head small">
              <h3>Colecciones disponibles</h3>
            </div>
            <div id="collection-list" class="tag-list"></div>
          </div>
        </section>

        <section class="panel chat-panel">
          <div class="panel-head">
            <h2>Chat</h2>
            <span id="chat-status" class="status-pill">Esperando</span>
          </div>

          <div class="toolbar">
            <label>
              Modelo
              <select id="model-select"></select>
            </label>
          </div>

          <div class="collection-picker">
            <p class="picker-title">Buscar en estas colecciones</p>
            <div id="chat-collections" class="tag-list selectable"></div>
          </div>

          <div id="messages" class="messages">
            <article class="message assistant">
              <p>Sube documentos y luego haz una pregunta para responder con RAG.</p>
            </article>
          </div>

          <form id="chat-form" class="chat-form">
            <textarea
              id="chat-input"
              rows="4"
              placeholder="Pregunta algo sobre los documentos cargados..."
            ></textarea>
            <p class="chat-hint">Enter para enviar. Shift+Enter para nueva linea.</p>
            <button type="submit">Preguntar</button>
          </form>
        </section>
      </main>
    </div>

    <script src="/static/app.js" defer></script>
  </body>
  </html>
```
