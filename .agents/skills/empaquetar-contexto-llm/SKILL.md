---
name: empaquetar-contexto-llm
description: Consolidar archivos clave de un proyecto en un unico archivo Markdown listo para darselo a otro LLM para revision tecnica, auditoria, onboarding o analisis de arquitectura. Usar cuando el usuario pida juntar codigo y configuracion relevante en un solo archivo, preparar contexto para un revisor externo, resumir el proyecto para otra IA, o evitar copiar muchos archivos manualmente.
---

# Empaquetar Contexto LLM

## Resumen

Generar un archivo unico con los archivos mas relevantes del proyecto, delimitados y ordenados para que otro LLM pueda revisarlos.
Usar el script `scripts/empaquetar_contexto.py` para seleccionar archivos utiles, excluir ruido comun y producir una salida reproducible.

## Flujo

1. Entender que quiere revisar el usuario.
2. Elegir si conviene usar autodeteccion o pasar archivos explicitamente.
3. Ejecutar `scripts/empaquetar_contexto.py` para producir el archivo consolidado.
4. Revisar rapidamente el resultado para comprobar que no faltan archivos clave y que no se filtraron secretos.
5. Responder indicando la ruta del archivo generado.

## Seleccion de archivos

Preferir autodeteccion cuando:
- El usuario pide "juntar lo importante" sin mas detalle.
- El repositorio es chico o mediano.
- Quieres incluir configuracion principal, documentacion y codigo fuente sin decidir archivo por archivo.

Preferir `--include` cuando:
- El usuario menciona componentes concretos.
- El repositorio es grande y quieres controlar el contexto.
- Hay carpetas pesadas o codigo generado que no debe entrar.

Excluir por defecto:
- Secretos y archivos sensibles como `.env`, `*.pem`, `*.key`, credenciales, tokens o dumps.
- Dependencias vendorizadas y artefactos como `node_modules`, `dist`, `build`, `.git`, caches y binarios.
- Archivos demasiado grandes salvo que el usuario los pida.

## Comandos base

Autodeteccion con salida estandar:

```bash
python .agents/skills/empaquetar-contexto-llm/scripts/empaquetar_contexto.py --root . --output revision-llm.md
```

Seleccion explicita de archivos:

```bash
python .agents/skills/empaquetar-contexto-llm/scripts/empaquetar_contexto.py --root . --output revision-backend.md --include AGENTS.md --include rag-api/main.py --include rag-api/requirements.txt --include docker-compose.yml
```

Incluir mas contexto manteniendo limites:

```bash
python .agents/skills/empaquetar-contexto-llm/scripts/empaquetar_contexto.py --root . --output revision-amplia.md --max-files 40 --max-bytes-per-file 50000
```

## Salida esperada

El archivo generado debe incluir:
- Cabecera con ruta raiz y fecha.
- Lista de archivos incluidos.
- Arbol resumido del proyecto.
- Bloques por archivo con delimitadores claros y contenido en fences.
- Avisos de truncado cuando un archivo supera el limite configurado.

## Reglas

1. No incluir secretos por defecto aunque aparezcan en el repositorio.
2. No meter binarios ni archivos generados salvo pedido explicito.
3. Si el usuario quiere revision de una parte concreta, reducir el paquete a esa parte.
4. Si el proyecto es muy grande, preferir `--include`, `--exclude`, `--max-files` y `--max-bytes-per-file`.
5. Mencionar siempre la ruta del archivo consolidado en la respuesta final.

## Script

Usar `scripts/empaquetar_contexto.py`.
Leer el `--help` del script solo si necesitas recordar flags exactos; no cargues mas contexto del necesario.
