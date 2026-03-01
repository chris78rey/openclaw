# Contexto Consolidado Para Revision LLM

- Raiz: `G:\opencode\openclaw`
- Generado: `2026-03-01 12:08:47 UTC`
- Archivos incluidos: `16`

## Archivos incluidos

- `AGENTS.md`
- `Dockerfile`
- `arq.md`
- `consideraciones.md`
- `docker-compose.yml`
- `instr.md`
- `rag-api/Dockerfile`
- `rag-api/main.py`
- `rag-api/requirements.txt`
- `scripts/validate_vps_stack.sh`
- `webapp/Dockerfile`
- `webapp/app.py`
- `webapp/requirements.txt`
- `webapp/static/app.js`
- `webapp/static/index.html`
- `webapp/static/styles.css`

## Arbol resumido

```text
+-- AGENTS.md
+-- arq.md
+-- consideraciones.md
+-- docker-compose.yml
+-- Dockerfile
+-- instr.md
+-- rag-api
|   +-- Dockerfile
|   +-- main.py
|   \-- requirements.txt
+-- scripts
|   \-- validate_vps_stack.sh
\-- webapp
    +-- app.py
    +-- Dockerfile
    +-- requirements.txt
    \-- static
        +-- app.js
        +-- index.html
        \-- styles.css
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

### Dockerfile

- Bytes leidos: `202`
- Lineas aproximadas: `10`

```
FROM node:22-bookworm

