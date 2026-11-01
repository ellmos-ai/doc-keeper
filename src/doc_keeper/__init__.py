"""doc-keeper: Reusable 3-Cause Documentation Auditor & Decision Rule Router."""
from .classifier import (
    AVAILABLE_DECISION_BRANCHES,
    DEFAULT_DOC_MACHINE_CONFIG,
    classify_doc_reality_diff,
    load_doc_machine_config,
    resolve_doc_machine_dispatch,
)
from .extractor import audit_repository, extract_repo_claims

__all__ = [
    "AVAILABLE_DECISION_BRANCHES",
    "DEFAULT_DOC_MACHINE_CONFIG",
    "audit_repository",
    "classify_doc_reality_diff",
    "extract_repo_claims",
    "load_doc_machine_config",
    "resolve_doc_machine_dispatch",
]
__version__ = "0.1.0"
