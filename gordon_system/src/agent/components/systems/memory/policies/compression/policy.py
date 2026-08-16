# Memory Compression Policy - Phase 5.1.5 Canonical Implementation
# ==================================================================
"""
Memory Compression Policy: Evaluate whether compression should occur.

Purpose:
    Determine if an artifact's representation should be compressed.
    
Policies evaluate. They never execute.

Policy Contract:
    Operation Proposal (Artifact)
         ↓
    CompressionPolicy.evaluate(proposal)
         ↓
    Decision (ALLOW, DENY, DEFER, ESCALATE)

Compression Laws:
    COMPRESSION-LAW-001: Compression Policies evaluate compression only
    COMPRESSION-LAW-002: Compression Policies never execute directly
    COMPRESSION-LAW-003: Compression recommendations preserve evidence
    COMPRESSION-LAW-004: Compression Policies preserve provenance
    COMPRESSION-LAW-005: Compression Policies expose guarantees explicitly
    COMPRESSION-LAW-006: Compression Policies remain explainable
    COMPRESSION-LAW-007: Compression Policies remain observable
    COMPRESSION-LAW-008: Compression Policies remain deterministic
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


class CompressionPolicy(MemoryPolicy):
    """
    Evaluate whether an artifact's representation should be compressed.
    
    The compression policy examines:
        - Artifact graph structure and redundancy
        - Compression cost estimates
        - Recovery guarantees
        - Current storage constraints
        
    This policy never performs compression; it only evaluates proposals.
    """
    
    def __init__(
        self,
        policy_id: Optional[str] = None,
        name: str = "compression",
        min_redundancy: float = 0.3,  # Minimum redundancy for compression consideration
        max_compression_cost_ms: float = 100.0,  # Maximum acceptable compression time (ms)
    ):
        """
        Initialize the compression policy.
        
        Args:
            policy_id: Unique ID for this policy instance
            name: Human-readable name
            min_redundancy: Minimum redundancy ratio for compression consideration
            max_compression_cost_ms: Maximum acceptable compression time
        """
        super().__init__(
            policy_id=policy_id,
            name=name,
            kind_=PolicyKind.COMPRESSION,
        )
        
        self.min_redundancy: float = max(0.0, min(1.0, min_redundancy))
        self.max_compression_cost_ms: float = max(0.0, max_compression_cost_ms)
        
    def evaluate(
        self,
        proposal: Dict[str, Any],
        context: Optional[Dict[str, Any]] = None,
    ) -> MemoryDecision:
        """
        Evaluate whether compression should occur.
        
        Args:
            proposal: The proposed action/transition to evaluate
                Required fields:
                    - target_type: Should be "memory_artifact" or "artifact_graph"
                    - target_id: ID of the artifact/graph
                Optional fields:
                    - artifact: The memory artifact (if available)
                    - redundancy_score: Current redundancy in representation
                    - compression_cost_ms: Estimated compression time
                    - recovery_guaranteed: Can decompression be guaranteed?
            context: Additional context for evaluation
            
        Returns:
            MemoryDecision with recommendation
        """
        target_type = proposal.get("target_type", "memory_artifact")
        target_id = proposal.get("target_id", "unknown")
        
        artifact = proposal.get("artifact")
        redundancy_score = proposal.get("redundancy_score", 0.5)
        compression_cost_ms = proposal.get("compression_cost_ms", 0.0)
        recovery_guaranteed = proposal.get("recovery_guaranteed", True)
        
        # Evaluate compression
        should_compress, reason = self._should_compress(
            artifact=artifact,
            redundancy_score=redundancy_score,
            compression_cost_ms=compression_cost_ms,
            recovery_guaranteed=recovery_guaranteed,
            context=context or {},
        )
        
        if should_compress:
            confidence = 0.7 + (redundancy_score * 0.3)  # Higher redundancy = higher confidence
            return MemoryDecisionBuilder(
                policy_id=self.policy_id,
                policy_kind="compression",
                kind_=DecisionKind.ALLOW,
                target_type=target_type,
                target_id=target_id,
            ).set_confidence(confidence).set_uncertainty(1.0 - confidence).add_evidence("artifact_qualifies").build()
        
        else:
            return MemoryDecisionBuilder(
                policy_id=self.policy_id,
                policy_kind="compression",
                kind_=DecisionKind.DENY,
                target_type=target_type,
                target_id=target_id,
            ).set_confidence(0.9).set_uncertainty(0.1).add_evidence("artifact_does_not_qualify").build()
    
    def _should_compress(
        self,
        artifact: Optional[Any],
        redundancy_score: float,
        compression_cost_ms: float,
        recovery_guaranteed: bool,
        context: Dict[str, Any],
    ) -> Tuple[bool, str]:
        """
        Determine if an artifact should be compressed.
        
        Returns:
            Tuple of (should_compress, reason)
        """
        # Check redundancy threshold
        if redundancy_score < self.min_redundancy:
            return False, f"Redundancy {redundancy_score} below minimum {self.min_redundancy}"
        
        # Check compression cost
        if compression_cost_ms > self.max_compression_cost_ms:
            return False, f"Compression cost {compression_cost_ms}ms exceeds maximum {self.max_compression_cost_ms}ms"
        
        # Check recovery guarantee
        if not recovery_guaranteed:
            return False, "Recovery is not guaranteed"
        
        # All checks passed
        return True, "Artifact meets compression criteria"


def create_compression_policy(
    policy_id: Optional[str] = None,
    name: str = "compression",
    min_redundancy: float = 0.3,
    max_compression_cost_ms: float = 100.0,
) -> CompressionPolicy:
    """Create a compression policy instance."""
    return CompressionPolicy(
        policy_id=policy_id,
        name=name,
        min_redundancy=min_redundancy,
        max_compression_cost_ms=max_compression_cost_ms,
    )


__all__ = [
    "CompressionPolicy",
    "create_compression_policy",
]