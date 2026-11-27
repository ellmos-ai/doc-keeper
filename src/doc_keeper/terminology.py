"""Deterministic single-repo and cross-repo terminology congruence checker (`doc-keeper`)."""
from __future__ import annotations

import json
import os
import re
from collections.abc import Iterable, Mapping, Sequence
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

DEFAULT_SCAN_EXTENSIONS: tuple[str, ...] = (
    ".astro",
    ".html",
    ".jsx",
    ".md",
    ".mdx",
    ".mjs",
    ".ts",
    ".tsx",
)

DEFAULT_EXCLUDED_DIRS: frozenset[str] = frozenset(
    {
        ".git",
        ".pytest_cache",
        ".ruff_cache",
        ".task-worktrees",
        ".venv",
        "__pycache__",
        "_archive",
        "build",
        "dist",
        "node_modules",
        "venv",
    }
)

DEFAULT_EXCLUDED_FILES: frozenset[str] = frozenset(
    {
        "CHANGELOG.md",
        "MARKETING-LOG.txt",
        "TERMINOLOGIE-RESSOURCEN-UND-AGENTEN.md",
        "terminology-congruence.v1.json",
    }
)

_LEGACY_DOM_TOKEN_RE = re.compile(
    r"""(?:id|for|name|data-[a-z0-9_-]+)\s*=\s*["'][^"']*["']|#[a-z][a-z0-9_-]*""",
    re.IGNORECASE,
)


class TerminologySpecError(ValueError):
    """Raised when a terminology congruence specification is unreadable or invalid."""


def load_terminology_spec(spec_path: str | Path) -> dict[str, Any]:
    """Load and validate an OCEAN/ellmos terminology congruence specification JSON."""
    path = Path(spec_path).resolve()
    try:
        raw = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise TerminologySpecError(f"Terminology spec unreadable: {path} ({exc})") from exc
    if not isinstance(raw, dict):
        raise TerminologySpecError(f"Terminology spec root must be a JSON object: {path}")

    policy = raw.get("policy")
    concepts = raw.get("concepts")
    if not isinstance(policy, dict) or not isinstance(concepts, list) or not concepts:
        raise TerminologySpecError(
            f"Terminology spec missing required `policy` object or non-empty `concepts` list: {path}"
        )

    forbidden = policy.get("forbidden_in_new_ui_and_docs")
    if not isinstance(forbidden, list) or not all(isinstance(t, str) and t.strip() for t in forbidden):
        raise TerminologySpecError(
            f"Terminology spec `policy.forbidden_in_new_ui_and_docs` must be a list of strings: {path}"
        )

    return {
        "spec_path": str(path),
        "schema": str(raw.get("schema") or "unknown"),
        "schema_version": raw.get("schema_version", 1),
        "decided_at": str(raw.get("decided_at") or ""),
        "policy": policy,
        "concepts": concepts,
    }


def _resolve_spec(spec: dict[str, Any] | str | Path) -> dict[str, Any]:
    if isinstance(spec, (str, Path)):
        return load_terminology_spec(spec)
    if isinstance(spec, dict) and "policy" in spec and "concepts" in spec:
        return spec
    raise TerminologySpecError("Expected a path or loaded terminology spec dictionary")


def _surface_type(rel_path: str) -> str:
    lower = rel_path.lower()
    if lower.endswith((".astro", ".html", ".jsx", ".tsx")):
        return "ui"
    if lower.endswith((".md", ".mdx")):
        return "docs"
    return "code_ui"


def _build_term_lookup(spec: dict[str, Any]) -> tuple[dict[str, dict[str, str]], list[str], list[str]]:
    forbidden_map: dict[str, dict[str, str]] = {}
    legacy_tokens: set[str] = set()
    canonical_terms: list[str] = []

    concepts = spec.get("concepts") or []
    for concept in concepts:
        if not isinstance(concept, dict):
            continue
        cid = str(concept.get("id") or "")
        canonical = str(concept.get("canonical_de") or "")
        if canonical and canonical not in canonical_terms:
            canonical_terms.append(canonical)
        for token in concept.get("legacy_wire_compat") or []:
            if isinstance(token, str) and token.strip():
                legacy_tokens.add(token.strip())
        for dep in concept.get("deprecated_ui_terms") or []:
            if isinstance(dep, str) and dep.strip():
                forbidden_map.setdefault(
                    dep.strip().lower(),
                    {"concept_id": cid, "canonical_de": canonical},
                )

    explicit_forbidden: dict[str, dict[str, str]] = {}
    for term in (spec.get("policy") or {}).get("forbidden_in_new_ui_and_docs") or []:
        t_clean = term.strip()
        if not t_clean:
            continue
        meta = forbidden_map.get(t_clean.lower())
        if meta is None:
            # Match by substring against concept deprecated_ui_terms for best canonical suggestion.
            for concept in concepts:
                if not isinstance(concept, dict):
                    continue
                deps = [str(d).lower() for d in (concept.get("deprecated_ui_terms") or [])]
                if any(d and d in t_clean.lower() for d in deps):
                    meta = {
                        "concept_id": str(concept.get("id") or ""),
                        "canonical_de": str(concept.get("canonical_de") or ""),
                    }
                    break
        explicit_forbidden[t_clean] = meta or {"concept_id": "unmapped", "canonical_de": ""}

    return explicit_forbidden, sorted(legacy_tokens, key=len, reverse=True), canonical_terms


