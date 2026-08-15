# Workspace Evaluation Request
# ============================

"""
Canonical evaluation request definitions.

ARCHITECTURAL PRINCIPLES:
    - Deeply immutable (frozen dataclass)
    - No runtime dependencies
    - External time providers only
    - Bounded collections
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Tuple, Optional
from enum import Enum


# =============================================================================
# EVALUATION PURPOSE
# =============================================================================

class WorkspaceEvaluationPurpose(Enum):
    """
    Canonical evaluation purposes.
    
    Purpose does not imply selection authority.
    """

    # =========================================================================
    # PREPARATION PURPOSES
    # =========================================================================

    PREPARE_FOR_COMPETITION = "prepare_for_competition"
    """Initial evaluation for upcoming competition."""

    # =========================================================================
    # REEVALUATION PURPOSES
    # =========================================================================

    REEVALUATE_AFTER_CONTEXT_CHANGE = "reevaluate_after_context_change"
    """Re-evaluation after context changes materially."""

    REEVALUATE_AFTER_CANDIDATE_REVISION = "reevaluate_after_candidate_revision"
    """Re-evaluation after candidate revision changes."""

    REEVALUATE_AFTER_POLICY_CHANGE = "reevaluate_after_policy_change"
    """Re-evaluation after policy changes."""

    REEVALUATE_AFTER_SECURITY_CHANGE = "reevaluate_after_security_change"
    """Re-evaluation after security changes."""

    REEVALUATE_AFTER_ATTENTION_CHANGE = "reevaluate_after_attention_change"
    """Re-evaluation after attention state changes."""

    REEVALUATE_AFTER_EXECUTIVE_MODULATION = "reevaluate_after_executive_modulation"
    """Re-evaluation after executive modulation changes."""

    REEVALUATE_AFTER_MOTIVATION_CHANGE = "reevaluate_after_motivation_change"
    """Re-evaluation after motivation state changes."""

    REEVALUATE_AFTER_SOURCE_RELIABILITY_CHANGE = "reevaluate_after_source_reliability_change"
    """Re-evaluation after source reliability changes."""

    REEVALUATE_AFTER_FRESHNESS_CHANGE = "reevaluate_after_freshness_change"
    """Re-evaluation after freshness changes."""

    # =========================================================================
    # AUDIT PURPOSES
    # =========================================================================

    AUDIT_EVALUATION = "audit_evaluation"
    """Evaluation audit or review."""

    REPLAY_EVALUATION = "replay_evaluation"
    """Historical replay evaluation."""

    # =========================================================================
    # GENERAL PURPOSES
    # =========================================================================

    GENERAL = "general"
    """General purpose evaluation."""

    UNKNOWN = "unknown"
    """Unknown or unspecified purpose."""


# =============================================================================
# EVALUATION REQUEST
# =============================================================================

@dataclass(frozen=True, slots=True)
class WorkspaceEvaluationRequest:
    """
    Immutable evaluation request.

    The request must not contain:
        - evaluators as callbacks
        - model clients
        - runtime capability objects
        - service handles
        - clocks
        - random generators
        - mutable caches
        - queues
        - futures

    ARCHITECTURAL INVARIANTS:
        WER-INV-001: Request never performs evaluation
        WER-INV-002: Request never invokes runtime services
        WER-INV-003: Request is deterministic from inputs
    """

    # Identity
    identity: str
    """Unique identifier for this request."""

    revision: int
    """Revision number for this request."""

    # References
    candidate_pool: str
    """Reference to source Candidate Pool."""

    context: str
    """Reference to evaluation Context."""

    dimension_set: str
    """Reference to Dimension Set."""

    # Purpose and Scope
    purpose: WorkspaceEvaluationPurpose
    """Evaluation purpose."""

    scope: Tuple[str, ...] = field(default_factory=tuple)
    """Scope identifiers for this evaluation."""

    authority: str
    """Authority reference for this request."""

    # Requirements and Constraints
    requirements: Tuple[str, ...] = field(default_factory=tuple)
    """Requirement references."""

    constraints: Tuple[str, ...] = field(default_factory=tuple)
    """Constraint references."""

    # Semantic Time
    semantic_time: str
    """Semantic time reference (external provider)."""

    # Privacy and Provenance
    privacy: str = "internal_only"
    """Privacy classification."""

    provenance: str = ""
    """Provenance reference."""

    # Bounded collections (max 1000 items each)
    @classmethod
    def create(
        cls,
        identity: str,
        revision: int,
        candidate_pool_ref: str,
        context_ref: str,
        dimension_set_ref: str,
        purpose: WorkspaceEvaluationPurpose,
        scope: Tuple[str, ...] = tuple(),
        authority_ref: str = "",
        requirements: Tuple[str, ...] = tuple(),
        constraints: Tuple[str, ...] = tuple(),
        semantic_time_ref: str = "semantic_time_origin",
        privacy_class: str = "internal_only",
        provenance_ref: str = "",
    ) -> WorkspaceEvaluationRequest:
        """
        Create a new evaluation request.

        Args:
            identity: Unique identifier
            revision: Request revision number
            candidate_pool_ref: Candidate Pool reference
            context_ref: Context reference
            dimension_set_ref: Dimension Set reference
            purpose: Evaluation purpose
            scope: Scope identifiers (bounded to 1000)
            authority_ref: Authority reference
            requirements: Requirement references (bounded to 1000)
            constraints: Constraint references (bounded to 1000)
            semantic_time_ref: Semantic time reference
            privacy_class: Privacy classification
            provenance_ref: Provenance reference

        Returns:
            New WorkspaceEvaluationRequest instance
        """
        return cls(
            identity=identity,
            revision=revision,
            candidate_pool=candidate_pool_ref,
            context=context_ref,
            dimension_set=dimension_set_ref,
            purpose=purpose,
            scope=scope[:1000],  # Bounded
            authority=authority_ref,
            requirements=requirements[:1000],  # Bounded
            constraints=constraints[:1000],  # Bounded
            semantic_time=semantic_time_ref,
            privacy=privacy_class,
            provenance=provenance_ref,
        )