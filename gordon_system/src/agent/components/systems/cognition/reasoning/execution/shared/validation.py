# Execution Reasoning Validation - Phase 7.21
# ===========================================

"""
Canonical Execution Validation for Phase 7.21.

Execution validation is observational - it evaluates execution correctness,
authorization integrity, resource synchronization, rollback safety,
policy compliance, and diagnostics without modifying execution artifacts.
"""

from __future__ import annotations

import time
import uuid
from dataclasses import dataclass, field
from typing import Dict, List, Tuple, Optional, Any
from enum import Enum, auto


class ValidationFindingKind(Enum):
    """Kinds of validation findings."""
    
    AUTHORIZATION_INTEGRITY = "authorization_integrity"       # Authorization state is invalid
    SYNCHRONIZATION_VIOLATION = "synchronization_violation"     # Synchronization constraints violated
    ROLLBACK_INCONSISTENCY = "rollback_inconsistency"           # Rollback state inconsistent
    POLICY_VIOLATION = "policy_violation"                       # Policy constraint not satisfied
    DEADLOCK_DETECTED = "deadlock_detected"                     # Potential deadlock detected


@dataclass(frozen=True)
class ExecutionValidation:
    """
    Execution Validation provides observational evaluation.
    
    Validation evaluates:
        - Execution correctness
        - Authorization integrity
        - Resource synchronization  
        - Rollback safety
        - Policy compliance
        - Diagnostics
    
    Validation remains observational and does not modify execution artifacts.
    """
    
    # Identity
    validation_identity: str                    # Unique validation identifier
    
    # Evaluated sessions
    evaluated_sessions: Tuple[str, ...]         # IDs of sessions validated
    
    # Findings
    findings: Tuple[ValidationFinding, ...] = ()
    
    # Validation state
    is_valid: bool = True                       # Overall validity
    
    @classmethod
    def create(
        cls,
        evaluated_sessions: Tuple[str, ...],
        findings: Tuple[ValidationFinding, ...] = (),
    ) -> ExecutionValidation:
        """Create a new execution validation."""
        return cls(
            validation_identity=f"validation:{uuid.uuid4().hex[:16]}",
            evaluated_sessions=evaluated_sessions,
            findings=findings,
            is_valid=len(findings) == 0 or all(f.finding_kind != ValidationFindingKind.DEADLOCK_DETECTED for f in findings),
        )
    
    @property
    def total_findings(self) -> int:
        """Total number of findings."""
        return len(self.findings)


@dataclass(frozen=True)
class ValidationFinding:
    """
    A single validation finding.
    
    Each finding includes kind, severity, and diagnostic information.
    """
    
    # Identity
    finding_identity: str                       # Unique finding identifier
    
    # Finding details
    finding_kind: ValidationFindingKind         # What type of issue?
    description: str                            # Human-readable description
    
    # Severity (warning, error, critical)
    severity: str = "warning"                   # Issue severity level
    
    @classmethod
    def create(
        cls,
        finding_kind: ValidationFindingKind,
        description: str,
        severity: str = "warning",
    ) -> ValidationFinding:
        """Create a new validation finding."""
        return cls(
            finding_identity=f"finding:{uuid.uuid4().hex[:16]}",
            finding_kind=finding_kind,
            description=description,
            severity=severity,
        )


@dataclass(frozen=True)
class ValidationTrace:
    """
    Trace of validation events for inspection.
    
    Enables replay and verification of validation decisions.
    """
    
    # Identity
    trace_identity: str
    
    # Validation steps
    validation_steps: Tuple[ValidationStep, ...]
    
    # Final result
    final_result: str                           # "valid", "invalid", "inconclusive"
    
    @classmethod
    def create(
        cls,
        validation_steps: Tuple[ValidationStep, ...],
        final_result: str = "valid",
    ) -> ValidationTrace:
        """Create a new validation trace."""
        return cls(
            trace_identity=f"val_trace:{uuid.uuid4().hex[:16]}",
            validation_steps=validation_steps,
            final_result=final_result,
        )


@dataclass(frozen=True)
class ValidationStep:
    """
    A single step in the validation process.
    """
    
    # Identity
    step_identity: str
    
    # Check name
    check_name: str                             # e.g., "authorization_check", "synchronization_check"
    
    # Result
    result: bool                                # Pass/fail
    diagnostic_message: Optional[str] = None
    
    @classmethod
    def create(
        cls,
        check_name: str,
        result: bool,
        diagnostic_message: Optional[str] = None,
    ) -> ValidationStep:
        """Create a new validation step."""
        return cls(
            step_identity=f"val_step:{uuid.uuid4().hex[:16]}",
            check_name=check_name,
            result=result,
            diagnostic_message=diagnostic_message,
        )


def dataclass_replace(instance: Any, **kwargs: Any) -> Any:
    """Simple dataclass replace helper for frozen instances."""
    return instance.__class__(**{**instance.__dict__, **kwargs})


__all__ = [
    "ExecutionValidation",
    "ValidationFindingKind",
    "ValidationFinding",
    "ValidationTrace",
    "ValidationStep",
]