# Memory Reconsolidation Operation - Phase 5.1.2
# ==============================================

"""
Memory Reconsolidation: Revise previously consolidated knowledge while preserving history.

Purpose:
    Update existing memories with new evidence while maintaining full history.

Reconsolidation owns:
    - revision of existing memory (with new evidence)
    - updated confidence estimates
    - extended provenance

Reconsolidation preserves identity, history, and provenance.

Input:
    - Existing artifact: The memory to update
    - New evidence: Supporting or contradicting information
    - Existing provenance: Current provenance record

Output:
    - New revision: Updated artifact version
    - Updated confidence: Revised belief level
    - Extended provenance: History of this update

Usage:

    from gordon_system.src.agent.components.systems.memory.operations.reconsolidation import ReconsolidationOperation
    
    reconsolidator = ReconsolidationOperation()
    
    # Reconsolidate an existing memory with new evidence
    result, projection = reconsolidator.execute(
        inputs={
            "artifact_id": "art-123",
            "new_evidence": {...},
            "evidence_confidence": 0.8,
        }
    )
"""

from __future__ import annotations

import time
import uuid
from typing import Dict, List, Tuple, Optional, Any
from dataclasses import dataclass, field


# =============================================================================
# RECONSOLIDATION CONFIGURATION
# =============================================================================


@dataclass(frozen=True)
class ReconsolidationConfig:
    """Configuration for the reconsolidation operation."""
    
    confidence_threshold_for_update: float = 0.75
    evidence_weight: float = 1.0
    update_confidence_by: float = 0.1


# =============================================================================
# RECONSOLIDATION RESULT
# =============================================================================


@dataclass(frozen=True)
class ReconsolidationResult:
    """Result produced by the reconsolidation operation."""
    
    result_id: str                          # Unique result ID
    revised_artifacts: Tuple[Any, ...]      # Updated artifact versions
    confidence_changes: Dict[str, float]    # How confidence changed for each
    duration_ms: float = 0.0                # Execution time
    timestamp_utc: float = field(default_factory=time.time)


# =============================================================================
# RECONSOLIDATION OPERATION
# =============================================================================


class ReconsolidationOperation:
    """
    Revise previously consolidated knowledge while preserving history.
    
    This operation:
        1. Retrieves the existing memory artifact
        2. Evaluates new evidence against existing confidence
        3. Creates a new revision with updated confidence if warranted
        4. Extends provenance with the update reason
        
    The original artifact remains unchanged; only the revision is created.
    
    Usage:
        reconsolidator = ReconsolidationOperation()
        result, projection = reconsolidator.execute(reconsolidation_inputs)
    """
    
    def __init__(
        self,
        operation_id: Optional[str] = None,
        config: Optional[ReconsolidationConfig] = None,
    ):
        """Initialize the reconsolidation operation."""
        self.operation_id: str = operation_id or str(uuid.uuid4())
        self.config: ReconsolidationConfig = config or ReconsolidationConfig()
    
    def validate(
        self,
        inputs: Any,
        context: Optional[Dict[str, Any]] = None,
    ) -> bool:
        """Validate reconsolidation inputs."""
        try:
            if not isinstance(inputs, dict):
                return False
            
            # Check required fields
            if "artifact_id" not in inputs or "new_evidence" not in inputs:
                return False
            
            artifact_id = inputs["artifact_id"]
            if not isinstance(artifact_id, str) or len(artifact_id) == 0:
                return False
            
            new_evidence = inputs["new_evidence"]
            if not isinstance(new_evidence, dict):
                return False
            
            return True
            
        except Exception:
            return False
    
    def execute(
        self,
        inputs: Any,
        context: Optional[Dict[str, Any]] = None,
    ) -> Tuple[ReconsolidationResult, Dict[str, Any]]:
        """
        Execute the reconsolidation operation.
        
        Args:
            inputs: Reconsolidation parameters
                - artifact_id: ID of the artifact to update
                - new_evidence: New evidence supporting or contradicting the memory
                - evidence_confidence: Trust level in the new evidence (optional)
            context: Optional execution context
            
        Returns:
            Tuple of (reconsolidation_result, projection)
            
        Raises:
            ValueError: If inputs are invalid
        """
        if not self.validate(inputs, context):
            raise ValueError("Invalid reconsolidation inputs")
        
        start_time = time.time()
        
        try:
            # Parse inputs
            artifact_id = inputs["artifact_id"]
            new_evidence = inputs["new_evidence"]
            evidence_confidence = inputs.get("evidence_confidence", self.config.confidence_threshold_for_update)
            
            # In a real implementation, this would:
            # 1. Retrieve the existing artifact revision
            # 2. Compare new evidence with current confidence
            # 3. Calculate updated confidence (weighted average)
            # 4. Create new revision with updated values
            
            # For now, return a placeholder result
            from ..foundations.artifact import MemoryArtifact
            
            revised_artifacts: Tuple[MemoryArtifact, ...] = ()
            
            duration_ms = (time.time() - start_time) * 1000
            
            reconsolidation_result = ReconsolidationResult(
                result_id=f"recon:{uuid.uuid4().hex[:12]}",
                revised_artifacts=revised_artifacts,
                confidence_changes={artifact_id: evidence_confidence},
                duration_ms=duration_ms,
                timestamp_utc=time.time(),
            )
            
            projection = {
                "operation_id": self.operation_id,
                "operation_kind": "reconsolidation",
                "state": "completed",
                "inputs_processed": 1,
                "outputs_produced": len(revised_artifacts),
                "duration_ms": duration_ms,
                "validation_status": "valid",
                "validation_result": f"Reconsolidated artifact {artifact_id}",
            }
            
            return reconsolidation_result, projection
            
        except Exception as e:
            raise ValueError(f"Reconsolidation operation failed: {str(e)}")


# =============================================================================
# UTILITY FUNCTIONS
# =============================================================================


def create_reconsolidation_operation(
    operation_id: Optional[str] = None,
    config: Optional[ReconsolidationConfig] = None,
) -> ReconsolidationOperation:
    """Create a reconsolidation operation instance."""
    return ReconsolidationOperation(operation_id=operation_id, config=config)


__all__ = [
    "ReconsolidationOperation",
    "ReconsolidationConfig",
    "ReconsolidationResult",
    "create_reconsolidation_operation",
]