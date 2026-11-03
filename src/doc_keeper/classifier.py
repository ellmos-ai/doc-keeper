"""Deterministic 3-Cause Classifier & Transparent Decision Processing Rule Engine."""
from __future__ import annotations

from copy import deepcopy
import json
from pathlib import Path
from typing import Any, Dict, List

AVAILABLE_DECISION_BRANCHES: tuple[str, ...] = (
    "local_taskplan",           # Simple repair/implementation task in local Ocean/BACH taskplan
    "local_genie_marblerun",    # Local MarbleRun wishes-come-true relay chain
    "gitlab_wishes_come_true",  # Developer redirect to local-genie / wishes-come-true repo
    "user_notification",        # Operator notification (GUI inbox / Telegram)
    "local_doc_update",         # Direct documentation & translation update
)

DEFAULT_DOC_MACHINE_CONFIG: Dict[str, Any] = {
    "schema": "ellmos.doc-machine.config.v1",
    "execution_locality": "local_ocean_bach_only",
    "default_repair_dispatch": "local_taskplan",
    "available_decision_branches": list(AVAILABLE_DECISION_BRANCHES),
    "decision_processing_rules": {
        "transparent": True,
        "user_configurable": True,
        "combinable_branches": True,
        "cause_routing": {
            "unintended_erosion": {
                "branches": ["local_taskplan", "user_notification"],
                "reason": "Ungewollte Erosion/Drift: Reparatur-Task für Hintergrund-Worker einstellen + Nutzer informieren.",
            },
            "planned_terraforming_pending": {
                "branches": ["local_taskplan"],
                "reason": "Fehlendes/geplantes Terraforming: Taskstatus prüfen/anpassen und SOLL vs. IST markieren.",
            },
            "completed_terraforming_doc_lag": {
                "branches": ["local_doc_update"],
                "reason": "Erfolgtes Terraforming mit lückenhafter Doku: Doku und Übersetzungen direkt lokal nachziehen.",
            },
            "aligned": {
                "branches": [],
                "reason": "Doku und Code-Realität stimmen überein.",
            },
        },
        "trigger_overrides": {
            "critical_security_or_lock_drift": {
                "branches": ["local_taskplan", "user_notification"],
                "reason": "Sicherheits- oder Lock-Abweichung erfordert sofortige Task + Nutzerbenachrichtigung.",
            },
            "complex_multi_file_doc_repair": {
                "branches": ["local_genie_marblerun", "user_notification"],
                "reason": "Mehrstufige Reparatur über lokale MarbleRun-Staffette (wishes-come-true-local).",
            },
            "developer_wishes_experiment": {
                "branches": ["gitlab_wishes_come_true", "user_notification"],
                "reason": "Entwickler-Feature (Lukas): Umleitung auf local-genie / wishes-come-true.",
            },
        },
    },
    "local_taskplan": {
        "enabled": True,
        "db_target": "bach_or_ocean_taskplan",
        "assigned_worker": "background_worker",
        "priority_unintended_erosion": "P1",
        "priority_planned_terraforming": "P2",
    },
    "local_marblerun_wishes": {
        "enabled": False,
        "chain_name": "wishes-come-true-local",
        "max_rounds": 3,
    },
    "user_notification": {
        "enabled": True,
        "channels": ["gui_user_inbox", "telegram_optional"],
        "notify_on_causes": ["unintended_erosion"],
    },
    "wishes_redirect": {
        "enabled": False,
        "feature_tier": "developer_only",
        "required_tier": "ocean-dev",
        "owner": "lukas",
        "target_mode": "local_marblerun_chain",
        "target_chain": "wishes-come-true-local",
        "local_genie_repo_path": "C:\\_Local_DEV\\repos\\local-genie",
        "wishes_come_true_repo_path": "C:\\_Local_DEV\\repos\\wishes-come-true",
        "redirect_on_causes": [
            "unintended_erosion",
            "planned_terraforming_pending",
        ],
        "allow_auto_fix_branch": True,
    },
}


def load_doc_machine_config(
    workspace_root: Path | None = None,
    config_override: Dict[str, Any] | None = None,
) -> Dict[str, Any]:
    """Load the local Documentation Machine configuration (`config/doc_machine.config.json` or override)."""
    cfg = deepcopy(DEFAULT_DOC_MACHINE_CONFIG)
    if workspace_root is not None:
        cfg_path = Path(workspace_root) / "config" / "doc_machine.config.json"
        if cfg_path.is_file():
            try:
                raw = json.loads(cfg_path.read_text(encoding="utf-8"))
                doc_block = raw.get("doc_machine", raw) if isinstance(raw, dict) else {}
                if isinstance(doc_block, dict):
                    for k, v in doc_block.items():
                        if isinstance(v, dict) and isinstance(cfg.get(k), dict):
                            cfg[k].update(v)
                        else:
                            cfg[k] = v
            except Exception:
                pass
    if isinstance(config_override, dict):
        doc_block = config_override.get("doc_machine", config_override)
        if isinstance(doc_block, dict):
            for k, v in doc_block.items():
                if isinstance(v, dict) and isinstance(cfg.get(k), dict):
                    cfg[k].update(v)
                else:
                    cfg[k] = v
    return cfg


