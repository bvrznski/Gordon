# Executive Demand Recommendation Types
# ======================================

"""
Types for demand recommendations.

The recommendation is advisory and must not mutate other systems or allocate
control directly.
"""

from __future__ import annotations

from typing import Tuple


class ExecutiveDemandRecommendation:
    """
    Advisory recommendations for executive demand responses.
    
    The recommendation is advisory - it must not allocate control, switch task
    sets, inhibit actions, schedule work, mutate other Networks, or suspend
    Execution directly.
    """
    
    MAINTAIN_CURRENT_CONTROL = "maintain_current_control"
    INTENSIFY_CONTROL = "intensify_control"
    REDUCE_CONTROL = "reduce_control"
    REDIRECT_CONTROL = "redirect_control"
    DISTRIBUTE_CONTROL = "distribute_control"
    REVIEW_TASK_SET = "review_task_set"
    REVIEW_PROGRAM = "review_program"
    REQUEST_CLARIFICATION = "request_clarification"
    REQUEST_EVIDENCE = "request_evidence"
    REQUEST_PLANNING = "request_planning"
    REQUEST_REASONING = "request_reasoning"
    REQUEST_SIMULATION = "request_simulation"
    REQUEST_DECISION = "request_decision"
    REQUEST_INHIBITION_REVIEW = "request_inhibition_review"
    REQUEST_SWITCH_REVIEW = "request_switch_review"
    REQUEST_MONITORING = "request_monitoring"
    REQUEST_RECOVERY = "request_recovery"
    REQUEST_POLICY_REVIEW = "request_policy_review"
    REQUEST_SECURITY_REVIEW = "request_security_review"
    REQUEST_AUTHORITY_REVIEW = "request_authority_review"
    SUSPEND_PROGRESSION = "suspend_progression"
    DEFER = "defer"
    NO_CHANGE = "no_change"

    @classmethod
    def all_recommendations(cls) -> Tuple[str, ...]:
        return tuple(v for k, v in vars(cls).items() if not k.startswith('_') and isinstance(v, str))


__all__: Tuple[str, ...] = ("ExecutiveDemandRecommendation",)