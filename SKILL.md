---
name: doc-keeper
version: 0.1.0
description: >
  Standalone 3-Cause Documentation Auditor & Decision Rule Router for Ocean, BACH, and
  arbitrary Git repositories. Extracts verifiable file-path and Python-AST symbol claims
  from markdown documentation and classifies discrepancies into unintended_erosion,
  planned_terraforming_pending, or completed_terraforming_doc_lag.
license: MIT
homepage: https://github.com/ellmos-ai/doc-keeper
---

# doc-keeper — Product Skill (P-022)

> **Product Skill for AI Agents & Operators** | Version: `0.1.0` | Runtime: Python `>=3.10` (stdlib only)

## 1. Purpose & Scope

Use `doc-keeper` (`ellmos-doc-keeper`) whenever you need to audit whether repository documentation (`README*.md`, `SKILL*.md`, `docs/**/*.md`) matches actual codebase reality without blindly overwriting intended target architecture (**SOLL**).

### What `doc-keeper` Does
- Extracts verifiable claims from documentation via `extract_repo_claims()`:
  - Backticked or Markdown-linked file paths
  - Backticked Python function/class call symbols (e.g., `audit_repository()`, `extract_repo_claims()`)
- Verifies claims statically against the repository filesystem, Python AST (`ast.parse`), plan documents (`TODO.md`, `DECISIONS.md`, `ROADMAP.md`, `AKTUELLER-PLAN.md`, `ANFORDERUNGEN-DETAIL.md`), and local `git log -S` history via `audit_repository()`.
- Classifies every mismatch deterministically via `classify_doc_reality_diff()` into one of **3 Causes**:
  1. **`unintended_erosion`**: Claimed artifact existed in `git log -S` history and broke/drifted unintentionally -> preserves SOLL in documentation and dispatches `["local_taskplan", "user_notification"]` (P1 repair task).
  2. **`planned_terraforming_pending`**: Claimed artifact is documented in roadmap/plan files (`TODO.md`, `DECISIONS.md`, etc.) and has not been implemented yet -> dispatches `["local_taskplan"]` (P2 task) and distinguishes **SOLL vs. IST**.
  3. **`completed_terraforming_doc_lag`**: Code was intentionally advanced without matching roadmap lag -> dispatches `["local_doc_update"]`.
- Routes actions transparently via `resolve_doc_machine_dispatch()` using `load_doc_machine_config()` and `config/doc_machine.config.json`.

### What `doc-keeper` Does NOT Do
- Does **not** execute untrusted repository code (uses static `ast.parse()` only).
- Does **not** perform network calls or modify remote repositories (`boundaries.network = "none"`).
- Does **not** automatically mutate files during `audit` or `rules` (strictly read-only unless `--output` is passed to write a JSON report file).

---

## 2. Installation & Prerequisites

- **Prerequisites:** Python `>=3.10`; optional `git` on `PATH` for `git log -S` erosion detection.
- **Zero third-party runtime dependencies:** Uses Python standard library only.

```bash
# Recommended: isolated virtual environment
python -m venv .venv
# Linux/macOS: source .venv/bin/activate
# Windows:     .venv\Scripts\activate
pip install -e .
```

---

## 3. Machine Interfaces (CLI & Python API)

### CLI Entry Points (`src/doc_keeper/cli.py`)

| Command | Purpose | Output |
|---|---|---|
| `python -m doc_keeper audit [repo] --json` | Audit repository docs vs. code reality (default `.`) | `ellmos.doc-keeper-audit-report.v1` JSON on stdout |
| `python -m doc_keeper audit [repo] --output report.json` | Write structured JSON audit report to file | JSON file at `--output` path |
| `python -m doc_keeper rules [repo]` | Print effective merged configuration | Merged `ellmos.doc-machine.config.v1` JSON on stdout |
| `doc-keeper audit [repo] --json` | Console script installed via `pyproject.toml` | Same as `python -m doc_keeper audit` |

- **Exit codes:** `0` on successful audit/rules execution; `2` on invalid CLI arguments (`argparse`).

### Python API (`src/doc_keeper/__init__.py`)

```python
from pathlib import Path
from doc_keeper import (
    audit_repository,
    classify_doc_reality_diff,
    extract_repo_claims,
    load_doc_machine_config,
    resolve_doc_machine_dispatch,
)

claims = extract_repo_claims(Path("."))
report = audit_repository(Path("."))
cfg = load_doc_machine_config(workspace_root=Path("."))
```

---

## 4. Verification & Readback

```bash
# 1. Verify CLI help and rules output
python -m doc_keeper --help
python -m doc_keeper rules .

# 2. Run self-audit and inspect summary counts
python -m doc_keeper audit . --json

# 3. Run unit & contract test suite
python -m pytest -ra -v
```

Confirm in the JSON output:
- `"schema": "ellmos.doc-keeper-audit-report.v1"`
- `"summary.total_claims_probed"` matches total extracted claims
- Any non-zero `unintended_erosion`, `planned_terraforming_pending`, or `completed_terraforming_doc_lag` entries include a `"dispatch"` object with `"decision_rule_trace"`.

---

## 5. Related Repository Files

- [README.md](README.md) / [README_de.md](README_de.md) — Bilingual documentation
- [llms.txt](llms.txt) / [llm.txt](llm.txt) — Machine-readable LLM entry index
- [config/doc_machine.config.json](config/doc_machine.config.json) — Default Decision Processing Rules
- [prompts/DOC-KEEPER.en.md](prompts/DOC-KEEPER.en.md) / [prompts/DOC-KEEPER.de.md](prompts/DOC-KEEPER.de.md) — Agent role prompts
- [ellmos-module.v2.json](ellmos-module.v2.json) — Module manifest (`ellmos.module.v2`)
