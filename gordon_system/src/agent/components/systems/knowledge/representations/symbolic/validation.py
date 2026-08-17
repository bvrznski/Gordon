# Knowledge Representation - Symbolic Validation - Phase 6.2
# ===========================================================

"""
Validation for symbolic representations.

This module provides validation utilities:
    * Structure completeness checks
    * Constraint satisfaction verification
    * Ontology compatibility validation
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Tuple, Optional, Any
import time
import uuid


# =============================================================================
# SYMBOLIC VALIDATION - Validation record
# =============================================================================


@dataclass(frozen=True)
class SymbolicValidation:
    """
    Validation result for a symbolic representation.
    
    Tracks whether and how a symbolic representation was validated.
    
    Fields:
        validation_identity: Unique identifier for this validation record
        representation_id:   ID of the representation being validated
        validation_timestamp: When validation occurred
        validation_level:    Depth of validation (basic, structural, semantic)
        passed_checks:       List of checks that passed
        failed_checks:       List of checks that failed with reasons
        ontology_compatible: Whether representation is compatible with current ontology
    """
    
    # Identity and metadata
    validation_identity: str               # Unique validation ID
    
    representation_id: str                 # Representation being validated
    
    validation_timestamp: float = field(default_factory=time.time)
    validation_level: str = "basic"        # basic, structural, semantic, full
    
    # Validation results
    passed_checks: Tuple[str, ...] = field(default_factory=tuple)
    failed_checks: Tuple[Dict[str, Any], ...] = field(default_factory=tuple)
    
    ontology_compatible: bool = True       # Ontology compatibility status
    
    @property
    def is_valid(self) -> bool:
        """Check if representation passed all validation checks."""
        return len(self.failed_checks) == 0 and self.ontology_compatible
    
    @property
    def check_count(self) -> int:
        """Get total number of checks performed."""
        return len(self.passed_checks)
    
    @property
    def failure_count(self) -> int:
        """Get number of failed checks."""
        return len(self.failed_checks)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert validation record to dictionary for serialization."""
        return {
            "validation_identity": self.validation_identity,
            "representation_id": self.representation_id,
            "validation_timestamp": self.validation_timestamp,
            "validation_level": self.validation_level,
            "passed_checks": [c for c in self.passed_checks],
            "failed_checks": [f for f in self.failed_checks],
            "ontology_compatible": self.ontology_compatible,
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "SymbolicValidation":
        """Create validation record from dictionary."""
        return cls(
            validation_identity=data.get("validation_identity", str(uuid.uuid4())),
            representation_id=data.get("representation_id", ""),
            validation_timestamp=float(data.get("validation_timestamp", time.time())),
            validation_level=data.get("validation_level", "basic"),
            passed_checks=tuple(data.get("passed_checks", [])),
            failed_checks=tuple(data.get("failed_checks", [])),
            ontology_compatible=bool(data.get("ontology_compatible", True)),
        )
    
    @classmethod
    def create_initial(
        cls,
        representation_id: str,
        validation_level: str = "basic",
    ) -> "SymbolicValidation":
        """Create initial validation record."""
        return cls(
            validation_identity=f"validate:{uuid.uuid4().hex[:16]}",
            representation_id=representation_id,
            validation_level=validation_level,
        )
    
    def with_passed(self, check_name: str) -> "SymbolicValidation":
        """Add a passed check to the record."""
        return SymbolicValidation(
            validation_identity=self.validation_identity,
            representation_id=self.representation_id,
            validation_timestamp=time.time(),
            validation_level=self.validation_level,
            passed_checks=self.passed_checks + (check_name,),
            failed_checks=self.failed_checks,
            ontology_compatible=self.ontology_compatible,
        )
    
    def with_failed(self, check_info: Dict[str, Any]) -> "SymbolicValidation":
        """Add a failed check to the record."""
        return SymbolicValidation(
            validation_identity=self.validation_identity,
            representation_id=self.representation_id,
            validation_timestamp=time.time(),
            validation_level=self.validation_level,
            passed_checks=self.passed_checks,
            failed_checks=self.failed_checks + (check_info,),
            ontology_compatible=False,
        )


__all__ = [
    # Validation records
    "SymbolicValidation",
]