RUN apt-get update \
    && apt-get install -y --no-install-recommends git ca-certificates \
    && rm -rf /var/lib/apt/lists/*

RUN npm install -g openclaw@latest

WORKDIR /root
```

### arq.md

- Bytes leidos: `8191`
- Lineas aproximadas: `269`

```markdown
# SOUL

Eres un asistente profesional especializado en consultas documentales para clientes de DA-TICA.

## Personalidad
- Formal pero cercano, siempre respetuoso
- Preciso y directo en tus respuestas
- Combinas el conocimiento de los documentos con tu conocimiento general
- Nunca inventas información — si no está en los documentos ni en tu conocimiento, lo dices claramente
- Siempre confirmas cuando una acción fue completada exitosamente

## Idioma
- Responde siempre en español
- Usa lenguaje claro, evita tecnicismos innecesarios

## Limitaciones que debes comunicar con respeto
- No puedes compartir documentos completos, solo responder consultas
- No puedes modificar ni eliminar colecciones
- Cada cliente tiene un límite de consultas diarias según su plan





---


AGENTS
Roles
Existen dos tipos de usuarios:

ADMIN — identificado por telegram_id en la lista de admins. Puede gestionar colecciones, clientes y configuraciones.
CLIENTE — cualquier otro usuario. Solo puede consultar colecciones que tenga asignadas.


Flujo ADMIN
Subir documentos

Admin envía archivo (PDF, Word) o pega texto
Admin indica: coleccion: juridico (o el nombre de la colección)
El agente procesa el contenido, lo indexa en Qdrant bajo esa colección
Confirma: "✅ Documento indexado en la colección juridico. Fragmentos generados: N"

Crear colección nueva
Comando: /nueva_coleccion nombre_coleccion

El agente crea la colección en Qdrant
Confirma: "✅ Colección nombre_coleccion creada exitosamente"

Asignar cliente a colección
Comando: /asignar telegram_id coleccion1,coleccion2

El agente guarda en memoria: qué colecciones puede consultar ese cliente
Confirma: "✅ Cliente telegram_id tiene acceso a: juridico"

Configurar límite de consultas por cliente
Comando: /limite telegram_id 100

El agente guarda el límite personalizado para ese cliente
Por defecto todos los clientes tienen 40 consultas diarias
Confirma: "✅ Cliente telegram_id actualizado a 100 consultas diarias"

Ver estado de un cliente
Comando: /estado telegram_id

El agente responde con:

Colecciones asignadas
Límite diario
Consultas usadas hoy
Consultas restantes hoy



Ver todas las colecciones
Comando: /colecciones

Lista todas las colecciones disponibles en Qdrant con número de documentos


Flujo CLIENTE
Consulta normal

Cliente escribe el tema: "juridico"
El agente verifica:

¿Tiene acceso a esa colección? Si no → "Lo siento, no tienes acceso a esa colección"
¿Tiene consultas disponibles hoy? Si no → "Has alcanzado tu límite de N consultas diarias. Se renueva mañana"


Cliente hace su pregunta
El agente busca en Qdrant (colección asignada) + combina con conocimiento general
Responde con la información encontrada
Descuenta 1 consulta del contador diario del cliente
Al final de la respuesta agrega discretamente: "(Consultas restantes hoy: N)"

Consulta en múltiples colecciones

Si el cliente tiene acceso a varias colecciones, puede indicar: "juridico y contratos"
El agente busca en ambas colecciones
Cuenta como 1 sola consulta (no una por colección)

Ver mis colecciones disponibles
Comando: /mis_colecciones

El agente lista las colecciones a las que tiene acceso ese cliente

Ver mis consultas disponibles
Comando: /mis_consultas

El agente responde cuántas consultas le quedan hoy y su límite diario


Reglas generales

El contador de consultas se reinicia cada día a medianoche (hora Ecuador, UTC-5)
Un cliente sin colecciones asignadas recibe: "Aún no tienes colecciones asignadas. Contacta al administrador"
Un cliente no registrado recibe: "No estás registrado en el sistema. Contacta al administrador"
Nunca reveles información de otros clientes
Nunca reveles los telegram_id de los admins
El agente NUNCA elimina colecciones, solo el admin puede hacerlo y debe confirmarlo dos veces



----

USER
Identificación

Cada usuario se identifica por su telegram_id (número único de Telegram)
El agente debe leer el telegram_id de cada mensaje entrante automáticamente
Nunca preguntes el nombre o identidad — ya la tienes por Telegram

Estructura de datos por cliente
Cada cliente tiene almacenado en memoria:
json{
  "telegram_id": "123456789",
  "colecciones": ["juridico"],
  "limite_diario": 40,
  "consultas_hoy": 0,
  "ultima_actualizacion": "2026-02-26"
}
Admins
Lista de telegram_id con rol admin (configura el admin al inicio):
json{
  "admins": ["TU_TELEGRAM_ID_AQUI"]
}
Comportamiento según tipo de usuario
Si es ADMIN

Tiene acceso a todos los comandos de gestión
No tiene límite de consultas
Puede consultar cualquier colección sin restricción

Si es CLIENTE registrado

Solo ve sus colecciones asignadas
Respeta su límite diario personalizado
Recibe contador de consultas restantes en cada respuesta

Si es desconocido (no registrado)

Recibe mensaje de bienvenida explicando que debe contactar al administrador
No tiene acceso a ninguna colección
No consume consultas




-----


TOOLS
Herramientas necesarias
1. qdrant_search
Busca fragmentos relevantes en una o varias colecciones de Qdrant.
Parámetros:

query — texto de la consulta del cliente
collections — lista de colecciones donde buscar
limit — número de fragmentos a retornar (default: 5)

Uso: Cuando un cliente hace una consulta, siempre llama esta herramienta primero antes de responder.

2. qdrant_index
Indexa texto o documento en una colección de Qdrant.
Parámetros:

text — contenido del documento
collection — nombre de la colección destino
metadata — información adicional (nombre archivo, fecha, admin_id)

Uso: Solo disponible para ADMIN. Se llama cuando el admin sube un documento.

3. qdrant_create_collection
Crea una nueva colección en Qdrant.
Parámetros:

collection_name — nombre de la colección

Uso: Solo disponible para ADMIN via comando /nueva_coleccion.

4. memory_get_client
Lee la configuración de un cliente desde memoria.
Parámetros:

telegram_id — ID del cliente

Retorna: colecciones asignadas, límite diario, consultas usadas hoy.

5. memory_set_client
Guarda o actualiza la configuración de un cliente en memoria.
Parámetros:

telegram_id
colecciones (opcional)
limite_diario (opcional)
consultas_hoy (opcional)

Uso: Después de cada consulta para descontar el contador. También cuando el admin asigna colecciones o cambia el límite.

6. memory_list_clients
Lista todos los clientes registrados con su estado.
Uso: Solo para ADMIN.

Flujo interno en cada mensaje
1. Leer telegram_id del mensaje entrante
2. Verificar si es ADMIN → si sí, ejecutar flujo admin
3. Si no, llamar memory_get_client(telegram_id)
4. Si cliente no existe → mensaje de no registrado
5. Si existe, verificar consultas_hoy < limite_diario
6. Si superó límite → mensaje de límite alcanzado
7. Si todo ok → llamar qdrant_search con la consulta
8. Combinar resultado RAG + conocimiento general
9. Responder al cliente
10. Llamar memory_set_client para incrementar consultas_hoy

Reset diario del contador
Cada día a medianoche (UTC-5, hora Ecuador):

Para cada cliente, si ultima_actualizacion es diferente a hoy → resetear consultas_hoy = 0 y actualizar ultima_actualizacion
Este reset se hace automáticamente al leer el cliente con memory_get_client



Listo, tienes los 4 archivos. Aquí el resumen de qué hacer con ellos:

**¿Dónde van estos archivos?**
En el volumen de OpenClaw, dentro del workspace del agente:
```
/root/.openclaw/workspace/
├── SOUL.md
├── AGENTS.md
├── USER.md
└── TOOLS.md
```

**Paso inmediato:** En el `USER.md` reemplaza `TU_TELEGRAM_ID_AQUI` con tu telegram_id real. Para saber cuál es, mándale un mensaje al bot y ejecuta:

```bash
docker logs $(docker ps --format "{{.Names}}" | grep claw) | grep "chat="
```

El número después de `chat=` es tu telegram_id.

**Siguiente paso cuando quieras:** construir la API RAG en FastAPI que implemente las herramientas definidas en `TOOLS.md`.


```

### consideraciones.md

- Bytes leidos: `1829`
- Lineas aproximadas: `23`

```markdown
## Lecciones aprendidas 🦞

**1. Identifica el proveedor real antes de configurar**
El error 401 de MiniMax apuntaba a un problema de autenticación, pero la causa raíz era que se estaba usando el formato Anthropic (`x-api-key`) en lugar del formato OpenAI (`Authorization: Bearer`). Siempre verifica qué protocolo usa cada proveedor.

**2. El `command` del compose sobreescribe cambios manuales**
Cualquier cambio hecho con `docker exec` se pierde en el siguiente restart porque el `command` vuelve a escribir la config. Los cambios permanentes deben ir en el compose, no hacerse manualmente.

**3. Los volúmenes persisten config vieja**
Un volumen Docker guarda estado entre deploys. Si la config tenía valores incorrectos, seguirán ahí aunque cambies el compose. Solución: agregar `rm -f /root/.openclaw/openclaw.json` al inicio del command para garantizar config limpia.

**4. Verifica las variables de entorno antes de debuggear el código**
El key de OpenRouter estaba en `MINIMAX_API_KEY` en lugar de `OPENROUTER_API_KEY`. Un `docker inspect` al inicio nos hubiera ahorrado varios deploys.

**5. El orden de los comandos de config importa**
OpenClaw valida la consistencia en cada `config set`. Poner `dmPolicy open` antes de `allowFrom '["*"]'` causaba error de validación. Primero el dato, luego la política que lo referencia.

**6. Proveedores nativos vs custom**
OpenRouter es nativo en OpenClaw — no necesita `baseUrl` ni `api` manual. Intentar configurarlo como proveedor custom causaba errores de validación. Lee la documentación antes de asumir que todo proveedor se configura igual.

**7. El nombre del contenedor en Coolify es dinámico**
Coolify ignora el `container_name` del compose y genera su propio nombre. Usar `docker ps | grep claw` en lugar del nombre hardcodeado.
```

### docker-compose.yml

- Bytes leidos: `4099`
- Lineas aproximadas: `149`

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
      CHAT_MODEL: ${CHAT_MODEL:-llama3.2:3b}
      EMBED_MODEL: ${EMBED_MODEL:-bge-m3}
      EMBED_DIM: ${EMBED_DIM:-1024}
      RAG_TOP_K: ${RAG_TOP_K:-6}
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
        echo '[init] Descargando modelos (skip si ya existen)...'
        ollama pull ${CHAT_MODEL:-llama3.2:3b}
        ollama pull ${EMBED_MODEL:-bge-m3}
        echo '[init] Modelos listos'
        wait $$OLLAMA_PID
      "
    healthcheck:
      test: ["CMD-SHELL", "ollama list | grep -q '${CHAT_MODEL:-llama3.2:3b}' && ollama list | grep -q '${EMBED_MODEL:-bge-m3}'"]
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

### instr.md

- Bytes leidos: `3176`
- Lineas aproximadas: `80`

```markdown
becesito crear una estructura base de docker compose para una vez creado en el vps instlar en el vps siguiendo los pasos que dicen en https://github.com/openclaw/openclaw.


1. Respecto al objetivo del Docker Compose para instalar OpenClaw en el VPS, ¿qué alcance se define desde el inicio?
   a) Plantilla mínima solo para OpenClaw y sus dependencias directas (RECOMENDADA)

2. Respecto a la forma de instalación y actualización en el VPS, ¿qué estrategia se adopta?
   b) Pasos manuales documentados (copiar/pegar comandos) sin automatización


3. Respecto a la red y exposición pública de servicios, ¿qué patrón se decide?
   b) Publicar al mundo

4. Respecto a los datos y persistencia, ¿qué enfoque de volúmenes y rutas se estandariza?
   c) Todo en volúmenes Docker sin rutas fijas ni convención de backup/restore

----


1. Respecto a la estructura de archivos del proyecto Docker Compose, ¿qué organización se define?
   a) Un solo docker-compose.yml en la raíz con archivos sueltos (.env, README, scripts) (RECOMENDADA)


2. Respecto a la construcción de las imágenes necesarias para OpenClaw, ¿qué enfoque se adopta?
Lo que quiero es subir lo minimo necesario y despues voy a seguir los pasos que dicen en https://github.com/openclaw/openclaw desde la terminal

3. Respecto a la gestión de variables de entorno, ¿qué estrategia se define?
   b) Variables exportadas manualmente en la terminal antes de ejecutar docker compose


----


1. Respecto al contenido mínimo que debe subirse al VPS antes de seguir los pasos de OpenClaw, ¿qué conjunto de archivos se define?
   a) Solo `docker-compose.yml` y `README.md` con los comandos a ejecutar (RECOMENDADA)

Mi subdominio es bot.da-tica.com


Aca te doy un ejemplo de uno que si funciono un compose para que  lo adaptes.


services:
  web:
    build:
      context: ./web
      dockerfile: Dockerfile
    image: 'da-tica_portal_web:1.0.0'
    restart: unless-stopped
    networks:
      - coolify
    expose:
      - '8080'
    healthcheck:
      test:
        - CMD
        - wget
        - '-qO-'
        - 'http://127.0.0.1:8080/'
      interval: 30s
      timeout: 5s
      retries: 3
      start_period: 10s
    labels:
      - traefik.enable=true
      - traefik.docker.network=coolify
      - traefik.http.routers.portal-da-tica-web.rule=Host(`portal.da-tica.com`)
      - traefik.http.routers.portal-da-tica-web.entrypoints=https
      - traefik.http.routers.portal-da-tica-web.tls=true
      - traefik.http.routers.portal-da-tica-web.tls.certresolver=letsencrypt
      - traefik.http.services.portal-da-tica-web.loadbalancer.server.port=8080
      - traefik.http.routers.portal-da-tica-web-http.rule=Host(`portal.da-tica.com`)
      - traefik.http.routers.portal-da-tica-web-http.entrypoints=http
      - traefik.http.routers.portal-da-tica-web-http.middlewares=portal-da-tica-redirect
      - traefik.http.middlewares.portal-da-tica-redirect.redirectscheme.scheme=https
      - traefik.http.middlewares.portal-da-tica-redirect.redirectscheme.permanent=true
networks:
  coolify:
    external: true
```

### rag-api/Dockerfile

- Bytes leidos: `364`
- Lineas aproximadas: `18`

```
FROM python:3.11-slim

WORKDIR /app

# Dependencias del sistema para PDF y Word
RUN apt-get update && apt-get install -y \
    libmagic1 \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY main.py .

EXPOSE 8000

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
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

### rag-api/requirements.txt

- Bytes leidos: `172`
- Lineas aproximadas: `10`

```
fastapi==0.111.0
uvicorn==0.30.1
qdrant-client==1.9.1
httpx==0.27.0
python-multipart==0.0.9
pdfplumber==0.11.0
python-docx==1.1.2
tinydb==4.8.0
python-jose==3.3.0
```

### scripts/validate_vps_stack.sh

- Bytes leidos: `10600`
- Lineas aproximadas: `347`

```bash
#!/usr/bin/env bash
set -u

DOMAIN="${1:-bot.da-tica.com}"
NETWORK="${DOCKER_NETWORK:-coolify}"
CHAT_MODEL="${CHAT_MODEL:-llama3.2:3b}"
EMBED_MODEL="${EMBED_MODEL:-bge-m3}"
WEB_NAME_FILTER="${WEB_NAME_FILTER:-webapp}"
OLLAMA_NAME_FILTER="${OLLAMA_NAME_FILTER:-ollama}"
QDRANT_NAME_FILTER="${QDRANT_NAME_FILTER:-qdrant}"
CHECK_TIMEOUT="${CHECK_TIMEOUT:-12}"
FAILURES=0
WARNINGS=0

red() { printf '\033[31m%s\033[0m\n' "$1"; }
green() { printf '\033[32m%s\033[0m\n' "$1"; }
yellow() { printf '\033[33m%s\033[0m\n' "$1"; }
blue() { printf '\033[36m%s\033[0m\n' "$1"; }

pass() { green "[PASS] $1"; }
fail() { red "[FAIL] $1"; FAILURES=$((FAILURES + 1)); }
warn() { yellow "[WARN] $1"; WARNINGS=$((WARNINGS + 1)); }
info() { blue "[INFO] $1"; }

section() {
  printf '\n'
  blue "== $1 =="
}

print_fix() {
  printf '       Sugerencia: %s\n' "$1"
}

need_command() {
  local cmd="$1"
  if ! command -v "$cmd" >/dev/null 2>&1; then
    fail "No existe el comando '$cmd'"
    print_fix "Instala '$cmd' y vuelve a ejecutar este script."
    exit 1
  fi
}

need_any_command() {
  local found=1
  local names="$*"
  for cmd in "$@"; do
    if command -v "$cmd" >/dev/null 2>&1; then
      found=0
      break
    fi
  done

  if [[ "$found" -ne 0 ]]; then
    fail "No existe ninguno de estos comandos: ${names}"
    print_fix "Instala al menos uno de ellos y vuelve a ejecutar este script."
    exit 1
  fi
}

run_with_timeout() {
  local seconds="$1"
  shift
  timeout --foreground "$seconds" "$@"
}

get_container_id() {
  local filter="$1"
  docker ps -qf "name=${filter}" | head -n 1
}

check_container_running() {
  local label="$1"
  local filter="$2"
  local cid
  cid="$(get_container_id "$filter")"
  if [[ -z "$cid" ]]; then
    fail "No hay contenedor en ejecucion para ${label} (filtro: ${filter})"
    print_fix "Ejecuta 'docker ps -a --filter name=${filter}' y revisa 'docker logs <contenedor>'."
    return 1
  fi

  pass "${label} esta corriendo (${cid})"
  return 0
}

check_health() {
  local label="$1"
  local cid="$2"
  local status

  status="$(docker inspect --format '{{if .State.Health}}{{.State.Health.Status}}{{else}}none{{end}}' "$cid" 2>/dev/null)"
  case "$status" in
    healthy)
      pass "${label} esta healthy"
      ;;
    starting)
      fail "${label} sigue en estado starting"
      print_fix "Revisa 'docker logs --tail 100 $cid'. Si es Ollama, puede estar descargando modelos todavia."
      ;;
    unhealthy)
      fail "${label} esta unhealthy"
      print_fix "Revisa 'docker inspect --format=\"{{json .State.Health}}\" $cid' y luego 'docker logs --tail 100 $cid'."
      ;;
    none)
      warn "${label} no tiene healthcheck"
      ;;
    *)
      fail "Estado de health inesperado para ${label}: ${status}"
      print_fix "Revisa 'docker inspect $cid'."
      ;;
  esac
}

check_network_exists() {
  if docker network inspect "$NETWORK" >/dev/null 2>&1; then
    pass "La red Docker '${NETWORK}' existe"
  else
    fail "No existe la red Docker '${NETWORK}'"
    print_fix "Crea la red o verifica DOCKER_NETWORK. Ejemplo: 'docker network create ${NETWORK}'."
  fi
}

check_container_in_network() {
  local label="$1"
  local cid="$2"
  local found

  found="$(docker network inspect "$NETWORK" --format '{{range .Containers}}{{.Name}} {{end}}' 2>/dev/null | grep -o "$cid" || true)"
  if [[ -n "$found" ]]; then
    pass "${label} esta conectado a la red '${NETWORK}'"
  else
    local cname
    cname="$(docker inspect --format '{{.Name}}' "$cid" 2>/dev/null | sed 's#^/##')"
    if docker network inspect "$NETWORK" --format '{{range .Containers}}{{.Name}} {{end}}' 2>/dev/null | grep -qw "$cname"; then
      pass "${label} esta conectado a la red '${NETWORK}'"
    else
      fail "${label} no aparece en la red '${NETWORK}'"
      print_fix "Recrea el stack y confirma que el servicio use la red externa '${NETWORK}'."
    fi
  fi
}

check_web_labels() {
  local cid="$1"
  local labels
  local traefik_network
  labels="$(docker inspect --format '{{json .Config.Labels}}' "$cid" 2>/dev/null)"
  traefik_network="$(docker inspect --format '{{ index .Config.Labels "traefik.docker.network" }}' "$cid" 2>/dev/null)"

  if printf '%s' "$labels" | grep -q 'traefik.enable'; then
    pass "webapp tiene labels de Traefik"
  else
    fail "webapp no tiene labels de Traefik"
    print_fix "Verifica docker-compose.yml y redeploy del servicio webapp."
    return
  fi

  if printf '%s' "$labels" | grep -q "${DOMAIN}"; then
    pass "webapp expone el dominio esperado (${DOMAIN})"
  else
    fail "webapp no publica el dominio esperado (${DOMAIN}) en labels"
    print_fix "Ajusta PUBLIC_WEB_HOST o las labels de Traefik y redeploy."
  fi

  if [[ "$traefik_network" == "$NETWORK" ]]; then
    pass "webapp declara la red de Traefik correcta (${NETWORK})"
  else
    fail "webapp no declara la red de Traefik correcta"
    print_fix "La label 'traefik.docker.network' debe apuntar a '${NETWORK}'."
  fi
}

check_http_from_container() {
  local cid="$1"
  local url="$2"
  local label="$3"

  if run_with_timeout "$CHECK_TIMEOUT" docker exec "$cid" sh -lc "wget -T ${CHECK_TIMEOUT} -qO- '$url' >/dev/null 2>&1 || curl --max-time ${CHECK_TIMEOUT} -fsS '$url' >/dev/null 2>&1"; then
    pass "${label} responde en ${url}"
  else
    local status=$?
    if [[ "$status" -eq 124 ]]; then
      fail "${label} excedio el timeout en ${url}"
      print_fix "Hay un cuelgue de red o resolucion DNS. Revisa conectividad interna y nombre del servicio."
    else
      fail "${label} no responde en ${url}"
      print_fix "Revisa conectividad interna, nombre DNS del contenedor y logs del servicio destino."
    fi
  fi
}

check_http_local() {
  local url="$1"
  local label="$2"
  if run_with_timeout "$CHECK_TIMEOUT" sh -lc "wget -T ${CHECK_TIMEOUT} -qO- '$url' >/dev/null 2>&1 || curl --max-time ${CHECK_TIMEOUT} -fsS '$url' >/dev/null 2>&1"; then
    pass "${label} responde en ${url}"
  else
    local status=$?
    if [[ "$status" -eq 124 ]]; then
      fail "${label} excedio el timeout en ${url}"
      print_fix "El endpoint local quedo colgado. Revisa el servicio y el puerto expuesto."
    else
      fail "${label} no responde en ${url}"
      print_fix "Si el contenedor esta healthy pero este endpoint falla, revisa Traefik o el puerto expuesto."
    fi
  fi
}

show_recent_logs() {
  local label="$1"
  local cid="$2"
  printf '\n'
  info "Ultimas 20 lineas de ${label}:"
  docker logs --tail 20 "$cid" 2>&1 || true
}

section "Prerequisitos"
need_command docker
need_command grep
need_command sed
need_command head
need_command timeout
need_any_command curl wget
need_command getent

if [[ "$(id -u)" -ne 0 ]]; then
  warn "No estas corriendo como root. El script sigue, pero algunas inspecciones pueden fallar."
fi

section "Docker"
if docker info >/dev/null 2>&1; then
  pass "Docker responde"
else
  fail "Docker no responde"
  print_fix "Verifica que el daemon este arriba con 'systemctl status docker' o equivalente."
  exit 1
fi

check_network_exists

section "Contenedores"
WEB_CID="$(get_container_id "$WEB_NAME_FILTER")"
OLLAMA_CID="$(get_container_id "$OLLAMA_NAME_FILTER")"
QDRANT_CID="$(get_container_id "$QDRANT_NAME_FILTER")"

check_container_running "webapp" "$WEB_NAME_FILTER" || true
check_container_running "ollama" "$OLLAMA_NAME_FILTER" || true
check_container_running "qdrant" "$QDRANT_NAME_FILTER" || true

for cid_triplet in \
  "webapp:$WEB_CID" \
  "ollama:$OLLAMA_CID" \
  "qdrant:$QDRANT_CID"; do
  name="${cid_triplet%%:*}"
  cid="${cid_triplet#*:}"
  if [[ -n "$cid" ]]; then
    check_container_in_network "$name" "$cid"
  fi
done

section "Healthchecks"
[[ -n "$WEB_CID" ]] && check_health "webapp" "$WEB_CID"
[[ -n "$OLLAMA_CID" ]] && check_health "ollama" "$OLLAMA_CID"
[[ -n "$QDRANT_CID" ]] && check_health "qdrant" "$QDRANT_CID"

section "Webapp"
if [[ -n "$WEB_CID" ]]; then
  check_web_labels "$WEB_CID"
  check_http_local "http://127.0.0.1:8080/api/health" "webapp local"
fi

section "Conectividad interna"
if [[ -n "$WEB_CID" ]]; then
  check_http_from_container "$WEB_CID" "http://ollama:11434/api/tags" "ollama desde webapp"
  check_http_from_container "$WEB_CID" "http://qdrant:6333/readyz" "qdrant desde webapp"
fi

section "Modelos en Ollama"
if [[ -n "$OLLAMA_CID" ]]; then
  MODELS="$(run_with_timeout "$CHECK_TIMEOUT" docker exec "$OLLAMA_CID" ollama list 2>/dev/null || true)"
  if [[ -n "$MODELS" ]]; then
    pass "Ollama devuelve listado de modelos"
    printf '%s\n' "$MODELS"
    if printf '%s' "$MODELS" | grep -q "$CHAT_MODEL"; then
      pass "Modelo de chat presente (${CHAT_MODEL})"
    else
      fail "Falta el modelo de chat (${CHAT_MODEL})"
      print_fix "Ejecuta: docker exec -it $OLLAMA_CID ollama pull ${CHAT_MODEL}"
    fi
    if printf '%s' "$MODELS" | grep -q "$EMBED_MODEL"; then
      pass "Modelo de embeddings presente (${EMBED_MODEL})"
    else
      fail "Falta el modelo de embeddings (${EMBED_MODEL})"
      print_fix "Ejecuta: docker exec -it $OLLAMA_CID ollama pull ${EMBED_MODEL}"
    fi
  else
    fail "No pude obtener el listado de modelos de Ollama"
    print_fix "Revisa logs de Ollama y prueba 'docker exec -it $OLLAMA_CID ollama list'. Si tarda, aumenta CHECK_TIMEOUT."
  fi
fi

section "Dominio publico"
if [[ -n "$DOMAIN" ]]; then
  if getent hosts "$DOMAIN" >/dev/null 2>&1; then
    pass "El dominio ${DOMAIN} resuelve por DNS"
  else
    fail "El dominio ${DOMAIN} no resuelve por DNS"
    print_fix "Apunta el subdominio al VPS y espera propagacion."
  fi

  if run_with_timeout "$CHECK_TIMEOUT" curl -kfsS --max-time "$CHECK_TIMEOUT" -H "Host: ${DOMAIN}" "https://${DOMAIN}/api/health" >/dev/null 2>&1; then
    pass "El dominio publico responde por HTTPS"
  else
    local status=$?
    if [[ "$status" -eq 124 ]]; then
      fail "El dominio publico excedio el timeout por HTTPS"
      print_fix "Traefik o el DNS podria estar colgando la peticion. Revisa proxy, certificado y resolucion."
    else
      fail "El dominio publico no responde por HTTPS"
      print_fix "Si webapp esta healthy, el problema suele ser Traefik/Coolify, labels o certificado."
    fi
  fi
fi

section "Resumen"
if [[ "$FAILURES" -eq 0 ]]; then
  pass "Validacion completada sin fallos"
else
  fail "Validacion completada con ${FAILURES} fallo(s)"
fi

if [[ "$WARNINGS" -gt 0 ]]; then
  warn "Tambien hubo ${WARNINGS} advertencia(s)"
fi

if [[ -n "$WEB_CID" ]]; then
  show_recent_logs "webapp" "$WEB_CID"
fi
if [[ -n "$OLLAMA_CID" ]]; then
  show_recent_logs "ollama" "$OLLAMA_CID"
fi
if [[ -n "$QDRANT_CID" ]]; then
  show_recent_logs "qdrant" "$QDRANT_CID"
fi

exit "$FAILURES"
```

### webapp/Dockerfile

- Bytes leidos: `323`
- Lineas aproximadas: `18`

```
FROM python:3.11-slim

WORKDIR /app

RUN apt-get update && apt-get install -y \
    libmagic1 \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY app.py .
COPY static ./static

EXPOSE 8080

CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8080"]
```

### webapp/app.py

- Bytes leidos: `8465`
- Lineas aproximadas: `268`

```python
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
            "model": model or CHAT_MODEL,
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
    http: httpx.AsyncClient = request.app.state.http
    response = await http.get(f"{OLLAMA_BASE}/api/tags", timeout=30)
    response.raise_for_status()
    payload = response.json()
    items = [model["name"] for model in payload.get("models", [])]
    return {"models": items, "default": CHAT_MODEL}


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
```

### webapp/requirements.txt

- Bytes leidos: `130`
- Lineas aproximadas: `8`

```
fastapi==0.111.0
uvicorn==0.30.1
qdrant-client==1.9.1
httpx==0.27.0
python-multipart==0.0.9
pdfplumber==0.11.0
python-docx==1.1.2
```

### webapp/static/app.js

- Bytes leidos: `5817`
- Lineas aproximadas: `195`

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

- Bytes leidos: `3008`
- Lineas aproximadas: `96`

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

### webapp/static/styles.css

- Bytes leidos: `3938`
- Lineas aproximadas: `250`

```css
:root {
  --bg: #f2efe8;
  --panel: rgba(255, 252, 246, 0.9);
  --panel-strong: #fffaf2;
  --line: rgba(49, 41, 29, 0.14);
  --text: #2e2418;
  --muted: #6f604d;
  --accent: #bf5b2c;
  --accent-strong: #8f3e1a;
  --success: #2f7d4b;
  --shadow: 0 18px 40px rgba(80, 53, 23, 0.12);
}

* {
  box-sizing: border-box;
}

body {
  margin: 0;
  min-height: 100vh;
  font-family: Georgia, "Times New Roman", serif;
  color: var(--text);
  background:
    radial-gradient(circle at top left, rgba(191, 91, 44, 0.16), transparent 28%),
    radial-gradient(circle at top right, rgba(143, 62, 26, 0.12), transparent 25%),
    linear-gradient(180deg, #f7f2ea 0%, var(--bg) 100%);
}

.page-shell {
  max-width: 1280px;
  margin: 0 auto;
  padding: 32px 20px 48px;
}

.hero {
  margin-bottom: 24px;
}

.eyebrow {
  margin: 0 0 8px;
  letter-spacing: 0.18em;
  text-transform: uppercase;
  font-size: 0.75rem;
  color: var(--accent-strong);
}

.hero h1 {
  margin: 0;
  font-size: clamp(2.2rem, 4vw, 4rem);
  line-height: 0.95;
}

.hero-copy {
  max-width: 620px;
  margin: 10px 0 0;
  font-size: 1.05rem;
  color: var(--muted);
}

.grid {
  display: grid;
  grid-template-columns: 360px minmax(0, 1fr);
  gap: 20px;
}

.panel {
  background: var(--panel);
  border: 1px solid var(--line);
  border-radius: 24px;
  box-shadow: var(--shadow);
  padding: 20px;
  backdrop-filter: blur(10px);
}

.panel-head {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
  margin-bottom: 16px;
}

.panel-head.small {
  margin: 16px 0 10px;
}

.panel h2,
.panel h3 {
  margin: 0;
  font-weight: 600;
}

.status-pill {
  display: inline-flex;
  align-items: center;
  border-radius: 999px;
  background: rgba(47, 125, 75, 0.12);
  color: var(--success);
  font-size: 0.82rem;
  padding: 6px 10px;
}

.stack-form,
.chat-form {
  display: grid;
  gap: 14px;
}

.chat-hint {
  margin: -4px 2px 0;
  font-size: 0.84rem;
  color: var(--muted);
}

label {
  display: grid;
  gap: 8px;
  font-size: 0.95rem;
  color: var(--muted);
}

input,
select,
textarea,
button {
  font: inherit;
}

input,
select,
textarea {
  width: 100%;
  border: 1px solid var(--line);
  background: var(--panel-strong);
  border-radius: 16px;
  padding: 12px 14px;
  color: var(--text);
}

textarea {
  resize: vertical;
  min-height: 110px;
}

button {
  border: 0;
  border-radius: 16px;
  background: linear-gradient(135deg, var(--accent) 0%, var(--accent-strong) 100%);
  color: white;
  padding: 12px 16px;
  cursor: pointer;
  transition: transform 150ms ease, opacity 150ms ease;
}

button:hover {
  transform: translateY(-1px);
}

button:disabled {
  opacity: 0.65;
  cursor: wait;
}

.inline-row {
  display: grid;
  grid-template-columns: 1fr auto;
  gap: 10px;
}

.toolbar {
  display: flex;
  justify-content: flex-start;
  margin-bottom: 16px;
}

.tag-list {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.tag {
  border-radius: 999px;
  border: 1px solid var(--line);
  background: rgba(255, 250, 242, 0.92);
  padding: 8px 12px;
  font-size: 0.88rem;
}

.tag.selectable {
  cursor: pointer;
}

.tag.active {
  background: rgba(191, 91, 44, 0.14);
  border-color: rgba(191, 91, 44, 0.4);
  color: var(--accent-strong);
}

.chat-panel {
  display: grid;
  grid-template-rows: auto auto auto 1fr auto;
}

.picker-title {
  margin: 0 0 10px;
  color: var(--muted);
  font-size: 0.92rem;
}

.messages {
  min-height: 380px;
  max-height: 54vh;
  overflow: auto;
  display: grid;
  gap: 12px;
  padding-right: 4px;
  margin: 16px 0;
}

.message {
  padding: 14px 16px;
  border-radius: 18px;
  border: 1px solid var(--line);
  background: rgba(255, 250, 242, 0.75);
}

.message.user {
  background: rgba(191, 91, 44, 0.1);
}

.message p {
  margin: 0;
  white-space: pre-wrap;
}

@media (max-width: 980px) {
  .grid {
    grid-template-columns: 1fr;
  }

  .chat-panel {
    grid-template-rows: auto;
  }

  .messages {
    max-height: none;
  }
}
```
