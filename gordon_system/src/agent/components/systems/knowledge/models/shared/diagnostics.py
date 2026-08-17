# Knowledge Model Diagnostics - Phase 6.7
# =======================================

"""
Model Diagnostics: Detailed diagnostic information about model structure and state.

Diagnostics provide comprehensive assessment data for troubleshooting, monitoring,
and optimization purposes.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Tuple, Optional, Any
import time
import uuid


# =============================================================================
# DIAGNOSTIC REPORT - Complete diagnostic summary
# =============================================================================


@dataclass(frozen=True)
class DiagnosticReport:
    """
    Canonical representation of model diagnostics in Gordon's knowledge system.
    
    Diagnostics provide comprehensive assessment data without modifying models.
    
    Fields:
        report_identity:       Unique identifier for this diagnostic report
        evaluated_model:       ID of the model being diagnosed
        structural_integrity:  Structural soundness score (0.0-1.0)
        semantic_coherence:    Semantic consistency score (0.0-1.0)
        coverage_completeness: Domain coverage completeness (0.0-1.0)
        assumption_coverage:   Explicit assumptions as % of needed
        constraint_satisfaction: Constraint satisfaction ratio
        diagnostic_timestamp:  When diagnostics were collected
        issues:                List of identified issues
        recommendations:       Suggested improvements
        provenance:            Origin tracking with timestamps and sources
    """
    
    # Identity fields (required)
    report_identity: str                # Unique ID for this report
    
    # Evaluated model reference (required)
    evaluated_model: str                # Model being diagnosed
    
    # Diagnostic metrics
    structural_integrity: float = 1.0   # Structural soundness (0.0-1.0)
    semantic_coherence: float = 1.0     # Semantic consistency (0.0-1.0)
    coverage_completeness: float = 1.0  # Domain coverage (0.0-1.0)
    
    # Analysis results
    assumption_coverage: float = 0.0    # % of needed assumptions captured
    constraint_satisfaction: float = 1.0  # Constraint compliance ratio
    
    # Timestamp and tracking
    diagnostic_timestamp: float = field(default_factory=time.time)  # UTC timestamp
    issues: Tuple[str, ...] = field(default_factory=tuple)  # Identified issues
    
    # Recommendations (if any)
    recommendations: Tuple[str, ...] = field(default_factory=tuple)  # Suggestions
    
    # Provenance tracking
    provenance: Dict[str, Any] = field(default_factory=dict)
    
    @property
    def overall_score(self) -> float:
        """Calculate overall diagnostic score."""
        return (
            self.structural_integrity +
            self.semantic_coherence +
            self.coverage_completeness
        ) / 3.0
    
    @property
    def is_healthy(self) -> bool:
        """Check if model passes basic diagnostics."""
        return (
            self.overall_score >= 0.7 and
            len(self.issues) == 0
        )
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert diagnostic report to dictionary for serialization."""
        return {
            "report_identity": self.report_identity,
            "evaluated_model": self.evaluated_model,
            "structural_integrity": self.structural_integrity,
            "semantic_coherence": self.semantic_coherence,
            "coverage_completeness": self.coverage_completeness,
            "assumption_coverage": self.assumption_coverage,
            "constraint_satisfaction": self.constraint_satisfaction,
            "diagnostic_timestamp": self.diagnostic_timestamp,
            "issues": list(self.issues),
            "recommendations": list(self.recommendations),
            "provenance": dict(self.provenance),
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "DiagnosticReport":
        """Create diagnostic report from dictionary."""
        return cls(
            report_identity=data.get("report_identity", str(uuid.uuid4())),
            evaluated_model=data.get("evaluated_model", ""),
            structural_integrity=float(data.get("structural_integrity", 1.0)),
            semantic_coherence=float(data.get("semantic_coherence", 1.0)),
            coverage_completeness=float(data.get("coverage_completeness", 1.0)),
            assumption_coverage=float(data.get("assumption_coverage", 0.0)),
            constraint_satisfaction=float(data.get("constraint_satisfaction", 1.0)),
            diagnostic_timestamp=float(data.get("diagnostic_timestamp", time.time())),
            issues=tuple(data.get("issues", [])),
            recommendations=tuple(data.get("recommendations", [])),
            provenance=dict(data.get("provenance", {})),
        )
    
    @classmethod
    def create(
        cls,
        evaluated_model: str,
        structural_integrity: float = 1.0,
        semantic_coherence: float = 1.0,
        coverage_completeness: float = 1.0,
        assumption_coverage: float = 0.0,
        constraint_satisfaction: float = 1.0,
    ) -> "DiagnosticReport":
        """
        Create a new diagnostic report.
        
        Args:
            evaluated_model: ID of the model being diagnosed
            structural_integrity: Structural soundness (0.0-1.0)
            semantic_coherence: Semantic consistency (0.0-1.0)
            coverage_completeness: Domain coverage completeness (0.0-1.0)
            assumption_coverage: % of needed assumptions captured (0.0-1.0)
            constraint_satisfaction: Constraint compliance ratio (0.0-1.0)
            
        Returns:
            A new diagnostic report
        """
        return cls(
            report_identity=f"diagnostic:{uuid.uuid4().hex[:16]}",
            evaluated_model=evaluated_model,
            structural_integrity=max(0.0, min(1.0, float(structural_integrity))),
            semantic_coherence=max(0.0, min(1.0, float(semantic_coherence))),
            coverage_completeness=max(0.0, min(1.0, float(coverage_completeness))),
            assumption_coverage=max(0.0, min(1.0, float(assumption_coverage))),
            constraint_satisfaction=max(0.0, min(1.0, float(constraint_satisfaction))),
            provenance={
                "created_at_utc": time.time(),
                "builder_version": "1.0",
            },
        )
    
    def add_issue(
        self,
        issue: str,
    ) -> "DiagnosticReport":
        """Create a revision with an additional issue."""
        return DiagnosticReport(
            report_identity=self.report_identity,
            evaluated_model=self.evaluated_model,
            structural_integrity=self.structural_integrity,
            semantic_coherence=self.semantic_coherence,
            coverage_completeness=self.coverage_completeness,
            assumption_coverage=self.assumption_coverage,
            constraint_satisfaction=self.constraint_satisfaction,
            issues=self.issues + (issue,),
            recommendations=self.recommendations,
            provenance={
                **self.provenance,
                "issue_added_at_utc": time.time(),
                "added_issue": issue,
            },
        )
    
    def add_recommendation(
        self,
        recommendation: str,
    ) -> "DiagnosticReport":
        """Create a revision with an additional recommendation."""
        return DiagnosticReport(
            report_identity=self.report_identity,
            evaluated_model=self.evaluated_model,
            structural_integrity=self.structural_integrity,
            semantic_coherence=self.semantic_coherence,
            coverage_completeness=self.coverage_completeness,
            assumption_coverage=self.assumption_coverage,
            constraint_satisfaction=self.constraint_satisfaction,
            issues=self.issues,
            recommendations=self.recommendations + (recommendation,),
            provenance={
                **self.provenance,
                "recommendation_added_at_utc": time.time(),
                "added_recommendation": recommendation,
            },
        )


# =============================================================================
# DIAGNOSTIC CHECK - Individual diagnostic check result
# =============================================================================


@dataclass(frozen=True)
class DiagnosticCheck:
    """
    Record of an individual diagnostic check.
    
    Each check evaluates one aspect of model health or structure.
    
    Fields:
        check_identity:        Unique identifier for this check
        check_name:            Name of the diagnostic check
        passed:                Whether the check passed
        score:                 Numeric score (0.0-1.0)
        details:               Additional information about the check result
    """
    
    # Identity and check info (required)
    check_identity: str                 # Unique ID for this check
    
    check_name: str                     # Name of the diagnostic check
    
    passed: bool                        # Whether the check passed
    
    score: float = 1.0                  # Numeric score (0.0-1.0)
    
    details: Tuple[str, ...] = field(default_factory=tuple)  # Additional info
    
    @property
    def is_critical(self) -> bool:
        """Check if this check represents a critical issue."""
        return not self.passed and self.score < 0.5
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert diagnostic check to dictionary for serialization."""
        return {
            "check_identity": self.check_identity,
            "check_name": self.check_name,
            "passed": self.passed,
            "score": self.score,
            "details": list(self.details),
        }
    
    @classmethod
    def create(
        cls,
        check_name: str,
        passed: bool = True,
        score: float = 1.0,
        details: Optional[List[str]] = None,
    ) -> "DiagnosticCheck":
        """
        Create a new diagnostic check record.
        
        Args:
            check_name: Name of the diagnostic check
            passed: Whether the check passed
            score: Numeric score (0.0-1.0)
            details: Additional information (optional)
            
        Returns:
            A new check record
        """
        return cls(
            check_identity=f"check:{uuid.uuid4().hex[:16]}",
            check_name=check_name,
            passed=bool(passed),
            score=max(0.0, min(1.0, float(score))),
            details=tuple(details or []),
        )


__all__ = [
    "DiagnosticReport",
    "DiagnosticCheck",
]