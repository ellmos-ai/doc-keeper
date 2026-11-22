# Changelog

## [Unreleased]
- Discoverability, Bilingual Architecture & Policy P-022 (Path B):
  - Added dark-mode terminal workflow vector asset (`assets/terminal-workflow.svg`) and embedded it in `README.md` and `README_de.md`.
  - Added deterministic audit & dispatch Mermaid `sequenceDiagram` alongside the 3-Cause flowchart and synchronized 9-section bilingual navigation (`README.md` & `README_de.md`), Python API quickstart, and verified shields.io badges (`14 passed`, `2026-11-22`).
  - Added Policy P-022 machine-readable LLM entry points (`SKILL.md`, `llms.txt`, `llm.txt`) and copyable `Install with your LLM` / `Mit deinem LLM installieren` prompt blocks.
  - Added bilingual Community Health files (`CODE_OF_CONDUCT.md`, `CONTRIBUTING.md`, `.github/ISSUE_TEMPLATE/{bug_report.md,feature_request.md,config.yml}`).
  - Added PEP 621 SEO `keywords`, `[project.urls]`, and `[project.optional-dependencies].dev` in `pyproject.toml` (version `0.1.0` strictly frozen).
  - Expanded `tests/test_metadata.py` with 4 discoverability, P-022, community-health, and self-audit dogfooding contract tests (`14 passed`).
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
