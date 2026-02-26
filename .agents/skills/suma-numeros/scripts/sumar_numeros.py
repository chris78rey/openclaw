#!/usr/bin/env python3
"""Suma numeros desde argumentos o stdin.

Uso:
  python scripts/sumar_numeros.py 1 2 3.5
  echo "1, 2; 3 4" | python scripts/sumar_numeros.py
"""

from __future__ import annotations

import argparse
import re
import sys
from decimal import Decimal, InvalidOperation


def tokenize(raw: str) -> list[str]:
    return [tok for tok in re.split(r"[\s,;]+", raw.strip()) if tok]


def parse_values(tokens: list[str]) -> tuple[list[Decimal], list[str]]:
    values: list[Decimal] = []
    ignored: list[str] = []
    for tok in tokens:
        try:
            values.append(Decimal(tok))
        except InvalidOperation:
            ignored.append(tok)
    return values, ignored


def main() -> int:
    parser = argparse.ArgumentParser(description="Suma numeros enteros o decimales.")
    parser.add_argument("numbers", nargs="*", help="Numeros separados por espacio.")
    args = parser.parse_args()

    raw = " ".join(args.numbers).strip()
    if not raw:
        raw = sys.stdin.read().strip()

    if not raw:
        print("Error: no se recibieron numeros.")
        return 2

    tokens = tokenize(raw)
    values, ignored = parse_values(tokens)

    if not values:
        print("Error: no hay numeros validos para sumar.")
        if ignored:
            print(f"Ignorados: {', '.join(ignored)}")
        return 2

    total = sum(values, Decimal("0"))
    parsed = ", ".join(str(v) for v in values)

    print(f"Valores: {parsed}")
    print(f"Total: {total}")
    if ignored:
        print(f"Ignorados: {', '.join(ignored)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
