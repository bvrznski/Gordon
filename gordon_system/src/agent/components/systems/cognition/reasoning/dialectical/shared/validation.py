# Dialectical Validation - Phase 7.17
# ===================================

"""
Canonical Dialectical Validation Contract.

Dialectical Validation is observational - it evaluates without modifying dialectics directly.
"""

from __future__ import annotations

import time
import uuid
from dataclasses import dataclass, field
from typing import Dict, List, Tuple, Optional, Any


@dataclass(frozen=True)
class DialecticalValidationResult:
    """
    A validation result for a dialectical process.

    Validation evaluates:
        - Argument quality (are arguments well-formed?)
        - Counterargument completeness (were all counterarguments considered?)
        - Conflict analysis validity (was conflict analysis correct?)
        - Synthesis robustness (is the synthesis defensible?)
        - Consensus stability (is the consensus stable?)

    Validation remains observational; it never modifies dialectical artifacts directly.
    """

    # Identity
    validation_id: str                      # Unique identifier

    # Evaluated sessions
    evaluated_sessions: Tuple[str, ...] = ()

    # Findings (what was found?)
    findings: Tuple[Dict[str, Any], ...] = ()

    # Validation checks passed/failed
    check_results: Tuple[Dict[str, Any], ...] = ()

    # Overall assessment
    is_valid: bool = False                  # Did it pass all validation checks?

    # Timing
    validated_at_utc: float = field(default_factory=time.time)

    @property
    def failed_checks(self) -> Tuple[Dict[str, Any], ...]:
        """Get only failed validation checks."""
        return tuple(c for c in self.check_results if not c.get("passed", False))

    @classmethod
    def create(
        cls,
        session_ids: Optional[List[str]] = None,
    ) -> DialecticalValidationResult:
        """Create a new validation result."""
        return cls(
            validation_id=f"dialectical_validation:{uuid.uuid4().hex[:16]}",
            evaluated_sessions=tuple(session_ids or []),
        )

    def with_check(self, check_name: str, passed: bool, details: Optional[Dict[str, Any]] = None) -> DialecticalValidationResult:
        """Record a validation check result."""
        check_result = {
            "check_name": check_name,
            "passed": passed,
            "details": details or {},
        }
        return dataclass_replace(
            self,
            check_results=self.check_results + (check_result,),
        )

    def with_finding(self, finding: Dict[str, Any]) -> DialecticalValidationResult:
        """Add a validation finding."""
        return dataclass_replace(
            self,
            findings=self.findings + (finding,),
        )


def dataclass_replace(instance: Any, **kwargs: Any) -> Any:
    """Simple dataclass replace helper for frozen instances."""
    return instance.__class__(**{**instance.__dict__, **kwargs})


__all__ = [
    "DialecticalValidationResult",
]