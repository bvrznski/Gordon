# Perception Event Projection - Phase 5.2.4
# ==========================================

"""
Event Projection: Exposes observed state transitions.

An Event Projection exposes observed state transitions. It may include Event
identity, kind, participants, temporal order, spatial relations, source Modalities,
supporting evidence, missing intervals, conflicts, alternative Event structures,
confidence, uncertainty.

An Event Projection shall not silently encode causality.
"""

from __future__ import annotations

import time as _time
from dataclasses import dataclass, field
from typing import Dict, List, Tuple, Optional, Any
import uuid


# =============================================================================
# EVENT PROJECTION
# =============================================================================


@dataclass(frozen=True)
class EventProjection:
    """
    Projection of observed state transitions.
    
    An Event Projection exposes observed state transitions only. It does not
    silently encode causality, intent, or desirability.
    
    Fields:
        projection_identity:    Unique identifier for this projection
        source_events:          IDs of source events used
        projected_events:       Events in this view (may include fused)
        participants:           Event participants
        temporal_relations:     Temporal ordering between events
        spatial_relations:      Spatial relations between event elements
        source_modalities:      Modalities that contributed evidence
        supporting_evidence:    Evidence records
        missing_intervals:      Time gaps in observation
        conflicts:              Conflicting interpretations
        alternatives:           Alternative Event structures
        confidence:             Overall projection confidence
        uncertainty:            Overall projection uncertainty
        limitations:            Limitations affecting view
        freshness_state:        How current is the projection
        revision:               Projection revision number
    """
    
    projection_identity: str
    
    # Source references
    source_events: Tuple[str, ...] = field(default_factory=tuple)
    
    # Event content
    projected_events: Tuple[Dict[str, Any], ...] = field(default_factory=tuple)
    
    # Participant information
    participants: Tuple[Dict[str, Any], ...] = field(default_factory=tuple)  # participant_id -> roles
    
    # Relations
    temporal_relations: Tuple[Dict[str, Any], ...] = field(default_factory=tuple)   # before, after, simultaneous
    spatial_relations: Tuple[Dict[str, Any], ...] = field(default_factory=tuple)    # near, far, same_location
    
    # Evidence and source info
    source_modalities: Tuple[str, ...] = field(default_factory=tuple)
    supporting_evidence: Tuple[Dict[str, Any], ...] = field(default_factory=tuple)  # evidence_id -> confidence
    
    # Temporal gaps
    missing_intervals: Tuple[Dict[str, float], ...] = field(default_factory=tuple)
    
    # Conflict and ambiguity
    conflicts: Tuple[Dict[str, Any], ...] = field(default_factory=tuple)
    alternatives: Tuple[Dict[str, Any], ...] = field(default_factory=tuple)
    
    # Quality metrics
    confidence: float = 1.0
    uncertainty: float = 0.0
    
    # Limitations
    limitations: Tuple[Dict[str, Any], ...] = field(default_factory=tuple)
    
    # Freshness and revision
    freshness_state: str = "current"
    freshness_timestamp_utc: float = field(default_factory=_time.time)
    source_revision_reference: Optional[str] = None
    projection_revision: int = 1
    
    @classmethod
    def create(
        cls,
        event_data: List[Dict[str, Any]],
        modalities: Optional[List[str]] = None,
        confidence: float = 1.0,
        uncertainty: float = 0.0,
    ) -> "EventProjection":
        """
        Create a new Event Projection.
        
        Args:
            event_data: Event records with kind, participants, timing
            modalities: Modalities that observed these events
            confidence: Overall projection confidence (0.0-1.0)
            uncertainty: Overall projection uncertainty (0.0-1.0)
            
        Returns:
            New EventProjection instance
        """
        return cls(
            projection_identity=f"event_projection:{uuid.uuid4().hex[:24]}",
            projected_events=tuple(event_data),
            source_modalities=tuple(modalities or []),
            confidence=confidence,
            uncertainty=uncertainty,
        )
    
    @classmethod
    def command_execution_event(
        cls,
        command_id: str,
        process_id: Optional[str] = None,
        console_output: Optional[List[Dict[str, Any]]] = None,
        filesystem_changes: Optional[List[Dict[str, Any]]] = None,
        network_activity: Optional[List[Dict[str, Any]]] = None,
    ) -> "EventProjection":
        """
        Create an Event Projection for a command execution event.
        
        Args:
            command_id: ID of the command being executed
            process_id: ID of the created process (if any)
            console_output: Console output records
            filesystem_changes: Filesystem modification records
            network_activity: Network activity records
            
        Returns:
            New EventProjection representing command execution
        """
        event_data = {
            "event_kind": "command_execution",
            "event_id": f"event:{uuid.uuid4().hex[:16]}",
            "timestamp_utc": _time.time(),
            "command": command_id,
            "process_id": process_id,
            "status": "in_progress",  # or completed, failed
        }
        
        events = [event_data]
        
        if console_output:
            for output in console_output:
                events.append({
                    "event_kind": "console_output",
                    "event_id": f"event:{uuid.uuid4().hex[:16]}",
                    **output,
                })
        
        if filesystem_changes:
            for change in filesystem_changes:
                events.append({
                    "event_kind": "filesystem_change",
                    "event_id": f"event:{uuid.uuid4().hex[:16]}",
                    **change,
                })
        
        if network_activity:
            for activity in network_activity:
                events.append({
                    "event_kind": "network_activity",
                    "event_id": f"event:{uuid.uuid4().hex[:16]}",
                    **activity,
                })
        
        return cls(
            projection_identity=f"event_projection:{uuid.uuid4().hex[:24]}",
            projected_events=tuple(events),
            source_modalities=("console", "filesystem", "network"),
            confidence=0.85,
            uncertainty=0.15,
        )
    
    @property
    def is_valid(self) -> bool:
        """Check if the projection has valid data."""
        if not self.projection_identity or len(self.projection_identity) == 0:
            return False
        if not (0.0 <= self.confidence <= 1.0):
            return False
        if not (0.0 <= self.uncertainty <= 1.0):
            return False
        
        # At least one event is required for non-empty projections
        if len(self.projected_events) == 0:
            # Empty projection is valid for "no events" case
            return True
        
        return True


