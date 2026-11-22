# SPDX-License-Identifier: MIT
"""Contract and metadata tests for doc-keeper repository.

Verifies PEP 621 / PEP 561 compliance, .gitignore hygiene, manifest integrity,
bilingual documentation parity, Policy P-022 LLM entry points, community health,
TODO.md release status table, self-audit consistency, and zero personal paths.
"""
from __future__ import annotations

import json
from pathlib import Path
import re
import sys
import xml.etree.ElementTree as ET

if sys.version_info >= (3, 11):
    import tomllib
else:
    import tomli as tomllib

import doc_keeper
from doc_keeper import audit_repository

REPO_ROOT = Path(__file__).resolve().parent.parent


def _read_text(relative_path: str) -> str:
    path = REPO_ROOT / relative_path
    assert path.is_file(), f"Expected file {relative_path} does not exist"
    return path.read_text(encoding="utf-8")


def test_gitignore_hygiene():
    """Verify .gitignore contains minimum entries and security/multihost guards."""
    content = _read_text(".gitignore")
    lines = {
        line.strip()
        for line in content.splitlines()
        if line.strip() and not line.startswith("#")
    }
    required_patterns = [
        "__pycache__/",
        "*.pyc",
        ".pytest_cache/",
        ".ruff_cache/",
        ".venv/",
        ".idea/",
        ".vscode/",
        "*.db",
        ".env",
        "data/",
        "*.key",
        "*.pem",
        "credentials.json",
        "secrets.json",
        "LOCK",
        "LOCK.*",
        "*-WORKSTATION*",
        "*-ASUS*",
        "*-LAPTOP*",
    ]
    for pattern in required_patterns:
        assert pattern in lines, f"Missing required .gitignore pattern: {pattern}"


def test_pep621_and_pep561_metadata():
    """Verify pyproject.toml PEP 621, PEP 561, PEP 639, URLs, and keywords."""
    with open(REPO_ROOT / "pyproject.toml", "rb") as f:
        data = tomllib.load(f)

    project = data.get("project", {})
    assert project.get("name") == "ellmos-doc-keeper"
    assert project.get("version") == doc_keeper.__version__
    assert project.get("version") == "0.1.0"
    assert project.get("license") == "MIT"
    assert "LICENSE" in project.get("license-files", [])
    assert "THIRD_PARTY_LICENSES.md" in project.get("license-files", [])
    classifiers = project.get("classifiers", [])
    assert "Typing :: Typed" in classifiers
    assert not any(c.startswith("License ::") for c in classifiers), (
        "PEP 639 license string must not be combined with License :: classifier"
    )
    assert len(project.get("keywords", [])) >= 5
    urls = project.get("urls", {})
    assert "Repository" in urls and "ellmos-ai/doc-keeper" in urls["Repository"]
    assert "Issues" in urls

    # Package data
    tool_setuptools = data.get("tool", {}).get("setuptools", {})
    package_data = tool_setuptools.get("package-data", {})
    assert "py.typed" in package_data.get("doc_keeper", [])

    # Pytest configuration
    pytest_cfg = data.get("tool", {}).get("pytest", {}).get("ini_options", {})
    assert "src" in pytest_cfg.get("pythonpath", [])


def test_py_typed_file_present():
    """Verify PEP 561 py.typed marker is physically present."""
    marker = REPO_ROOT / "src" / "doc_keeper" / "py.typed"
    assert marker.is_file(), "src/doc_keeper/py.typed must exist"


def test_todo_md_status_table_and_tasks():
    """Verify TODO.md has the standardized 10-category STATUS table and task IDs."""
    content = _read_text("TODO.md")
    assert "## STATUS" in content
    assert "| Category" in content and "| Status" in content and "| Notes" in content
    assert "Overall" in content
    assert "PASS (10/10 Gates)" in content
    assert "TASK-DK-01" in content
    assert "TASK-DK-03" in content


def test_manifest_schema_and_roles():
    """Verify ellmos-module.v2.json conforms to strict schema and declares roles."""
    with open(REPO_ROOT / "ellmos-module.v2.json", "r", encoding="utf-8") as f:
        manifest = json.load(f)

    assert manifest.get("schema") == "ellmos.module.v2"
    assert manifest.get("id") == "doc-keeper"
    assert manifest.get("version") == "0.1.0"
    assert manifest.get("category") == "control"
    assert manifest.get("kind") == "tool"
    assert manifest.get("status") == "active"
    assert manifest.get("visibility") == "public"

    roles = manifest.get("roles", [])
    assert len(roles) >= 1
    assert roles[0].get("id") == "doc-keeper"
    prompt_file = REPO_ROOT / roles[0].get("prompt", "")
    assert prompt_file.is_file(), f"Role prompt {prompt_file} must exist"


