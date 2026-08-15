# Executive Flexibility Assessment Contracts
# ============================================

"""
Canonical immutable dataclasses for flexibility, stability, rigidity,
and instability assessments.

These represent Phase 4.4.8 semantic architecture for assessing
whether the current executive organization should persist, stabilize,
relax, suspend, resume, switch, or be reconfigured.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Tuple, Optional
from enum import Enum

# Import status types
from gordon_system.src.agent.networks.executive.flexibility.status import (
    FlexibilityStatus,
    StabilityStatus,
    RigidityStatus,
    InstabilityStatus,
)


# =============================================================================
# BASE ASSESSMENT TYPE
# =============================================================================


@dataclass(frozen=True)
class ExecutiveFlexibilityAssessment:
    """
    Assessment of executive flexibility capacity.
    
    Canonical definition:
        Cognitive Flexibility is the bounded executive capacity to revise,
        suspend, replace, restore, or reconfigure an active executive
        organization when supplied evidence indicates that the current
        organization is no longer the most appropriate admissible configuration.
    
    This assessment reports on whether flexibility exists and is adequate.
    """
    
    # Identity and revisioning
    assessment_id: str = "flexibility_assessment_initial"
    """Unique identifier for this assessment."""
    
    revision: int = 0
    """Current revision number (strictly monotonic)."""
    
    schema_version: str = "1.0.0"
    """Schema version for compatibility tracking."""
    
    # Assessment values
    flexibility_status: FlexibilityStatus = FlexibilityStatus.ADEQUATE
    """Current flexibility status."""
    
    capacity: float = 1.0
    """Flexibility capacity (0.0 to 1.0)."""
    
    evidence_count: int = 0
    """Number of pieces of evidence considered."""
    
    # Context
    active_program_id: str = "exec_program_initial"
    """Current active program being assessed."""
    
    active_task_set_id: Optional[str] = None
    """Current active task set (if any)."""
    
    current_strategy_id: Optional[str] = None
    """Current strategy reference (if any)."""
    
    # Assessment details
    adaptive_changes_made: int = 0
    """Number of adaptive changes made recently."""
    
    maladaptive_persistence_detected: bool = False
    """Whether persistence without adaptation was detected."""
    
    rapid_reconfiguration_detected: bool = False
    """ Whether rapid reconfigurations were detected (potential instability)."""
    
    # Confidence and completeness
    confidence_class: str = "unknown"
    """Classification of assessment confidence."""
    
    completeness_class: str = "waiting"
    """Classification of assessment completeness."""
    
    # Metadata
    privacy_classification: str = "internal"
    """Privacy classification of this assessment."""
    
    provenance_created_by: str = "flexibility_assessor"
    """Who/what created this assessment."""
    
    provenance_created_at_utc: float = 0.0


@dataclass(frozen=True)
class ExecutiveStabilityAssessment:
    """
    Assessment of executive stability.
    
    Canonical definition:
        Executive Stability is the bounded capacity to maintain a valid
        executive organization despite transient noise, temporary uncertainty,
        weak competing signals, and non-material fluctuations.
    
    Stability is NOT rigidity - rigidity preserves INVALID organization.
    """
    
    assessment_id: str = "stability_assessment_initial"
    """Unique identifier for this assessment."""
    
    revision: int = 0
    """Current revision number."""
    
    schema_version: str = "1.0.0"
    """Schema version."""
    
    stability_status: StabilityStatus = StabilityStatus.ADEQUATE
    """Current stability status."""
    
    organization_validity_class: str = "unknown"
    """Validity classification of current executive organization."""
    
    resistance_to_noise: float = 0.5
    """How well the organization resists noise (0.0 to 1.0)."""
    
    transient_fluctuations_count: int = 0
    """Count of transient fluctuations detected."""
    
    # Evidence for stability
    valid_continuity_patterns: Tuple[str, ...] = field(default_factory=tuple)
    """IDs of valid continuity patterns."""
    
    adaptive_capacity_remaining: float = 1.0
    """Remaining adaptive capacity."""
    
    # Assessment details
    continuity_maintained: bool = True
    """Whether continuity was maintained."""
    
    organization_preserved: bool = True
    """Whether current organization was preserved."""
    
    # Confidence and completeness
    confidence_class: str = "unknown"
    """Assessment confidence classification."""
    
    completeness_class: str = "waiting"
    """Assessment completeness classification."""
    
    # Metadata
    privacy_classification: str = "internal"
    provenance_created_by: str = "stability_assessor"
    provenance_created_at_utc: float = 0.0


@dataclass(frozen=True)
class ExecutiveRigidityAssessment:
    """
    Assessment of executive rigidity.
    
    Canonical definition:
        Executive Rigidity is the maladaptive inability or refusal to revise
        an executive configuration despite sufficient evidence, authority,
        and opportunity for justified reconfiguration.
    
    Rigidity is NOT stability - it preserves INVALID organization.
    """
    
    assessment_id: str = "rigidity_assessment_initial"
    """Unique identifier."""
    
    revision: int = 0
    """Revision number."""
    
    schema_version: str = "1.0.0"
    """Schema version."""
    
    rigidity_status: RigidityStatus = RigidityStatus.FLEXIBLE
    """Current rigidity status."""
    
    # Evidence of rigidity
    valid_switches_rejected_count: int = 0
    """Number of valid switches that were rejected without sufficient reason."""
    
    invalid_configuration_maintained: bool = False
    """Whether an invalid configuration is maintained."""
    
    ineffective_strategy_maintained: bool = False
    """Whether an ineffective strategy is maintained."""
    
    authority_decision_ignored: bool = False
    """Whether authority decisions have been ignored."""
    
    excessive_cost_weighting: bool = False
    """Whether excessive switch cost is being used to justify maintaining status quo."""
    
    # Context
    current_configuration_validity_class: str = "unknown"
    """Validity classification of current configuration."""
    
    available_alternatives_count: int = 0
    """Number of valid alternatives available."""
    
    # Assessment details
    responsiveness_to_evidence: float = 1.0
    """How responsive the organization is to evidence (0.0 to 1.0)."""
    
    restoration_path_available: bool = True
    """Whether prior state can be restored."""
    
    # Confidence and completeness
    confidence_class: str = "unknown"
    provenance_created_by: str = "rigidity_assessor"
    provenance_created_at_utc: float = 0.0


@dataclass(frozen=True)
class ExecutiveInstabilityAssessment:
    """
    Assessment of executive instability.
    
    Canonical definition:
        Executive Instability is excessive or poorly justified reconfiguration
        of the executive organization.
    """
    
    assessment_id: str = "instability_assessment_initial"
    """Unique identifier."""
    
    revision: int = 0
    """Revision number."""
    
    schema_version: str = "1.0.0"
    """Schema version."""
    
    instability_status: InstabilityStatus = InstabilityStatus.STABLE
    """Current instability status."""
    
    # Evidence of instability
    excessive_switching_detected: bool = False
    """Whether excessive switching was detected."""
    
    rapid_reversals_count: int = 0
    """Number of rapid reversals detected."""
    
    unresolved_program_churn: bool = False
    """Whether programs are being churned without resolution."""
    
    repeated_task_set_replacement: bool = False
    """Whether task sets are repeatedly replaced."""
    
    insufficient_continuity: bool = False
    """Whether continuity is insufficient."""
    
    # Context
    average_stabilization_period_seconds: float = 0.0
    """Average time between switches and stabilization."""
    
    switch_count_last_window: int = 0
    """Number of switches in recent window."""
    
    # Assessment details
    organization_coherence_class: str = "unknown"
    """Coherence classification of current organization."""
    
    control_allocation_stability: float = 1.0
    """Stability of control allocation (0.0 to 1.0)."""
    
    # Confidence and completeness
    confidence_class: str = "unknown"
    provenance_created_by: str = "instability_assessor"
    provenance_created_at_utc: float = 0.0


__all__ = [
    "ExecutiveFlexibilityAssessment",
    "ExecutiveStabilityAssessment",
    "ExecutiveRigidityAssessment",
    "ExecutiveInstabilityAssessment",
]