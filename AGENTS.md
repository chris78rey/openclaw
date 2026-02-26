# Repository Guidelines

## Project Structure & Module Organization
This repository currently hosts Codex skills.

- `.agents/skills/`: skill folders recognized by Codex.
- `.agents/skills/suma-numeros/`: active example skill.
- `.agents/skills/<skill>/SKILL.md`: required skill definition (frontmatter + instructions).
- `.agents/skills/<skill>/agents/openai.yaml`: UI metadata for skill chips/lists.
- `.agents/skills/<skill>/scripts/`: executable helpers (Python, shell, etc.).
- `instr.md`: local notes/instructions (not part of skill runtime).

When adding a new skill, follow the same folder layout and keep each skill self-contained.

## Build, Test, and Development Commands
There is no global build system yet. Work at skill level.

- `python .agents/skills/suma-numeros/scripts/sumar_numeros.py 1 2 3.5`
  Runs the skill script with CLI args.
- `echo "1, 2; 3" | python .agents/skills/suma-numeros/scripts/sumar_numeros.py`
  Runs the same script via `stdin`.
- `python C:\Users\crrb\.codex\skills\.system\skill-creator\scripts\quick_validate.py .agents/skills/suma-numeros`
  Validates skill structure and frontmatter.

## Coding Style & Naming Conventions
- Use Python 3 with 4-space indentation and readable, small functions.
- Prefer ASCII in files unless a clear reason requires Unicode.
- Skill folder names: lowercase hyphen-case (example: `suma-numeros`).
- Script names: snake_case (example: `sumar_numeros.py`).
- Keep `SKILL.md` concise and imperative; put only trigger criteria in frontmatter `description`.

## Testing Guidelines
- Test scripts with representative valid and invalid inputs.
- For numeric parsers, include decimals, separators (space/comma/semicolon), and ignored tokens.
- Re-run `quick_validate.py` after any `SKILL.md` or metadata update.

## Commit & Pull Request Guidelines
No commit history exists yet, so use this baseline:

- Commit style: `type(scope): short summary` (e.g., `feat(skill): add suma-numeros parser`).
- Keep commits focused (one skill or one behavior change per commit).
- PRs should include:
  - What changed and why
  - Paths touched (for example, `.agents/skills/suma-numeros/...`)
  - Validation evidence (command run + result)
