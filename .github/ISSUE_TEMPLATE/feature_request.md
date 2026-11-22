---
name: Feature Request
about: Suggest an enhancement for claim extraction or decision rules
title: "[Feature]: "
labels: enhancement
assignees: ""
---

## Problem / Motivation
Describe what documentation claim type or decision branch is missing.
Beschreiben Sie, welcher Dokumentations-Claim-Typ oder Aktionszweig fehlt.

## Proposed Solution / Vorgeschlagene Lösung
How should `extract_repo_claims()`, `classify_doc_reality_diff()`, or `resolve_doc_machine_dispatch()` behave?

## Constraints / Rahmenbedingungen
- [ ] Keeps zero third-party runtime dependencies (Python stdlib only)
- [ ] Preserves static-only inspection (no execution of audited repository code)
- [ ] Maintains deterministic output and transparent `decision_rule_trace`
