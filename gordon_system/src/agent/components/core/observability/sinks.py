# Core Event Sinks
# ================

"""
Event sink contracts and implementations.

This module provides:
- Sink protocol for structured event delivery
- Bounded buffer with eviction policies
- Redaction support for sensitive data
- Graceful failure handling
- Flush semantics
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional, Deque
from collections import deque
from enum import Enum, auto
import time


# =============================================================================
# Sink Status
# =============================================================================

class SinkStatus(Enum):
    """Event sink operational status."""
    
    ACTIVE = "active"         # Accepting events normally
    DRAINING = "draining"     # Flushing remaining events
    FAILED = "failed"         # Permanently failed
    CLOSED = "closed"         # Closed and flushed


# =============================================================================
# Bounded Buffer with Eviction Policy
# =============================================================================

class EvictionPolicy(Enum):
    """Strategy for evicting old events when buffer is full."""
    
    DROP_OLDEST = auto()   # Remove oldest events (FIFO)
    DROP_LOWEST_SEVERITY = auto()  # Remove lowest severity events first


@dataclass
class BoundedBufferConfig:
    """
    Configuration for bounded event buffers.
    
    Args:
        max_size: Maximum number of events in buffer
        eviction_policy: Strategy when buffer is full
        flush_timeout_seconds: Timeout for flush operations
    """
    
    max_size: int = 1000
    eviction_policy: EvictionPolicy = EvictionPolicy.DROP_OLDEST
    flush_timeout_seconds: float = 5.0


# =============================================================================
# Event Sink Protocol
# =============================================================================

class EventSink(ABC):
    """
    Contract for event sinks.
    
    Sinks receive structured events and deliver them to their destination.
    They must be:
    - Thread-safe where applicable
    - Non-blocking where possible
    - Graceful in failure scenarios
    
    Usage:
        async with MySink() as sink:
            await sink.emit(event)
        
        # Or manually:
        sink = MySink()
        try:
            await sink.emit(event)
        finally:
            await sink.close()
    """
    
    @abstractmethod
    async def emit(self, event: Dict[str, Any]) -> bool:
        """
        Emit an event to the sink.
        
        Args:
            event: Event data dictionary
            
        Returns:
            True if event was accepted, False if dropped or rejected
        """
        ...
    
    @abstractmethod
    async def flush(self, timeout_seconds: Optional[float] = None) -> bool:
        """
        Flush pending events.
        
        Args:
            timeout_seconds: Maximum time to wait for flush
            
        Returns:
            True if all pending events were flushed, False on timeout
        """
        ...
    
    @abstractmethod
    async def close(self) -> None:
        """Close the sink and release resources."""
        ...
    
    @property
    @abstractmethod
    def status(self) -> SinkStatus:
        """Return current sink status."""
        ...
    
    @property
    @abstractmethod
    def queued_count(self) -> int:
        """Return number of events currently queued."""
        ...
    
    @property
    @abstractmethod
    def total_emitted(self) -> int:
        """Return total events emitted (including dropped)."""
        ...
    
    @property
    @abstractmethod
    def total_dropped(self) -> int:
        """Return total events dropped due to buffer full or failure."""
        ...


# =============================================================================
# No-op Sink for Testing/Disabling
# =============================================================================

class NoOpSink(EventSink):
    """
    Event sink that discards all events.
    
    Useful for testing, disabled observability, or when sinks fail.
    """
    
    def __init__(self) -> None:
        self._status = SinkStatus.ACTIVE
        self._total_emitted = 0
    
    async def emit(self, event: Dict[str, Any]) -> bool:
        """Discard the event."""
        self._total_emitted += 1
        return True
    
    async def flush(self, timeout_seconds: Optional[float] = None) -> bool:
        """No-op - nothing to flush."""
        return True
    
    async def close(self) -> None:
        """Mark as closed."""
        self._status = SinkStatus.CLOSED
    
    @property
    def status(self) -> SinkStatus:
        return self._status
    
    @property
    def queued_count(self) -> int:
        return 0
    
    @property
    def total_emitted(self) -> int:
        return self._total_emitted
    
    @property
    def total_dropped(self) -> int:
        return 0


# =============================================================================
# In-Memory Buffer with Bounded Size
# =============================================================================

class InMemorySink(EventSink):
    """
    In-memory event buffer with bounded size and eviction policy.
    
    Events are stored in a deque for O(1) append/popleft operations.
    When full, events are evicted according to the configured policy.
    
    Thread-safety: Uses locking for concurrent access.
    """
    
    def __init__(
        self,
        config: Optional[BoundedBufferConfig] = None
    ) -> None:
        import threading
        
        self._config = config or BoundedBufferConfig()
        self._buffer: Deque[Dict[str, Any]] = deque(maxlen=self._config.max_size)
        self._lock = threading.Lock()
        
        # Statistics
        self._total_emitted = 0
        self._total_dropped = 0
        
        # Status
        self._status = SinkStatus.ACTIVE
    
    async def emit(self, event: Dict[str, Any]) -> bool:
        """
        Emit an event to the buffer.
        
        If buffer is full and policy is DROP_OLDEST, removes oldest events
        until there's room. If policy is DROP_LOWEST_SEVERITY, removes
        lower-severity events.
        
        Args:
            event: Event data dictionary
            
        Returns:
            True if event was accepted (possibly after eviction)
        """
        import time
        
        # Add metadata
        event_with_meta = dict(event)
        event_with_meta["_received_at"] = time.monotonic()
        
        with self._lock:
            self._total_emitted += 1
            
            # If not full, just append
            if len(self._buffer) < self._config.max_size:
                self._buffer.append(event_with_meta)
                return True
            
            # Buffer is full - apply eviction policy
            if self._config.eviction_policy == EvictionPolicy.DROP_OLDEST:
                # Remove oldest event(s) until we have space
                while len(self._buffer) >= self._config.max_size:
                    old_event = self._buffer.popleft()
                    self._total_dropped += 1
                
                self._buffer.append(event_with_meta)
                
            elif self._config.eviction_policy == EvictionPolicy.DROP_LOWEST_SEVERITY:
                # Try to find and remove lower-severity events
                event_severity = event.get("severity", 3)  # INFO level default
                
                if not self._remove_lower_severity_event(event_severity):
                    # No lower severity found - drop this one instead
                    self._total_dropped += 1
                    return False
                
                self._buffer.append(event_with_meta)
            
            return True
    
    def _remove_lower_severity_event(self, target_severity: int) -> bool:
        """
        Try to remove a lower-severity event from the buffer.
        
        Args:
            target_severity: Severity level of incoming event
            
        Returns:
            True if an event was removed
        """
        # Find index of lowest severity event
        min_severity = float('inf')
        min_index = -1
        
        for i, event in enumerate(self._buffer):
            sev = event.get("severity", 3)
            if sev < min_severity:
                min_severity = sev
                min_index = i
        
        # If found and it's lower than target, remove it
        if min_index >= 0 and min_severity < target_severity:
            self._buffer.remove(self._buffer[min_index])
            self._total_dropped += 1
            return True
        
        return False
    
    async def flush(self, timeout_seconds: Optional[float] = None) -> bool:
        """
        Flush pending events.
        
        In-memory sink doesn't have external delivery, so this is a no-op
        that just verifies buffer state.
        
        Args:
            timeout_seconds: Timeout parameter (unused for in-memory)
            
        Returns:
            True (buffer is always "flushed")
        """
        # Record flush time for potential cleanup
        with self._lock:
            if not self._buffer:
                return True
            
            current_time = time.monotonic()
            
            # Check if any events are too old
            timeout = timeout_seconds or self._config.flush_timeout_seconds
            
            # For in-memory, we don't actually remove old events on flush
            # This would be done by a separate cleanup mechanism
            return True
    
    async def close(self) -> None:
        """Mark sink as closed."""
        with self._lock:
            self._status = SinkStatus.CLOSED
            # Don't clear buffer - allow inspection after close
    
    @property
    def status(self) -> SinkStatus:
        return self._status
    
    @property
    def queued_count(self) -> int:
        with self._lock:
            return len(self._buffer)
    
    @property
    def total_emitted(self) -> int:
        return self._total_emitted
    
    @property
    def total_dropped(self) -> int:
        return self._total_dropped
    
    def get_buffer_snapshot(self) -> List[Dict[str, Any]]:
        """Get a copy of the current buffer contents."""
        with self._lock:
            return list(self._buffer)


# =============================================================================
# Redacting Sink Decorator
# =============================================================================

class RedactingSink(EventSink):
    """
    Event sink decorator that redacts sensitive fields from events.
    
    Provides security by ensuring sensitive data is never emitted to sinks.
    
    Usage:
        base_sink = InMemorySink()
        redacting_sink = RedactingSink(base_sink, ["password", "token", "secret"])
        
        await redacting_sink.emit(event_with_sensitive_data)
    """
    
    # Common sensitive field names
    SENSITIVE_PATTERNS = {
        "password",
        "passwd",
        "secret",
        "api_key",
        "apikey",
        "token",
        "access_token",
        "refresh_token",
        "credential",
        "credentials",
        "private_key",
        "auth",
        "authorization",
    }
    
    def __init__(
        self,
        base_sink: EventSink,
        sensitive_keys: Optional[List[str]] = None
    ) -> None:
        self._base_sink = base_sink
        self._sensitive_keys = set(sensitive_keys or [])
        self._sensitive_keys.update(self.SENSITIVE_PATTERNS)
    
    async def emit(self, event: Dict[str, Any]) -> bool:
        """
        Emit an event after redacting sensitive fields.
        
        Args:
            event: Event data dictionary
            
        Returns:
            Result of base sink emit
        """
        # Create a copy and redact
        event_copy = self._redact_event(event)
        
        return await self._base_sink.emit(event_copy)
    
    def _redact_event(self, event: Dict[str, Any]) -> Dict[str, Any]:
        """Create a copy of event with sensitive fields redacted."""
        result = dict(event)
        redacted_fields = []
        
        # Redact direct payload
        if "payload" in result and isinstance(result["payload"], dict):
            result["payload"] = self._redact_dict(result["payload"])
        
        # Check for common sensitive field patterns
        for key, value in list(result.items()):
            if self._is_sensitive_key(key) and not isinstance(value, (int, float, bool)):
                result[key] = "[REDACTED]"
                redacted_fields.append(key)
        
        # Mark event as having been redacted if we made changes
        if redacted_fields:
            result["_redacted"] = True
            result["_redacted_fields"] = redacted_fields
        
        return result
    
    def _is_sensitive_key(self, key: str) -> bool:
        """Check if a key name suggests sensitive data."""
        key_lower = key.lower()
        
        # Direct match
        if key_lower in self._sensitive_keys:
            return True
        
        # Check for common patterns
        for pattern in self.SENSITIVE_PATTERNS:
            if pattern in key_lower:
                return True
        
        return False
    
    def _redact_dict(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Recursively redact sensitive fields in a dictionary."""
        result = {}
        
        for key, value in data.items():
            if self._is_sensitive_key(key):
                result[key] = "[REDACTED]"
            elif isinstance(value, dict):
                result[key] = self._redact_dict(value)
            elif isinstance(value, list):
                result[key] = [
                    self._redact_dict(item) if isinstance(item, dict)
                    else item
                    for item in value
                ]
            else:
                result[key] = value
        
        return result
    
    async def flush(self, timeout_seconds: Optional[float] = None) -> bool:
        """Flush the base sink."""
        return await self._base_sink.flush(timeout_seconds)
    
    async def close(self) -> None:
        """Close the base sink."""
        await self._base_sink.close()
    
    @property
    def status(self) -> SinkStatus:
        return self._base_sink.status
    
    @property
    def queued_count(self) -> int:
        return self._base_sink.queued_count
    
    @property
    def total_emitted(self) -> int:
        return self._base_sink.total_emitted
    
    @property
    def total_dropped(self) -> int:
        return self._base_sink.total_dropped


