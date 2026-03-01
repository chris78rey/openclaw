# Comandos para verificar red y conectividad entre openclaw y ollama

Usa estos bloques tal cual.

## 1. Ver que contenedores estan en la red `coolify`

```bash
docker network inspect coolify --format='{{range .Containers}}{{.Name}} {{end}}'
```

## 2. Probar conectividad directa desde openclaw hacia Ollama

```bash
docker exec $(docker ps -qf name=openclaw) curl -s http://ollama:11434/api/tags
```
