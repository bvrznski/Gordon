# Evaluation Governance - Phase 7.23
# ===================================

"""
Evaluation Governance for Gordon's Evaluation Reasoning subsystem.

Governance evaluates:
- Metric validity
- Assessment consistency
- Quality estimation accuracy
- Objective verification correctness
- Appraisal robustness
"""

from __future__ import annotations

import time
import uuid
from dataclasses import dataclass, field
from typing import Dict, List, Tuple, Optional, Any
from enum import Enum, auto


class GovernanceFindingKind(Enum):
    """Kinds of governance findings."""
    
    INVALID_METRIC = "invalid_metric"                 # Metric definition is invalid
    INCONSISTENT_ASSESSMENT = "inconsistent_assessment"  # Assessment conflicts with others
    LOW_QUALITY_ESTIMATION = "low_quality_estimation"   # Quality estimation lacks confidence
    MISSING_VERIFICATION_EVIDENCE = "missing_verification_evidence"  # Verification without evidence
    WEAK_APPRAISAL_SUPPORT = "weak_appraisal_support"   # Appraisal lacks sufficient findings


@dataclass(frozen=True)
class GovernanceFinding:
    """
    A governance finding.
    
    Each finding contains:
        - Finding kind and description
        - Affected evaluation component
        - Severity (high/medium/low)
        - Timestamps
    
    Findings remain explicit and inspectable.
    """
    
    finding_id: str                   # Unique finding identifier
    finding_kind: GovernanceFindingKind  # What type of governance issue?
    description: str                  # Human-readable description
    affected_component: Optional[str] = None  # Which evaluation component?
    severity: str = "medium"          # high/medium/low
    timestamp_utc: float = field(default_factory=time.time)


@dataclass(frozen=True)
class EvaluationGovernance:
    """
    An evaluation governance assessment.
    
    Governance contains:
        - Governance identity
        - Evaluated sessions (which evaluations were reviewed)
        - Findings (issues detected)
        - Violations (contract breaches)
        - Recommendations (how to fix issues)
        - Provenance tracking
    
    Governance remains observational and never modifies evaluation artifacts directly.
    """
    
    # Identity
    governance_id: str                # Unique governance identifier
    semantic_identity: str            # Semantic identity for traceability
    
    # Evaluated sessions
    evaluated_sessions: List[Dict[str, Any]] = field(default_factory=list)
    
    # Findings
    findings: List[GovernanceFinding] = field(default_factory=list)
    
    # Violations (contract breaches)
    violations: List[str] = field(default_factory=list)  # Violated laws/rules
    
    # Recommendations
    recommendations: Dict[str, Any] = field(default_factory=dict)
    
    # Governance outcome
    overall_status: str = "unknown"   # valid/invalid/pending_review
    
    # Metadata
    assessed_at_utc: float = field(default_factory=time.time)
    
    # Provenance
    source_governance_id: Optional[str] = None
    origin_context: str = "unknown"
    
    @property
    def finding_count(self) -> int:
        """Return number of findings."""
        return len(self.findings)
    
    @property
    def violation_count(self) -> int:
        """Return number of violations."""
        return len(self.violations)
    
    @classmethod
    def create(
        cls,
        semantic_identity: str,
        evaluated_sessions: List[Dict[str, Any]],
        findings: Optional[List[GovernanceFinding]] = None,
        origin_context: str = "unknown",
        source_governance_id: Optional[str] = None,
    ) -> EvaluationGovernance:
        """Create a new evaluation governance assessment."""
        return cls(
            governance_id=f"governance:{uuid.uuid4().hex[:16]}",
            semantic_identity=semantic_identity,
            evaluated_sessions=list(evaluated_sessions),
            findings=list(findings or []),
            origin_context=origin_context,
            source_governance_id=source_governance_id,
            assessed_at_utc=time.time(),
        )


def dataclass_replace(instance: Any, **kwargs: Any) -> Any:
    """Simple dataclass replace helper for frozen instances."""
    return instance.__class__(**{**instance.__dict__, **kwargs})


__all__ = [
    "GovernanceFindingKind",
    "GovernanceFinding",
    "EvaluationGovernance",
]