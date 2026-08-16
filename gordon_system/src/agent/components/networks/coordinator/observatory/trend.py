# Gordon Cognitive Architecture - Phase 4.11.8
# ===========================================

"""
Trend Analysis and Reports
==========================

Trend models for detecting long-term patterns.

TREND LAWS (from spec)
----------------------
TREND-LAW-001: Trends shall derive from metric histories.
TREND-LAW-002: Trend direction shall remain explicit.
TREND-LAW-003: Trend stability shall remain explicit.
TREND-LAW-004: Trend confidence shall remain explicit.
TREND-LAW-005: Trend evidence shall remain inspectable.
TREND-LAW-006: Trend provenance shall remain complete.
TREND-LAW-007: Historical trends shall remain immutable.
TREND-LAW-008: Trend evaluation shall remain deterministic.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Optional


# =============================================================================
# TREND DIRECTIONS
# =============================================================================

class TrendDirection(Enum):
    """
    Canonical directions for trends.
    
    TREND-LAW-002: Trend direction remains explicit.
    """
    IMPROVING = "improving"
    """Metric values are improving over time."""
    
    STABLE = "stable"
    """Metric values are stable within normal range."""
    
    DEGRADING = "degrading"
    """Metric values are degrading over time."""
    
    OSCILLATING = "oscillating"
    """Metric values are oscillating without clear trend."""
    
    UNKNOWN = "unknown"
    """Trend direction cannot be determined."""


# =============================================================================
# TREND
# =============================================================================

@dataclass(frozen=True, slots=True)
class Trend:
    """
    Immutable record of an identified trend.
    
    TREND-LAW-001: Trends derive from metric histories.
    TREND-LAW-002: Trend direction remains explicit.
    """
    
    trend_identity: str
    """Unique identifier for this trend."""
    
    observed_metric: str
    """Metric being analyzed."""
    
    direction: str = "unknown"
    """Direction of the trend (from TrendDirection)."""
    
    slope: float = 0.0
    """Calculated slope of the trend."""
    
    stability: float = 1.0
    """Stability of the trend (0.0 to 1.0)."""
    
    confidence: float = 0.5
    """Confidence in trend identification."""
    
    provenance: dict[str, str] = field(default_factory=dict)
    """Provenance information for this trend."""
    
    def __post_init__(self):
        """Validate trend components."""
        if not self.trend_identity:
            raise ValueError("Trend identity cannot be empty")
        
        # Validate confidence bounds
        if not 0.0 <= self.confidence <= 1.0:
            raise ValueError("Confidence must be between 0.0 and 1.0")
        
        # Validate stability bounds
        if not 0.0 <= self.stability <= 1.0:
            raise ValueError("Stability must be between 0.0 and 1.0")
    
    @classmethod
    def create(
        cls,
        observed_metric: str,
        direction: str = "unknown",
        slope: float = 0.0,
        stability: float = 1.0,
        confidence: float = 0.5,
        provenance: Optional[dict[str, str]] = None,
    ) -> Trend:
        """
        Create a new trend record.
        
        Args:
            observed_metric: Metric being analyzed
            direction: Direction of the trend (from TrendDirection)
            slope: Calculated slope of the trend
            stability: Stability of the trend (0.0 to 1.0)
            confidence: Confidence in identification
            provenance: Optional provenance dictionary
            
        Returns:
            New Trend instance with deterministic identity
        """
        import hashlib
        
        # Create deterministic identity based on content
        identity_content = f"trend:{observed_metric}:{direction}"
        identity_hash = hashlib.sha256(identity_content.encode()).hexdigest()[:16]
        
        return cls(
            trend_identity=f"trend:{identity_hash}",
            observed_metric=observed_metric,
            direction=direction,
            slope=slope,
            stability=stability,
            confidence=confidence,
            provenance=provenance or {},
        )
    
    def is_significant(self, min_confidence: float = 0.7) -> bool:
        """Check if this trend is considered significant."""
        return self.confidence >= min_confidence
    
    def to_dict(self) -> dict[str, Any]:
        """Convert trend to dictionary."""
        return {
            "trend_identity": self.trend_identity,
            "observed_metric": self.observed_metric,
            "direction": self.direction,
            "slope": self.slope,
            "stability": self.stability,
            "confidence": self.confidence,
            "provenance": dict(self.provenance),
        }
    
    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> Trend:
        """Create trend from dictionary."""
        return cls(
            trend_identity=data["trend_identity"],
            observed_metric=data["observed_metric"],
            direction=data.get("direction", "unknown"),
            slope=float(data.get("slope", 0.0)),
            stability=float(data.get("stability", 1.0)),
            confidence=float(data.get("confidence", 0.5)),
            provenance=dict(data.get("provenance", {})),
        )


# =============================================================================
# TREND REPORT
# =============================================================================

@dataclass(frozen=True, slots=True)
class TrendReport:
    """
    Immutable trend report aggregating multiple trends.
    
    TREND-LAW-006: Provenance remains complete.
    """
    
    identity: str
    """Unique identifier for this report."""
    
    observed_scope: str
    """Scope being analyzed for trends."""
    
    trends: tuple[Trend, ...] = ()
    """Collection of identified trends."""
    
    overall_direction: str = "unknown"
    """Overall trend direction across all metrics."""
    
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
        trends: tuple[Trend, ...] = (),
        overall_direction: str = "unknown",
        provenance: Optional[dict[str, str]] = None,
    ) -> TrendReport:
        """
        Create a new trend report.
        
        Args:
            observed_scope: Scope being analyzed
            trends: Collection of identified trends
            overall_direction: Overall direction across all metrics
            provenance: Optional provenance dictionary
            
        Returns:
            New TrendReport instance with deterministic identity
        """
        import hashlib
        
        # Create deterministic identity based on content
        identity_content = f"report:trend:{observed_scope}"
        identity_hash = hashlib.sha256(identity_content.encode()).hexdigest()[:16]
        
        return cls(
            identity=f"report:trend:{identity_hash}",
            observed_scope=observed_scope,
            trends=trends,
            overall_direction=overall_direction,
            provenance=provenance or {},
        )
    
    def to_dict(self) -> dict[str, Any]:
        """Convert report to dictionary."""
        return {
            "identity": self.identity,
            "observed_scope": self.observed_scope,
            "trends": [t.to_dict() for t in self.trends],
            "overall_direction": self.overall_direction,
            "limitations": list(self.limitations),
            "provenance": dict(self.provenance),
        }
    
    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> TrendReport:
        """Create report from dictionary."""
        return cls(
            identity=data["identity"],
            observed_scope=data["observed_scope"],
            trends=tuple(Trend.from_dict(t) for t in data.get("trends", [])),
            overall_direction=data.get("overall_direction", "unknown"),
            limitations=tuple(data.get("limitations", [])),
            provenance=dict(data.get("provenance", {})),
        )