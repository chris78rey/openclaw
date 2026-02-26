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
