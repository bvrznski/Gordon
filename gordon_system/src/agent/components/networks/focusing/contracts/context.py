# Focusing Network Context Contracts
# ====================================

"""
Context contracts for the FocusingNetwork Phase 4.2.8.

These define the computational context through which projections are carried
without ownership. Context carries information about execution, policy,
resources, and history without modifying any state.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Tuple, Dict, Any, Optional
from datetime import datetime


# =============================================================================
# EXECUTION PROJECTION - Information about current execution context
# =============================================================================

@dataclass(frozen=True)
class ExecutionProjection:
    """
    Projection of current execution state without ownership.
    
    Contains information about the ongoing computational process that may
    influence focus allocation decisions. Never owns or modifies state.
    
    PROPERTIES:
        • Immutable once created
        • No side effects when read
        • Versioned for compatibility tracking
    """
    
    # Execution identity
    execution_id: str = field(default_factory=lambda: f"exec_{id(datetime.utcnow()):x}")
    """Unique identifier for this execution context."""
    
    # Process state
    is_active: bool = True
    """Whether the current process is active."""
    
    active_thread_count: int = 1
    """Number of threads currently running in this context."""
    
    # Timing information
    start_timestamp_utc: datetime = field(default_factory=datetime.utcnow)
    """When execution began."""
    
    last_update_utc: datetime = field(default_factory=datetime.utcnow)
    """Last time this projection was updated."""
    
    # Priority hints (from outside the FocusingNetwork)
    active_priority_level: str = "medium"
    """Current priority level of the executing process."""
    
    deadline_seconds: Optional[float] = None
    """Optional deadline for completion in seconds."""
    
    # Resource context
    available_threads: int = 4
    """Number of threads available for allocation."""
    
    estimated_completion_seconds: Optional[float] = None
    """Estimated remaining duration if known."""
    
    @classmethod
    def active_context(cls) -> "ExecutionProjection":
        """Create a projection representing currently active execution."""
        return cls(is_active=True)
    
    def with_deadline(self, seconds: float) -> "ExecutionProjection":
        """Create a copy with deadline set."""
        return dataclass_replace(self, deadline_seconds=seconds)
    
    def mark_inactive(self) -> "ExecutionProjection":
        """Create a copy marking execution as inactive."""
        return dataclass_replace(self, is_active=False)


def dataclass_replace(obj: Any, **kwargs) -> Any:
    """
    Replace fields in a frozen dataclass instance.
    
    Creates a new copy with specified fields updated while maintaining
    immutability guarantees.
    """
    if hasattr(obj, "__dataclass_fields__"):
        field_dict = {
            f.name: getattr(obj, f.name)
            for f in obj.__dataclass_fields__.values()
        }
        field_dict.update(kwargs)
        return type(obj)(**field_dict)
    raise TypeError(f"Object {obj} is not a dataclass")


# =============================================================================
# POLICY PROJECTION - Information about active policies
# =============================================================================

@dataclass(frozen=True)
class PolicyProjection:
    """
    Projection of active policy constraints without ownership.
    
    Contains information about policies that should influence focus allocation.
    Policies define constraints and guidelines that the FocusingNetwork must
    respect but does not enforce.
    
    PROPERTIES:
        • Immutable once created
        • No enforcement responsibility (that's for higher layers)
        • Versioned for compatibility tracking
    """
    
    # Policy identity
    policy_id: str = field(default_factory=lambda: f"policy_{id(datetime.utcnow()):x}")
    """Unique identifier for this policy projection."""
    
    # Policy metadata
    policy_name: str = "default"
    """Name of the active policy set."""
    
    policy_version: str = "1.0.0"
    """Version of the active policy set."""
    
    # Priority constraints
    max_concurrent_focus_targets: int = 3
    """Maximum concurrent focus targets allowed by policy."""
    
    priority_threshold: float = 0.5
    """Minimum priority required for focus allocation."""
    
    # Duration policies
    default_duration_seconds: float = 60.0
    """Default duration for focus allocation."""
    
    max_focus_streak_minutes: float = 30.0
    """Maximum continuous focus time before forced break."""
    
    # Resource constraints
    budget_limit: float = 1.0
    """Maximum resource budget percentage (0.0 to 1.0)."""
    
    min_resource_allocation: float = 0.05
    """Minimum guaranteed allocation per target."""
    
    # Special policies
    allow_priority_override: bool = False
    """Whether priority can be overridden by executive decision."""
    
    allow_precision_adaptation: bool = True
    """Whether precision can adapt based on context."""
    
    def with_max_targets(self, count: int) -> "PolicyProjection":
        """Create a copy with different max targets."""
        return dataclass_replace(self, max_concurrent_focus_targets=count)


# =============================================================================
# RESOURCE PROJECTION - Information about resource availability
# =============================================================================

@dataclass(frozen=True)
class ResourceProjection:
    """
    Projection of available computational resources without ownership.
    
    Contains information about system resources that may affect focus allocation.
    The FocusingNetwork reads this but never owns or modifies the actual resources.
    
    PROPERTIES:
        • Immutable once created
        • Snapshot at a point in time
        • Versioned for compatibility tracking
    """
    
    # Resource identity
    projection_id: str = field(default_factory=lambda: f"resource_{id(datetime.utcnow()):x}")
    """Unique identifier for this resource projection."""
    
    # CPU resources
    cpu_available_percent: float = 100.0
    """Available CPU capacity as percentage (0.0 to 100.0)."""
    
    cpu_used_percent: float = 0.0
    """Currently used CPU capacity as percentage."""
    
    # Memory resources
    memory_available_mb: int = 8192
    """Available memory in MB."""
    
    memory_total_mb: int = 16384
    """Total available memory in MB."""
    
    # Storage (for persistence-related focus)
    storage_free_gb: float = 100.0
    """Free storage space in GB."""
    
    storage_used_gb: float = 50.0
    """Used storage space in GB."""
    
    # Network resources
    network_latency_ms: Optional[float] = None
    """Current network latency in milliseconds, if known."""
    
    # Thread resources
    available_threads: int = 4
    """Number of threads available for allocation."""
    
    max_concurrent_operations: int = 10
    """Maximum concurrent operations supported."""
    
    def get_memory_utilization(self) -> float:
        """Return memory utilization as ratio (0.0 to 1.0)."""
        if self.memory_total_mb == 0:
            return 0.0
        return self.memory_used_mb / self.memory_total_mb
    
    @property
    def memory_used_mb(self) -> int:
        """Calculate used memory from available and total."""
        return self.memory_total_mb - self.memory_available_mb


# =============================================================================
# HISTORICAL PROJECTION - Information about past states
# =============================================================================

@dataclass(frozen=True)
class HistoricalProjection:
    """
    Projection of historical state without ownership.
    
    Contains information about past focus allocations and their outcomes that may
    influence current decisions. History is read-only for the FocusingNetwork.
    
    PROPERTIES:
        • Immutable once created
        • Bounded capacity (never unbounded growth)
        • Versioned for compatibility tracking
    """
    
    # History identity
    projection_id: str = field(default_factory=lambda: f"history_{id(datetime.utcnow()):x}")
    """Unique identifier for this historical projection."""
    
    # Historical data (read-only snapshots)
    recent_allocations: Tuple[Dict[str, Any], ...] = field(default_factory=tuple)
    """Recent focus allocations in chronological order."""
    
    allocation_history_count: int = 0
    """Total number of allocations in history."""
    
    last_focus_shift_utc: Optional[datetime] = None
    """When the last focus shift occurred."""
    
    # Success metrics (from external tracking)
    average_allocation_success_rate: float = 1.0
    """Historical success rate of allocations (0.0 to 1.0)."""
    
    typical_focus_duration_seconds: Optional[float] = None
    """Average duration of typical focus periods."""
    
    # State transitions
    recent_transitions: Tuple[Dict[str, Any], ...] = field(default_factory=tuple)
    """Recent state transitions for context."""
    
    def get_recent_allocations(self, count: int) -> Tuple[Dict[str, Any], ...]:
        """
        Get the most recent allocations up to count.
        
        Args:
            count: Maximum number of allocations to return
            
        Returns:
            Tuple of allocation dictionaries (newest first)
        """
        if not self.recent_allocations:
            return tuple()
        return self.recent_allocations[-min(count, len(self.recent_allocations)):]
    
    def get_allocation_count_in_window(self, seconds: float) -> int:
        """
        Count allocations within a time window.
        
        Args:
            seconds: Time window in seconds
            
        Returns:
            Number of allocations in the window
        """
        if not self.recent_allocations or seconds <= 0:
            return 0
        
        cutoff = datetime.utcnow().timestamp() - seconds
        count = 0
        for allocation in reversed(self.recent_allocations):
            timestamp = allocation.get("allocation_time_utc")
            if isinstance(timestamp, str):
                try:
                    alloc_ts = datetime.fromisoformat(timestamp).timestamp()
                    if alloc_ts >= cutoff:
                        count += 1
                    else:
                        break
                except ValueError:
                    continue
        return count


# =============================================================================
# FOCUS COMPUTATION CONTEXT - Complete context for computation
# =============================================================================

@dataclass(frozen=True)
class FocusComputationContext:
    """
    Complete context for focus computation without ownership.
    
    Combines all projections (execution, policy, resources, history) into a single
    immutable context that can be passed to the FocusingNetwork. The Network reads
    from this context but never owns or modifies it.
    
    PROPERTIES:
        • Immutable once created
        • Carries projections only - no ownership
        • Versioned for compatibility tracking
        • Complete snapshot of relevant external state
    """
    
    # Context identity
    context_id: str = field(default_factory=lambda: f"context_{id(datetime.utcnow()):x}")
    """Unique identifier for this computation context."""
    
    # Timestamps
    created_at_utc: datetime = field(default_factory=datetime.utcnow)
    """When this context was created."""
    
    revision: int = 1
    """Context revision number (for tracking updates)."""
    
    # Projections (all read-only)
    execution: ExecutionProjection = field(default_factory=ExecutionProjection.active_context)
    """Current execution state projection."""
    
    policy: PolicyProjection = field(default_factory=PolicyProjection)
    """Active policy constraints projection."""
    
    resources: ResourceProjection = field(default_factory=ResourceProjection)
    """Available resources projection."""
    
    history: HistoricalProjection = field(default_factory=HistoricalProjection)
    """Historical state projection."""
    
    # Additional context
    active_focus_targets: Tuple[str, ...] = field(default_factory=tuple)
    """IDs of currently focused targets (from outside)."""
    
    pending_assessment_id: Optional[str] = None
    """ID of an assessment that is in progress (if any)."""
    
    external_context_data: Dict[str, Any] = field(default_factory=dict)
    """Any additional context data from external systems."""
    
    @classmethod
    def create(cls) -> "FocusComputationContext":
        """
        Create a new computation context with default values.
        
        Returns:
            New FocusComputationContext instance
        """
        return cls()
    
    def with_execution(self, execution: ExecutionProjection) -> "FocusComputationContext":
        """Create a copy with different execution projection."""
        return dataclass_replace(self, execution=execution)
    
    def with_policy(self, policy: PolicyProjection) -> "FocusComputationContext":
        """Create a copy with different policy projection."""
        return dataclass_replace(self, policy=policy)
    
    def with_resources(self, resources: ResourceProjection) -> "FocusComputationContext":
        """Create a copy with different resources projection."""
        return dataclass_replace(self, resources=resources)
    
    def with_history(self, history: HistoricalProjection) -> "FocusComputationContext":
        """Create a copy with different history projection."""
        return dataclass_replace(self, history=history)
    
    def to_serializable(self) -> Dict[str, Any]:
        """
        Convert context to serializable dictionary.
        
        Returns:
            Dictionary representation suitable for storage or transmission
        """
        return {
            "context_id": self.context_id,
            "created_at_utc": self.created_at_utc.isoformat() if hasattr(self.created_at_utc, 'isoformat') else str(self.created_at_utc),
            "revision": self.revision,
            "execution": {
                "is_active": self.execution.is_active,
                "active_thread_count": self.execution.active_thread_count,
            },
            "policy": {
                "max_concurrent_focus_targets": self.policy.max_concurrent_focus_targets,
                "default_duration_seconds": self.policy.default_duration_seconds,
            },
            "resources": {
                "available_threads": self.resources.available_threads,
                "cpu_available_percent": self.resources.cpu_available_percent,
            },
            "history_count": len(self.history.recent_allocations),
        }


# =============================================================================
# EXTERNAL INTERFACE - Runtime_checkable protocols for type checking
# =============================================================================

try:
    from typing import Protocol, runtime_checkable
except ImportError:
    # Python < 3.8 fallback
    from typing_extensions import Protocol, runtime_checkable


@runtime_checkable
class FocusComputationContextProvider(Protocol):
    """
    Protocol for providing computation context to the FocusingNetwork.
    
    This protocol allows external systems to supply context without coupling
    to the FocusingNetwork implementation.
    
    VERSION: 1.0.0
    COMPATIBILITY: backward
    DEPRECATION: three_releases policy
    EXTENSION: additive_only (new projection types via enum)
    """
    
    @property
    def version(self) -> str:
        """Return the contract version string."""
        ...
    
    @property
    def compatibility_policy(self) -> str:
        """Return the compatibility policy string."""
        ...
    
    @abstractmethod
    def get_context_snapshot(
        self,
    ) -> FocusComputationContext:
        """
        Get a complete context snapshot for computation.
        
        Returns:
            Complete FocusComputationContext with all projections
        """
        ...
    
    @abstractmethod
    def get_execution_projection(self) -> ExecutionProjection:
        """Get current execution projection."""
        ...
    
    @abstractmethod
    def get_policy_projection(self) -> PolicyProjection:
        """Get current policy projection."""
        ...
    
    @abstractmethod
    def get_resource_projection(self) -> ResourceProjection:
        """Get current resource projection."""
        ...
    
    @abstractmethod
    def get_historical_projection(self) -> HistoricalProjection:
        """Get current historical projection."""
        ...


__all__ = [
    # Projections (no ownership)
    "ExecutionProjection",
    "PolicyProjection",
    "ResourceProjection",
    "HistoricalProjection",
    # Complete context
    "FocusComputationContext",
    # Protocol for external systems
    "FocusComputationContextProvider",
]