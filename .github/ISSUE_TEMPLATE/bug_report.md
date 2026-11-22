---
name: Bug Report
about: Report a bug or false classification in doc-keeper
title: "[Bug]: "
labels: bug
assignees: ""
---

## Describe the Bug / Fehlerbeschreibung
A clear and concise description of what went wrong.
Eine klare Beschreibung des beobachteten Problems.

## Steps to Reproduce / Schritte zur Reproduktion
1. Command run (e.g. `python -m doc_keeper audit <path> --json`)
2. Sample doc/code claim
3. Observed output vs. expected 3-Cause classification (`unintended_erosion`, `planned_terraforming_pending`, `completed_terraforming_doc_lag`)

## Environment / Umgebung
- OS: (Windows / Linux / macOS)
- Python version: (`python --version`)
- `doc-keeper` version: (`0.1.0`)

## Checklist / Checkliste
- [ ] Zero-egress / local-only behavior confirmed (no sensitive paths or tokens in logs)
- [ ] Reproducible with minimal sample repository