# =============================================================================
# EVENT SEQUENCE PROJECTION
# =============================================================================


@dataclass(frozen=True)
class EventSequenceProjection:
    """
    Projection of an ordered sequence of Events.
    
    Projection shall preserve partial order when total ordering is unsupported.
    
    Fields:
        sequence_identity:      Unique identifier for this sequence projection
        source_events:          IDs of source events used
        event_ordering:         Temporal ordering information
        partial_order_graph:    Graph representation of ordering (for partial orders)
        overlapping_events:     Events with overlapping time spans
        missing_intervals:      Time gaps in the sequence
        concurrent_events:      Events that occurred concurrently
        unresolved_ordering:    Ordering that could not be determined
        confidence:             Confidence in the ordering
        uncertainty:            Uncertainty about the ordering
    """
    
    sequence_identity: str
    
    # Source references
    source_events: Tuple[str, ...] = field(default_factory=tuple)
    
    # Event records (may include partial information)
    events: Tuple[Dict[str, Any], ...] = field(default_factory=tuple)
    
    # Ordering representation
    event_ordering: Tuple[Dict[str, Any], ...] = field(default_factory=tuple)  # before/after relations
    
    partial_order_graph: Dict[str, List[str]] = field(
        default_factory=dict
    )  # event_id -> events that must come after
    
    # Timing information
    overlapping_events: Tuple[Tuple[str, str], ...] = field(default_factory=tuple)
    
    missing_intervals: Tuple[Dict[str, float], ...] = field(default_factory=tuple)
    
    concurrent_events: Tuple[Tuple[str, str], ...] = field(default_factory=tuple)
    
    unresolved_ordering: Tuple[Tuple[str, str], ...] = field(default_factory=tuple)
    
    # Quality metrics
    confidence: float = 1.0
    uncertainty: float = 0.0
    
    @classmethod
    def create_sequence(
        cls,
        events: List[Dict[str, Any]],
        ordering: Optional[List[Tuple[str, str]]] = None,  # (before_event_id, after_event_id)
        confidence: float = 1.0,
        uncertainty: float = 0.0,
    ) -> "EventSequenceProjection":
        """
        Create a new Event Sequence Projection.
        
        Args:
            events: Event records with IDs and timing
            ordering: List of (before, after) tuples for ordering constraints
            confidence: Confidence in the sequence
            uncertainty: Uncertainty about the sequence
            
        Returns:
            New EventSequenceProjection instance
        """
        event_ids = [e.get("event_id", f"event:{uuid.uuid4().hex[:16]}") for e in events]
        
        # Build partial order graph from ordering constraints
        partial_order_graph: Dict[str, List[str]] = {}
        for before_id, after_id in (ordering or []):
            if before_id not in partial_order_graph:
                partial_order_graph[before_id] = []
            partial_order_graph[before_id].append(after_id)
        
        return cls(
            sequence_identity=f"event_sequence:{uuid.uuid4().hex[:24]}",
            source_events=tuple(event_ids),
            events=tuple(events),
            event_ordering=tuple({"before": b, "after": a} for b, a in (ordering or [])),
            partial_order_graph=partial_order_graph,
            confidence=confidence,
            uncertainty=uncertainty,
        )
    
    @classmethod
    def from_timestamps(
        cls,
        events: List[Dict[str, Any]],
    ) -> "EventSequenceProjection":
        """
        Create a sequence projection by sorting events by timestamp.
        
        Args:
            events: Event records with 'timestamp_utc' field
            
        Returns:
            New EventSequenceProjection with sorted order
        """
        # Sort events by timestamp
        sorted_events = sorted(events, key=lambda e: e.get("timestamp_utc", 0.0))
        
        # Build ordering (each event comes after the previous)
        ordering = []
        for i in range(len(sorted_events) - 1):
            ordering.append((sorted_events[i].get("event_id", "unknown"), 
                           sorted_events[i + 1].get("event_id", "unknown")))
        
        return cls.create_sequence(
            events=sorted_events,
            ordering=ordering,
            confidence=0.95,  # High confidence for timestamp-based ordering
            uncertainty=0.05,
        )
    
    @property
    def is_valid(self) -> bool:
        """Check if the sequence projection has valid data."""
        if not self.sequence_identity or len(self.sequence_identity) == 0:
            return False
        if not (0.0 <= self.confidence <= 1.0):
            return False
        
        # At least one event is required for non-empty sequences
        if len(self.events) == 0:
            return True
        
        return True


