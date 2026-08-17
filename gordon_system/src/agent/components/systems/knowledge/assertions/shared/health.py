# Knowledge Assertions - Health Contract - Phase 6.4
# =====================================================

"""
Assertion Health: Metrics describing assertion system status.

Health remains descriptive - it does not modify assertions.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Tuple, Optional, Any
import time
import uuid


# =============================================================================
# ASSERTION HEALTH METRICS
# =============================================================================


@dataclass(frozen=True)
class AssertionHealthMetrics:
    """
    Health metrics for the assertion system.
    
    Health remains descriptive - it does not modify assertions.
    
    Fields:
        total_assertions:        Total number of assertions in the system
        supported_assertions:    Count with supporting evidence/justification
        unsupported_assertions:  Count without support
        contradicted_assertions: Count involved in contradictions
        conditional_assertions:  Count with conditions applied
        revision_depth:          Average revision depth across assertions
        evidence_coverage:       Fraction of assertions with evidence (0.0-1.0)
        diagnostics:             Additional diagnostic metrics
    
    CONTRACT REQUIREMENTS:
        ASSERTION-LAW-006: Assertions remain independently inspectable
        ASSERTION-LAW-007: Assertions remain deterministic
    """
    
    total_assertions: int = 0
    supported_assertions: int = 0
    unsupported_assertions: int = 0
    contradicted_assertions: int = 0
    conditional_assertions: int = 0
    revision_depth: float = 0.0
    evidence_coverage: float = 0.0
    diagnostics: Dict[str, Any] = field(default_factory=dict)

    @property
    def is_healthy(self) -> bool:
        """Check if system appears healthy."""
        # Healthy if most assertions are supported and evidence coverage is good
        return (
            self.supported_assertions >= self.unsupported_assertions or
            (self.total_assertions > 0 and 
             self.evidence_coverage >= 0.5)
        )

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for deterministic serialization."""
        return {
            "total_assertions": self.total_assertions,
            "supported_assertions": self.supported_assertions,
            "unsupported_assertions": self.unsupported_assertions,
            "contradicted_assertions": self.contradicted_assertions,
            "conditional_assertions": self.conditional_assertions,
            "revision_depth": self.revision_depth,
            "evidence_coverage": self.evidence_coverage,
            "diagnostics": dict(self.diagnostics),
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> AssertionHealthMetrics:
        """Create from dictionary (deterministic)."""
        return cls(
            total_assertions=int(data.get("total_assertions", 0)),
            supported_assertions=int(data.get("supported_assertions", 0)),
            unsupported_assertions=int(data.get("unsupported_assertions", 0)),
            contradicted_assertions=int(data.get("contradicted_assertions", 0)),
            conditional_assertions=int(data.get("conditional_assertions", 0)),
            revision_depth=float(data.get("revision_depth", 0.0)),
            evidence_coverage=float(data.get("evidence_coverage", 0.0)),
            diagnostics=dict(data.get("diagnostics", {})),
        )


# =============================================================================
# ASSERTION HEALTH SUMMARY
# =============================================================================


@dataclass(frozen=True)
class AssertionHealthSummary:
    """
    Summary of assertion health over a period.
    
    Provides diagnostic overview without modifying assertions.
    
    Fields:
        health_identity:          Unique identifier for this health summary
        assessment_timestamp:     When assessment was made
        metrics:                  Health metrics
        findings_summary:         Summary of governance findings
        recommendations:          Suggested improvements based on health
        provenance:               Origin tracking information
    """
    
    health_identity: str
    assessment_timestamp: float = field(default_factory=time.time)
    metrics: AssertionHealthMetrics = field(default_factory=AssertionHealthMetrics)
    findings_summary: Dict[str, int] = field(default_factory=dict)  # finding_kind -> count
    recommendations: Tuple[str, ...] = field(default_factory=tuple)
    provenance: Dict[str, Any] = field(default_factory=dict)

    @property
    def health_score(self) -> float:
        """Calculate overall health score (0.0-1.0)."""
        total = self.metrics.total_assertions
        if total == 0:
            return 1.0  # No assertions = healthy by default

        # Factor in supported ratio
        support_ratio = self.metrics.supported_assertions / max(1, total)
        
        # Factor in evidence coverage
        evidence_factor = self.metrics.evidence_coverage
        
        # Penalty for contradictions
        contradiction_penalty = min(1.0, self.metrics.contradicted_assertions / max(1, total) * 2)
        
        score = (support_ratio * 0.4 + evidence_factor * 0.4) * (1 - contradiction_penalty)
        return round(max(0.0, min(1.0, score)), 3)

    @property
    def is_healthy(self) -> bool:
        """Check if system appears healthy."""
        return self.health_score >= 0.7 and self.metrics.is_healthy

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for deterministic serialization."""
        return {
            "health_identity": self.health_identity,
            "assessment_timestamp": self.assessment_timestamp,
            "metrics": self.metrics.to_dict(),
            "findings_summary": dict(self.findings_summary),
            "recommendations": list(self.recommendations),
            "provenance": dict(self.provenance),
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> AssertionHealthSummary:
        """Create from dictionary (deterministic)."""
        return cls(
            health_identity=data.get("health_identity", ""),
            assessment_timestamp=float(data.get("assessment_timestamp", time.time())),
            metrics=AssertionHealthMetrics.from_dict(data.get("metrics", {})),
            findings_summary=dict(data.get("findings_summary", {})),
            recommendations=tuple(data.get("recommendations", [])),
            provenance=dict(data.get("provenance", {})),
        )

    @classmethod
    def create(
        cls,
        metrics: AssertionHealthMetrics = None,
    ) -> AssertionHealthSummary:
        """Create a new health summary."""
        return cls(
            health_identity=f"health:{uuid.uuid4().hex[:16]}",
            assessment_timestamp=time.time(),
            metrics=metrics or AssertionHealthMetrics(),
            findings_summary={},
            recommendations=(),
            provenance={"created_at_utc": time.time()},
        )

    def add_finding(self, finding_kind: str, count: int = 1) -> AssertionHealthSummary:
        """Add a finding to the summary."""
        new_findings = dict(self.findings_summary)
        current = new_findings.get(finding_kind, 0)
        new_findings[finding_kind] = current + count

        return AssertionHealthSummary(
            health_identity=self.health_identity,
            assessment_timestamp=time.time(),
            metrics=self.metrics,
            findings_summary=new_findings,
            recommendations=self.recommendations,
            provenance={
                **self.provenance,
                "assessment_updated_at_utc": time.time(),
                "new_finding": {finding_kind: count},
            },
        )

    def add_recommendation(self, recommendation: str) -> AssertionHealthSummary:
        """Add a health recommendation."""
        return AssertionHealthSummary(
            health_identity=self.health_identity,
            assessment_timestamp=time.time(),
            metrics=self.metrics,
            findings_summary=dict(self.findings_summary),
            recommendations=self.recommendations + (recommendation,),
            provenance={
                **self.provenance,
                "recommendation_added_at_utc": time.time(),
                "new_recommendation": recommendation,
            },
        )