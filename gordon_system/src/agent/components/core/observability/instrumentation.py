# Core Instrumentation Framework
# ===============================

"""
Instrumentation framework for Gordon Core observability.

This module provides:
- Lifecycle hooks for runtime events
- Execution hooks for code execution points
- Performance measurement hooks
- Resource usage hooks
- Extension points for custom instrumentation

Instrumentation is OBSERVATIONAL - it never changes runtime behavior.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Dict, List, Any, Optional, Callable, Awaitable
from enum import Enum, auto
import time
import uuid
import threading


# =============================================================================
# HOOK TYPES
# =============================================================================

class HookType(Enum):
    """Types of instrumentation hooks."""
    
    # Lifecycle hooks - entity lifecycle transitions
    LIFECYCLE_START = "lifecycle_start"
    LIFECYCLE_END = "lifecycle_end"
    LIFECYCLE_STATE_CHANGE = "lifecycle_state_change"
    
    # Execution hooks - code execution points
    EXECUTION_START = "execution_start"
    EXECUTION_END = "execution_end"
    EXECUTION_ERROR = "execution_error"
    
    # Resource hooks - resource usage tracking
    RESOURCE_ACQUIRE = "resource_acquire"
    RESOURCE_RELEASE = "resource_release"
    RESOURCE_USAGE = "resource_usage"
    
    # Performance hooks - timing and measurement
    PERF_MEASURE = "perf_measure"
    PERF_LATENCY = "perf_latency"
    PERF_THROUGHPUT = "perf_throughput"
    
    # API hooks - external API calls
    API_CALL_START = "api_call_start"
    API_CALL_END = "api_call_end"
    API_CALL_ERROR = "api_call_error"


@dataclass(frozen=True)
class HookDescriptor:
    """
    Descriptor for an instrumentation hook.
    
    Defines the contract and metadata for a hook type.
    """
    
    hook_type: HookType
    name: str  # Human-readable name
    description: str  # What this hook measures
    priority: int = 100  # Execution priority (lower = earlier)
    is_async: bool = False  # Whether the hook is async


# =============================================================================
# INSTRUMENTATION HOOKS
# =============================================================================

@dataclass(frozen=True)
class InstrumentationHook(ABC):
    """
    Base class for instrumentation hooks.
    
    Hooks are called at specific points during runtime execution to collect
    telemetry data without altering program semantics.
    """
    
    descriptor: HookDescriptor
    
    @abstractmethod
    def __call__(self, context: Dict[str, Any]) -> None:
        """
        Execute the hook with the given context.
        
        Args:
            context: Dictionary containing hook-specific data
        """
        ...
    
    @property
    def name(self) -> str:
        """Get hook name."""
        return self.descriptor.name
    
    @property
    def hook_type(self) -> HookType:
        """Get hook type."""
        return self.descriptor.hook_type


@dataclass(frozen=True)
class LifecycleHook(InstrumentationHook):
    """Hook for lifecycle event instrumentation."""
    
    def __call__(self, context: Dict[str, Any]) -> None:
        """
        Handle a lifecycle transition.
        
        Context keys:
            - entity_id: ID of the entity transitioning
            - from_state: Previous state
            - to_state: New state
            - timestamp_utc: When transition occurred
        """
        pass  # Subclasses implement specific behavior


@dataclass(frozen=True)
class ExecutionHook(InstrumentationHook):
    """Hook for code execution instrumentation."""
    
    def __call__(self, context: Dict[str, Any]) -> None:
        """
        Handle an execution event.
        
        Context keys:
            - function_name: Name of the executed function
            - duration_seconds: How long it took
            - return_value: What was returned (if successful)
            - error: Exception if failed
            - timestamp_utc: When execution occurred
        """
        pass  # Subclasses implement specific behavior


@dataclass(frozen=True)
class ResourceHook(InstrumentationHook):
    """Hook for resource usage instrumentation."""
    
    def __call__(self, context: Dict[str, Any]) -> None:
        """
        Handle a resource event.
        
        Context keys:
            - resource_type: Type of resource (cpu, memory, disk, etc.)
            - value: Amount used or acquired
            - unit: Unit of measurement
            - timestamp_utc: When measurement occurred
        """
        pass  # Subclasses implement specific behavior


@dataclass(frozen=True)
class PerfHook(InstrumentationHook):
    """Hook for performance measurement instrumentation."""
    
    def __call__(self, context: Dict[str, Any]) -> None:
        """
        Handle a performance measurement.
        
        Context keys:
            - operation_name: Name of the operation
            - duration_seconds: Time taken
            - timestamp_utc: When measurement occurred
            - labels: Additional metrics labels
        """
        pass  # Subclasses implement specific behavior


# =============================================================================
# HOOK REGISTRY
# =============================================================================

class HookRegistry:
    """
    Registry for instrumentation hooks.
    
    Manages hook registration, discovery, and execution.
    """
    
    def __init__(self) -> None:
        self._lock = threading.RLock()
        self._hooks: Dict[HookType, List[InstrumentationHook]] = {}
        self._hook_by_name: Dict[str, InstrumentationHook] = {}
    
    def register_hook(self, hook: InstrumentationHook) -> "HookRegistry":
        """
        Register an instrumentation hook.
        
        Args:
            hook: The hook to register
            
        Returns:
            Self for method chaining
        """
        with self._lock:
            if hook.hook_type not in self._hooks:
                self._hooks[hook.hook_type] = []
            
            # Insert in priority order (lower number = higher priority)
            hooks = self._hooks[hook.hook_type]
            insert_idx = 0
            while insert_idx < len(hooks) and hook.descriptor.priority > hooks[insert_idx].descriptor.priority:
                insert_idx += 1
            
            hooks.insert(insert_idx, hook)
            
            # Index by name for easy lookup
            self._hook_by_name[f"{hook.hook_type.value}:{hook.name}"] = hook
            
        return self
    
    def get_hooks(self, hook_type: HookType) -> List[InstrumentationHook]:
        """
        Get all hooks of a specific type.
        
        Args:
            hook_type: The hook type to retrieve
            
        Returns:
            List of hooks in priority order
        """
        with self._lock:
            return list(self._hooks.get(hook_type, []))
    
    def execute_hooks(
        self,
        hook_type: HookType,
        context: Dict[str, Any]
    ) -> None:
        """
        Execute all hooks of a given type.
        
        Args:
            hook_type: Type of hooks to execute
            context: Context data for the hooks
        """
        with self._lock:
            hooks = self._hooks.get(hook_type, [])
        
        for hook in hooks:
            try:
                hook(context)
            except Exception:
                # Don't let one hook failure affect others
                continue
    
    def get_hook(self, name: str) -> Optional[InstrumentationHook]:
        """Get a specific hook by name."""
        with self._lock:
            return self._hook_by_name.get(name)


# =============================================================================
# EXECUTION INSTRUMENTATION CONTEXT
# =============================================================================

class InstrumentationContext:
    """
    Context for instrumentation during execution.
    
    Provides correlation between different hooks during code execution.
    """
    
    def __init__(
        self,
        runtime_id: str,
        correlation_id: Optional[str] = None,
        trace_id: Optional[str] = None,
        span_id: Optional[str] = None,
    ) -> None:
        self.runtime_id = runtime_id
        self.correlation_id = correlation_id or str(uuid.uuid4())
        self.trace_id = trace_id or str(uuid.uuid4())
        self.span_id = span_id or str(uuid.uuid4())
        
        self._start_time = time.monotonic()
        self._timestamps: Dict[str, float] = {}
        self._metadata: Dict[str, Any] = {}
    
    def record_timestamp(self, label: str) -> "InstrumentationContext":
        """Record a timestamp with the given label."""
        self._timestamps[label] = time.monotonic() - self._start_time
        return self
    
    def get_duration_seconds(self, start_label: str, end_label: Optional[str] = None) -> float:
        """
        Get duration between two timestamps.
        
        Args:
            start_label: Start timestamp label
            end_label: End timestamp label (current if not provided)
            
        Returns:
            Duration in seconds
        """
        end_time = self._timestamps.get(end_label, time.monotonic() - self._start_time)
        return end_time - self._timestamps.get(start_label, 0.0)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert context to dictionary."""
        return {
            "runtime_id": self.runtime_id,
            "correlation_id": self.correlation_id,
            "trace_id": self.trace_id,
            "span_id": self.span_id,
            "timestamps": dict(self._timestamps),
            "metadata": dict(self._metadata),
        }


