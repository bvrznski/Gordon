# Counterfactual Validation - Phase 7.6
# =====================================

"""
Validation of counterfactual reasoning results.

Counterfactual Validation is observational - it evaluates and reports findings
without modifying the alternative worlds or counterfactual artifacts.
"""

from __future__ import annotations

import time
import uuid
from dataclasses import dataclass, field
from typing import Dict, List, Tuple, Optional, Any
from enum import Enum, auto


class ValidationResultKind(Enum):
    """Types of validation results."""
    
    VALID = "valid"                           # World passes all checks
    CONDITIONALLY_VALID = "conditionally_valid"  # World is valid with caveats
    INVALID = "invalid"                       # World has critical issues
    UNKNOWN = "unknown"                       # Validation could not determine status


class ValidationFindingKind(Enum):
    """Kinds of validation findings."""
    
    INCONSISTENT_STATE = "inconsistent_state"
    VIOLATED_CONSTRAINT = "violated_constraint"
    MISSING_PROVENANCE = "missing_provenance"
    IMPOSSIBLE_WORLD = "impossible_world"     # Violates known physical/logical laws
    UNSUPPORTED_WORLD = "unsupported_world"   # Not supported by current model


@dataclass(frozen=True)
class CounterfactualValidation:
    """
    Validation of a counterfactual reasoning result.
    
    Validation remains observational - it never modifies the artifacts being validated.
    Instead, it produces reports about their state and quality.
    """
    
    # Identity
    validation_id: str                        # Unique validation identifier
    
    # Validated artifact (world, session, etc.)
    validated_artifact_type: str              # "counterfactual_session", "alternative_world"
    validated_artifact_id: str                # ID of the validated artifact
    
    # Result
    result: ValidationResultKind = ValidationResultKind.UNKNOWN
    
    # Findings (what was found during validation)
    findings: Tuple[ValidationFinding, ...] = ()
    
    # Provenance
    created_at_utc: float = field(default_factory=time.time)
    
    @property
    def is_valid(self) -> bool:
        """Check if validation succeeded."""
        return self.result == ValidationResultKind.VALID
    
    @classmethod
    def create(
        cls,
        artifact_type: str,
        artifact_id: str,
    ) -> CounterfactualValidation:
        """Create a new validation record."""
        return cls(
            validation_id=f"validation:{uuid.uuid4().hex[:16]}",
            validated_artifact_type=artifact_type,
            validated_artifact_id=artifact_id,
        )
    
    def with_result(self, result: ValidationResultKind) -> CounterfactualValidation:
        """Return a copy with the given result."""
        return dataclass_replace(
            self,
            result=result,
        )
    
    def add_finding(self, finding: ValidationFinding) -> CounterfactualValidation:
        """Return a copy with an additional finding."""
        return dataclass_replace(
            self,
            findings=self.findings + (finding,),
        )


@dataclass(frozen=True)
class ValidationFinding:
    """
    A specific finding from validation.
    
    Each finding describes a particular issue, constraint violation, or quality assessment.
    """
    
    # Identity
    finding_id: str                           # Unique finding identifier
    
    # Finding type
    finding_kind: ValidationFindingKind       # What kind of finding?
    
    # Description
    description: str                          # Human-readable explanation
    
    # Severity (low, medium, high)
    severity: str = "medium"                  # Impact assessment
    
    # Provenance
    created_at_utc: float = field(default_factory=time.time)
    
    @classmethod
    def create(
        cls,
        finding_kind: ValidationFindingKind,
        description: str,
    ) -> ValidationFinding:
        """Create a new validation finding."""
        return cls(
            finding_id=f"finding:{uuid.uuid4().hex[:16]}",
            finding_kind=finding_kind,
            description=description,
        )


@dataclass(frozen=True)
class ValidationTrace:
    """
    Complete trace of all validation steps performed.
    
    The trace preserves all findings and their context for inspection.
    """
    
    # Identity
    trace_id: str                             # Unique trace identifier
    
    # Steps executed
    validation_steps: Tuple[str, ...] = ()    # e.g., "integrity_check", "consistency_check"
    
    # Findings from each step
    findings_by_step: Dict[str, Tuple[ValidationFinding, ...]] = field(default_factory=dict)
    
    # Overall result
    overall_result: ValidationResultKind = ValidationResultKind.UNKNOWN
    
    # Provenance
    created_at_utc: float = field(default_factory=time.time)
    
    @classmethod
    def create(cls) -> ValidationTrace:
        """Create a new validation trace."""
        return cls(
            trace_id=f"trace:{uuid.uuid4().hex[:16]}",
        )
    
    def with_step(self, step_name: str, findings: Tuple[ValidationFinding, ...] = ()) -> ValidationTrace:
        """Return a copy with an additional validation step."""
        new_findings = dict(self.findings_by_step)
        new_findings[step_name] = findings
        return dataclass_replace(
            self,
            validation_steps=self.validation_steps + (step_name,),
            findings_by_step=new_findings,
        )


def dataclass_replace(instance: Any, **kwargs: Any) -> Any:
    """Simple dataclass replace helper for frozen instances."""
    return instance.__class__(**{**instance.__dict__, **kwargs})


__all__ = [
    "CounterfactualValidation",
    "ValidationResultKind",
    "ValidationFindingKind",
    "ValidationFinding",
    "ValidationTrace",
]