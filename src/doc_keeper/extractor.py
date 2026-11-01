"""Generic Repository Claim Extractor & 3-Cause Reality Auditor (`doc-keeper`)."""
from __future__ import annotations

import ast
from datetime import datetime, timezone
from pathlib import Path
import re
import subprocess
from typing import Any, Dict, List, Set

from .classifier import classify_doc_reality_diff

PATH_CLAIM_RE = re.compile(
    r"(?:`([A-Za-z0-9_./-]+\.(?:py|json|toml|yaml|yml|sh|ps1|txt|astro|ts|js))`|\[[^\]]+\]\(([A-Za-z0-9_./-]+\.(?:py|json|toml|yaml|yml|sh|ps1|txt|astro|ts|js|md))\))"
)
SYMBOL_CALL_RE = re.compile(r"`([a-zA-Z_][a-zA-Z0-9_]*)\(\)`")
PLAN_DOC_NAMES = ("TODO.md", "DECISIONS.md", "AKTUELLER-PLAN.md", "ANFORDERUNGEN-DETAIL.md", "ROADMAP.md")


def _collect_python_symbols(repo_root: Path) -> Set[str]:
    """Collect all top-level and class-level function and class names across `.py` files in `repo_root`."""
    symbols: Set[str] = set()
    excluded = {".git", ".venv", "venv", "node_modules", "__pycache__", ".pytest_cache", "build", "dist"}
    for py_file in repo_root.rglob("*.py"):
        if any(part in excluded for part in py_file.parts):
            continue
        try:
            tree = ast.parse(py_file.read_text(encoding="utf-8", errors="ignore"))
        except SyntaxError:
            continue
        for node in ast.walk(tree):
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
                symbols.add(node.name)
    return symbols


def _collect_plan_text(repo_root: Path) -> str:
    """Concatenate roadmap/plan/decision files in `repo_root` to detect planned Terraforming."""
    chunks: List[str] = []
    for name in PLAN_DOC_NAMES:
        p = repo_root / name
        if p.is_file():
            try:
                chunks.append(p.read_text(encoding="utf-8", errors="ignore"))
            except OSError:
                pass
    return "\n".join(chunks)


def _existed_in_git_history(repo_root: Path, token: str) -> bool:
    """Check via `git log -S` whether `token` previously existed in the repository (Erosion detection)."""
    if not (repo_root / ".git").exists():
        return False
    try:
        res = subprocess.run(
            ["git", "-C", str(repo_root), "log", "-n", "1", "--oneline", "-S", token],
            capture_output=True,
            text=True,
            timeout=5,
            check=False,
        )
        return res.returncode == 0 and bool(res.stdout.strip())
    except (OSError, subprocess.TimeoutExpired):
        return False


def extract_repo_claims(repo_root: str | Path, doc_globs: tuple[str, ...] = ("README*.md", "SKILL*.md", "docs/**/*.md")) -> List[Dict[str, Any]]:
    """Extract verifiable file-path and Python-symbol claims from documentation files in `repo_root`."""
    root = Path(repo_root).resolve()
    doc_files: List[Path] = []
    for pattern in doc_globs:
        for p in root.glob(pattern):
            if p.is_file() and p not in doc_files and p.name not in PLAN_DOC_NAMES:
                doc_files.append(p)

    claims: List[Dict[str, Any]] = []
    seen: Set[tuple[str, str, str]] = set()
    for doc_path in sorted(doc_files):
        rel_doc = doc_path.relative_to(root).as_posix()
        try:
            text = doc_path.read_text(encoding="utf-8", errors="ignore")
        except OSError:
            continue

        # 1. File path claims
        for match in PATH_CLAIM_RE.finditer(text):
            raw_path = match.group(1) or match.group(2) or ""
            raw_path = raw_path.strip().lstrip("./")
            if (
                not raw_path
                or raw_path.startswith(("http://", "https://", "file://", "<"))
                or "*" in raw_path
                or "/" not in raw_path and not (root / raw_path).exists() and raw_path.endswith((".txt", ".json", ".py", ".sh", ".ps1"))
            ):
                continue
            key = (rel_doc, "file_path", raw_path)
            if key in seen:
                continue
            seen.add(key)
            claims.append(
                {
                    "doc_source": rel_doc,
                    "claim_type": "file_path",
                    "target": raw_path,
                    "claim_statement": f"Referenced path `{raw_path}` exists in repository",
                }
            )

        # 2. Function/Method symbol claims `func_name()`
        for match in SYMBOL_CALL_RE.finditer(text):
            sym = match.group(1)
            if len(sym) < 4 or sym in {"print", "open", "dict", "list", "set", "str", "int", "bool", "main", "init"}:
                continue
            key = (rel_doc, "python_symbol", sym)
            if key in seen:
                continue
            seen.add(key)
            claims.append(
                {
                    "doc_source": rel_doc,
                    "claim_type": "python_symbol",
                    "target": sym,
                    "claim_statement": f"Python symbol `{sym}()` is defined in codebase",
                }
            )
    return claims


def audit_repository(
    repo_root: str | Path,
    *,
    doc_globs: tuple[str, ...] = ("README*.md", "SKILL*.md", "docs/**/*.md"),
    config_override: Dict[str, Any] | None = None,
) -> Dict[str, Any]:
    """Run a complete 3-Cause Documentation Audit on `repo_root` (`ellmos.doc-keeper-audit-report.v1`)."""
    root = Path(repo_root).resolve()
    claims = extract_repo_claims(root, doc_globs=doc_globs)
    py_symbols = _collect_python_symbols(root)
    plan_text = _collect_plan_text(root)

    findings: List[Dict[str, Any]] = []
    counts = {
        "total_claims_probed": len(claims),
        "aligned_claims": 0,
        "unintended_erosion": 0,
        "planned_terraforming_pending": 0,
        "completed_terraforming_doc_lag": 0,
    }

    for item in claims:
        target = item["target"]
        ctype = item["claim_type"]
        if ctype == "file_path":
            matches = (root / target).exists()
        else:
            matches = target in py_symbols

        if matches:
            counts["aligned_claims"] += 1
            continue

        in_plan = target in plan_text
        existed_before = _existed_in_git_history(root, target)
        # If it existed before and was intentionally replaced by newer code, or if neither in plan nor erosion
        code_advanced = not in_plan and not existed_before

        diff = classify_doc_reality_diff(
            claim_statement=item["claim_statement"],
            doc_source=item["doc_source"],
            reality_matches_doc=False,
            code_has_newer_intentional_change=code_advanced,
            planned_in_roadmap_or_decisions=in_plan,
            previously_worked_in_reality=existed_before and not in_plan,
            config_override=config_override,
            workspace_root=root,
        )
        cause = diff["cause"]
        counts[cause] = counts.get(cause, 0) + 1
        findings.append(diff)

    return {
        "schema": "ellmos.doc-keeper-audit-report.v1",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "repository": root.name,
        "repository_path": str(root),
        "summary": counts,
        "findings": findings,
    }
