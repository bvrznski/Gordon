# Reward Network - Evidence Attribution
# ======================================

"""
Evidence attribution models for RewardEvidence.

Every evidence item records its origin subsystem, object, event, context,
and revision. Complete attribution remains explicit and immutable.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Tuple, Optional


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

    ATTRIBUTION LAWS:
        ATTRIBUTION-LAW-001: Every RewardEvidence possesses explicit attribution
        ATTRIBUTION-LAW-002: Source subsystem remains explicit
        ATTRIBUTION-LAW-003: Origin object remains explicit
        ATTRIBUTION-LAW-004: Origin context remains explicit
        ATTRIBUTION-LAW-005: Origin revision remains explicit
        ATTRIBUTION-LAW-006: Origin semantic time remains explicit
        ATTRIBUTION-LAW-007: Attribution remains immutable
        ATTRIBUTION-LAW-008: Attribution shall never be inferred retrospectively
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


EvidenceProvenance = str
"""
Provenance reference for a RewardEvidence item.
Indicates where this evidence type is documented or specified.
"""

# =============================================================================
# ATTRIBUTION HELPER FUNCTIONS
# =============================================================================


def create_evidence_attribution(
    origin_subsystem: str,
    origin_outcome: Tuple[str, ...],
    origin_event: Optional[str] = None,
    origin_revision: int = 0,
    origin_context: Tuple[str, ...] = tuple(),
    origin_policy: Optional[str] = None,
    origin_semantic_time: str = "immediate",
) -> EvidenceAttribution:
    """
    Create a new evidence attribution.

    Args:
        origin_subsystem: Source subsystem that produced the evidence
        origin_outcome: Outcome ID(s) that triggered this evidence
        origin_event: Event type or action name
        origin_revision: Revision number at time of attribution
        origin_context: Context at time of attribution
        origin_policy: Policy reference at time of attribution
        origin_semantic_time: Semantic time at time of attribution

    Returns:
        New EvidenceAttribution instance
    """
    return EvidenceAttribution(
        origin_subsystem=origin_subsystem,
        origin_outcome=origin_outcome,
        origin_event=origin_event,
        origin_revision=origin_revision,
        origin_context=origin_context,
        origin_policy=origin_policy,
        origin_semantic_time=origin_semantic_time,
    )