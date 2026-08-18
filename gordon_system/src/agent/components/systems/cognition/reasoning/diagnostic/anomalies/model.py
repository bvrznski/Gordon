# Anomaly Model - Phase 7.39
# =========================

"""
Anomaly management models.

Defines:
    - AnomalyModel: A model of an observed anomaly
    - AnomalyClassification: How the anomaly is classified
    - AnomalySeverity: The impact level of the anomaly
"""

from __future__ import annotations

import time
import uuid
from dataclasses import dataclass, field
from typing import Dict, List, Tuple, Optional, Any
from enum import Enum, auto


class AnomalyKind(Enum):
    """Kinds of anomalies."""
    
    BEHAVIORAL = "behavioral"       # Behavior deviation from expected
    STRUCTURAL = "structural"       # Structural deviation (e.g., topology)
    TEMPORAL = "temporal"           # Timing or order violation
    SEMANTIC = "semantic"           # Meaning or interpretation error
    STATISTICAL = "statistical"     # Statistical outlier


class AnomalyClassification(Enum):
    """Classification categories for anomalies."""
    
    NOVEL = "novel"                 # Never seen before
    RECURRING = "recurring"         # Seen before with same cause
    CASCADING = "cascading"         # Caused by upstream failure
    SYMPTOMATIC = "symptomatic"     # Symptom of root cause elsewhere


class AnomalySeverity(Enum):
    """Severity levels for anomalies."""
    
    INFO = "info"           # Observation only, no impact
    LOW = "low"             # Minor deviation, acceptable behavior
    MEDIUM = "medium"       # Significant deviation, requires attention
    HIGH = "high"           # Critical deviation, immediate action required
    CRITICAL = "critical"   # System failure imminent or occurring


@dataclass(frozen=True)
class AnomalyModel:
    """
    Model of an observed anomaly.
    
    Each anomaly includes:
        - Identity and classification
        - Expected vs observed behavior
        - Severity assessment
        - Provenance tracking
    """
    
    anomaly_id: str
    semantic_identity: str  # Stable identity across occurrences
    
    # Classification
    anomaly_kind: AnomalyKind
    anomaly_classification: AnomalyClassification
    
    # Behavior comparison
    expected_behavior: Dict[str, Any]
    observed_behavior: Dict[str, Any]
    
    # Severity and confidence
    severity: AnomalySeverity = AnomalySeverity.LOW
    classification_confidence: float = 1.0  # 0.0 to 1.0
    
    # Context
    affected_components: List[str] = field(default_factory=list)
    timestamp_utc: float = field(default_factory=time.time)
    
    # Provenance
    source_id: Optional[str] = None  # Source observation ID
    context: Dict[str, Any] = field(default_factory=dict)
    
    @property
    def deviation(self) -> str:
        """Describe the nature of the anomaly."""
        return "behavioral" if self.anomaly_kind == AnomalyKind.BEHAVIORAL else \
               "structural" if self.anomaly_kind == AnomalyKind.STRUCTURAL else \
               "temporal" if self.anomaly_kind == AnomalyKind.TEMPORAL else \
               "semantic" if self.anomaly_kind == AnomalyKind.SEMANTIC else "statistical"
    
    @property
    def is_critical(self) -> bool:
        """Check if anomaly is critical."""
        return self.severity in (AnomalySeverity.HIGH, AnomalySeverity.CRITICAL)
    
    @classmethod
    def create(
        cls,
        expected_behavior: Dict[str, Any],
        observed_behavior: Dict[str, Any],
        anomaly_kind: AnomalyKind = AnomalyKind.BEHAVIORAL,
        severity: AnomalySeverity = AnomalySeverity.LOW,
        classification_confidence: float = 1.0,
        affected_components: Optional[List[str]] = None,
        context: Optional[Dict[str, Any]] = None,
    ) -> AnomalyModel:
        """Create a new anomaly model."""
        return cls(
            anomaly_id=f"anomaly:{uuid.uuid4().hex[:16]}",
            semantic_identity=f"{anomaly_kind.value}:{uuid.uuid4().hex[:8]}",
            anomaly_kind=anomaly_kind,
            anomaly_classification=AnomalyClassification.NOVEL,
            expected_behavior=expected_behavior,
            observed_behavior=observed_behavior,
            severity=severity,
            classification_confidence=classification_confidence,
            affected_components=affected_components or [],
            context=context or {},
        )
    
    def update_classification(
        self,
        new_classification: AnomalyClassification,
        new_confidence: Optional[float] = None,
    ) -> AnomalyModel:
        """Return updated anomaly with new classification."""
        kwargs = {
            "anomaly_classification": new_classification,
        }
        if new_confidence is not None:
            kwargs["classification_confidence"] = new_confidence
        return dataclass_replace(self, **kwargs)


@dataclass(frozen=True)
class AnomalySetIdentity:
    """
    Identity for a set of anomalies.
    
    Allows grouping and comparison of anomaly sets.
    """
    
    set_id: str
    semantic_identity: str
    created_at_utc: float
    
    @classmethod
    def create(cls, semantic_identity: str) -> AnomalySetIdentity:
        """Create an anomaly set identity."""
        return cls(
            set_id=f"anomaly_set:{uuid.uuid4().hex[:16]}",
            semantic_identity=semantic_identity,
            created_at_utc=time.time(),
        )


def dataclass_replace(instance: Any, **kwargs: Any) -> Any:
    """Simple dataclass replace helper for frozen instances."""
    return instance.__class__(**{**instance.__dict__, **kwargs})


__all__ = [
    "AnomalyKind",
    "AnomalyClassification", 
    "AnomalySeverity",
    "AnomalyModel",
    "AnomalySetIdentity",
]