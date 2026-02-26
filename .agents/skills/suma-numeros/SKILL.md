---
name: suma-numeros
description: Sumar numeros enteros o decimales y devolver el total con formato claro. Usar cuando el usuario pida calcular una suma, totalizar listas de valores, o validar rapidamente un resultado numerico.
---

# Suma Numeros

## Resumen

Calcular sumas de forma directa en chat o por script.
Preferir `scripts/sumar_numeros.py` cuando haya muchos valores, separadores mixtos o necesidad de reproducibilidad.

## Flujo

1. Extraer todos los numeros del pedido del usuario.
2. Si son pocos, sumar mentalmente y responder el total.
3. Si son muchos o ambiguos, ejecutar `scripts/sumar_numeros.py`.
4. Mostrar:
- Valores interpretados
- Total
- Nota corta si hubo tokens ignorados

## Script

Ejecutar:

```bash
python scripts/sumar_numeros.py 10 20 30.5
```

Separadores soportados:
- Espacio, coma, punto y coma, salto de linea, tab

Entrada por `stdin`:

```bash
echo "1, 2; 3 4" | python scripts/sumar_numeros.py
```

## Reglas

1. Usar punto (`.`) para decimales.
2. Ignorar tokens no numericos y reportarlos.
3. Si no hay numeros validos, responder error claro y pedir nueva entrada.
