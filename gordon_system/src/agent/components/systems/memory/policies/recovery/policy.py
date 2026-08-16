# Memory Recovery Policy - Phase 5.1.5 Canonical Implementation
# ===============================================================
"""
Memory Recovery Policy: Evaluate whether recovery should be attempted after lifecycle failure.

Purpose:
    Determine if a failed memory artifact can or should be recovered.
    
Policies evaluate. They never execute.

Policy Contract:
    Operation Proposal (Failure Report)
         ↓
    RecoveryPolicy.evaluate(proposal)
         ↓
    Decision (ALLOW, DENY, DEFER, ESCALATE)

Recovery Laws:
    RECOVERY-LAW-001: Recovery Policies evaluate recovery only
    RECOVERY-LAW-002: Recovery Policies never execute directly
    RECOVERY-LAW-003: Recovery recommendations preserve evidence
    RECOVERY-LAW-004: Recovery Policies preserve provenance
    RECOVERY-LAW-005: Recovery Policies expose recoverability explicitly
    RECOVERY-LAW-006: Recovery Policies remain explainable
    RECOVERY-LAW-007: Recovery Policies remain observable
    RECOVERY-LAW-008: Recovery Policies remain deterministic
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


class RecoveryPolicy(MemoryPolicy):
    """
    Evaluate whether recovery should be attempted after a lifecycle failure.
    
    The recovery policy examines:
        - Failure report and diagnostics
        - Current state of the artifact
        - Recoverability assessment
        - Historical data availability
        
    This policy never performs recovery; it only evaluates proposals.
    """
    
    def __init__(
        self,
        policy_id: Optional[str] = None,
        name: str = "recovery",
        min_recoverability: float = 0.5,  # Minimum recoverability threshold
        max_failure_age_days: int = 7,  # Maximum age of failure for recovery consideration
    ):
        """
        Initialize the recovery policy.
        
        Args:
            policy_id: Unique ID for this policy instance
            name: Human-readable name
            min_recoverability: Minimum recoverability score for approval
            max_failure_age_days: Maximum days since failure for recovery
        """
        super().__init__(
            policy_id=policy_id,
            name=name,
            kind_=PolicyKind.RECOVERY,
        )
        
        self.min_recoverability: float = max(0.0, min(1.0, min_recoverability))
        self.max_failure_age_days: int = max_failure_age_days
        
    def evaluate(
        self,
        proposal: Dict[str, Any],
        context: Optional[Dict[str, Any]] = None,
    ) -> MemoryDecision:
        """
        Evaluate whether recovery should be attempted.
        
        Args:
            proposal: The proposed action/transition to evaluate
                Required fields:
                    - target_type: Should be "recovery"
                    - target_id: ID for this recovery request
                Optional fields:
                    - failure_report: Details of the failure
                    - diagnostics: System diagnostics
                    - integrity_state: Current integrity state
                    - recoverability_score: Assessed recoverability (0.0-1.0)
            context: Additional context for evaluation
            
        Returns:
            MemoryDecision with recommendation
        """
        target_type = proposal.get("target_type", "recovery")
        target_id = proposal.get("target_id", "unknown")
        
        failure_report = proposal.get("failure_report", {})
        diagnostics = proposal.get("diagnostics", [])
        integrity_state = proposal.get("integrity_state", "corrupted")
        recoverability_score = proposal.get("recoverability_score", 0.5)
        
        # Evaluate recovery
        should_recover, reason = self._should_recover(
            failure_report=failure_report,
            diagnostics=diagnostics,
            integrity_state=integrity_state,
            recoverability_score=recoverability_score,
            context=context or {},
        )
        
        if should_recover:
            confidence = 0.5 + (recoverability_score * 0.5)  # Direct correlation
            return MemoryDecisionBuilder(
                policy_id=self.policy_id,
                policy_kind="recovery",
                kind_=DecisionKind.ALLOW,
                target_type=target_type,
                target_id=target_id,
            ).set_confidence(confidence).set_uncertainty(1.0 - confidence).add_evidence("artifact_recoverable").build()
        
        else:
            return MemoryDecisionBuilder(
                policy_id=self.policy_id,
                policy_kind="recovery",
                kind_=DecisionKind.DENY,
                target_type=target_type,
                target_id=target_id,
            ).set_confidence(0.9).set_uncertainty(0.1).add_evidence("artifact_not_recoverable").build()
    
    def _should_recover(
        self,
        failure_report: Dict[str, Any],
        diagnostics: List[Dict[str, Any]],
        integrity_state: str,
        recoverability_score: float,
        context: Dict[str, Any],
    ) -> Tuple[bool, str]:
        """
        Determine if recovery should be attempted.
        
        Returns:
            Tuple of (should_recover, reason)
        """
        # Check failure report exists
        if not failure_report:
            return False, "No failure report provided"
        
        # Check integrity state - some states are not recoverable
        non_recoverable_states = ("irreversible_loss", "permanent_corruption")
        if integrity_state in non_recoverable_states:
            return False, f"State {integrity_state} is not recoverable"
        
        # Check recoverability score threshold
        if recoverability_score < self.min_recoverability:
            return False, f"Recoverability {recoverability_score} below minimum {self.min_recoverability}"
        
        # All checks passed
        return True, "Artifact meets recovery criteria"


def create_recovery_policy(
    policy_id: Optional[str] = None,
    name: str = "recovery",
    min_recoverability: float = 0.5,
    max_failure_age_days: int = 7,
) -> RecoveryPolicy:
    """Create a recovery policy instance."""
    return RecoveryPolicy(
        policy_id=policy_id,
        name=name,
        min_recoverability=min_recoverability,
        max_failure_age_days=max_failure_age_days,
    )


__all__ = [
    "RecoveryPolicy",
    "create_recovery_policy",
]