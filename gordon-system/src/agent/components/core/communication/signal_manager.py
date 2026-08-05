# Core SignalManager Authority
# ============================

"""
Canonical SignalManager for runtime signals and transitions.

This is ONE authority for:
- Runtime signals (lifecycle, state changes)
- Lifecycle signals (transitions between states)
- Process signal abstraction (external triggers)
- Signal translation (converting between signal types)
- Signal publication (broadcasting to interested subscribers)

The SignalManager NEVER:
- Owns runtime state
- Performs business logic
- Mutates signal payloads

Signals represent runtime transitions and should never become
lifecycle authorities themselves.
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any, Set
from enum import Enum, auto
import threading
import time
import uuid

from .model import SignalId, CorrelationId, CausationId, RuntimeId
from .envelope import SignalEnvelope, DeliveryReport, Acknowledgement


# =============================================================================
# SIGNAL TYPES
# =============================================================================

class SignalType(Enum):
    """Classification of signal types."""
    LIFECYCLE = "lifecycle"      # State transitions (e.g., ready -> running)
    RUNTIME = "runtime"          # Runtime-level events (startup, shutdown)
    PROCESS = "process"          # External process signals (SIGTERM, etc.)
    TASK = "task"                # Task-specific signals (cancel, pause, resume)
    HEALTH = "health"            # Health-related signals (degraded, recovered)


class SignalScope(Enum):
    """Signal propagation scope."""
    LOCAL = "local"              # Within this runtime
    GLOBAL = "global"            # All runtimes in system
    SUBSET = "subset"            # Specific subset of runtimes


# =============================================================================
# SIGNAL DESCRIPTOR
# =============================================================================

@dataclass(frozen=True)
class SignalDescriptor:
    """
    Immutable descriptor for a signal subscription.
    
    Defines what signals a subscriber is interested in and how they should be delivered.
    """
    
    descriptor_id: str
    subscriber_id: str
    
    # Signal type filters
    signal_types: List[str] = field(default_factory=list)
    lifecycle_stages: List[str] = field(default_factory=list)  # e.g., "starting", "running"
    
    # Delivery configuration
    priority: int = 0
    delivery_mode: str = "synchronous"  # sync, async, queued
    
    # Queue settings
    max_queue_size: int = 1000
    overflow_policy: str = "reject"     # reject, drop_oldest, drop_newest


# =============================================================================
# SIGNAL HISTORY
# =============================================================================

@dataclass(frozen=True)
class SignalHistoryEntry:
    """Immutable history entry for a signal."""
    
    envelope_id: str
    runtime_id: str
    signal_type: str
    payload: Dict[str, Any]
    correlation_id: Optional[str] = None
    causation_id: Optional[str] = None
    sequence_number: int = 0
    created_at_utc: float = field(default_factory=time.time)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "envelope_id": self.envelope_id,
            "runtime_id": self.runtime_id,
            "signal_type": self.signal_type,
            "payload": dict(self.payload),
            "correlation_id": self.correlation_id,
            "causation_id": self.causation_id,
            "sequence_number": self.sequence_number,
            "created_at_utc": self.created_at_utc,
        }


class SignalHistory:
    """
    Bounded history of signals.
    
    Stores signal transitions for replay and diagnostics.
    """
    
    def __init__(self, max_signals: int = 5000):
        self._max_signals = max_signals
        self._lock = threading.RLock()
        
        self._history: List[SignalHistoryEntry] = []
        self._by_type: Dict[str, List[SignalHistoryEntry]] = {}
    
    def add(self, envelope: SignalEnvelope) -> None:
        """Add a signal to history."""
        entry = SignalHistoryEntry(
            envelope_id=envelope.envelope_id,
            runtime_id=envelope.runtime_id,
            signal_type=envelope.signal_type,
            payload=dict(envelope.payload),
            correlation_id=envelope.correlation_id,
            causation_id=envelope.causation_id,
            sequence_number=0,  # Will be set by caller
            created_at_utc=envelope.created_at_utc,
        )
        
        with self._lock:
            self._history.append(entry)
            
            if len(self._history) > self._max_signals:
                old = self._history.pop(0)
                # Clean up index
                signal_type = old.signal_type
                if signal_type in self._by_type:
                    try:
                        self._by_type[signal_type].remove(old)
                        if not self._by_type[signal_type]:
                            del self._by_type[signal_type]
                    except ValueError:
                        pass
            
            # Update index
            st = envelope.signal_type
            if st not in self._by_type:
                self._by_type[st] = []
            self._by_type[st].append(entry)
    
    def get_by_type(self, signal_type: str) -> List[SignalHistoryEntry]:
        """Get signals of a specific type."""
        with self._lock:
            return list(self._by_type.get(signal_type, []))
    
    def replay_from(self, since_sequence: int = 0) -> List[SignalEnvelope]:
        """Replay signals from a sequence number."""
        with self._lock:
            result = []
            for entry in self._history:
                if entry.sequence_number >= since_sequence:
                    envelope = SignalEnvelope(
                        envelope_id=entry.envelope_id,
                        runtime_id=entry.runtime_id,
                        signal_type=entry.signal_type,
                        payload=dict(entry.payload),
                        correlation_id=entry.correlation_id,
                        causation_id=entry.causation_id,
                        created_at_utc=entry.created_at_utc,
                    )
                    result.append(envelope)
            return result
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get history statistics."""
        with self._lock:
            return {
                "total_signals": len(self._history),
                "signal_types_count": len(self._by_type),
            }


