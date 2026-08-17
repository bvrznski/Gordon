# Semantic Validation - Phase 7.10
# =================================

"""
Canonical Semantic Validation contracts.

Semantic validation is observational - it does NOT modify semantic artifacts directly.
It evaluates:
    - Ontology correctness
    - Relation consistency
    - Inheritance correctness
    - Constraint preservation
    - Concept integrity

Validation remains independent and inspectable.
"""

from __future__ import annotations

import time
import uuid
from dataclasses import dataclass, field
from typing import Dict, List, Tuple, Optional, Any
from enum import Enum, auto


@dataclass(frozen=True)
class SemanticValidation:
    """
    Semantic validation result.
    
    A SemanticValidation contains:
        - Validation identity
        - Evaluated semantic artifacts
        - Check results
        - Findings
        - Provenance tracking
    
    Validation remains observational - it never modifies artifacts directly.
    """
    
    # Identity
    validation_id: str                      # Unique identifier
    
    # Reasoning goal
    reasoning_goal: str                     # What was validated?
    
    # Evaluated artifacts
    evaluated_artifacts: Tuple[str, ...] = ()
    
    # Validation checks (name -> passed)
    validation_checks: Dict[str, bool] = field(default_factory=dict)
    
    # Findings
    findings: Tuple[ValidationFinding, ...] = ()
    
    # State
    state: str = "created"
    
    # Timing
    created_at_utc: float = field(default_factory=time.time)
    completed_at_utc: Optional[float] = None
    
    @property
    def artifact_count(self) -> int:
        """Count of evaluated artifacts."""
        return len(self.evaluated_artifacts)
    
    @property
    def check_count(self) -> int:
        """Count of validation checks."""
        return len(self.validation_checks)
    
    @property
    def all_passed(self) -> bool:
        """Check if all validation checks passed."""
        return all(self.validation_checks.values())
    
    @classmethod
    def create(
        cls,
        reasoning_goal: str,
        artifacts: Optional[List[str]] = None,
    ) -> SemanticValidation:
        """Create a new semantic validation record."""
        return cls(
            validation_id=f"validation:{uuid.uuid4().hex[:16]}",
            reasoning_goal=reasoning_goal,
            evaluated_artifacts=tuple(artifacts or []),
        )
    
    def record_check(self, check_name: str, passed: bool) -> SemanticValidation:
        """Record a validation check result."""
        new_checks = dict(self.validation_checks)
        new_checks[check_name] = passed
        return dataclass_replace(
            self,
            validation_checks=new_checks,
        )
    
    def add_findings(self, findings: List[ValidationFinding]) -> SemanticValidation:
        """Add validation findings."""
        new_findings = tuple(self.findings) + tuple(findings)
        return dataclass_replace(
            self,
            findings=new_findings,
        )
    
    def complete(self) -> SemanticValidation:
        """Mark validation as completed."""
        return dataclass_replace(
            self,
            state="completed",
            completed_at_utc=time.time(),
        )


@dataclass(frozen=True)
class ValidationFinding:
    """
    A finding from semantic validation.
    """
    
    finding_id: str                         # Unique identifier
    finding_type: str                       # e.g., "inconsistent", "ambiguous"
    message: str                            # Finding description
    severity: str = "info"                  # info, warning, error
    
    @classmethod
    def create_inconsistency(cls, details: str) -> ValidationFinding:
        """Create an inconsistency finding."""
        return cls(
            finding_id=f"finding:{uuid.uuid4().hex[:16]}",
            finding_type="inconsistent",
            message=f"Inconsistency detected: {details}",
            severity="error",
        )
    
    @classmethod
    def create_ambiguous(cls, details: str) -> ValidationFinding:
        """Create an ambiguity finding."""
        return cls(
            finding_id=f"finding:{uuid.uuid4().hex[:16]}",
            finding_type="ambiguous",
            message=f"Ambiguity detected: {details}",
            severity="warning",
        )


def dataclass_replace(instance: Any, **kwargs: Any) -> Any:
    """Simple dataclass replace helper for frozen instances."""
    return instance.__class__(**{**instance.__dict__, **kwargs})


__all__ = [
    "SemanticValidation",
    "ValidationFinding",
]