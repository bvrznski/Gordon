# Gordon Cognitive Architecture - Phase 4.11.7
# ===========================================
"""
Completion Policy Models
========================

Policies for determining cycle completion.
"""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(frozen=True, slots=True)
class CompletionPolicySpec:
    """
    Immutable completion policy specification.
    
    COMPLETION-LAW-001: Completion policy shall remain explicit
    COMPLETION-LAW-002: Cycle completion shall satisfy completion policy requirements
    
    Suggested policies per spec:
        ALL_REQUIRED_COMPLETE - all mandatory participants must complete
        MAJORITY_COMPLETE - majority participation sufficient
        GOAL_SATISFIED - stop when goal is achieved
        FIRST_VALID_RESULT - accept first valid result
        TIME_LIMIT - terminate after time budget exhausted
        MANUAL_TERMINATION - external control required
    """
    
    policy_type: str = ""
    """Type of completion policy."""
    
    mandatory_participants_complete: bool = True
    """Whether all mandatory participants must complete."""
    
    majority_threshold: float = 0.5
    """Threshold for majority completion (0.5 to 1.0)."""
    
    timeout_semantic_time: float = 0.0
    """Timeout in semantic time units."""
    
    early_termination_allowed: bool = False
    """Whether early termination is allowed."""
    
    manual_termination_required: bool = False
    """Whether external control required for termination."""
    
    provenance_ref: str = ""
    """Reference to provenance record."""
    
    @classmethod
    def all_required_complete(cls) -> CompletionPolicySpec:
        """Create an all-required-complete policy."""
        return cls(
            policy_type="all_required_complete",
            mandatory_participants_complete=True,
        )
    
    @classmethod
    def majority_complete(cls, threshold: float = 0.5) -> CompletionPolicySpec:
        """Create a majority-complete policy."""
        return cls(
            policy_type="majority_complete",
            mandatory_participants_complete=False,
            majority_threshold=threshold,
        )
    
    @classmethod
    def goal_satisfied(cls) -> CompletionPolicySpec:
        """Create a goal-satisfied policy."""
        return cls(
            policy_type="goal_satisfied",
            early_termination_allowed=True,
        )
    
    @classmethod
    def first_valid_result(cls) -> CompletionPolicySpec:
        """Create a first-valid-result policy."""
        return cls(
            policy_type="first_valid_result",
            early_termination_allowed=True,
        )
    
    @classmethod
    def time_limit(cls, timeout: float = 0.0) -> CompletionPolicySpec:
        """Create a time-limit policy."""
        return cls(
            policy_type="time_limit",
            timeout_semantic_time=timeout,
        )
    
    @classmethod
    def manual_termination(cls) -> CompletionPolicySpec:
        """Create a manual-termination policy."""
        return cls(
            policy_type="manual_termination",
            manual_termination_required=True,
        )
    
    def is_all_required_complete(self) -> bool:
        return self.policy_type == "all_required_complete"
    
    def is_majority_complete(self) -> bool:
        return self.policy_type == "majority_complete"
    
    def is_goal_satisfied(self) -> bool:
        return self.policy_type == "goal_satisfied"
    
    def is_first_valid_result(self) -> bool:
        return self.policy_type == "first_valid_result"
    
    def is_time_limit(self) -> bool:
        return self.policy_type == "time_limit"
    
    def is_manual_termination(self) -> bool:
        return self.policy_type == "manual_termination"
    
    def __str__(self) -> str:
        return f"CompletionPolicy({self.policy_type})"