def test_config_umlauts_and_structure():
    """Verify config/doc_machine.config.json has true German umlauts."""
    with open(REPO_ROOT / "config" / "doc_machine.config.json", "r", encoding="utf-8") as f:
        cfg = json.load(f)

    assert cfg.get("schema") == "ellmos.doc-machine.config.v1"
    reasons = json.dumps(cfg, ensure_ascii=False)
    # Ensure genuine German umlauts are preserved
    assert "Realität" in reasons
    assert "prüfen" in reasons
    assert "Rückmeldung" in reasons
    assert "überein" in reasons


def test_bilingual_readme_and_mermaid():
    """Verify English README.md and German README_de.md both contain flowchart and sequenceDiagram."""
    readme_en = _read_text("README.md")
    readme_de = _read_text("README_de.md")

    assert "```mermaid" in readme_en
    assert "```mermaid" in readme_de
    assert "sequenceDiagram" in readme_en
    assert "sequenceDiagram" in readme_de
    assert "classify_doc_reality_diff" in readme_en
    assert "classify_doc_reality_diff" in readme_de
    assert "assets/terminal-workflow.svg" in readme_en
    assert "assets/terminal-workflow.svg" in readme_de
    assert "## 5. Install with your LLM" in readme_en
    assert "## 5. Mit deinem LLM installieren" in readme_de
    assert "llms.txt" in readme_en and "SKILL.md" in readme_en
    assert "llms.txt" in readme_de and "SKILL.md" in readme_de


def test_terminal_workflow_svg_valid():
    """Verify assets/terminal-workflow.svg exists and parses as valid SVG XML."""
    svg_text = _read_text("assets/terminal-workflow.svg")
    root = ET.fromstring(svg_text)
    assert root.tag.endswith("svg")
    assert "doc-keeper" in svg_text


def test_p022_llm_entry_files_present():
    """Verify SKILL.md, llms.txt, and llm.txt meet Policy P-022 requirements."""
    skill_text = _read_text("SKILL.md")
    llms_text = _read_text("llms.txt")
    llm_text = _read_text("llm.txt")

    assert "name: doc-keeper" in skill_text
    assert "0.1.0" in skill_text
    assert "audit_repository()" in skill_text
    assert "Prerequisites" in llms_text
    assert "Installation Command" in llms_text
    assert "Verification Command" in llms_text
    assert "Minimal Example" in llms_text
    assert "Last-checked:" in llms_text
    assert "llms.txt" in llm_text


def test_community_health_files_bilingual_and_templates():
    """Verify bilingual CODE_OF_CONDUCT.md, CONTRIBUTING.md, and GitHub issue templates."""
    coc = _read_text("CODE_OF_CONDUCT.md")
    contrib = _read_text("CONTRIBUTING.md")
    bug_tpl = _read_text(".github/ISSUE_TEMPLATE/bug_report.md")
    feat_tpl = _read_text(".github/ISSUE_TEMPLATE/feature_request.md")
    cfg_tpl = _read_text(".github/ISSUE_TEMPLATE/config.yml")

    assert "## Deutsch" in coc and "## English" in coc
    assert "## Deutsch" in contrib and "## English" in contrib
    assert "labels: bug" in bug_tpl
    assert "labels: enhancement" in feat_tpl
    assert "security/advisories" in cfg_tpl


def test_dogfood_self_audit_clean():
    """Verify doc-keeper's own documentation claims align 100% with codebase reality."""
    report = audit_repository(REPO_ROOT)
    summary = report["summary"]
    assert summary["total_claims_probed"] > 0
    assert summary["unintended_erosion"] == 0, f"Findings: {report['findings']}"
    assert summary["planned_terraforming_pending"] == 0, f"Findings: {report['findings']}"
    assert summary["completed_terraforming_doc_lag"] == 0, f"Findings: {report['findings']}"
    assert summary["aligned_claims"] == summary["total_claims_probed"]


def test_zero_personal_paths_and_secrets():
    """Verify zero personal paths and credentials in tracked codebase."""
    personal_path_re = re.compile(r"[C-Z]:\\Users\\[a-zA-Z0-9_.-]+", re.IGNORECASE)
    secret_key_re = re.compile(r"(?:api[_-]?key|secret[_-]?token)\s*=\s*['\"][a-zA-Z0-9]{20,}['\"]", re.IGNORECASE)

    for py_file in (REPO_ROOT / "src").rglob("*.py"):
        text = py_file.read_text(encoding="utf-8")
        assert not personal_path_re.search(text), f"Personal path found in {py_file}"
        assert not secret_key_re.search(text), f"Secret key pattern found in {py_file}"
