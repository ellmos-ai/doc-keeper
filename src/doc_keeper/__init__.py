"""doc-keeper: Reusable 3-Cause Documentation Auditor & Decision Rule Router."""
from .classifier import (
    AVAILABLE_DECISION_BRANCHES,
    DEFAULT_DOC_MACHINE_CONFIG,
    classify_doc_reality_diff,
    load_doc_machine_config,
    resolve_doc_machine_dispatch,
)
from .extractor import audit_repository, extract_repo_claims
from .terminology import (
    TerminologySpecError,
    audit_terminology_cross_repo,
    audit_terminology_repository,
    load_terminology_spec,
    terminology_check,
)

__all__ = [
    "AVAILABLE_DECISION_BRANCHES",
    "DEFAULT_DOC_MACHINE_CONFIG",
    "TerminologySpecError",
    "audit_repository",
    "audit_terminology_cross_repo",
    "audit_terminology_repository",
    "classify_doc_reality_diff",
    "extract_repo_claims",
    "load_doc_machine_config",
    "load_terminology_spec",
    "resolve_doc_machine_dispatch",
    "terminology_check",
]
__version__ = "0.1.0"
