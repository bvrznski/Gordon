# Inference Queue - Request Batching and Queuing Authority
# =========================================================

"""
Inference queue for deterministic request handling and batching.

This module provides:
- Deterministic inference request queuing
- Request batching for efficiency
- Cancellation support
- Timeout management
- Order preservation

Architecture Principle: Exactly ONE inference queue instance exists.
"""

from dataclasses import dataclass, field
from typing import (
    Any,
    Dict,
    List,
    Optional,
    Set,
    Tuple,
)
from enum import Enum, auto
import time
import uuid
from collections import deque


# =============================================================================
# REQUEST AND RESPONSE TYPES
# =============================================================================


class RequestState(Enum):
    """States of an inference request."""
    
    PENDING = "pending"       # Waiting in queue
    BATCHED = "batched"       # Added to batch
    RUNNING = "running"       # Currently executing
    COMPLETED = "completed"   # Finished successfully
    FAILED = "failed"         # Failed during execution
    CANCELLED = "cancelled"   # Cancelled by client


@dataclass(frozen=True)
class InferenceRequest:
    """
    Immutable record of an inference request.
    
    Contains all information needed to process the request.
    """
    
    request_id: str               # Unique request ID
    model_id: str                 # Model to use for inference
    input_data: Dict[str, Any]    # Input data for inference
    priority: int = 0             # Request priority (higher = more urgent)
    
    # Timing
    submitted_at: float = field(default_factory=time.time)  # When queued
    started_at: Optional[float] = None                      # When execution starts
    completed_at: Optional[float] = None                    # When finished
    
    # Configuration
    timeout_ms: int = 30000       # Default 30 second timeout
    batchable: bool = True        # Can be batched with other requests
    
    def elapsed_time_ms(self) -> float:
        """Return time elapsed since submission in milliseconds."""
        end = self.completed_at or time.time()
        return (end - self.submitted_at) * 1000


@dataclass
class InferenceResponse:
    """
    Record of an inference response.
    
    Contains the result of processing a request.
    """
    
    request_id: str               # Original request ID
    output_data: Dict[str, Any]   # Output from model inference
    timing_ms: float              # Total time in milliseconds
    
    success: bool = True          # Whether execution succeeded
    error_message: Optional[str] = None  # Error if failed


# =============================================================================
# BATCH CONFIGURATION
# =============================================================================


@dataclass(frozen=True)
class BatchConfig:
    """
    Configuration for batch processing.
    
    Controls how requests are grouped into batches.
    """
    
    max_batch_size: int = 16          # Maximum requests per batch
    max_wait_ms: int = 100            # Max wait time before forced batch
    min_batch_size: int = 1           # Minimum batch size (can be < max)
    compatible_only: bool = True      # Only batch compatible models


# =============================================================================
# QUEUE ERRORS
# =============================================================================


class QueueError(Exception):
    """Base exception for queue errors."""
    
    pass


class QueueTimeoutError(QueueError):
    """Raised when a request times out in the queue."""
    
    def __init__(self, request_id: str, timeout_ms: int):
        super().__init__(
            f"Request '{request_id}' timed out after {timeout_ms}ms"
        )
        self.request_id = request_id
        self.timeout_ms = timeout_ms


class RequestCancelledError(QueueError):
    """Raised when a request is cancelled."""
    
    def __init__(self, request_id: str):
        super().__init__(f"Request '{request_id}' was cancelled")
        self.request_id = request_id


# =============================================================================
# INFERENCE QUEUE
# =============================================================================


