# Core Request-Response Infrastructure
# =====================================

"""
Typed request-response correlation infrastructure.

Request-response patterns:
- Stable request IDs for tracking
- Correlation of requests with responses
- Typed results and failures
- Deadline/timeout enforcement
- Bounded pending-request registries
- Cleanup on shutdown
"""

from dataclasses import dataclass, field
from typing import Dict, Any, Optional, List, Callable
from enum import Enum
import time
import uuid


class RequestState(Enum):
    """States of a request lifecycle."""
    PENDING = "pending"
    DISPATCHED = "dispatched"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"
    TIMEOUT = "timeout"


@dataclass(frozen=True)
class RequestId:
    """Unique identifier for a request."""
    value: str
    
    @classmethod
    def generate(cls) -> "RequestId":
        return cls(value=f"req_{uuid.uuid4().hex[:16]}")
    
    def __str__(self) -> str:
        return self.value


@dataclass(frozen=True)
class ResponseId:
    """Unique identifier for a response."""
    value: str
    
    @classmethod
    def generate(cls) -> "ResponseId":
        return cls(value=f"resp_{uuid.uuid4().hex[:16]}")
    
    def __str__(self) -> str:
        return self.value


@dataclass(frozen=True)
class RequestMetadata:
    """Metadata for requests."""
    request_type: str  # e.g., "task.execute", "state.get"
    
    correlation_id: Optional[str] = None
    causation_id: Optional[str] = None
    
    timestamp_utc: float = field(default_factory=time.time)
    monotonic_time: float = field(default_factory=time.monotonic)
    
    source_id: Optional[str] = None
    destination_id: Optional[str] = None
    
    priority: int = 0
    deadline_utc: Optional[float] = None
    timeout_seconds: Optional[float] = None
    
    security_context: Dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class Request:
    """
    Base class for requests.
    
    Requests expect corresponding responses. They are NOT commands or events -
    they are explicit request-response interactions.
    
    Invariants:
        - Each request has exactly one expected response
        - Responses must match the original request's correlation
        - Bounded lifetime (cleanup on timeout/shutdown)
    """
    
    request_id: RequestId
    payload: Dict[str, Any] = field(default_factory=dict)
    metadata: RequestMetadata = field(default_factory=RequestMetadata)
    
    @property
    def is_expired(self) -> bool:
        """Check if the request has exceeded its deadline."""
        if self.metadata.deadline_utc is None:
            return False
        return time.time() > self.metadata.deadline_utc
    
    @classmethod
    def create(
        cls,
        request_type: str,
        payload: Optional[Dict[str, Any]] = None,
        correlation_id: Optional[str] = None,
        causation_id: Optional[str] = None,
        priority: int = 0,
        deadline_utc: Optional[float] = None,
        timeout_seconds: Optional[float] = None,
    ) -> "Request":
        """Create a new request."""
        metadata = RequestMetadata(
            request_type=request_type,
            correlation_id=correlation_id,
            causation_id=causation_id,
            priority=priority,
            deadline_utc=deadline_utc,
            timeout_seconds=timeout_seconds,
        )
        return cls(
            request_id=RequestId.generate(),
            payload=dict(payload or {}),
            metadata=metadata,
        )


class ResponseType(Enum):
    """Types of responses."""
    SUCCESS = "success"
    FAILURE = "failure"
    ERROR = "error"
    CANCELLED = "cancelled"
    TIMEOUT = "timeout"


