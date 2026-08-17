# Knowledge Belief System - Acceptance Module - Phase 6.6
# ==========================================================

"""
Acceptance module for belief state management.

This module handles the acceptance state of beliefs - whether a belief is currently
accepted as true, rejected, suspended, or in another epistemic condition.
"""

from __future__ import annotations

import uuid
import time
from typing import Dict, List, Tuple, Optional


class BeliefAcceptanceManager:
    """
    Manages the acceptance state of beliefs.
    
    Handles transitions between acceptance states (ACCEPTED, REJECTED, SUSPENDED,
    CONTESTED) while preserving history and provenance for each transition.
    """
    
    def __init__(self):
        """Initialize the acceptance manager."""
        self._acceptances: dict = {}  # belief_id -> current state
        self._history: list = []      # All state transitions
    
    @property
    def active_belief_count(self) -> int:
        """Get count of beliefs with known acceptance states."""
        return len(self._acceptances)
    
    def get_acceptance_state(self, belief_id: str) -> Optional[str]:
        """Get the current acceptance state for a belief."""
        return self._acceptances.get(belief_id)
    
    def accept_belief(
        self,
        belief_id: str,
        supporting_evidence: List[str] = None,
        justification: str = None,
    ) -> dict:
        """
        Accept a belief as true.
        
        Args:
            belief_id: ID of the belief to accept
            supporting_evidence: IDs of evidence supporting acceptance
            justification: Description of why this belief is accepted
            
        Returns:
            Acceptance record dictionary
        """
        state = "accepted"
        self._acceptances[belief_id] = state
        
        record = {
            "belief_id": belief_id,
            "state": state,
            "timestamp_utc": time.time(),
            "supporting_evidence": supporting_evidence or [],
            "justification": justification,
        }
        
        self._history.append(record)
        return record
    
    def reject_belief(
        self,
        belief_id: str,
        justification: str,
    ) -> dict:
        """
        Reject a belief as false.
        
        Args:
            belief_id: ID of the belief to reject
            justification: Reason for rejection
            
        Returns:
            Rejection record dictionary
        """
        state = "rejected"
        self._acceptances[belief_id] = state
        
        record = {
            "belief_id": belief_id,
            "state": state,
            "timestamp_utc": time.time(),
            "justification": justification,
        }
        
        self._history.append(record)
        return record
    
    def suspend_belief(
        self,
        belief_id: str,
        reason: str,
        expected_resolution: str = None,
    ) -> dict:
        """
        Suspend judgment on a belief without rejecting it.
        
        Args:
            belief_id: ID of the belief to suspend
            reason: Reason for suspension
            expected_resolution: When/why the suspension might end
            
        Returns:
            Suspension record dictionary
        """
        state = "suspended"
        self._acceptances[belief_id] = state
        
        record = {
            "belief_id": belief_id,
            "state": state,
            "timestamp_utc": time.time(),
            "reason": reason,
            "expected_resolution": expected_resolution,
        }
        
        self._history.append(record)
        return record
    
    def reopen_belief(
        self,
        belief_id: str,
        new_state: str = "accepted",
    ) -> dict:
        """
        Reopen a previously suspended belief.
        
        Args:
            belief_id: ID of the belief to reopen
            new_state: State to transition to (default: accepted)
            
        Returns:
            Reopening record dictionary
        """
        state = new_state
        self._acceptances[belief_id] = state
        
        record = {
            "belief_id": belief_id,
            "state": state,
            "timestamp_utc": time.time(),
            "previous_state": "suspended",
        }
        
        self._history.append(record)
        return record
    
    def get_history(self, belief_id: str = None) -> List[dict]:
        """
        Get acceptance history.
        
        Args:
            belief_id: If provided, only history for that belief
            
        Returns:
            List of state transition records
        """
        if belief_id is None:
            return list(self._history)
        return [
            h for h in self._history 
            if h.get("belief_id") == belief_id
        ]
    
    def clear_history(self):
        """Clear all history (for reset purposes)."""
        self._acceptances.clear()
        self._history.clear()


