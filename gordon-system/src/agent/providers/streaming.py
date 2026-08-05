# Provider Streaming - Async Stream Management
# ==============================================
"""
Streaming support for provider capability requests.

This module provides:
- StreamState: Track streaming session state
- StreamOptions: Configure stream behavior
- CancellationToken: Cancel streaming on request
- StreamContext: Context manager for stream lifecycle
- BackpressureController: Handle backpressure during streaming
- StreamTimeoutManager: Manage per-chunk timeouts
- ManagedStream: Wrapper for async iterator with cleanup
"""
from dataclasses import dataclass, field
from typing import Protocol, AsyncIterator, Optional, Dict, Any, List, Tuple, Set
from enum import Enum
import time
import asyncio
import uuid


class StreamState(Enum):
    """States of a streaming session."""
    CREATED = "created"         # Stream initialized but not started
    ACTIVE = "active"           # Streaming in progress
    PAUSED = "paused"           # Temporarily paused
    COMPLETED = "completed"     # All data received
    CANCELLED = "cancelled"     # Cancelled by consumer
    ERRORED = "errored"         # Error occurred


@dataclass(frozen=True)
class StreamOptions:
    """
    Options for stream configuration.
    
    Args:
        timeout_seconds: Per-chunk timeout
        max_buffer_size: Maximum buffered chunks
        backpressure_threshold: When to pause producer
        auto_resume: Whether to resume after buffer clears
    """
    timeout_seconds: float = 60.0
    max_buffer_size: int = 100
    backpressure_threshold: int = 80
    auto_resume: bool = True


@dataclass(frozen=True)
class StreamEnvelope:
    """
    A single message in a stream.
    
    Args:
        sequence: Sequence number (0-indexed)
        data: The streamed data
        done: Whether this is the final chunk
        error: Optional error if this chunk represents an error state
    """
    sequence: int
    data: Any
    done: bool = False
    error: Optional[Exception] = None


@dataclass(frozen=True)
class CancellationToken:
    """
    Token for cancelling a stream.
    
    Provides thread-safe cancellation signaling.
    
    Args:
        token_id: Unique identifier for this token
    """
    token_id: str = field(default_factory=lambda: f"cancel_{uuid.uuid4().hex[:8]}")
    _cancelled: bool = False
    _lock: asyncio.Lock = field(default_factory=asyncio.Lock)
    
    async def cancel(self) -> None:
        """Cancel the stream."""
        async with self._lock:
            self._cancelled = True
    
    async def is_cancelled(self) -> bool:
        """Check if cancellation has been requested."""
        async with self._lock:
            return self._cancelled


@dataclass(frozen=True)
class StreamContext:
    """
    Context for a streaming operation.
    
    Args:
        context_id: Unique identifier for this stream
        created_at: Timestamp of creation
        options: Stream configuration
        cancellation_token: Token for cancellation
    """
    context_id: str = field(default_factory=lambda: f"stream_{uuid.uuid4().hex[:8]}")
    created_at: float = field(default_factory=time.monotonic)
    options: StreamOptions = field(default_factory=StreamOptions)
    cancellation_token: CancellationToken = field(default_factory=CancellationToken)


class BackpressureController:
    """
    Controller for managing backpressure during streaming.
    
    Detects when the consumer cannot keep up and applies
    appropriate throttling or pause signals.
    """
    
    def __init__(
        self,
        max_buffer_size: int = 100,
        threshold: float = 0.8,
    ):
        """
        Initialize the backpressure controller.
        
        Args:
            max_buffer_size: Maximum buffered items
            threshold: Ratio at which to trigger backpressure
        """
        self._max_buffer = max_buffer_size
        self._threshold = threshold
        self._current_buffer = 0
        self._paused = False
        self._lock = asyncio.Lock()
    
    @property
    def is_paused(self) -> bool:
        """Check if backpressure has paused the stream."""
        return self._paused
    
    async def record_sent(self, count: int = 1) -> None:
        """Record items sent to consumer."""
        async with self._lock:
            self._current_buffer += count
            if not self._paused and self._current_buffer >= self._max_buffer * self._threshold:
                self._paused = True
    
    async def record_received(self, count: int = 1) -> None:
        """Record items received/consumed."""
        async with self._lock:
            self._current_buffer = max(0, self._current_buffer - count)
            if self._paused and self._current_buffer <= self._max_buffer * (self._threshold / 2):
                self._paused = False
    
    async def should_pause(self) -> bool:
        """Check if producer should pause."""
        async with self._lock:
            return self._current_buffer >= self._max_buffer
    
    async def wait_if_paused(self, timeout: Optional[float] = None) -> bool:
        """
        Wait if paused, return False if cancelled.
        
        Args:
            timeout: Maximum time to wait
            
        Returns:
            True if unpaused, False if cancelled
        """
        start_time = time.monotonic()
        
        while self._paused:
            remaining = None if timeout is None else timeout - (time.monotonic() - start_time)
            
            if remaining is not None and remaining <= 0:
                return False
            
            await asyncio.sleep(0.1)
        
        return True


class StreamTimeoutManager:
    """
    Manager for stream chunk timeouts.
    
    Tracks time between chunks and can cancel slow streams.
    """
    
    def __init__(self, timeout_seconds: float = 60.0):
        """
        Initialize the timeout manager.
        
        Args:
            timeout_seconds: Per-chunk timeout
        """
        self._timeout = timeout_seconds
        self._last_chunk_time: Optional[float] = None
        self._lock = asyncio.Lock()
    
    async def record_chunk(self) -> bool:
        """
        Record a chunk arrival and check for timeout.
        
        Returns:
            True if within timeout, False if timed out
        """
        async with self._lock:
            now = time.monotonic()
            
            if self._last_chunk_time is not None:
                elapsed = now - self._last_chunk_time
                if elapsed > self._timeout:
                    return False
            
            self._last_chunk_time = now
            return True
    
    async def reset(self) -> None:
        """Reset the timeout timer."""
        async with self._lock:
            self._last_chunk_time = time.monotonic()


