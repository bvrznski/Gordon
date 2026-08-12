# Core Replay Engine
# ==================

"""
Deterministic replay engine using immutable history.

Replay supports:
- Deterministic re-execution of past events
- Preserved correlation and causation chains
- Provenance preservation
- Sequence number ordering

Replay NEVER republishes mutable artifacts - only immutable envelopes.
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any, Tuple
from enum import Enum, auto
import threading
import time


# =============================================================================
# REPLAY STATE
# =============================================================================

class ReplayState(Enum):
    """States of a replay operation."""
    PENDING = "pending"       # Scheduled but not started
    RUNNING = "running"       # Currently replaying
    PAUSED = "paused"         # Paused (can resume)
    COMPLETED = "completed"   # All events replayed
    CANCELLED = "cancelled"   # Manually cancelled
    FAILED = "failed"         # Error during replay


# =============================================================================
# REPLAY HISTORY ENTRY
# =============================================================================

@dataclass(frozen=True)
class ReplayHistoryEntry:
    """
    Immutable record of a historical event for replay.
    
    Captures all information needed to reproduce the original delivery.
    """
    
    sequence_number: int
    timestamp_utc: float
    
    # Original envelope data
    envelope_id: str
    runtime_id: str
    
    # Event-specific fields (one of these will be populated)
    event_type: Optional[str] = None
    message_type: Optional[str] = None
    signal_type: Optional[str] = None
    
    payload: Dict[str, Any] = field(default_factory=dict)
    
    correlation_id: Optional[str] = None
    causation_id: Optional[str] = None
    
    # Original delivery context (for accurate replay)
    delivery_mode: str = "synchronous"
    priority: int = 0
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "sequence_number": self.sequence_number,
            "timestamp_utc": self.timestamp_utc,
            "envelope_id": self.envelope_id,
            "runtime_id": self.runtime_id,
            "event_type": self.event_type,
            "message_type": self.message_type,
            "signal_type": self.signal_type,
            "payload": dict(self.payload),
            "correlation_id": self.correlation_id,
            "causation_id": self.causation_id,
            "delivery_mode": self.delivery_mode,
            "priority": self.priority,
        }


# =============================================================================
# REPLAY HISTORY
# =============================================================================

class ReplayHistory:
    """
    History of events suitable for replay.
    
    Stores events in sequence order with all metadata preserved.
    """
    
    def __init__(self, max_entries: int = 100000):
        self._max_entries = max_entries
        
        self._lock = threading.RLock()
        
        # Sequence-number indexed history
        self._history: Dict[int, ReplayHistoryEntry] = {}
        self._sequence_numbers: List[int] = []  # Ordered list for iteration
    
    def add(self, entry: ReplayHistoryEntry) -> None:
        """Add an entry to replay history."""
        with self._lock:
            if entry.sequence_number not in self._history:
                self._history[entry.sequence_number] = entry
                self._sequence_numbers.append(entry.sequence_number)
                
                # Enforce max size (remove oldest)
                while len(self._sequence_numbers) > self._max_entries:
                    oldest = self._sequence_numbers.pop(0)
                    del self._history[oldest]
    
    def get_by_sequence(
        self,
        sequence_numbers: List[int],
    ) -> List[ReplayHistoryEntry]:
        """Get entries by their sequence numbers (in order)."""
        with self._lock:
            return [
                self._history.get(seq)
                for seq in sequence_numbers
                if seq in self._history
            ]
    
    def get_range(
        self,
        start_sequence: int = 0,
        end_sequence: Optional[int] = None,
    ) -> List[ReplayHistoryEntry]:
        """Get entries within a sequence range."""
        with self._lock:
            result = []
            
            for seq in sorted(self._sequence_numbers):
                if seq < start_sequence:
                    continue
                if end_sequence is not None and seq > end_sequence:
                    break
                
                result.append(self._history[seq])
            
            return result
    
    def get_latest_sequence(self) -> int:
        """Get the highest sequence number."""
        with self._lock:
            if not self._sequence_numbers:
                return 0
            return max(self._sequence_numbers)
    
    def replay_from(
        self,
        since_sequence: int = 0,
    ) -> List[ReplayHistoryEntry]:
        """
        Get entries for replay from a sequence number.
        
        Args:
            since_sequence: Start from this sequence (inclusive)
            
        Returns:
            Ordered list of history entries
        """
        return self.get_range(start_sequence=since_sequence)
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get replay history statistics."""
        with self._lock:
            # Count by type
            event_types: Dict[str, int] = {}
            
            for entry in self._history.values():
                t = entry.event_type or entry.message_type or entry.signal_type
                if t:
                    event_types[t] = event_types.get(t, 0) + 1
            
            return {
                "total_entries": len(self._history),
                "sequence_range": (
                    min(self._sequence_numbers) if self._sequence_numbers else None,
                    max(self._sequence_numbers) if self._sequence_numbers else None
                ),
                "event_type_counts": event_types,
            }


