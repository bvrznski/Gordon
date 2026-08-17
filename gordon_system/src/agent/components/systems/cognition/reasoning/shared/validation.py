# Reasoning Validation - Phase 7.0
# ==================================

"""
Canonical Validation Contract.

Validation evaluates reasoning without modifying it directly.
"""

from __future__ import annotations

import time
import uuid
from dataclasses import dataclass, field
from typing import Dict, List, Tuple, Optional, Any


@dataclass(frozen=True)
class ReasoningValidation:
    """
    Validation of a reasoning session or pipeline.
    
    Validation evaluates:
        - Logical consistency
        - Ontology compatibility
        - Assumption completeness
        - Trace completeness
        - Unsupported conclusions
    
    Validation remains observational;
    it never modifies the reasoning being validated.
    """
    
    # Identity
    validation_id: str                      # Unique identifier
    
    # Target
    evaluated_session: str                  # Which session/pipeline was evaluated?
    
    # Validation checks performed
    validation_checks: Dict[str, bool] = field(default_factory=dict)
    # e.g., {"consistency": True, "trace_complete": True}
    
    # Findings
    findings: Tuple[Dict[str, Any], ...] = ()  # List of finding dicts
    
    # Recommendations
    recommendations: Tuple[str, ...] = ()
    # Suggestions for improvement
    
    # Overall assessment
    is_valid: bool = False                  # Passed all checks?
    validity_reasons: Tuple[str, ...] = ()  # Why/why not?
    
    # Diagnostics
    diagnostics: Dict[str, Any] = field(default_factory=dict)
    
    # Timing
    validated_at_utc: float = field(default_factory=time.time)
    
    @property
    def check_count(self) -> int:
        """Total number of checks performed."""
        return len(self.validation_checks)
    
    @property
    def passed_check_count(self) -> int:
        """Number of checks that passed."""
        return sum(1 for v in self.validation_checks.values() if v)
    
    @classmethod
    def create(
        cls,
        evaluated_session: str,
        check_names: Optional[List[str]] = None,
    ) -> ReasoningValidation:
        """Create a new validation with initial checks."""
        initial_checks = {name: False for name in (check_names or [])}
        return cls(
            validation_id=f"validation:{uuid.uuid4().hex[:16]}",
            evaluated_session=evaluated_session,
            validation_checks=initial_checks,
        )
    
    def record_check(self, check_name: str, passed: bool, details: Optional[Dict[str, Any]] = None) -> "ReasoningValidation":
        """Record result of a validation check."""
        new_checks = dict(self.validation_checks)
        new_checks[check_name] = passed
        
        findings_list = list(self.findings)
        if details:
            finding = {
                "check": check_name,
                "passed": passed,
                **(details or {})
            }
            findings_list.append(finding)
        
        return dataclass_replace(
            self,
            validation_checks=new_checks,
            findings=tuple(findings_list),
        )
    
    def finalize(self, is_valid: bool, reasons: Optional[List[str]] = None) -> "ReasoningValidation":
        """Mark validation as complete."""
        return dataclass_replace(
            self,
            is_valid=is_valid,
            validity_reasons=tuple(reasons or []),
            diagnostics={
                **self.diagnostics,
                "completed_at_utc": time.time(),
            },
        )


@dataclass(frozen=True)
class ReasoningFailure:
    """
    A reasoning failure with diagnostic information.
    
    Failures may include:
        - Insufficient knowledge
        - Contradictory assumptions
        - Timeout
        - Resource exhaustion
        - Unsupported inference
    
    Failures remain explicit; they don't silently terminate sessions.
    """
    
    # Identity
    failure_id: str                         # Unique identifier
    
    # Failure details
    failure_kind: str                       # What type of failure?
    affected_reasoning: str                 # Which reasoning failed?
    
    # Diagnostics
    diagnostics: Dict[str, Any] = field(default_factory=dict)
    error_message: Optional[str] = None     # Human-readable description
    
    # Recovery options
    recovery_options: Tuple[str, ...] = ()  # How might this be recovered?
    
    # Timing
    occurred_at_utc: float = field(default_factory=time.time)
    
    # Provenance
    provenance: Dict[str, str] = field(default_factory=dict)
    
    @property
    def is_recoverable(self) -> bool:
        """Check if recovery is possible."""
        return len(self.recovery_options) > 0
    
    @classmethod
    def create(
        cls,
        failure_kind: str,
        affected_reasoning: str,
        diagnostics: Optional[Dict[str, Any]] = None,
        error_message: Optional[str] = None,
        recovery_options: Optional[List[str]] = None,
    ) -> ReasoningFailure:
        """Create a new failure record."""
        return cls(
            failure_id=f"failure:{uuid.uuid4().hex[:16]}",
            failure_kind=failure_kind,
            affected_reasoning=affected_reasoning,
            diagnostics=diagnostics or {},
            error_message=error_message,
            recovery_options=tuple(recovery_options or []),
            occurred_at_utc=time.time(),
        )


@dataclass(frozen=True)
class ReasoningGovernance:
    """
    Governance evaluation of reasoning.
    
    Governance evaluates:
        - Unsupported conclusions
        - Trace completeness
        - Reasoning consistency
        - Non-determinism detection
        - Resource usage compliance
    
    Governance remains observational;
    it never modifies the reasoning being governed.
    """
    
    # Identity
    governance_id: str                      # Unique identifier
    
    # Evaluated sessions
    evaluated_sessions: Tuple[str, ...] = ()
    
    # Findings
    findings: Tuple[Dict[str, Any], ...] = ()
    
    # Violations (policy breaches)
    violations: Tuple[Dict[str, Any], ...] = ()
    
    # Recommendations
    recommendations: Tuple[str, ...] = ()
    
    # Overall assessment
    is_compliant: bool = False              # Passed all governance checks?
    
    # Timing
    evaluated_at_utc: float = field(default_factory=time.time)
    
    @property
    def violation_count(self) -> int:
        """Count of governance violations."""
        return len(self.violations)
    
    @classmethod
    def create(
        cls,
        session_ids: Optional[List[str]] = None,
    ) -> ReasoningGovernance:
        """Create a new governance evaluation."""
        return cls(
            governance_id=f"governance:{uuid.uuid4().hex[:16]}",
            evaluated_sessions=tuple(session_ids or []),
        )
    
    def record_violation(self, violation: Dict[str, Any]) -> "ReasoningGovernance":
        """Record a governance violation."""
        return dataclass_replace(
            self,
            violations=self.violations + (violation,),
        )


def dataclass_replace(instance: Any, **kwargs: Any) -> Any:
    """Simple dataclass replace helper for frozen instances."""
    return instance.__class__(**{**instance.__dict__, **kwargs})


__all__ = [
    "ReasoningValidation", 
    "ReasoningFailure",
    "ReasoningGovernance",
]