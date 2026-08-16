# Gordon Cognitive Architecture - Phase 4.11.8
# ===========================================

"""
Bottleneck Detection and Reports
================================

Bottleneck models for identifying architectural constraints.

BOTTLENECK LAWS (from spec)
---------------------------
BOTTLENECK-LAW-001: Every bottleneck shall identify the affected coordination scope.
BOTTLENECK-LAW-002: Supporting metrics shall remain explicit.
BOTTLENECK-LAW-003: Estimated impact shall remain explicit.
BOTTLENECK-LAW-004: Root dependencies shall remain explicit.
BOTTLENECK-LAW-005: Bottleneck evidence shall remain inspectable.
BOTTLENECK-LAW-006: Bottleneck provenance shall remain complete.
BOTTLENECK-LAW-007: Historical bottlenecks shall remain inspectable.
BOTTLENECK-LAW-008: Bottleneck identification shall remain deterministic.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Optional


@dataclass(frozen=True, slots=True)
class Bottleneck:
    """
    Immutable bottleneck in the coordination architecture.
    
    BOTTLENECK-LAW-001: Bottlenecks identify affected scope.
    BOTTLENECK-LAW-002: Supporting metrics remain explicit.
    """
    
    bottleneck_identity: str
    """Unique identifier for this bottleneck."""
    
    affected_networks: tuple[str, ...] = ()
    """Networks affected by the bottleneck."""
    
    affected_cycles: tuple[str, ...] = ()
    """Cycles affected by the bottleneck."""
    
    impact_estimate: float = 0.0
    """Estimated impact on system performance."""
    
    supporting_metrics: tuple[str, ...] = ()
    """Metrics supporting bottleneck identification."""
    
    confidence: float = 0.5
    """Confidence in bottleneck identification."""
    
    provenance: dict[str, str] = field(default_factory=dict)
    """Provenance information for this bottleneck."""
    
    def __post_init__(self):
        """Validate bottleneck components."""
        if not self.bottleneck_identity:
            raise ValueError("Bottleneck identity cannot be empty")
        
        # Validate confidence bounds
        if not 0.0 <= self.confidence <= 1.0:
            raise ValueError("Confidence must be between 0.0 and 1.0")
    
    @classmethod
    def create(
        cls,
        affected_networks: tuple[str, ...] = (),
        affected_cycles: tuple[str, ...] = (),
        impact_estimate: float = 0.0,
        supporting_metrics: tuple[str, ...] = (),
        confidence: float = 0.5,
        provenance: Optional[dict[str, str]] = None,
    ) -> Bottleneck:
        """
        Create a new bottleneck record.
        
        Args:
            affected_networks: Networks affected by the bottleneck
            affected_cycles: Cycles affected by the bottleneck
            impact_estimate: Estimated performance impact (0.0 to 1.0)
            supporting_metrics: References to supporting metrics
            confidence: Confidence in identification
            provenance: Optional provenance dictionary
            
        Returns:
            New Bottleneck instance with deterministic identity
        """
        import hashlib
        
        # Create deterministic identity based on content
        identity_content = f"bn:{len(affected_networks)} networks"
        identity_hash = hashlib.sha256(identity_content.encode()).hexdigest()[:16]
        
        return cls(
            bottleneck_identity=f"bottleneck:{identity_hash}",
            affected_networks=affected_networks,
            affected_cycles=affected_cycles,
            impact_estimate=impact_estimate,
            supporting_metrics=supporting_metrics,
            confidence=confidence,
            provenance=provenance or {},
        )
    
    def to_dict(self) -> dict[str, Any]:
        """Convert bottleneck to dictionary."""
        return {
            "bottleneck_identity": self.bottleneck_identity,
            "affected_networks": list(self.affected_networks),
            "affected_cycles": list(self.affected_cycles),
            "impact_estimate": self.impact_estimate,
            "supporting_metrics": list(self.supporting_metrics),
            "confidence": self.confidence,
            "provenance": dict(self.provenance),
        }
    
    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> Bottleneck:
        """Create bottleneck from dictionary."""
        return cls(
            bottleneck_identity=data["bottleneck_identity"],
            affected_networks=tuple(data.get("affected_networks", [])),
            affected_cycles=tuple(data.get("affected_cycles", [])),
            impact_estimate=float(data.get("impact_estimate", 0.0)),
            supporting_metrics=tuple(data.get("supporting_metrics", [])),
            confidence=float(data.get("confidence", 0.5)),
            provenance=dict(data.get("provenance", {})),
        )


@dataclass(frozen=True, slots=True)
class BottleneckReport:
    """
    Immutable bottleneck report aggregating multiple bottlenecks.
    
    BOTTLENECK-LAW-006: Provenance remains complete.
    """
    
    identity: str
    """Unique identifier for this report."""
    
    observed_scope: str
    """Scope being analyzed for bottlenecks."""
    
    bottlenecks: tuple[Bottleneck, ...] = ()
    """Collection of identified bottlenecks."""
    
    affected_goals: tuple[str, ...] = ()
    """Goals affected by bottlenecks."""
    
    estimated_impact: float = 0.0
    """Overall estimated impact on system."""
    
    recommendations: tuple[str, ...] = ()
    """Suggested improvements."""
    
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
        bottlenecks: tuple[Bottleneck, ...] = (),
        affected_goals: tuple[str, ...] = (),
        estimated_impact: float = 0.0,
        recommendations: tuple[str, ...] = (),
        provenance: Optional[dict[str, str]] = None,
    ) -> BottleneckReport:
        """
        Create a new bottleneck report.
        
        Args:
            observed_scope: Scope being analyzed
            bottlenecks: Collection of identified bottlenecks
            affected_goals: Goals affected by bottlenecks
            estimated_impact: Overall impact estimate
            recommendations: Suggested improvements
            provenance: Optional provenance dictionary
            
        Returns:
            New BottleneckReport instance with deterministic identity
        """
        import hashlib
        
        # Create deterministic identity based on content
        identity_content = f"report:bn:{observed_scope}"
        identity_hash = hashlib.sha256(identity_content.encode()).hexdigest()[:16]
        
        return cls(
            identity=f"report:bottleneck:{identity_hash}",
            observed_scope=observed_scope,
            bottlenecks=bottlenecks,
            affected_goals=affected_goals,
            estimated_impact=estimated_impact,
            recommendations=recommendations,
            provenance=provenance or {},
        )
    
    @property
    def highest_impact(self) -> float:
        """Get the highest impact among all bottlenecks."""
        if not self.bottlenecks:
            return 0.0
        return max(b.impact_estimate for b in self.bottlenecks)
    
    def to_dict(self) -> dict[str, Any]:
        """Convert report to dictionary."""
        return {
            "identity": self.identity,
            "observed_scope": self.observed_scope,
            "bottlenecks": [b.to_dict() for b in self.bottlenecks],
            "affected_goals": list(self.affected_goals),
            "estimated_impact": self.estimated_impact,
            "recommendations": list(self.recommendations),
            "limitations": list(self.limitations),
            "provenance": dict(self.provenance),
        }
    
    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> BottleneckReport:
        """Create report from dictionary."""
        return cls(
            identity=data["identity"],
            observed_scope=data["observed_scope"],
            bottlenecks=tuple(Bottleneck.from_dict(b) for b in data.get("bottlenecks", [])),
            affected_goals=tuple(data.get("affected_goals", [])),
            estimated_impact=float(data.get("estimated_impact", 0.0)),
            recommendations=tuple(data.get("recommendations", [])),
            limitations=tuple(data.get("limitations", [])),
            provenance=dict(data.get("provenance", {})),
        )