class ManagedStream(Protocol):
    """
    Protocol for a managed streaming provider.
    
    Provides async iteration with automatic cleanup.
    """
    
    async def __aiter__(self) -> AsyncIterator[StreamEnvelope]:
        """Iterate over stream chunks."""
        ...
    
    async def cancel(self) -> None:
        """Cancel the stream."""
        ...
    
    async def close(self) -> None:
        """Close the stream and release resources."""
        ...
    
    @property
    def state(self) -> StreamState:
        """Get current stream state."""
        ...


class StreamPool:
    """
    Pool of managed streams for efficient reuse.
    
    Manages a pool of stream contexts to reduce allocation overhead
    during high-volume streaming operations.
    """
    
    def __init__(
        self,
        max_size: int = 10,
        idle_timeout_seconds: float = 30.0,
    ):
        """
        Initialize the stream pool.
        
        Args:
            max_size: Maximum number of streams in pool
            idle_timeout_seconds: How long idle streams are kept
        """
        self._max_size = max_size
        self._idle_timeout = idle_timeout_seconds
        
        # Available streams (context_id -> StreamContext)
        self._available: Dict[str, Tuple[StreamContext, float]] = {}
        
        # In-use streams
        self._in_use: Set[str] = set()
        
        self._lock = asyncio.Lock()
    
    async def acquire(self) -> StreamContext:
        """
        Acquire a stream context from the pool.
        
        Returns:
            A new or reused stream context
        """
        async with self._lock:
            now = time.monotonic()
            
            # Clean up expired entries first
            expired = [
                cid for cid, (_, t) in self._available.items()
                if now - t > self._idle_timeout
            ]
            for cid in expired:
                del self._available[cid]
            
            # Try to reuse an existing context
            if self._available:
                cid, _ = next(iter(self._available.items()))
                context = self._available.pop(cid)[0]
                self._in_use.add(cid)
                return context
            
            # Create new context
            context = StreamContext()
            self._in_use.add(context.context_id)
            return context
    
    async def release(self, context: StreamContext) -> None:
        """
        Release a stream context back to the pool.
        
        Args:
            context: The context to release
        """
        async with self._lock:
            if context.context_id in self._in_use:
                self._in_use.remove(context.context_id)
                
                # Only add to available if under max size
                if len(self._available) < self._max_size:
                    self._available[context.context_id] = (context, time.monotonic())
    
    def size(self) -> int:
        """Get current pool size."""
        return len(self._available)
    
    def in_use_count(self) -> int:
        """Get number of streams currently in use."""
        return len(self._in_use)


class StreamCancelledError(Exception):
    """Raised when a stream is cancelled."""
    pass


class StreamTimeoutError(Exception):
    """Raised when a stream chunk times out."""
    pass


async def stream_with_context(
    context: StreamContext,
    iterator: AsyncIterator[Any],
) -> AsyncIterator[StreamEnvelope]:
    """
    Wrap an async iterator with stream context management.
    
    Args:
        context: The stream context
        iterator: The underlying iterator
        
    Yields:
        StreamEnvelopes with sequence numbers and data
    """
    sequence = 0
    
    try:
        async for item in iterator:
            # Check for cancellation
            if await context.cancellation_token.is_cancelled():
                raise StreamCancelledError(f"Stream {context.context_id} was cancelled")
            
            envelope = StreamEnvelope(
                sequence=sequence,
                data=item,
                done=False,
            )
            
            yield envelope
            sequence += 1
        
        # Emit final completion envelope
        yield StreamEnvelope(
            sequence=sequence,
            data=None,
            done=True,
        )
        
    except asyncio.CancelledError:
        await context.cancellation_token.cancel()
        raise


async def stream_with_timeout(
    iterator: AsyncIterator[StreamEnvelope],
    timeout_manager: StreamTimeoutManager,
) -> AsyncIterator[StreamEnvelope]:
    """
    Wrap a stream with timeout checking.
    
    Args:
        iterator: The stream to wrap
        timeout_manager: Manages per-chunk timeouts
        
    Yields:
        Envelopes from the underlying iterator
        
    Raises:
        StreamTimeoutError: If a chunk takes too long
    """
    async for envelope in iterator:
        if not await timeout_manager.record_chunk():
            raise StreamTimeoutError(
                f"Stream chunk timed out after {timeout_manager._timeout}s"
            )
        
        yield envelope


async def stream_with_backpressure(
    iterator: AsyncIterator[StreamEnvelope],
    controller: BackpressureController,
) -> AsyncIterator[StreamEnvelope]:
    """
    Wrap a stream with backpressure control.
    
    Args:
        iterator: The stream to wrap
        controller: Manages backpressure signals
        
    Yields:
        Envelopes from the underlying iterator
    """
    async for envelope in iterator:
        # Check if we should pause
        if await controller.should_pause():
            if not await controller.wait_if_paused(timeout=60.0):
                raise StreamCancelledError("Stream paused and cancelled")
        
        yield envelope
        
        # Record that consumer received this item
        await controller.record_received()


__all__ = [
    # Enums
    "StreamState",
    
    # Data classes
    "StreamOptions",
    "StreamEnvelope",
    "CancellationToken",
    "StreamContext",
    
    # Classes
    "BackpressureController",
    "StreamTimeoutManager",
    "ManagedStream",
    "StreamPool",
    
    # Errors
    "StreamCancelledError",
    "StreamTimeoutError",
]