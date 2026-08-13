# Stream Registry
# ===============

"""
Registry for managing streams and their lifecycle.

The StreamRegistry owns the infrastructure aspects of streams while domain
subsystems own stream semantics. It handles:
    - Stream creation, lookup, and discovery
    - Generation management (new generations, closure)
    - Cursor tracking and checkpointing
    - Ownership assignment and validation

Stream Registry does NOT own:
    - Stream content or semantic meaning
    - Producer or consumer state
    - Scheduling or delivery logic
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Set, Tuple, Any, Protocol, runtime_checkable
from enum import Enum, auto
import time
import uuid
import threading

from .__init__ import (
    StreamId,
    StreamKind,
    StreamGenerationId,
    StreamRecordId,
    StreamCursor,
    StreamCheckpoint,
    StreamPosition,
    StreamLifecycleState,
    StreamLifecycleTransition,
    StreamNotFoundError,
    StreamClosedError,
    StreamPausedError,
    CapacityExceededError,
)


# =============================================================================
# STREAM REGISTRY CONFIGURATION
# =============================================================================

@dataclass(frozen=True)
class StreamConfig:
    """
    Configuration for a stream's behavior and policy.
    
    These settings determine how the stream behaves during its lifecycle.
    """
    # Ownership and scope
    owner_domain: str                    # Who owns the semantics
    is_public: bool = False              # Can be read by other domains
    
    # Capacity limits
    max_generations: int = 10            # Max generations before cleanup
    max_records_per_generation: int = 100000  # Max records per gen
    max_bytes_per_record: int = 65536    # 64KB max record size
    
    # Retention policy
    retention_seconds: int = 86400       # 24 hours default
    min_retained_generations: int = 3    # Always keep at least this many
    
    # Delivery guarantees
    delivery_mode: str = "at-least-once"  # at-most-once, at-least-once, effectively-once
    max_delivery_attempts: int = 3       # Before giving up
    
    # Ordering and consistency
    ordering: str = "sequential"         # sequential, causal, logical
    allow_reordering: bool = False       # Allow out-of-order commits
    
    # Backpressure
    backpressure_threshold: float = 0.8  # 80% capacity triggers backpressure
    max_subscriber_lag: int = 1000       # Max records behind head
    
    # Security
    requires_authentication: bool = True
    requires_authorization: bool = True


# =============================================================================
# STREAM STATE
# =============================================================================

@dataclass
class StreamState:
    """
    Runtime state of a stream.
    
    This is mutable runtime state, not the immutable record data itself.
    It tracks the current condition and metadata of the stream.
    """
    # Identity (immutable)
    stream_id: StreamId
    
    # Lifecycle
    lifecycle_state: StreamLifecycleState = StreamLifecycleState.DECLARED
    created_at_utc: float = field(default_factory=time.time)
    
    # Generations
    current_generation_number: int = 0
    generation_boundaries: List[Tuple[int, float]] = field(
        default_factory=list
    )  # (generation_num, started_at)
    
    # Cursor management
    active_cursors: Dict[str, StreamCursor] = field(default_factory=dict)
    
    # Statistics
    total_records_committed: int = 0
    total_bytes_committed: int = 0
    
    # Backpressure state
    pending_commits: int = 0
    last_backpressure_utc: Optional[float] = None
    
    # Metadata
    config: StreamConfig = field(default_factory=StreamConfig)
    
    def is_active(self) -> bool:
        """Check if stream can accept commits."""
        return self.lifecycle_state in (
            StreamLifecycleState.ACTIVE,
            StreamLifecycleState.PAUSED,  # Can read while paused
        )
    
    def can_commit(self) -> bool:
        """Check if stream can accept new commits."""
        return self.lifecycle_state == StreamLifecycleState.ACTIVE
    
    def can_subscribe(self) -> bool:
        """Check if stream can be subscribed to."""
        return self.lifecycle_state in (
            StreamLifecycleState.ACTIVE,
            StreamLifecycleState.PAUSED,
            StreamLifecycleState.READY,
        )
    
    def is_at_capacity(self) -> Tuple[bool, Optional[str]]:
        """
        Check if stream has exceeded capacity limits.
        
        Returns: (is_exceeded, reason) tuple
        """
        if self.total_records_committed >= self.config.max_records_per_generation:
            return True, "max_records"
        # Could add bytes check here too
        return False, None


# =============================================================================
# GENERATION STATE
# =============================================================================

@dataclass
class GenerationState:
    """
    State of a specific stream generation.
    
    Generations are sequential epochs in a stream's lifecycle. When a stream
    is paused and resumed, it may continue with the same generation or create
    a new one depending on policy.
    """
    generation_id: StreamGenerationId
    
    # Record tracking
    start_sequence: int = 0
    next_sequence: int = 0
    record_count: int = 0
    
    # Timestamps
    started_at_utc: float = field(default_factory=time.time)
    last_record_utc: Optional[float] = None
    
    # Commit tracking
    committed_records: Set[str] = field(default_factory=set)  # Record IDs
    pending_commits: List[StreamRecordId] = field(default_factory=list)
    
    # Integrity verification
    commit_hashes: Dict[int, str] = field(default_factory=dict)
    
    def next_record_id(self) -> StreamRecordId:
        """Generate the next record ID in this generation."""
        record_id = StreamRecordId(
            generation_id=self.generation_id,
            sequence=self.next_sequence
        )
        self.next_sequence += 1
        return record_id
    
    def is_empty(self) -> bool:
        """Check if generation has no records."""
        return self.record_count == 0
    
    def record_exists(self, record_id: StreamRecordId) -> bool:
        """Check if a record already exists in this generation."""
        # Extract sequence from record_id
        seq = record_id.sequence
        return seq < self.next_sequence


# =============================================================================
# SUBSCRIBER STATE
# =============================================================================

@dataclass
class SubscriberState:
    """
    State of a stream subscriber.
    
    Tracks what a consumer is interested in and their current position.
    """
    # Identity
    subscriber_id: str
    
    # Stream interests
    streams: Set[StreamId] = field(default_factory=set)
    generation_filters: Dict[StreamId, Optional[int]] = field(
        default_factory=dict
    )  # stream -> generation or None for all
    
    # Cursor state per stream
    cursors: Dict[StreamId, StreamCursor] = field(default_factory=dict)
    
    # Delivery tracking
    records_delivered: int = 0
    records_acked: int = 0
    records_rejected: int = 0
    
    # Backpressure tracking
    last_backpressure_utc: Optional[float] = None
    lag_count: int = 0
    
    def get_cursor(self, stream_id: StreamId) -> Optional[StreamCursor]:
        """Get cursor for a specific stream."""
        return self.cursors.get(stream_id)
    
    def update_cursor(
        self,
        stream_id: StreamId,
        new_position: StreamPosition
    ) -> None:
        """Update cursor position for a stream."""
        current = self.cursors.get(stream_id)
        if current is None:
            self.cursors[stream_id] = StreamCursor(
                stream_id=stream_id,
                generation_id=new_position.generation_id,
                position=new_position
            )
        else:
            self.cursors[stream_id] = current.advance(new_position)


# =============================================================================
# STREAM REGISTRY (Main Class)
# =============================================================================

class StreamRegistry:
    """
    Registry for managing streams, generations, and subscriptions.
    
    This is the canonical authority on stream existence, lifecycle state,
    and generation tracking. It does NOT store record data - that's handled
    by separate storage implementations.
    
    Thread safety: All public methods are thread-safe.
    """
    
    def __init__(self):
        self._lock = threading.RLock()
        
        # Stream states keyed by stream_id
        self._streams: Dict[StreamId, StreamState] = {}
        
        # Generation states keyed by generation_id.value
        self._generations: Dict[str, GenerationState] = {}
        
        # Subscriber states keyed by subscriber_id
        self._subscribers: Dict[str, SubscriberState] = {}
    
    # -------------------------------------------------------------------------
    # STREAM LIFECYCLE MANAGEMENT
    # -------------------------------------------------------------------------
    
    def declare_stream(
        self,
        stream_id: StreamId,
        config: Optional[StreamConfig] = None,
    ) -> Tuple[bool, StreamLifecycleTransition]:
        """
        Declare a new stream in the registry.
        
        This creates the infrastructure for a stream but doesn't activate it
        yet. Use activate_stream() to begin accepting commits.
        
        Args:
            stream_id: Unique identifier for the stream
            config: Configuration for stream behavior
            
        Returns: (success, transition) tuple
        """
        with self._lock:
            if stream_id in self._streams:
                return False, StreamLifecycleTransition(
                    stream_id=stream_id,
                    from_state=self._streams[stream_id].lifecycle_state,
                    to_state=self._streams[stream_id].lifecycle_state,
                    reason="Stream already exists"
                )
            
            state = StreamState(
                stream_id=stream_id,
                lifecycle_state=StreamLifecycleState.DECLARED,
                config=config or StreamConfig(owner_domain="unknown")
            )
            self._streams[stream_id] = state
            
            return True, StreamLifecycleTransition(
                stream_id=stream_id,
                from_state=StreamLifecycleState.DECLARED,
                to_state=StreamLifecycleState.CONFIGURED,
                reason="Initial declaration"
            )
    
    def initialize_stream(self, stream_id: StreamId) -> Tuple[bool, StreamLifecycleTransition]:
        """Initialize a declared stream with resources."""
        with self._lock:
            if stream_id not in self._streams:
                return False, StreamLifecycleTransition(
                    stream_id=stream_id,
                    from_state=StreamLifecycleState.DECLARED,
                    to_state=StreamLifecycleState.DECLARED,
                    reason="Stream not found"
                )
            
            state = self._streams[stream_id]
            if state.lifecycle_state != StreamLifecycleState.CONFIGURED:
                return False, StreamLifecycleTransition(
                    stream_id=stream_id,
                    from_state=state.lifecycle_state,
                    to_state=state.lifecycle_state,
                    reason=f"Cannot initialize: {state.lifecycle_state.value}"
                )
            
            state.lifecycle_state = StreamLifecycleState.INITIALIZING
            
            # Create initial generation
            gen_id = self._create_generation(stream_id)
            
            state.current_generation_number = gen_id.number
            state.generation_boundaries.append((gen_id.number, time.time()))
            
            state.lifecycle_state = StreamLifecycleState.READY
            
            return True, StreamLifecycleTransition(
                stream_id=stream_id,
                from_state=StreamLifecycleState.CONFIGURED,
                to_state=StreamLifecycleState.READY,
                reason="Initial generation created"
            )
    
    def activate_stream(self, stream_id: StreamId) -> Tuple[bool, StreamLifecycleTransition]:
        """Activate a ready stream for accepting commits."""
        with self._lock:
            if stream_id not in self._streams:
                return False, self._not_found_transition(stream_id)
            
            state = self._streams[stream_id]
            if state.lifecycle_state != StreamLifecycleState.READY:
                return False, self._invalid_state_transition(state, "ready")
            
            state.lifecycle_state = StreamLifecycleState.ACTIVE
            
            return True, StreamLifecycleTransition(
                stream_id=stream_id,
                from_state=StreamLifecycleState.READY,
                to_state=StreamLifecycleState.ACTIVE,
                reason="Activated by owner"
            )
    
    def pause_stream(self, stream_id: StreamId) -> Tuple[bool, StreamLifecycleTransition]:
        """Temporarily pause a stream."""
        with self._lock:
            if stream_id not in self._streams:
                return False, self._not_found_transition(stream_id)
            
            state = self._streams[stream_id]
            if state.lifecycle_state != StreamLifecycleState.ACTIVE:
                return False, self._invalid_state_transition(state, "active")
            
            state.lifecycle_state = StreamLifecycleState.PAUSED
            
            return True, StreamLifecycleTransition(
                stream_id=stream_id,
                from_state=StreamLifecycleState.ACTIVE,
                to_state=StreamLifecycleState.PAUSED,
                reason="Paused by owner"
            )
    
    def resume_stream(self, stream_id: StreamId) -> Tuple[bool, StreamLifecycleTransition]:
        """Resume a paused stream."""
        with self._lock:
            if stream_id not in self._streams:
                return False, self._not_found_transition(stream_id)
            
            state = self._streams[stream_id]
            if state.lifecycle_state != StreamLifecycleState.PAUSED:
                return False, self._invalid_state_transition(state, "paused")
            
            state.lifecycle_state = StreamLifecycleState.ACTIVE
            
            return True, StreamLifecycleTransition(
                stream_id=stream_id,
                from_state=StreamLifecycleState.PAUSED,
                to_state=StreamLifecycleState.ACTIVE,
                reason="Resumed by owner"
            )
    
    def close_stream(self, stream_id: StreamId) -> Tuple[bool, StreamLifecycleTransition]:
        """Permanently close a stream."""
        with self._lock:
            if stream_id not in self._streams:
                return False, self._not_found_transition(stream_id)
            
            state = self._streams[stream_id]
            
            # Transition through draining first for graceful shutdown
            old_state = state.lifecycle_state
            if old_state == StreamLifecycleState.ACTIVE:
                state.lifecycle_state = StreamLifecycleState.DRAINING
                
                # Wait for pending commits (simplified - in real impl, would wait)
                
            elif old_state == StreamLifecycleState.PAUSED:
                pass  # Can go directly from paused to closed
            
            state.lifecycle_state = StreamLifecycleState.CLOSED
            
            return True, StreamLifecycleTransition(
                stream_id=stream_id,
                from_state=old_state,
                to_state=StreamLifecycleState.CLOSED,
                reason="Closed by owner"
            )
    
    def fail_stream(
        self,
        stream_id: StreamId,
        reason: str
    ) -> Tuple[bool, StreamLifecycleTransition]:
        """Mark a stream as failed."""
        with self._lock:
            if stream_id not in self._streams:
                return False, self._not_found_transition(stream_id)
            
            state = self._streams[stream_id]
            old_state = state.lifecycle_state
            
            state.lifecycle_state = StreamLifecycleState.FAILED
            
            return True, StreamLifecycleTransition(
                stream_id=stream_id,
                from_state=old_state,
                to_state=StreamLifecycleState.FAILED,
                reason=f"Failed: {reason}"
            )
    
    # -------------------------------------------------------------------------
    # GENERATION MANAGEMENT
    # -------------------------------------------------------------------------
    
    def _create_generation(self, stream_id: StreamId) -> StreamGenerationId:
        """Create a new generation for a stream."""
        state = self._streams[stream_id]
        
        gen_num = state.current_generation_number + 1
        
        gen_id = StreamGenerationId(stream_id=stream_id, number=gen_num)
        
        gen_state = GenerationState(
            generation_id=gen_id,
            start_sequence=0,
            next_sequence=0
        )
        self._generations[gen_id.value] = gen_state
        
        state.current_generation_number = gen_num
        
        return gen_id
    
    def get_current_generation(self, stream_id: StreamId) -> Optional[StreamGenerationId]:
        """Get the current active generation for a stream."""
        with self._lock:
            if stream_id not in self._streams:
                return None
            state = self._streams[stream_id]
            if state.current_generation_number == 0:
                return None
            return StreamGenerationId(
                stream_id=stream_id,
                number=state.current_generation_number
            )
    
    # -------------------------------------------------------------------------
    # SUBSCRIBER MANAGEMENT
    # -------------------------------------------------------------------------
    
    def register_subscriber(
        self,
        subscriber_id: str,
        streams: Optional[List[StreamId]] = None,
        generation_filter: Optional[int] = None,
    ) -> bool:
        """Register a subscriber for one or more streams."""
        with self._lock:
            if subscriber_id not in self._subscribers:
                self._subscribers[subscriber_id] = SubscriberState(
                    subscriber_id=subscriber_id
                )
            
            sub_state = self._subscribers[subscriber_id]
            
            for stream_id in streams or []:
                sub_state.streams.add(stream_id)
                sub_state.generation_filters[stream_id] = generation_filter
                
                # Initialize cursor at beginning if needed
                if stream_id not in sub_state.cursors:
                    sub_state.cursors[stream_id] = StreamCursor(
                        stream_id=stream_id,
                        generation_id=None,
                        position=StreamPosition.from_beginning()
                    )
            
            return True
    
    def unregister_subscriber(self, subscriber_id: str) -> bool:
        """Remove a subscriber registration."""
        with self._lock:
            if subscriber_id in self._subscribers:
                del self._subscribers[subscriber_id]
                return True
            return False
    
    # -------------------------------------------------------------------------
    # STATE QUERIES
    # -------------------------------------------------------------------------
    
    def get_stream_state(self, stream_id: StreamId) -> Optional[StreamState]:
        """Get current state of a stream."""
        with self._lock:
            return self._streams.get(stream_id)
    
    def list_streams(
        self,
        kind: Optional[StreamKind] = None,
        lifecycle_state: Optional[StreamLifecycleState] = None,
    ) -> List[StreamId]:
        """List streams, optionally filtered by kind or state."""
        with self._lock:
            result = []
            for stream_id, state in self._streams.items():
                if kind is not None and state.stream_id.kind != kind:
                    continue
                if lifecycle_state is not None and state.lifecycle_state != lifecycle_state:
                    continue
                result.append(stream_id)
            return result
    
    def get_active_subscribers(
        self,
        stream_id: StreamId,
    ) -> List[SubscriberState]:
        """Get subscribers currently subscribed to a stream."""
        with self._lock:
            result = []
            for sub in self._subscribers.values():
                if stream_id in sub.streams:
                    result.append(sub)
            return result
    
    # -------------------------------------------------------------------------
    # CAPACITY & BACKPRESSURE
    # -------------------------------------------------------------------------
    
    def check_capacity(
        self,
        stream_id: StreamId,
        additional_bytes: int = 0,
    ) -> Tuple[bool, Optional[str]]:
        """
        Check if a stream can accept more data.
        
        Returns: (can_commit, reason) tuple
        """
        with self._lock:
            if stream_id not in self._streams:
                return False, "stream_not_found"
            
            state = self._streams[stream_id]
            
            # Check if active
            if not state.can_commit():
                return False, f"stream_{state.lifecycle_state.value}"
            
            # Check record count capacity
            exceeded, reason = state.is_at_capacity()
            if exceeded:
                return False, reason
            
            return True, None
    
    def record_backpressure(
        self,
        stream_id: StreamId,
        subscriber_id: Optional[str] = None,
    ) -> None:
        """Record that backpressure is occurring."""
        with self._lock:
            if stream_id in self._streams:
                state = self._streams[stream_id]
                state.last_backpressure_utc = time.time()
                
                # Also track on subscriber if provided
                if subscriber_id and subscriber_id in self._subscribers:
                    sub = self._subscribers[subscriber_id]
                    sub.last_backpressure_utc = time.time()
    
    # -------------------------------------------------------------------------
    # INTERNAL HELPERS
    # -------------------------------------------------------------------------
    
    def _not_found_transition(self, stream_id: StreamId) -> StreamLifecycleTransition:
        return StreamLifecycleTransition(
            stream_id=stream_id,
            from_state=StreamLifecycleState.DECLARED,
            to_state=StreamLifecycleState.DECLARED,
            reason="Stream not found"
        )
    
    def _invalid_state_transition(
        self,
        state: StreamState,
        expected: str
    ) -> StreamLifecycleTransition:
        return StreamLifecycleTransition(
            stream_id=state.stream_id,
            from_state=state.lifecycle_state,
            to_state=state.lifecycle_state,
            reason=f"Expected {expected}, got {state.lifecycle_state.value}"
        )
    
    # -------------------------------------------------------------------------
    # DIAGNOSTICS
    # -------------------------------------------------------------------------
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get registry-wide statistics."""
        with self._lock:
            return {
                "total_streams": len(self._streams),
                "stream_states": {
                    state.value: sum(1 for s in self._streams.values() 
                                    if s.lifecycle_state == state)
                    for state in StreamLifecycleState
                },
                "total_generations": len(self._generations),
                "total_subscribers": len(self._subscribers),
            }


__all__ = [
    # Config and state
    "StreamConfig",
    "StreamState",
    "GenerationState",
    "SubscriberState",
    
    # Main registry
    "StreamRegistry",
]