# Gordon Cognitive Architecture - Phase 4.11.8
# ===========================================

"""
Anomaly Detection and Reports
=============================

Anomaly models for detecting unexpected behavior.

ANOMALY LAWS (from spec)
----------------------
ANOMALY-LAW-001: Every anomaly shall compare observed behavior with expected behavior.
ANOMALY-LAW-002: Deviation shall remain explicit.
ANOMALY-LAW-003: Severity shall remain explicit.
ANOMALY-LAW-004: Possible explanations shall remain hypotheses.
ANOMALY-LAW-005: Anomaly confidence shall remain explicit.
ANOMALY-LAW-006: Anomaly provenance shall remain complete.
ANOMALY-LAW-007: Historical anomalies shall remain inspectable.
ANOMALY-LAW-008: Anomaly detection shall remain deterministic.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Optional


@dataclass(frozen=True, slots=True)
class Anomaly:
    """
    Immutable record of an anomalous observation.
    
    ANOMALY-LAW-001: Anomalies compare observed vs expected behavior.
    ANOMALY-LAW-002: Deviation remains explicit.
    """
    
    anomaly_identity: str
    """Unique identifier for this anomaly."""
    
    expected_behavior: str = ""
    """Description of expected behavior."""
    
    observed_behavior: str = ""
    """Description of observed (anomalous) behavior."""
    
    deviation: float = 0.0
    """Magnitude of deviation from expected."""
    
    severity: str = "warning"
    """Severity level of the anomaly."""
    
    confidence: float = 0.5
    """Confidence in anomaly identification."""
    
    possible_explanations: tuple[str, ...] = ()
    """Possible explanations (hypotheses)."""
    
    provenance: dict[str, str] = field(default_factory=dict)
    """Provenance information for this anomaly."""
    
    def __post_init__(self):
        """Validate anomaly components."""
        if not self.anomaly_identity:
            raise ValueError("Anomaly identity cannot be empty")
        
        # Validate deviation is non-negative
        if self.deviation < 0.0:
            raise ValueError(f"Deviation must be non-negative: {self.deviation}")
        
        # Validate confidence bounds
        if not 0.0 <= self.confidence <= 1.0:
            raise ValueError("Confidence must be between 0.0 and 1.0")
    
    @classmethod
    def create(
        cls,
        expected_behavior: str = "",
        observed_behavior: str = "",
        deviation: float = 0.0,
        severity: str = "warning",
        confidence: float = 0.5,
        possible_explanations: tuple[str, ...] = (),
        provenance: Optional[dict[str, str]] = None,
    ) -> Anomaly:
        """
        Create a new anomaly record.
        
        Args:
            expected_behavior: Description of expected behavior
            observed_behavior: Description of observed behavior
            deviation: Magnitude of deviation from expected
            severity: Severity level (critical, warning, info)
            confidence: Confidence in identification
            possible_explanations: Possible explanations (hypotheses)
            provenance: Optional provenance dictionary
            
        Returns:
            New Anomaly instance with deterministic identity
        """
        import hashlib
        
        # Create deterministic identity based on content
        identity_content = f"anom:{severity}:{abs(deviation):.4f}"
        identity_hash = hashlib.sha256(identity_content.encode()).hexdigest()[:16]
        
        return cls(
            anomaly_identity=f"anomaly:{identity_hash}",
            expected_behavior=expected_behavior,
            observed_behavior=observed_behavior,
            deviation=deviation,
            severity=severity,
            confidence=confidence,
            possible_explanations=possible_explanations,
            provenance=provenance or {},
        )
    
    def is_significant(self, threshold: float = 0.5) -> bool:
        """Check if this anomaly exceeds the significance threshold."""
        return self.deviation >= threshold and self.confidence >= 0.7
    
    def to_dict(self) -> dict[str, Any]:
        """Convert anomaly to dictionary."""
        return {
            "anomaly_identity": self.anomaly_identity,
            "expected_behavior": self.expected_behavior,
            "observed_behavior": self.observed_behavior,
            "deviation": self.deviation,
            "severity": self.severity,
            "confidence": self.confidence,
            "possible_explanations": list(self.possible_explanations),
            "provenance": dict(self.provenance),
        }
    
    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> Anomaly:
        """Create anomaly from dictionary."""
        return cls(
            anomaly_identity=data["anomaly_identity"],
            expected_behavior=data.get("expected_behavior", ""),
            observed_behavior=data.get("observed_behavior", ""),
            deviation=float(data.get("deviation", 0.0)),
            severity=data.get("severity", "warning"),
            confidence=float(data.get("confidence", 0.5)),
            possible_explanations=tuple(data.get("possible_explanations", [])),
            provenance=dict(data.get("provenance", {})),
        )


@dataclass(frozen=True, slots=True)
class AnomalyReport:
    """
    Immutable anomaly report aggregating multiple anomalies.
    
    ANOMALY-LAW-006: Provenance remains complete.
    """
    
    identity: str
    """Unique identifier for this report."""
    
    observed_scope: str
    """Scope being monitored for anomalies."""
    
    anomalies: tuple[Anomaly, ...] = ()
    """Collection of identified anomalies."""
    
    total_deviation: float = 0.0
    """Total deviation across all anomalies."""
    
    recommendations: tuple[str, ...] = ()
    """Suggested investigations or remediations."""
    
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
        anomalies: tuple[Anomaly, ...] = (),
        total_deviation: float = 0.0,
        recommendations: tuple[str, ...] = (),
        provenance: Optional[dict[str, str]] = None,
    ) -> AnomalyReport:
        """
        Create a new anomaly report.
        
        Args:
            observed_scope: Scope being monitored
            anomalies: Collection of identified anomalies
            total_deviation: Total deviation across all anomalies
            recommendations: Suggested investigations or remediations
            provenance: Optional provenance dictionary
            
        Returns:
            New AnomalyReport instance with deterministic identity
        """
        import hashlib
        
        # Create deterministic identity based on content
        identity_content = f"report:anom:{observed_scope}"
        identity_hash = hashlib.sha256(identity_content.encode()).hexdigest()[:16]
        
        return cls(
            identity=f"report:anomaly:{identity_hash}",
            observed_scope=observed_scope,
            anomalies=anomalies,
            total_deviation=total_deviation,
            recommendations=recommendations,
            provenance=provenance or {},
        )
    
    @property
    def highest_severity(self) -> str:
        """Get the highest severity among all anomalies."""
        if not self.anomalies:
            return "normal"
        
        severity_order = {"critical": 3, "warning": 2, "info": 1}
        max_sev = 1
        
        for anomaly in self.anomalies:
            current = severity_order.get(anomaly.severity, 0)
            if current > max_sev:
                max_sev = current
        
        return {3: "critical", 2: "warning", 1: "info"}.get(max_sev, "normal")
    
    def to_dict(self) -> dict[str, Any]:
        """Convert report to dictionary."""
        return {
            "identity": self.identity,
            "observed_scope": self.observed_scope,
            "anomalies": [a.to_dict() for a in self.anomalies],
            "total_deviation": self.total_deviation,
            "recommendations": list(self.recommendations),
            "limitations": list(self.limitations),
            "provenance": dict(self.provenance),
        }
    
    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> AnomalyReport:
        """Create report from dictionary."""
        return cls(
            identity=data["identity"],
            observed_scope=data["observed_scope"],
            anomalies=tuple(Anomaly.from_dict(a) for a in data.get("anomalies", [])),
            total_deviation=float(data.get("total_deviation", 0.0)),
            recommendations=tuple(data.get("recommendations", [])),
            limitations=tuple(data.get("limitations", [])),
            provenance=dict(data.get("provenance", {})),
        )