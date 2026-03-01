---
name: comandos-en-markdown
description: Preparar comandos operativos en un archivo Markdown listo para copiar y pegar. Usar cuando el usuario pida comandos para ejecutar, pasos de terminal, bloques para VPS, secuencias de deploy o verificacion, o indique que prefiere no copiar desde la terminal. En este repositorio, regenerar G:/opencode/openclaw/comando.md desde cero con bloques de codigo claros y pequenos.
---

# Comandos En Markdown

## Resumen

Generar un archivo `comando.md` con los comandos exactos que el usuario debe ejecutar.
Evitar dejar los comandos solo en la respuesta de chat o depender de que el usuario los copie desde la terminal.

## Flujo

1. Inferir qué comandos necesita el usuario y en qué entorno los va a pegar.
2. Borrar el archivo existente `G:/opencode/openclaw/comando.md` y recrearlo desde cero.
3. Escribir una guia breve seguida de bloques de codigo listos para copiar.
4. Preferir bloques chicos por tarea o paso. Si una secuencia es sensible, separarla en varios bloques en vez de mezclar demasiadas acciones.
5. Mantener los comentarios fuera del bloque de codigo salvo que sean estrictamente necesarios.
6. Si hay variables o placeholders, explicarlos en una linea corta antes del bloque.
7. Responder al usuario indicando que los comandos quedaron en `comando.md`.

## Reglas

1. No pedir al usuario que copie comandos desde la salida de la terminal si puedes dejarlos en `comando.md`.
2. No acumular comandos viejos: regenerar el archivo completo en cada pedido nuevo de comandos, salvo que el usuario pida anexar.
3. Usar fences con lenguaje cuando aplique, normalmente `bash`.
4. Escribir comandos exactos, una linea por accion cuando eso mejore la copia y el pegado.
5. No ocultar pasos destructivos o sensibles; marcarlos claramente fuera del bloque antes de mostrarlos.
6. Si un comando depende del resultado del paso anterior, decirlo en una frase corta y separarlo en otro bloque.
7. Mantener el archivo enfocado al pedido actual; no convertirlo en una bitacora acumulativa.

## Formato

Usar esta estructura base:

```md
# Comandos para <objetivo>

Breve contexto de una linea.

## 1. <paso>

```bash
comando exacto
```
```

## Casos comunes

- Si el usuario dice "dame los comandos", "pasame el comando", "que ejecuto", "dejame un markdown para pegar", activar esta skill.
- Si hay que verificar un despliegue, separar en bloques como `docker ps`, logs, healthchecks y pruebas puntuales.
- Si hay que editar variables antes de correr algo, dejar primero la nota y luego el bloque con exportaciones o asignaciones.
