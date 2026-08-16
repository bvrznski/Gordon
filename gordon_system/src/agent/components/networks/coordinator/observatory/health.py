# Gordon Cognitive Architecture - Phase 4.11.8
# ===========================================

"""
Health Indicators and Reports
=============================

Health assessment models for architectural observation.

HEALTH LAWS (from spec)
-----------------------
HEALTH-LAW-001: Health indicators shall derive from supporting evidence.
HEALTH-LAW-002: Health shall never be inferred without supporting metrics.
HEALTH-LAW-003: Health dimensions shall remain explicit.
HEALTH-LAW-004: Health severity shall remain explicit.
HEALTH-LAW-005: Health reports shall preserve supporting evidence.
HEALTH-LAW-006: Health confidence shall remain explicit.
HEALTH-LAW-007: Health provenance shall remain complete.
HEALTH-LAW-008: Health evaluation shall remain deterministic.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Optional


# =============================================================================
# HEALTH DIMENSIONS
# =============================================================================

class HealthDimension(Enum):
    """
    Canonical dimensions of architectural health.
    
    HEALTH-LAW-003: Health dimensions remain explicit.
    """
    STABILITY = "stability"
    """Stability of system state."""
    
    CONSISTENCY = "consistency"
    """Consistency across components."""
    
    ROBUSTNESS = "robustness"
    """Robustness against failures."""
    
    COORDINATION = "coordination"
    """Coordination effectiveness."""
    
    RECOVERABILITY = "recoverability"
    """Ability to recover from failures."""
    
    SCALABILITY = "scalability"
    """Scalability characteristics."""
    
    RESPONSIVENESS = "responsiveness"
    """Responsiveness to stimuli."""
    
    ADAPTABILITY = "adaptability"
    """Adaptation capability."""
    
    EFFICIENCY = "efficiency"
    """Operational efficiency."""
    
    UNKNOWN = "unknown"
    """Unknown health dimension."""


# =============================================================================
# HEALTH INDICATOR
# =============================================================================

@dataclass(frozen=True, slots=True)
class HealthIndicator:
    """
    Immutable health indicator based on metrics.
    
    HEALTH-LAW-001: Indicators derive from supporting evidence (metrics).
    HEALTH-LAW-002: Health requires measurable metrics.
    """
    
    indicator_identity: str
    """Unique identifier for this health indicator."""
    
    health_dimension: str
    """Dimension being assessed (from HealthDimension)."""
    
    measured_scope: str
    """Scope being measured (network, cycle, goal, etc.)."""
    
    current_value: float = 0.0
    """Current health value (0.0 to 1.0)."""
    
    expected_range: tuple[float, float] = field(default_factory=lambda: (0.8, 1.0))
    """Expected healthy range (min, max)."""
    
    severity: str = "normal"
    """Severity level of this indicator."""
    
    supporting_metrics: tuple[str, ...] = ()
    """References to metrics supporting this indicator."""
    
    provenance: dict[str, str] = field(default_factory=dict)
    """Provenance information for this indicator."""
    
    def __post_init__(self):
        """Validate indicator components."""
        if not self.indicator_identity:
            raise ValueError("Indicator identity cannot be empty")
        
        if not self.measured_scope:
            raise ValueError("Measured scope cannot be empty")
        
        # Validate current value bounds
        if not 0.0 <= self.current_value <= 1.0:
            raise ValueError(f"Current value must be between 0.0 and 1.0: {self.current_value}")
    
    @classmethod
    def create(
        cls,
        health_dimension: str,
        measured_scope: str,
        current_value: float,
        supporting_metrics: tuple[str, ...] = (),
        expected_min: float = 0.8,
        provenance: Optional[dict[str, str]] = None,
    ) -> HealthIndicator:
        """
        Create a new health indicator.
        
        Args:
            health_dimension: Dimension being assessed
            measured_scope: Scope being measured
            current_value: Current health value (0.0 to 1.0)
            supporting_metrics: References to supporting metrics
            expected_min: Minimum acceptable value
            provenance: Optional provenance dictionary
            
        Returns:
            New HealthIndicator instance with deterministic identity
        """
        import hashlib
        
        # Create deterministic identity based on content
        identity_content = f"{health_dimension}:{measured_scope}"
        identity_hash = hashlib.sha256(identity_content.encode()).hexdigest()[:16]
        
        return cls(
            indicator_identity=f"health:{identity_hash}",
            health_dimension=health_dimension,
            measured_scope=measured_scope,
            current_value=current_value,
            expected_range=(expected_min, 1.0),
            severity="normal" if current_value >= expected_min else "degraded",
            supporting_metrics=supporting_metrics,
            provenance=provenance or {},
        )
    
    def is_healthy(self) -> bool:
        """Check if this indicator indicates healthy state."""
        min_val, max_val = self.expected_range
        return min_val <= self.current_value <= max_val
    
    def to_dict(self) -> dict[str, Any]:
        """Convert indicator to dictionary."""
        return {
            "indicator_identity": self.indicator_identity,
            "health_dimension": self.health_dimension,
            "measured_scope": self.measured_scope,
            "current_value": self.current_value,
            "expected_range": list(self.expected_range),
            "severity": self.severity,
            "supporting_metrics": list(self.supporting_metrics),
            "provenance": dict(self.provenance),
        }
    
    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> HealthIndicator:
        """Create indicator from dictionary."""
        return cls(
            indicator_identity=data["indicator_identity"],
            health_dimension=data["health_dimension"],
            measured_scope=data["measured_scope"],
            current_value=float(data.get("current_value", 0.0)),
            expected_range=tuple(data.get("expected_range", [0.8, 1.0])),
            severity=data.get("severity", "normal"),
            supporting_metrics=tuple(data.get("supporting_metrics", [])),
            provenance=dict(data.get("provenance", {})),
        )


# =============================================================================
# HEALTH REPORT
# =============================================================================

@dataclass(frozen=True, slots=True)
class HealthReport:
    """
    Immutable health report aggregating multiple indicators.
    
    HEALTH-LAW-005: Reports preserve supporting evidence (indicators).
    """
    
    report_identity: str
    """Unique identifier for this report."""
    
    observed_scope: str
    """Scope being reported on."""
    
    health_indicators: tuple[HealthIndicator, ...] = ()
    """Collection of health indicators."""
    
    findings: tuple[str, ...] = ()
    """Summary findings."""
    
    recommendations: tuple[str, ...] = ()
    """Suggested improvements."""
    
    limitations: tuple[str, ...] = ()
    """Limitations of this report."""
    
    confidence: float = 0.5
    """Confidence in the health assessment."""
    
    provenance: dict[str, str] = field(default_factory=dict)
    """Provenance information for this report."""
    
    def __post_init__(self):
        """Validate report components."""
        if not self.report_identity:
            raise ValueError("Report identity cannot be empty")
        
        if not self.observed_scope:
            raise ValueError("Observed scope cannot be empty")
        
        # Validate confidence bounds
        if not 0.0 <= self.confidence <= 1.0:
            raise ValueError("Confidence must be between 0.0 and 1.0")
    
    @classmethod
    def create(
        cls,
        observed_scope: str,
        health_indicators: tuple[HealthIndicator, ...] = (),
        findings: tuple[str, ...] = (),
        recommendations: tuple[str, ...] = (),
        confidence: float = 0.5,
        provenance: Optional[dict[str, str]] = None,
    ) -> HealthReport:
        """
        Create a new health report.
        
        Args:
            observed_scope: Scope being reported on
            health_indicators: Collection of health indicators
            findings: Summary findings
            recommendations: Suggested improvements
            confidence: Confidence in the assessment
            provenance: Optional provenance dictionary
            
        Returns:
            New HealthReport instance with deterministic identity
        """
        import hashlib
        
        # Create deterministic identity based on content
        identity_content = f"health:{observed_scope}"
        identity_hash = hashlib.sha256(identity_content.encode()).hexdigest()[:16]
        
        return cls(
            report_identity=f"report:health:{identity_hash}",
            observed_scope=observed_scope,
            health_indicators=health_indicators,
            findings=findings,
            recommendations=recommendations,
            confidence=confidence,
            provenance=provenance or {},
        )
    
    @property
    def overall_health(self) -> float:
        """Compute overall health score as average of indicator values."""
        if not self.health_indicators:
            return 0.5
        
        return sum(i.current_value for i in self.health_indicators) / len(self.health_indicators)
    
    def is_healthy(self) -> bool:
        """Check if all indicators indicate healthy state."""
        return all(indicator.is_healthy() for indicator in self.health_indicators)
    
    def to_dict(self) -> dict[str, Any]:
        """Convert report to dictionary."""
        return {
            "report_identity": self.report_identity,
            "observed_scope": self.observed_scope,
            "health_indicators": [i.to_dict() for i in self.health_indicators],
            "findings": list(self.findings),
            "recommendations": list(self.recommendations),
            "limitations": list(self.limitations),
            "confidence": self.confidence,
            "provenance": dict(self.provenance),
        }
    
    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> HealthReport:
        """Create report from dictionary."""
        return cls(
            report_identity=data["report_identity"],
            observed_scope=data["observed_scope"],
            health_indicators=tuple(HealthIndicator.from_dict(i) for i in data.get("health_indicators", [])),
            findings=tuple(data.get("findings", [])),
            recommendations=tuple(data.get("recommendations", [])),
            limitations=tuple(data.get("limitations", [])),
            confidence=float(data.get("confidence", 0.5)),
            provenance=dict(data.get("provenance", {})),
        )