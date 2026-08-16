# Memory Supersession Policy - Phase 5.1.5 Canonical Implementation
# ==================================================================
"""
Memory Supersession Policy: Evaluate whether a revision should supersede another.

Purpose:
    Determine if a newer revision of an artifact should replace the current one.
    
Policies evaluate. They never execute.

Policy Contract:
    Operation Proposal (Revisions)
         ↓
    SupersessionPolicy.evaluate(proposal)
         ↓
    Decision (ALLOW, DENY, DEFER, ESCALATE)

Supersession Laws:
    SUPERSESSION-LAW-001: Supersession Policies evaluate supersession only
    SUPERSESSION-LAW-002: Supersession Policies never execute directly
    SUPERSESSION-LAW-003: Supersession recommendations preserve evidence
    SUPERSESSION-LAW-004: Supersession Policies preserve provenance
    SUPERSESSION-LAW-005: Supersession Policies expose validation explicitly
    SUPERSESSION-LAW-006: Supersession Policies remain explainable
    SUPERSESSION-LAW-007: Supersession Policies remain observable
    SUPERSESSION-LAW-008: Supersession Policies remain deterministic
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


class SupersessionPolicy(MemoryPolicy):
    """
    Evaluate whether a newer revision should replace an older revision.
    
    The supersession policy examines:
        - Current and candidate revisions
        - Validation status of new revision
        - Evidence supporting the change
        - Impact assessment
        
    This policy never performs supersession; it only evaluates proposals.
    """
    
    def __init__(
        self,
        policy_id: Optional[str] = None,
        name: str = "supersession",
        require_validation: bool = True,
        min_confidence: float = 0.7,  # Minimum confidence for supersession
    ):
        """
        Initialize the supersession policy.
        
        Args:
            policy_id: Unique ID for this policy instance
            name: Human-readable name
            require_validation: Must new revision be validated?
            min_confidence: Minimum confidence threshold
        """
        super().__init__(
            policy_id=policy_id,
            name=name,
            kind_=PolicyKind.SUPERSESSION,
        )
        
        self.require_validation: bool = require_validation
        self.min_confidence: float = max(0.0, min(1.0, min_confidence))
        
    def evaluate(
        self,
        proposal: Dict[str, Any],
        context: Optional[Dict[str, Any]] = None,
    ) -> MemoryDecision:
        """
        Evaluate whether a revision should supersede another.
        
        Args:
            proposal: The proposed action/transition to evaluate
                Required fields:
                    - target_type: Should be "revision"
                    - target_id: ID of the current revision
                Optional fields:
                    - current_revision: The existing current revision
                    - candidate_revision: The proposed new revision
                    - evidence: Supporting evidence for the change
                    - validation_status: Validation status of candidate
            context: Additional context for evaluation
            
        Returns:
            MemoryDecision with recommendation
        """
        target_type = proposal.get("target_type", "revision")
        target_id = proposal.get("target_id", "unknown")
        
        current_revision = proposal.get("current_revision")
        candidate_revision = proposal.get("candidate_revision")
        evidence = proposal.get("evidence", [])
        validation_status = proposal.get("validation_status", {})
        
        # Evaluate supersession
        should_supersede, reason = self._should_supersede(
            current_revision=current_revision,
            candidate_revision=candidate_revision,
            evidence=evidence,
            validation_status=validation_status,
            context=context or {},
        )
        
        if should_supersede:
            confidence = 0.8 + (len(evidence) * 0.05)  # More evidence = higher confidence
            return MemoryDecisionBuilder(
                policy_id=self.policy_id,
                policy_kind="supersession",
                kind_=DecisionKind.ALLOW,
                target_type=target_type,
                target_id=target_id,
            ).set_confidence(confidence).set_uncertainty(1.0 - confidence).add_evidence("revision_valid").build()
        
        else:
            return MemoryDecisionBuilder(
                policy_id=self.policy_id,
                policy_kind="supersession",
                kind_=DecisionKind.DENY,
                target_type=target_type,
                target_id=target_id,
            ).set_confidence(0.9).set_uncertainty(0.1).add_evidence("revision_not_valid").build()
    
    def _should_supersede(
        self,
        current_revision: Optional[Any],
        candidate_revision: Optional[Any],
        evidence: List[Dict[str, Any]],
        validation_status: Dict[str, Any],
        context: Dict[str, Any],
    ) -> Tuple[bool, str]:
        """
        Determine if a revision should supersede another.
        
        Returns:
            Tuple of (should_supersede, reason)
        """
        # Check candidate exists
        if candidate_revision is None:
            return False, "No candidate revision provided"
        
        # Check validation status
        if self.require_validation:
            if validation_status.get("status") != "valid":
                return False, f"Validation status: {validation_status.get('status', 'unknown')}"
        
        # Check confidence (if available in evidence)
        for ev in evidence:
            conf = ev.get("confidence", 1.0)
            if conf < self.min_confidence:
                return False, f"Evidence confidence {conf} below threshold {self.min_confidence}"
        
        # All checks passed
        return True, "Revision meets supersession criteria"


def create_supersession_policy(
    policy_id: Optional[str] = None,
    name: str = "supersession",
    require_validation: bool = True,
    min_confidence: float = 0.7,
) -> SupersessionPolicy:
    """Create a supersession policy instance."""
    return SupersessionPolicy(
        policy_id=policy_id,
        name=name,
        require_validation=require_validation,
        min_confidence=min_confidence,
    )


__all__ = [
    "SupersessionPolicy",
    "create_supersession_policy",
]