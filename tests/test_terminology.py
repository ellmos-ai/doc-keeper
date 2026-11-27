from __future__ import annotations

import json
from pathlib import Path

import pytest
from doc_keeper import (
    TerminologySpecError,
    audit_terminology_cross_repo,
    audit_terminology_repository,
    load_terminology_spec,
    terminology_check,
)
from doc_keeper.cli import main as cli_main


def _write_sample_spec(path: Path) -> Path:
    spec = {
        "schema": "ellmos.ocean-terminology-congruence.v1",
        "schema_version": 1,
        "decided_at": "2026-11-27",
        "policy": {
            "one_term_per_concept": True,
            "preserve_legacy_wire_compatibility": True,
            "forbidden_in_new_ui_and_docs": [
                "Aktueller Fackelhalter",
                "Hardware-Fackel",
                "Steckplatz einrichten",
                "Anbieter-Sockel",
                "Agenten-Fabrik",
            ],
        },
        "concepts": [
            {
                "id": "stage1_ram_allocation",
                "canonical_de": "RAM-Zuteilung",
                "legacy_wire_compat": ["/api/fackel", "fackel"],
                "deprecated_ui_terms": ["Aktueller Fackelhalter", "Hardware-Fackel", "Fackel"],
            },
            {
                "id": "stage2_model_time_allocation",
                "canonical_de": "Modellzeit-Zuteilung",
                "legacy_wire_compat": ["compute_turn"],
                "deprecated_ui_terms": ["Model Torch"],
            },
            {
                "id": "configured_agent",
                "canonical_de": "Agent",
                "legacy_wire_compat": ["/api/slots", "slots_config.json"],
                "deprecated_ui_terms": ["Steckplatz einrichten", "Steckplatz"],
            },
            {
                "id": "library_role_template",
                "canonical_de": "Rollenvorlage",
                "legacy_wire_compat": ["ellmos.role-socket-catalog.v1"],
                "deprecated_ui_terms": ["Agenten-Fabrik"],
            },
        ],
    }
    spec_path = path / "terminology-congruence.v1.json"
    spec_path.write_text(json.dumps(spec, indent=2, ensure_ascii=False), encoding="utf-8")
    return spec_path


def test_single_repo_separates_visible_ui_violations_from_legacy_wire_compat(tmp_path: Path):
    spec_path = _write_sample_spec(tmp_path)
    repo = tmp_path / "ellmos-system-gui"
    (repo / "src" / "pages").mkdir(parents=True)
    # Clean page with intentional legacy API route and DOM id: must pass with 0 violations!
    (repo / "src" / "pages" / "running.astro").write_text(
        '<section id="fackel-banner">\n'
        '  <h2>RAM-Zuteilung &amp; Modellzeit-Zuteilung</h2>\n'
        '  <script>fetch("/api/fackel"); fetch("/api/slots");</script>\n'
        "</section>\n",
        encoding="utf-8",
    )
    # Changelog and glossary files must be ignored by default
    (repo / "CHANGELOG.md").write_text("Removed Hardware-Fackel and Agenten-Fabrik.\n", encoding="utf-8")

    clean_report = audit_terminology_repository(repo, spec_path)
    assert clean_report["ok"] is True
    assert clean_report["violation_count"] == 0
    assert clean_report["legacy_wire_compat_count"] >= 1
    assert "RAM-Zuteilung" in clean_report["canonical_terms_present"]
    assert "Modellzeit-Zuteilung" in clean_report["canonical_terms_present"]

    # Now introduce a visible UI regression
    (repo / "src" / "pages" / "blueprints.astro").write_text(
        "<h1>Agenten-Fabrik</h1>\n<button>Steckplatz einrichten</button>\n",
        encoding="utf-8",
    )
    dirty_report = audit_terminology_repository(repo, spec_path)
    assert dirty_report["ok"] is False
    assert dirty_report["violation_count"] == 2
    terms = {v["term"] for v in dirty_report["violations"]}
    assert terms == {"Agenten-Fabrik", "Steckplatz einrichten"}
    by_term = {v["term"]: v for v in dirty_report["violations"]}
    assert by_term["Agenten-Fabrik"]["canonical_de"] == "Rollenvorlage"
    assert by_term["Steckplatz einrichten"]["canonical_de"] == "Agent"


def test_cross_repo_audit_detects_asymmetry_and_cli_exit_codes(tmp_path: Path):
    spec_path = _write_sample_spec(tmp_path)

    repo_a = tmp_path / "open-ocean"
    repo_a.mkdir()
    (repo_a / "README.md").write_text(
        "# OCEAN\nStufe 1: RAM-Zuteilung. Stufe 2: Modellzeit-Zuteilung.\n",
        encoding="utf-8",
    )

    repo_b = tmp_path / "bach"
    repo_b.mkdir()
    (repo_b / "README.md").write_text(
        "# BACH\nSteuert die Hardware-Fackel fuer lokale Modelle.\n",
        encoding="utf-8",
    )

    report = terminology_check([repo_a, repo_b], spec_path)
    assert report["schema"] == "ellmos.doc-keeper-terminology-report.v1"
    assert report["scope"] == "cross_repo"
    assert report["ok"] is False
    assert report["summary"]["repos_scanned"] == 2
    assert report["summary"]["total_violations"] == 1
    assert report["summary"]["violations_by_repo"] == {"open-ocean": 0, "bach": 1}
    assert len(report["cross_repo_findings"]) == 1
    finding = report["cross_repo_findings"][0]
    assert finding["rule"] == "TERMINOLOGY-CROSS-REPO-ASYMMETRY"
    assert finding["repo"] == "bach"
    assert finding["canonical_de"] == "RAM-Zuteilung"
    assert finding["aligned_peer_repos"] == ["open-ocean"]

    # CLI with --fail-on-violations returns 1 when violations exist, 0 for clean repo
    out_file = tmp_path / "term-report.json"
    rc_fail = cli_main(
        ["terminology", str(repo_a), str(repo_b), "--spec", str(spec_path), "--output", str(out_file), "--fail-on-violations"]
    )
    assert rc_fail == 1
    saved = json.loads(out_file.read_text(encoding="utf-8"))
    assert saved["summary"]["total_violations"] == 1

    rc_ok = cli_main(["terminology", str(repo_a), "--spec", str(spec_path), "--fail-on-violations"])
    assert rc_ok == 0


def test_invalid_spec_raises_terminology_spec_error(tmp_path: Path):
    bad_spec = tmp_path / "broken.json"
    bad_spec.write_text('{"schema": "bad"}', encoding="utf-8")
    with pytest.raises(TerminologySpecError):
        load_terminology_spec(bad_spec)
    with pytest.raises(TerminologySpecError):
        audit_terminology_cross_repo([tmp_path], bad_spec)
    assert cli_main(["terminology", str(tmp_path), "--spec", str(bad_spec)]) == 2
