# Executive Validation - Phase 7.30
# ==================================

"""
Executive Validation Module.

Validation evaluates executive decisions without modifying them directly.
"""

from __future__ import annotations

import time
import uuid
from dataclasses import dataclass, field
from typing import Dict, List, Tuple, Optional, Any

from .shared import (
    ExecutiveDescriptor,
    ExecutiveState,
    ExecutiveSet,
    ValidationOutcome,
)


@dataclass(frozen=True)
class ExecutiveValidation:
    """
    Validation of executive decisions.
    
    Validation evaluates:
        - Coordination correctness
        - Arbitration quality  
        - Directive correctness
        - Synchronization quality
    
    Validation remains observational and never modifies executive artifacts directly.
    """
    
    # Identity
    validation_id: str                          # Unique identifier
    
    # Evaluated session
    evaluated_session_id: str                   # Which executive session?
    executive_descriptor: ExecutiveDescriptor   # Descriptor of the session
    
    # Evaluation results
    outcome: ValidationOutcome = ValidationOutcome.VALID  # Passed/failed/warning
    
    # Findings (what was correct?)
    findings: Tuple[Dict[str, Any], ...] = ()   # Positive findings
    
    # Issues (what needs attention?)
    issues: Tuple[Dict[str, Any], ...] = ()     # Minor concerns
    
    # Failures (what went wrong?)
    failures: Tuple[Dict[str, Any], ...] = ()   # Critical issues
    
    # Timing
    validated_at_utc: float = field(default_factory=time.time)
    
    @property
    def is_valid(self) -> bool:
        """Check if validation passed."""
        return self.outcome == ValidationOutcome.VALID
    
    @property
    def issue_count(self) -> int:
        """Count of issues found."""
        return len(self.issues)
    
    @property
    def failure_count(self) -> int:
        """Count of failures found."""
        return len(self.failures)
    
    @classmethod
    def create(
        cls,
        evaluated_session_id: str,
        executive_descriptor: ExecutiveDescriptor,
    ) -> "ExecutiveValidation":
        """Create a new validation record."""
        return cls(
            validation_id=f"exec_validation:{uuid.uuid4().hex[:16]}",
            evaluated_session_id=evaluated_session_id,
            executive_descriptor=executive_descriptor,
        )
    
    def with_issue(self, issue: Dict[str, Any]) -> "ExecutiveValidation":
        """Record an issue found during validation."""
        return dataclass_replace(
            self,
            issues=self.issues + (issue,),
        )
    
    def with_failure(self, failure: Dict[str, Any]) -> "ExecutiveValidation":
        """Record a failure found during validation."""
        new_failures = self.failures + (failure,)
        return dataclass_replace(
            self,
            failures=new_failures,
            outcome=ValidationOutcome.INVALID,
        )
    
    def finalize_with_outcome(self, outcome: ValidationOutcome) -> "ExecutiveValidation":
        """Finalize validation with a specific outcome."""
        if self.failure_count > 0:
            outcome = ValidationOutcome.INVALID
        elif self.issue_count > 0 and outcome == ValidationOutcome.VALID:
            outcome = ValidationOutcome.WARNING
        
        return dataclass_replace(
            self,
            outcome=outcome,
        )


@dataclass(frozen=True)
class ValidationRule:
    """
    A validation rule for executive decisions.
    
    Rules define what constitutes valid vs invalid executive behavior.
    """
    
    # Identity
    rule_id: str                                # Unique identifier
    
    # Rule description
    name: str                                   # Human-readable name
    description: str                            # What does this check?
    
    # Validation logic (returns True if valid)
    validation_function: str                    # Function name or description
    
    # Scope
    applies_to_subsystems: Tuple[str, ...] = ()  # Which subsystems? Empty = all
    
    @classmethod
    def create(
        cls,
        rule_id: str,
        name: str,
        description: str,
    ) -> "ValidationRule":
        """Create a new validation rule."""
        return cls(
            rule_id=rule_id,
            name=name,
            description=description,
        )


@dataclass(frozen=True)
class Validator:
    """
    Global executive validator that ensures correctness.
    
    The validator ensures that all executive decisions conform to
    specified rules and policies without modifying them directly.
    """
    
    # Identity
    validator_id: str                           # Unique identifier
    
    # Policy
    validation_policy: str                      # Policy name
    
    # Rules (by ID)
    rules: Dict[str, ValidationRule] = field(default_factory=dict)
    
    # Validation history
    completed_validations: Tuple[Dict[str, Any], ...] = field(default_factory=tuple)
    
    # Metrics
    total_validated: int = 0
    valid_count: int = 0
    
    @classmethod
    def create(
        cls,
        policy: str = "default",
    ) -> "Validator":
        """Create a new validator."""
        return cls(
            validator_id=f"validator:{uuid.uuid4().hex[:16]}",
            validation_policy=policy,
        )
    
    def register_rule(self, rule: ValidationRule) -> "Validator":
        """Register a new validation rule."""
        new_rules = dict(self.rules)
        new_rules[rule.rule_id] = rule
        return dataclass_replace(self, rules=new_rules)


def dataclass_replace(instance: Any, **kwargs: Any) -> Any:
    """Simple dataclass replace helper for frozen instances."""
    return instance.__class__(**{**instance.__dict__, **kwargs})


__all__ = [
    "ExecutiveValidation",
    "ValidationRule", 
    "Validator",
]
