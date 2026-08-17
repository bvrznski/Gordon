# Knowledge-Memory Evidence Integration
# =====================================

"""
Evidence retrieval and eligibility modules for Knowledge-Memory Integration.

This module implements:

1. Memory Evidence Request - Requests memory artifacts as evidence
2. Memory Evidence Response - Returns retained memory artifacts with metadata
3. Evidence Eligibility - Determines which artifacts may participate in extraction
4. Evidence Set Construction - Groups eligible evidence for semantic operations

The Evidence layer enables Knowledge to request retained experiences while
preserving the architectural boundary: Memory owns retention, Integration
coordinates retrieval, and Knowledge owns interpretation.
"""

from .request import (
    EvidenceRequest,
    RequestedArtifactKinds,
    SourceRoleFilter,
)

from .response import (
    EvidenceResponse,
    RetrievalStatus,
    SupersessionState,
    ConfidenceBounds,
)

from .eligibility import (
    EvidenceEligibility,
    EligibilityKind,
)

from .evidence_set import (
    KnowledgeMemoryEvidenceSet,
)

__all__ = [
    "EvidenceRequest",
    "RequestedArtifactKinds",
    "SourceRoleFilter",
    "EvidenceResponse",
    "RetrievalStatus",
    "SupersessionState",
    "ConfidenceBounds",
    "EvidenceEligibility",
    "EligibilityKind",
    "KnowledgeMemoryEvidenceSet",
]