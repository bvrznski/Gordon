# Memory Reconstruction Policy - Phase 5.1.5 Canonical Implementation
# ====================================================================
"""
Memory Reconstruction Policy: Determine whether reconstruction should occur.

Purpose:
    Evaluate if missing or incomplete memory can be reconstructed.
    
Policies evaluate. They never execute.

Policy Contract:
    Operation Proposal (Query/Incomplete Evidence)
         ↓
    ReconstructionPolicy.evaluate(proposal)
         ↓
    Decision (ALLOW, DENY, DEFER, ESCALATE)

Reconstruction Laws:
    RECONSTRUCTION-LAW-001: Reconstruction Policies evaluate reconstruction only
    RECONSTRUCTION-LAW-002: Reconstruction Policies never execute directly
    RECONSTRUCTION-LAW-003: Reconstruction recommendations preserve evidence
    RECONSTRUCTION-LAW-004: Reconstruction Policies preserve provenance
    RECONSTRUCTION-LAW-005: Reconstruction Policies expose confidence explicitly
    RECONSTRUCTION-LAW-006: Reconstruction Policies remain explainable
    RECONSTRUCTION-LAW-007: Reconstruction Policies remain observable
    RECONSTRUCTION-LAW-008: Reconstruction Policies remain deterministic
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


class ReconstructionPolicy(MemoryPolicy):
    """
    Evaluate whether reconstruction of incomplete memory is appropriate.
    
    The reconstruction policy examines:
        - Query or request for reconstruction
        - Available incomplete evidence
        - Context and supporting information
        - Expected confidence in reconstructed result
        
    This policy never performs reconstruction; it only evaluates proposals.
    """
    
    def __init__(
        self,
        policy_id: Optional[str] = None,
        name: str = "reconstruction",
        min_context_similarity: float = 0.4,  # Minimum context similarity
        max_incompleteness: float = 0.7,  # Maximum allowed incompleteness
    ):
        """
        Initialize the reconstruction policy.
        
        Args:
            policy_id: Unique ID for this policy instance
            name: Human-readable name
            min_context_similarity: Minimum context similarity for reconstruction
            max_incompleteness: Maximum allowed incompleteness (0.0-1.0)
        """
        super().__init__(
            policy_id=policy_id,
            name=name,
            kind_=PolicyKind.RECONSTRUCTION,
        )
        
        self.min_context_similarity: float = max(0.0, min(1.0, min_context_similarity))
        self.max_incompleteness: float = max(0.0, min(1.0, max_incompleteness))
        
    def evaluate(
        self,
        proposal: Dict[str, Any],
        context: Optional[Dict[str, Any]] = None,
    ) -> MemoryDecision:
        """
        Evaluate whether reconstruction should occur.
        
        Args:
            proposal: The proposed action/transition to evaluate
                Required fields:
                    - target_type: Should be "reconstruction"
                    - target_id: ID for this reconstruction request
                Optional fields:
                    - query: The reconstruction query
                    - incomplete_evidence: Available partial evidence
                    - context_similarity: Similarity score with available context
                    - expected_confidence: Expected confidence in result
            context: Additional context for evaluation
            
        Returns:
            MemoryDecision with recommendation
        """
        target_type = proposal.get("target_type", "reconstruction")
        target_id = proposal.get("target_id", "unknown")
        
        query = proposal.get("query", "")
        incomplete_evidence = proposal.get("incomplete_evidence", [])
        context_similarity = proposal.get("context_similarity", 0.5)
        expected_confidence = proposal.get("expected_confidence", 0.5)
        
        # Evaluate reconstruction
        should_reconstruct, reason = self._should_reconstruct(
            query=query,
            incomplete_evidence=incomplete_evidence,
            context_similarity=context_similarity,
            expected_confidence=expected_confidence,
            context=context or {},
        )
        
        if should_reconstruct:
            confidence = 0.6 + (context_similarity * 0.4)  # Higher similarity = higher confidence
            return MemoryDecisionBuilder(
                policy_id=self.policy_id,
                policy_kind="reconstruction",
                kind_=DecisionKind.ALLOW,
                target_type=target_type,
                target_id=target_id,
            ).set_confidence(confidence).set_uncertainty(1.0 - confidence).add_evidence("query_qualifies").build()
        
        else:
            return MemoryDecisionBuilder(
                policy_id=self.policy_id,
                policy_kind="reconstruction",
                kind_=DecisionKind.DENY,
                target_type=target_type,
                target_id=target_id,
            ).set_confidence(0.9).set_uncertainty(0.1).add_evidence("query_does_not_qualify").build()
    
    def _should_reconstruct(
        self,
        query: str,
        incomplete_evidence: List[Dict[str, Any]],
        context_similarity: float,
        expected_confidence: float,
        context: Dict[str, Any],
    ) -> Tuple[bool, str]:
        """
        Determine if reconstruction should occur.
        
        Returns:
            Tuple of (should_reconstruct, reason)
        """
        # Check query exists
        if not query:
            return False, "No query provided"
        
        # Check incomplete evidence threshold
        total_incompleteness = sum(e.get("incompleteness", 0.5) for e in incomplete_evidence)
        avg_incompleteness = total_incompleteness / len(incomplete_evidence) if incomplete_evidence else 1.0
        
        if avg_incompleteness > self.max_incompleteness:
            return False, f"Incompleteness {avg_incompleteness} exceeds maximum {self.max_incompleteness}"
        
        # Check context similarity
        if context_similarity < self.min_context_similarity:
            return False, f"Context similarity {context_similarity} below minimum {self.min_context_similarity}"
        
        # All checks passed
        return True, "Query meets reconstruction criteria"


def create_reconstruction_policy(
    policy_id: Optional[str] = None,
    name: str = "reconstruction",
    min_context_similarity: float = 0.4,
    max_incompleteness: float = 0.7,
) -> ReconstructionPolicy:
    """Create a reconstruction policy instance."""
    return ReconstructionPolicy(
        policy_id=policy_id,
        name=name,
        min_context_similarity=min_context_similarity,
        max_incompleteness=max_incompleteness,
    )


__all__ = [
    "ReconstructionPolicy",
    "create_reconstruction_policy",
]