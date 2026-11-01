# doc-keeper — 3-Cause Documentation Machine & Decision Rule Router (`ellmos.module.v2`)

**English** | [Deutsch](README_de.md)

`doc-keeper` (`ellmos-doc-keeper`) is a standalone, zero-dependency Python module and CLI tool for **Open Ocean**, **BACH**, and **arbitrary Git repositories**. It extracts verifiable documentation claims (file paths, AST Python symbols, CLI flags) and classifies every discrepancy between documentation and code reality into one of **3 deterministic causes** governed by transparent, combinable **Decision Processing Rules (`config/doc_machine.config.json`)**.

---

## Architecture: The 3-Cause Documentation Model

When documentation (`README*.md`, `SKILL.md`, `docs/**/*.md`, `system/docs/help/*.txt`) diverges from measured code reality, `doc-keeper` never blindly overwrites target architecture:

| Cause (`classify_doc_reality_diff`) | Meaning | Transparent Action Branches (`selected_branches`) |
|---|---|---|
| **1. `unintended_erosion`** | Documentation states intended SOLL, code broke or drifted unintentionally (`git log -S` proof). | **`["local_taskplan", "user_notification"]`** — keep SOLL in doc, create P1 repair task, notify operator. |
| **2. `planned_terraforming_pending`** | Documentation describes planned target architecture from `TODO.md` / `DECISIONS.md` not yet finished in code. | **`["local_taskplan"]`** — create/sync P2 task and separate **SOLL vs. IST** in documentation. |
| **3. `completed_terraforming_doc_lag`** | Code was intentionally advanced, documentation lags behind. | **`["local_doc_update"]`** — update documentation and translations locally. |

```mermaid
flowchart TD
    classDef probe fill:#fef3c7,stroke:#d97706,stroke-width:2px,color:#92400e
    classDef c1 fill:#fee2e2,stroke:#dc2626,stroke-width:2px,color:#991b1b
    classDef c2 fill:#e0f2fe,stroke:#0284c7,stroke-width:2px,color:#0369a1
    classDef c3 fill:#ecfdf5,stroke:#059669,stroke-width:2px,color:#065f46

    subgraph S1["1. Generic Claim Extraction & 3-Cause Classification"]
        EXT["extract_repo_claims(repo_root)
File Paths + Python AST Symbols"]:::probe
        CLS{"classify_doc_reality_diff()
Checks AST, Filesystem, Plan Docs & Git History"}:::probe
        U1["Cause 1: unintended_erosion
(Existed in git history, broke unintentionally)"]:::c1
        U2["Cause 2: planned_terraforming_pending
(Listed in TODO.md / DECISIONS.md)"]:::c2
        U3["Cause 3: completed_terraforming_doc_lag
(Code intentionally updated, doc lags)"]:::c3
        EXT --> CLS
        CLS --> U1
        CLS --> U2
        CLS --> U3
    end

    subgraph S2["2. Transparent Decision Processing Rules (doc_machine.config.json)"]
        RULE{"resolve_doc_machine_dispatch()
Combinable Action Branches"}:::probe
        B1["local_taskplan (P1/P2 Task)"]:::c3
        B2["local_genie_marblerun (wishes-come-true-local)"]:::c2
        B3["gitlab_wishes_come_true (wishes_redirect)"]:::probe
        B4["user_notification (GUI Inbox / Telegram)"]:::c1
        B5["local_doc_update (Auto-Update Docs)"]:::c3
        U1 --> RULE
        U2 --> RULE
        U3 --> B5
        RULE --> B1
        RULE --> B2
        RULE --> B3
        RULE --> B4
    end
```

---

## Quickstart (CLI & Python API)

```bash
pip install -e .

# Audit any repository and output structured JSON report
python -m doc_keeper audit /path/to/repo --json

# Inspect active Decision Processing Rules for a repository
python -m doc_keeper rules /path/to/repo
```

```python
from doc_keeper import audit_repository, classify_doc_reality_diff, resolve_doc_machine_dispatch

report = audit_repository(".")
print(report["summary"])
```