# =============================================================================
# Fan-out Sink
# =============================================================================

class FanOutSink(EventSink):
    """
    Event sink that fans out events to multiple sinks.
    
    Events are emitted to all registered sinks. If one sink fails,
    others continue processing.
    
    Usage:
        sink1 = InMemorySink()
        sink2 = AnotherSink()
        
        fan_out = FanOutSink([sink1, sink2])
        await fan_out.emit(event)
    """
    
    def __init__(self, sinks: Optional[List[EventSink]] = None) -> None:
        self._sinks = list(sinks or [])
    
    async def emit(self, event: Dict[str, Any]) -> bool:
        """
        Emit to all registered sinks.
        
        Args:
            event: Event data dictionary
            
        Returns:
            True if at least one sink accepted the event
        """
        any_accepted = False
        
        for sink in self._sinks:
            try:
                result = await sink.emit(event)
                if result:
                    any_accepted = True
            except Exception:
                # Continue to other sinks even if one fails
                continue
        
        return any_accepted
    
    async def flush(self, timeout_seconds: Optional[float] = None) -> bool:
        """
        Flush all registered sinks.
        
        Args:
            timeout_seconds: Timeout for each sink's flush
            
        Returns:
            True if all sinks flushed successfully
        """
        all_flushed = True
        
        for sink in self._sinks:
            try:
                result = await sink.flush(timeout_seconds)
                if not result:
                    all_flushed = False
            except Exception:
                all_flushed = False
        
        return all_flushed
    
    async def close(self) -> None:
        """Close all registered sinks."""
        for sink in self._sinks:
            try:
                await sink.close()
            except Exception:
                # Continue closing other sinks
                continue
    
    @property
    def status(self) -> SinkStatus:
        """
        Return aggregated status.
        
        Status is ACTIVE if any sink is active, FAILED if all are failed.
        """
        statuses = [s.status for s in self._sinks]
        
        if SinkStatus.FAILED in statuses and len(statuses) > 0:
            return SinkStatus.FAILED
        
        if SinkStatus.CLOSED in statuses and len(statuses) > 0:
            return SinkStatus.CLOSED
        
        return SinkStatus.ACTIVE
    
    @property
    def queued_count(self) -> int:
        """Return total events across all sinks."""
        return sum(s.queued_count for s in self._sinks)
    
    @property
    def total_emitted(self) -> int:
        """Sum of emitted events across all sinks."""
        return sum(s.total_emitted for s in self._sinks)
    
    @property
    def total_dropped(self) -> int:
        """Sum of dropped events across all sinks."""
        return sum(s.total_dropped for s in self._sinks)


__all__ = [
    "SinkStatus",
    "EvictionPolicy",
    "BoundedBufferConfig",
    "EventSink",
    "NoOpSink",
    "InMemorySink",
    "RedactingSink",
    "FanOutSink",
]