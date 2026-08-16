# Memory Admission Policy - Phase 5.1.5 Canonical Implementation
# ================================================================
"""
Memory Admission Policy: Determine whether a candidate should enter Memory.

Purpose:
    Evaluate if a candidate artifact should be admitted into the Memory Substrate.
    
Policies evaluate. They never execute.

Policy Contract:
    Operation Proposal (Candidate Artifact)
         ↓
    AdmissionPolicy.evaluate(proposal)
         ↓
    Decision (ALLOW, DENY, DEFER, ESCALATE)

Admission Laws:
    ADMISSION-LAW-001: Admission Policies evaluate candidates only
    ADMISSION-LAW-002: Admission Policies never create Memory Artifacts
    ADMISSION-LAW-003: Admission Policies preserve validation evidence
    ADMISSION-LAW-004: Admission Policies preserve provenance
    ADMISSION-LAW-005: Admission Policies expose explicit recommendations
    ADMISSION-LAW-006: Admission Policies remain explainable
    ADMISSION-LAW-007: Admission Policies remain observable
    ADMISSION-LAW-008: Admission Policies remain deterministic
"""

from __future__ import annotations

import time
import uuid

from typing import Dict, List, Tuple, Optional, Any

# Import core policy components - use absolute imports for clarity
try:
    from gordon_system.src.agent.components.systems.memory.policies.decision import DecisionKind, MemoryDecision, MemoryDecisionBuilder
    from gordon_system.src.agent.components.systems.memory.policies.evidence import EvidenceKind, PolicyEvidence
    from gordon_system.src.agent.components.systems.memory.policies.policy import MemoryPolicy, PolicyKind
except ImportError:
    # Fallback for direct execution
    from decision import DecisionKind, MemoryDecision, MemoryDecisionBuilder
    from evidence import EvidenceKind, PolicyEvidence
    from policy import MemoryPolicy, PolicyKind


class AdmissionPolicy(MemoryPolicy):
    """
    Evaluate whether a candidate artifact should enter the Memory Substrate.
    
    The admission policy examines:
        - Candidate validation status
        - Provenance and origin
        - Confidence and certainty metrics
        - Importance signals from context
        
    This policy never creates artifacts; it only evaluates them.
    """
    
    def __init__(
        self,
        policy_id: Optional[str] = None,
        name: str = "admission",
        min_confidence: float = 0.5,  # Minimum confidence for ALLOW
        require_validation: bool = True,
    ):
        """
        Initialize the admission policy.
        
        Args:
            policy_id: Unique ID for this policy instance
            name: Human-readable name
            min_confidence: Minimum confidence threshold for allowing
            require_validation: Must artifact be validated to be admitted?
        """
        super().__init__(
            policy_id=policy_id,
            name=name,
            kind_=PolicyKind.ADMISSION,
        )
        
        self.min_confidence: float = max(0.0, min(1.0, min_confidence))
        self.require_validation: bool = require_validation
        
    def evaluate(
        self,
        proposal: Dict[str, Any],
        context: Optional[Dict[str, Any]] = None,
    ) -> MemoryDecision:
        """
        Evaluate a candidate for admission into Memory.
        
        Args:
            proposal: The proposed action/transition to evaluate
                Required fields:
                    - target_type: Should be "memory_artifact"
                    - target_id: ID of the artifact
                Optional fields:
                    - artifact: The candidate memory artifact (if available)
                    - validation_report: Validation report from the artifact
                    - confidence: Pre-computed confidence score
                    - provenance: Origin and processing history
            context: Additional context for evaluation
                Workspace state, active goals, importance signals
            
        Returns:
            MemoryDecision with recommendation
        """
        # Parse proposal
        target_type = proposal.get("target_type", "memory_artifact")
        target_id = proposal.get("target_id", "unknown")
        
        artifact = proposal.get("artifact")
        validation_report = proposal.get("validation_report", {})
        precomputed_confidence = proposal.get("confidence")
        provenance = proposal.get("provenance", {})
        
        # Build evidence collection
        evidence_refs: List[str] = []
        
        # Evaluate candidate
        is_valid, reason = self._evaluate_candidate(
            artifact=artifact,
            validation_report=validation_report,
            precomputed_confidence=precomputed_confidence,
            provenance=provenance,
            context=context or {},
        )
        
        if is_valid:
            confidence = precomputed_confidence if precomputed_confidence is not None else 0.8
            return MemoryDecisionBuilder(
                policy_id=self.policy_id,
                policy_kind="admission",
                kind_=DecisionKind.ALLOW,
                target_type=target_type,
                target_id=target_id,
            ).set_confidence(confidence).set_uncertainty(1.0 - confidence).add_evidence("candidate_validated").add_rule("min_confidence_threshold").build()
        
        else:
            return MemoryDecisionBuilder(
                policy_id=self.policy_id,
                policy_kind="admission",
                kind_=DecisionKind.DENY,
                target_type=target_type,
                target_id=target_id,
            ).set_confidence(0.9).set_uncertainty(0.1).add_evidence("candidate_failed_validation").add_rule("validation_required").build()
    
    def _evaluate_candidate(
        self,
        artifact: Optional[Any],
        validation_report: Dict[str, Any],
        precomputed_confidence: Optional[float],
        provenance: Dict[str, Any],
        context: Dict[str, Any],
    ) -> Tuple[bool, str]:
        """
        Evaluate a candidate for admission.
        
        Returns:
            Tuple of (is_valid, reason)
        """
        # Check validation report first
        if self.require_validation:
            is_validated = validation_report.get("status") == "valid"
            if not is_validated:
                return False, "Validation failed or missing"
        
        # Check confidence (if provided)
        if precomputed_confidence is not None:
            if precomputed_confidence < self.min_confidence:
                return False, f"Confidence {precomputed_confidence} below threshold {self.min_confidence}"
        
        # Artifact presence check
        if artifact is None:
            return False, "No artifact provided"
        
        # Check provenance (basic check)
        origin = provenance.get("origin")
        if not origin:
            return False, "Missing provenance information"
        
        # All checks passed
        return True, "Candidate passes all admission criteria"


def create_admission_policy(
    policy_id: Optional[str] = None,
    name: str = "admission",
    min_confidence: float = 0.5,
    require_validation: bool = True,
) -> AdmissionPolicy:
    """Create an admission policy instance."""
    return AdmissionPolicy(
        policy_id=policy_id,
        name=name,
        min_confidence=min_confidence,
        require_validation=require_validation,
    )


__all__ = [
    "AdmissionPolicy",
    "create_admission_policy",
]