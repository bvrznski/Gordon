# Core Local Transport Layer
# ===========================

"""
Local in-process communication transport.

Provides:
- Synchronous and asynchronous dispatch
- Bounded queue delivery with backpressure
- Dead-letter handling for undeliverable messages
- Lifecycle-aware operation (start/stop)
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Callable, Any, Protocol, Awaitable
from enum import Enum
import time
import asyncio
import threading


class DeliveryMode(Enum):
    """Delivery mode for local transport."""
    SYNCHRONOUS = "synchronous"   # Block until handler completes
    ASYNCHRONOUS = "async"        # Fire and forget to queue
    IMMEDIATE = "immediate"       # Execute immediately without queuing


@dataclass(frozen=True)
class DeliveryResult:
    """Result of a delivery attempt."""
    
    success: bool
    mode: DeliveryMode = DeliveryMode.SYNCHRONOUS
    
    message_id: Optional[str] = None
    handler_id: Optional[str] = None
    
    error_message: Optional[str] = None
    error_type: Optional[str] = None
    
    queue_wait_ms: float = 0.0
    delivery_latency_ms: float = 0.0
    processing_latency_ms: float = 0.0
    
    @classmethod
    def success(
        cls,
        message_id: str,
        handler_id: Optional[str] = None,
        queue_wait_ms: float = 0.0,
        delivery_latency_ms: float = 0.0,
        processing_latency_ms: float = 0.0,
    ) -> "DeliveryResult":
        return cls(
            success=True,
            message_id=message_id,
            handler_id=handler_id,
            queue_wait_ms=queue_wait_ms,
            delivery_latency_ms=delivery_latency_ms,
            processing_latency_ms=processing_latency_ms,
        )
    
    @classmethod
    def failure(
        cls,
        message_id: str,
        error_message: str,
        error_type: Optional[str] = None,
        queue_wait_ms: float = 0.0,
        delivery_latency_ms: float = 0.0,
    ) -> "DeliveryResult":
        return cls(
            success=False,
            message_id=message_id,
            error_message=error_message,
            error_type=error_type,
            queue_wait_ms=queue_wait_ms,
            delivery_latency_ms=delivery_latency_ms,
        )


class LocalTransportConfig:
    """Configuration for local transport."""
    
    def __init__(
        self,
        default_queue_size: int = 10000,
        default_delivery_mode: DeliveryMode = DeliveryMode.SYNCHRONOUS,
        max_handlers_per_message: int = 1,  # For commands (single handler)
        async_workers: int = 4,
    ):
        self.default_queue_size = default_queue_size
        self.default_delivery_mode = default_delivery_mode
        self.max_handlers_per_message = max_handlers_per_message
        self.async_workers = async_workers


class LocalTransport:
    """
    Canonical local in-process transport.
    
    This is THE ONE authority for message delivery within the runtime instance.
    
    Invariants maintained:
        1. Bounded queues (never grow unbounded)
        2. Lifecycle-aware (start/stop required)
        3. Synchronous or asynchronous delivery
        4. Dead-letter handling for failures
    """
    
    def __init__(self, config: Optional[LocalTransportConfig] = None):
        self._config = config or LocalTransportConfig()
        
        # State
        self._lock = threading.RLock()
        self._running = False
        
        # Message handlers by message type
        self._handlers: Dict[str, List[Callable]] = {}
        
        # Async task queue and workers
        self._queue: asyncio.Queue = None  # Initialized on start
        self._workers: List[asyncio.Task] = []
        
        # Statistics
        self._messages_accepted = 0
        self._messages_delivered = 0
        self._messages_failed = 0
        
        # Dead letter storage
        self._dead_letters: List[Dict[str, Any]] = []
    
    def start(self) -> None:
        """Start the transport and workers."""
        with self._lock:
            if self._running:
                return
            
            import asyncio
            self._queue = asyncio.Queue(maxsize=self._config.default_queue_size)
            
            # Start async workers
            for i in range(self._config.async_workers):
                task = asyncio.create_task(self._worker_loop(i))
                self._workers.append(task)
            
            self._running = True
    
    def stop(self) -> None:
        """Stop the transport and wait for workers to finish."""
        with self._lock:
            if not self._running:
                return
            
            # Signal workers to stop (via sentinel)
            import asyncio
            for _ in range(len(self._workers)):
                try:
                    self._queue.put_nowait(None)  # Sentinel
                except asyncio.QueueFull:
                    pass
            
            # Wait for workers to finish
            async def wait_for_workers():
                if self._workers:
                    await asyncio.gather(*self._workers, return_exceptions=True)
            
            asyncio.run(wait_for_workers())
            
            self._workers.clear()
            self._running = False
    
    @property
    def is_running(self) -> bool:
        """Check if transport is running."""
        with self._lock:
            return self._running
    
    def register_handler(
        self,
        message_type: str,
        handler: Callable[[Any], Any],
        max_handlers: Optional[int] = None,
    ) -> bool:
        """
        Register a handler for a message type.
        
        Args:
            message_type: The message type to handle
            handler: Sync or async callable that processes messages
            max_handlers: Max concurrent handlers (None = unlimited)
            
        Returns:
            True if registration succeeded
        """
        with self._lock:
            if message_type not in self._handlers:
                self._handlers[message_type] = []
            
            # Check limit
            if max_handlers and len(self._handlers[message_type]) >= max_handlers:
                return False
            
            self._handlers[message_type].append(handler)
            return True
    
    def unregister_handler(
        self,
        message_type: str,
        handler: Callable[[Any], Any],
    ) -> bool:
        """Remove a registered handler."""
        with self._lock:
            if message_type not in self._handlers:
                return False
            
            try:
                self._handlers[message_type].remove(handler)
                
                # Clean up empty list
                if not self._handlers[message_type]:
                    del self._handlers[message_type]
                
                return True
            except ValueError:
                return False
    
    def send(
        self,
        message: Any,
        message_type: Optional[str] = None,
        mode: Optional[DeliveryMode] = None,
    ) -> DeliveryResult:
        """
        Send a message for delivery.
        
        Args:
            message: The message to send
            message_type: Type of the message (auto-detect if not provided)
            mode: Delivery mode override
            
        Returns:
            Delivery result with success/failure and timing
        """
        start_time = time.monotonic()
        
        # Get message type from payload if not provided
        msg_type = message_type or self._detect_message_type(message)
        
        if not msg_type:
            return DeliveryResult.failure(
                message_id=str(id(message)),
                error_message="Could not determine message type",
            )
        
        # Determine handler(s)
        handlers = self._get_handlers(msg_type)
        
        if not handlers:
            return DeliveryResult.failure(
                message_id=str(id(message)),
                error_message=f"No handler registered for type: {msg_type}",
            )
        
        mode = mode or self._config.default_delivery_mode
        
        queue_wait = time.monotonic() - start_time
        delivery_latency = 0.0
        processing_latency = 0.0
        
        if len(handlers) > self._config.max_handlers_per_message:
            handlers = handlers[:self._config.max_handlers_per_message]
        
        # Execute based on mode
        success = True
        
        for handler in handlers:
            handler_start = time.monotonic()
            
            try:
                if asyncio.iscoroutinefunction(handler):
                    if mode == DeliveryMode.SYNCHRONOUS:
                        import asyncio
                        asyncio.run(handler(message))
                    elif mode == DeliveryMode.ASYNCHRONOUS:
                        # Add to queue for async worker
                        self._queue.put_nowait((message, handler))
                else:
                    # Sync handler
                    if mode == DeliveryMode.IMMEDIATE or mode == DeliveryMode.SYNCHRONOUS:
                        handler(message)
                    elif mode == DeliveryMode.ASYNCHRONOUS:
                        self._queue.put_nowait((message, handler))
                
                delivery_latency += time.monotonic() - handler_start
                
            except Exception as e:
                success = False
                self._record_dead_letter(
                    message=message,
                    error=str(e),
                    handler=handler,
                )
                self._messages_failed += 1
        
        total_latency = time.monotonic() - start_time
        
        if success:
            self._messages_delivered += 1
        
        return DeliveryResult(
            success=success,
            mode=mode,
            message_id=str(id(message)),
            queue_wait_ms=queue_wait * 1000,
            delivery_latency_ms=delivery_latency * 1000,
            processing_latency_ms=(total_latency - queue_wait - delivery_latency) * 1000,
        )
    
    def publish(
        self,
        message: Any,
        message_type: Optional[str] = None,
    ) -> int:
        """
        Publish a message to all handlers (fan-out).
        
        Args:
            message: The message to publish
            message_type: Type of the message
            
        Returns:
            Number of handlers that received the message
        """
        msg_type = message_type or self._detect_message_type(message)
        handlers = self._get_handlers(msg_type)
        
        if not handlers:
            return 0
        
        # Fire and forget to async queue for fan-out
        count = len(handlers)
        
        for handler in handlers:
            try:
                self._queue.put_nowait((message, handler))
            except asyncio.QueueFull:
                break
        
        return min(count, self._config.default_queue_size)
    
    def _detect_message_type(self, message: Any) -> Optional[str]:
        """Try to detect the message type from its structure."""
        if hasattr(message, 'get'):
            # Dict-like
            return message.get('type') or message.get('message_type')
        
        if hasattr(message, '__class__'):
            return message.__class__.__name__.lower()
        
        return None
    
    def _get_handlers(self, message_type: str) -> List[Callable]:
        """Get handlers for a message type."""
        with self._lock:
            return list(self._handlers.get(message_type, []))
    
    async def _worker_loop(self, worker_id: int) -> None:
        """Async worker loop for processing queued messages."""
        import asyncio
        
        while True:
            try:
                item = await self._queue.get()
                
                if item is None:  # Sentinel - shutdown
                    self._queue.task_done()
                    break
                
                message, handler = item
                
                try:
                    start_time = time.monotonic()
                    
                    if asyncio.iscoroutinefunction(handler):
                        await handler(message)
                    else:
                        # Run sync handler in thread pool
                        loop = asyncio.get_event_loop()
                        await loop.run_in_executor(None, handler, message)
                    
                    self._messages_delivered += 1
                    
                except Exception as e:
                    self._record_dead_letter(
                        message=message,
                        error=str(e),
                        handler=handler,
                    )
                    self._messages_failed += 1
                
                finally:
                    self._queue.task_done()
                    
            except asyncio.CancelledError:
                break
    
    def _record_dead_letter(
        self,
        message: Any,
        error: str,
        handler: Optional[Callable] = None,
    ) -> None:
        """Record a message as dead letter."""
        with self._lock:
            entry = {
                "message": message,
                "error": error,
                "handler_id": str(id(handler)) if handler else None,
                "timestamp_utc": time.time(),
            }
            
            self._dead_letters.append(entry)
            
            # Trim to max size
            max_dlq_size = 10000
            while len(self._dead_letters) > max_dlq_size:
                self._dead_letters.pop(0)
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get transport statistics."""
        with self._lock:
            return {
                "running": self._running,
                "handlers_count": sum(len(h) for h in self._handlers.values()),
                "messages_accepted": self._messages_accepted,
                "messages_delivered": self._messages_delivered,
                "messages_failed": self._messages_failed,
                "queue_size": self._queue.qsize() if self._queue else 0,
                "dead_letter_count": len(self._dead_letters),
            }


class LocalDeliveryProtocol(Protocol):
    """Protocol for local delivery operations."""
    
    def send(
        self,
        message: Any,
        message_type: Optional[str] = None,
        mode: Optional[DeliveryMode] = None,
    ) -> DeliveryResult:
        ...
    
    def publish(
        self,
        message: Any,
        message_type: Optional[str] = None,
    ) -> int:
        ...


__all__ = [
    # Types
    "DeliveryMode",
    
    # Results
    "DeliveryResult",
    
    # Config
    "LocalTransportConfig",
    
    # Transport
    "LocalTransport",
    "LocalDeliveryProtocol",
]