def resolve_doc_machine_dispatch(
    *,
    cause: str,
    task_action: str,
    trigger: str = "deterministic_doc_scan",
    branches_override: List[str] | None = None,
    config_override: Dict[str, Any] | None = None,
    workspace_root: Path | None = None,
    active_tier: str = "ocean-dev",
) -> Dict[str, Any]:
    """Transparent & Configurable Decision Processing Rule Engine (`ellmos-doc-keeper`)."""
    cfg = load_doc_machine_config(workspace_root=workspace_root, config_override=config_override)
    locality = str(cfg.get("execution_locality") or "local_ocean_bach_only")
    rules = cfg.get("decision_processing_rules") or {}
    cause_routing = rules.get("cause_routing") or {}
    trigger_overrides = rules.get("trigger_overrides") or {}

    if branches_override is not None:
        selected_branches = [b for b in branches_override if b in AVAILABLE_DECISION_BRANCHES]
        rule_source = "explicit_branches_override"
        rule_reason = "Vom Aufrufer/Operator explizit gesetzte Aktionszweige."
    elif trigger in trigger_overrides and isinstance(trigger_overrides[trigger], dict):
        t_rule = trigger_overrides[trigger]
        selected_branches = list(t_rule.get("branches") or [])
        rule_source = f"trigger_override:{trigger}"
        rule_reason = str(t_rule.get("reason") or f"Trigger-Regel fuer {trigger}")
    else:
        c_rule = cause_routing.get(cause) or {}
        selected_branches = list(c_rule.get("branches") or [])
        rule_source = f"cause_routing:{cause}"
        rule_reason = str(c_rule.get("reason") or f"Deterministische Regel fuer Ursache {cause}")

    if cause == "aligned":
        return {
            "dispatch_mode": "none",
            "selected_branches": [],
            "execution_locality": locality,
            "target": "none",
            "developer_redirect_active": False,
            "decision_rule_trace": {
                "transparent": True,
                "trigger": trigger,
                "cause": cause,
                "rule_source": rule_source,
                "reason": rule_reason,
            },
        }

    if cause == "completed_terraforming_doc_lag" or task_action == "none":
        if not selected_branches:
            selected_branches = ["local_doc_update"]
        return {
            "dispatch_mode": "local_doc_update",
            "selected_branches": selected_branches,
            "execution_locality": locality,
            "target": "local_doc_keeper",
            "developer_redirect_active": False,
            "decision_rule_trace": {
                "transparent": True,
                "trigger": trigger,
                "cause": cause,
                "rule_source": rule_source,
                "reason": rule_reason,
            },
        }

    redirect_cfg = cfg.get("wishes_redirect") or {}
    redirect_enabled = bool(redirect_cfg.get("enabled", False))
    required_tier = str(redirect_cfg.get("required_tier") or "ocean-dev")
    allowed_causes = set(redirect_cfg.get("redirect_on_causes") or [])
    if (
        (redirect_enabled and active_tier in (required_tier, "ocean-admin") and cause in allowed_causes)
        or "gitlab_wishes_come_true" in selected_branches
    ):
        if "gitlab_wishes_come_true" not in selected_branches:
            selected_branches = ["gitlab_wishes_come_true"] + selected_branches
        return {
            "dispatch_mode": "wishes_redirect",
            "selected_branches": selected_branches,
            "execution_locality": locality,
            "target": str(redirect_cfg.get("target_mode") or "local_marblerun_chain"),
            "target_chain": str(redirect_cfg.get("target_chain") or "wishes-come-true-local"),
            "local_genie_repo_path": str(redirect_cfg.get("local_genie_repo_path") or ""),
            "wishes_come_true_repo_path": str(redirect_cfg.get("wishes_come_true_repo_path") or ""),
            "developer_redirect_active": True,
            "task_action": task_action,
            "decision_rule_trace": {
                "transparent": True,
                "trigger": trigger,
                "cause": cause,
                "rule_source": "wishes_redirect_developer_feature" if redirect_enabled else rule_source,
                "reason": rule_reason,
            },
        }

    default_dispatch = str(cfg.get("default_repair_dispatch") or "local_taskplan")
    marblerun_cfg = cfg.get("local_marblerun_wishes") or {}
    if (
        default_dispatch in ("local_marblerun_wishes", "local_genie_marblerun")
        or bool(marblerun_cfg.get("enabled", False))
        or "local_genie_marblerun" in selected_branches
    ):
        if "local_genie_marblerun" not in selected_branches:
            selected_branches = ["local_genie_marblerun"] + [b for b in selected_branches if b != "local_taskplan"]
        return {
            "dispatch_mode": "local_marblerun_wishes",
            "selected_branches": selected_branches,
            "execution_locality": locality,
            "target": str(marblerun_cfg.get("chain_name") or "wishes-come-true-local"),
            "developer_redirect_active": False,
            "task_action": task_action,
            "decision_rule_trace": {
                "transparent": True,
                "trigger": trigger,
                "cause": cause,
                "rule_source": rule_source,
                "reason": rule_reason,
            },
        }

    tp_cfg = cfg.get("local_taskplan") or {}
    priority = (
        str(tp_cfg.get("priority_unintended_erosion") or "P1")
        if cause == "unintended_erosion"
        else str(tp_cfg.get("priority_planned_terraforming") or "P2")
    )
    if not selected_branches:
        selected_branches = ["local_taskplan"]
    return {
        "dispatch_mode": "local_taskplan",
        "selected_branches": selected_branches,
        "execution_locality": locality,
        "target": str(tp_cfg.get("db_target") or "bach_or_ocean_taskplan"),
        "assigned_worker": str(tp_cfg.get("assigned_worker") or "background_worker"),
        "priority": priority,
        "developer_redirect_active": False,
        "task_action": task_action,
        "decision_rule_trace": {
            "transparent": True,
            "trigger": trigger,
            "cause": cause,
            "rule_source": rule_source,
            "reason": rule_reason,
        },
    }


