# Executive Conflict Monitoring Outcome Types
# ===========================================

"""
Types for monitoring outcomes generated after conflict assessment.

An outcome represents the final result of a monitoring request, not the
intermediate products.
"""

from __future__ import annotations

from typing import Tuple


class ExecutiveConflictMonitoringOutcome:
    """
    Kinds of outcomes that may result from conflict monitoring.
    
    Outcomes represent the final result of a monitoring cycle or request.
    """
    
    NO_CONFLICT_DETECTED = "no_conflict_detected"
    CONFLICT_CANDIDATE_DETECTED = "conflict_candidate_detected"
    CONFLICT_CONFIRMED = "conflict_confirmed"
    MULTIPLE_CONFLICTS_CONFIRMED = "multiple_conflicts_confirmed"
    CONFLICT_DISPUTED = "conflict_disputed"
    
    CONFLICT_RECURRED = "conflict_recurred"
    CONFLICT_ESCALATED = "conflict_escalated"
    CONFLICT_MITIGATED = "conflict_mitigated"
    CONFLICT_RESOLVED = "conflict_resolved"
    
    INTERFERENCE_IDENTIFIED = "interference_identified"
    AMBIGUITY_IDENTIFIED = "ambiguity_identified"
    UNCERTAINTY_DEMAND_IDENTIFIED = "uncertainty_demand_identified"
    EVIDENCE_GAP_IDENTIFIED = "evidence_gap_identified"
    EXECUTIVE_GAP_IDENTIFIED = "executive_gap_identified"
    EXECUTIVE_TENSION_IDENTIFIED = "executive_tension_identified"
    
    EXECUTIVE_DEMAND_ASSESSED = "executive_demand_assessed"
    CONTROL_INSUFFICIENCY_IDENTIFIED = "control_insufficiency_identified"
    CONTROL_SATURATION_IDENTIFIED = "control_saturation_identified"
    EXECUTIVE_OVERLOAD_IDENTIFIED = "executive_overload_identified"
    
    PARTIAL_PROGRESS = "partial_progress"
    
    WAITING_FOR_CONTEXT = "waiting_for_context"
    WAITING_FOR_EVIDENCE = "waiting_for_evidence"
    WAITING_FOR_AUTHORITY = "waiting_for_authority"
    
    INSUFFICIENT_EVIDENCE = "insufficient_evidence"
    NO_MEANINGFUL_RESULT = "no_meaningful_result"
    
    FAILED = "failed"
    CANCELLED = "cancelled"
    EXPIRED = "expired"

    @classmethod
    def all_outcomes(cls) -> Tuple[str, ...]:
        return tuple(v for k, v in vars(cls).items() if not k.startswith('_') and isinstance(v, str))


__all__: Tuple[str, ...] = ("ExecutiveConflictMonitoringOutcome",)