# Beitragsrichtlinie / Contributing Guide

## Deutsch

Vielen Dank für Ihr Interesse, zu `doc-keeper` (`ellmos-doc-keeper`) beizutragen!

### Wie Sie beitragen können

1. **Bug melden:** Erstellen Sie ein Issue mit der Vorlage für Fehlermeldungen (`bug_report.md`)
2. **Feature vorschlagen:** Erstellen Sie ein Issue mit der Vorlage für Funktionswünsche (`feature_request.md`)
3. **Code oder Dokumentation beitragen:** Erstellen Sie einen Pull Request

### Pull Requests

1. Forken Sie das Repository
2. Erstellen Sie einen Feature-Branch: `git checkout -b feature/mein-feature`
3. Prüfen Sie Ihre Änderungen lokal:
   - `python -m pytest -ra -v`
   - `ruff check .`
   - `python -m doc_keeper audit . --json`
4. Committen Sie Ihre Änderungen: `git commit -m "Beschreibung der Änderung"`
5. Pushen Sie den Branch: `git push origin feature/mein-feature`
6. Erstellen Sie einen Pull Request gegen `main`

### Lizenz- und Rechtehinweise

Ohne ausdrückliche Zusatzregel gelten Pull Requests unter der `MIT`-Lizenz dieses Projekts ([LICENSE](LICENSE)).

### Code-Richtlinien

- Python `>=3.10`, PEP 8 Stil, Type Hints (`py.typed`)
- **Zero-Dependency-Prinzip:** Keine externen Laufzeitabhängigkeiten in `dependencies = []` (nur Python-Standardbibliothek)
- **Local-First & Zero-Egress:** Keine Netzwerkzugriffe in Audit- oder Klassifikationspfaden; statisches `ast.parse()` statt Codeausführung
- Encoding: UTF-8 für alle Dateien; echte deutsche Umlaute (`ä`, `ö`, `ü`, `ß`) in deutschen Texten
- Keine hartcodierten Benutzerpfade oder API-Keys

### Erste Schritte

Starten Sie mit [README_de.md](README_de.md) (bzw. [README.md](README.md)) und [SKILL.md](SKILL.md).

---

## English

Thank you for your interest in contributing to `doc-keeper` (`ellmos-doc-keeper`)!

### How to Contribute

1. **Report bugs:** Open an issue using the bug report template (`bug_report.md`)
2. **Suggest features:** Open an issue using the feature request template (`feature_request.md`)
3. **Contribute code or docs:** Open a Pull Request

### Pull Requests

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/my-feature`
3. Verify your changes locally:
   - `python -m pytest -ra -v`
   - `ruff check .`
   - `python -m doc_keeper audit . --json`
4. Commit your changes: `git commit -m "Description of change"`
5. Push the branch: `git push origin feature/my-feature`
6. Open a Pull Request targeting `main`

### Licensing and Contribution Terms

Unless stated otherwise, pull requests are understood to be submitted under the project's `MIT` license ([LICENSE](LICENSE)).

### Code Guidelines

- Python `>=3.10`, PEP 8 style, type annotations (`py.typed`)
- **Zero-Dependency Principle:** Keep `dependencies = []` in `pyproject.toml` (Python standard library only)
- **Local-First & Zero-Egress:** No network calls in audit or classification paths; static `ast.parse()` instead of executing untrusted code
- Encoding: UTF-8 for all files
- No hardcoded personal paths or API keys

### Getting Started

Start with [README.md](README.md) (or [README_de.md](README_de.md)) and [SKILL.md](SKILL.md).
