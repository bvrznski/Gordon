# Hypothetical Validation - Phase 7.15 Part 2
# =============================================

"""
Canonical Validation Contract.

Hypothetical Validation is observational only - it never modifies
hypothetical artifacts directly.
"""

from __future__ import annotations

import time
import uuid
from dataclasses import dataclass, field
from typing import Dict, List, Tuple, Optional, Any
from enum import Enum, auto


class ValidationFindingKind(Enum):
    """Kinds of validation findings."""
    
    SUPPORTING_EVIDENCE = "supporting_evidence"  # Has supporting evidence
    INSUFFICIENT_EVIDENCE = "insufficient_evidence"  # Missing key evidence
    INCONSISTENCY = "inconsistency"              # Internal contradiction
    CONTRADICTION = "contradiction"              # Contradicts known facts
    UNKNOWN_REGION = "unknown_region"            # Relies on unknown assumptions


@dataclass(frozen=True)
class ValidationIdentity:
    """
    Immutable identity for a validation.
    
    Allows tracking validations across sessions.
    """
    
    semantic_identity: str                    # Stable identity across runs
    
    @classmethod
    def create(cls, semantic_identity: str) -> ValidationIdentity:
        """Create a new validation identity."""
        return cls(semantic_identity=semantic_identity)


@dataclass(frozen=True)
class ValidationFinding:
    """
    A finding from hypothetical validation.
    
    Findings remain explicit and inspectable at all times.
    """
    
    # Identity
    finding_id: str                           # Unique identifier
    
    # Target
    validated_hypothesis_id: str              # Which hypothesis was evaluated?
    
    # Finding details
    finding_kind: ValidationFindingKind       # What kind of finding?
    finding_statement: str                    # Description of the finding
    
    # Assessment
    confidence: float = 1.0                   # Confidence in this finding
    
    # Metadata
    found_at_utc: float = field(default_factory=time.time)
    
    @classmethod
    def create(
        cls,
        validated_hypothesis_id: str,
        finding_kind: ValidationFindingKind,
        finding_statement: str,
        confidence: float = 1.0,
    ) -> ValidationFinding:
        """Create a new validation finding."""
        return cls(
            finding_id=f"finding:{uuid.uuid4().hex[:16]}",
            validated_hypothesis_id=validated_hypothesis_id,
            finding_kind=finding_kind,
            finding_statement=finding_statement,
            confidence=confidence,
        )


@dataclass(frozen=True)
class ValidationResult:
    """
    Complete validation result for a hypothetical reasoning session.
    
    Validation remains observational - it never mutates artifacts directly.
    """
    
    # Identity
    validation_id: str                        # Unique identifier
    
    # Status
    status: str = "pending"                   # "pending", "valid", "invalid", "conditional"
    
    # Findings
    findings: Tuple[ValidationFinding, ...] = ()  # All findings from validation
    
    # Assessment
    confidence_score: float = 0.5             # Overall confidence score
    is_unsupported: bool = False              # No evidence either way
    is_untested: bool = True                  # Not yet tested against evidence
    
    # Metadata
    validated_at_utc: float = field(default_factory=time.time)
    
    @property
    def total_findings(self) -> int:
        """Return number of findings."""
        return len(self.findings)
    
    @classmethod
    def create(
        cls,
        status: str = "pending",
        findings: Optional[List[ValidationFinding]] = None,
        confidence_score: float = 0.5,
        is_unsupported: bool = False,
        is_untested: bool = True,
    ) -> ValidationResult:
        """Create a new validation result."""
        return cls(
            validation_id=f"validation:{uuid.uuid4().hex[:16]}",
            status=status,
            findings=tuple(findings or []),
            confidence_score=confidence_score,
            is_unsupported=is_unsupported,
            is_untested=is_untested,
        )


@dataclass(frozen=True)
class HypotheticalValidationError(Exception):
    """Exception raised when validation fails critically."""
    
    message: str                              # Error description
    findings: Tuple[ValidationFinding, ...] = ()  # Associated findings
    
    @classmethod
    def create(cls, message: str, findings: Optional[List[ValidationFinding]] = None) -> "HypotheticalValidationError":
        """Create a new validation error."""
        return cls(
            message=message,
            findings=tuple(findings or []),
        )


def dataclass_replace(instance: Any, **kwargs: Any) -> Any:
    """Simple dataclass replace helper for frozen instances."""
    return instance.__class__(**{**instance.__dict__, **kwargs})


__all__ = [
    "ValidationFindingKind",
    "ValidationIdentity",
    "ValidationFinding",
    "ValidationResult",
    "HypotheticalValidationError",
]