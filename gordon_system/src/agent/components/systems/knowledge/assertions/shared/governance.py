# Knowledge Assertions - Governance Contract - Phase 6.4
# =======================================================

"""
Assertion Governance: Observational evaluation of assertion states.

Governance evaluates assertions but never modifies them directly.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Tuple, Optional, Any
from enum import Enum, auto
import time
import uuid


# =============================================================================
# GOVERNANCE FINDING KINDS
# =============================================================================


class GovernanceFindingKind(Enum):
    """Kinds of governance findings."""
    
    DUPLICATE = "duplicate"               # Duplicate assertion detected
    UNSUPPORTED = "unsupported"           # No evidence or justification
    CONTRADICTION = "contradiction"       # Conflicts with another assertion
    ORPHAN = "orphan"                     # References non-existent artifact
    SCOPE_VIOLATION = "scope_violation"   # Outside applicability scope
    PREDICATE_INCONSISTENCY = "predicate_inconsistency"  # Inconsistent predicate usage


# =============================================================================
# GOVERNANCE FINDING
# =============================================================================


@dataclass(frozen=True)
class GovernanceFinding:
    """
    A single governance finding about an assertion.
    
    Findings are observational and never modify assertions directly.
    
    Fields:
        finding_identity:   Unique identifier for this finding
        assertion_id:       The assertion being evaluated
        finding_kind:       Type of finding (DUPLICATE, UNSUPPORTED, etc.)
        details:            Additional information about the finding
        severity:           Finding severity (LOW, MEDIUM, HIGH)
        provenance:         Origin tracking information
    """
    
    finding_identity: str
    assertion_id: str
    finding_kind: GovernanceFindingKind = GovernanceFindingKind.UNSUPPORTED
    details: str = ""
    severity: int = 1  # 1-5 scale (1=lowest, 5=highest)
    provenance: Dict[str, Any] = field(default_factory=dict)

    @property
    def is_critical(self) -> bool:
        """Check if finding is critical."""
        return self.severity >= 4

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for deterministic serialization."""
        return {
            "finding_identity": self.finding_identity,
            "assertion_id": self.assertion_id,
            "finding_kind": self.finding_kind.value,
            "details": self.details,
            "severity": self.severity,
            "provenance": dict(self.provenance),
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> GovernanceFinding:
        """Create from dictionary (deterministic)."""
        return cls(
            finding_identity=data.get("finding_identity", ""),
            assertion_id=data.get("assertion_id", ""),
            finding_kind=GovernanceFindingKind(data.get("finding_kind", "unsupported")),
            details=data.get("details", ""),
            severity=int(data.get("severity", 1)),
            provenance=dict(data.get("provenance", {})),
        )

    @classmethod
    def duplicate_finding(
        cls,
        assertion_id: str,
        duplicate_of: str,
        confidence: float = 0.95,
    ) -> GovernanceFinding:
        """Create a duplicate finding."""
        return cls(
            finding_identity=f"finding:{uuid.uuid4().hex[:16]}",
            assertion_id=assertion_id,
            finding_kind=GovernanceFindingKind.DUPLICATE,
            details=f"Duplicate of {duplicate_of}",
            severity=2,
            provenance={
                "created_at_utc": time.time(),
                "kind": "duplicate",
                "confidence": confidence,
            },
        )

    @classmethod
    def unsupported_finding(
        cls,
        assertion_id: str,
        missing_evidence_count: int = 0,
        missing_justification: bool = False,
    ) -> GovernanceFinding:
        """Create an unsupported finding."""
        severity = 3 if missing_evidence_count > 3 else 1
        return cls(
            finding_identity=f"finding:{uuid.uuid4().hex[:16]}",
            assertion_id=assertion_id,
            finding_kind=GovernanceFindingKind.UNSUPPORTED,
            details=(
                f"Missing {missing_evidence_count} evidence sources, "
                f"justification: {'yes' if missing_justification else 'no'}"
            ),
            severity=severity,
            provenance={
                "created_at_utc": time.time(),
                "kind": "unsupported",
            },
        )

    @classmethod
    def contradiction_finding(
        cls,
        assertion_id: str,
        conflicting_assertion: str,
        confidence: float = 0.85,
    ) -> GovernanceFinding:
        """Create a contradiction finding."""
        return cls(
            finding_identity=f"finding:{uuid.uuid4().hex[:16]}",
            assertion_id=assertion_id,
            finding_kind=GovernanceFindingKind.CONTRADICTION,
            details=f"Conflicts with {conflicting_assertion}",
            severity=3,
            provenance={
                "created_at_utc": time.time(),
                "kind": "contradiction",
                "confidence": confidence,
            },
        )

    @classmethod
    def orphan_finding(
        cls,
        assertion_id: str,
        missing_artifact_id: str,
    ) -> GovernanceFinding:
        """Create an orphan finding."""
        return cls(
            finding_identity=f"finding:{uuid.uuid4().hex[:16]}",
            assertion_id=assertion_id,
            finding_kind=GovernanceFindingKind.ORPHAN,
            details=f"References non-existent artifact: {missing_artifact_id}",
            severity=2,
            provenance={
                "created_at_utc": time.time(),
                "kind": "orphan",
            },
        )


# =============================================================================
# ASSERTION GOVERNANCE
# =============================================================================


@dataclass(frozen=True)
class AssertionGovernance:
    """
    Governance evaluation of assertions.
    
    Governance remains observational - it evaluates but never modifies assertions.
    
    Fields:
        governance_identity: Unique identifier for this governance session
        evaluated_assertions:  IDs of assertions being evaluated
        findings:              List of governance findings
        violations:            List of policy violations
        recommendations:       Suggested actions based on findings
        evaluation_timestamp:  When evaluation occurred
        provenance:            Origin tracking information
    
    CONTRACT REQUIREMENTS:
        GOVERNANCE-LAW-001: Assertion Governance remains observational.
        GOVERNANCE-LAW-002: Governance detects duplicate Assertions.
        GOVERNANCE-LAW-003: Governance detects unsupported Assertions.
        GOVERNANCE-LAW-004: Governance detects contradictory Assertions.
        GOVERNANCE-LAW-005: Governance preserves findings.
        GOVERNANCE-LAW-006: Governance preserves provenance.
        GOVERNANCE-LAW-007: Governance never modifies Assertions directly.
        GOVERNANCE-LAW-008: Equivalent Assertion states produce equivalent governance results.
    """
    
    governance_identity: str
    evaluated_assertions: Tuple[str, ...]
    findings: Tuple[GovernanceFinding, ...] = field(default_factory=tuple)
    violations: Tuple[str, ...] = field(default_factory=tuple)  # Policy violation messages
    recommendations: Tuple[str, ...] = field(default_factory=tuple)  # Action suggestions
    evaluation_timestamp: float = field(default_factory=time.time)
    provenance: Dict[str, Any] = field(default_factory=dict)

    @property
    def finding_count(self) -> int:
        """Count of findings."""
        return len(self.findings)

    @property
    def violation_count(self) -> int:
        """Count of violations."""
        return len(self.violations)

    @property
    def has_issues(self) -> bool:
        """Check if there are any issues."""
        return self.finding_count > 0 or self.violation_count > 0

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for deterministic serialization."""
        return {
            "governance_identity": self.governance_identity,
            "evaluated_assertions": list(self.evaluated_assertions),
            "findings": [f.to_dict() for f in self.findings],
            "violations": list(self.violations),
            "recommendations": list(self.recommendations),
            "evaluation_timestamp": self.evaluation_timestamp,
            "provenance": dict(self.provenance),
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> AssertionGovernance:
        """Create from dictionary (deterministic)."""
        return cls(
            governance_identity=data.get("governance_identity", ""),
            evaluated_assertions=tuple(data.get("evaluated_assertions", [])),
            findings=tuple(GovernanceFinding.from_dict(f) for f in data.get("findings", [])),
            violations=tuple(data.get("violations", [])),
            recommendations=tuple(data.get("recommendations", [])),
            evaluation_timestamp=float(data.get("evaluation_timestamp", time.time())),
            provenance=dict(data.get("provenance", {})),
        )

    @classmethod
    def create(
        cls,
        assertion_ids: Tuple[str, ...],
    ) -> AssertionGovernance:
        """Create a new governance session."""
        return cls(
            governance_identity=f"governance:{uuid.uuid4().hex[:16]}",
            evaluated_assertions=assertion_ids,
            findings=(),
            violations=(),
            recommendations=(),
            evaluation_timestamp=time.time(),
            provenance={"created_at_utc": time.time()},
        )

    def add_finding(self, finding: GovernanceFinding) -> AssertionGovernance:
        """Add a finding to this governance session."""
        return AssertionGovernance(
            governance_identity=self.governance_identity,
            evaluated_assertions=self.evaluated_assertions,
            findings=self.findings + (finding,),
            violations=self.violations,
            recommendations=self.recommendations,
            evaluation_timestamp=self.evaluation_timestamp,
            provenance={
                **self.provenance,
                "finding_added_at_utc": time.time(),
                "new_finding_id": finding.finding_identity,
            },
        )

    def add_violation(self, violation: str) -> AssertionGovernance:
        """Add a policy violation to this governance session."""
        return AssertionGovernance(
            governance_identity=self.governance_identity,
            evaluated_assertions=self.evaluated_assertions,
            findings=self.findings,
            violations=self.violations + (violation,),
            recommendations=self.recommendations,
            evaluation_timestamp=self.evaluation_timestamp,
            provenance={
                **self.provenance,
                "violation_added_at_utc": time.time(),
                "new_violation": violation,
            },
        )

    def add_recommendation(self, recommendation: str) -> AssertionGovernance:
        """Add a recommendation based on findings."""
        return AssertionGovernance(
            governance_identity=self.governance_identity,
            evaluated_assertions=self.evaluated_assertions,
            findings=self.findings,
            violations=self.violations,
            recommendations=self.recommendations + (recommendation,),
            evaluation_timestamp=self.evaluation_timestamp,
            provenance={
                **self.provenance,
                "recommendation_added_at_utc": time.time(),
                "new_recommendation": recommendation,
            },
        )

    def merge(self, other: AssertionGovernance) -> AssertionGovernance:
        """Merge two governance sessions."""
        return AssertionGovernance(
            governance_identity=self.governance_identity,
            evaluated_assertions=tuple(set(self.evaluated_assertions + other.evaluated_assertions)),
            findings=self.findings + other.findings,
            violations=self.violations + other.violations,
            recommendations=self.recommendations + other.recommendations,
            evaluation_timestamp=max(self.evaluation_timestamp, other.evaluation_timestamp),
            provenance={
                **self.provenance,
                "merged_at_utc": time.time(),
                "merged_from": [other.governance_identity],
            },
        )