# doc-keeper — 3-Ursachen-Dokumentationsmaschine & Entscheidungs-Router (`ellmos.module.v2`)

[English](README.md) | **Deutsch**

`doc-keeper` (`ellmos-doc-keeper`) ist ein eigenständiges, wiederverwendbares Python-Modul und CLI-Werkzeug für **Open Ocean**, **BACH** und **beliebige Git-Repositories**. Es extrahiert prüfbare Dokumentations-Aussagen (Dateipfade, Python-AST-Symbole, CLI-Flags) und klassifiziert jede Abweichung zwischen Dokumentation und Code-Realität deterministisch in eine der **3 Ursachen** anhand transparenter, frei kombinierbarer **Entscheidungsverarbeitungsregeln (`config/doc_machine.config.json`)**.

---

## Architektur: Das 3-Ursachen-Dokumentationsmodell

Stellt `doc-keeper` eine Abweichung zwischen Dokumentation (`README*.md`, `SKILL.md`, `docs/**/*.md`, `system/docs/help/*.txt`) und Code-Realität fest, überschreibt er niemals blind gewollte SOLL-Architektur:

| Ursache (`classify_doc_reality_diff`) | Bedeutung | Transparente Aktionszweige (`selected_branches`) |
|---|---|---|
| **1. `unintended_erosion`** | Doku beschreibt gewolltes SOLL, Code ist ungewollt kaputtgegangen/abgedriftet (`git log -S`-Beleg). | **`["local_taskplan", "user_notification"]`** — SOLL in Doku bewahren, P1-Reparatur-Task einstellen, Nutzer informieren. |
| **2. `planned_terraforming_pending`** | Vorauseilende Doku aus `TODO.md` / `DECISIONS.md`, im Code noch nicht fertig. | **`["local_taskplan"]`** — P2-Bau-Task prüfen/anlegen und **SOLL vs. IST** kennzeichnen. |
| **3. `completed_terraforming_doc_lag`** | Vorauseilender Code, Dokumentation hinkt hinterher. | **`["local_doc_update"]`** — Dokumentation und Übersetzungen lokal nachziehen. |

```mermaid
flowchart TD
    classDef probe fill:#fef3c7,stroke:#d97706,stroke-width:2px,color:#92400e
    classDef c1 fill:#fee2e2,stroke:#dc2626,stroke-width:2px,color:#991b1b
    classDef c2 fill:#e0f2fe,stroke:#0284c7,stroke-width:2px,color:#0369a1
    classDef c3 fill:#ecfdf5,stroke:#059669,stroke-width:2px,color:#065f46

    subgraph S1["1. Generische Claim-Extraktion & 3-Ursachen-Klassifikation"]
        EXT["extract_repo_claims(repo_root)
Dateipfade + Python-AST-Symbole"]:::probe
        CLS{"classify_doc_reality_diff()
Prüft AST, Dateisystem, Plan-Doku & Git-Historie"}:::probe
        U1["Ursache 1: unintended_erosion
(In Git-Historie vorhanden, ungewollt gebrochen)"]:::c1
        U2["Ursache 2: planned_terraforming_pending
(In TODO.md / DECISIONS.md als geplant geführt)"]:::c2
        U3["Ursache 3: completed_terraforming_doc_lag
(Code gewollt weiterentwickelt, Doku hinkt nach)"]:::c3
        EXT --> CLS
        CLS --> U1
        CLS --> U2
        CLS --> U3
    end

    subgraph S2["2. Transparente Entscheidungsverarbeitungsregeln (doc_machine.config.json)"]
        RULE{"resolve_doc_machine_dispatch()
Kombinierbare Aktionszweige"}:::probe
        B1["local_taskplan (P1/P2-Task)"]:::c3
        B2["local_genie_marblerun (wishes-come-true-local)"]:::c2
        B3["gitlab_wishes_come_true (wishes_redirect)"]:::probe
        B4["user_notification (GUI-Inbox / Telegram)"]:::c1
        B5["local_doc_update (Doku lokal nachziehen)"]:::c3
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

## Schnellstart (CLI & Python-API)

```bash
pip install -e .

# Beliebiges Repository prüfen und strukturierten JSON-Bericht ausgeben
python -m doc_keeper audit /pfad/zum/repo --json

# Aktive Entscheidungsverarbeitungsregeln eines Repos anzeigen
python -m doc_keeper rules /pfad/zum/repo
```
