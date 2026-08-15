# Focusing Network State Contracts
# ==================================

"""
State contracts for the FocusingNetwork Phase 4.2.8.

These define immutable state views that external systems can observe.
The FocusingNetwork owns state internally, but exposes read-only views
through these contracts.

NO MUTATION: These are purely observational interfaces.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Tuple, Dict, Any, Optional
from datetime import datetime


# =============================================================================
# FOCUS STATE VIEW - Read-only view of focus state
# =============================================================================

@dataclass(frozen=True)
class FocusStateView:
    """
    Immutable view of focus state for observation only.
    
    Contains all information about currently maintained focus targets and their
    metadata. Never mutates internal state - only exposes it.
    
    PROPERTIES:
        • Read-only - no mutation allowed
        • Versioned for compatibility tracking
        • Complete snapshot at a point in time
    """
    
    # Focus identity
    view_id: str = field(default_factory=lambda: f"focus_view_{id(datetime.utcnow()):x}")
    """Unique identifier for this state view."""
    
    # Currently maintained targets (IDs only - no ownership)
    current_focus_target_ids: Tuple[str, ...] = field(default_factory=tuple)
    """IDs of currently focused targets."""
    
    dominant_target_id: Optional[str] = None
    """ID of the currently dominant focus target."""
    
    # Focus metadata
    focus_age_seconds: float = 0.0
    """How long current focus has been maintained."""
    
    last_focus_shift_utc: Optional[datetime] = None
    """When the last focus shift occurred."""
    
    continuity_count: int = 0
    """Number of continuous focus periods."""
    
    # Target metadata (external ownership)
    target_metadata: Dict[str, Dict[str, Any]] = field(default_factory=dict)
    """Metadata for each focus target (keyed by target ID)."""
    
    def get_target_priority(self, target_id: str) -> Optional[float]:
        """
        Get priority for a target from its metadata.
        
        Args:
            target_id: Target identifier
            
        Returns:
            Priority value (0.0 to 1.0) or None if not tracked
        """
        meta = self.target_metadata.get(target_id, {})
        return meta.get("priority")
    
    def get_target_category(self, target_id: str) -> Optional[str]:
        """
        Get semantic category for a target from its metadata.
        
        Args:
            target_id: Target identifier
            
        Returns:
            Category string or None if not tracked
        """
        meta = self.target_metadata.get(target_id, {})
        return meta.get("semantic_category")


# =============================================================================
# PRIORITY STATE VIEW - Read-only view of priority state
# =============================================================================

@dataclass(frozen=True)
class PriorityStateView:
    """
    Immutable view of priority state for observation only.
    
    Contains information about priority assessments without exposing how they
    were computed. Only the results, not the computation.
    
    PROPERTIES:
        • Read-only - no mutation allowed
        • Versioned for compatibility tracking
        • Complete snapshot at a point in time
    """
    
    # Priority view identity
    view_id: str = field(default_factory=lambda: f"priority_view_{id(datetime.utcnow()):x}")
    """Unique identifier for this state view."""
    
    # Priority assessments (results only - no algorithms)
    target_priorities: Dict[str, float] = field(default_factory=dict)
    """Priority values for each target ID (0.0 to 1.0)."""
    
    highest_priority_target_id: Optional[str] = None
    """ID of the target with highest priority."""
    
    # Priority metadata
    assessment_timestamp_utc: Optional[datetime] = None
    """When priorities were last assessed."""
    
    confidence_level: float = 1.0
    """Confidence in the priority assessments (0.0 to 1.0)."""
    
    assessment_count: int = 0
    """Number of targets with priority assessments."""
    
    def get_priority(self, target_id: str) -> Optional[float]:
        """
        Get priority for a specific target.
        
        Args:
            target_id: Target identifier
            
        Returns:
            Priority value (0.0 to 1.0) or None if not tracked
        """
        return self.target_priorities.get(target_id)


# =============================================================================
# PERSISTENCE STATE VIEW - Read-only view of persistence state
# =============================================================================

@dataclass(frozen=True)
class PersistenceStateView:
    """
    Immutable view of persistence state for observation only.
    
    Contains information about focus maintenance without exposing the
    persistence algorithms.
    
    PROPERTIES:
        • Read-only - no mutation allowed
        • Versioned for compatibility tracking
        • Complete snapshot at a point in time
    """
    
    # Persistence view identity
    view_id: str = field(default_factory=lambda: f"persistence_view_{id(datetime.utcnow()):x}")
    """Unique identifier for this state view."""
    
    # Maintenance info (results only)
    maintained_targets: Tuple[str, ...] = field(default_factory=tuple)
    """IDs of targets currently being maintained."""
    
    total_maintenance_seconds: float = 0.0
    """Total time spent maintaining focus across all targets."""
    
    last_focus_lifetime_seconds: float = 0.0
    """Duration of the last focus period."""
    
    # Persistence metadata
    decay_rate: Optional[float] = None
    """Current decay rate for unfocused targets."""
    
    stability_score: Optional[float] = None
    """Overall stability of current focus (0.0 to 1.0)."""
    
    continuity_count: int = 0
    """Number of continuous focus periods."""
    
    def is_maintained(self, target_id: str) -> bool:
        """
        Check if a target is currently being maintained.
        
        Args:
            target_id: Target identifier
            
        Returns:
            True if the target is in maintained_targets
        """
        return target_id in self.maintained_targets


# =============================================================================
# PRECISION STATE VIEW - Read-only view of precision state
# =============================================================================

@dataclass(frozen=True)
class PrecisionStateView:
    """
    Immutable view of precision state for observation only.
    
    Contains information about focus precision without exposing estimation
    algorithms.
    
    PROPERTIES:
        • Read-only - no mutation allowed
        • Versioned for compatibility tracking
        • Complete snapshot at a point in time
    """
    
    # Precision view identity
    view_id: str = field(default_factory=lambda: f"precision_view_{id(datetime.utcnow()):x}")
    """Unique identifier for this state view."""
    
    # Precision assessments (results only)
    target_precisions: Dict[str, float] = field(default_factory=dict)
    """Precision values for each target ID (0.0 to 1.0)."""
    
    default_precision: float = 0.5
    """Default precision when not otherwise specified."""
    
    # Precision metadata
    estimation_timestamp_utc: Optional[datetime] = None
    """When precisions were last estimated."""
    
    average_confidence: float = 1.0
    """Average confidence in precision estimates (0.0 to 1.0)."""
    
    bandwidth_allocation: Dict[str, str] = field(default_factory=dict)
    """Bandwidth allocation for each target (e.g., 'coarse', 'moderate', 'fine')."""
    
    def get_precision(self, target_id: str) -> Optional[float]:
        """
        Get precision for a specific target.
        
        Args:
            target_id: Target identifier
            
        Returns:
            Precision value (0.0 to 1.0) or None if not tracked
        """
        return self.target_precisions.get(target_id)
    
    def get_bandwidth(self, target_id: str) -> Optional[str]:
        """
        Get bandwidth allocation for a specific target.
        
        Args:
            target_id: Target identifier
            
        Returns:
            Bandwidth string or None if not allocated
        """
        return self.bandwidth_allocation.get(target_id)


# =============================================================================
# ALLOCATION STATE VIEW - Read-only view of allocation state
# =============================================================================

@dataclass(frozen=True)
class AllocationStateView:
    """
    Immutable view of allocation state for observation only.
    
    Contains information about resource allocations without exposing the
    allocation algorithms.
    
    PROPERTIES:
        • Read-only - no mutation allowed
        • Versioned for compatibility tracking
        • Complete snapshot at a point in time
    """
    
    # Allocation view identity
    view_id: str = field(default_factory=lambda: f"allocation_view_{id(datetime.utcnow()):x}")
    """Unique identifier for this state view."""
    
    # Allocation results (no algorithms)
    target_allocations: Dict[str, float] = field(default_factory=dict)
    """Resource allocation values for each target ID (0.0 to 1.0)."""
    
    total_allocated_budget: float = 0.0
    """Total budget currently allocated across all targets."""
    
    reserved_budget: float = 0.1
    """Budget reserved for dynamic allocation."""
    
    # Allocation metadata
    allocation_timestamp_utc: Optional[datetime] = None
    """When allocations were last computed."""
    
    max_targets_allocated: int = 3
    """Maximum number of simultaneously allocated targets."""
    
    def get_allocation(self, target_id: str) -> Optional[float]:
        """
        Get resource allocation for a specific target.
        
        Args:
            target_id: Target identifier
            
        Returns:
            Allocation value (0.0 to 1.0) or None if not tracked
        """
        return self.target_allocations.get(target_id)
    
    def get_allocation_count(self) -> int:
        """Return the number of targets with allocations."""
        return len(self.target_allocations)


# =============================================================================
# BIAS STATE VIEW - Read-only view of bias state
# =============================================================================

@dataclass(frozen=True)
class BiasStateView:
    """
    Immutable view of bias state for observation only.
    
    Contains information about top-down biases without exposing the
    bias generation algorithms.
    
    PROPERTIES:
        • Read-only - no mutation allowed
        • Versioned for compatibility tracking
        • Complete snapshot at a point in time
    """
    
    # Bias view identity
    view_id: str = field(default_factory=lambda: f"bias_view_{id(datetime.utcnow()):x}")
    """Unique identifier for this state view."""
    
    # Bias assessments (results only)
    target_biases: Dict[str, Dict[str, float]] = field(default_factory=dict)
    """
    Bias values per target.
    Structure: {target_id: {"goal": 0.5, "task": 0.3, ...}}
    """
    
    active_bias_modalities: Tuple[str, ...] = field(default_factory=tuple)
    """Modalities currently contributing to bias (e.g., 'goal', 'task', 'memory')."""
    
    # Bias metadata
    assessment_timestamp_utc: Optional[datetime] = None
    """When biases were last assessed."""
    
    average_bias_strength: float = 0.0
    """Average strength of active biases across all targets (0.0 to 1.0)."""
    
    max_active_biases_per_target: int = 4
    """Maximum number of concurrent bias modalities per target."""
    
    def get_target_bias(self, target_id: str, modality: str) -> Optional[float]:
        """
        Get specific bias for a target and modality.
        
        Args:
            target_id: Target identifier
            modality: Bias modality (e.g., 'goal', 'task', 'memory')
            
        Returns:
            Bias value (0.0 to 1.0) or None if not tracked
        """
        target_bias = self.target_biases.get(target_id, {})
        return target_bias.get(modality)
    
    def get_total_bias(self, target_id: str) -> Optional[float]:
        """
        Get total bias (sum of all modalities) for a target.
        
        Args:
            target_id: Target identifier
            
        Returns:
            Sum of all modality biases or None if not tracked
        """
        target_bias = self.target_biases.get(target_id, {})
        return sum(target_bias.values()) if target_bias else None


# =============================================================================
# DIAGNOSTICS VIEW - Read-only view of diagnostics state
# =============================================================================

@dataclass(frozen=True)
class DiagnosticsView:
    """
    Immutable view of diagnostics state for observation only.
    
    Contains diagnostic and telemetry information without exposing how it's
    collected or stored.
    
    PROPERTIES:
        • Read-only - no mutation allowed
        • Versioned for compatibility tracking
        • Complete snapshot at a point in time
    """
    
    # Diagnostics view identity
    view_id: str = field(default_factory=lambda: f"diagnostics_view_{id(datetime.utcnow()):x}")
    """Unique identifier for this state view."""
    
    # Diagnostic counts (no collection logic)
    total_assessments: int = 0
    """Total number of assessments performed."""
    
    total_transitions: int = 0
    """Total number of focus transitions."""
    
    focus_shifts: int = 0
    """Number of times focus shifted to a new target."""
    
    # Timing information (results only)
    last_assessment_utc: Optional[datetime] = None
    """When the last assessment was performed."""
    
    average_assessment_duration_ms: float = 0.0
    """Average duration of assessments in milliseconds."""
    
    # State summary
    active_target_count: int = 0
    """Number of currently focused targets."""
    
    suppressed_target_count: int = 0
    """Number of currently suppressed targets."""
    
    # Diagnostic metadata
    evaluation_window_seconds: float = 60.0
    """Time window for recent diagnostic data."""
    
    def get_assessment_rate(self) -> float:
        """
        Get assessment rate per second.
        
        Returns:
            Assessments per second (may be 0.0)
        """
        if self.average_assessment_duration_ms <= 0:
            return 0.0
        return 1000.0 / self.average_assessment_duration_ms


# =============================================================================
# EXTERNAL INTERFACES - Protocol definitions for external systems
# =============================================================================

try:
    from typing import Protocol, runtime_checkable
except ImportError:
    from typing_extensions import Protocol, runtime_checkable


@runtime_checkable
class FocusStateViewProvider(Protocol):
    """
    Protocol for providing focus state views.
    
    Allows external systems to observe focus state without coupling to
    FocusingNetwork implementation.
    """
    
    @property
    def version(self) -> str:
        """Return the contract version string."""
        ...
    
    @abstractmethod
    def get_focus_state_view(self) -> FocusStateView:
        """Get current focus state view."""
        ...
    
    @abstractmethod
    def get_priority_state_view(self) -> PriorityStateView:
        """Get current priority state view."""
        ...
    
    @abstractmethod
    def get_persistence_state_view(self) -> PersistenceStateView:
        """Get current persistence state view."""
        ...
    
    @abstractmethod
    def get_precision_state_view(self) -> PrecisionStateView:
        """Get current precision state view."""
        ...
    
    @abstractmethod
    def get_allocation_state_view(self) -> AllocationStateView:
        """Get current allocation state view."""
        ...
    
    @abstractmethod
    def get_bias_state_view(self) -> BiasStateView:
        """Get current bias state view."""
        ...
    
    @abstractmethod
    def get_diagnostics_view(self) -> DiagnosticsView:
        """Get current diagnostics view."""
        ...


__all__ = [
    # State views (immutable, read-only)
    "FocusStateView",
    "PriorityStateView",
    "PersistenceStateView",
    "PrecisionStateView",
    "AllocationStateView",
    "BiasStateView",
    "DiagnosticsView",
    # External provider interface
    "FocusStateViewProvider",
]