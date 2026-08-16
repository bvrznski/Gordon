# Memory Activation Policy - Phase 5.1.5 Canonical Implementation
# ================================================================
"""
Memory Activation Policy: Determine whether an artifact should become active.

Purpose:
    Evaluate if a memory artifact should be activated for current cognition.
    
Policies evaluate. They never execute.

Policy Contract:
    Operation Proposal (Artifact)
         ↓
    ActivationPolicy.evaluate(proposal)
         ↓
    Decision (ALLOW, DENY, DEFER, ESCALATE)

Activation Laws:
    ACTIVATION-LAW-001: Activation Policies evaluate activation only
    ACTIVATION-LAW-002: Activation Policies never activate Memory directly
    ACTIVATION-LAW-003: Activation recommendations preserve evidence
    ACTIVATION-LAW-004: Activation Policies preserve provenance
    ACTIVATION-LAW-005: Activation Policies expose priorities explicitly
    ACTIVATION-LAW-006: Activation Policies remain explainable
    ACTIVATION-LAW-007: Activation Policies remain observable
    ACTIVATION-LAW-008: Activation Policies remain deterministic
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


class ActivationPolicy(MemoryPolicy):
    """
    Evaluate whether an existing memory artifact should become active.
    
    The activation policy examines:
        - Current context and workspace demand
        - Artifact importance signals
        - Priority metrics
        - Recent access history
        
    This policy never activates artifacts; it only recommends activation.
    """
    
    def __init__(
        self,
        policy_id: Optional[str] = None,
        name: str = "activation",
        min_importance: float = 0.3,  # Minimum importance threshold
    ):
        """
        Initialize the activation policy.
        
        Args:
            policy_id: Unique ID for this policy instance
            name: Human-readable name
            min_importance: Minimum importance for activation consideration
        """
        super().__init__(
            policy_id=policy_id,
            name=name,
            kind_=PolicyKind.ACTIVATION,
        )
        
        self.min_importance: float = max(0.0, min(1.0, min_importance))
        
    def evaluate(
        self,
        proposal: Dict[str, Any],
        context: Optional[Dict[str, Any]] = None,
    ) -> MemoryDecision:
        """
        Evaluate whether an artifact should become active.
        
        Args:
            proposal: The proposed action/transition to evaluate
                Required fields:
                    - target_type: Should be "memory_artifact"
                    - target_id: ID of the artifact
                Optional fields:
                    - artifact: The memory artifact (if available)
                    - current_state: Current lifecycle state
                    - priority: Artifact priority value
                    - importance: Importance signal from context
            context: Additional context for evaluation
                Workspace demand, active goals, attention state
            
        Returns:
            MemoryDecision with recommendation and priority info
        """
        target_type = proposal.get("target_type", "memory_artifact")
        target_id = proposal.get("target_id", "unknown")
        
        artifact = proposal.get("artifact")
        current_state = proposal.get("current_state", "dormant")
        priority = proposal.get("priority", 0.5)
        importance_signal = proposal.get("importance")
        
        # Build evidence
        evidence_refs: List[str] = []
        
        # Evaluate activation candidate
        should_activate, reason = self._should_activate(
            artifact=artifact,
            current_state=current_state,
            priority=priority,
            importance_signal=importance_signal,
            context=context or {},
        )
        
        if should_activate:
            confidence = 0.8 + (priority * 0.2)  # Base confidence + priority boost
            return MemoryDecisionBuilder(
                policy_id=self.policy_id,
                policy_kind="activation",
                kind_=DecisionKind.ALLOW,
                target_type=target_type,
                target_id=target_id,
            ).set_confidence(confidence).set_uncertainty(1.0 - confidence).add_evidence("artifact_qualified").add_rule("priority_threshold").build()
        
        else:
            return MemoryDecisionBuilder(
                policy_id=self.policy_id,
                policy_kind="activation",
                kind_=DecisionKind.DENY,
                target_type=target_type,
                target_id=target_id,
            ).set_confidence(0.9).set_uncertainty(0.1).add_evidence("artifact_not_qualified").build()
    
    def _should_activate(
        self,
        artifact: Optional[Any],
        current_state: str,
        priority: float,
        importance_signal: Optional[float],
        context: Dict[str, Any],
    ) -> Tuple[bool, str]:
        """
        Determine if an artifact should be activated.
        
        Returns:
            Tuple of (should_activate, reason)
        """
        # Check if already active
        if current_state == "active":
            return False, "Artifact is already active"
        
        # Check priority threshold
        if priority < 0.3:  # Minimum priority for consideration
            return False, f"Priority {priority} below threshold"
        
        # Check importance signal (if provided)
        if importance_signal is not None:
            if importance_signal < self.min_importance:
                return False, f"Importance {importance_signal} below minimum {self.min_importance}"
        
        # All checks passed
        return True, "Artifact meets activation criteria"


def create_activation_policy(
    policy_id: Optional[str] = None,
    name: str = "activation",
    min_importance: float = 0.3,
) -> ActivationPolicy:
    """Create an activation policy instance."""
    return ActivationPolicy(
        policy_id=policy_id,
        name=name,
        min_importance=min_importance,
    )


__all__ = [
    "ActivationPolicy",
    "create_activation_policy",
]