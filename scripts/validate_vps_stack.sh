#!/usr/bin/env bash
set -u

DOMAIN="${1:-bot.da-tica.com}"
NETWORK="${DOCKER_NETWORK:-coolify}"
CHAT_MODEL="${CHAT_MODEL:-llama3.2:3b}"
EMBED_MODEL="${EMBED_MODEL:-bge-m3}"
WEB_NAME_FILTER="${WEB_NAME_FILTER:-webapp}"
OLLAMA_NAME_FILTER="${OLLAMA_NAME_FILTER:-ollama}"
QDRANT_NAME_FILTER="${QDRANT_NAME_FILTER:-qdrant}"
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
  labels="$(docker inspect --format '{{json .Config.Labels}}' "$cid" 2>/dev/null)"

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

  if printf '%s' "$labels" | grep -q '"traefik.docker.network":"'"${NETWORK}"'"'; then
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

  if docker exec "$cid" sh -lc "wget -qO- '$url' >/dev/null 2>&1 || curl -fsS '$url' >/dev/null 2>&1"; then
    pass "${label} responde en ${url}"
  else
    fail "${label} no responde en ${url}"
    print_fix "Revisa conectividad interna, nombre DNS del contenedor y logs del servicio destino."
  fi
}

check_http_local() {
  local url="$1"
  local label="$2"
  if wget -qO- "$url" >/dev/null 2>&1 || curl -fsS "$url" >/dev/null 2>&1; then
    pass "${label} responde en ${url}"
  else
    fail "${label} no responde en ${url}"
    print_fix "Si el contenedor esta healthy pero este endpoint falla, revisa Traefik o el puerto expuesto."
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
  MODELS="$(docker exec "$OLLAMA_CID" ollama list 2>/dev/null || true)"
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
    print_fix "Revisa logs de Ollama y prueba 'docker exec -it $OLLAMA_CID ollama list'."
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

  if curl -kfsS -H "Host: ${DOMAIN}" "https://${DOMAIN}/api/health" >/dev/null 2>&1; then
    pass "El dominio publico responde por HTTPS"
  else
    fail "El dominio publico no responde por HTTPS"
    print_fix "Si webapp esta healthy, el problema suele ser Traefik/Coolify, labels o certificado."
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
