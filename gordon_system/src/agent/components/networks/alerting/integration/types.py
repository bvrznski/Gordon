# Integration Types for AlertingNetwork - Phase 4.1.6
# ======================================================
#
# Type definitions supporting the integration contracts.
# These are NOT contracts but helper types used by contract implementations.

"""
Integration Types for AlertingNetwork - Phase 4.1.6

These types support the contract layer by providing:
- Standardized data structures
- Serialization formats  
- Common conventions

TYPES:
======

AssessmentDelivery: Complete assessment delivery record with metadata
ContextSnapshot: Immutable snapshot of alerting context values
SignalBatch: Batch of signals for history-based assessment
TracingEvent: Trace event for diagnostics

These types are used by both contract providers and consumers.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, Optional, Tuple
from datetime import datetime
from enum import Enum


# =============================================================================
# ASSESSMENT DELIVERY TYPES
# =============================================================================

class AssessmentDeliveryMode(Enum):
    """
    Mode of assessment delivery to consumers.
    
    IMMEDIATE: Deliver as soon as ready (default)
    BATCHED: Batch multiple assessments for efficiency
    DEFERRED: Defer for later processing
    DROPPABLE: May be dropped if consumer overloaded
    
    CONSUMER IMPACT:
        - immediate: Best latency, worst throughput
        - batched: Good balance of latency/throughput
        - deferred: High throughput, acceptable latency
        - droppable: Max throughput, may lose data under load
    """
    
    IMMEDIATE = "immediate"
    BATCHED = "batched"
    DEFERRED = "deferred"
    DROPPABLE = "droppable"


@dataclass(frozen=True, slots=True)
class AssessmentDelivery:
    """Complete assessment delivery record with metadata."""
    
    delivery_id: str
    assessment: Dict[str, Any]
    timestamp: datetime
    mode: AssessmentDeliveryMode
    consumer_id: Optional[str] = None
    
    @property
    def is_droppable(self) -> bool:
        return self.mode == AssessmentDeliveryMode.DROPPABLE


# =============================================================================
# CONTEXT TYPES
# =============================================================================

@dataclass(frozen=True, slots=True)
class ContextSnapshot:
    """Immutable snapshot of alerting context values."""
    
    active_focus: Optional[float] = None
    task_criticality: Optional[float] = None
    execution_pressure: Optional[float] = None
    
    def is_empty(self) -> bool:
        return all(v is None for v in [self.active_focus, self.task_criticality, self.execution_pressure])
    
    def to_dict(self) -> Dict[str, Optional[float]]:
        return {
            "active_focus": self.active_focus,
            "task_criticality": self.task_criticality,
            "execution_pressure": self.execution_pressure,
        }


# =============================================================================
# SIGNAL TYPES
# =============================================================================

@dataclass(frozen=True, slots=True)
class SignalBatch:
    """Batch of signals for history-based assessment."""
    
    signals: Tuple[Dict[str, Any], ...]
    before_timestamp: Optional[datetime] = None
    count: int = field(default=0, init=False)
    
    def __post_init__(self):
        object.__setattr__(self, "count", len(self.signals))
    
    @property
    def is_empty(self) -> bool:
        return self.count == 0
    
    @property
    def oldest_timestamp(self) -> Optional[datetime]:
        if not self.signals:
            return None
        first = self.signals[0]
        ts_str = first.get("timestamp")
        return datetime.fromisoformat(ts_str) if isinstance(ts_str, str) else None
    
    @property
    def newest_timestamp(self) -> Optional[datetime]:
        if not self.signals or len(self.signals) < 2:
            return self.oldest_timestamp
        last = self.signals[-1]
        ts_str = last.get("timestamp")
        return datetime.fromisoformat(ts_str) if isinstance(ts_str, str) else None


# =============================================================================
# DIAGNOSTICS TYPES
# =============================================================================

@dataclass(frozen=True, slots=True)
class TracingEvent:
    """Trace event for diagnostics."""
    
    event_type: str
    timestamp: datetime
    data: Dict[str, Any] = field(default_factory=dict)
    trace_id: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "event_type": self.event_type,
            "timestamp": self.timestamp.isoformat() if isinstance(self.timestamp, datetime) else str(self.timestamp),
            "data": dict(self.data),
            "trace_id": self.trace_id,
        }


# =============================================================================
# COMMON CONSTANTS
# =============================================================================

# Valid assessment field ranges
ASSESSMENT_VALUE_MIN = 0.0
ASSESSMENT_VALUE_MAX = 1.0

# Required assessment fields
REQUIRED_ASSESSMENT_FIELDS = (
    "demand_score",
    "confidence", 
    "level",
    "recommendation",
    "features",
)

# Valid alert levels
VALID_ALERT_LEVELS = frozenset({
    "NEGLIGIBLE",
    "LOW", 
    "MODERATE",
    "HIGH",
    "CRITICAL",
})

# Valid recommendations  
VALID_RECOMMENDATIONS = frozenset({
    "IGNORE",
    "OBSERVE",
    "REQUEST_ATTENTION",
    "REQUEST_URGENT_ATTENTION",
})