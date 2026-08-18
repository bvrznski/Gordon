# Monitoring Validation Contract - Phase 7.22
# ===========================================

"""
Canonical Monitoring Validation.

Validation verifies monitoring results for correctness and completeness.
"""

from __future__ import annotations

import time
import uuid
from dataclasses import dataclass, field
from typing import Dict, List, Tuple, Optional, Any
from enum import Enum, auto


class ValidationStatus(Enum):
    """Status of validation."""
    
    PENDING = "pending"                         # Not yet validated
    VALIDATING = "validating"                   # Currently validating
    VALID = "valid"                             # Passed all checks
    INVALID = "invalid"                         # Failed validation
    INCONCLUSIVE = "inconclusive"               # Could not determine


@dataclass(frozen=True)
class ValidationFinding:
    """
    A finding from the validation process.
    """
    
    # Identity
    finding_id: str                           # Unique finding identifier
    
    # Finding details
    category: str                             # What kind of finding?
    severity: str = "info"                    # info, warning, error
    description: str = ""                     # Human-readable explanation
    
    # Evidence
    supporting_observations: List[str] = field(default_factory=list)
    
    # Timing
    detected_at_utc: float = field(default_factory=time.time)


@dataclass(frozen=True)
class MonitoringValidation:
    """
    Validation results for a monitoring session.
    
    A validation result contains:
        - Identity and provenance
        - Evaluated sessions
        - Findings
        - Violations
        - Recommendations
    
    Validation remains observational (never modifies artifacts).
    """
    
    # Identity
    validation_id: str                        # Unique validation identifier
    
    # Evaluated session
    evaluated_session_ids: List[str] = field(default_factory=list)  # Session IDs validated
    
    # Validation results
    validation_status: ValidationStatus = ValidationStatus.PENDING
    
    # Findings
    findings: List[ValidationFinding] = field(default_factory=list)
    
    # Violations (contract violations)
    violations: List[str] = field(default_factory=list)  # Violation descriptions
    
    # Recommendations
    recommendations: List[str] = field(default_factory=list)
    
    # Validation metrics
    observations_validated: int = 0
    anomalies_checked: int = 0
    state_consistency_verified: bool = False
    
    # Timing
    started_at_utc: float = field(default_factory=time.time)
    completed_at_utc: Optional[float] = None
    
    @property
    def is_valid(self) -> bool:
        """Check if validation passed."""
        return self.validation_status == ValidationStatus.VALID
    
    @property
    def has_findings(self) -> bool:
        """Check if any findings exist."""
        return len(self.findings) > 0
    
    @property
    def has_violations(self) -> bool:
        """Check if any violations exist."""
        return len(self.violations) > 0
    
    def add_finding(
        self,
        category: str,
        severity: str = "info",
        description: str = "",
        supporting_observations: Optional[List[str]] = None,
    ) -> MonitoringValidation:
        """Add a validation finding."""
        new_findings = list(self.findings)
        
        new_findings.append(ValidationFinding(
            finding_id=f"finding:{uuid.uuid4().hex[:16]}",
            category=category,
            severity=severity,
            description=description,
            supporting_observations=supporting_observations or [],
            detected_at_utc=time.time(),
        ))
        
        return dataclass_replace(
            self,
            findings=new_findings,
        )
    
    def add_violation(self, violation: str) -> MonitoringValidation:
        """Add a contract violation."""
        new_violations = list(self.violations)
        if violation not in new_violations:
            new_violations.append(violation)
        
        return dataclass_replace(
            self,
            violations=new_violations,
            validation_status=ValidationStatus.INVALID,
        )
    
    def add_recommendation(self, recommendation: str) -> MonitoringValidation:
        """Add a validation recommendation."""
        new_recommendations = list(self.recommendations)
        if recommendation not in new_recommendations:
            new_recommendations.append(recommendation)
        
        return dataclass_replace(
            self,
            recommendations=new_recommendations,
        )
    
    def mark_valid(self) -> MonitoringValidation:
        """Mark validation as passed."""
        return dataclass_replace(
            self,
            validation_status=ValidationStatus.VALID,
        )
    
    def mark_inconclusive(self, reason: str = "unknown") -> MonitoringValidation:
        """Mark validation as inconclusive."""
        return dataclass_replace(
            self,
            validation_status=ValidationStatus.INCONCLUSIVE,
        )
    
    def complete(self) -> MonitoringValidation:
        """Complete the validation process."""
        return dataclass_replace(
            self,
            completed_at_utc=time.time(),
        )
    
    @classmethod
    def create(
        cls,
        evaluated_session_ids: Optional[List[str]] = None,
    ) -> MonitoringValidation:
        """Create a new validation session."""
        return cls(
            validation_id=f"validation:{uuid.uuid4().hex[:16]}",
            evaluated_session_ids=evaluated_session_ids or [],
            started_at_utc=time.time(),
        )


def dataclass_replace(instance: Any, **kwargs: Any) -> Any:
    """Simple dataclass replace helper for frozen instances."""
    return instance.__class__(**{**instance.__dict__, **kwargs})


__all__ = [
    "MonitoringValidation",
    "ValidationFinding",
    "ValidationStatus",
]