"""CLI entry point for `doc-keeper` (`python -m doc_keeper`)."""
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Sequence

from .classifier import load_doc_machine_config
from .extractor import audit_repository


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="doc-keeper",
        description="3-Cause Documentation Auditor & Decision Processing Rule Router (Ocean / BACH).",
    )
    sub = parser.add_subparsers(dest="command", required=True)

    p_audit = sub.add_parser("audit", help="Audit a repository's documentation against code reality.")
    p_audit.add_argument("repo", nargs="?", default=".", help="Target repository path (default: current directory)")
    p_audit.add_argument("--json", action="store_true", help="Print full JSON report to stdout")
    p_audit.add_argument("--output", type=Path, help="Write JSON report to file")

    p_rules = sub.add_parser("rules", help="Show active Decision Processing Rules for a repository.")
    p_rules.add_argument("repo", nargs="?", default=".", help="Target repository path")

    args = parser.parse_args(argv)
    if args.command == "rules":
        cfg = load_doc_machine_config(Path(args.repo).resolve())
        print(json.dumps(cfg, indent=2, ensure_ascii=False))
        return 0

    report = audit_repository(Path(args.repo).resolve())
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    if args.json or not args.output:
        print(json.dumps(report, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
