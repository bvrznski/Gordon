# Memory Archival Policy - Phase 5.1.5 Canonical Implementation
# ===============================================================
"""
Memory Archival Policy: Determine whether an artifact should be archived.

Purpose:
    Evaluate if a memory artifact should be moved from active to archive storage.
    
Policies evaluate. They never execute.

Policy Contract:
    Operation Proposal (Artifact)
         ↓
    ArchivalPolicy.evaluate(proposal)
         ↓
    Decision (ALLOW, DENY, DEFER, ESCALATE)

Archival Laws:
    ARCHIVAL-LAW-001: Archival Policies evaluate archival only
    ARCHIVAL-LAW-002: Archival Policies never archive directly
    ARCHIVAL-LAW-003: Archival recommendations preserve evidence
    ARCHIVAL-LAW-004: Archival Policies preserve provenance
    ARCHIVAL-LAW-005: Archival Policies expose urgency explicitly
    ARCHIVAL-LAW-006: Archival Policies remain explainable
    ARCHIVAL-LAW-007: Archival Policies remain observable
    ARCHIVAL-LAW-008: Archival Policies remain deterministic
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


class ArchivalPolicy(MemoryPolicy):
    """
    Evaluate whether a memory artifact should be archived.
    
    The archival policy examines:
        - Current retention status
        - Historical value assessment
        - Usage patterns and relationships
        - Storage cost considerations
        
    This policy never archives artifacts; it only recommends archival.
    """
    
    def __init__(
        self,
        policy_id: Optional[str] = None,
        name: str = "archival",
        min_retention_days: int = 30,  # Minimum days before archival consideration
        max_usage_threshold: float = 0.1,  # Max usage rate to consider archiving
    ):
        """
        Initialize the archival policy.
        
        Args:
            policy_id: Unique ID for this policy instance
            name: Human-readable name
            min_retention_days: Minimum days in active storage before considering archival
            max_usage_threshold: Maximum usage rate to consider archiving
        """
        super().__init__(
            policy_id=policy_id,
            name=name,
            kind_=PolicyKind.ARCHIVAL,
        )
        
        self.min_retention_days: int = min_retention_days
        self.max_usage_threshold: float = max(0.0, min(1.0, max_usage_threshold))
        
    def evaluate(
        self,
        proposal: Dict[str, Any],
        context: Optional[Dict[str, Any]] = None,
    ) -> MemoryDecision:
        """
        Evaluate whether an artifact should be archived.
        
        Args:
            proposal: The proposed action/transition to evaluate
                Required fields:
                    - target_type: Should be "memory_artifact"
                    - target_id: ID of the artifact
                Optional fields:
                    - artifact: The memory artifact (if available)
                    - current_state: Current lifecycle state
                    - retention_days: Days in active storage
                    - usage_rate: Recent usage rate
            context: Additional context for evaluation
            
        Returns:
            MemoryDecision with recommendation
        """
        target_type = proposal.get("target_type", "memory_artifact")
        target_id = proposal.get("target_id", "unknown")
        
        artifact = proposal.get("artifact")
        current_state = proposal.get("current_state", "active")
        retention_days = proposal.get("retention_days", 0)
        usage_rate = proposal.get("usage_rate", 1.0)
        
        # Evaluate archival candidate
        should_archive, reason = self._should_archive(
            artifact=artifact,
            current_state=current_state,
            retention_days=retention_days,
            usage_rate=usage_rate,
            context=context or {},
        )
        
        if should_archive:
            confidence = 0.8 - (usage_rate * 0.3)  # Higher confidence when usage is low
            return MemoryDecisionBuilder(
                policy_id=self.policy_id,
                policy_kind="archival",
                kind_=DecisionKind.ALLOW,
                target_type=target_type,
                target_id=target_id,
            ).set_confidence(confidence).set_uncertainty(1.0 - confidence).add_evidence("artifact_qualifies").build()
        
        else:
            return MemoryDecisionBuilder(
                policy_id=self.policy_id,
                policy_kind="archival",
                kind_=DecisionKind.DENY,
                target_type=target_type,
                target_id=target_id,
            ).set_confidence(0.9).set_uncertainty(0.1).add_evidence("artifact_does_not_qualify").build()
    
    def _should_archive(
        self,
        artifact: Optional[Any],
        current_state: str,
        retention_days: int,
        usage_rate: float,
        context: Dict[str, Any],
    ) -> Tuple[bool, str]:
        """
        Determine if an artifact should be archived.
        
        Returns:
            Tuple of (should_archive, reason)
        """
        # Check current state - already archived?
        if current_state == "archived":
            return False, "Artifact is already archived"
        
        # Check retention period minimum
        if retention_days < self.min_retention_days:
            return False, f"Retention period {retention_days} days below minimum {self.min_retention_days}"
        
        # Check usage rate - high usage prevents archival
        if usage_rate > self.max_usage_threshold:
            return False, f"Usage rate {usage_rate} exceeds threshold {self.max_usage_threshold}"
        
        # All checks passed
        return True, "Artifact meets archival criteria"


def create_archival_policy(
    policy_id: Optional[str] = None,
    name: str = "archival",
    min_retention_days: int = 30,
    max_usage_threshold: float = 0.1,
) -> ArchivalPolicy:
    """Create an archival policy instance."""
    return ArchivalPolicy(
        policy_id=policy_id,
        name=name,
        min_retention_days=min_retention_days,
        max_usage_threshold=max_usage_threshold,
    )


__all__ = [
    "ArchivalPolicy",
    "create_archival_policy",
]