# Spatial Validation - Phase 7.9
# =============================

"""
Canonical Spatial Validation.

Spatial validation evaluates geometric correctness, topological validity,
frame consistency, and spatial coherence.
Validation remains observational (never modifies artifacts directly).
"""

from __future__ import annotations

import time
import uuid
from dataclasses import dataclass, field
from typing import Dict, List, Tuple, Optional, Any
from enum import Enum, auto


@dataclass(frozen=True)
class ValidationResult:
    """
    Individual validation result for a check.
    
    Each validation documents what was checked and whether it passed.
    """
    
    # Identity
    validation_id: str                      # Unique identifier
    
    # Check type
    check_type: str                         # e.g., "geometry_validity", "topology_consistency"
    
    # Result
    is_valid: bool = True                   # Did the check pass?
    severity: str = "info"                  # info, warning, error
    
    # Details
    description: str = ""                   # Human-readable description
    affected_entity_ids: Tuple[str, ...] = ()  # Which entities are affected?
    
    # Provenance
    created_at_utc: float = field(default_factory=time.time)
    source_descriptor_id: str = ""


@dataclass(frozen=True)
class SpatialValidation:
    """
    Result of spatial validation evaluation.
    
    Validation remains observational (never modifies artifacts directly).
    """
    
    # Identity
    validation_id: str                      # Unique identifier
    
    # Evaluated entities
    evaluated_entities: Tuple[str, ...] = ()  # Which entity IDs?
    
    # All validation checks performed
    validations: Tuple[ValidationResult, ...] = ()
    
    # Overall result
    overall_valid: bool = True              # Did all checks pass?
    violation_count: int = 0                # Number of violations
    
    # Check summaries
    geometry_validity_valid: bool = True
    topological_validity_valid: bool = True
    frame_consistency_valid: bool = True
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
    ) -> SpatialValidation:
        """Create a new validation result."""
        return cls(
            validation_id=f"validation:{uuid.uuid4().hex[:16]}",
            evaluated_entities=tuple(entity_ids),
            created_at_utc=time.time(),
            source_descriptor_id=semantic_identity,
        )
    
    def add_validation(self, result: ValidationResult) -> SpatialValidation:
        """Return new validation with additional check."""
        violations = self.violation_count + (0 if result.is_valid else 1)
        return dataclass_replace(
            self,
            validations=self.validations + (result,),
            overall_valid=self.overall_valid and result.is_valid,
            violation_count=violations,
        )


def dataclass_replace(instance: Any, **kwargs: Any) -> Any:
    """Simple dataclass replace helper for frozen instances."""
    return instance.__class__(**{**instance.__dict__, **kwargs})


__all__ = [
    "SpatialValidation", 
    "ValidationResult",
]