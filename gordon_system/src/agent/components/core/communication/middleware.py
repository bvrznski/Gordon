# Core Middleware Infrastructure
# ==============================

"""
Middleware for cross-cutting communication concerns.

Middleware provides:
- Validation before dispatch
- Tracing and observability injection
- Authorization checks
- Rate limiting
- Dead-letter routing on failure
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Callable, Any, Protocol
from enum import Enum
import time


class MiddlewarePhase(Enum):
    """Phases where middleware can run."""
    VALIDATION = "validation"       # Before any processing
    AUTHORIZATION = "authorization"  # Security checks
    OBSERVABILITY = "observability"  # Tracing/metrics
    ENRICHMENT = "enrichment"      # Add context
    TRANSFORMATION = "transformation"  # Modify message
    DEAD_LETTER = "dead_letter"    # On failure routing


@dataclass(frozen=True)
class MiddlewareId:
    """Unique identifier for middleware."""
    value: str
    
    @classmethod
    def generate(cls) -> "MiddlewareId":
        import uuid
        return cls(value=f"mw_{uuid.uuid4().hex[:16]}")
    
    def __str__(self) -> str:
        return self.value


@dataclass(frozen=True)
class MiddlewareContext:
    """Context passed through middleware chain."""
    
    message: Any
    timestamp_utc: float = field(default_factory=time.time)
    
    # Observability
    trace_id: Optional[str] = None
    span_id: Optional[str] = None
    
    # Auth
    actor_id: Optional[str] = None
    permissions: List[str] = field(default_factory=list)
    
    # Custom context
    custom: Dict[str, Any] = field(default_factory=dict)


class MiddlewareResultType(Enum):
    """Types of middleware results."""
    CONTINUE = "continue"      # Continue to next middleware
    REJECT = "reject"         # Reject message
    TRANSFORM = "transform"   # Message transformed
    DEAD_LETTER = "dead_letter"  # Route to DLQ


@dataclass(frozen=True)
class MiddlewareResult:
    """Result of middleware processing."""
    
    result_type: MiddlewareResultType = MiddlewareResultType.CONTINUE
    
    message: Optional[Any] = None  # Transformed message or original
    error_message: Optional[str] = None  # Rejection reason
    
    custom: Dict[str, Any] = field(default_factory=dict)


class Middleware(Protocol):
    """Protocol for middleware components."""
    
    async def __call__(
        self,
        context: MiddlewareContext,
        next_middleware: Callable[[MiddlewareContext], Any],
    ) -> MiddlewareResult:
        """
        Process message through this middleware.
        
        Args:
            context: Current context (includes message, tracing, auth)
            next_middleware: Function to call for next middleware
            
        Returns:
            Result indicating continue/reject/transform
        """


# =============================================================================
# BUILT-IN MIDDLEWARE
# =============================================================================

class ValidationMiddleware:
    """Validates messages before dispatch."""
    
    def __init__(self, validator: Optional[Callable[[Any], bool]] = None):
        self._validator = validator or (lambda x: True)
    
    async def __call__(
        self,
        context: MiddlewareContext,
        next_middleware: Callable[[MiddlewareContext], Any],
    ) -> MiddlewareResult:
        if not self._validator(context.message):
            return MiddlewareResult(
                result_type=MiddlewareResultType.REJECT,
                error_message="Message validation failed",
            )
        
        # Pass to next middleware
        return await next_middleware(context)


class AuthorizationMiddleware:
    """Checks authorization before dispatch."""
    
    def __init__(self, authorizer: Callable[[MiddlewareContext], bool]):
        self._authorizer = authorizer
    
    async def __call__(
        self,
        context: MiddlewareContext,
        next_middleware: Callable[[MiddlewareContext], Any],
    ) -> MiddlewareResult:
        if not self._authorizer(context):
            return MiddlewareResult(
                result_type=MiddlewareResultType.REJECT,
                error_message="Not authorized",
            )
        
        return await next_middleware(context)


class TracingMiddleware:
    """Adds tracing context to messages."""
    
    async def __call__(
        self,
        context: MiddlewareContext,
        next_middleware: Callable[[MiddlewareContext], Any],
    ) -> MiddlewareResult:
        import time
        
        # Start timing
        start_time = time.monotonic()
        
        try:
            result = await next_middleware(context)
            
            if hasattr(result, 'custom'):
                result.custom['duration_ms'] = (time.monotonic() - start_time) * 1000
            
            return result
            
        except Exception as e:
            if hasattr(e, 'custom'):
                e.custom['duration_ms'] = (time.monotonic() - start_time) * 1000
            raise


class DeadLetterMiddleware:
    """Routes failures to dead-letter queue."""
    
    def __init__(
        self,
        dlq: Any,  # Dead letter queue interface
        max_retries: int = 3,
    ):
        self._dlq = dlq
        self._max_retries = max_retries
    
    async def __call__(
        self,
        context: MiddlewareContext,
        next_middleware: Callable[[MiddlewareContext], Any],
    ) -> MiddlewareResult:
        try:
            return await next_middleware(context)
            
        except Exception as e:
            # Check retry count
            retry_count = context.custom.get('retry_count', 0)
            
            if retry_count >= self._max_retries:
                # Send to dead-letter queue
                if self._dlq:
                    self._dlq.add(
                        message=context.message,
                        error=str(e),
                        reason="max_retries_exceeded",
                    )
                
                return MiddlewareResult(
                    result_type=MiddlewareResultType.DEAD_LETTER,
                    error_message=f"Max retries ({self._max_retries}) exceeded: {e}",
                )
            
            # Add retry context and re-throw for retry
            context.custom['retry_count'] = retry_count + 1
            
            raise


class RateLimitMiddleware:
    """Rate limiting middleware."""
    
    def __init__(
        self,
        rate_limit: int,  # requests per window
        window_seconds: float = 60.0,
    ):
        self._rate_limit = rate_limit
        self._window = window_seconds
        
        # Simple counter-based rate limit
        import threading
        self._lock = threading.Lock()
        self._requests: List[float] = []
    
    async def __call__(
        self,
        context: MiddlewareContext,
        next_middleware: Callable[[MiddlewareContext], Any],
    ) -> MiddlewareResult:
        now = time.time()
        
        with self._lock:
            # Clean old requests outside window
            cutoff = now - self._window
            self._requests = [t for t in self._requests if t > cutoff]
            
            if len(self._requests) >= self._rate_limit:
                return MiddlewareResult(
                    result_type=MiddlewareResultType.REJECT,
                    error_message="Rate limit exceeded",
                )
            
            # Record this request
            self._requests.append(now)
        
        return await next_middleware(context)


class EnrichmentMiddleware:
    """Enriches messages with additional context."""
    
    def __init__(self, enricher: Callable[[Any], Dict[str, Any]]):
        self._enricher = enricher
    
    async def __call__(
        self,
        context: MiddlewareContext,
        next_middleware: Callable[[MiddlewareContext], Any],
    ) -> MiddlewareResult:
        enrichment = self._enricher(context.message)
        
        new_context = MiddlewareContext(
            message=context.message,
            timestamp_utc=context.timestamp_utc,
            trace_id=context.trace_id,
            span_id=context.span_id,
            actor_id=context.actor_id,
            permissions=list(context.permissions),
            custom={**context.custom, **enrichment},
        )
        
        return await next_middleware(new_context)


# =============================================================================
# MIDDLEWARE CHAIN
# =============================================================================

class MiddlewareChain:
    """
    Ordered chain of middleware processors.
    
    Each middleware can:
    - Modify the context/message
    - Short-circuit with rejection
    - Pass to next middleware
    
    Order matters! Common ordering:
        1. Validation (reject invalid early)
        2. Authorization (security before processing)
        3. Observability (trace all)
        4. Enrichment (add context)
        5. Main handler
        6. Transformation (modify output if needed)
    """
    
    def __init__(self):
        self._lock = None
        self._middleware: List[Middleware] = []
        self._phases: Dict[MiddlewarePhase, List[str]] = {}
    
    def _get_lock(self):
        import threading
        if self._lock is None:
            self._lock = threading.RLock()
        return self._lock
    
    def add(
        self,
        middleware: Middleware,
        phase: Optional[MiddlewarePhase] = None,
    ) -> MiddlewareId:
        """
        Add middleware to the chain.
        
        Args:
            middleware: The middleware component
            phase: Optional phase for ordering (default = any)
            
        Returns:
            Middleware ID for removal
        """
        lock = self._get_lock()
        with lock:
            mw_id = MiddlewareId.generate().value
            
            if phase is not None:
                if phase not in self._phases:
                    self._phases[phase] = []
                # Insert at appropriate position based on phase order
                phase_order = [
                    MiddlewarePhase.VALIDATION,
                    MiddlewarePhase.AUTHORIZATION,
                    MiddlewarePhase.OBSERVABILITY,
                    MiddlewarePhase.ENRICHMENT,
                    MiddlewarePhase.TRANSFORMATION,
                    MiddlewarePhase.DEAD_LETTER,
                ]
                
                insert_idx = 0
                for i, p in enumerate(phase_order):
                    if p == phase:
                        break
                    insert_idx += len(self._phases.get(p, []))
                
                self._middleware.insert(insert_idx, middleware)
            else:
                self._middleware.append(middleware)
            
            return MiddlewareId(value=mw_id)
    
    def remove(self, mw_id: str) -> bool:
        """Remove middleware by ID."""
        lock = self._get_lock()
        with lock:
            try:
                idx = next(
                    i for i, m in enumerate(self._middleware)
                    if str(id(m)) == mw_id or str(m).find(mw_id[:8]) != -1
                )
                del self._middleware[idx]
                return True
            except StopIteration:
                return False
    
    async def execute(
        self,
        message: Any,
        context: Optional[MiddlewareContext] = None,
    ) -> MiddlewareResult:
        """
        Execute all middleware in order.
        
        Args:
            message: Message to process
            context: Initial context (optional)
            
        Returns:
            Final result after all middleware
        """
        ctx = context or MiddlewareContext(message=message)
        
        # Build chained call
        async def make_next_call(idx: int):
            if idx >= len(self._middleware):
                return MiddlewareResult(
                    result_type=MiddlewareResultType.CONTINUE,
                    message=ctx.message,
                )
            
            middleware = self._middleware[idx]
            
            async def next_callable(c: MiddlewareContext) -> MiddlewareResult:
                return await make_next_call(idx + 1)
            
            return await middleware(ctx, next_callable)
        
        return await make_next_call(0)
    
    def get_middleware_count(self) -> int:
        """Get count of middleware in chain."""
        lock = self._get_lock()
        with lock:
            return len(self._middleware)


# =============================================================================
# PUBLIC API
# =============================================================================

__all__ = [
    # Phases and results
    "MiddlewarePhase",
    "MiddlewareResultType",
    
    # Identities
    "MiddlewareId",
    
    # Context
    "MiddlewareContext",
    
    # Protocol
    "Middleware",
    
    # Built-in middleware
    "ValidationMiddleware",
    "AuthorizationMiddleware",
    "TracingMiddleware",
    "DeadLetterMiddleware",
    "RateLimitMiddleware",
    "EnrichmentMiddleware",
    
    # Chain
    "MiddlewareChain",
]