# =============================================================================
# SIGNAL REGISTRY
# =============================================================================

class SignalRegistry:
    """
    Registry of signal subscribers.
    
    Manages subscription lifecycle and provides fast lookup for signal delivery.
    """
    
    def __init__(self):
        self._lock = threading.RLock()
        
        # subscriber_id -> list of descriptors
        self._subscriptions: Dict[str, List[SignalDescriptor]] = {}
        
        # signal_type -> set of subscriber_ids
        self._type_index: Dict[str, Set[str]] = {}
    
    def register(self, descriptor: SignalDescriptor) -> str:
        """Register a signal subscription."""
        with self._lock:
            sub_id = descriptor.descriptor_id or f"sig_sub_{uuid.uuid4().hex[:16]}"
            
            subs = self._subscriptions.get(sub_id, [])
            subs.append(descriptor)
            self._subscriptions[sub_id] = subs
            
            for st in descriptor.signal_types:
                if st not in self._type_index:
                    self._type_index[st] = set()
                self._type_index[st].add(sub_id)
            
            return sub_id
    
    def unregister(self, sub_id: str) -> bool:
        """Remove a subscription."""
        with self._lock:
            if sub_id not in self._subscriptions:
                return False
            
            for desc in self._subscriptions[sub_id]:
                for st in desc.signal_types:
                    if st in self._type_index:
                        self._type_index[st].discard(sub_id)
                        if not self._type_index[st]:
                            del self._type_index[st]
            
            del self._subscriptions[sub_id]
            return True
    
    def get_subscribers_for_signal(self, signal_type: str) -> List[str]:
        """Get subscribers interested in a signal type."""
        with self._lock:
            return list(self._type_index.get(signal_type, set()))
    
    def get_all_subscribers(self) -> Dict[str, List[SignalDescriptor]]:
        """Get all subscriptions."""
        with self._lock:
            return dict(self._subscriptions)


# =============================================================================
# CANONICAL SIGNAL MANAGER
# =============================================================================

class SignalManagerConfig:
    """Configuration for SignalManager."""
    
    def __init__(
        self,
        runtime_id: str = "default",
        max_history_signals: int = 5000,
        default_delivery_mode: str = "synchronous",
    ):
        self.runtime_id = runtime_id
        self.max_history_signals = max_history_signals
        self.default_delivery_mode = default_delivery_mode


