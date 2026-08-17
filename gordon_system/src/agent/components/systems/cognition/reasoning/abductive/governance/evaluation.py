# Abduction Governance Evaluation - Phase 7.3
# ==========================================

"""
Governance evaluation for abductive reasoning.

This module provides:
    - Governance session management
    - Finding detection and reporting
    - Health metrics collection
"""

from __future__ import annotations

import time
import uuid
from dataclasses import dataclass, field
from typing import Dict, List, Tuple, Optional, Any
from enum import Enum, auto


class GovernanceRule(Enum):
    """Governance rules for abductive reasoning."""
    
    EVIDENCE_LAW_001 = "evidence_law_001"  # Evidence must have explicit origin
    EVIDENCE_LAW_002 = "evidence_law_002"  # Quality must be explicit
    EVIDENCE_LAW_003 = "evidence_law_003"  # Uncertainty must be explicit
    EVIDENCE_LAW_004 = "evidence_law_004"  # Provenance must be complete
    
    EXPLANATION_LAW_001 = "explanation_law_001"  # Must reference supporting evidence
    EXPLANATION_LAW_002 = "explanation_law_002"  # Assumptions must be explicit
    EXPLANATION_LAW_003 = "explanation_law_003"  # Scope must be explicit
    EXPLANATION_LAW_004 = "explanation_law_004"  # Provenance must be complete
    
    CAUSAL_LAW_001 = "causal_law_001"      # Causation must differ from correlation
    CAUSAL_LAW_002 = "causal_law_002"      # Causal assumptions must be explicit
    CAUSAL_LAW_003 = "causal_law_003"      # Alternative causal mechanisms must be representable
    
    GOVERNANCE_LAW_001 = "governance_law_001"  # Must not modify abductive artifacts directly


class GovernanceFindingKind(Enum):
    """Kinds of governance findings."""
    
    EVIDENCE_FABRICATION = "evidence_fabrication"       # Evidence was fabricated
    CAUSAL_ERROR = "causal_error"                       # Causal relationship is incorrect
    PROVENANCE_INCOMPLETE = "provenance_incomplete"     # Provenance tracking incomplete
    VIOLATION = "violation"                             # Rule violation detected
    WARNING = "warning"                                 # Non-critical issue


@dataclass(frozen=True)
class GovernanceFinding:
    """
    A single governance finding.
    
    Each finding describes a specific governance issue identified during
    evaluation of abductive reasoning artifacts.
    """
    
    # Identity
    finding_id: str                           # Unique identifier
    
    # Content
    finding_kind: GovernanceFindingKind       # What kind of finding?
    description: str                          # Detailed explanation
    
    # Assessment
    severity: str = "warning"                 # "info", "warning", or "error"
    confidence: float = 1.0                   # Confidence in the finding
    
    @property
    def is_critical(self) -> bool:
        """Check if this finding is critical."""
        return self.severity == "error"
    
    @classmethod
    def create(
        cls,
        finding_kind: GovernanceFindingKind,
        description: str,
        severity: str = "warning",
        confidence: float = 1.0,
    ) -> GovernanceFinding:
        """Create a new governance finding."""
        return cls(
            finding_id=f"finding:{uuid.uuid4().hex[:16]}",
            finding_kind=finding_kind,
            description=description,
            severity=severity,
            confidence=confidence,
        )


@dataclass(frozen=True)
class AbductionGovernance:
    """
    Complete governance evaluation record.
    
    This provides:
        - Evaluated sessions
        - All findings identified
        - Violations detected
        - Recommendations
    
    Governance remains observational (never modifies abductive artifacts).
    """
    
    # Identity
    governance_id: str                        # Unique identifier
    
    # Evaluation scope
    evaluated_sessions: Tuple[str, ...] = ()  # Session IDs evaluated
    
    # Findings
    findings: Tuple[GovernanceFinding, ...] = ()  # All findings
    violations: Tuple[str, ...] = ()            # Rule violations detected
    
    # Recommendations
    recommendations: Tuple[Dict[str, Any], ...] = ()  # Improvement suggestions
    
    @property
    def check_pass_rate(self) -> float:
        """Calculate percentage of checks that passed."""
        if not self.evaluated_sessions:
            return 1.0
        
        total_checks = len(self.findings) + len(self.violations)
        passed = max(0, len(self.evaluated_sessions) - total_checks)
        return passed / len(self.evaluated_sessions)
    
    @property
    def has_violations(self) -> bool:
        """Check if any violations were detected."""
        return len(self.violations) > 0
    
    @property
    def violation_count(self) -> int:
        """Count of rule violations."""
        return len(self.violations)
    
    @classmethod
    def create(
        cls,
        evaluated_session_ids: List[str],
        findings: Optional[List[GovernanceFinding]] = None,
        violations: Optional[List[str]] = None,
        recommendations: Optional[List[Dict[str, Any]]] = None,
    ) -> AbductionGovernance:
        """Create a new governance evaluation record."""
        return cls(
            governance_id=f"governance:{uuid.uuid4().hex[:16]}",
            evaluated_sessions=tuple(evaluated_session_ids),
            findings=tuple(findings or []),
            violations=tuple(violations or []),
            recommendations=tuple(recommendations or []),
        )


@dataclass(frozen=True)
class GovernanceHealth:
    """
    Health metrics for abductive governance.
    
    This provides:
        - Session evaluation counts
        - Pass rates by category
        - Trend analysis
    
    Health remains descriptive (never modifies governance state).
    """
    
    # Identity
    health_id: str                            # Unique identifier
    
    # Metrics
    total_sessions_evaluated: int = 0         # Total sessions evaluated
    successful_evaluations: int = 0           # Passed all checks
    failed_evaluations: int = 0               # Had violations or errors
    
    # Detailed metrics
    findings_by_kind: Dict[str, int] = field(default_factory=dict)  # kind -> count
    violations_by_rule: Dict[str, int] = field(default_factory=dict)  # rule -> count
    
    @property
    def evaluation_rate(self) -> float:
        """Calculate success rate."""
        if self.total_sessions_evaluated == 0:
            return 1.0
        return self.successful_evaluations / self.total_sessions_evaluated
    
    @classmethod
    def create(cls, health_id: Optional[str] = None) -> GovernanceHealth:
        """Create a new governance health record."""
        return cls(
            health_id=health_id or f"health:{uuid.uuid4().hex[:16]}",
        )


__all__ = [
    "GovernanceRule",
    "GovernanceFindingKind",
    "GovernanceFinding",
    "AbductionGovernance",
    "GovernanceHealth",
]