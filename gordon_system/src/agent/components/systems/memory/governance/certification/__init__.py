# Certification Domain - Governance Subsystem

"""
Certification: Complete memory system evaluation and certification.

The certification domain:
    
    - Aggregates all governance evidence
    - Evaluates architectural correctness
    - Produces certification decisions
    - Preserves audit history
    
Certification Laws:

    CERTIFICATION-LAW-001: Evaluate the complete Memory System
    CERTIFICATION-LAW-002: Aggregate governance evidence
    CERTIFICATION-LAW-003: Preserve supporting diagnostics
    CERTIFICATION-LAW-004: Preserve audit history
    CERTIFICATION-LAW-005: Expose explicit conditions
    CERTIFICATION-LAW-006: Never hide violations
    CERTIFICATION-LAW-007: Remain reproducible
    CERTIFICATION-LAW-008: Evaluation remains deterministic

Certification Input:
    
    - Integrity evaluation results
    - Compliance evaluation results
    - Audit history
    - Diagnostics information
    - All evidence records

Certification Output:
    
    - Certification decision (pass/fail/conditional)
    - Evidence summary
    - Violation report
    - Health metrics

Anti-Patterns Rejected:
    
    - Hiding violations
    - Non-deterministic certification
    - Hidden evaluation criteria
"""

from __future__ import annotations

from typing import Dict, List, Tuple, Optional, Any
from dataclasses import dataclass, field
from enum import Enum, auto
import time


# =============================================================================
# CERTIFICATION RESULTS
# =============================================================================


class CertificationResult(Enum):
    """Possible certification outcomes."""
    
    PASS = "pass"
    FAIL = "fail"
    CONDITIONAL = "conditional"


@dataclass(frozen=True)
class CertificationDecision:
    """A certification decision with supporting evidence."""
    
    result: CertificationResult
    confidence: float  # 0.0-1.0
    
    violations: Tuple[str, ...] = field(default_factory=tuple)
    recommendations: Tuple[str, ...] = field(default_factory=tuple)
    
    timestamp_utc: float = field(default_factory=time.time)
    revision_id: str = ""
    
    @property
    def is_certified(self) -> bool:
        """Check if memory passed certification."""
        return self.result == CertificationResult.PASS
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert decision to dictionary representation."""
        return {
            "result": self.result.value,
            "confidence": self.confidence,
            "violations": list(self.violations),
            "recommendations": list(self.recommendations),
            "timestamp_utc": self.timestamp_utc,
            "revision_id": self.revision_id,
        }


# =============================================================================
# CERTIFICATION DIAGNOSTICS
# =============================================================================


@dataclass(frozen=True)
class CertificationDiagnostics:
    """Diagnostic information from certification evaluation."""
    
    integrity_violations: int = 0
    compliance_violations: int = 0
    
    evidence_records_count: int = 0
    audit_events_count: int = 0
    
    # Timing
    start_time_utc: float = field(default_factory=time.time)
    end_time_utc: float = field(default_factory=time.time)
    
    @property
    def duration_seconds(self) -> float:
        """Get evaluation duration in seconds."""
        return self.end_time_utc - self.start_time_utc
    
    @property
    def total_violations(self) -> int:
        """Get total violation count."""
        return self.integrity_violations + self.compliance_violations


# =============================================================================
# EXPORTS
# =============================================================================

__all__ = [
    "CertificationResult",
    "CertificationDecision",
    "CertificationDiagnostics",
]