# Comandos para priorizar velocidad sin reindexar

Objetivo: probar `qwen2.5:0.5b` sobre la coleccion `oracle` sin tocar embeddings ni Qdrant.

No reindexes todavia. Solo cambia `CHAT_MODEL`.

## 1. Ver modelos disponibles en Ollama

```bash
docker exec $(docker ps -qf name=ollama) ollama list
```

## 2. Descargar `qwen2.5:0.5b`

```bash
docker exec $(docker ps -qf name=ollama) ollama pull qwen2.5:0.5b
```

## 3. Cambiar el modelo de chat en Coolify o en tu `.env`

```text
CHAT_MODEL=qwen2.5:0.5b
```

## 4. Redeployar solo `webapp` y `ollama`

Si usas Docker Compose directo:

```bash
docker compose up -d --build webapp ollama
```

## 5. Verificar que la API expone el nuevo modelo por defecto

```bash
curl -s https://bot.da-tica.com/api/models
```

## 6. Medir primera consulta sobre `oracle`

```bash
curl -s -o /tmp/oracle-fast-1.json -w "\nhttp_code=%{http_code}\ntime_starttransfer=%{time_starttransfer}\ntime_total=%{time_total}\n" \
  https://bot.da-tica.com/api/chat \
  -H "Content-Type: application/json" \
  -d '{
    "question": "Como se debe arreglar el AWR?",
    "collections": ["oracle"],
    "model": null
  }'
```

## 7. Medir 5 corridas calientes

```bash
for i in 1 2 3 4 5; do
  echo "run=$i"
  curl -s -o /dev/null -w "http_code=%{http_code} time_starttransfer=%{time_starttransfer} time_total=%{time_total}\n" \
    https://bot.da-tica.com/api/chat \
    -H "Content-Type: application/json" \
    -d '{
      "question": "Como se debe arreglar el AWR?",
      "collections": ["oracle"],
      "model": null
    }'
done
```

## 8. Si quieres comparar contra el modelo anterior

```bash
for i in 1 2 3; do
  echo "run=$i"
  curl -s -o /dev/null -w "http_code=%{http_code} time_starttransfer=%{time_starttransfer} time_total=%{time_total}\n" \
    https://bot.da-tica.com/api/chat \
    -H "Content-Type: application/json" \
    -d '{
      "question": "Como se debe arreglar el AWR?",
      "collections": ["oracle"],
      "model": "llama3.2:3b"
    }'
done
```

## 9. Regla de decision

Si `qwen2.5:0.5b` baja fuerte la latencia y la calidad sigue aceptable, dejalo como default.

```text
Prioridad velocidad:
1. qwen2.5:0.5b
```

## 10. Solo si luego cambias embeddings, ahi si reindexas

Esto NO es para ahora. Solo aplica si cambias `EMBED_MODEL` o `EMBED_DIM`.

```text
Cambiar CHAT_MODEL: no reindexa
Cambiar EMBED_MODEL: si reindexa
Cambiar EMBED_DIM: si reindexa
```
