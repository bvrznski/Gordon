# Gordon Phase 5.7.2-I: Experiential Field Builder
# ===============================================================================
#
# Canonical implementation of the experiential field construction capability.
#
"""
Experiential Field Builder Package

This package implements Gordon's canonical deterministic, bounded,
provenance-preserving experiential field builder.

Architectural Position:
    Perception ──────────────┐
    Memory ──────────────────┤
    Workspace ───────────────┤
    Salience ────────────────┤
    Attention ───────────────┤
    Personality ─────────────┤
    Motivation ──────────────┤
    Cognition Proposals ─────┤
    Action Feedback ─────────┤
                             ▼
                    Context Contributions
                             ▼
                  Experiential Field Builder
                             ▼
                  Immutable Field Snapshot
                             ▼
             Consciousness Public Facade
                             ▼
              Cognition / Agency / Action

Key Responsibilities:
    - Deterministic field construction from contributions
    - Immutable snapshot production with atomic transitions
    - Contribution validation and normalization
    - Duplicate detection and resolution
    - Capacity enforcement and bounded content sets
    - Field-level relation assembly
    - Provenance preservation across generations
    - Deterministic ordering for reproducibility

Not Responsible For:
    - Global availability (Workspace Network)
    - Persistence (Memory System)  
    - Reasoning/interpretation (Cognition)
    - Decision making (Agency)
    - Action execution (Action)
    - Intentionality semantics (Phase 5.7.3)
    - Temporal continuity (Phase 5.7.4)
    - Presence/awareness semantics (Phase 5.7.5)
    - Perspective/self-reference (Phase 5.7.6)
    - Situated world interpretation (Phase 5.7.7)

Version: 5.7.2-I
"""


# =============================================================================
# VERSION AND METADATA
# =============================================================================

__version__ = "5.7.2-I"
"""Package semantic version for Phase 5.7.2-I implementation."""

__name__ = "gordon.agent.capabilities.consciousness.experiential_field"
"""Fully qualified package name."""

__docformat__ = "google"


# =============================================================================
# CAPABILITY OWNERSHIP
# =============================================================================

_EXPERIENTIAL_FIELD_BUILDER_ID = "experiential-field-builder-001"
"""Canonical experiential field builder identity."""


# =============================================================================
# IMPORTS - Public API
# =============================================================================

from gordon.agent.components.systems.consciousnessbuilder import ExperientialFieldBuilder, FieldBuildResult, FieldBuildRequest
from gordon.agent.components.systems.consciousnesssnapshot import ExperientialFieldSnapshot, FieldContent, FieldRelation
from gordon.agent.components.systems.consciousnesstransition import (
    FieldTransition,
    FieldTransitionAuthority,
    TransitionCommitResult,
)
from gordon.agent.components.systems.consciousnessnormalization import ContributionNormalizer, NormalizationAction
from gordon.agent.components.systems.consciousnessvalidation import (
    ContributionValidator,
    ValidationOutcome,
    RejectionReason,
)
from gordon.agent.components.systems.consciousnesscapacity import FieldCapacityPolicy, CapacityEnforcementResult
from gordon.agent.components.systems.consciousnessordering import DeterministicOrderer, OrderingKey
from gordon.agent.components.systems.consciousnessintegrity import FieldIntegrityChecker, IntegrityCheckResult

# =============================================================================
# PUBLIC API
# =============================================================================

__all__: tuple[str, ...] = (
    # Builder core
    "ExperientialFieldBuilder",
    "FieldBuildResult",
    "FieldBuildRequest",
    # Snapshot model
    "ExperientialFieldSnapshot",
    "FieldContent",
    "FieldRelation",
    # Transition management
    "FieldTransition",
    "FieldTransitionAuthority",
    "TransitionCommitResult",
    # Normalization
    "ContributionNormalizer",
    "NormalizationAction",
    # Validation
    "ContributionValidator",
    "ValidationOutcome",
    "RejectionReason",
    # Capacity
    "FieldCapacityPolicy",
    "CapacityEnforcementResult",
    # Ordering
    "DeterministicOrderer",
    "OrderingKey",
    # Integrity
    "FieldIntegrityChecker",
    "IntegrityCheckResult",
)