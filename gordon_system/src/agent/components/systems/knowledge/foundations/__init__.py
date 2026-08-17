# Knowledge Foundations - Phase 6.1
# ===================================

"""
Knowledge Foundations: Universal semantic primitives for Gordon's knowledge capability.

This module defines the foundational semantic primitives that form the basis of
semantic organization in Gordon's cognitive system:

    Identity     - Unique semantic identity
    Provenance   - Origin tracking and history
    Validity     - Truth and logical soundness assessment
    Confidence   - Semantic certainty metrics
    Uncertainty  - Semantic ambiguity metrics  
    Revision     - Change management and versioning
    Scope        - Semantic domain boundaries
    Authority    - Source reliability and weight

These primitives work together to provide stable, revisable semantic structure
that transforms grounded evidence into knowledge.
"""

from __future__ import annotations

# Core foundations (Phase 6.1)
from .shared.artifact import (
    SemanticLifecycleState,
    SemanticPublicationStatus,
    SemanticCompatibilityKind,
    SemanticCertificationLevel,
    SemanticValidationLevel,
    BaseKnowledgeArtifact,
)

from .identity import (
    IdentitySource,
    IdentityResolution,
    SemanticIdentity,
    IdentityTracker,
    IdentityValidator,
)

from .provenance import (
    ProvenanceAction,
    ProvenanceEvent,
    ProvenanceTrail,
    ProvenanceValidator,
)

from .validity import (
    ValidityState,
    EvidenceKind,
    ValidityEvidence,
    ValidityAssessment,
    ValidityEngine,
)

from .confidence import (
    ConfidenceSource,
    SemanticConfidence,
    ConfidenceAggregator,
)

from .uncertainty import (
    UncertaintySource,
    SemanticUncertainty,
    UncertaintyAggregator,
)

from .revision import (
    RevisionEventType,
    RevisionEvent,
    RevisionHistory,
    RevisionManager,
)

from .scope import (
    ScopeDomain,
    ScopeBoundary,
    SemanticScope,
    ScopeValidator,
)

from .authority import (
    AuthorityLevel,
    AuthoritySource,
    AuthorityAssessment,
    AuthorityValidator,
)

# Lifecycle management (Part 2 - Section 1)
from .lifecycle import (
    LifecycleState,
    LifecycleTransition,
    LifecycleHistory,
    LifecycleManager,
)

from .compatibility import (
    CompatibilityKind,
    CompatibilityRecord,
    MigrationRecord,
    CompatibilityEngine,
)

from .governance import (
    GovernanceFindingKind,
    GovernanceFinding,
    GovernanceEvaluation,
    GovernanceEngine,
)

from .replay import (
    ReplayStatus,
    ReplayRecord,
    HistoricalRecord,
    ReplayEngine,
)

from .observability import (
    ObservabilityMetric,
    ObservabilityReport,
    ObservabilityEngine,
)

__all__ = [
    # Artifact base contract and enums
    "SemanticLifecycleState",
    "SemanticPublicationStatus", 
    "SemanticCompatibilityKind",
    "SemanticCertificationLevel",
    "SemanticValidationLevel",
    "BaseKnowledgeArtifact",
    # Identity
    "IdentitySource",
    "IdentityResolution",
    "SemanticIdentity",
    "IdentityTracker",
    "IdentityValidator",
    # Provenance
    "ProvenanceAction",
    "ProvenanceEvent",
    "ProvenanceTrail",
    "ProvenanceValidator",
    # Validity
    "ValidityState",
    "EvidenceKind",
    "ValidityEvidence",
    "ValidityAssessment",
    "ValidityEngine",
    # Confidence
    "ConfidenceSource",
    "SemanticConfidence",
    "ConfidenceAggregator",
    # Uncertainty
    "UncertaintySource",
    "SemanticUncertainty",
    "UncertaintyAggregator",
    # Revision
    "RevisionEventType",
    "RevisionEvent",
    "RevisionHistory",
    "RevisionManager",
    # Scope
    "ScopeDomain",
    "ScopeBoundary",
    "SemanticScope",
    "ScopeValidator",
    # Authority
    "AuthorityLevel",
    "AuthoritySource",
    "AuthorityAssessment",
    "AuthorityValidator",
    # Lifecycle management
    "LifecycleState",
    "LifecycleTransition",
    "LifecycleHistory",
    "LifecycleManager",
    # Compatibility management  
    "CompatibilityKind",
    "CompatibilityRecord",
    "MigrationRecord",
    "CompatibilityEngine",
    # Governance management
    "GovernanceFindingKind",
    "GovernanceFinding",
    "GovernanceEvaluation",
    "GovernanceEngine",
    # Replay and historical
    "ReplayStatus",
    "ReplayRecord",
    "HistoricalRecord",
    "ReplayEngine",
    # Observability
    "ObservabilityMetric",
    "ObservabilityReport",
    "ObservabilityEngine",
]
