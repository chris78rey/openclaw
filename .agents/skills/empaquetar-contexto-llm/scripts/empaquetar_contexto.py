#!/usr/bin/env python3
"""
Consolida archivos clave de un proyecto en un unico Markdown para revision por LLM.
"""

from __future__ import annotations

import argparse
import fnmatch
import os
from datetime import datetime, timezone
from pathlib import Path


IMPORTANT_FILENAMES = {
    "readme",
    "readme.md",
    "readme.txt",
    "agents.md",
    "dockerfile",
    "docker-compose.yml",
    "docker-compose.yaml",
    "compose.yml",
    "compose.yaml",
    "makefile",
    "package.json",
    "pyproject.toml",
    "requirements.txt",
    "poetry.lock",
    "pnpm-lock.yaml",
    "package-lock.json",
    "tsconfig.json",
    "vite.config.ts",
    "vite.config.js",
    "next.config.js",
    "next.config.mjs",
}

IMPORTANT_SUFFIXES = {
    ".py",
    ".js",
    ".jsx",
    ".ts",
    ".tsx",
    ".mjs",
    ".cjs",
    ".json",
    ".toml",
    ".yaml",
    ".yml",
    ".md",
    ".txt",
    ".html",
    ".css",
    ".scss",
    ".sh",
    ".ps1",
    ".sql",
}

EXCLUDED_DIRS = {
    ".agents",
    ".git",
    ".hg",
    ".svn",
    ".venv",
    "venv",
    "__pycache__",
    "node_modules",
    "dist",
    "build",
    ".next",
    ".nuxt",
    ".cache",
    ".mypy_cache",
    ".pytest_cache",
    "coverage",
    "target",
    "bin",
    "obj",
    ".idea",
    ".vscode",
}

EXCLUDED_SUFFIXES = {
    ".png",
    ".jpg",
    ".jpeg",
    ".gif",
    ".webp",
    ".ico",
    ".pdf",
    ".zip",
    ".gz",
    ".tar",
    ".tgz",
    ".7z",
    ".rar",
    ".mp3",
    ".mp4",
    ".wav",
    ".mov",
    ".avi",
    ".dll",
    ".so",
    ".dylib",
    ".exe",
    ".class",
    ".jar",
    ".pyc",
    ".pyo",
    ".woff",
    ".woff2",
    ".ttf",
    ".otf",
}

SECRET_PATTERNS = (
    ".env",
    ".env.*",
    "*.pem",
    "*.key",
    "*.crt",
    "*.p12",
    "*.pfx",
    "*secret*",
    "*token*",
    "*credential*",
    "*credentials*",
    "*private*",
    "*id_rsa*",
)

SOURCE_DIR_HINTS = {
    "src",
    "app",
    "apps",
    "backend",
    "frontend",
    "server",
    "client",
    "api",
    "web",
    "webapp",
    "services",
    "rag-api",
    "scripts",
}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Empaqueta archivos clave del proyecto en un solo Markdown."
    )
    parser.add_argument("--root", default=".", help="Raiz del proyecto.")
    parser.add_argument(
        "--output",
        default="revision-llm.md",
        help="Archivo Markdown de salida.",
    )
    parser.add_argument(
        "--include",
        action="append",
        default=[],
        help="Ruta relativa a incluir explicitamente. Repetible.",
    )
    parser.add_argument(
        "--exclude",
        action="append",
        default=[],
        help="Patron glob relativo a excluir. Repetible.",
    )
    parser.add_argument(
        "--max-files",
        type=int,
        default=25,
        help="Cantidad maxima de archivos a incluir cuando se usa autodeteccion.",
    )
    parser.add_argument(
        "--max-bytes-per-file",
        type=int,
        default=30000,
        help="Maximo de bytes por archivo en la salida.",
    )
    parser.add_argument(
        "--all-text",
        action="store_true",
        help="Incluir todos los archivos de texto detectados que pasen los filtros.",
    )
    return parser.parse_args()


def is_secret_path(rel_path: str) -> bool:
    lowered = rel_path.lower()
    return any(fnmatch.fnmatch(lowered, pattern) for pattern in SECRET_PATTERNS)


def is_excluded(rel_path: str, custom_patterns: list[str]) -> bool:
    parts = Path(rel_path).parts
    if any(part.lower() in EXCLUDED_DIRS for part in parts[:-1]):
        return True
    suffix = Path(rel_path).suffix.lower()
    if suffix in EXCLUDED_SUFFIXES:
        return True
    if is_secret_path(rel_path):
        return True
    lowered = rel_path.lower()
    return any(fnmatch.fnmatch(lowered, pattern.lower()) for pattern in custom_patterns)


def is_probably_text(path: Path) -> bool:
    if path.suffix.lower() in IMPORTANT_SUFFIXES:
        return True
    try:
        chunk = path.read_bytes()[:2048]
    except OSError:
        return False
    if b"\x00" in chunk:
        return False
    try:
        chunk.decode("utf-8")
        return True
    except UnicodeDecodeError:
        return False


def score_path(rel_path: str) -> int:
    path = Path(rel_path)
    parts = [part.lower() for part in path.parts]
    name = path.name.lower()
    stem = path.stem.lower()
    suffix = path.suffix.lower()

    score = 0
    if name in IMPORTANT_FILENAMES or stem in IMPORTANT_FILENAMES:
        score += 120
    if suffix in IMPORTANT_SUFFIXES:
        score += 20
    if any(part in SOURCE_DIR_HINTS for part in parts[:-1]):
        score += 35
    depth_penalty = max(len(parts) - 3, 0) * 4
    score -= depth_penalty
    if "test" in parts or "tests" in parts:
        score -= 10
    if name.endswith(".lock"):
        score -= 15
    if "migration" in parts or "migrations" in parts:
        score -= 5
    return score


