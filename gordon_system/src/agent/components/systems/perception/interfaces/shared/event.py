# Perception Interface Event - Phase 5.2.5
# =========================================

"""
Perception Interface Event: Observational communication from the interface.

Interface Events:
- Represent observable communication or service state transitions
- Preserve originating Interface, session or subscription identity  
- Preserve ordering and revision metadata where applicable
- Shall not silently execute consumer actions
- Preserve authorization constraints
- Remain immutable

EVENT-LAW-001: Every Interface Event shall represent an observable communication or service state transition.
EVENT-LAW-002: Every Event shall preserve originating Interface, session or subscription identity.
EVENT-LAW-003: Events shall preserve ordering and revision metadata where applicable.
EVENT-LAW-004: Interface Events shall not silently execute consumer actions.
EVENT-LAW-005: Event publication shall preserve authorization constraints.
EVENT-LAW-006: Events shall remain immutable.
EVENT-LAW-007: Event history shall remain inspectable.
EVENT-LAW-008: Event publication shall remain deterministic.
"""

from __future__ import annotations

import time as _time
from dataclasses import dataclass, field
from typing import Dict, List, Tuple, Optional, Any, Set
import uuid


# =============================================================================
# EVENT KINDS (per interface)
# =============================================================================


class EventKind:
    """Categories of event kinds."""
    
    # Sensors Interface Events
    EVIDENCE_PUBLISHED = "evidence_published"
    SENSOR_STATUS_CHANGE = "sensor_status_change"
    ACQUISITION_FAILURE = "acquisition_failure"
    
    # Workspace Interface Events
    PROJECTION_PUBLISHED = "projection_published"
    SNAPSHOT_PUBLISHED = "snapshot_published"
    ARTIFACT_UPDATED = "artifact_updated"
    UPDATE_GAP_DETECTED = "update_gap_detected"
    
    # Memory Interface Events  
    ADMISSION_RESULT = "admission_result"
    CORRELATION_PRODUCED = "correlation_produced"
    
    # Knowledge Interface Events
    GROUNDING_PRODUCED = "grounding_produced"
    MISMATCH_DETECTED = "mismatch_detected"
    
    # Attention Interface Events
    ATTENTION_ASSIGNED = "attention_assigned"
    INSPECTION_REQUESTED = "inspection_requested"
    PRIORITY_CHANGED = "priority_changed"
    
    # Learning Interface Events
    PROPOSAL_REVIEWED = "proposal_reviewed"
    DEPLOYMENT_READY = "deployment_ready"
    
    # Identity Interface Events
    IDENTITY_ANCHOR = "identity_anchor"
    CONFLICT_DETECTED = "conflict_detected"
    
    # Reasoning Interface Events
    HYPOTHESIS_TESTED = "hypothesis_tested"
    CONTRADICTION_FOUND = "contradiction_found"
    CONFIRMATION_FOUND = "confirmation_found"
    
    # World Model Interface Events
    WORLD_STATE_UPDATED = "world_state_updated"
    EXPECTATION_MISMATCH = "expectation_mismatch"
    STATE_TRANSITION = "state_transition"
    
    # Coordination Interface Events
    COORDINATION_UPDATE = "coordination_update"
    DEPENDENCY_CHANGED = "dependency_changed"
    SYNC_COMPLETED = "sync_completed"
    
    # Governance Interface Events
    CERTIFICATION_RESULT = "certification_result"
    DRIFT_DETECTED = "drift_detected"
    COMPLIANCE_ISSUE = "compliance_issue"
    
    # External Interface Events
    PUBLICATION_PUBLISHED = "publication_published"
    SUBSCRIPTION_UPDATE = "subscription_update"
    SUBSCRIPTION_TERMINATED = "subscription_terminated"


# =============================================================================
# EVENT CONTEXT
# =============================================================================


@dataclass(frozen=True)
class EventContext:
    """
    Context information for an event.
    
    Fields:
        originating_interface: Which interface published the event
        session_id: Session context if applicable
        subscription_id: Subscription context if applicable  
        ordering_sequence: Sequence number for ordering
        revision: Revision associated with this event
    """
    originating_interface: str
    session_id: Optional[str] = None
    subscription_id: Optional[str] = None
    ordering_sequence: int = 0
    revision: int = 1


# =============================================================================
# INTERFACE EVENT
# =============================================================================


