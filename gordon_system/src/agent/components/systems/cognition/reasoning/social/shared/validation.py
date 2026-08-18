# Social Validation - Phase 7.32
# ==============================

"""
Canonical Social Validation.

Validation is observational only:
- Validates social reasoning results
- Does NOT modify social artifacts directly
- Produces findings and recommendations
"""

from __future__ import annotations

import time
import uuid
from dataclasses import dataclass, field
from typing import Dict, List, Tuple, Optional, Any


@dataclass(frozen=True)
class SocialValidation:
    """
    Social validation result.
    
    Validation is OBSERVATIONAL - it only evaluates social artifacts,
    never modifies them directly.
    """
    
    # Identity
    validation_id: str                        # Unique identifier
    
    # Evaluated artifacts
    evaluated_sessions: Tuple[str, ...] = ()  # Session IDs that were validated
    
    # Findings (what was discovered)
    findings: Tuple[Dict[str, Any], ...] = ()
    
    # Violations (contract violations detected)
    violations: Tuple[Dict[str, Any], ...] = ()
    
    # Recommendations
    recommendations: Tuple[str, ...] = ()
    
    # Metadata
    created_at_utc: float = field(default_factory=time.time)
    validator_type: str = "default"
    
    @property
    def finding_count(self) -> int:
        """Count of validation findings."""
        return len(self.findings)
    
    @property
    def has_violations(self) -> bool:
        """Check if any violations were found."""
        return len(self.violations) > 0
    
    @classmethod
    def create(cls, sessions: List[str]) -> SocialValidation:
        """Create a new validation result."""
        return cls(
            validation_id=f"validation:{uuid.uuid4().hex[:16]}",
            evaluated_sessions=tuple(sessions),
            created_at_utc=time.time(),
        )
    
    def with_finding(self, finding: Dict[str, Any]) -> SocialValidation:
        """Return a copy with an additional finding."""
        return dataclass_replace(
            self,
            findings=self.findings + (finding,),
        )
    
    def with_violation(self, violation: Dict[str, Any]) -> SocialValidation:
        """Return a copy with an additional violation."""
        return dataclass_replace(
            self,
            violations=self.violations + (violation,),
        )


@dataclass(frozen=True)
class ValidationFinding:
    """
    A single validation finding.
    
    Includes:
        - Finding type (warning, error, etc.)
        - Description
        - Affected artifact
        - Severity level
    """
    
    finding_id: str                           # Unique identifier
    finding_type: str                         # warning, error, info
    description: str                          # What was found?
    affected_artifact: str                    # Which artifact is affected?
    severity: float = 0.5                     # 0.0 to 1.0
    
    @property
    def is_error(self) -> bool:
        """Check if this is an error-level finding."""
        return self.severity >= 0.8
    
    @property
    def is_warning(self) -> bool:
        """Check if this is a warning-level finding."""
        return 0.5 <= self.severity < 0.8


def dataclass_replace(instance: Any, **kwargs: Any) -> Any:
    """Simple dataclass replace helper for frozen instances."""
    return instance.__class__(**{**instance.__dict__, **kwargs})


__all__ = [
    "SocialValidation",
    "ValidationFinding",
]