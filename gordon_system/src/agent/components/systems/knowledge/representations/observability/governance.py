# Knowledge Representation Governance - Phase 6.2
# ===============================================

"""
Governance for knowledge representations.

This module provides policy enforcement and quality evaluation:
    * Consistency checking
    * Completeness evaluation
    * Redundancy analysis
    * Stale representation analysis
    * Findings and recommendations
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Tuple, Optional, Any
import time
import uuid


# =============================================================================
# REPRESENTATION GOVERNANCE - Policy enforcement and evaluation
# =============================================================================


@dataclass(frozen=True)
class RepresentationGovernance:
    """
    Governance evaluation for representations.
    
    Evaluates representation quality without modifying semantics. Provides
    findings and recommendations for improvement.
    
    Fields:
        governance_identity: Unique identifier for this governance record
        evaluated_representations: IDs of representations evaluated
        consistency: Consistency assessment results
        completeness: Completeness metrics
        redundancy: Redundancy analysis results
        stale_analysis: Stale representation findings
        findings: List of governance findings
        recommendations: Suggested improvements
    """
    
    # Identity (required)
    governance_identity: str               # Unique governance ID
    
    evaluated_representations: Tuple[str, ...] = field(default_factory=tuple)
    
    # Evaluation results (optional, with defaults)
    consistency: Dict[str, Any] = field(default_factory=dict)
    completeness: Dict[str, Any] = field(default_factory=dict)
    redundancy: Dict[str, Any] = field(default_factory=dict)
    stale_analysis: Dict[str, Any] = field(default_factory=dict)
    
    # Findings and recommendations
    findings: Tuple[Dict[str, Any], ...] = field(default_factory=tuple)
    recommendations: Tuple[Dict[str, Any], ...] = field(default_factory=tuple)
    
    created_at_utc: float = field(default_factory=time.time)
    evaluated_at_utc: float = field(default_factory=time.time)
    
    @property
    def governance_score(self) -> float:
        """Calculate overall governance score (0.0 to 1.0)."""
        scores = []
        
        # Consistency score (if available)
        if self.consistency.get("score") is not None:
            scores.append(float(self.consistency["score"]))
        
        # Completeness score (if available)
        if self.completeness.get("score") is not None:
            scores.append(float(self.completeness["score"]))
        
        # Redundancy penalty
        if self.redundancy.get("redundant_count", 0) > 0:
            scores.append(max(0, 1.0 - (self.redundancy.get("redundant_count", 0) * 0.1)))
        
        # Stale penalty
        stale = self.stale_analysis.get("stale_count", 0)
        if stale > 0:
            scores.append(max(0, 1.0 - (stale * 0.1)))
        
        return sum(scores) / len(scores) if scores else 1.0
    
    @property
    def has_findings(self) -> bool:
        """Check if governance found issues."""
        return len(self.findings) > 0 or len(self.recommendations) > 0
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert governance record to dictionary for serialization."""
        return {
            "governance_identity": self.governance_identity,
            "evaluated_representations": [r for r in self.evaluated_representations],
            "consistency": self.consistency,
            "completeness": self.completeness,
            "redundancy": self.redundancy,
            "stale_analysis": self.stale_analysis,
            "findings": [f for f in self.findings],
            "recommendations": [r for r in self.recommendations],
            "created_at_utc": self.created_at_utc,
            "evaluated_at_utc": self.evaluated_at_utc,
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "RepresentationGovernance":
        """Create governance record from dictionary."""
        return cls(
            governance_identity=data.get("governance_identity", str(uuid.uuid4())),
            evaluated_representations=tuple(data.get("evaluated_representations", [])),
            consistency=data.get("consistency", {}),
            completeness=data.get("completeness", {}),
            redundancy=data.get("redundancy", {}),
            stale_analysis=data.get("stale_analysis", {}),
            findings=tuple(data.get("findings", [])),
            recommendations=tuple(data.get("recommendations", [])),
            created_at_utc=float(data.get("created_at_utc", time.time())),
            evaluated_at_utc=float(data.get("evaluated_at_utc", time.time())),
        )
    
    @classmethod
    def create_initial(
        cls,
        evaluated_representations: Tuple[str, ...] = tuple(),
    ) -> "RepresentationGovernance":
        """Create initial governance evaluation."""
        return cls(
            governance_identity=f"governance:{uuid.uuid4().hex[:16]}",
            evaluated_representations=evaluated_representations,
        )
    
    def with_consistency(self, consistency: Dict[str, Any]) -> "RepresentationGovernance":
        """Add consistency findings."""
        return RepresentationGovernance(
            governance_identity=self.governance_identity,
            evaluated_representations=self.evaluated_representations,
            consistency=consistency,
            completeness=self.completeness,
            redundancy=self.redundancy,
            stale_analysis=self.stale_analysis,
            findings=self.findings,
            recommendations=self.recommendations,
            created_at_utc=self.created_at_utc,
            evaluated_at_utc=time.time(),
        )
    
    def with_findings(self, *findings: Dict[str, Any]) -> "RepresentationGovernance":
        """Add governance findings."""
        return RepresentationGovernance(
            governance_identity=self.governance_identity,
            evaluated_representations=self.evaluated_representations,
            consistency=self.consistency,
            completeness=self.completeness,
            redundancy=self.redundancy,
            stale_analysis=self.stale_analysis,
            findings=self.findings + tuple(findings),
            recommendations=self.recommendations,
            created_at_utc=self.created_at_utc,
            evaluated_at_utc=time.time(),
        )


__all__ = [
    # Governance records
    "RepresentationGovernance",
]