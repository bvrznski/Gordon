# Memory Association Operation - Phase 5.1.2
# ===========================================

"""
Memory Association: Create new semantic relationships between artifacts.

Purpose:
    Discover or create semantic relationships between memory artifacts.

Association owns:
    - relationship proposal (new associations)
    - relationship confidence (initial trust level)
    - relationship revision (tracking changes)

Association never changes artifact identity or provenance.

Input:
    - Memory Artifacts: Source and target artifacts
    - Existing relations: Current graph state
    - Semantic context: Additional information for association discovery

Output:
    - Candidate relations: Proposed new relationships
    - Relation revisions: Tracking of relationship changes
    - Association evidence: Supporting data for associations

Usage:

    from gordon_system.src.agent.components.systems.memory.operations.association import AssociationOperation
    
    associator = AssociationOperation()
    
    # Create association between two artifacts
    result, projection = associator.execute(
        inputs={
            "source_artifact_id": "art-123",
            "target_artifact_id": "art-456",
            "relation_kind": "supports",
        }
    )
"""

from __future__ import annotations

import time
import uuid
from typing import Dict, List, Tuple, Optional, Any
from dataclasses import dataclass, field


# =============================================================================
# RELATION KIND MAPPINGS
# =============================================================================

RELATION_KINDS = {
    "references": "reference",
    "contains": "containment",
    "belongs_to": "membership",
    "precedes": "temporal_order",
    "follows": "temporal_order",
    "supports": "semantic_support",
    "contradicts": "semantic_conflict",
    "derived_from": "causal_derivation",
    "causes": "causal_relationship",
    "generalizes": "semantic_hierarchy",
    "specializes": "semantic_hierarchy",
    "similar_to": "semantic_similarity",
}


# =============================================================================
# ASSOCIATION CONFIGURATION
# =============================================================================


@dataclass(frozen=True)
class AssociationConfig:
    """Configuration for the association operation."""
    
    default_confidence: float = 0.75
    min_evidence_for_association: int = 1
    max_associations_per_artifact: int = 100
    bidirectional_by_default: bool = False


# =============================================================================
# ASSOCIATION RESULT
# =============================================================================


@dataclass(frozen=True)
class AssociationResult:
    """Result produced by the association operation."""
    
    result_id: str                          # Unique result ID
    new_relations: Tuple[Any, ...]          # Newly created relationships
    updated_revisions: Tuple[Any, ...]      # Updated revision records
    duration_ms: float = 0.0                # Execution time
    timestamp_utc: float = field(default_factory=time.time)


# =============================================================================
# ASSOCIATION OPERATION
# =============================================================================


class AssociationOperation:
    """
    Create semantic relationships between memory artifacts.
    
    This operation creates new associations without modifying artifact identity,
    provenance, or history. Each association is tracked with confidence and
    can be revised later if needed.
    
    Usage:
        associator = AssociationOperation()
        result, projection = associator.execute(association_inputs)
    """
    
    def __init__(
        self,
        operation_id: Optional[str] = None,
        config: Optional[AssociationConfig] = None,
    ):
        """Initialize the association operation."""
        self.operation_id: str = operation_id or str(uuid.uuid4())
        self.config: AssociationConfig = config or AssociationConfig()
    
    def validate(
        self,
        inputs: Any,
        context: Optional[Dict[str, Any]] = None,
    ) -> bool:
        """Validate association inputs."""
        try:
            if not isinstance(inputs, dict):
                return False
            
            # Check required fields
            if "source_artifact_id" not in inputs or "target_artifact_id" not in inputs:
                return False
            
            # Validate relation kind if provided
            if "relation_kind" in inputs:
                kind = inputs["relation_kind"]
                if not isinstance(kind, str):
                    return False
            
            # Validate confidence if provided
            if "confidence" in inputs:
                conf = inputs["confidence"]
                if not isinstance(conf, (int, float)) or not 0.0 <= conf <= 1.0:
                    return False
            
            return True
            
        except Exception:
            return False
    
    def execute(
        self,
        inputs: Any,
        context: Optional[Dict[str, Any]] = None,
    ) -> Tuple[AssociationResult, Dict[str, Any]]:
        """
        Execute the association operation.
        
        Args:
            inputs: Association parameters
                - source_artifact_id: ID of the source artifact
                - target_artifact_id: ID of the target artifact
                - relation_kind: Type of relationship (default: "references")
                - confidence: Trust level (optional)
            context: Optional execution context
            
        Returns:
            Tuple of (association_result, projection)
            
        Raises:
            ValueError: If inputs are invalid
        """
        if not self.validate(inputs, context):
            raise ValueError("Invalid association inputs")
        
        start_time = time.time()
        
        try:
            # Parse inputs
            source_id = inputs["source_artifact_id"]
            target_id = inputs["target_artifact_id"]
            
            kind_str = inputs.get("relation_kind", "references")
            confidence = inputs.get("confidence", self.config.default_confidence)
            
            # Import relation classes at runtime
            from ..foundations.relation import MemoryRelation, MemoryRelationKind
            
            # Determine relation kind enum
            try:
                relation_kind = MemoryRelationKind(kind_str)
            except ValueError:
                # Use REFERENCES as fallback for unknown kinds
                relation_kind = MemoryRelationKind.REFERENCES
            
            # Create the new relationship
            new_relation = MemoryRelation(
                identity=str(uuid.uuid4()),
                source_artifact=source_id,
                target_artifact=target_id,
                relation_kind=relation_kind,
                strength=self.config.default_confidence,
                confidence=confidence,
                uncertainty=1.0 - confidence,
                provenance=f"association:{self.operation_id}",
                created_at_utc=time.time(),
            )
            
            duration_ms = (time.time() - start_time) * 1000
            
            association_result = AssociationResult(
                result_id=f"assoc:{uuid.uuid4().hex[:12]}",
                new_relations=(new_relation,),
                updated_revisions=(),  # No revisions in this simple case
                duration_ms=duration_ms,
                timestamp_utc=time.time(),
            )
            
            projection = {
                "operation_id": self.operation_id,
                "operation_kind": "association",
                "state": "completed",
                "inputs_processed": 1,
                "outputs_produced": len(association_result.new_relations),
                "duration_ms": duration_ms,
                "validation_status": "valid",
                "validation_result": f"Created {len(association_result.new_relations)} new associations",
            }
            
            return association_result, projection
            
        except Exception as e:
            raise ValueError(f"Association operation failed: {str(e)}")


# =============================================================================
# UTILITY FUNCTIONS
# =============================================================================


def create_association_operation(
    operation_id: Optional[str] = None,
    config: Optional[AssociationConfig] = None,
) -> AssociationOperation:
    """Create an association operation instance."""
    return AssociationOperation(operation_id=operation_id, config=config)


__all__ = [
    "AssociationOperation",
    "AssociationConfig",
    "AssociationResult",
    "create_association_operation",
]