@dataclass(frozen=True)
class Response:
    """
    Base class for responses.
    
    Responses are the outcome of a request. They must correlate with
    their original request via correlation_id or request_id matching.
    
    Invariants:
        - Each response corresponds to exactly one request
        - Must include success/failure status
        - May include result data or error information
    """
    
    response_id: ResponseId
    request_id: RequestId  # Reference back to original request
    
    state: RequestState = RequestState.COMPLETED
    response_type: ResponseType = ResponseType.SUCCESS
    
    result_payload: Dict[str, Any] = field(default_factory=dict)
    error_message: Optional[str] = None
    error_type: Optional[str] = None
    
    timestamp_utc: float = field(default_factory=time.time)
    
    # Correlation tracking
    correlation_id: Optional[str] = None
    
    @classmethod
    def success(
        cls,
        request_id: RequestId,
        result_payload: Optional[Dict[str, Any]] = None,
        correlation_id: Optional[str] = None,
    ) -> "Response":
        return cls(
            response_id=ResponseId.generate(),
            request_id=request_id,
            state=RequestState.COMPLETED,
            response_type=ResponseType.SUCCESS,
            result_payload=dict(result_payload or {}),
            correlation_id=correlation_id,
        )
    
    @classmethod
    def failure(
        cls,
        request_id: RequestId,
        error_message: str,
        error_type: Optional[str] = None,
        correlation_id: Optional[str] = None,
    ) -> "Response":
        return cls(
            response_id=ResponseId.generate(),
            request_id=request_id,
            state=RequestState.FAILED,
            response_type=ResponseType.FAILURE,
            error_message=error_message,
            error_type=error_type,
            correlation_id=correlation_id,
        )
    
    @classmethod
    def cancelled(
        cls,
        request_id: RequestId,
        correlation_id: Optional[str] = None,
    ) -> "Response":
        return cls(
            response_id=ResponseId.generate(),
            request_id=request_id,
            state=RequestState.CANCELLED,
            response_type=ResponseType.CANCELLED,
            error_message="Request was cancelled",
            correlation_id=correlation_id,
        )
    
    @classmethod
    def timeout(
        cls,
        request_id: RequestId,
        correlation_id: Optional[str] = None,
    ) -> "Response":
        return cls(
            response_id=ResponseId.generate(),
            request_id=request_id,
            state=RequestState.TIMEOUT,
            response_type=ResponseType.TIMEOUT,
            error_message="Request timed out",
            correlation_id=correlation_id,
        )


class RequestTimeoutError(Exception):
    """Raised when a request exceeds its timeout."""
    
    def __init__(
        self,
        request_id: RequestId,
        message: Optional[str] = None,
    ):
        super().__init__(message or f"Request {request_id} timed out")
        self.request_id = request_id


class ResponseMismatchError(Exception):
    """Raised when a response doesn't match the expected request."""
    
    def __init__(
        self,
        received_response_id: ResponseId,
        expected_request_id: RequestId,
        message: Optional[str] = None,
    ):
        super().__init__(
            message or f"Response mismatch: {received_response_id} != {expected_request_id}"
        )
        self.received_response_id = received_response_id
        self.expected_request_id = expected_request_id


class PendingRequestRegistry:
    """
    Registry for pending requests with timeout and cleanup support.
    
    Tracks all active requests and their responses. Provides:
    - Bounded storage (removes old entries)
    - Timeout-based cleanup
    - Shutdown-aware cancellation
    
    Usage:
        registry = PendingRequestRegistry(max_pending=1000, default_timeout=30)
        
        # Create a request
        request = Request.create("task.execute", {"task": "abc"})
        
        # Register it
        pending_id = await registry.register(request)
        
        # Later, get the response
        response = await registry.wait_for_response(pending_id, timeout=30)
    """
    
    def __init__(
        self,
        max_pending: int = 10000,
        default_timeout_seconds: float = 30.0,
    ):
        self._max_pending = max_pending
        self._default_timeout = default_timeout_seconds
        
        # request_id -> (request, future_or_callback)
        self._pending: Dict[RequestId, Any] = {}
        
        # response_id -> pending_request_id
        self._response_index: Dict[str, RequestId] = {}
        
        self._lock = None
    
    def _get_lock(self):
        import threading
        if self._lock is None:
            self._lock = threading.RLock()
        return self._lock
    
    async def register(
        self,
        request: Request,
        timeout_seconds: Optional[float] = None,
    ) -> str:
        """
        Register a pending request.
        
        Args:
            request: The request that will receive a response
            timeout_seconds: Optional override for default timeout
            
        Returns:
            Pending request ID (may be same as request_id)
            
        Raises:
            RuntimeError: If registry is at capacity
        """
        lock = self._get_lock()
        with lock:
            if len(self._pending) >= self._max_pending:
                raise RuntimeError(
                    f"Pending request registry at capacity ({self._max_pending})"
                )
            
            pending_id = str(request.request_id.value)
            timeout = timeout_seconds or self._default_timeout
            
            # Store with expiration time
            deadline = time.time() + timeout
            
            self._pending[pending_id] = {
                "request": request,
                "deadline_utc": deadline,
                "timeout_seconds": timeout,
            }
            
            return pending_id
    
    def complete(
        self,
        response: Response,
    ) -> bool:
        """
        Complete a pending request with a response.
        
        Args:
            response: The response to apply
            
        Returns:
            True if request was completed, False if not found
        """
        lock = self._get_lock()
        with lock:
            pending_id = str(response.request_id.value)
            
            if pending_id not in self._pending:
                return False
            
            # Store the response
            entry = self._pending[pending_id]
            entry["response"] = response
            entry["completed_at_utc"] = time.time()
            
            return True
    
    def get_pending_request(self, request_id: RequestId) -> Optional[Request]:
        """Get a pending request by ID."""
        lock = self._get_lock()
        with lock:
            pending_id = str(request_id.value)
            entry = self._pending.get(pending_id)
            if entry is None:
                return None
            return entry.get("request")
    
    def get_response(self, request_id: RequestId) -> Optional[Response]:
        """Get response for a completed request."""
        lock = self._get_lock()
        with lock:
            pending_id = str(request_id.value)
            entry = self._pending.get(pending_id)
            return entry.get("response") if entry else None
    
    def remove(self, request_id: RequestId) -> bool:
        """Remove a completed or timed-out request."""
        lock = self._get_lock()
        with lock:
            pending_id = str(request_id.value)
            if pending_id in self._pending:
                del self._pending[pending_id]
                return True
            return False
    
    def cleanup_expired(self) -> List[RequestId]:
        """
        Remove expired requests and return their IDs.
        
        Used for maintenance during operation or shutdown.
        """
        lock = self._get_lock()
        with lock:
            now = time.time()
            expired = [
                RequestId(value=k)
                for k, v in list(self._pending.items())
                if v.get("deadline_utc", float('inf')) < now
            ]
            
            for req_id in expired:
                del self._pending[str(req_id.value)]
            
            return expired
    
    def get_pending_count(self) -> int:
        """Get count of pending requests."""
        lock = self._get_lock()
        with lock:
            return len(self._pending)
    
    def is_at_capacity(self) -> bool:
        """Check if registry is at capacity."""
        return self.get_pending_count() >= self._max_pending


