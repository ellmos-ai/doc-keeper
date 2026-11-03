# TODO — doc-keeper

## STATUS

| Category | Status | Notes |
|----------|--------|-------|
| Secrets | :green_circle: OK | 0 Secrets in getrackten Dateien; AST- und Text-Scan sauber |
| Private Data (PII) | :green_circle: OK | 0 personenbezogene Entwicklerdaten oder PII in getrackten Dateien |
| Hardcoded Paths | :green_circle: OK | Keine hardcodierten Entwickler-Pfade (<HOME>/...); portable relative Pfade |
| Database Files | :green_circle: OK | 0 `.db` oder SQLite-Dateien im Repository getrackt |
| .env Files | :green_circle: OK | 0 `.env`-Dateien getrackt; `.gitignore` schützt Umgebungsvariablen |
| BACH Internals | :green_circle: OK | 0 BACH-interne Dokumente; eigenständiges, portables Audit-Werkzeug |
| .gitignore | :green_circle: OK | Alle Pflichtmuster (`__pycache__`, `*.pyc`, `.env`, `*.db`, `data/`, etc.) gehärtet |
| Language & Parity | :green_circle: OK | Englisches `README.md`, zweisprachiges deutsches `README_de.md`, echte Umlaute |
| LICENSE & SBOM | :green_circle: OK | MIT-Lizenz, Level 1 SBOM (`THIRD_PARTY_LICENSES.md`), PEP 639 Metadaten |
| Overall | **PASS (10/10 Gates)** | `final_gate_check.py` 10 PASS, 0 FAIL, 0 WARN; Pytest grün |

**Audit-Datum:** 2026-11-03 (Geprüft durch Antigravity / Gemini worker via `[AI_MODULES_CARE]`)<br>
**Gate-Check-Ergebnis:** 0 (10 PASS, 0 FAIL, 0 WARN — READY FOR PUBLIC RELEASE)<br>
**Testsuite-Status:** Alle Pytest-Tests bestanden (100% grün auf Windows)

## Offene Punkte

- [ ] **TASK-DK-01: Erweiterte Claim-Parser für API-Routes & Type-Annotations** (`effort=medium`, `scope=features`, priority `normal`).
  - **Ziel:** `extract_repo_claims` um automatisierte Erkennung von FastAPI/Flask-Routen und Funktions-Signaturen erweitern.
  - **Definition of Done:** Parser extrahiert HTTP-Methoden und Typannotationen aus Docstrings und Code.

- [ ] **TASK-DK-02: Optionale Task-Master- und MarbleRun-Direktanbindung** (`effort=low`, `scope=integrations`, priority `normal`).
  - **Ziel:** Direkte Dispatch-Ausführung gegen `~/.taskplan/taskplan.db` bei `local_taskplan` Zweig realisieren.
  - **Definition of Done:** Unit-Tests verifizieren SQLite-Taskeinstellung ohne externe Netzwerkaufrufe.

## Abgeschlossene Aufgaben

- [x] **TASK-DK-03: Final Gate Check Härtung (10/10 PASS), .gitignore-Schutz & Testsuite-Setup (v0.1.0)** (`effort=low`, `scope=hygiene`, priority `high`).
  - **Ergebnis:** `.gitignore` um standardisierte Ausschlussmuster gehärtet (Gate 1 PASS); `pyproject.toml` um `[tool.pytest.ini_options]` (`pythonpath = ["src"]`) und Trove-Classifier `"Typing :: Typed"` ergänzt; `ruff check` Bereinigung ungenutzter Imports durchgeführt; standardisiertes `TODO.md` mit `## STATUS`-Tabelle etabliert (Gate 10 PASS); Vertragstests in `tests/test_metadata.py` ergänzt.

- [x] **TASK-DK-04: Standalone-Extraktion & 3-Ursachen-Dokumentationsmodell** (`effort=high`, `scope=core`, priority `high`).
  - **Ergebnis:** Eigenständige Extraktion aus `help_projection.py` überführt; deterministische Klassifikation (`unintended_erosion`, `planned_terraforming_pending`, `completed_terraforming_doc_lag`) implementiert.

- [x] **TASK-DK-05: Transparente Entscheidungsverarbeitungsregeln & CLI** (`effort=medium`, `scope=cli`, priority `high`).
  - **Ergebnis:** Kombinierbare Aktionszweige (`local_taskplan`, `local_doc_update`, `user_notification`, `local_genie_marblerun`, `gitlab_wishes_come_true`) über `config/doc_machine.config.json` realisiert; CLI `python -m doc_keeper audit` und `python -m doc_keeper rules` bereitgestellt.

- [x] **TASK-DK-06: Zweisprachige Dokumentation & Umlautharmonisierung** (`effort=low`, `scope=docs`, priority `normal`).
  - **Ergebnis:** `README.md` (Englisch) und `README_de.md` (Deutsch) mit Mermaid-Diagrammen angelegt; End-User-Texte auf echte deutsche Umlaute (ä, ö, ü, ß) harmonisiert.
