# Reward Network - Evidence Model
# ================================

"""
Canonical Reward Evidence model (Phase 4.10.2).

RewardEvidence represents semantic facts supporting or contradicting future
reward estimates. Each evidence item is immutable, traceable, and explicitly
linked to the outcomes that generated it.

EVIDENCE LAWS:
    EVIDENCE-LAW-001: Every RewardEvidence references at least one Outcome
    EVIDENCE-LAW-002: RewardEvidence preserves semantic identity
    EVIDENCE-LAW-003: RewardEvidence preserves provenance
    EVIDENCE-LAW-004: RewardEvidence is immutable
    EVIDENCE-LAW-005: Evidence processing remains deterministic
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Tuple, Optional


# =============================================================================
# CANONICAL EVIDENCE TYPES (Part 1)
# =============================================================================

EvidenceType = str
"""
Canonical evidence type identifier.
"""


EvidenceKind = str
"""
Semantic kind of evidence within a type.

EVIDENCE KINDS:
    • goal_progress: Goal advancement detected
    • goal_retreat: Goal regression detected  
    • resource_acquired: Resources gained
    • resource_lost: Resources depleted
    • constraint_satisfied: Constraints met
    • constraint_violated: Constraints breached
    • prediction_success: Predictive accuracy confirmed
    • prediction_failure: Prediction error occurred
    • behavior_reinforced: Behavior strengthened
    • behavior_suppressed: Behavior weakened
    • social_approve: Social validation received
    • social_reject: Social disapproval received
    • knowledge_gained: New knowledge acquired
    • knowledge_lost: Knowledge forgotten
    • unexpected_success: Unpredicted positive outcome
    • unexpected_failure: Unpredicted negative outcome