class InferenceQueue:
    """
    Canonical inference queue authority.
    
    This is the SINGLE canonical authority for inference request queuing in Gordon.
    
    Responsibilities:
        - Queue inference requests deterministically
        - Support batching for efficiency
        - Handle cancellation and timeout
        - Preserve request ordering
    
    Does NOT:
        - Execute inference (handled by compute scheduler)
        - Own model lifecycle
        - Manage compute resources
    
    Architecture Invariants:
        - Exactly ONE queue instance exists
        - Queue is deterministic (same inputs = same outputs)
        - No implicit queuing during import
    """
    
    def __init__(
        self,
        config: Optional[BatchConfig] = None,
        max_queue_size: int = 10000,
    ):
        """
        Initialize the inference queue.
        
        Args:
            config: Batch configuration (uses defaults if None)
            max_queue_size: Maximum pending requests
        """
        self._config = config or BatchConfig()
        self._max_queue_size = max_queue_size
        
        # Request storage
        self._requests: Dict[str, InferenceRequest] = {}
        self._pending: deque = deque()
        
        # Batching state
        self._batch_buffer: List[InferenceRequest] = []
        self._last_batch_time: float = time.time()
        
        # Active batches (request_id -> batch_info)
        self._active_batches: Dict[str, Dict[str, Any]] = {}
        
        # Statistics
        self._total_queued = 0
        self._total_processed = 0
        self._total_cancelled = 0
        
        self._lock = __import__("threading").Lock()
    
    @property
    def pending_count(self) -> int:
        """Return number of pending requests."""
        with self._lock:
            return len(self._pending)
    
    @property
    def queue_size_limit(self) -> int:
        """Return maximum queue size."""
        return self._max_queue_size
    
    # -------------------------------------------------------------------------
    # Request queuing (deterministic)
    # -------------------------------------------------------------------------
    
    def submit(
        self,
        request: InferenceRequest,
    ) -> Tuple[bool, Optional[str]]:
        """
        Submit an inference request to the queue.
        
        Args:
            request: The inference request
            
        Returns:
            Tuple of (success, batch_id if batched)
            
        Raises:
            QueueError: If queue is full
        """
        with self._lock:
            # Check capacity
            if len(self._pending) >= self._max_queue_size:
                raise QueueError(
                    f"Queue full (max {self._max_queue_size} requests)"
                )
            
            # Add to pending queue (sorted by priority)
            self._requests[request.request_id] = request
            self._pending.append(request)
            self._total_queued += 1
            
            return self._attempt_batch()
    
    def _attempt_batch(
        self,
    ) -> Tuple[bool, Optional[str]]:
        """
        Attempt to form a batch from pending requests.
        
        Returns:
            Tuple of (batched, batch_id if created)
        """
        # Check if we can/should form a batch
        if not self._config.batchable or len(self._pending) < self._config.min_batch_size:
            return False, None
        
        # Check if enough time has passed for a new batch
        elapsed_ms = (time.time() - self._last_batch_time) * 1000
        if elapsed_ms < self._config.max_wait_ms:
            # Wait for more requests or timeout
            return False, None
        
        # Form the batch
        batch_size = min(
            len(self._pending),
            self._config.max_batch_size
        )
        
        batch_requests = []
        for _ in range(batch_size):
            if self._pending:
                req = self._pending.popleft()
                batch_requests.append(req)
                
                # Update request state
                req.started_at = time.time()
                self._active_batches[req.request_id] = {
                    "batched": True,
                    "started_at": req.started_at,
                }
        
        self._last_batch_time = time.time()
        return len(batch_requests) > 0, str(uuid.uuid4())[:8]
    
    # -------------------------------------------------------------------------
    # Request completion
    # -------------------------------------------------------------------------
    
    def complete(
        self,
        request_id: str,
        output_data: Dict[str, Any],
        success: bool = True,
        error_message: Optional[str] = None,
    ) -> Optional[InferenceResponse]:
        """
        Mark a request as completed.
        
        Args:
            request_id: The request to complete
            output_data: Model output
            success: Whether execution succeeded
            error_message: Error if failed
            
        Returns:
            Response record if found
        """
        with self._lock:
            request = self._requests.get(request_id)
            
            if request is None:
                return None
            
            # Calculate timing
            completed_at = time.time()
            timing_ms = (completed_at - request.started_at) * 1000 if request.started_at else 0
            
            response = InferenceResponse(
                request_id=request_id,
                output_data=output_data,
                timing_ms=timing_ms,
                success=success,
                error_message=error_message,
            )
            
            # Update state
            request.completed_at = completed_at
            self._total_processed += 1
            
            if request_id in self._active_batches:
                del self._active_batches[request_id]
            
            return response
    
    # -------------------------------------------------------------------------
    # Cancellation
    # -------------------------------------------------------------------------
    
    def cancel(self, request_id: str) -> bool:
        """
        Cancel a pending or active request.
        
        Args:
            request_id: The request to cancel
            
        Returns:
            True if cancelled, False if not found
        """
        with self._lock:
            # Check in pending queue
            for i, req in enumerate(self._pending):
                if req.request_id == request_id:
                    del self._pending[i]
                    self._total_cancelled += 1
                    return True
            
            # Check active batches (cannot cancel once running)
            if request_id in self._active_batches:
                # Mark as cancelled but cannot interrupt execution
                self._requests[request_id].completed_at = time.time()
                return False
            
            return False
    
    # -------------------------------------------------------------------------
    # Timeout handling
    # -------------------------------------------------------------------------
    
    def check_timeouts(self) -> List[str]:
        """
        Check for timed-out requests and cancel them.
        
        Returns:
            List of cancelled request IDs
        """
        now = time.time()
        cancelled = []
        
        with self._lock:
            for req in list(self._pending):
                elapsed_ms = (now - req.submitted_at) * 1000
                
                if elapsed_ms > req.timeout_ms:
                    # Cancel this request
                    for i, r in enumerate(self._pending):
                        if r.request_id == req.request_id:
                            del self._pending[i]
                            break
                    
                    cancelled.append(req.request_id)
                    self._total_cancelled += 1
            
            return cancelled
    
    def set_timeout(self, request_id: str, timeout_ms: int) -> bool:
        """
        Update the timeout for a pending request.
        
        Args:
            request_id: The request to update
            timeout_ms: New timeout in milliseconds
            
        Returns:
            True if updated, False if not found
        """
        with self._lock:
            request = self._requests.get(request_id)
            
            if request is None:
                return False
            
            request.timeout_ms = timeout_ms
            return True
    
    # -------------------------------------------------------------------------
    # Statistics
    # -------------------------------------------------------------------------
    
    def get_stats(self) -> Dict[str, Any]:
        """
        Get queue statistics.
        
        Returns:
            Dictionary of queue metrics
        """
        with self._lock:
            return {
                "pending_count": len(self._pending),
                "total_queued": self._total_queued,
                "total_processed": self._total_processed,
                "total_cancelled": self._total_cancelled,
                "queue_utilization": (
                    len(self._pending) / self._max_queue_size
                    if self._max_queue_size > 0 else 0
                ),
            }