# =============================================================================
# REPLAY ENGINE
# =============================================================================

@dataclass(frozen=True)
class ReplayConfig:
    """Configuration for a replay operation."""
    
    start_sequence: int = 0
    end_sequence: Optional[int] = None
    
    # Speed control
    replay_speed: str = "realtime"  # realtime, instant, custom_multiplier
    
    # Behavior
    preserve_timing: bool = True
    resume_from_checkpoint: Optional[int] = None
    
    # Filtering
    event_types: List[str] = field(default_factory=list)  # Empty = all types


class ReplayEngine:
    """
    Deterministic replay engine for communication history.
    
    Provides replay of past events while preserving:
        - Correlation chains
        - Causation relationships  
        - Sequence ordering
        - Provenance information
    
    The replay is deterministic - given the same history and config,
    it will always produce the same results.
    """
    
    def __init__(self, history: ReplayHistory):
        self._history = history
        
        self._lock = threading.RLock()
        
        # Current state
        self._state = ReplayState.PENDING
        self._current_sequence = 0
        self._checkpoint: Optional[int] = None
    
    @property
    def state(self) -> ReplayState:
        """Get current replay state."""
        with self._lock:
            return self._state
    
    @property
    def current_sequence(self) -> int:
        """Get current replay position."""
        with self._lock:
            return self._current_sequence
    
    def prepare(
        self,
        config: ReplayConfig,
    ) -> List[ReplayHistoryEntry]:
        """
        Prepare for replay and get the entries to replay.
        
        Args:
            config: Replay configuration
            
        Returns:
            List of history entries to replay
        """
        with self._lock:
            # Get range from history
            start_seq = (
                config.resume_from_checkpoint 
                if config.resume_from_checkpoint 
                else config.start_sequence
            )
            
            entries = self._history.get_range(
                start_sequence=start_seq,
                end_sequence=config.end_sequence,
            )
            
            # Apply type filtering
            if config.event_types:
                entries = [
                    e for e in entries
                    if e.event_type in config.event_types or
                       e.message_type in config.event_types or
                       e.signal_type in config.event_types
                ]
            
            self._current_sequence = start_seq
            
            return entries
    
    def execute(
        self,
        entries: List[ReplayHistoryEntry],
        delivery_callback: Optional[Any] = None,  # Callable[[ReplayHistoryEntry], bool]
    ) -> Tuple[bool, int]:
        """
        Execute replay of the given entries.
        
        Args:
            entries: History entries to replay
            delivery_callback: Optional callback called for each entry
            
        Returns:
            Tuple of (success, replayed_count)
        """
        with self._lock:
            self._state = ReplayState.RUNNING
        
        replayed = 0
        success = True
        
        try:
            for entry in entries:
                # Deliver the entry
                if delivery_callback is not None:
                    delivered = delivery_callback(entry)
                    
                    if not delivered:
                        success = False
                
                replayed += 1
                self._current_sequence = entry.sequence_number
                
                # Update checkpoint periodically
                if replayed % 100 == 0:
                    self._checkpoint = self._current_sequence
        
        except Exception as e:
            with self._lock:
                self._state = ReplayState.FAILED
            
            return False, replayed
        
        with self._lock:
            self._state = ReplayState.COMPLETED
            self._checkpoint = self._current_sequence
        
        return success, replayed
    
    def cancel(self) -> None:
        """Cancel the current replay."""
        with self._lock:
            if self._state == ReplayState.RUNNING:
                self._state = ReplayState.CANCELLED
    
    def get_checkpoint(self) -> Optional[int]:
        """Get current replay checkpoint (resume position)."""
        with self._lock:
            return self._checkpoint
    
    def resume_from(
        self,
        sequence_number: int,
    ) -> List[ReplayHistoryEntry]:
        """
        Resume replay from a specific sequence number.
        
        Args:
            sequence_number: Where to resume
            
        Returns:
            Remaining entries to replay
        """
        with self._lock:
            # Update state
            if self._state == ReplayState.PAUSED:
                self._state = ReplayState.RUNNING
        
        return self._history.replay_from(since_sequence=sequence_number)
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get replay engine statistics."""
        with self._lock:
            return {
                "state": self._state.value,
                "current_sequence": self._current_sequence,
                "checkpoint": self._checkpoint,
                **self._history.get_statistics(),
            }


# =============================================================================
# CANONICAL REPLAY ENGINE FACTORY
# =============================================================================

class ReplayEngineFactory:
    """
    Factory for creating replay engines with history.
    
    Usage:
        factory = ReplayEngineFactory(max_history=100000)
        
        # Add events to history
        factory.add_event(envelope)
        
        # Create a replay engine
        replay_engine = factory.create_replay()
    """
    
    def __init__(self, max_history: int = 100000):
        self._max_history = max_history
        
        self._lock = threading.RLock()
        
        # Event storage
        self._events: Dict[int, ReplayHistoryEntry] = {}
        self._sequence_counter = 0
    
    def add_event(
        self,
        envelope_id: str,
        runtime_id: str,
        event_type: Optional[str] = None,
        message_type: Optional[str] = None,
        signal_type: Optional[str] = None,
        payload: Optional[Dict[str, Any]] = None,
        correlation_id: Optional[str] = None,
        causation_id: Optional[str] = None,
        delivery_mode: str = "synchronous",
        priority: int = 0,
    ) -> ReplayHistoryEntry:
        """
        Add an event to the replay history.
        
        Args:
            envelope_id: ID of the envelope
            runtime_id: Which runtime generated it
            event_type, message_type, signal_type: Type info (one required)
            payload: Event data
            correlation_id, causation_id: Traceability IDs
            
        Returns:
            The created ReplayHistoryEntry
        """
        with self._lock:
            self._sequence_counter += 1
            seq = self._sequence_counter
            
            entry = ReplayHistoryEntry(
                sequence_number=seq,
                timestamp_utc=time.time(),
                envelope_id=envelope_id,
                runtime_id=runtime_id,
                event_type=event_type,
                message_type=message_type,
                signal_type=signal_type,
                payload=dict(payload or {}),
                correlation_id=correlation_id,
                causation_id=causation_id,
                delivery_mode=delivery_mode,
                priority=priority,
            )
            
            self._events[seq] = entry
            
            # Enforce max size
            while len(self._events) > self._max_history:
                oldest_seq = min(self._events.keys())
                del self._events[oldest_seq]
            
            return entry
    
    def create_replay(self) -> ReplayEngine:
        """Create a replay engine using current history."""
        history = ReplayHistory(max_entries=self._max_history)
        
        with self._lock:
            for seq, entry in sorted(self._events.items()):
                history.add(entry)
        
        return ReplayEngine(history)


__all__ = [
    # State
    "ReplayState",
    
    # History types
    "ReplayHistoryEntry",
    "ReplayHistory",
    
    # Engine
    "ReplayConfig",
    "ReplayEngine",
    
    # Factory
    "ReplayEngineFactory",
]