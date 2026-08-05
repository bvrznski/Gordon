# Core Correlation Manager
# ========================

"""
Runtime correlation state management for Gordon.

This module provides:
- CorrelationManager: Canonical authority for correlation ID management
- Correlation context propagation across subsystem boundaries
- Session and request tracking
- Trace-to-correlation mapping

Correlation is OBSERVATIONAL - it never changes runtime behavior.
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any
from enum import Enum, auto
import threading
import time
import uuid

from .models import (
    CorrelationContext,
    CorrelationSnapshot,
)


# =============================================================================
# CORRELATION CONTEXT PROVIDER
# =============================================================================

class CorrelationScope(Enum):
    """Scopes for correlation context."""
    
    GLOBAL = "global"          # All operations in this runtime
    SESSION = "session"        # User session scope
    REQUEST = "request"        # Single request/response cycle
    TASK = "task"              # Task execution scope
    SPAN = "span"              # Distributed trace span


@dataclass(frozen=True)
class CorrelationState:
    """
    Current correlation state for a specific scope.
    
    This is a snapshot of the correlation context at a point in time.
    It is immutable and can be safely shared across threads.
    """
    
    scope: CorrelationScope
    runtime_id: str
    
    correlation_id: Optional[str] = None   # Groups related operations
    causation_id: Optional[str] = None     # Identifies causing event
    session_id: Optional[str] = None       # User/session context
    request_id: Optional[str] = None       # External request identifier
    
    trace_id: Optional[str] = None         # Distributed trace ID
    span_id: Optional[str] = None          # Span within the trace
    
    timestamp_utc: float = field(default_factory=time.time)


# =============================================================================
# CORRELATION MANAGER
# =============================================================================

class CorrelationManager:
    """
    Canonical authority for correlation state management.
    
    Provides:
        - Runtime-scoped correlation context (one per runtime)
        - Context propagation across subsystem boundaries
        - Session tracking and request identification
        - Trace-to-correlation mapping
    
    INVAR: Exactly one CorrelationManager exists per runtime.
    INVAR: Correlation never changes runtime behavior.
    
    Usage:
        # Create manager (runtime-scoped)
        manager = CorrelationManager(runtime_id="runtime_123")
        
        # Start a new request context
        with manager.request_context(request_id="req_abc") as ctx:
            # All logs/metrics in this scope will have the same correlation ID
            logging.info("Processing request", request_id=ctx.correlation_id)
            
            # Create nested span context
            with manager.span_context(span_name="db_query") as span_ctx:
                logging.debug("Executing query", trace_id=span_ctx.trace_id)
        
        # Get current state snapshot for diagnostics
        snapshot = manager.get_snapshot()
    """
    
    def __init__(
        self,
        runtime_id: Optional[str] = None,
        initial_correlation_id: Optional[str] = None,
    ) -> None:
        import uuid
        
        self._runtime_id = runtime_id or str(uuid.uuid4())
        
        # Thread-local storage for nested contexts
        self._local = threading.local()
        
        # State management
        self._lock = threading.RLock()
        
        # Active correlation groups (correlation_id -> related_ids)
        self._correlation_groups: Dict[str, List[str]] = {}
        
        # Active traces (trace_id -> span_count)
        self._active_traces: Dict[str, int] = {}
        
        # Session tracking
        self._sessions: Dict[str, float] = {}  # session_id -> last_activity
        
        # Set initial context
        initial_ctx = CorrelationContext(
            runtime_id=self._runtime_id,
            correlation_id=initial_correlation_id or str(uuid.uuid4())
        )
        
        self._set_initial_context(initial_ctx)
    
    def _get_context(self) -> Optional[CorrelationContext]:
        """Get current thread-local context."""
        if not hasattr(self._local, "context_stack"):
            return None
        if not self._local.context_stack:
            return None
        return self._local.context_stack[-1]
    
    def _set_initial_context(self, ctx: CorrelationContext) -> None:
        """Set initial correlation context for thread."""
        if not hasattr(self._local, "context_stack"):
            self._local.context_stack = []
        self._local.context_stack.append(ctx)
        
        # Register in groups
        with self._lock:
            if ctx.correlation_id:
                if ctx.correlation_id not in self._correlation_groups:
                    self._correlation_groups[ctx.correlation_id] = []
                if ctx.runtime_id not in self._correlation_groups[ctx.correlation_id]:
                    self._correlation_groups[ctx.correlation_id].append(ctx.runtime_id)
    
    def get_current_context(self) -> CorrelationContext:
        """
        Get the current correlation context for this thread.
        
        If no context exists, creates a new one with a fresh correlation ID.
        
        Returns:
            Current CorrelationContext
        """
        ctx = self._get_context()
        if ctx is None:
            # Create new root context
            ctx = CorrelationContext(
                runtime_id=self._runtime_id,
                correlation_id=str(uuid.uuid4())
            )
            self._set_initial_context(ctx)
        
        return ctx
    
    def get_correlation_id(self) -> str:
        """Get current correlation ID."""
        ctx = self.get_current_context()
        if ctx.correlation_id:
            return ctx.correlation_id
        # Fallback to runtime ID
        return self._runtime_id
    
    @property
    def runtime_id(self) -> str:
        """Get the runtime identifier."""
        return self._runtime_id
    
    # ------------------------------------------------------------------
    # Context Managers (for nested scopes)
    # ------------------------------------------------------------------
    
    def request_context(
        self,
        request_id: Optional[str] = None,
        session_id: Optional[str] = None,
    ):
        """
        Create a context manager for request-scoped correlation.
        
        Usage:
            with manager.request_context(request_id="req_123"):
                # All operations in this scope share the same correlation
                pass
        
        Args:
            request_id: External request identifier (optional)
            session_id: User session ID (optional)
            
        Returns:
            Context manager for request context
        """
        return _RequestContext(self, request_id, session_id)
    
    def span_context(
        self,
        span_name: str,
        trace_id: Optional[str] = None,
        parent_span_id: Optional[str] = None,
    ):
        """
        Create a context manager for span-scoped correlation.
        
        Usage:
            with manager.span_context("database_query"):
                # Log with span context
                pass
        
        Args:
            span_name: Human-readable operation name
            trace_id: Parent trace ID (optional)
            parent_span_id: Parent span ID (optional)
            
        Returns:
            Context manager for span context
        """
        return _SpanContext(self, span_name, trace_id, parent_span_id)
    
    def session_context(
        self,
        session_id: str,
        correlation_id: Optional[str] = None,
    ):
        """
        Create a context manager for session-scoped correlation.
        
        Args:
            session_id: User/session identifier
            correlation_id: Correlation ID (optional, generates if not provided)
            
        Returns:
            Context manager for session context
        """
        return _SessionContext(self, session_id, correlation_id)
    
    def task_context(
        self,
        task_id: str,
        parent_task_id: Optional[str] = None,
        correlation_id: Optional[str] = None,
    ):
        """
        Create a context manager for task-scoped correlation.
        
        Args:
            task_id: Task identifier
            parent_task_id: Parent task ID (optional)
            correlation_id: Correlation ID (optional)
            
        Returns:
            Context manager for task context
        """
        return _TaskContext(self, task_id, parent_task_id, correlation_id)
    
    # ------------------------------------------------------------------
    # State Management
    # ------------------------------------------------------------------
    
    def get_snapshot(self) -> CorrelationSnapshot:
        """
        Get a snapshot of current correlation state.
        
        Returns:
            CorrelationSnapshot with all active correlations
        """
        with self._lock:
            return CorrelationSnapshot(
                runtime_id=self._runtime_id,
                timestamp_utc=time.time(),
                correlation_groups=dict(self._correlation_groups),
                active_traces=dict(self._active_traces),
                active_sessions=dict(self._sessions)
            )
    
    def get_active_correlations(self) -> List[str]:
        """Get all currently active correlation IDs."""
        with self._lock:
            return list(self._correlation_groups.keys())
    
    # ------------------------------------------------------------------
    # Context Propagation
    # ------------------------------------------------------------------
    
    def extract_context(self, ctx: CorrelationContext) -> Dict[str, str]:
        """
        Extract context for propagation to other subsystems.
        
        Usage:
            ctx = manager.get_current_context()
            props = manager.extract_context(ctx)
            
            # Pass to another component
            next_component.execute(props)
        
        Args:
            ctx: Context to extract
            
        Returns:
            Dictionary suitable for JSON serialization/propagation
        """
        return {
            "runtime_id": ctx.runtime_id,
            "correlation_id": ctx.correlation_id or "",
            "causation_id": ctx.causation_id or "",
            "session_id": ctx.session_id or "",
            "request_id": ctx.request_id or "",
            "trace_id": ctx.trace_id or "",
            "span_id": ctx.span_id or "",
        }
    
    def inject_context(self, props: Dict[str, str]) -> CorrelationContext:
        """
        Inject external context into this runtime's correlation state.
        
        Usage:
            props = received_from_remote()
            ctx = manager.inject_context(props)
            
            # Now logging uses the injected context
            logging.info("Received", correlation_id=ctx.correlation_id)
        
        Args:
            props: Context dictionary from propagation
            
        Returns:
            CorrelationContext with injected values
        """
        return CorrelationContext(
            runtime_id=self._runtime_id,
            correlation_id=props.get("correlation_id"),
            causation_id=props.get("causation_id"),
            session_id=props.get("session_id"),
            request_id=props.get("request_id"),
            trace_id=props.get("trace_id"),
            span_id=props.get("span_id"),
        )
    
    # ------------------------------------------------------------------
    # Statistics
    # ------------------------------------------------------------------
    
    @property
    def active_correlation_count(self) -> int:
        """Return count of active correlation groups."""
        with self._lock:
            return len(self._correlation_groups)
    
    @property
    def active_session_count(self) -> int:
        """Return count of active sessions."""
        with self._lock:
            return len(self._sessions)


# =============================================================================
# CONTEXT MANAGER IMPLEMENTATIONS
# =============================================================================

class _RequestContext:
    """Context manager for request-scoped correlation."""
    
    def __init__(
        self,
        manager: CorrelationManager,
        request_id: Optional[str] = None,
        session_id: Optional[str] = None,
    ) -> None:
        self._manager = manager
        self._request_id = request_id or str(uuid.uuid4())
        self._session_id = session_id
    
    def __enter__(self) -> CorrelationContext:
        ctx = self._manager.get_current_context()
        
        new_ctx = CorrelationContext(
            runtime_id=ctx.runtime_id,
            correlation_id=ctx.correlation_id,
            request_id=self._request_id,
            session_id=self._session_id or ctx.session_id,
        )
        
        if not hasattr(self._manager._local, "context_stack"):
            self._manager._local.context_stack = []
        self._manager._local.context_stack.append(new_ctx)
        
        return new_ctx
    
    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        # Pop the context
        if hasattr(self._manager._local, "context_stack"):
            if len(self._manager._local.context_stack) > 1:
                self._manager._local.context_stack.pop()
            else:
                # Keep root context but restore it
                pass


class _SpanContext:
    """Context manager for span-scoped correlation."""
    
    def __init__(
        self,
        manager: CorrelationManager,
        span_name: str,
        trace_id: Optional[str] = None,
        parent_span_id: Optional[str] = None,
    ) -> None:
        self._manager = manager
        self._span_name = span_name
        self._trace_id = trace_id or str(uuid.uuid4())
        self._parent_span_id = parent_span_id
    
    def __enter__(self) -> CorrelationContext:
        ctx = self._manager.get_current_context()
        
        new_ctx = CorrelationContext(
            runtime_id=ctx.runtime_id,
            correlation_id=ctx.correlation_id,
            trace_id=self._trace_id,
            span_id=str(uuid.uuid4()),
            parent_span_id=self._parent_span_id or ctx.span_id,
        )
        
        # Register in active traces
        with self._manager._lock:
            if self._trace_id not in self._manager._active_traces:
                self._manager._active_traces[self._trace_id] = 0
            self._manager._active_traces[self._trace_id] += 1
        
        if not hasattr(self._manager._local, "context_stack"):
            self._manager._local.context_stack = []
        self._manager._local.context_stack.append(new_ctx)
        
        return new_ctx
    
    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        # Pop the context
        if hasattr(self._manager._local, "context_stack"):
            if len(self._manager._local.context_stack) > 1:
                self._manager._local.context_stack.pop()
        
        # Decrement trace span count
        with self._manager._lock:
            if self._trace_id in self._manager._active_traces:
                self._manager._active_traces[self._trace_id] -= 1


class _SessionContext:
    """Context manager for session-scoped correlation."""
    
    def __init__(
        self,
        manager: CorrelationManager,
        session_id: str,
        correlation_id: Optional[str] = None,
    ) -> None:
        self._manager = manager
        self._session_id = session_id
        self._correlation_id = correlation_id
    
    def __enter__(self) -> CorrelationContext:
        ctx = self._manager.get_current_context()
        
        new_ctx = CorrelationContext(
            runtime_id=ctx.runtime_id,
            correlation_id=self._correlation_id or ctx.correlation_id,
            session_id=self._session_id,
        )
        
        # Track session activity
        with self._manager._lock:
            self._manager._sessions[self._session_id] = time.time()
        
        if not hasattr(self._manager._local, "context_stack"):
            self._manager._local.context_stack = []
        self._manager._local.context_stack.append(new_ctx)
        
        return new_ctx
    
    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        # Pop the context
        if hasattr(self._manager._local, "context_stack"):
            if len(self._manager._local.context_stack) > 1:
                self._manager._local.context_stack.pop()


class _TaskContext:
    """Context manager for task-scoped correlation."""
    
    def __init__(
        self,
        manager: CorrelationManager,
        task_id: str,
        parent_task_id: Optional[str] = None,
        correlation_id: Optional[str] = None,
    ) -> None:
        self._manager = manager
        self._task_id = task_id
        self._parent_task_id = parent_task_id
        self._correlation_id = correlation_id
    
    def __enter__(self) -> CorrelationContext:
        ctx = self._manager.get_current_context()
        
        new_ctx = CorrelationContext(
            runtime_id=ctx.runtime_id,
            correlation_id=self._correlation_id or ctx.correlation_id,
            task_id=self._task_id,
            parent_task_id=self._parent_task_id,
        )
        
        if not hasattr(self._manager._local, "context_stack"):
            self._manager._local.context_stack = []
        self._manager._local.context_stack.append(new_ctx)
        
        return new_ctx
    
    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        # Pop the context
        if hasattr(self._manager._local, "context_stack"):
            if len(self._manager._local.context_stack) > 1:
                self._manager._local.context_stack.pop()


__all__ = [
    "CorrelationScope",
    "CorrelationState",
    "CorrelationManager",
]