# =============================================================================
# GLOBAL QUEUE ACCESSOR
# =============================================================================


class _GlobalInferenceQueue:
    """Internal global inference queue accessor."""
    
    def __init__(self) -> None:
        self._instance: Optional[InferenceQueue] = None
    
    def set_instance(self, instance: InferenceQueue) -> None:
        if self._instance is not None:
            raise RuntimeError("Global inference queue already initialized")
        self._instance = instance
    
    @property
    def instance(self) -> InferenceQueue:
        if self._instance is None:
            self._instance = InferenceQueue()
        return self._instance


_global_queue_accessor = _GlobalInferenceQueue()


def get_inference_queue() -> InferenceQueue:
    """Get the global inference queue instance."""
    return _global_queue_accessor.instance


def set_inference_queue(instance: InferenceQueue) -> None:
    """Set the global inference queue instance."""
    _global_queue_accessor.set_instance(instance)


__all__ = [
    # Enums
    "RequestState",
    # Dataclasses
    "InferenceRequest",
    "InferenceResponse",
    "BatchConfig",
    # Exceptions
    "QueueError",
    "QueueTimeoutError",
    "RequestCancelledError",
    # Queue
    "InferenceQueue",
    # Global accessor
    "get_inference_queue",
    "set_inference_queue",
]