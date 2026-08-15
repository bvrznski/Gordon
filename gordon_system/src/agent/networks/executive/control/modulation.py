# Gordon Executive Network - Control Modulation Proposals
# =========================================================

"""
Control Modulation Proposals for Phase 4.4.7.

These are semantic proposals to alter the relative activation, maintenance,
accessibility, suppression, gating, stability, or review status of executive
or cognitive structures.
"""

from dataclasses import dataclass, field
from typing import Tuple, Optional, Literal

# =============================================================================
# MODULATION PROPOSAL BASE TYPE
# =============================================================================


@dataclass(frozen=True)
class TopDownModulationProposal:
    """
    A top-down modulation proposal to alter a target's activation or state.

    A modulation proposal must not contain:
        * callback;
        * concrete provider;
        * service endpoint;
        * mutable subsystem object;
        * runtime queue;
        * execution command.
    """

    proposal_id: str
    target_id: str
    target_kind: str
    target_revision: int
    modulation_kind: Literal[
        "maintenance",
        "stabilization",
        "facilitation",
        "amplification",
        "attenuation",
        "suppression_review",
        "gating",
        "release",
        "refresh",
        "accessibility_increase",
        "accessibility_decrease",
        "evidence_acquisition",
        "monitoring_increase",
        "monitoring_decrease",
        "review_request",
        "switch_preparation",
        "recovery_support",
        "decision_support",
    ]
    direction: Literal["increase", "decrease", "maintain"]
    requested_intensity: str
    persistence: str
    purpose: Optional[str] = None
    supporting_allocation_id: Optional[str] = None
    expected_effect: Optional[str] = None
    constraints: Tuple[str, ...] = field(default_factory=tuple)
    authority_required: Optional[str] = None
    expiration: Optional[str] = None
    confidence_class: str = "unknown"
    limitations: Tuple[str, ...] = field(default_factory=tuple)


# =============================================================================
# FACILITATION PROPOSAL
# =============================================================================


@dataclass(frozen=True)
class ExecutiveFacilitationProposal:
    """Proposal to facilitate a target's engagement."""

    proposal_id: str
    target_kind: Literal[
        "planning",
        "reasoning",
        "evidence_acquisition",
        "decision_preparation",
        "working_memory_maintenance",
        "focus_stabilization",
        "monitoring",
        "recovery",
        "communication_preparation",
    ]
    intensity: str
    persistence: str


# =============================================================================
# ATTENUATION PROPOSAL
# =============================================================================


@dataclass(frozen=True)
class ExecutiveAttenuationProposal:
    """Proposal to attenuate a target's engagement."""

    proposal_id: str
    target_kind: Literal[
        "low_value_cognitive_engagement",
        "repetitive_reasoning",
        "resolved_conflict_review",
        "obsolete_monitoring",
        "superseded_strategy_support",
        "excessive_control",
        "low_relevance_workspace_review",
        "stale_evidence_maintenance",
    ]
    intensity: str
    release_conditions: Tuple[str, ...] = field(default_factory=tuple)


# =============================================================================
# GATING PROPOSAL
# =============================================================================


@dataclass(frozen=True)
class ExecutiveGatingProposal:
    """Proposal to gate a target's progression."""

    proposal_id: str
    target_kind: Literal[
        "decision_commitment",
        "action_selection_progression",
        "communication_release",
        "program_activation",
        "task_set_activation",
        "strategy_commitment",
        "completion_acceptance",
    ]
    gate_status: Literal["open", "open_with_conditions", "review_required", "hold", "block_proposed", "authority_required"]
    conditions: Tuple[str, ...] = field(default_factory=tuple)


# =============================================================================
# MAINTENANCE PROPOSAL
# =============================================================================


@dataclass(frozen=True)
class ExecutiveMaintenanceProposal:
    """Proposal to maintain a target's active relevance."""

    proposal_id: str
    target_kind: Literal[
        "goal_binding",
        "commitment_binding",
        "task_set_rule",
        "assumption",
        "hypothesis",
        "working_memory_reference",
        "focus_requirement",
        "monitoring_condition",
        "decision_criterion",
    ]
    persistence: str


# =============================================================================
# BIAS PROPOSAL
# =============================================================================


@dataclass(frozen=True)
class ExecutiveBiasProposal:
    """Proposal to express a relative preference toward a target."""

    proposal_id: str
    target_kind: Literal[
        "executive_program",
        "goal",
        "decision_criterion",
        "evidence_source",
        "strategy_review_path",
        "action_selection_constraint",
        "working_memory_item",
        "focus_candidate",
    ]
    preference_strength: str


# =============================================================================
# EXPORTS
# =============================================================================

__all__: Tuple[str, ...] = (
    "TopDownModulationProposal",
    "ExecutiveFacilitationProposal",
    "ExecutiveAttenuationProposal",
    "ExecutiveGatingProposal",
    "ExecutiveMaintenanceProposal",
    "ExecutiveBiasProposal",
)