def classify_doc_reality_diff(
    *,
    claim_statement: str,
    doc_source: str,
    reality_matches_doc: bool,
    code_has_newer_intentional_change: bool = False,
    planned_in_roadmap_or_decisions: bool = False,
    previously_worked_in_reality: bool = False,
    linked_task_id: str | None = None,
    task_status: str | None = None,
    config_override: Dict[str, Any] | None = None,
    workspace_root: Path | None = None,
    active_tier: str = "ocean-dev",
) -> Dict[str, Any]:
    """Deterministic 3-Cause Classifier & Action Router for Documentation <-> Reality Diffs."""
    if reality_matches_doc:
        dispatch = resolve_doc_machine_dispatch(
            cause="aligned",
            task_action="none",
            config_override=config_override,
            workspace_root=workspace_root,
            active_tier=active_tier,
        )
        return {
            "schema": "ellmos.doc-keeper.diff-classification.v1",
            "claim_statement": claim_statement,
            "doc_source": doc_source,
            "cause": "aligned",
            "deterministic_action": "keep_verified",
            "preserve_soll_in_doc": True,
            "update_ist_in_doc": False,
            "task_action": "none",
            "linked_task_id": linked_task_id,
            "dispatch": dispatch,
        }

    # Cause 3: Completed Terraforming in code with lagging docs
    if code_has_newer_intentional_change and (task_status == "done" or not planned_in_roadmap_or_decisions):
        dispatch = resolve_doc_machine_dispatch(
            cause="completed_terraforming_doc_lag",
            task_action="none",
            config_override=config_override,
            workspace_root=workspace_root,
            active_tier=active_tier,
        )
        return {
            "schema": "ellmos.doc-keeper.diff-classification.v1",
            "claim_statement": claim_statement,
            "doc_source": doc_source,
            "cause": "completed_terraforming_doc_lag",
            "deterministic_action": "update_documentation_to_match_reality",
            "preserve_soll_in_doc": True,
            "update_ist_in_doc": True,
            "task_action": "none",
            "linked_task_id": linked_task_id,
            "dispatch": dispatch,
        }

    # Cause 2: Planned Terraforming pending (doc is ahead of code)
    if planned_in_roadmap_or_decisions and not previously_worked_in_reality:
        task_act = "check_or_adjust_existing_task" if linked_task_id else "create_terraforming_task"
        dispatch = resolve_doc_machine_dispatch(
            cause="planned_terraforming_pending",
            task_action=task_act,
            config_override=config_override,
            workspace_root=workspace_root,
            active_tier=active_tier,
        )
        return {
            "schema": "ellmos.doc-keeper.diff-classification.v1",
            "claim_statement": claim_statement,
            "doc_source": doc_source,
            "cause": "planned_terraforming_pending",
            "deterministic_action": "mark_soll_vs_ist_and_sync_task",
            "preserve_soll_in_doc": True,
            "update_ist_in_doc": True,
            "task_action": task_act,
            "linked_task_id": linked_task_id,
            "task_status": task_status or "missing_task",
            "dispatch": dispatch,
        }

    # Cause 1: Unintended Erosion / Drift (code broke unintentionally)
    dispatch = resolve_doc_machine_dispatch(
        cause="unintended_erosion",
        task_action="create_bugfix_terraforming_task",
        config_override=config_override,
        workspace_root=workspace_root,
        active_tier=active_tier,
    )
    return {
        "schema": "ellmos.doc-keeper.diff-classification.v1",
        "claim_statement": claim_statement,
        "doc_source": doc_source,
        "cause": "unintended_erosion",
        "deterministic_action": "create_repair_task_and_keep_soll_doc",
        "preserve_soll_in_doc": True,
        "update_ist_in_doc": True,
        "task_action": "create_bugfix_terraforming_task",
        "linked_task_id": linked_task_id,
        "dispatch": dispatch,
    }