# =============================================================================
# REQUEST-RESPONSE CLIENT
# =============================================================================

class RequestClient:
    """
    Client for making request-response calls.
    
    Manages the full lifecycle of a request including registration,
    dispatch, and response handling.
    """
    
    def __init__(
        self,
        pending_registry: PendingRequestRegistry,
        dispatcher: Optional[Callable[[Request], None]] = None,
    ):
        self._registry = pending_registry
        self._dispatcher = dispatcher
    
    async def send_request(
        self,
        request: Request,
        timeout_seconds: Optional[float] = None,
    ) -> Response:
        """
        Send a request and wait for the response.
        
        Args:
            request: The request to send
            timeout_seconds: Optional override
            
        Returns:
            The response
            
        Raises:
            RequestTimeoutError: If no response within timeout
        """
        # Register pending request
        pending_id = await self._registry.register(request, timeout_seconds)
        
        # Dispatch if dispatcher available
        if self._dispatcher is not None:
            try:
                import asyncio
                future = asyncio.get_event_loop().create_future()
                
                # Store future for later completion
                lock = self._registry._get_lock()
                with lock:
                    entry = self._registry._pending.get(pending_id)
                    if entry:
                        entry["future"] = future
                
                self._dispatcher(request)
                
                # Wait for response or timeout
                try:
                    await asyncio.wait_for(future, timeout=timeout_seconds or 30.0)
                    return future.result()
                except asyncio.TimeoutError:
                    raise RequestTimeoutError(request.request_id)
                    
            except Exception as e:
                # Request failed before completion
                return Response.failure(
                    request_id=request.request_id,
                    error_message=str(e),
                )
        
        # No dispatcher - just wait for external response
        # (In practice, would use event loop or callback)
        import asyncio
        await asyncio.sleep(timeout_seconds or 30.0)
        
        raise RequestTimeoutError(request.request_id)
    
    def receive_response(self, response: Response) -> bool:
        """
        Receive and process a response.
        
        Args:
            response: The response to process
            
        Returns:
            True if the response was processed successfully
        """
        return self._registry.complete(response)


__all__ = [
    # States and types
    "RequestState",
    "ResponseType",
    
    # Identities
    "RequestId",
    "ResponseId",
    
    # Metadata
    "RequestMetadata",
    
    # Contracts
    "Request",
    "Response",
    
    # Errors
    "RequestTimeoutError",
    "ResponseMismatchError",
    
    # Registry
    "PendingRequestRegistry",
    
    # Client
    "RequestClient",
]