# =============================================================================
# INSTRUMENTATION MANAGER
# =============================================================================

class InstrumentationManager:
    """
    Manager for instrumentation hooks.
    
    Coordinates all instrumentation during runtime execution.
    """
    
    def __init__(
        self,
        runtime_id: Optional[str] = None,
    ) -> None:
        import uuid
        
        self._runtime_id = runtime_id or str(uuid.uuid4())
        self._registry = HookRegistry()
        
        # Statistics
        self._total_hooks_executed = 0
        self._hooks_by_type: Dict[HookType, int] = {}
    
    @property
    def runtime_id(self) -> str:
        """Get the runtime identifier."""
        return self._runtime_id
    
    def register_hook(self, hook: InstrumentationHook) -> "InstrumentationManager":
        """
        Register an instrumentation hook.
        
        Args:
            hook: The hook to register
            
        Returns:
            Self for method chaining
        """
        self._registry.register_hook(hook)
        return self
    
    def execute_hook(
        self,
        hook_type: HookType,
        context: Dict[str, Any]
    ) -> None:
        """
        Execute hooks of a specific type.
        
        Args:
            hook_type: Type of hooks to execute
            context: Context data for the hooks
        """
        with self._registry._lock:
            if hook_type not in self._hooks_by_type:
                self._hooks_by_type[hook_type] = 0
        
        self._registry.execute_hooks(hook_type, context)
        
        with self._registry._lock:
            self._total_hooks_executed += 1
            self._hooks_by_type[hook_type] += 1
    
    def instrument_execution(
        self,
        func: Optional[Callable[..., Any]] = None,
        operation_name: str = "anonymous",
    ) -> Callable[..., Any]:
        """
        Decorator to instrument a function with lifecycle hooks.
        
        Args:
            func: Function to decorate (if None, returns decorator)
            operation_name: Name of the operation for telemetry
            
        Returns:
            Wrapped function
        """
        def decorator(f: Callable[..., Any]) -> Callable[..., Any]:
            def wrapper(*args: Any, **kwargs: Any) -> Any:
                ctx = InstrumentationContext(
                    runtime_id=self._runtime_id,
                    trace_id=str(uuid.uuid4()),
                    span_id=str(uuid.uuid4()),
                )
                
                # Record start
                ctx.record_timestamp("start")
                self.execute_hook(HookType.EXECUTION_START, {
                    "function_name": operation_name,
                    "context": ctx.to_dict(),
                })
                
                try:
                    result = f(*args, **kwargs)
                    
                    # Record end
                    ctx.record_timestamp("end")
                    duration = ctx.get_duration_seconds("start", "end")
                    
                    self.execute_hook(HookType.EXECUTION_END, {
                        "function_name": operation_name,
                        "duration_seconds": duration,
                        "return_value": result,
                        "context": ctx.to_dict(),
                    })
                    
                    return result
                    
                except Exception as e:
                    # Record error
                    ctx.record_timestamp("error")
                    duration = ctx.get_duration_seconds("start", "error")
                    
                    self.execute_hook(HookType.EXECUTION_ERROR, {
                        "function_name": operation_name,
                        "duration_seconds": duration,
                        "error": str(e),
                        "context": ctx.to_dict(),
                    })
                    raise
            
            return wrapper
        
        if func is not None:
            return decorator(func)
        return decorator
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get instrumentation statistics."""
        with self._registry._lock:
            return {
                "runtime_id": self._runtime_id,
                "total_hooks_executed": self._total_hooks_executed,
                "hooks_by_type": {k.value: v for k, v in self._hooks_by_type.items()},
            }


# =============================================================================
# BUILT-IN HOOKS
# =============================================================================

class LoggingLifecycleHook(LifecycleHook):
    """Lifecycle hook that emits structured logs."""
    
    def __call__(self, context: Dict[str, Any]) -> None:
        """
        Emit a log for lifecycle transitions.
        
        Context:
            - entity_id: Entity being tracked
            - from_state: Previous state
            - to_state: New state
        """
        entity_id = context.get("entity_id", "unknown")
        from_state = context.get("from_state", "unknown")
        to_state = context.get("to_state", "unknown")
        
        # Would typically emit a log record here


class MetricsExecutionHook(ExecutionHook):
    """Execution hook that records metrics."""
    
    def __call__(self, context: Dict[str, Any]) -> None:
        """
        Record metrics for execution events.
        
        Context:
            - function_name: Function being executed
            - duration_seconds: Execution time
            - return_value: What was returned (if any)
        """
        func_name = context.get("function_name", "unknown")
        duration = context.get("duration_seconds", 0.0)
        
        # Would typically update metrics here


# =============================================================================
# ASYNC HOOK SUPPORT
# =============================================================================

@dataclass(frozen=True)
class AsyncInstrumentationHook:
    """Async variant of instrumentation hook."""
    
    hook: InstrumentationHook
    
    async def __call__(self, context: Dict[str, Any]) -> None:
        """
        Execute the hook asynchronously.
        
        Args:
            context: Context data for the hooks
        """
        self.hook(context)


__all__ = [
    # Hook types
    "HookType",
    
    # Descriptors and base classes
    "HookDescriptor",
    "InstrumentationHook",
    "LifecycleHook",
    "ExecutionHook",
    "ResourceHook",
    "PerfHook",
    
    # Registry and manager
    "HookRegistry",
    "InstrumentationContext",
    "InstrumentationManager",
    
    # Built-in hooks
    "LoggingLifecycleHook",
    "MetricsExecutionHook",
    
    # Async support
    "AsyncInstrumentationHook",
]