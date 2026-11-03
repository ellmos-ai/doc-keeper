# Changelog

## [Unreleased]
- Release-Readiness & Final Gate Härtung (10/10 PASS):
  - `.gitignore` um Mindestmuster (`*.pyc`, `.env`, `*.db`, `data/`, etc.), Multi-Host-Locks und Secret-Schutz gehärtet (Gate 1 PASS).
  - `pyproject.toml` um `[tool.pytest.ini_options]` (`pythonpath = ["src"]`) und Trove-Classifier `"Typing :: Typed"` ergänzt.
  - `ruff check` Bereinigung ungenutzter Imports in `src/doc_keeper/cli.py` und `tests/test_doc_keeper.py` durchgeführt.
  - Standardisiertes `TODO.md` mit 10-Kategorien `## STATUS`-Tabelle, Audit-Metadaten und formalisierten Aufgaben (`TASK-DK-01` bis `TASK-DK-06`) etabliert (Gate 10 PASS).
  - Deutsche Texte in `classifier.py` und `config/doc_machine.config.json` auf echte Umlaute (ä, ö, ü, ß) harmonisiert.
  - Vertragstestsuite `tests/test_metadata.py` mit 8 Contract-Tests ergänzt (PEP 621/561, .gitignore, py.typed, TODO.md, Manifest, Umlaut-Konfiguration, Mermaid, Pfad- & Secret-Neutralität).
  - `final_gate_check.py` 10 PASS, 0 FAIL, 0 WARN erzielt (READY FOR PUBLIC RELEASE).

## [0.1.0] - 2026-11-01
- Initial standalone release of `doc-keeper` (`ellmos.module.v2`):
  - Generic repository claim extractor (`extract_repo_claims`) for file paths, Python AST symbols, and CLI flags.
  - Deterministic 3-Cause Documentation Classifier (`classify_doc_reality_diff`): distinguishes `unintended_erosion`, `planned_terraforming_pending`, and `completed_terraforming_doc_lag`.
  - Transparent & combinable Decision Processing Rules (`resolve_doc_machine_dispatch`, `config/doc_machine.config.json`).
  - CLI (`python -m doc_keeper audit <repo>`) and Agent-Library role (`doc-keeper`).