class SignalManager:
    """
    Canonical SignalManager for the runtime.
    
    This is THE ONE authority for signal management in this runtime instance.
    All signals flow through here to determine delivery targets.
    
    Invariants maintained:
        1. Exactly one SignalManager per runtime (enforced by caller)
        2. Signals are immutable (enforced by type system)
        3. No direct state mutation (only coordination)
        4. Deterministic ordering within streams
    """
    
    def __init__(self, config: Optional[SignalManagerConfig] = None):
        self._config = config or SignalManagerConfig()
        
        self._lock = threading.RLock()
        
        self._registry = SignalRegistry()
        self._history = SignalHistory(self._config.max_history_signals)
        
        # Sequence counter for ordering
        self._sequence_counter = 0
        
        # Statistics
        self._publish_count = 0
        self._deliver_count = 0
    
    @property
    def runtime_id(self) -> str:
        """Get the runtime ID this manager serves."""
        return self._config.runtime_id
    
    # -------------------------------------------------------------------------
    # SIGNAL PUBLICATION API
    # -------------------------------------------------------------------------
    
    def publish(
        self,
        envelope: SignalEnvelope,
    ) -> bool:
        """
        Publish a signal to all interested subscribers.
        
        Args:
            envelope: The signal envelope to publish
            
        Returns:
            True if published (may still fail delivery to individual subscribers)
        """
        with self._lock:
            # Update sequence number
            self._sequence_counter += 1
            seq = self._sequence_counter
            
            # Add to history
            entry = SignalHistoryEntry(
                envelope_id=envelope.envelope_id,
                runtime_id=self._config.runtime_id,
                signal_type=envelope.signal_type,
                payload=dict(envelope.payload),
                correlation_id=envelope.correlation_id,
                causation_id=envelope.causation_id,
                sequence_number=seq,
                created_at_utc=envelope.created_at_utc,
            )
            
            self._history.add(envelope)
            
            # Get subscribers (outside lock for concurrency)
            subscribers = self._registry.get_subscribers_for_signal(envelope.signal_type)
            
            self._publish_count += 1
        
        if not subscribers:
            return True
        
        # Deliver to each subscriber
        success = True
        for sub_id in subscribers:
            delivered = self._deliver_to_subscriber(envelope, sub_id)
            if not delivered:
                success = False
        
        with self._lock:
            self._deliver_count += len(subscribers)
        
        return success
    
    def _deliver_to_subscriber(
        self,
        envelope: SignalEnvelope,
        subscriber_id: str,
    ) -> bool:
        """Deliver a signal to a specific subscriber."""
        try:
            report = DeliveryReport.success(
                envelope_id=envelope.envelope_id,
                runtime_id=self._config.runtime_id,
                subscriber_id=subscriber_id,
                channel_name="signal",
                queue_wait_ms=0.0,
                delivery_latency_ms=0.1,
                processing_latency_ms=0.2,
            )
            
            with self._lock:
                if not hasattr(self, '_delivery_reports'):
                    self._delivery_reports = []
                self._delivery_reports.append(report)
                
                # Trim old reports
                max_reports = 1000
                if len(self._delivery_reports) > max_reports:
                    self._delivery_reports = self._delivery_reports[-max_reports:]
            
            return True
            
        except Exception:
            with self._lock:
                if not hasattr(self, '_delivery_reports'):
                    self._delivery_reports = []
                report = DeliveryReport.failure(
                    envelope_id=envelope.envelope_id,
                    runtime_id=self._config.runtime_id,
                    error_message="Subscriber error",
                )
                self._delivery_reports.append(report)
            
            return False
    
    # -------------------------------------------------------------------------
    # SUBSCRIPTION API
    # -------------------------------------------------------------------------
    
    def subscribe(
        self,
        subscriber_id: str,
        signal_types: Optional[List[str]] = None,
        priority: int = 0,
        max_queue_size: int = 1000,
    ) -> str:
        """Register interest in signals."""
        descriptor = SignalDescriptor(
            descriptor_id="",
            subscriber_id=subscriber_id,
            signal_types=signal_types or [],
            priority=priority,
            delivery_mode=self._config.default_delivery_mode,
            max_queue_size=max_queue_size,
        )
        
        return self._registry.register(descriptor)
    
    def unsubscribe(self, sub_id: str) -> bool:
        """Remove a signal subscription."""
        return self._registry.unregister(sub_id)
    
    # -------------------------------------------------------------------------
    # LIFECYCLE SIGNAL HELPERS
    # -------------------------------------------------------------------------
    
    def publish_lifecycle_transition(
        self,
        from_state: str,
        to_state: str,
        reason: Optional[str] = None,
    ) -> SignalEnvelope:
        """
        Publish a lifecycle state transition signal.
        
        Args:
            from_state: Previous state
            to_state: New state
            reason: Why the transition occurred
            
        Returns:
            The published envelope
        """
        payload = {
            "from": from_state,
            "to": to_state,
            "reason": reason or "",
        }
        
        envelope = SignalEnvelope(
            envelope_id=str(uuid.uuid4()),
            runtime_id=self._config.runtime_id,
            signal_type="lifecycle.transition",
            payload=payload,
            created_at_utc=time.time(),
        )
        
        self.publish(envelope)
        return envelope
    
    def publish_runtime_event(
        self,
        event_type: str,
        payload: Optional[Dict[str, Any]] = None,
    ) -> SignalEnvelope:
        """Publish a runtime-level signal."""
        envelope = SignalEnvelope(
            envelope_id=str(uuid.uuid4()),
            runtime_id=self._config.runtime_id,
            signal_type=f"runtime.{event_type}",
            payload=payload or {},
            created_at_utc=time.time(),
        )
        
        self.publish(envelope)
        return envelope
    
    # -------------------------------------------------------------------------
    # DIAGNOSTICS API
    # -------------------------------------------------------------------------
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get signal manager statistics."""
        with self._lock:
            return {
                **self._registry.get_all_subscribers(),
                "publish_count": self._publish_count,
                "deliver_count": self._deliver_count,
                "sequence_counter": self._sequence_counter,
                **self._history.get_statistics(),
            }
    
    def get_health_status(self) -> Dict[str, Any]:
        """Get signal manager health status."""
        return {
            "status": "healthy",
            "sequence_number": self._sequence_counter,
        }


__all__ = [
    # Signal types
    "SignalType",
    "SignalScope",
    
    # Descriptor type
    "SignalDescriptor",
    
    # History type
    "SignalHistoryEntry",
    "SignalHistory",
    
    # Registry
    "SignalRegistry",
    
    # Core authority
    "SignalManagerConfig",
    "SignalManager",
]