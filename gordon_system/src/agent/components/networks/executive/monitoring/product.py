# Executive Conflict Monitoring Product Types
# ===========================================

"""
Types for monitoring products generated during conflict assessment.

A monitoring product is an intermediate or final result of the monitoring
process. Products are not executed - they are produced.
"""

from __future__ import annotations

from typing import Tuple


class ExecutiveConflictMonitoringProduct:
    """
    Kinds of products that may be produced by conflict monitoring.
    
    Products are the outputs of monitoring steps, not executable work items.
    """
    
    EXECUTIVE_CONFLICT = "executive_conflict"
    CONFLICT_VALIDATION = "conflict_validation"
    CONFLICT_SEVERITY_ASSESSMENT = "conflict_severity_assessment"
    CONFLICT_PERSISTENCE_ASSESSMENT = "conflict_persistence_assessment"
    CONFLICT_RECURRENCE_ASSESSMENT = "conflict_recurrence_assessment"
    CONFLICT_PROPAGATION_ASSESSMENT = "conflict_propagation_assessment"
    
    INTERFERENCE_ASSESSMENT = "interference_assessment"
    AMBIGUITY_ASSESSMENT = "ambiguity_assessment"
    UNCERTAINTY_DEMAND = "uncertainty_demand"
    
    EVIDENCE_GAP = "evidence_gap"
    EXECUTIVE_GAP = "executive_gap"
    EXECUTIVE_TENSION = "executive_tension"
    
    EXECUTIVE_DEMAND_ASSESSMENT = "executive_demand_assessment"
    CONTROL_INSUFFICIENCY_ASSESSMENT = "control_insufficiency_assessment"
    CONTROL_SATURATION_ASSESSMENT = "control_saturation_assessment"
    EXECUTIVE_OVERLOAD_ASSESSMENT = "executive_overload_assessment"
    
    CONFLICT_DUPLICATE_REPORT = "conflict_duplicate_report"
    CONFLICT_AGGREGATE = "conflict_aggregate"
    CONFLICT_DECOMPOSITION = "conflict_decomposition"
    
    ESCALATION_ASSESSMENT = "escalation_assessment"
    MITIGATION_ASSESSMENT = "mitigation_assessment"
    DEMAND_RECOMMENDATION = "demand_recommendation"
    
    NO_MEANINGFUL_RESULT = "no_meaningful_result"

    @classmethod
    def all_kinds(cls) -> Tuple[str, ...]:
        return tuple(v for k, v in vars(cls).items() if not k.startswith('_') and isinstance(v, str))


__all__: Tuple[str, ...] = ("ExecutiveConflictMonitoringProduct",)