# =============================================================================
# PROJECTION BUILDER
# =============================================================================


class EventProjectionBuilder:
    """Mutable builder for constructing event projections."""
    
    def __init__(self):
        self._projection_identity: str = f"event_projection:{uuid.uuid4().hex[:24]}"
        self._source_events: List[str] = []
        self._events: List[Dict[str, Any]] = []
        self._participants: List[Dict[str, Any]] = []
        self._temporal_relations: List[Dict[str, Any]] = []
        self._spatial_relations: List[Dict[str, Any]] = []
        self._modalities: List[str] = []
        self._evidence: List[Dict[str, Any]] = []
        self._missing_intervals: List[Dict[str, float]] = []
        self._conflicts: List[Dict[str, Any]] = []
        self._alternatives: List[Dict[str, Any]] = []
        self._limitations: List[Dict[str, Any]] = []
        self._confidence: float = 1.0
        self._uncertainty: float = 0.0
    
    def set_identity(self, identity: str) -> "EventProjectionBuilder":
        """Set the projection identity."""
        self._projection_identity = identity
        return self
    
    def add_source_event(self, event_id: str) -> "EventProjectionBuilder":
        """Add a source event ID."""
        if event_id not in self._source_events:
            self._source_events.append(event_id)
        return self
    
    def add_event(self, event_data: Dict[str, Any]) -> "EventProjectionBuilder":
        """Add an event record."""
        self._events.append(dict(event_data))
        return self
    
    def add_participant(
        self,
        participant_id: str,
        roles: Tuple[str, ...],
    ) -> "EventProjectionBuilder":
        """Add a participant with its roles."""
        self._participants.append({
            "participant_id": participant_id,
            "roles": list(roles),
        })
        return self
    
    def add_temporal_relation(
        self,
        before_event: str,
        after_event: str,
        relation_type: str = "before",
    ) -> "EventProjectionBuilder":
        """Add a temporal ordering relation."""
        self._temporal_relations.append({
            "before": before_event,
            "after": after_event,
            "relation_type": relation_type,
        })
        return self
    
    def add_spatial_relation(
        self,
        event1: str,
        event2: str,
        spatial_relationship: Dict[str, Any],
    ) -> "EventProjectionBuilder":
        """Add a spatial relation between events."""
        self._spatial_relations.append({
            "event1": event1,
            "event2": event2,
            **spatial_relationship,
        })
        return self
    
    def add_modality(self, modality_id: str) -> "EventProjectionBuilder":
        """Add a contributing modality."""
        if modality_id not in self._modalities:
            self._modalities.append(modality_id)
        return self
    
    def add_evidence(
        self,
        evidence_data: Dict[str, Any],
    ) -> "EventProjectionBuilder":
        """Add supporting evidence."""
        self._evidence.append(dict(evidence_data))
        return self
    
    def add_missing_interval(self, start_time: float, end_time: float) -> "EventProjectionBuilder":
        """Add a missing time interval in observation."""
        self._missing_intervals.append({
            "start": start_time,
            "end": end_time,
            "duration_seconds": end_time - start_time,
        })
        return self
    
    def add_conflict(self, conflict: Dict[str, Any]) -> "EventProjectionBuilder":
        """Add a conflicting interpretation."""
        self._conflicts.append(dict(conflict))
        return self
    
    def add_alternative(self, alternative: Dict[str, Any]) -> "EventProjectionBuilder":
        """Add an alternative Event structure."""
        self._alternatives.append(dict(alternative))
        return self
    
    def add_limitation(
        self,
        limitation: Dict[str, Any],
    ) -> "EventProjectionBuilder":
        """Add a limitation affecting this projection."""
        self._limitations.append(dict(limitation))
        return self
    
    def set_confidence(self, confidence: float) -> "EventProjectionBuilder":
        """Set overall projection confidence (0.0-1.0)."""
        if not 0.0 <= confidence <= 1.0:
            raise ValueError(f"Confidence must be 0.0-1.0, got {confidence}")
        self._confidence = confidence
        return self
    
    def set_uncertainty(self, uncertainty: float) -> "EventProjectionBuilder":
        """Set overall projection uncertainty (0.0-1.0)."""
        if not 0.0 <= uncertainty <= 1.0:
            raise ValueError(f"Uncertainty must be 0.0-1.0, got {uncertainty}")
        self._uncertainty = uncertainty
        return self
    
    def set_freshness(self, state: str) -> "EventProjectionBuilder":
        """Set freshness state (current, recent, stale, expired)."""
        valid_states = ("current", "recent", "stale", "expired")
        if state not in valid_states:
            raise ValueError(f"Invalid freshness state: {state}")
        self._freshness_state = state
        return self
    
    def build(self) -> EventProjection:
        """Build an immutable EventProjection."""
        if len(self._events) == 0 and len(self._source_events) == 0:
            raise ValueError("At least one event or source event is required")
        
        return EventProjection(
            projection_identity=self._projection_identity,
            source_events=tuple(self._source_events),
            projected_events=tuple(dict(e) for e in self._events),
            participants=tuple(dict(p) for p in self._participants),
            temporal_relations=tuple(dict(r) for r in self._temporal_relations),
            spatial_relations=tuple(dict(r) for r in self._spatial_relations),
            source_modalities=tuple(self._modalities),
            supporting_evidence=tuple(dict(e) for e in self._evidence),
            missing_intervals=tuple(dict(i) for i in self._missing_intervals),
            conflicts=tuple(dict(c) for c in self._conflicts),
            alternatives=tuple(dict(a) for a in self._alternatives),
            limitations=tuple(dict(l) for l in self._limitations),
            confidence=self._confidence,
            uncertainty=self._uncertainty,
        )


__all__ = [
    "EventProjection",
    "EventSequenceProjection",
    "EventProjectionBuilder",
]