class AcceptanceDecisionEngine:
    """
    Engine for making acceptance decisions based on evidence.
    
    Evaluates whether a belief candidate should be accepted, rejected,
    or suspended based on available evidence and justification.
    """
    
    def __init__(
        self,
        minimum_evidence_threshold: int = 1,
        maximum_counter_ratio: float = 0.5,
    ):
        """Initialize the decision engine."""
        self._min_evidence = minimum_evidence_threshold
        self._max_counter_ratio = maximum_counter_ratio
    
    @property
    def min_evidence_threshold(self) -> int:
        """Get minimum evidence threshold for acceptance."""
        return self._min_evidence
    
    def make_decision(
        self,
        belief_id: str,
        supporting_evidence_count: int,
        counter_evidence_count: int,
        justification: str = None,
    ) -> Tuple[str, dict]:
        """
        Make an acceptance decision based on evidence analysis.
        
        Args:
            belief_id: ID of the belief being evaluated
            supporting_evidence_count: Number of supporting evidence items
            counter_evidence_count: Number of countering evidence items
            justification: Optional justification text
            
        Returns:
            Tuple of (decision, details)
        """
        total = supporting_evidence_count + counter_evidence_count
        
        # Rule 1: Must have minimum evidence to accept
        if supporting_evidence_count < self._min_evidence:
            return "suspended", {
                "reason": f"Insufficient supporting evidence: {supporting_evidence_count} < {self._min_evidence}",
            }
        
        # Rule 2: Counter-evidence ratio check
        counter_ratio = counter_evidence_count / total if total > 0 else 0
        
        if counter_ratio > self._max_counter_ratio:
            return "rejected", {
                "reason": f"Counter-evidence exceeds threshold: {counter_ratio:.2f} > {self._max_counter_ratio}",
                "supporting_count": supporting_evidence_count,
                "counter_count": counter_evidence_count,
            }
        
        # Rule 3: Default to accepted if evidence looks good
        return "accepted", {
            "reason": "Sufficient supporting evidence with acceptable counter-ratio",
            "supporting_count": supporting_evidence_count,
            "counter_count": counter_evidence_count,
            "counter_ratio": counter_ratio,
            "justification": justification,
        }
    
    def evaluate_state(
        self,
        belief_id: str,
        acceptance_manager: BeliefAcceptanceManager,
    ) -> Tuple[str, dict]:
        """
        Evaluate what the optimal state should be for a belief.
        
        Args:
            belief_id: ID of the belief
            acceptance_manager: Manager to query current state
            
        Returns:
            Tuple of (optimal_state, details)
        """
        current = acceptance_manager.get_acceptance_state(belief_id)
        
        # If already suspended or rejected, may need review
        if current in ("suspended", "rejected"):
            return "evaluating", {
                "current": current,
                "action": "review_for_reopening",
            }
        
        # Otherwise, current state is likely optimal
        return current or "unknown", {
            "status": "confirmed_current_state",
        }


class AcceptanceValidator:
    """
    Validates acceptance decisions for consistency and correctness.
    
    Ensures that acceptance state transitions follow valid patterns
    and preserve required metadata.
    """
    
    def __init__(self):
        """Initialize the validator."""
        self._violations: list = []
    
    @property
    def violation_count(self) -> int:
        """Get count of recorded violations."""
        return len(self._violations)
    
    def validate_acceptance_state(self, state: str) -> Tuple[bool, Optional[str]]:
        """
        Validate that a state string is valid.
        
        Args:
            state: The state to validate
            
        Returns:
            Tuple of (is_valid, error_message if invalid)
        """
        valid_states = {"accepted", "rejected", "suspended", "contested", "unknown"}
        
        if state not in valid_states:
            return False, f"Invalid acceptance state: {state}. Must be one of {valid_states}"
        
        return True, None
    
    def validate_acceptance_transition(
        self,
        current_state: str,
        new_state: str,
    ) -> Tuple[bool, Optional[str]]:
        """
        Validate that a state transition is allowed.
        
        Args:
            current_state: Current acceptance state
            new_state: Proposed new state
            
        Returns:
            Tuple of (is_valid, error_message if invalid)
        """
        # Basic valid transitions
        valid_transitions = {
            "accepted": {"rejected", "suspended"},
            "rejected": {"accepted", "suspended"},
            "suspended": {"accepted", "rejected", "unknown"},
            "contested": {"accepted", "rejected", "suspended"},
            "unknown": {"accepted", "rejected", "suspended", "contested"},
        }
        
        if current_state not in valid_transitions:
            return False, f"Unknown current state: {current_state}"
        
        if new_state not in valid_transitions.get(current_state, set()):
            return False, f"Invalid transition: {current_state} -> {new_state}"
        
        return True, None
    
    def record_violation(self, violation: str):
        """Record a validation violation."""
        self._violations.append({
            "violation": violation,
            "timestamp_utc": time.time(),
        })
    
    def clear_violations(self):
        """Clear all violations."""
        self._violations.clear()


__all__ = [
    "BeliefAcceptanceManager",
    "AcceptanceDecisionEngine",
    "AcceptanceValidator",
]