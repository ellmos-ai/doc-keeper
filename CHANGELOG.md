# Changelog

## [0.1.0] - 2026-11-01
- Initial standalone release of `doc-keeper` (`ellmos.module.v2`):
  - Generic repository claim extractor (`extract_repo_claims`) for file paths, Python AST symbols, and CLI flags.
  - Deterministic 3-Cause Documentation Classifier (`classify_doc_reality_diff`): distinguishes `unintended_erosion`, `planned_terraforming_pending`, and `completed_terraforming_doc_lag`.
  - Transparent & combinable Decision Processing Rules (`resolve_doc_machine_dispatch`, `config/doc_machine.config.json`).
  - CLI (`python -m doc_keeper audit <repo>`) and Agent-Library role (`doc-keeper`).