def _iter_candidate_files(
    root: Path,
    *,
    extensions: tuple[str, ...] = DEFAULT_SCAN_EXTENSIONS,
    include_tests: bool = False,
    excluded_dirs: Iterable[str] = DEFAULT_EXCLUDED_DIRS,
    excluded_files: Iterable[str] = DEFAULT_EXCLUDED_FILES,
) -> list[Path]:
    ex_dirs = set(excluded_dirs)
    if not include_tests:
        ex_dirs.update({"tests", "test", "__tests__"})
    ex_files = set(excluded_files)

    files: list[Path] = []
    for dirpath, dirnames, filenames in os.walk(root, topdown=True):
        dirnames[:] = sorted(d for d in dirnames if d not in ex_dirs)
        base = Path(dirpath)
        for fname in sorted(filenames):
            if fname in ex_files:
                continue
            path = base / fname
            if path.suffix.lower() not in extensions:
                continue
            if not include_tests and (
                fname.startswith("test_")
                or fname.endswith((".test.mjs", ".test.js", ".test.ts", ".spec.ts", ".spec.js"))
            ):
                continue
            files.append(path)
    return files


def _strip_legacy_wire_segments(line: str, legacy_tokens: Sequence[str]) -> tuple[str, list[str]]:
    """Remove intentional legacy wire/API/DOM identifiers from a line copy before UI term matching."""
    matched_legacy: list[str] = []
    cleaned = line
    for token in legacy_tokens:
        if token in cleaned:
            matched_legacy.append(token)
            cleaned = cleaned.replace(token, " ")
    # Remove HTML/DOM id/name/data-* attributes so e.g. id="fackel-banner" stays wire-compatible.
    cleaned = _LEGACY_DOM_TOKEN_RE.sub(" ", cleaned)
    return cleaned, matched_legacy


def audit_terminology_repository(
    repo_root: str | Path,
    spec: dict[str, Any] | str | Path,
    *,
    repo_name: str | None = None,
    extensions: tuple[str, ...] = DEFAULT_SCAN_EXTENSIONS,
    include_tests: bool = False,
    excluded_dirs: Iterable[str] = DEFAULT_EXCLUDED_DIRS,
    excluded_files: Iterable[str] = DEFAULT_EXCLUDED_FILES,
) -> dict[str, Any]:
    """Audit a single repository for terminology congruence while preserving legacy wire compatibility."""
    resolved_spec = _resolve_spec(spec)
    root = Path(repo_root).resolve()
    if not root.is_dir():
        raise TerminologySpecError(f"Repository directory does not exist: {root}")

    forbidden_terms, legacy_tokens, canonical_terms = _build_term_lookup(resolved_spec)
    # Precompile case-insensitive regexes with Unicode word boundaries where applicable.
    compiled_terms = [
        (term, meta, re.compile(rf"(?<!\w){re.escape(term)}(?!\w)", re.IGNORECASE))
        for term, meta in forbidden_terms.items()
    ]

    candidate_files = _iter_candidate_files(
        root,
        extensions=extensions,
        include_tests=include_tests,
        excluded_dirs=excluded_dirs,
        excluded_files=excluded_files,
    )

    violations: list[dict[str, Any]] = []
    legacy_hits: list[dict[str, Any]] = []
    canonical_present: set[str] = set()

    for file_path in candidate_files:
        rel_path = file_path.relative_to(root).as_posix()
        try:
            content = file_path.read_text(encoding="utf-8", errors="ignore")
        except OSError:
            continue

        for c_term in canonical_terms:
            if c_term in content:
                canonical_present.add(c_term)

        surface = _surface_type(rel_path)
        for line_no, raw_line in enumerate(content.splitlines(), start=1):
            cleaned_line, matched_legacy = _strip_legacy_wire_segments(raw_line, legacy_tokens)
            if matched_legacy:
                legacy_hits.append(
                    {
                        "file": rel_path,
                        "line": line_no,
                        "tokens": matched_legacy,
                        "surface": surface,
                    }
                )
            for term, meta, pattern in compiled_terms:
                if pattern.search(cleaned_line):
                    violations.append(
                        {
                            "rule": "TERMINOLOGY-FORBIDDEN-UI-OR-DOC",
                            "severity": "error",
                            "cause": "terminology_drift",
                            "term": term,
                            "concept_id": meta["concept_id"],
                            "canonical_de": meta["canonical_de"],
                            "file": rel_path,
                            "line": line_no,
                            "surface": surface,
                            "excerpt": raw_line.strip()[:160],
                        }
                    )

    return {
        "repo_name": repo_name or root.name,
        "repo_path": str(root),
        "ok": len(violations) == 0,
        "files_scanned": len(candidate_files),
        "violation_count": len(violations),
        "legacy_wire_compat_count": len(legacy_hits),
        "canonical_terms_present": sorted(canonical_present),
        "violations": violations,
        "legacy_wire_compat_hits": legacy_hits,
    }