@dataclass(frozen=True)
class PerceptionInterfaceEvent:
    """
    Event published by an Interface.
    
    Fields:
        event_identity: Unique identifier for this event
        event_kind: The type of event (see EventKind)
        timestamp: When the event occurred
        context: Context information for ordering and correlation
        
    EVENT-LAW-001: Every Interface Event shall represent an observable communication or service state transition.
    EVENT-LAW-002: Every Event shall preserve originating Interface, session or subscription identity.
    EVENT-LAW-003: Events shall preserve ordering and revision metadata where applicable.
    EVENT-LAW-004: Interface Events shall not silently execute consumer actions.
    EVENT-LAW-005: Event publication shall preserve authorization constraints.
    EVENT-LAW-006: Events shall remain immutable.
    EVENT-LAW-007: Event history shall remain inspectable.
    EVENT_LAW-008: Event publication shall remain deterministic.
    """
    
    # Identity
    event_identity: str = field(default_factory=lambda: f"event:{uuid.uuid4().hex[:16]}")
    
    # Event kind
    event_kind: str  # Must be one of EventKind
    
    # Timestamp
    timestamp: float = field(default_factory=_time.time)
    
    # Context
    context: EventContext = field(default_factory=lambda: EventContext(originating_interface="unknown"))
    
    # Payload data specific to the event kind
    payload: Dict[str, Any] = field(default_factory=dict)
    
    @classmethod
    def create_sensor_evidence_published(
        cls,
        sensor_id: str,
        evidence_reference: str,
        modality: str,
        **kwargs
    ) -> "PerceptionInterfaceEvent":
        """Create an evidence published event for a sensor."""
        return cls(
            event_kind=EventKind.EVIDENCE_PUBLISHED,
            context=EventContext(originating_interface="sensors", revision=kwargs.get("revision", 1)),
            payload={
                "sensor_id": sensor_id,
                "evidence_reference": evidence_reference,
                "modality": modality,
                "timestamp": _time.time(),
            },
        )
    
    @classmethod
    def create_workspace_projection_published(
        cls,
        projection_identity: str,
        revision: int,
        **kwargs
    ) -> "PerceptionInterfaceEvent":
        """Create a workspace projection published event."""
        return cls(
            event_kind=EventKind.PROJECTION_PUBLISHED,
            context=EventContext(originating_interface="workspace", revision=revision),
            payload={
                "projection_identity": projection_identity,
                "revision": revision,
                "timestamp": _time.time(),
            },
        )
    
    @classmethod
    def create_admission_result(
        cls,
        submission_reference: str,
        outcome: str,
        **kwargs
    ) -> "PerceptionInterfaceEvent":
        """Create a memory admission result event."""
        return cls(
            event_kind=EventKind.ADMISSION_RESULT,
            context=EventContext(originating_interface="memory", revision=kwargs.get("revision", 1)),
            payload={
                "submission_reference": submission_reference,
                "outcome": outcome,
                "timestamp": _time.time(),
            },
        )
    
    @classmethod
    def create_grounding_produced(
        cls,
        request_reference: str,
        concept_candidates: List[Dict[str, Any]],
        **kwargs
    ) -> "PerceptionInterfaceEvent":
        """Create a knowledge grounding produced event."""
        return cls(
            event_kind=EventKind.GROUNDING_PRODUCED,
            context=EventContext(originating_interface="knowledge", revision=kwargs.get("revision", 1)),
            payload={
                "request_reference": request_reference,
                "concept_candidates": list(concept_candidates),
                "timestamp": _time.time(),
            },
        )
    
    @classmethod
    def create_world_state_updated(
        cls,
        world_state_revision: int,
        state_delta: Dict[str, Any],
        **kwargs
    ) -> "PerceptionInterfaceEvent":
        """Create a world model state updated event."""
        return cls(
            event_kind=EventKind.WORLD_STATE_UPDATED,
            context=EventContext(originating_interface="world_model", revision=world_state_revision),
            payload={
                "state_revision": world_state_revision,
                "state_delta": dict(state_delta),
                "timestamp": _time.time(),
            },
        )
    
    @classmethod
    def create_certification_result(
        cls,
        certification_type: str,
        result: str,
        **kwargs
    ) -> "PerceptionInterfaceEvent":
        """Create a governance certification result event."""
        return cls(
            event_kind=EventKind.CERTIFICATION_RESULT,
            context=EventContext(originating_interface="governance", revision=kwargs.get("revision", 1)),
            payload={
                "certification_type": certification_type,
                "result": result,
                "timestamp": _time.time(),
            },
        )
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "event_identity": self.event_identity,
            "event_kind": self.event_kind,
            "timestamp": self.timestamp,
            "context": {
                "originating_interface": self.context.originating_interface,
                "session_id": self.context.session_id,
                "subscription_id": self.context.subscription_id,
                "ordering_sequence": self.context.ordering_sequence,
                "revision": self.context.revision,
            },
            "payload": dict(self.payload),
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "PerceptionInterfaceEvent":
        """Create event from dictionary."""
        context_data = data.get("context", {})
        return cls(
            event_identity=data.get("event_identity", ""),
            event_kind=data.get("event_kind", ""),
            timestamp=float(data.get("timestamp", _time.time())),
            context=EventContext(
                originating_interface=context_data.get("originating_interface", "unknown"),
                session_id=context_data.get("session_id"),
                subscription_id=context_data.get("subscription_id"),
                ordering_sequence=int(context_data.get("ordering_sequence", 0)),
                revision=int(context_data.get("revision", 1)),
            ),
            payload=dict(data.get("payload", {})),
        )


