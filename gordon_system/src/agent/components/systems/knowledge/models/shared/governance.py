# Knowledge Model Governance - Phase 6.7
# =======================================

"""
Model Governance: Observational evaluation of model quality and compliance.

Governance evaluates models without modifying them, detecting issues like
obsolete models, invalid assumptions, inconsistent predictions, and missing coverage.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Tuple, Optional, Any
from enum import Enum, auto
import time
import uuid


# =============================================================================
# GOVERNANCE FINDING - Individual governance observation
# =============================================================================


@dataclass(frozen=True)
class GovernanceFinding:
    """
    Record of an individual governance evaluation.
    
    Each finding represents one aspect of model quality or compliance observed
    during governance evaluation.
    
    Fields:
        finding_identity:      Unique identifier for this finding
        issue_type:            Category of the observed issue
        severity:              Issue severity level
        description:           Description of the observation
        affected_model:        Model being evaluated
    """
    
    # Identity and issue info (required)
    finding_identity: str               # Unique ID for this finding
    
    issue_type: str                     # Category: "obsolete", "invalid_assumption", etc.
    
    severity: str = "info"              # "info", "warning", or "error"
    
    description: str = ""               # Description of the observation
    
    affected_model: Optional[str] = None  # Model ID (optional)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert finding to dictionary for serialization."""
        return {
            "finding_identity": self.finding_identity,
            "issue_type": self.issue_type,
            "severity": self.severity,
            "description": self.description,
            "affected_model": self.affected_model,
        }


# =============================================================================
# GOVERNANCE VIOLATION - Rule violation record
# =============================================================================


