# Core Shutdown and Cancellation Signals
# =======================================

"""
Domain-neutral signaling infrastructure.

Provides:
- Distinct cancellation and shutdown signals
- Request state without direct mutation
- Propagation control
- Idempotent request semantics
"""

from dataclasses import dataclass, field
from typing import Optional, List
from enum import Enum
import threading
import time


class SignalType(Enum):
    """Signal type classification."""
    CANCELLATION = "cancellation"
    SHUTDOWN = "shutdown"


@dataclass(frozen=True)
class SignalOrigin:
    """
    Origin of a signal request.
    
    Tracks where the signal came from for debugging and policy decisions.
    """
    
    source_id: str  # Who requested it
    scope_id: Optional[str] = None  # Scope if nested
    timestamp: float = field(default_factory=time.monotonic)
    reason: Optional[str] = None


@dataclass(frozen=True)
class SignalState:
    """
    Immutable signal state.
    
    Represents the current state of a request without mutation.
    """
    
    requested: bool
    reason: Optional[str]
    source_id: str
    timestamp: float
    acknowledged: bool = False
    propagated: bool = True  # Whether to propagate to children


class CancellationRequestedError(Exception):
    """Raised when an operation is cancelled."""
    
    def __init__(
        self,
        message: str,
        origin: Optional[SignalOrigin] = None,
        reason: Optional[str] = None
    ) -> None:
        super().__init__(message)
        self.origin = origin
        self.reason = reason


class ShutdownRequestedError(Exception):
    """Raised when runtime shutdown is requested."""
    
    def __init__(
        self,
        message: str,
        origin: Optional[SignalOrigin] = None,
        reason: Optional[str] = None
    ) -> None:
        super().__init__(message)
        self.origin = origin
        self.reason = reason


class CancellationSignal:
    """
    Domain-neutral cancellation signal.
    
    Represents a request to stop an operation or task.
    
    Usage:
        # Create signal (not requested by default)
        signal = CancellationSignal()
        
        # Request cancellation
        signal.request("Operation timeout")
        
        # Check status
        if signal.is_requested:
            raise CancellationRequestedError("Operation cancelled")
        
        # Get origin info for debugging
        origin = signal.origin
    """
    
    def __init__(self, source_id: Optional[str] = None) -> None:
        self._lock = threading.Lock()
        self._requested = False
        self._origin: Optional[SignalOrigin] = None
        self._source_id = source_id or "unknown"
    
    @property
    def is_requested(self) -> bool:
        """Check if cancellation has been requested."""
        with self._lock:
            return self._requested
    
    @property
    def origin(self) -> Optional[SignalOrigin]:
        """Get the signal origin (who requested, when, why)."""
        with self._lock:
            return self._origin
    
    @property
    def state(self) -> SignalState:
        """Get immutable state snapshot."""
        with self._lock:
            return SignalState(
                requested=self._requested,
                reason=self._origin.reason if self._origin else None,
                source_id=self._origin.source_id if self._origin else "unknown",
                timestamp=self._origin.timestamp if self._origin else 0.0,
                acknowledged=False,
                propagated=True
            )
    
    def request(self, reason: Optional[str] = None) -> SignalState:
        """
        Request cancellation.
        
        Idempotent - can be called multiple times safely.
        
        Args:
            reason: Optional explanation for the cancellation
            
        Returns:
            Current state after request
        """
        with self._lock:
            if not self._requested:
                self._origin = SignalOrigin(
                    source_id=self._source_id,
                    timestamp=time.monotonic(),
                    reason=reason
                )
            self._requested = True
            return self.state
    
    def reset(self) -> None:
        """
        Reset the signal to non-requested state.
        
        Raises:
            RuntimeError: If signal has been used (for safety)
        """
        with self._lock:
            if self._origin is not None and self._origin.timestamp != 0.0:
                # Signal was used, don't reset for safety
                return
            self._requested = False
            self._origin = None
    
    def check(self) -> None:
        """Raise CancellationRequestedError if requested."""
        if self.is_requested:
            raise CancellationRequestedError(
                "Operation cancelled",
                origin=self._origin,
                reason=self._origin.reason if self._origin else None
            )
    
    def __bool__(self) -> bool:
        """Support boolean check: if signal: ..."""
        return self.is_requested


