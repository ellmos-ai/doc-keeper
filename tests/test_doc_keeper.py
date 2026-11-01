from __future__ import annotations

import json
from pathlib import Path
import subprocess

from doc_keeper import (
    AVAILABLE_DECISION_BRANCHES,
    audit_repository,
    classify_doc_reality_diff,
    extract_repo_claims,
    load_doc_machine_config,
    resolve_doc_machine_dispatch,
)
from doc_keeper.cli import main as cli_main


def test_three_cause_classifier_and_combinable_decision_rules():
    assert "local_taskplan" in AVAILABLE_DECISION_BRANCHES
    assert "local_doc_update" in AVAILABLE_DECISION_BRANCHES

    # Cause 1: Unintended Erosion
    c1 = classify_doc_reality_diff(
        claim_statement="Function `parse_invoice()` exists",
        doc_source="README.md",
        reality_matches_doc=False,
        previously_worked_in_reality=True,
    )
    assert c1["cause"] == "unintended_erosion"
    assert c1["dispatch"]["selected_branches"] == ["local_taskplan", "user_notification"]
    assert c1["dispatch"]["priority"] == "P1"

    # Cause 2: Planned Terraforming Pending
    c2 = classify_doc_reality_diff(
        claim_statement="Function `future_quantum_router()` exists",
        doc_source="README.md",
        reality_matches_doc=False,
        planned_in_roadmap_or_decisions=True,
        linked_task_id="T-900",
    )
    assert c2["cause"] == "planned_terraforming_pending"
    assert c2["dispatch"]["selected_branches"] == ["local_taskplan"]
    assert c2["dispatch"]["priority"] == "P2"

    # Cause 3: Completed Terraforming Doc Lag
    c3 = classify_doc_reality_diff(
        claim_statement="Old signature `run_v1()`",
        doc_source="README.md",
        reality_matches_doc=False,
        code_has_newer_intentional_change=True,
        task_status="done",
    )
    assert c3["cause"] == "completed_terraforming_doc_lag"
    assert c3["dispatch"]["selected_branches"] == ["local_doc_update"]

    # Developer wishes_redirect override
    disp = resolve_doc_machine_dispatch(
        cause="unintended_erosion",
        task_action="create_bugfix_terraforming_task",
        config_override={"wishes_redirect": {"enabled": True, "target_mode": "local_genie_pipeline"}},
        active_tier="ocean-dev",
    )
    assert disp["dispatch_mode"] == "wishes_redirect"
    assert disp["developer_redirect_active"] is True


def test_generic_repo_extractor_and_three_cause_audit(tmp_path: Path):
    # Initialize a real temporary git repo to test all 3 causes end-to-end!
    subprocess.run(["git", "init", str(tmp_path)], check=True, capture_output=True)
    subprocess.run(["git", "-C", str(tmp_path), "config", "user.email", "test@ellmos.ai"], check=True)
    subprocess.run(["git", "-C", str(tmp_path), "config", "user.name", "Test"], check=True)

    src_dir = tmp_path / "src"
    src_dir.mkdir()
    (src_dir / "engine.py").write_text(
        "def active_feature():\n    return True\n\ndef eroded_helper():\n    return 1\n",
        encoding="utf-8",
    )
    subprocess.run(["git", "-C", str(tmp_path), "add", "."], check=True)
    subprocess.run(["git", "-C", str(tmp_path), "commit", "-m", "initial"], check=True, capture_output=True)

    # Now remove eroded_helper() unintentionally (so it exists in git history -> Cause 1 unintended_erosion)
    (src_dir / "engine.py").write_text("def active_feature():\n    return True\n", encoding="utf-8")
    subprocess.run(["git", "-C", str(tmp_path), "add", "."], check=True)
    subprocess.run(["git", "-C", str(tmp_path), "commit", "-m", "refactor"], check=True, capture_output=True)

    # Plan doc mentions `planned_feature` -> Cause 2 planned_terraforming_pending
    (tmp_path / "TODO.md").write_text("- [ ] Implement `planned_feature` in next milestone\n", encoding="utf-8")

    # README mentions:
    # 1. `src/engine.py` and `active_feature()` -> aligned
    # 2. `eroded_helper()` -> existed in git history -> Cause 1 (unintended_erosion)
    # 3. `planned_feature()` -> in TODO.md -> Cause 2 (planned_terraforming_pending)
    # 4. `legacy_renamed_func()` -> neither in git history nor in TODO.md -> Cause 3 (completed_terraforming_doc_lag)
    (tmp_path / "README.md").write_text(
        "# Demo\n"
        "See `src/engine.py` and `active_feature()`.\n"
        "Also calls `eroded_helper()`, `planned_feature()`, and `legacy_renamed_func()`.\n",
        encoding="utf-8",
    )

    claims = extract_repo_claims(tmp_path)
    assert len(claims) == 5

    report = audit_repository(tmp_path)
    assert report["schema"] == "ellmos.doc-keeper-audit-report.v1"
    assert report["summary"]["total_claims_probed"] == 5
    assert report["summary"]["aligned_claims"] == 2
    assert report["summary"]["unintended_erosion"] == 1
    assert report["summary"]["planned_terraforming_pending"] == 1
    assert report["summary"]["completed_terraforming_doc_lag"] == 1

    # Verify CLI execution
    out_file = tmp_path / "report.json"
    rc = cli_main(["audit", str(tmp_path), "--output", str(out_file)])
    assert rc == 0
    saved = json.loads(out_file.read_text(encoding="utf-8"))
    assert saved["summary"]["aligned_claims"] == 2
