# Temporal Validation - Phase 7.8
# ================================

"""
Canonical Temporal Validation.

Temporal validation remains observational - it evaluates but never modifies
temporal artifacts directly.
"""

from __future__ import annotations

import time
import uuid
from dataclasses import dataclass, field
from typing import Dict, List, Tuple, Optional, Any
from enum import Enum, auto


class ValidationType(Enum):
    """Types of temporal validation."""
    
    TIMESTAMP_INCONSISTENCY = "timestamp_inconsistency"  # Timestamp conflicts
    ORDERING_VIOLATION = "ordering_violation"           # Chronological ordering violated
    CONSTRAINT_VIOLATION = "constraint_violation"       # Temporal constraints violated
    CYCLE_DETECTION = "cycle_detection"                  # Cyclic dependencies found
    INTERVAL_GAP = "interval_gap"                        # Gaps between intervals
    OVERLAP_VIOLATION = "overlap_violation"             # Forbidden overlaps detected
    PASSED = "passed"                                    # Validation passed


class ValidationResult(Enum):
    """Validation result states."""
    
    PASSED = "passed"
    FAILED = "failed"
    WARNING = "warning"
    INDETERMINATE = "indeterminate"


@dataclass(frozen=True)
class TemporalValidation:
    """
    Result of temporal validation.
    
    Validation is observational - it never modifies temporal artifacts directly.
    """
    
    # Identity
    validation_id: str                      # Unique validation identifier
    semantic_identity: str                  # Semantic identity (stable across runs)
    
    # What was validated
    validated_object_type: str              # "event_set", "chronology", etc.
    validated_object_id: Optional[str] = None  # ID of validated object
    
    # Findings
    findings: Tuple[str, ...] = ()          # Detailed validation notes
    validation_type: ValidationType = ValidationType.TIMESTAMP_INCONSISTENCY  # Default - will be updated by actual validation
    
    # Result
    result: ValidationResult = ValidationResult.INDETERMINATE
    
    # Metadata
    created_at_utc: float = field(default_factory=time.time)
    
    # Provenance
    source_validation_id: Optional[str] = None   # If derived from another validation
    origin_context: str = "unknown"              # Where did the validation originate?
    
    @property
    def is_passed(self) -> bool:
        """Check if validation passed."""
        return self.result == ValidationResult.PASSED
    
    @property
    def is_failed(self) -> bool:
        """Check if validation failed."""
        return self.result == ValidationResult.FAILED
    
    @property
    def has_warnings(self) -> bool:
        """Check if validation had warnings."""
        return self.result == ValidationResult.WARNING
    
    def has_finding(self, finding_type: str) -> bool:
        """Check if a specific type of finding was recorded."""
        return any(finding_type in f for f in self.findings)


@dataclass(frozen=True)
class TemporalValidationIdentity:
    """
    Immutable identity for a temporal validation result.
    
    Allows replay and verification of validation results.
    """
    
    # Core identity
    semantic_identity: str                    # Stable identity across runs
    
    # Context
    validation_number: int = 1                # For repeated validations
    timestamp_utc: float = field(default_factory=time.time)
    
    @classmethod
    def create(cls, semantic_identity: str, validation_number: int = 1) -> TemporalValidationIdentity:
        """Create a new temporal validation identity."""
        return cls(
            semantic_identity=semantic_identity,
            validation_number=validation_number,
        )


def dataclass_replace(instance: Any, **kwargs: Any) -> Any:
    """Simple dataclass replace helper for frozen instances."""
    # For Python 3.12+, use dataclasses.replace
    # This is a simple implementation for compatibility
    return instance.__class__(**{**instance.__dict__, **kwargs})


__all__ = [
    "TemporalValidation",
    "TemporalValidationIdentity",
    "ValidationType",
    "ValidationResult",
]