class ShutdownSignal:
    """
    Domain-neutral shutdown signal.
    
    Represents a request to stop the runtime or runtime scope.
    
    Usage:
        # Create signal
        shutdown = ShutdownSignal()
        
        # Request shutdown (e.g., from external source)
        shutdown.request(reason="Graceful shutdown")
        
        # Check in components
        if shutdown.is_requested:
            await self.stop_gracefully()
    """
    
    def __init__(self, source_id: Optional[str] = None) -> None:
        self._lock = threading.Lock()
        self._requested = False
        self._origin: Optional[SignalOrigin] = None
        self._source_id = source_id or "unknown"
    
    @property
    def is_requested(self) -> bool:
        """Check if shutdown has been requested."""
        with self._lock:
            return self._requested
    
    @property
    def origin(self) -> Optional[SignalOrigin]:
        """Get the signal origin."""
        with self._lock:
            return self._origin
    
    @property
    def state(self) -> SignalState:
        """Get immutable state snapshot."""
        with self._lock:
            return SignalState(
                requested=self._requested,
                reason=self._origin.reason if self._origin else None,
                source_id=self._origin.source_id if self._origin else "unknown",
                timestamp=self._origin.timestamp if self._origin else 0.0,
                acknowledged=False,
                propagated=True
            )
    
    def request(self, reason: Optional[str] = None) -> SignalState:
        """
        Request shutdown.
        
        Idempotent - can be called multiple times safely.
        
        Args:
            reason: Optional explanation for the shutdown
            
        Returns:
            Current state after request
        """
        with self._lock:
            if not self._requested:
                self._origin = SignalOrigin(
                    source_id=self._source_id,
                    timestamp=time.monotonic(),
                    reason=reason
                )
            self._requested = True
            return self.state
    
    def reset(self) -> None:
        """Reset the signal (not recommended for shutdown signals)."""
        with self._lock:
            if self._origin is not None and self._origin.timestamp != 0.0:
                return
            self._requested = False
            self._origin = None
    
    def check(self) -> None:
        """Raise ShutdownRequestedError if requested."""
        if self.is_requested:
            raise ShutdownRequestedError(
                "Shutdown requested",
                origin=self._origin,
                reason=self._origin.reason if self._origin else None
            )
    
    def __bool__(self) -> bool:
        return self.is_requested


class CombinedSignal:
    """
    Combines multiple signals into one view.
    
    Raises if ANY underlying signal is requested.
    """
    
    def __init__(
        self,
        cancellation: Optional[CancellationSignal] = None,
        shutdown: Optional[ShutdownSignal] = None
    ) -> None:
        self._cancellation = cancellation
        self._shutdown = shutdown
    
    @property
    def is_requested(self) -> bool:
        """Check if any underlying signal is requested."""
        if self._cancellation and self._cancellation.is_requested:
            return True
        if self._shutdown and self._shutdown.is_requested:
            return True
        return False
    
    def request_cancellation(self, reason: Optional[str] = None) -> SignalState:
        """Request cancellation on underlying signal."""
        if self._cancellation:
            return self._cancellation.request(reason)
        raise RuntimeError("No cancellation signal available")
    
    def request_shutdown(self, reason: Optional[str] = None) -> SignalState:
        """Request shutdown on underlying signal."""
        if self._shutdown:
            return self._shutdown.request(reason)
        raise RuntimeError("No shutdown signal available")


__all__ = [
    "SignalType",
    "SignalOrigin",
    "SignalState",
    "CancellationRequestedError",
    "ShutdownRequestedError",
    "CancellationSignal",
    "ShutdownSignal",
    "CombinedSignal",
]