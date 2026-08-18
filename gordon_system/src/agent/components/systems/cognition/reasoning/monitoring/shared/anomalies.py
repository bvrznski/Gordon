# Monitoring Anomaly Contract - Phase 7.22
# =========================================

"""
Canonical Operational Anomaly.

Anomalies represent unexpected behavior or state deviations.
"""

from __future__ import annotations

import time
import uuid
from dataclasses import dataclass, field
from typing import Dict, List, Tuple, Optional, Any
from enum import Enum, auto


class AnomalySeverity(Enum):
    """Severity levels for anomalies."""
    
    DEBUG = "debug"                             # Informational only
    INFO = "info"                               # Notable but expected
    WARNING = "warning"                         # Deviation from normal
    ERROR = "error"                             # Significant deviation
    CRITICAL = "critical"                       # System-critical issue


class AnomalyType(Enum):
    """Types of anomalies."""
    
    STATE_DEVIATION = "state_deviation"         # Unexpected state
    EXECUTION_DIVERGENCE = "execution_divergence"  # Execution not matching plan
    RESOURCE_ANOMALY = "resource_anomaly"       # Resource usage anomaly
    COMMUNICATION_FAILURE = "communication_failure"  # Communication issue
    MISSING_OBSERVATION = "missing_observation"   # Expected observation missing
    BEHAVIOR_DEVIATION = "behavior_deviation"   # Unexpected behavior pattern


@dataclass(frozen=True)
class OperationalAnomaly:
    """
    An anomaly detected during monitoring.
    
    An anomaly contains:
        - Identity and provenance
        - Anomaly type and severity
        - Supporting observations
        - Context and detection evidence
    
    Anomalies remain explicit and inspectable.
    """
    
    # Identity
    anomaly_id: str                           # Unique anomaly identifier
    
    # Classification
    anomaly_type: AnomalyType                 # What kind of anomaly?
    severity: AnomalySeverity = AnomalySeverity.INFO  # How severe is it?
    
    # Description
    description: str                         # Human-readable explanation
    
    # Supporting observations
    supporting_observations: List[str] = field(default_factory=list)  # Observation IDs
    
    # Detection evidence
    detection_method: str = "unknown"        # How was this detected?
    confidence: float = 0.5                  # Confidence in anomaly detection
    
    # Context
    context: Dict[str, Any] = field(default_factory=dict)
    
    # Timing
    detected_at_utc: float = field(default_factory=time.time)
    first_seen_utc: Optional[float] = None   # When first observed (if known)
    
    # Provenance
    source_descriptor_id: Optional[str] = None
    origin_context: str = "unknown"
    
    @property
    def age_seconds(self) -> float:
        """Calculate how long since detection."""
        return time.time() - self.detected_at_utc
    
    @property
    def is_critical(self) -> bool:
        """Check if anomaly is critical."""
        return self.severity == AnomalySeverity.CRITICAL
    
    @property
    def is_error(self) -> bool:
        """Check if anomaly is an error."""
        return self.severity == AnomalySeverity.ERROR
    
    def add_observation_reference(self, observation_id: str) -> OperationalAnomaly:
        """Add a supporting observation reference."""
        new_observations = list(self.supporting_observations)
        if observation_id not in new_observations:
            new_observations.append(observation_id)
        
        return dataclass_replace(
            self,
            supporting_observations=new_observations,
        )
    
    def update_severity(self, new_severity: AnomalySeverity) -> OperationalAnomaly:
        """Update anomaly severity."""
        return dataclass_replace(
            self,
            severity=new_severity,
        )
    
    @classmethod
    def create(
        cls,
        anomaly_type: AnomalyType,
        description: str,
        supporting_observations: Optional[List[str]] = None,
        severity: AnomalySeverity = AnomalySeverity.INFO,
        detection_method: str = "unknown",
        confidence: float = 0.5,
        source_descriptor_id: Optional[str] = None,
    ) -> OperationalAnomaly:
        """Create a new anomaly."""
        return cls(
            anomaly_id=f"anomaly:{uuid.uuid4().hex[:16]}",
            anomaly_type=anomaly_type,
            description=description,
            severity=severity,
            supporting_observations=supporting_observations or [],
            detection_method=detection_method,
            confidence=confidence,
            detected_at_utc=time.time(),
            source_descriptor_id=source_descriptor_id,
        )


@dataclass(frozen=True)
class AnomalySet:
    """
    A collection of anomalies.
    
    Provides operations for anomaly set management.
    """
    
    # Identity
    anomaly_set_id: str                       # Unique set identifier
    
    # Anomalies
    anomalies: List[OperationalAnomaly] = field(default_factory=list)
    
    # Aggregated state
    max_severity: AnomalySeverity = AnomalySeverity.DEBUG
    total_count: int = 0
    
    # Timing
    created_at_utc: float = field(default_factory=time.time)
    
    # Provenance
    source_descriptor_id: Optional[str] = None
    
    @property
    def has_critical(self) -> bool:
        """Check if any anomalies are critical."""
        return any(a.severity == AnomalySeverity.CRITICAL for a in self.anomalies)
    
    @property
    def has_error(self) -> bool:
        """Check if any anomalies are errors."""
        return any(a.severity == AnomalySeverity.ERROR for a in self.anomalies)
    
    def get_by_type(self, anomaly_type: AnomalyType) -> List[OperationalAnomaly]:
        """Get all anomalies of a specific type."""
        return [a for a in self.anomalies if a.anomaly_type == anomaly_type]
    
    def get_by_severity(self, severity: AnomalySeverity) -> List[OperationalAnomaly]:
        """Get all anomalies at a specific severity level."""
        return [a for a in self.anomalies if a.severity == severity]
    
    def add_anomaly(self, anomaly: OperationalAnomaly) -> AnomalySet:
        """Add an anomaly to the set."""
        new_anomalies = list(self.anomalies)
        
        # Check if we already have this anomaly (by ID or type + description)
        existing_ids = {a.anomaly_id for a in new_anomalies}
        if anomaly.anomaly_id not in existing_ids:
            new_anomalies.append(anomaly)
        
        return dataclass_replace(
            self,
            anomalies=new_anomalies,
            total_count=len(new_anomalies),
            # Recalculate max severity
            max_severity=self._calculate_max_severity(new_anomalies),
        )
    
    def _calculate_max_severity(self, anomalies: List[OperationalAnomaly]) -> AnomalySeverity:
        """Calculate the maximum severity in a list."""
        if not anomalies:
            return AnomalySeverity.DEBUG
        
        severity_order = [
            AnomalySeverity.CRITICAL,
            AnomalySeverity.ERROR,
            AnomalySeverity.WARNING,
            AnomalySeverity.INFO,
            AnomalySeverity.DEBUG,
        ]
        
        for sev in severity_order:
            if any(a.severity == sev for a in anomalies):
                return sev
        
        return AnomalySeverity.DEBUG
    
    @classmethod
    def create(
        cls,
        source_descriptor_id: Optional[str] = None,
    ) -> AnomalySet:
        """Create a new anomaly set."""
        return cls(
            anomaly_set_id=f"anomalyset:{uuid.uuid4().hex[:16]}",
            source_descriptor_id=source_descriptor_id,
        )


def dataclass_replace(instance: Any, **kwargs: Any) -> Any:
    """Simple dataclass replace helper for frozen instances."""
    return instance.__class__(**{**instance.__dict__, **kwargs})


__all__ = [
    "OperationalAnomaly",
    "AnomalySet",
    "AnomalySeverity",
    "AnomalyType",
]