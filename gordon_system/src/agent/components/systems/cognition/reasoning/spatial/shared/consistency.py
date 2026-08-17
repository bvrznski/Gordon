# Spatial Consistency - Phase 7.9
# ===============================

"""
Canonical Spatial Consistency Evaluation.

Spatial consistency evaluates:
    frame consistency, geometric validity, topological validity,
    transform correctness, environment coherence.
"""

from __future__ import annotations

import time
import uuid
from dataclasses import dataclass, field
from typing import Dict, List, Tuple, Optional, Any
from enum import Enum, auto


@dataclass(frozen=True)
class ConsistencyFinding:
    """
    Individual finding from consistency evaluation.
    
    Each finding documents a specific check result.
    """
    
    # Identity
    finding_id: str                         # Unique identifier
    
    # Check type
    check_type: str                         # e.g., "frame_consistency", "geometric_validity"
    
    # Result
    is_valid: bool = True                   # Did the check pass?
    severity: str = "info"                  # info, warning, error
    
    # Details
    description: str = ""                   # Human-readable description
    affected_entities: Tuple[str, ...] = ()  # Which entities are affected?
    
    # Provenance
    created_at_utc: float = field(default_factory=time.time)
    source_descriptor_id: str = ""


class ConsistencyType(Enum):
    """Kinds of consistency checks."""
    
    FRAME_CONSISTENCY = "frame_consistency"        # Reference frames agree
    GEOMETRIC_VALIDITY = "geometric_validity"      # Geometry is well-formed
    TOPOLOGICAL_VALIDITY = "topological_validity"  # Topology is consistent
    TRANSFORM_CORRECTNESS = "transform_correctness"  # Transforms are accurate
    ENVIRONMENT_COHERENCE = "environment_coherence"  # Environment makes sense


@dataclass(frozen=True)
class SpatialConsistency:
    """
    Result of spatial consistency evaluation.
    
    Consistency remains observational (never modifies artifacts directly).
    """
    
    # Identity
    consistency_id: str                     # Unique identifier
    
    # Evaluated entities
    evaluated_entities: Tuple[str, ...] = ()  # Which entity IDs?
    
    # Findings from all checks
    findings: Tuple[ConsistencyFinding, ...] = ()
    
    # Overall status
    overall_valid: bool = True              # Are all checks valid?
    violation_count: int = 0                # Number of violations
    
    # Check results summary
    frame_consistency_valid: bool = True
    geometric_validity_valid: bool = True
    topological_validity_valid: bool = True
    transform_correctness_valid: bool = True
    
    # Provenance
    created_at_utc: float = field(default_factory=time.time)
    source_descriptor_id: str = ""
    
    @property
    def has_violations(self) -> bool:
        """Check if any violations were found."""
        return self.violation_count > 0 or not self.overall_valid
    
    @classmethod
    def create(
        cls,
        semantic_identity: str,
        entity_ids: List[str],
    ) -> SpatialConsistency:
        """Create a new consistency evaluation result."""
        return cls(
            consistency_id=f"consistency:{uuid.uuid4().hex[:16]}",
            evaluated_entities=tuple(entity_ids),
            created_at_utc=time.time(),
            source_descriptor_id=semantic_identity,
        )
    
    def add_finding(self, finding: ConsistencyFinding) -> SpatialConsistency:
        """Return new consistency with additional finding."""
        violations = self.violation_count + (0 if finding.is_valid else 1)
        return dataclass_replace(
            self,
            findings=self.findings + (finding,),
            overall_valid=self.overall_valid and finding.is_valid,
            violation_count=violations,
        )


def dataclass_replace(instance: Any, **kwargs: Any) -> Any:
    """Simple dataclass replace helper for frozen instances."""
    return instance.__class__(**{**instance.__dict__, **kwargs})


__all__ = [
    "SpatialConsistency",
    "ConsistencyFinding", 
    "ConsistencyType",
]