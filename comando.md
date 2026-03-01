# Comandos para probar la misma pregunta con tres modelos

Usa estos bloques tal cual.

La pregunta de prueba sera:

```text
Como se deben subir los archivos?
```

## 1. Probar `llama3.2:3b` directo contra Ollama

```bash
docker exec $(docker ps -qf name=webapp) sh -lc '
curl http://ollama:11434/api/generate \
  -H "Content-Type: application/json" \
  -d '"'"'{
    "model": "llama3.2:3b",
    "prompt": "Como se deben subir los archivos?",
    "stream": false
  }'"'"'
'
```

## 2. Probar `qwen2.5:7b` directo contra Ollama

```bash
docker exec $(docker ps -qf name=webapp) sh -lc '
curl http://ollama:11434/api/generate \
  -H "Content-Type: application/json" \
  -d '"'"'{
    "model": "qwen2.5:7b",
    "prompt": "Como se deben subir los archivos?",
    "stream": false
  }'"'"'
'
```

## 3. Probar `bge-m3` directo contra Ollama

`bge-m3` es un modelo de embeddings, no de chat. Este bloque sirve para confirmar que no debe usarse para responder preguntas.

```bash
docker exec $(docker ps -qf name=webapp) sh -lc '
curl http://ollama:11434/api/generate \
  -H "Content-Type: application/json" \
  -d '"'"'{
    "model": "bge-m3",
    "prompt": "Como se deben subir los archivos?",
    "stream": false
  }'"'"'
'
```

## 4. Probar `llama3.2:3b` en la app web con RAG

```bash
curl https://bot.da-tica.com/api/chat \
  -H "Content-Type: application/json" \
  -d '{
    "question": "Como se deben subir los archivos?",
    "collections": ["prueba"],
    "model": "llama3.2:3b"
  }'
```

## 5. Probar `qwen2.5:7b` en la app web con RAG

```bash
curl https://bot.da-tica.com/api/chat \
  -H "Content-Type: application/json" \
  -d '{
    "question": "Como se deben subir los archivos?",
    "collections": ["prueba"],
    "model": "qwen2.5:7b"
  }'
```

## 6. Probar `bge-m3` en la app web con RAG

```bash
curl https://bot.da-tica.com/api/chat \
  -H "Content-Type: application/json" \
  -d '{
    "question": "Como se deben subir los archivos?",
    "collections": ["prueba"],
    "model": "bge-m3"
  }'
```