# =============================================================================
# SENSOR EVENTS
# =============================================================================


@dataclass(frozen=True)
class SensorStatusEvent:
    """
    Event describing a sensor status change.
    
    Fields:
        sensor_id: The sensor that changed status
        previous_status: What the status was before
        new_status: What the status is now
        timestamp: When the change occurred
        reason: Why the status changed (if known)
    """
    sensor_id: str
    previous_status: str
    new_status: str
    timestamp: float = field(default_factory=_time.time)
    reason: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "sensor_id": self.sensor_id,
            "previous_status": self.previous_status,
            "new_status": self.new_status,
            "timestamp": self.timestamp,
            "reason": self.reason,
        }


@dataclass(frozen=True)
class AcquisitionFailureEvent:
    """
    Event describing a sensor acquisition failure.
    
    Fields:
        session_id: The acquisition session that failed
        sensor_id: The sensor involved
        error_kind: What kind of failure occurred
        timestamp: When the failure occurred
    """
    session_id: str
    sensor_id: str
    error_kind: str
    timestamp: float = field(default_factory=_time.time)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "session_id": self.session_id,
            "sensor_id": self.sensor_id,
            "error_kind": self.error_kind,
            "timestamp": self.timestamp,
        }


# =============================================================================
# WORKSPACE EVENTS
# =============================================================================


@dataclass(frozen=True)
class UpdateGapEvent:
    """
    Event describing a gap in the update stream.
    
    Fields:
        subscription_id: Which subscription had the gap
        gap_start_revision: The revision where the gap starts
        gap_end_revision: The revision where the gap ends (exclusive)
        missing_count: How many revisions are missing
        timestamp: When the gap was detected
    """
    subscription_id: str
    gap_start_revision: int
    gap_end_revision: int
    missing_count: int
    timestamp: float = field(default_factory=_time.time)
    
    @property
    def is_minor_gap(self) -> bool:
        """Check if this is a minor gap (small number of missing revisions)."""
        return self.missing_count <= 3
    
    @property
    def is_major_gap(self) -> bool:
        """Check if this is a major gap."""
        return self.missing_count > 3
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "subscription_id": self.subscription_id,
            "gap_start_revision": self.gap_start_revision,
            "gap_end_revision": self.gap_end_revision,
            "missing_count": self.missing_count,
            "timestamp": self.timestamp,
        }


# =============================================================================
# MEMORY EVENTS
# =============================================================================


@dataclass(frozen=True)
class MemoryCorrelationEvent:
    """
    Event describing a new memory correlation.
    
    Fields:
        perception_artifact: Reference to the perception artifact
        memory_artifact: Reference to the correlated memory artifact
        relation_type: What kind of relationship was proposed
        confidence: Confidence in the correlation (0.0-1.0)
        timestamp: When the correlation was produced
    """
    perception_artifact: str
    memory_artifact: str
    relation_type: str
    confidence: float = 1.0
    timestamp: float = field(default_factory=_time.time)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "perception_artifact": self.perception_artifact,
            "memory_artifact": self.memory_artifact,
            "relation_type": self.relation_type,
            "confidence": self.confidence,
            "timestamp": self.timestamp,
        }


# =============================================================================
# COORDINATION EVENTS
# =============================================================================


@dataclass(frozen=True)
class CoordinationStatusEvent:
    """
    Event describing a coordination status change.
    
    Fields:
        component_id: Which component's status changed
        previous_status: What the status was before
        new_status: What the status is now
        timestamp: When the change occurred
        details: Additional status information
    """
    component_id: str
    previous_status: str
    new_status: str
    timestamp: float = field(default_factory=_time.time)
    details: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "component_id": self.component_id,
            "previous_status": self.previous_status,
            "new_status": self.new_status,
            "timestamp": self.timestamp,
            "details": dict(self.details),
        }


# =============================================================================
# EXTERNAL EVENTS
# =============================================================================


@dataclass(frozen=True)
class SubscriptionTerminationEvent:
    """
    Event describing a subscription termination.
    
    Fields:
        subscription_id: The terminated subscription
        reason: Why it was terminated
        timestamp: When the termination occurred
        grace_period_seconds: How long until cleanup is complete
    """
    subscription_id: str
    reason: str
    timestamp: float = field(default_factory=_time.time)
    grace_period_seconds: int = 0
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "subscription_id": self.subscription_id,
            "reason": self.reason,
            "timestamp": self.timestamp,
            "grace_period_seconds": self.grace_period_seconds,
        }


__all__ = [
    # Event kinds
    "EventKind",
    
    # Context
    "EventContext",
    
    # Core event type
    "PerceptionInterfaceEvent",
    
    # Interface-specific events
    "SensorStatusEvent",
    "AcquisitionFailureEvent",
    "UpdateGapEvent",
    "MemoryCorrelationEvent",
    "CoordinationStatusEvent",
    "SubscriptionTerminationEvent",
]