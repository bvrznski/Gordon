# Gordon Cognitive Architecture - Phase 4.11.8
# ===========================================

"""
Optimization Recommendations
============================

Models for generating architecture optimization recommendations.

OPTIMIZATION LAWS (from spec)
-----------------------------
OPTIMIZATION-LAW-001: Optimization recommendations shall remain advisory.
OPTIMIZATION-LAW-002: Recommendations shall preserve supporting evidence.
OPTIMIZATION-LAW-003: Expected benefit shall remain explicit.
OPTIMIZATION-LAW-004: Recommendations shall preserve limitations.
OPTIMIZATION-LAW-005: Recommendations shall preserve confidence.
OPTIMIZATION-LAW-006: Recommendations shall preserve provenance.
OPTIMIZATION-LAW-007: Recommendations shall never directly modify cognition.
OPTIMIZATION-LAW-008: Recommendation generation shall remain deterministic.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Optional


@dataclass(frozen=True, slots=True)
class OptimizationRecommendation:
    """
    Immutable optimization recommendation.
    
    OPTIMIZATION-LAW-001: Recommendations are advisory only.
    OPTIMIZATION-LAW-002: Recommendations preserve supporting evidence.
    """
    
    recommendation_identity: str
    """Unique identifier for this recommendation."""
    
    target_scope: str = ""
    """Scope to be optimized (network, cycle, etc.)."""
    
    expected_benefit: float = 0.0
    """Expected improvement from implementing recommendation."""
    
    supporting_observations: tuple[str, ...] = ()
    """Observations supporting this recommendation."""
    
    confidence: float = 0.5
    """Confidence in the recommendation."""
    
    limitations: tuple[str, ...] = ()
    """Limitations of this recommendation."""
    
    provenance: dict[str, str] = field(default_factory=dict)
    """Provenance information for this recommendation."""
    
    def __post_init__(self):
        """Validate recommendation components."""
        if not self.recommendation_identity:
            raise ValueError("Recommendation identity cannot be empty")
        
        # Validate confidence bounds
        if not 0.0 <= self.confidence <= 1.0:
            raise ValueError("Confidence must be between 0.0 and 1.0")
    
    @classmethod
    def create(
        cls,
        target_scope: str = "",
        expected_benefit: float = 0.0,
        supporting_observations: tuple[str, ...] = (),
        confidence: float = 0.5,
        limitations: tuple[str, ...] = (),
        provenance: Optional[dict[str, str]] = None,
    ) -> OptimizationRecommendation:
        """
        Create a new optimization recommendation.
        
        Args:
            target_scope: Scope to be optimized
            expected_benefit: Expected improvement (0.0 to 1.0)
            supporting_observations: Observations supporting the recommendation
            confidence: Confidence in the recommendation
            limitations: Limitations of this recommendation
            provenance: Optional provenance dictionary
            
        Returns:
            New OptimizationRecommendation instance with deterministic identity
        """
        import hashlib
        
        # Create deterministic identity based on content
        identity_content = f"opt:{target_scope}:{expected_benefit:.4f}"
        identity_hash = hashlib.sha256(identity_content.encode()).hexdigest()[:16]
        
        return cls(
            recommendation_identity=f"recommendation:opt:{identity_hash}",
            target_scope=target_scope,
            expected_benefit=expected_benefit,
            supporting_observations=supporting_observations,
            confidence=confidence,
            limitations=limitations,
            provenance=provenance or {},
        )
    
    def is_actionable(self, min_confidence: float = 0.7) -> bool:
        """Check if this recommendation is actionable (high confidence)."""
        return self.confidence >= min_confidence
    
    def to_dict(self) -> dict[str, Any]:
        """Convert recommendation to dictionary."""
        return {
            "recommendation_identity": self.recommendation_identity,
            "target_scope": self.target_scope,
            "expected_benefit": self.expected_benefit,
            "supporting_observations": list(self.supporting_observations),
            "confidence": self.confidence,
            "limitations": list(self.limitations),
            "provenance": dict(self.provenance),
        }
    
    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> OptimizationRecommendation:
        """Create recommendation from dictionary."""
        return cls(
            recommendation_identity=data["recommendation_identity"],
            target_scope=data.get("target_scope", ""),
            expected_benefit=float(data.get("expected_benefit", 0.0)),
            supporting_observations=tuple(data.get("supporting_observations", [])),
            confidence=float(data.get("confidence", 0.5)),
            limitations=tuple(data.get("limitations", [])),
            provenance=dict(data.get("provenance", {})),
        )


@dataclass(frozen=True, slots=True)
class OptimizationReport:
    """
    Immutable optimization report aggregating multiple recommendations.
    
    OPTIMIZATION-LAW-002: Reports preserve supporting evidence (recommendations).
    """
    
    identity: str
    """Unique identifier for this report."""
    
    observed_scope: str
    """Scope being analyzed for optimizations."""
    
    recommendations: tuple[OptimizationRecommendation, ...] = ()
    """Collection of optimization recommendations."""
    
    estimated_total_benefit: float = 0.0
    """Total estimated benefit from all recommendations."""
    
    limitations: tuple[str, ...] = ()
    """Limitations of this analysis."""
    
    provenance: dict[str, str] = field(default_factory=dict)
    """Provenance information for this report."""
    
    def __post_init__(self):
        """Validate report components."""
        if not self.identity:
            raise ValueError("Report identity cannot be empty")
        
        if not self.observed_scope:
            raise ValueError("Observed scope cannot be empty")
    
    @classmethod
    def create(
        cls,
        observed_scope: str,
        recommendations: tuple[OptimizationRecommendation, ...] = (),
        estimated_total_benefit: float = 0.0,
        provenance: Optional[dict[str, str]] = None,
    ) -> OptimizationReport:
        """
        Create a new optimization report.
        
        Args:
            observed_scope: Scope being analyzed
            recommendations: Collection of optimization recommendations
            estimated_total_benefit: Total estimated benefit
            provenance: Optional provenance dictionary
            
        Returns:
            New OptimizationReport instance with deterministic identity
        """
        import hashlib
        
        # Create deterministic identity based on content
        identity_content = f"report:opt:{observed_scope}"
        identity_hash = hashlib.sha256(identity_content.encode()).hexdigest()[:16]
        
        return cls(
            identity=f"report:optimization:{identity_hash}",
            observed_scope=observed_scope,
            recommendations=recommendations,
            estimated_total_benefit=estimated_total_benefit,
            provenance=provenance or {},
        )
    
    @property
    def highest_priority(self) -> OptimizationRecommendation | None:
        """Get the recommendation with highest expected benefit."""
        if not self.recommendations:
            return None
        return max(self.recommendations, key=lambda r: r.expected_benefit)
    
    def to_dict(self) -> dict[str, Any]:
        """Convert report to dictionary."""
        return {
            "identity": self.identity,
            "observed_scope": self.observed_scope,
            "recommendations": [r.to_dict() for r in self.recommendations],
            "estimated_total_benefit": self.estimated_total_benefit,
            "limitations": list(self.limitations),
            "provenance": dict(self.provenance),
        }
    
    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> OptimizationReport:
        """Create report from dictionary."""
        return cls(
            identity=data["identity"],
            observed_scope=data["observed_scope"],
            recommendations=tuple(OptimizationRecommendation.from_dict(r) for r in data.get("recommendations", [])),
            estimated_total_benefit=float(data.get("estimated_total_benefit", 0.0)),
            limitations=tuple(data.get("limitations", [])),
            provenance=dict(data.get("provenance", {})),
        )