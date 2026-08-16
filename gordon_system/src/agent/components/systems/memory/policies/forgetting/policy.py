# Memory Forgetting Policy - Phase 5.1.5 Canonical Implementation
# ================================================================
"""
Memory Forgetting Policy: Evaluate whether accessibility should decrease.

Purpose:
    Determine if an artifact's accessibility should be reduced over time.
    
Policies evaluate. They never execute.

Policy Contract:
    Operation Proposal (Artifact)
         ↓
    ForgettingPolicy.evaluate(proposal)
         ↓
    Decision (ALLOW, DENY, DEFER, ESCALATE)

Forgetting Laws:
    FORGETTING-LAW-001: Forgetting Policies evaluate accessibility reduction only
    FORGETTING-LAW-002: Forgetting Policies never execute directly
    FORGETTING-LAW-003: Forgetting recommendations preserve evidence
    FORGETTING-LAW-004: Forgetting Policies preserve provenance
    FORGETTING-LAW-005: Forgetting Policies expose urgency explicitly
    FORGETTING-LAW-006: Forgetting Policies remain explainable
    FORGETTING-LAW-007: Forgetting Policies remain observable
    FORGETTING-LAW-008: Forgetting Policies remain deterministic
"""

from __future__ import annotations

import time
import uuid

from typing import Dict, List, Tuple, Optional, Any

try:
    from gordon_system.src.agent.components.systems.memory.policies.decision import DecisionKind, MemoryDecision, MemoryDecisionBuilder
    from gordon_system.src.agent.components.systems.memory.policies.evidence import EvidenceKind, PolicyEvidence
    from gordon_system.src.agent.components.systems.memory.policies.policy import MemoryPolicy, PolicyKind
except ImportError:
    from decision import DecisionKind, MemoryDecision, MemoryDecisionBuilder
    from evidence import EvidenceKind, PolicyEvidence
    from policy import MemoryPolicy, PolicyKind


class ForgettingPolicy(MemoryPolicy):
    """
    Evaluate whether an artifact's accessibility should decrease.
    
    The forgetting policy examines:
        - Importance and utility of the artifact
        - Recency of access
        - Activation history patterns
        
    This policy never reduces accessibility directly; it only evaluates.
    """
    
    def __init__(
        self,
        policy_id: Optional[str] = None,
        name: str = "forgetting",
        min_importance_for_retention: float = 0.3,
        max_days_since_access: int = 30,
    ):
        """
        Initialize the forgetting policy.
        
        Args:
            policy_id: Unique ID for this policy instance
            name: Human-readable name
            min_importance_for_retention: Minimum importance to avoid reduction
            max_days_since_access: Maximum days since last access before reduction considered
        """
        super().__init__(
            policy_id=policy_id,
            name=name,
            kind_=PolicyKind.FORGETTING,
        )
        
        self.min_importance_for_retention: float = max(0.0, min(1.0, min_importance_for_retention))
        self.max_days_since_access: int = max_days_since_access
        
    def evaluate(
        self,
        proposal: Dict[str, Any],
        context: Optional[Dict[str, Any]] = None,
    ) -> MemoryDecision:
        """
        Evaluate whether accessibility should decrease.
        
        Args:
            proposal: The proposed action/transition to evaluate
                Required fields:
                    - target_type: Should be "memory_artifact"
                    - target_id: ID of the artifact
                Optional fields:
                    - artifact: The memory artifact (if available)
                    - current_state: Current lifecycle state
                    - importance: Artifact importance score
                    - days_since_access: Days since last access
                    - activation_history: Access patterns over time
            context: Additional context for evaluation
            
        Returns:
            MemoryDecision with recommendation
        """
        target_type = proposal.get("target_type", "memory_artifact")
        target_id = proposal.get("target_id", "unknown")
        
        artifact = proposal.get("artifact")
        current_state = proposal.get("current_state", "active")
        importance = proposal.get("importance", 0.5)
        days_since_access = proposal.get("days_since_access", 0)
        activation_history = proposal.get("activation_history", [])
        
        # Evaluate forgetting
        should_reduce_access, reason = self._should_reduce_access(
            artifact=artifact,
            current_state=current_state,
            importance=importance,
            days_since_access=days_since_access,
            activation_history=activation_history,
            context=context or {},
        )
        
        if should_reduce_access:
            confidence = 0.6 + ((1.0 - importance) * 0.4)  # Lower importance = higher confidence
            return MemoryDecisionBuilder(
                policy_id=self.policy_id,
                policy_kind="forgetting",
                kind_=DecisionKind.ALLOW,
                target_type=target_type,
                target_id=target_id,
            ).set_confidence(confidence).set_uncertainty(1.0 - confidence).add_evidence("artifact_qualifies").build()
        
        else:
            return MemoryDecisionBuilder(
                policy_id=self.policy_id,
                policy_kind="forgetting",
                kind_=DecisionKind.DENY,
                target_type=target_type,
                target_id=target_id,
            ).set_confidence(0.9).set_uncertainty(0.1).add_evidence("artifact_does_not_qualify").build()
    
    def _should_reduce_access(
        self,
        artifact: Optional[Any],
        current_state: str,
        importance: float,
        days_since_access: int,
        activation_history: List[Dict[str, Any]],
        context: Dict[str, Any],
    ) -> Tuple[bool, str]:
        """
        Determine if accessibility should be reduced.
        
        Returns:
            Tuple of (should_reduce_access, reason)
        """
        # Check current state
        if current_state in ("forgotten", "deleted"):
            return False, "Artifact already in forgotten or deleted state"
        
        # Check importance threshold
        if importance >= self.min_importance_for_retention:
            return False, f"Importance {importance} meets retention threshold"
        
        # Check days since access
        if days_since_access < self.max_days_since_access:
            return False, f"Days since access {days_since_access} below maximum {self.max_days_since_access}"
        
        # All checks passed - reduce accessibility
        return True, "Artifact meets forgetting criteria"


def create_forgetting_policy(
    policy_id: Optional[str] = None,
    name: str = "forgetting",
    min_importance_for_retention: float = 0.3,
    max_days_since_access: int = 30,
) -> ForgettingPolicy:
    """Create a forgetting policy instance."""
    return ForgettingPolicy(
        policy_id=policy_id,
        name=name,
        min_importance_for_retention=min_importance_for_retention,
        max_days_since_access=max_days_since_access,
    )


__all__ = [
    "ForgettingPolicy",
    "create_forgetting_policy",
]