def collect_candidates(root: Path, excludes: list[str]) -> list[Path]:
    candidates: list[Path] = []
    for path in root.rglob("*"):
        if not path.is_file():
            continue
        rel_path = path.relative_to(root).as_posix()
        if is_excluded(rel_path, excludes):
            continue
        if not is_probably_text(path):
            continue
        candidates.append(path)
    return candidates


def tree_for_paths(paths: list[Path], root: Path) -> str:
    tree: dict[str, dict] = {}
    for path in paths:
        node = tree
        for part in path.relative_to(root).parts:
            node = node.setdefault(part, {})

    lines: list[str] = []

    def walk(node: dict[str, dict], prefix: str = "") -> None:
        items = sorted(node.items(), key=lambda item: (bool(item[1]), item[0].lower()))
        for index, (name, child) in enumerate(items):
            connector = "\\-- " if index == len(items) - 1 else "+-- "
            lines.append(prefix + connector + name)
            extension = "    " if index == len(items) - 1 else "|   "
            walk(child, prefix + extension)

    walk(tree)
    return "\n".join(lines)


def language_for(path: Path) -> str:
    mapping = {
        ".py": "python",
        ".js": "javascript",
        ".jsx": "jsx",
        ".ts": "typescript",
        ".tsx": "tsx",
        ".json": "json",
        ".toml": "toml",
        ".yaml": "yaml",
        ".yml": "yaml",
        ".md": "markdown",
        ".html": "html",
        ".css": "css",
        ".scss": "scss",
        ".sh": "bash",
        ".ps1": "powershell",
        ".sql": "sql",
    }
    return mapping.get(path.suffix.lower(), "")


def read_text_limited(path: Path, max_bytes: int) -> tuple[str, bool]:
    data = path.read_bytes()
    truncated = len(data) > max_bytes
    if truncated:
        data = data[:max_bytes]
    text = data.decode("utf-8", errors="replace")
    return text, truncated


def resolve_includes(root: Path, includes: list[str], excludes: list[str]) -> list[Path]:
    resolved: list[Path] = []
    for raw in includes:
        path = (root / raw).resolve()
        if not path.exists() or not path.is_file():
            raise FileNotFoundError(f"No existe el archivo incluido: {raw}")
        rel_path = path.relative_to(root.resolve()).as_posix()
        if is_excluded(rel_path, excludes):
            raise ValueError(f"El archivo incluido esta excluido por seguridad o filtros: {raw}")
        if not is_probably_text(path):
            raise ValueError(f"El archivo incluido no parece de texto: {raw}")
        resolved.append(path)
    return sorted(set(resolved), key=lambda item: item.relative_to(root).as_posix())


def select_files(root: Path, includes: list[str], excludes: list[str], max_files: int, all_text: bool) -> list[Path]:
    if includes:
        return resolve_includes(root, includes, excludes)

    candidates = collect_candidates(root, excludes)
    if all_text:
        return sorted(candidates, key=lambda item: item.relative_to(root).as_posix())

    ranked = sorted(
        candidates,
        key=lambda item: (
            -score_path(item.relative_to(root).as_posix()),
            item.relative_to(root).as_posix(),
        ),
    )
    return ranked[:max_files]


def render_output(root: Path, files: list[Path], max_bytes_per_file: int) -> str:
    timestamp = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")
    lines: list[str] = [
        "# Contexto Consolidado Para Revision LLM",
        "",
        f"- Raiz: `{root}`",
        f"- Generado: `{timestamp}`",
        f"- Archivos incluidos: `{len(files)}`",
        "",
        "## Archivos incluidos",
        "",
    ]

    for path in files:
        rel_path = path.relative_to(root).as_posix()
        lines.append(f"- `{rel_path}`")

    lines.extend(["", "## Arbol resumido", "", "```text"])
    tree = tree_for_paths(files, root)
    lines.append(tree if tree else "(sin archivos)")
    lines.extend(["```", "", "## Contenido", ""])

    for path in files:
        rel_path = path.relative_to(root).as_posix()
        text, truncated = read_text_limited(path, max_bytes_per_file)
        language = language_for(path)
        line_count = text.count("\n") + (0 if not text else 1)
        lines.append(f"### {rel_path}")
        lines.append("")
        lines.append(f"- Bytes leidos: `{min(path.stat().st_size, max_bytes_per_file)}`")
        lines.append(f"- Lineas aproximadas: `{line_count}`")
        if truncated:
            lines.append(f"- Aviso: truncado a `{max_bytes_per_file}` bytes")
        lines.append("")
        lines.append(f"```{language}")
        lines.append(text.rstrip("\n"))
        lines.append("```")
        lines.append("")

    return "\n".join(lines).rstrip() + "\n"


def main() -> int:
    args = parse_args()
    root = Path(args.root).resolve()
    if not root.exists() or not root.is_dir():
        raise SystemExit(f"La raiz no existe o no es directorio: {root}")

    output_path = Path(args.output)
    if not output_path.is_absolute():
        output_path = root / output_path

    excludes = list(args.exclude)
    try:
        files = select_files(root, args.include, excludes, args.max_files, args.all_text)
    except (FileNotFoundError, ValueError) as exc:
        raise SystemExit(str(exc)) from exc

    if output_path.exists():
        files = [path for path in files if path.resolve() != output_path.resolve()]

    if not files:
        raise SystemExit("No se encontraron archivos para incluir.")

    output = render_output(root, files, args.max_bytes_per_file)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(output, encoding="utf-8")

    print(f"Archivo generado: {output_path}")
    print(f"Archivos incluidos: {len(files)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
