# Memory Retention Policy - Phase 5.1.5 Canonical Implementation
# ================================================================
"""
Memory Retention Policy: Evaluate whether an artifact should be retained long-term.

Purpose:
    Determine if a memory artifact should remain in active or archived storage.
    
Policies evaluate. They never execute.

Policy Contract:
    Operation Proposal (Artifact)
         ↓
    RetentionPolicy.evaluate(proposal)
         ↓
    Decision (ALLOW, DENY, DEFER, ESCALATE)

Retention Laws:
    RETENTION-LAW-001: Retention Policies evaluate preservation
    RETENTION-LAW-002: Retention Policies preserve Memory identity
    RETENTION-LAW-003: Retention Policies preserve provenance
    RETENTION-LAW-004: Retention Policies preserve revision history
    RETENTION-LAW-005: Retention recommendations remain explicit
    RETENTION-LAW-006: Retention Policies never archive directly
    RETENTION-LAW-007: Retention Policies remain observable
    RETENTION-LAW-008: Retention Policies remain deterministic
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


class RetentionPolicy(MemoryPolicy):
    """
    Evaluate whether a memory artifact should be retained long-term.
    
    The retention policy examines:
        - Artifact importance and utility
        - Access frequency and recency
        - Identity relevance to active goals
        - Historical value
        
    This policy never archives artifacts; it only evaluates retention needs.
    """
    
    def __init__(
        self,
        policy_id: Optional[str] = None,
        name: str = "retention",
        min_importance: float = 0.3,  # Minimum importance for retention
        min_access_frequency: float = 0.1,  # Minimum access rate (per day)
    ):
        """
        Initialize the retention policy.
        
        Args:
            policy_id: Unique ID for this policy instance
            name: Human-readable name
            min_importance: Minimum importance threshold for retention
            min_access_frequency: Minimum access rate (per day) to consider active
        """
        super().__init__(
            policy_id=policy_id,
            name=name,
            kind_=PolicyKind.RETENTION,
        )
        
        self.min_importance: float = max(0.0, min(1.0, min_importance))
        self.min_access_frequency: float = max(0.0, min(1.0, min_access_frequency))
        
    def evaluate(
        self,
        proposal: Dict[str, Any],
        context: Optional[Dict[str, Any]] = None,
    ) -> MemoryDecision:
        """
        Evaluate whether an artifact should be retained.
        
        Args:
            proposal: The proposed action/transition to evaluate
                Required fields:
                    - target_type: Should be "memory_artifact"
                    - target_id: ID of the artifact
                Optional fields:
                    - artifact: The memory artifact (if available)
                    - current_state: Current lifecycle state
                    - importance: Artifact importance score
                    - access_frequency: Recent access rate
                    - last_access_utc: When was it last accessed?
            context: Additional context for evaluation
                Workspace demand, active goals, attention state
            
        Returns:
            MemoryDecision with recommendation
        """
        target_type = proposal.get("target_type", "memory_artifact")
        target_id = proposal.get("target_id", "unknown")
        
        artifact = proposal.get("artifact")
        current_state = proposal.get("current_state", "active")
        importance = proposal.get("importance", 0.5)
        access_frequency = proposal.get("access_frequency", 0.0)
        last_access_utc = proposal.get("last_access_utc", time.time() - 86400)  # Default: 1 day ago
        
        # Evaluate retention
        should_retain, reason = self._should_retain(
            artifact=artifact,
            current_state=current_state,
            importance=importance,
            access_frequency=access_frequency,
            last_access_utc=last_access_utc,
            context=context or {},
        )
        
        if should_retain:
            confidence = 0.7 + (importance * 0.3)  # Base confidence + importance boost
            return MemoryDecisionBuilder(
                policy_id=self.policy_id,
                policy_kind="retention",
                kind_=DecisionKind.ALLOW,
                target_type=target_type,
                target_id=target_id,
            ).set_confidence(confidence).set_uncertainty(1.0 - confidence).add_evidence("artifact_qualifies").add_rule("importance_threshold").build()
        
        else:
            return MemoryDecisionBuilder(
                policy_id=self.policy_id,
                policy_kind="retention",
                kind_=DecisionKind.DENY,
                target_type=target_type,
                target_id=target_id,
            ).set_confidence(0.9).set_uncertainty(0.1).add_evidence("artifact_does_not_qualify").build()
    
    def _should_retain(
        self,
        artifact: Optional[Any],
        current_state: str,
        importance: float,
        access_frequency: float,
        last_access_utc: float,
        context: Dict[str, Any],
    ) -> Tuple[bool, str]:
        """
        Determine if an artifact should be retained.
        
        Returns:
            Tuple of (should_retain, reason)
        """
        # Check current state
        if current_state == "archived":
            return False, "Artifact is already archived"
        
        # Check importance threshold
        if importance < self.min_importance:
            return False, f"Importance {importance} below minimum {self.min_importance}"
        
        # Check access frequency (if recent)
        now = time.time()
        days_since_access = (now - last_access_utc) / 86400
        
        if days_since_access > 7:  # If not accessed in 7 days
            if access_frequency < self.min_access_frequency:
                return False, f"Access frequency {access_frequency} too low"
        
        # All checks passed
        return True, "Artifact meets retention criteria"


def create_retention_policy(
    policy_id: Optional[str] = None,
    name: str = "retention",
    min_importance: float = 0.3,
    min_access_frequency: float = 0.1,
) -> RetentionPolicy:
    """Create a retention policy instance."""
    return RetentionPolicy(
        policy_id=policy_id,
        name=name,
        min_importance=min_importance,
        min_access_frequency=min_access_frequency,
    )


__all__ = [
    "RetentionPolicy",
    "create_retention_policy",
]