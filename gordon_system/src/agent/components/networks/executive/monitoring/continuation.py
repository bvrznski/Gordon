# Executive Conflict Monitoring Continuation Types
# ================================================

"""
Types for advisory continuation decisions after conflict monitoring.

Continuation specifies what should happen next - it is advisory and does not
perform any action itself.
"""

from __future__ import annotations

from typing import Tuple


class ExecutiveConflictMonitoringContinuation:
    """
    Advisory continuations after conflict monitoring activity.
    
    Continuation specifies what should happen next. It does not perform any
    action itself.
    """
    
    COMPLETE = "complete"
    
    CONTINUE_MONITORING = "continue_monitoring"
    REASSESS_CONFLICT = "reassess_conflict"
    
    REQUEST_CONTEXT_REFRESH = "request_context_refresh"
    REQUEST_EVIDENCE = "request_evidence"
    REQUEST_CLARIFICATION = "request_clarification"
    
    REQUEST_GOAL_REVIEW = "request_goal_review"
    REQUEST_COMMITMENT_REVIEW = "request_commitment_review"
    REQUEST_PRIORITY_REVIEW = "request_priority_review"
    
    REQUEST_TASK_SET_REVIEW = "request_task_set_review"
    REQUEST_PROGRAM_REVIEW = "request_program_review"
    REQUEST_STRATEGY_REVIEW = "request_strategy_review"
    
    REQUEST_DECISION = "request_decision"
    REQUEST_SWITCH_REVIEW = "request_switch_review"
    REQUEST_INHIBITION_REVIEW = "request_inhibition_review"
    
    REQUEST_MONITORING = "request_monitoring"
    REQUEST_RECOVERY = "request_recovery"
    
    REQUEST_POLICY_REVIEW = "request_policy_review"
    REQUEST_SECURITY_REVIEW = "request_security_review"
    REQUEST_AUTHORITY_REVIEW = "request_authority_review"
    
    REQUEST_CONTROL_ALLOCATION = "request_control_allocation"
    
    WAIT_FOR_RESULT = "wait_for_result"
    WAIT_FOR_AUTHORITY = "wait_for_authority"
    
    SUSPEND = "suspend"
    FAIL = "fail"
    CANCEL = "cancel"

    @classmethod
    def all_continuations(cls) -> Tuple[str, ...]:
        return tuple(v for k, v in vars(cls).items() if not k.startswith('_') and isinstance(v, str))


__all__: Tuple[str, ...] = ("ExecutiveConflictMonitoringContinuation",)