# Canonical Workspace Semantics Package - Phase 4.6.2
# ====================================================

"""
Canonical semantic definitions for Workspace Content and related artifacts.

ARCHITECTURAL PRINCIPLES:
    1. All artifacts are deeply immutable (frozen dataclasses)
    2. No runtime dependencies (time, UUID generation)
    3. Bounded collections only
    4. External identity providers
    5. Semantic-time preservation

SEMANTIC MODEL STRUCTURE:
=========================

Core Identity Types:
    - WorkspaceContentIdentity      - Unique identifier for content instances
    - WorkspaceContentRevision      - Monotonically increasing version number
    - WorkspaceContentReference     - Immutable reference to content

Digest and Fingerprint Types:
    - WorkspaceContentDigest        - Cryptographic or deterministic digest
    - WorkspaceContentFingerprint   - Short fingerprint for identification

Semantic Representation Types:
    - WorkspaceContentKind          - Canonical categories (60+ kinds)
    - WorkspaceContentContext       - Semantic context without runtime embedding
    - WorkspaceContentScope         - Broadcast eligibility and target scope
    - WorkspaceContentValidity      - Validation state
    - WorkspaceContentFreshness     - Temporal relevance
    - WorkspaceContentVisibility    - Who may see the content (independent of accessibility)
    - WorkspaceContentAccessibility - Whether it can be accessed (independent of visibility)
    - WorkspaceContentAvailability  - Whether currently available

Ownership and Authority:
    - WorkspaceContentOwnership     - External ownership information (projection only)
    - WorkspaceContentAuthority     - Authority constraints for actions

Provenance and Integrity:
    - WorkspaceContentProvenance    - Complete origin chain
    - WorkspaceContentConstraint    - Limiting factors on use/interpretation
    - WorkspaceContentDependency    - Required artifacts for interpretation

Assumptions, Evidence, Justification:
    - WorkspaceContentAssumption    - Explicit underlying beliefs
    - WorkspaceContentEvidence      - Supporting or challenging evidence
    - WorkspaceContentJustification - Rationale and explanation

Lifecycle Management:
    - WorkspaceContentLifecycle     - Semantic lifecycle states (not runtime)
    - WorkspaceContentMetadata      - Administrative metadata

Utilities:
    - WorkspaceContentKindRegistry  - Extensible kind registration
    - WorkspaceContentValidator     - Validation logic without runtime deps
"""

from __future__ import annotations

# =============================================================================
# IDENTITY TYPES
# =============================================================================

WorkspaceContentIdentity = str
"""Unique identifier for workspace content (deterministic, replayable)."""

WorkspaceContentRevision = int
"""Monotonically increasing revision number."""

WorkspaceContentReference = str
"""Immutable reference to Workspace Content ("identity@revision")."""

WorkspaceContentDigest = str
"""Cryptographic or deterministic digest of semantic content."""

WorkspaceContentFingerprint = str
"""Short fingerprint for quick identification."""


# =============================================================================
# CONTENT KINDS TAXONOMY
# =============================================================================

from .content import WorkspaceContentKind


# =============================================================================
# CONTEXT TYPES - Semantic context without runtime embedding
# =============================================================================

from .content import (
    TaskContext,
    GoalContext,
    DecisionContext,
    ReasoningContext,
    PlanningContext,
    ExecutiveContext,
    AttentionContext,
    MotivationContext,
    TemporalContext,
    SpatialContext,
    EnvironmentalContext,
    IdentityContext,
    PerceptualContext,
    OperationalContext,
)


# =============================================================================
# SEMANTIC REPRESENTATION TYPES
# =============================================================================

from .content import (
    WorkspaceContentContext,
    WorkspaceContentScope,
    WorkspaceContentValidity,
    WorkspaceContentFreshness,
    WorkspaceContentVisibility,
    WorkspaceContentAccessibility,
    WorkspaceContentAvailability,
)


# =============================================================================
# OWNERSHIP AND AUTHORITY
# =============================================================================

from .content import (
    WorkspaceContentOwnership,
    WorkspaceContentAuthority,
)


# =============================================================================
# PROVENANCE AND INTEGRITY
# =============================================================================

from .content import (
    WorkspaceContentProvenance,
    WorkspaceContentConstraint,
    WorkspaceContentDependency,
)


# =============================================================================
# ASSUMPTIONS, EVIDENCE, JUSTIFICATION
# =============================================================================

from .content import (
    WorkspaceContentAssumption,
    WorkspaceContentEvidence,
    WorkspaceContentJustification,
)


# =============================================================================
# LIFECYCLE MANAGEMENT
# =============================================================================

from .content import (
    WorkspaceContentLifecycle,
)


# =============================================================================
# METADATA AND UTILITIES
# =============================================================================

from .content import (
    WorkspaceContentMetadata,
    WorkspaceContentKindRegistry,
    WorkspaceContentValidator,
)


# =============================================================================
# PRIMARY SEMANTIC ARTIFACT
# =============================================================================

from .content import WorkspaceContent


__all__ = [
    # Identity types
    "WorkspaceContentIdentity",
    "WorkspaceContentRevision",
    "WorkspaceContentReference",
    "WorkspaceContentDigest",
    "WorkspaceContentFingerprint",

    # Content kinds taxonomy (60+ canonical kinds)
    "WorkspaceContentKind",

    # Context types
    "TaskContext",
    "GoalContext",
    "DecisionContext",
    "ReasoningContext",
    "PlanningContext",
    "ExecutiveContext",
    "AttentionContext",
    "MotivationContext",
    "TemporalContext",
    "SpatialContext",
    "EnvironmentalContext",
    "IdentityContext",
    "PerceptualContext",
    "OperationalContext",

    # Semantic representation types
    "WorkspaceContentContext",
    "WorkspaceContentScope",
    "WorkspaceContentValidity",
    "WorkspaceContentFreshness",
    "WorkspaceContentVisibility",
    "WorkspaceContentAccessibility",
    "WorkspaceContentAvailability",

    # Ownership and authority
    "WorkspaceContentOwnership",
    "WorkspaceContentAuthority",

    # Provenance and integrity
    "WorkspaceContentProvenance",
    "WorkspaceContentConstraint",
    "WorkspaceContentDependency",

    # Assumptions, evidence, justification
    "WorkspaceContentAssumption",
    "WorkspaceContentEvidence",
    "WorkspaceContentJustification",

    # Lifecycle management
    "WorkspaceContentLifecycle",

    # Metadata and utilities
    "WorkspaceContentMetadata",
    "WorkspaceContentKindRegistry",
    "WorkspaceContentValidator",

    # Primary semantic artifact
    "WorkspaceContent",
]