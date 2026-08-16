# Executive Demand Assessment Types
# ==================================

"""
Types for assessing executive demand.

Executive Demand is a structured assessment of the amount, persistence,
specificity, and type of control that may be required.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Tuple


@dataclass(frozen=True)
class ExecutiveDemandAssessmentId:
    """
    Unique identifier for an executive demand assessment.
    """
    
    value: str


@dataclass(frozen=True)
class ExecutiveDemandLevel:
    """
    Demand levels for executive assessments.
    """
    
    NONE = "none"
    MINIMAL = "minimal"
    LOW = "low"
    MODERATE = "moderate"
    ELEVATED = "elevated"
    HIGH = "high"
    SEVERE = "severe"
    CRITICAL = "critical"
    SATURATED = "saturated"
    UNKNOWN = "unknown"


@dataclass(frozen=True)
class ExecutiveDemandAssessment:
    """
    Structured assessment of executive demand.
    
    Do not reduce executive demand to one unexplained scalar.
    """
    
    assessment_id: ExecutiveDemandAssessmentId
    subject: str  # Subject being assessed
    
    level_class: str = "none"
    profile_kind: str = "unknown"
    
    # Demand components (contributions)
    conflict_demand_contrib: float = 0.0
    uncertainty_demand_contrib: float = 0.0
    evidence_gap_demand_contrib: float = 0.0
    decision_demand_contrib: float = 0.0
    switching_demand_contrib: float = 0.0
    inhibition_demand_contrib: float = 0.0
    monitoring_demand_contrib: float = 0.0
    recovery_demand_contrib: float = 0.0
    effort_demand_contrib: float = 0.0
    
    # Control assessment
    control_insufficiency_class: str = "unknown"
    control_saturation_class: str = "unknown"
    overload_class: str = "unknown"
    
    # Targets and evidence
    targets: Tuple[str, ...] = ()
    supporting_evidence: Tuple[str, ...] = ()
    opposing_evidence: Tuple[str, ...] = ()
    
    # Metrics
    urgency_class: str = "none"
    persistence_class: str = "transient"
    confidence_class: str = "unknown"
    completeness_class: str = "unknown"


__all__: Tuple[str, ...] = (
    "ExecutiveDemandAssessmentId",
    "ExecutiveDemandLevel",
    "ExecutiveDemandAssessment",
)