"""


# =============================================================================
# CANONICAL EVIDENCE MODEL (Part 1)
# =============================================================================

@dataclass(frozen=True, slots=True)
class RewardEvidence:
    """
    Canonical semantic evidence supporting or contradicting reward estimates.

    Every reward estimate derives from structured evidence. Evidence remains
    immutable and traceable through its complete lifecycle.

    EVIDENCE PROPERTIES:
        • evidence_id: Unique identifier for this evidence item
        • evidence_type: Canonical type (OutcomeEvidence, GoalEvidence, etc.)
        • evidence_kind: Semantic kind within the type
        • outcome_ref: Reference to the generating Outcome
        • semantic_content: The semantic fact itself
        • relationship: Whether it supports/contradicts reward/punishment
        • confidence: How reliable this evidence is
        • uncertainty: What information is missing or ambiguous
        • timescale: Temporal scope (immediate, short-term, etc.)
        • provenance: Source subsystem and trace information

    EVIDENCE RELATIONSHIPS:
        • supports_reward: Evidence that increases estimated reward
        • supports_punishment: Evidence that increases punishment value
        • contradicts_reward: Evidence that decreases estimated reward
        • contradicts_punishment: Evidence that decreases punishment value
        • unknown: Relationship is not determined

    EVIDENCE TIMESCALES:
        • immediate: Current time step evidence
        • short_term: Recent history (last N steps)
        • medium_term: Medium-term pattern evidence
        • long_term: Historical pattern evidence
        • persistent: Long-lasting state evidence
        • predicted: Future-expected evidence

    EVIDENCE NOT RESPONSIBLE FOR:
        • Computing reward values
        • Estimating benefit/cost
        • Making executive decisions
        • Modifying system state
    """

    # Identity and reference
    evidence_id: str
    """Unique identifier for this evidence item."""

    evidence_type: EvidenceType
    """Canonical type (e.g., 'outcome', 'goal', 'resource')."""

    evidence_kind: EvidenceKind
    """Semantic kind within the evidence type."""

    outcome_ref: Tuple[str, ...]
    """Reference(s) to Outcome IDs that generated this evidence."""

    # Semantic content
    semantic_content: str
    """The actual semantic fact being evidenced."""

    relationship: str = "unknown"
    """Relationship to reward/punishment (see EVIDENCE RELATIONSHIPS)."""

    # Quality assessment
    confidence: float = 0.5
    """How reliable this evidence is (0.0 to 1.0)."""

    uncertainty: float = 0.0
    """What information is missing or ambiguous (0.0 to 1.0)."""

    # Temporal semantics
    timescale: str = "immediate"
    """Temporal scope of this evidence (see EVIDENCE TIMESCALES)."""

    # Provenance and attribution
    source_subsystem: Optional[str] = None
    """Origin subsystem that produced this evidence."""

    provenance: Optional[str] = None
    """Provenance reference for this evidence type."""

    context: Tuple[str, ...] = field(default_factory=tuple)
    """Semantic context (e.g., goal_id, task_id, world_state)."""

    # Revision and metadata
    revision: int = 0
    """Revision number for versioning."""

    created_at_utc: str = ""
    """When this evidence was produced (ISO 8601)."""

    # Optional metadata fields
    derived_from: Tuple[str, ...] = field(default_factory=tuple)
    """References to other evidence items this was derived from."""

    @property
    def canonical_identity(self) -> str:
        """Return fully qualified canonical identity."""
        return f"{self.evidence_id}@v{self.revision}"

    @classmethod
    def create(
        cls,
        evidence_id: str,
        evidence_type: EvidenceType,
        evidence_kind: EvidenceKind,
        outcome_ref: Tuple[str, ...],
        semantic_content: str,
        relationship: str = "unknown",
        confidence: float = 0.5,
        uncertainty: float = 0.0,
        timescale: str = "immediate",
        source_subsystem: Optional[str] = None,
        context: Tuple[str, ...] = tuple(),
        derived_from: Tuple[str, ...] = tuple(),
    ) -> RewardEvidence:
        """
        Create a new evidence item.

        Args:
            evidence_id: Unique identifier for this evidence
            evidence_type: Canonical type of evidence
            evidence_kind: Semantic kind within the type
            outcome_ref: Reference(s) to generating Outcomes
            semantic_content: The semantic fact being evidenced
            relationship: Relationship to reward/punishment
            confidence: How reliable this evidence is
            uncertainty: What information is missing or ambiguous
            timescale: Temporal scope of this evidence
            source_subsystem: Origin subsystem
            context: Semantic context
            derived_from: References to other evidence items this was derived from

        Returns:
            New RewardEvidence instance
        """
        return cls(
            evidence_id=evidence_id,
            revision=0,
            evidence_type=evidence_type,
            evidence_kind=evidence_kind,
            outcome_ref=outcome_ref,
            semantic_content=semantic_content,
            relationship=relationship,
            confidence=confidence,
            uncertainty=uncertainty,
            timescale=timescale,
            source_subsystem=source_subsystem,
            context=context,
            derived_from=derived_from,
        )


# =============================================================================
# CANONICAL EVIDENCE ATTRIBUTION (Part 1)
# =============================================================================

@dataclass(frozen=True, slots=True)
class EvidenceAttribution:
    """
    Attribution information for a RewardEvidence item.

    Every evidence item records its origin subsystem, object, event, context,
    and revision. Complete attribution remains explicit and immutable.

    ATTRIBUTION PROPERTIES:
        • origin_subsystem: Source subsystem that produced the evidence
        • origin_outcome: Outcome ID that triggered this evidence
        • origin_event: Event type or action
        • origin_revision: Revision number at time of attribution
        • origin_context: Context at time of attribution
        • origin_policy: Policy reference at time of attribution

    ATTRIBUTION INVARIANTS:
        • Attribution remains immutable once set
        • Source subsystem is always explicit
        • Origin outcome is always traceable
    """

    origin_subsystem: str
    """Source subsystem that produced this evidence."""

    origin_outcome: Tuple[str, ...]
    """Outcome ID(s) that triggered this evidence."""

    origin_event: Optional[str] = None
    """Event type or action name."""

    origin_revision: int = 0
    """Revision number at time of attribution."""

    origin_context: Tuple[str, ...] = field(default_factory=tuple)
    """Context at time of attribution."""

    origin_policy: Optional[str] = None
    """Policy reference at time of attribution."""

    origin_semantic_time: str = "immediate"
    """Semantic time at time of attribution."""


# =============================================================================
# CANONICAL EVIDENCE SOURCE SUBSYSTEM (Part 1)
# =============================================================================

EvidenceSourceSubsystem = str
"""
Canonical source subsystem identifier for evidence.

SUBSYSTEMS:
    • predictive: Predictive Processing Network
    • salience: Salience Network
    • attention: Attention Network
    • executive: Executive Control Network
    • motivation: Motivation System
    • memory: Memory System
    • action: Action Selection System
    • world_model: World Model System
    • goal: Goal System
"""

# =============================================================================
# CANONICAL EVIDENCE PROVENANCE (Part 1)
# =============================================================================

EvidenceProvenance = str
"""
Provenance reference for a RewardEvidence item.
Indicates where this evidence type is documented or specified.
"""