def audit_terminology_cross_repo(
    repos: Sequence[str | Path] | Mapping[str, str | Path] | str | Path,
    spec: dict[str, Any] | str | Path,
    *,
    extensions: tuple[str, ...] = DEFAULT_SCAN_EXTENSIONS,
    include_tests: bool = False,
    excluded_dirs: Iterable[str] = DEFAULT_EXCLUDED_DIRS,
    excluded_files: Iterable[str] = DEFAULT_EXCLUDED_FILES,
) -> dict[str, Any]:
    """Audit one or multiple repositories against the canonical terminology specification."""
    resolved_spec = _resolve_spec(spec)

    normalized_repos: list[tuple[str, Path]] = []
    if isinstance(repos, (str, Path)):
        p = Path(repos).resolve()
        normalized_repos.append((p.name, p))
    elif isinstance(repos, Mapping):
        for name, rpath in repos.items():
            normalized_repos.append((str(name), Path(rpath).resolve()))
    else:
        for item in repos:
            p = Path(item).resolve()
            normalized_repos.append((p.name, p))

    if not normalized_repos:
        raise TerminologySpecError("At least one repository path is required for terminology_check")

    repo_reports: list[dict[str, Any]] = []
    violations_by_repo: dict[str, int] = {}
    violations_by_term: dict[str, int] = {}
    total_files = 0
    total_violations = 0
    total_legacy = 0

    for name, path in normalized_repos:
        rep = audit_terminology_repository(
            path,
            resolved_spec,
            repo_name=name,
            extensions=extensions,
            include_tests=include_tests,
            excluded_dirs=excluded_dirs,
            excluded_files=excluded_files,
        )
        repo_reports.append(rep)
        v_count = rep["violation_count"]
        violations_by_repo[name] = v_count
        total_files += rep["files_scanned"]
        total_violations += v_count
        total_legacy += rep["legacy_wire_compat_count"]
        for v in rep["violations"]:
            violations_by_term[v["term"]] = violations_by_term.get(v["term"], 0) + 1

    cross_repo_findings: list[dict[str, Any]] = []
    if len(repo_reports) > 1:
        canonical_adopters: dict[str, list[str]] = {}
        for rep in repo_reports:
            for c_term in rep["canonical_terms_present"]:
                canonical_adopters.setdefault(c_term, []).append(rep["repo_name"])

        for rep in repo_reports:
            if not rep["violations"]:
                continue
            by_concept: dict[str, list[str]] = {}
            for v in rep["violations"]:
                c_de = v.get("canonical_de") or ""
                if c_de:
                    by_concept.setdefault(c_de, []).append(v["term"])
            for c_de, used_legacy in sorted(by_concept.items()):
                aligned_peers = [r for r in canonical_adopters.get(c_de, []) if r != rep["repo_name"]]
                if aligned_peers:
                    cross_repo_findings.append(
                        {
                            "rule": "TERMINOLOGY-CROSS-REPO-ASYMMETRY",
                            "repo": rep["repo_name"],
                            "canonical_de": c_de,
                            "deprecated_terms_found": sorted(set(used_legacy)),
                            "aligned_peer_repos": sorted(aligned_peers),
                        }
                    )

    return {
        "schema": "ellmos.doc-keeper-terminology-report.v1",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "scope": "single_repo" if len(repo_reports) == 1 else "cross_repo",
        "spec_schema": resolved_spec["schema"],
        "spec_path": resolved_spec.get("spec_path", ""),
        "spec_decided_at": resolved_spec.get("decided_at", ""),
        "preserve_legacy_wire_compatibility": bool(
            (resolved_spec.get("policy") or {}).get("preserve_legacy_wire_compatibility", True)
        ),
        "ok": total_violations == 0,
        "summary": {
            "repos_scanned": len(repo_reports),
            "files_scanned": total_files,
            "total_violations": total_violations,
            "total_legacy_wire_compat_hits": total_legacy,
            "violations_by_repo": violations_by_repo,
            "violations_by_term": dict(sorted(violations_by_term.items())),
        },
        "repos": repo_reports,
        "cross_repo_findings": cross_repo_findings,
    }


terminology_check = audit_terminology_cross_repo
