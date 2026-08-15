# Executive Flexibility-Balance Assessment
# =========================================

"""
Canonical stability-flexibility balance assessment.

The Executive Network must maintain an appropriate balance between:
    - STABILITY: maintaining valid executive organization long enough to make progress
    - FLEXIBILITY: replacing invalid executive organization when evidence justifies change

This phase prevents two opposite failures:
    - EXECUTIVE INSTABILITY: repeated unnecessary switching, loss of continuity,
      abandoned commitments, fragmented cognition, unstable control.
    - EXECUTIVE RIGIDITY: preserving invalid goals, task sets, strategies, assumptions,
      responses, or Programs despite evidence that change is required.

Balance is assessed across multiple dimensions and must be interpretable,
not reduced to a single opaque scalar.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Tuple
from enum import Enum


class BalanceKind(Enum):
    """
    Type of stability-flexibility balance observed.
    """
    APPROPRIATE_STABILITY = "appropriate_stability"
    """Balance appropriately favors stability for current context."""
    
    APPROPRIATE_FLEXIBILITY = "appropriate_flexibility"
    """Balance appropriately favors flexibility for current context."""
    
    STABILITY_BIASED = "stability_biased"
    """Balance biased toward stability - potential for rigidity."""
    
    FLEXIBILITY_BIASED = "flexibility_biased"
    """Balance biased toward flexibility - potential for instability."""
    
    RIGID = "rigid"
    """Rigid state - no flexibility observed."""
    
    UNSTABLE = "unstable"
    """Unstable state - excessive flexibility detected."""
    
    CONFLICTED = "conflicted"
    """Conflicting signals - cannot determine balance."""
    
    CONTEXT_DEPENDENT = "context_dependent"
    """Balance is context-dependent and appropriate."""
    
    UNKNOWN = "unknown"
    """Balance type cannot be determined."""


@dataclass(frozen=True)
class StabilityFlexibilityBalance:
    """
    Assessment of stability-flexibility balance.
    
    The balance assessment considers multiple dimensions:
        - Progress toward goals
        - Conflict resolution rate
        - Error frequency and severity
        - Performance metrics
        - Switching history (frequency, reversals)
        - Current commitments
        - Uncertainty levels
        - Switching cost vs benefit
        - Reversibility of changes
        - Authority constraints
        - Overload status
        - Control effectiveness
    
    Do NOT reduce balance to one unexplained scalar.
    """
    
    # Identity and revisioning
    assessment_id: str = "balance_assessment_initial"
    """Unique identifier for this balance assessment."""
    
    revision: int = 0
    """Current revision number (strictly monotonic)."""
    
    schema_version: str = "1.0.0"
    """Schema version for compatibility tracking."""
    
    # Balance kind and status
    kind: BalanceKind = BalanceKind.UNKNOWN
    """Type of balance observed."""
    
    overall_status_class: str = "unknown"
    """Overall status classification (stable/appropriate/fragile/etc)."""
    
    # Dimension scores (0.0 to 1.0)
    stability_score: float = 0.5
    """Stability score across all dimensions."""
    
    flexibility_score: float = 0.5
    """Flexibility score across all dimensions."""
    
    adaptability_score: float = 0.5
    """Ability to adapt when needed."""
    
    continuity_score: float = 0.5
    """Continuity preservation score."""
    
    # Dimension-specific assessments
    program_continuity_class: str = "unknown"
    task_set_continuity_class: str = "unknown"
    goal_continuity_class: str = "unknown"
    commitment_continuity_class: str = "unknown"
    strategy_continuity_class: str = "unknown"
    
    # History metrics
    switch_count_recent_window: int = 0
    """Number of switches in recent assessment window."""
    
    reversal_count_recent_window: int = 0
    """Number of reversals in recent assessment window."""
    
    average_stabilization_seconds: float = 0.0
    """Average time to stabilize after a switch."""
    
    # Context metrics
    current_progress_class: str = "unknown"
    """Progress toward goals classification."""
    
    conflict_resolution_rate: float = 1.0
    """Rate of conflict resolution (0.0 to 1.0)."""
    
    error_rate: float = 0.0
    """Current error rate."""
    
    performance_score: float = 1.0
    """Overall performance score (0.0 to 1.0)."""
    
    # Authority and constraint satisfaction
    authority_constraints_satisfied: bool = True
    """Whether all authority constraints are satisfied."""
    
    policy_compliance_class: str = "unknown"
    security_compliance_class: str = "unknown"
    
    # Assessment details
    recommendations: Tuple[str, ...] = field(default_factory=tuple)
    """Recommendations for balance adjustment."""
    
    stability_risk_factors: Tuple[str, ...] = field(default_factory=tuple)
    """Identified stability risk factors."""
    
    flexibility_risk_factors: Tuple[str, ...] = field(default_factory=tuple)
    """Identified flexibility risk factors."""
    
    # Confidence and completeness
    confidence_class: str = "unknown"
    """Confidence classification of this assessment."""
    
    completeness_class: str = "waiting"
    """Completeness classification."""
    
    # Metadata
    privacy_classification: str = "internal"
    provenance_created_by: str = "balance_assessor"
    provenance_created_at_utc: float = 0.0


__all__ = [
    "BalanceKind",
    "StabilityFlexibilityBalance",
]