@dataclass(frozen=True)
class GovernanceViolation:
    """
    Record of a governance rule violation.
    
    Violations represent confirmed breaches of model laws or requirements.
    
    Fields:
        violation_identity:    Unique identifier for this violation
        violated_rule:         Name of the violated rule/law
        affected_model:        Model that violates the rule
        evidence:              Evidence supporting the violation finding
    """
    
    # Identity and rule info (required)
    violation_identity: str             # Unique ID for this violation
    
    violated_rule: str                  # Name of the violated law/rule
    
    affected_model: str                 # Model violating the rule
    
    evidence: Tuple[str, ...] = field(default_factory=tuple)  # Supporting evidence
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert violation to dictionary for serialization."""
        return {
            "violation_identity": self.violation_identity,
            "violated_rule": self.violated_rule,
            "affected_model": self.affected_model,
            "evidence": list(self.evidence),
        }


# =============================================================================
# MODEL GOVERNANCE - Canonical governance record
# =============================================================================


@dataclass(frozen=True)
class ModelGovernance:
    """
    Canonical representation of model governance in Gordon's knowledge system.
    
    Governance is observational - it evaluates models without modifying them.
    
    Fields:
        governance_identity:   Unique identifier for this governance session
        evaluated_models:      IDs of models being evaluated
        findings:              Observations made during evaluation
        violations:            Confirmed rule violations
        recommendations:       Suggested actions based on findings
        provenance:            Origin tracking with timestamps and sources
    """
    
    # Identity fields (required)
    governance_identity: str            # Unique ID for this governance session
    
    # Evaluated models (required)
    evaluated_models: Tuple[str, ...]   # IDs of the models evaluated
    
    # Findings and violations
    findings: Tuple[GovernanceFinding, ...] = field(default_factory=tuple)  # Observations
    violations: Tuple[GovernanceViolation, ...] = field(default_factory=tuple)  # Violations
    
    # Recommendations (if any)
    recommendations: Tuple[str, ...] = field(default_factory=tuple)  # Suggested actions
    
    # Provenance tracking
    provenance: Dict[str, Any] = field(default_factory=dict)
    
    @property
    def model_count(self) -> int:
        """Get the number of models evaluated."""
        return len(self.evaluated_models)
    
    @property
    def is_valid(self) -> bool:
        """Check if governance record has minimal required data."""
        return (
            len(self.governance_identity) > 0 and
            self.model_count >= 1
        )
    
    @property
    def violation_count(self) -> int:
        """Get the number of violations found."""
        return len(self.violations)
    
    @property
    def finding_count(self) -> int:
        """Get the number of findings made."""
        return len(self.findings)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert governance record to dictionary for serialization."""
        return {
            "governance_identity": self.governance_identity,
            "evaluated_models": list(self.evaluated_models),
            "findings": [f.to_dict() for f in self.findings],
            "violations": [v.to_dict() for v in self.violations],
            "recommendations": list(self.recommendations),
            "provenance": dict(self.provenance),
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "ModelGovernance":
        """Create governance record from dictionary."""
        findings_data = data.get("findings", [])
        findings = tuple(GovernanceFinding(**f) for f in findings_data)
        
        violations_data = data.get("violations", [])
        violations = tuple(
            GovernanceViolation(
                violation_identity=v.get("violation_identity", str(uuid.uuid4())),
                violated_rule=v.get("violated_rule", ""),
                affected_model=v.get("affected_model", ""),
                evidence=tuple(v.get("evidence", [])),
            )
            for v in violations_data
        )
        
        return cls(
            governance_identity=data.get("governance_identity", str(uuid.uuid4())),
            evaluated_models=tuple(data.get("evaluated_models", [])),
            findings=findings,
            violations=violations,
            recommendations=tuple(data.get("recommendations", [])),
            provenance=dict(data.get("provenance", {})),
        )
    
    @classmethod
    def create(
        cls,
        evaluated_models: List[str],
        findings: Optional[List[GovernanceFinding]] = None,
        violations: Optional[List[GovernanceViolation]] = None,
    ) -> "ModelGovernance":
        """
        Create a new model governance record.
        
        Args:
            evaluated_models: IDs of models being evaluated
            findings: Observations made (optional)
            violations: Confirmed violations (optional)
            
        Returns:
            A new governance record
        """
        return cls(
            governance_identity=f"governance:{uuid.uuid4().hex[:16]}",
            evaluated_models=tuple(evaluated_models),
            findings=tuple(findings or []),
            violations=tuple(violations or []),
            provenance={
                "created_at_utc": time.time(),
                "builder_version": "1.0",
            },
        )
    
    def add_finding(
        self,
        finding: GovernanceFinding,
    ) -> "ModelGovernance":
        """Create a revision with an additional finding."""
        return ModelGovernance(
            governance_identity=self.governance_identity,
            evaluated_models=self.evaluated_models,
            findings=self.findings + (finding,),
            violations=self.violations,
            recommendations=self.recommendations,
            provenance={
                **self.provenance,
                "finding_added_at_utc": time.time(),
                "added_finding_type": finding.issue_type,
            },
        )
    
    def add_violation(
        self,
        violation: GovernanceViolation,
    ) -> "ModelGovernance":
        """Create a revision with an additional violation."""
        return ModelGovernance(
            governance_identity=self.governance_identity,
            evaluated_models=self.evaluated_models,
            findings=self.findings,
            violations=self.violations + (violation,),
            recommendations=self.recommendations,
            provenance={
                **self.provenance,
                "violation_added_at_utc": time.time(),
                "added_violation_rule": violation.violated_rule,
            },
        )
    
    def add_recommendation(
        self,
        recommendation: str,
    ) -> "ModelGovernance":
        """Create a revision with an additional recommendation."""
        return ModelGovernance(
            governance_identity=self.governance_identity,
            evaluated_models=self.evaluated_models,
            findings=self.findings,
            violations=self.violations,
            recommendations=self.recommendations + (recommendation,),
            provenance={
                **self.provenance,
                "recommendation_added_at_utc": time.time(),
                "added_recommendation": recommendation,
            },
        )


__all__ = [
    "GovernanceFinding",
    "GovernanceViolation",
    "ModelGovernance",
]