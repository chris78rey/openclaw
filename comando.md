# Comandos de verificacion para el VPS

Usa estos bloques tal cual.

## 1. Verificar contenedores activos

```bash
docker ps | grep -E "claw|ollama|rag|qdrant"
```

## 2. Verificar log reciente de OpenClaw

```bash
docker ps --format '{{.Names}}' | grep openclaw | head -n 1 | xargs docker logs --tail 80
```

## 3. Verificar log reciente de Ollama

```bash
docker ps --format '{{.Names}}' | grep ollama | head -n 1 | xargs docker logs --tail 80
```

## 4. Comprobar modelo activo y variable OLLAMA_MODEL en OpenClaw

```bash
CONTAINER=$(docker ps --format '{{.Names}}' | grep openclaw | head -n 1)
echo "CONTAINER=$CONTAINER"
docker exec -it "$CONTAINER" sh -lc 'echo "OLLAMA_MODEL=$OLLAMA_MODEL"'
docker logs --tail 80 "$CONTAINER" | grep "agent model"
```

## 5. Prueba directa de generacion desde OpenClaw hacia Ollama

```bash
cat > /tmp/probar_ollama.sh <<'EOF'
#!/bin/bash
set -e

CONTAINER="$(docker ps --format '{{.Names}}' | grep openclaw | head -n 1)"
echo "CONTAINER=$CONTAINER"

docker exec -i "$CONTAINER" sh <<'INNER'
set -e

echo '== llama3.2:3b =='
cat >/tmp/llama.json <<'JSON'
{"model":"llama3.2:3b","prompt":"Di hola en una frase corta","stream":false}
JSON
curl -s http://ollama:11434/api/generate -H 'Content-Type: application/json' --data @/tmp/llama.json
echo
echo

echo '== qwen2.5:7b =='
cat >/tmp/qwen.json <<'JSON'
{"model":"qwen2.5:7b","prompt":"Di hola en una frase corta","stream":false}
JSON
curl -s http://ollama:11434/api/generate -H 'Content-Type: application/json' --data @/tmp/qwen.json
echo
INNER
EOF
chmod +x /tmp/probar_ollama.sh
/tmp/probar_ollama.sh
```

## 6. Confirmar que no reaparecieron errores conocidos

```bash
docker ps --format '{{.Names}}' | grep openclaw | head -n 1 | xargs docker logs --tail 200 | grep -E "allowedOrigins|JSON5 parse failed|context window too small|fetch failed|Failed to discover Ollama models"
```
