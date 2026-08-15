# Executive Conflict Monitoring Plan Types
# ========================================

"""
Types for declarative conflict monitoring plans.

A plan is a sequence of steps that defines how to execute the monitoring
activity. The plan itself does not perform any work - execution belongs
to Phase 4.4.6.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Tuple


@dataclass(frozen=True)
class ExecutiveConflictMonitoringStepKind:
    """
    Kinds of steps in a conflict monitoring plan.
    
    Not every request requires every step - plans are selective.
    """
    
    VALIDATE_CONTEXT = "validate_context"
    VALIDATE_PROGRAMS = "validate_programs"
    VALIDATE_TASK_SETS = "validate_task_sets"
    VALIDATE_GOALS = "validate_goals"
    VALIDATE_COMMITMENTS = "validate_commitments"
    VALIDATE_CONSTRAINTS = "validate_constraints"
    VALIDATE_DECISIONS = "validate_decisions"
    VALIDATE_ACTION_CANDIDATES = "validate_action_candidates"
    
    NORMALIZE_OWNERSHIP = "normalize_ownership"
    NORMALIZE_AUTHORITY = "normalize_authority"
    NORMALIZE_REVISIONS = "normalize_revisions"
    NORMALIZE_FACTUALITY = "normalize_factuality"
    
    IDENTIFY_CONFLICT_CANDIDATES = "identify_conflict_candidates"
    CLASSIFY_CONFLICT = "classify_conflict"
    CLASSIFY_DIMENSIONS = "classify_dimensions"
    
    VALIDATE_EVIDENCE = "validate_evidence"
    
    DETECT_DUPLICATES = "detect_duplicates"
    CORRELATE_PRIOR_CONFLICTS = "correlate_prior_conflicts"
    
    ASSESS_SEVERITY = "assess_severity"
    ASSESS_PERSISTENCE = "assess_persistence"
    ASSESS_RECURRENCE = "assess_recurrence"
    ASSESS_PROPAGATION = "assess_propagation"
    
    ASSESS_INTERFERENCE = "assess_interference"
    ASSESS_AMBIGUITY = "assess_ambiguity"
    ASSESS_UNCERTAINTY = "assess_uncertainty"
    ASSESS_EVIDENCE_GAPS = "assess_evidence_gaps"
    
    ASSESS_EXECUTIVE_GAPS = "assess_executive_gaps"
    ASSESS_EXECUTIVE_TENSION = "assess_executive_tension"
    
    ASSESS_DECISION_DEMAND = "assess_decision_demand"
    ASSESS_SWITCHING_DEMAND = "assess_switching_demand"
    ASSESS_INHIBITION_DEMAND = "assess_inhibition_demand"
    ASSESS_MONITORING_DEMAND = "assess_monitoring_demand"
    ASSESS_RECOVERY_DEMAND = "assess_recovery_demand"
    ASSESS_EFFORT_DEMAND = "assess_effort_demand"
    
    ASSESS_CONTROL_INSUFFICIENCY = "assess_control_insufficiency"
    ASSESS_CONTROL_SATURATION = "assess_control_saturation"
    ASSESS_EXECUTIVE_OVERLOAD = "assess_executive_overload"
    
    COMPOSE_DEMAND = "compose_demand"
    IDENTIFY_TARGETS = "identify_targets"
    IDENTIFY_AUTHORITY = "identify_authority"
    
    ASSESS_ESCALATION = "assess_escalation"
    ASSESS_MITIGATION = "assess_mitigation"
    
    PREPARE_RECOMMENDATION = "prepare_recommendation"
    COMPOSE_OUTCOME = "compose_outcome"


@dataclass(frozen=True)
class ExecutiveConflictMonitoringPlan:
    """
    Declarative plan for conflict monitoring activity.
    
    A plan defines the steps to execute, but does not perform any work by
    itself. Execution belongs to Phase 4.4.6.
    """
    
    plan_id: str = ""
    priority: int = 0
    
    # Step kinds in execution order
    step_kinds: Tuple[str, ...] = ()
    
    # Scope for this plan
    scope: ExecutiveConflictMonitoringScope = None  # type: ignore


__all__: Tuple[str, ...] = (
    "ExecutiveConflictMonitoringStepKind",
    "ExecutiveConflictMonitoringPlan",
)