# Hypothetical Governance - Phase 7.15 Part 2
# =============================================

"""
Canonical Hypothetical Governance Contract.

Hypothetical Governance evaluates hypothesis diversity, assumption quality,
scenario coverage, exploration efficiency, constraint correctness,
and diagnostics.
"""

from __future__ import annotations

import time
import uuid
from dataclasses import dataclass, field
from typing import Dict, List, Tuple, Optional, Any
from enum import Enum, auto


class GovernanceRule(Enum):
    """Governance rules for hypothetical reasoning."""
    
    HYPOTHESIS_LAW_001 = "hypothesis_law_001"  # Every hypothesis has identity
    HYPOTHESIS_LAW_002 = "hypothesis_law_002"  # Hypothesis statements are explicit
    ASSUMPTION_LAW_001 = "assumption_law_001"  # Every assumption has identity
    ASSUMPTION_LAW_006 = "assumption_law_006"  # Hidden assumptions never influence silently
    POSSIBILITY_LAW_007 = "possibility_law_007"  # Spaces remain inspectable
    VALIDATION_LAW_001 = "validation_law_001"  # Validation is observational
    GOVERNANCE_LAW_007 = "governance_law_007"  # Governance never mutates directly


class GovernanceFindingKind(Enum):
    """Kinds of governance findings."""
    
    CONTRADICTORY_ASSUMPTIONS = "contradictory_assumptions"     # Conflicting assumptions
    DEGENERATE_SPACE = "degenerate_space"                       # Empty or trivial space
    NONDETERMINISTIC_GEN = "nondeterministic_generation"       # Non-deterministic behavior


@dataclass(frozen=True)
class GovernanceIdentity:
    """
    Immutable identity for governance evaluation.
    
    Allows tracking governance across sessions.
    """
    
    semantic_identity: str                    # Stable identity across runs
    
    @classmethod
    def create(cls, semantic_identity: str) -> GovernanceIdentity:
        """Create a new governance identity."""
        return cls(semantic_identity=semantic_identity)


@dataclass(frozen=True)
class GovernanceFinding:
    """
    A finding from hypothetical governance evaluation.
    
    Findings remain explicit and inspectable at all times.
    """
    
    # Identity
    finding_id: str                           # Unique identifier
    
    # Rule that was evaluated
    rule_violated: Optional[GovernanceRule] = None  # Which rule, if any?
    
    # Finding details
    finding_kind: GovernanceFindingKind       # What kind of finding?
    finding_statement: str                    # Description of the finding
    
    # Assessment
    severity: str = "warning"                 # "info", "warning", "error"
    confidence: float = 1.0                   # Confidence in this finding
    
    # Metadata
    found_at_utc: float = field(default_factory=time.time)
    
    @classmethod
    def create(
        cls,
        finding_kind: GovernanceFindingKind,
        finding_statement: str,
        rule_violated: Optional[GovernanceRule] = None,
        severity: str = "warning",
        confidence: float = 1.0,
    ) -> GovernanceFinding:
        """Create a new governance finding."""
        return cls(
            finding_id=f"governance_finding:{uuid.uuid4().hex[:16]}",
            rule_violated=rule_violated,
            finding_kind=finding_kind,
            finding_statement=finding_statement,
            severity=severity,
            confidence=confidence,
        )


@dataclass(frozen=True)
class HypotheticalGovernance:
    """
    Record of governance evaluation.
    
    Governance remains observational - it never modifies hypothetical artifacts directly.
    """
    
    # Identity
    governance_id: str                        # Unique identifier
    
    # Evaluated sessions
    evaluated_sessions: Tuple[GovernanceIdentity, ...] = ()  # All evaluated
    
    # Findings
    findings: Tuple[GovernanceFinding, ...] = ()  # All findings
    
    # Violations (findings with severity "error")
    violations: Tuple[GovernanceFinding, ...] = ()  # Errors only
    
    # Recommendations
    recommendations: Tuple[str, ...] = ()     # How to improve
    
    # Metadata
    evaluated_at_utc: float = field(default_factory=time.time)
    
    @property
    def total_findings(self) -> int:
        """Return number of findings."""
        return len(self.findings)
    
    @property
    def has_violations(self) -> bool:
        """Check if any violations were found."""
        return len(self.violations) > 0
    
    @classmethod
    def create(
        cls,
        evaluated_sessions: Optional[List[GovernanceIdentity]] = None,
        findings: Optional[List[GovernanceFinding]] = None,
        recommendations: Optional[List[str]] = None,
    ) -> HypotheticalGovernance:
        """Create a new governance evaluation record."""
        violations = tuple(f for f in (findings or []) if f.severity == "error")
        return cls(
            governance_id=f"governance:{uuid.uuid4().hex[:16]}",
            evaluated_sessions=tuple(evaluated_sessions or []),
            findings=tuple(findings or []),
            violations=violations,
            recommendations=tuple(recommendations or []),
        )


@dataclass(frozen=True)
class GovernanceHealth:
    """
    Health metrics for hypothetical governance.
    
    Metrics remain descriptive and observational.
    """
    
    # Identity
    health_id: str                            # Unique identifier
    
    # Metrics
    evaluation_rate: float = 0.0              # Sessions evaluated per time unit
    violation_rate: float = 0.0               # Violations per session
    pass_rate: float = 1.0                    # Percentage passing governance
    
    # Metadata
    measured_at_utc: float = field(default_factory=time.time)
    
    @classmethod
    def create(
        cls,
        evaluation_rate: float = 0.0,
        violation_rate: float = 0.0,
        pass_rate: float = 1.0,
    ) -> GovernanceHealth:
        """Create a new governance health record."""
        return cls(
            health_id=f"governance_health:{uuid.uuid4().hex[:16]}",
            evaluation_rate=evaluation_rate,
            violation_rate=violation_rate,
            pass_rate=pass_rate,
        )


def dataclass_replace(instance: Any, **kwargs: Any) -> Any:
    """Simple dataclass replace helper for frozen instances."""
    return instance.__class__(**{**instance.__dict__, **kwargs})


__all__ = [
    "GovernanceRule",
    "GovernanceFindingKind",
    "GovernanceIdentity",
    "GovernanceFinding",
    "HypotheticalGovernance",
    "GovernanceHealth",
]