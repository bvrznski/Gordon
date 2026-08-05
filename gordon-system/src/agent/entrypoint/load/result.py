"""Gordon Agent Load Result Models.

Phase 3.7.30: Agent Initialization Chain
========================================

Immutable models for component loading results.
"""

from __future__ import annotations

import uuid
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum, auto
from typing import (
    Any,
    Dict,
    List,
    Optional,
    Tuple,
)


# =============================================================================
# COMPONENT LOAD STATUS (per-component result)
# =============================================================================


@dataclass(frozen=True)
class AgentComponentLoadStatus:
    """Immutable status record for a single component load.
    
    Each component in the plan produces one of these records indicating
    whether it was loaded successfully, skipped, or failed.
    """
    
    component_name: str
    """Name of the component."""
    
    load_status: str
    """Status string: 'loaded', 'skipped', 'failed'."""
    
    error_message: Optional[str] = None
    """Error message if loading failed."""
    
    error_type: Optional[str] = None
    """Exception type name if available."""
    
    load_duration_seconds: float = 0.0
    """Time spent loading this component."""
    
    dependencies_loaded: Tuple[str, ...] = field(default_factory=tuple)
    """Dependencies that were successfully loaded."""
    
    optional: bool = False
    """Whether this component is optional (can be skipped)."""
    
    @classmethod
    def created(
        cls,
        component_name: str,
    ) -> "AgentComponentLoadStatus":
        """Create initial status for a component."""
        return cls(
            component_name=component_name,
            load_status="pending",
            error_message=None,
            error_type=None,
            optional=False,
        )
    
    @classmethod
    def loaded(
        cls,
        component_name: str,
        dependencies_loaded: Optional[Tuple[str, ...]] = None,
        duration_seconds: float = 0.0,
    ) -> "AgentComponentLoadStatus":
        """Create success status for a component."""
        return cls(
            component_name=component_name,
            load_status="loaded",
            error_message=None,
            error_type=None,
            load_duration_seconds=duration_seconds,
            dependencies_loaded=dependencies_loaded or (),
            optional=False,
        )
    
    @classmethod
    def skipped(
        cls,
        component_name: str,
        reason: str,
        optional: bool = True,
    ) -> "AgentComponentLoadStatus":
        """Create skipped status for a component."""
        return cls(
            component_name=component_name,
            load_status="skipped",
            error_message=reason,
            error_type=None,
            optional=optional,
        )
    
    @classmethod
    def failed(
        cls,
        component_name: str,
        error_message: str,
        error_type: Optional[str] = None,
        optional: bool = False,
        duration_seconds: float = 0.0,
    ) -> "AgentComponentLoadStatus":
        """Create failure status for a component."""
        return cls(
            component_name=component_name,
            load_status="failed",
            error_message=error_message,
            error_type=error_type,
            load_duration_seconds=duration_seconds,
            optional=optional,
        )
    
    @property
    def is_success(self) -> bool:
        """Check if this component loaded successfully."""
        return self.load_status == "loaded"
    
    @property
    def is_failure(self) -> bool:
        """Check if this component failed to load."""
        return self.load_status == "failed"


# =============================================================================
# LOAD RESULT (overall result)
# =============================================================================


@dataclass(frozen=True)
class AgentLoadResult:
    """Immutable result of a component loading operation.
    
    This is the canonical output contract for loading. It contains
    all necessary information about what was loaded, skipped, or failed.
    """
    
    # Identity and provenance
    load_id: str
    """Unique load operation ID."""
    
    launch_id: str
    """Launch session ID from request."""
    
    plan_id: str
    """Load plan ID that was used."""
    
    config_fingerprint: str
    """Fingerprint of configuration used."""
    
    # Timing
    start_time_ns: int
    """Start time in nanoseconds."""
    
    end_time_ns: Optional[int]
    """End time in nanoseconds (None if still loading)."""
    
    total_duration_seconds: float
    """Total loading duration."""
    
    # Summary counts
    components_requested: int
    """Number of components in the plan."""
    
    components_loaded: int
    """Number of components successfully loaded."""
    
    components_skipped: int
    """Number of components skipped (optional or mode-dependent)."""
    
    components_failed: int
    """Number of components that failed to load."""
    
    # Component statuses
    component_statuses: Tuple[AgentComponentLoadStatus, ...]
    """Status records for each component."""
    
    # Failure evidence
    primary_failure: Optional[str]
    """Primary failure message if loading failed."""
    
    secondary_failures: Tuple[str, ...]
    """Secondary failures that did not cascade."""
    
    # Operational interface
    operational_interface_type: str
    """Type of operational interface available after load."""
    
    degraded_restrictions: Tuple[str, ...]
    """Any degradation restrictions applied."""
    
    @property
    def is_success(self) -> bool:
        """Check if loading completed successfully.
        
        Success means all required components loaded and any failures
        were optional components that were skipped gracefully.
        """
        return self.components_failed == 0
    
    @property
    def has_failures(self) -> bool:
        """Check if any failures occurred during loading."""
        return self.components_failed > 0 or len(self.secondary_failures) > 0
    
    @classmethod
    def create(
        cls,
        load_id: str,
        launch_id: str,
        plan_id: str,
        config_fingerprint: str,
        component_statuses: Tuple[AgentComponentLoadStatus, ...],
        start_time_ns: int,
        end_time_ns: Optional[int] = None,
        primary_failure: Optional[str] = None,
        secondary_failures: Optional[Tuple[str, ...]] = None,
    ) -> "AgentLoadResult":
        """Create a new load result.
        
        Args:
            load_id: Unique load operation ID
            launch_id: Launch session ID from request
            plan_id: Load plan ID that was used
            config_fingerprint: Fingerprint of configuration used
            component_statuses: Status records for each component
            start_time_ns: Start time in nanoseconds
            end_time_ns: End time in nanoseconds (optional)
            primary_failure: Primary failure message if any
            secondary_failures: Secondary failures that did not cascade
            
        Returns:
            New AgentLoadResult instance
        """
        now_ns = int(datetime.now().timestamp() * 1_000_000_000)
        
        # Calculate durations and counts
        duration_seconds = (end_time_ns - start_time_ns) / 1_000_000_000 if end_time_ns else 0.0
        
        loaded_count = sum(1 for s in component_statuses if s.load_status == "loaded")
        skipped_count = sum(1 for s in component_statuses if s.load_status == "skipped")
        failed_count = sum(1 for s in component_statuses if s.load_status == "failed")
        
        # Build degradation restrictions
        degraded: List[str] = []
        if any(s.is_failure and s.optional for s in component_statuses):
            degraded.append("some optional components were unavailable or failed")
        if any(s.load_duration_seconds > 5.0 for s in component_statuses):
            degraded.append("slow component loading detected")
        
        return cls(
            load_id=load_id,
            launch_id=launch_id,
            plan_id=plan_id,
            config_fingerprint=config_fingerprint,
            start_time_ns=start_time_ns,
            end_time_ns=end_time_ns,
            total_duration_seconds=duration_seconds,
            components_requested=len(component_statuses),
            components_loaded=loaded_count,
            components_skipped=skipped_count,
            components_failed=failed_count,
            component_statuses=component_statuses,
            primary_failure=primary_failure,
            secondary_failures=secondary_failures or (),
            operational_interface_type="canonical" if loaded_count > 0 else "none",
            degraded_restrictions=tuple(degraded),
        )
    
    @classmethod
    def success(
        cls,
        load_id: str,
        launch_id: str,
        plan_id: str,
        config_fingerprint: str,
        component_statuses: Tuple[AgentComponentLoadStatus, ...],
        start_time_ns: int,
        end_time_ns: Optional[int] = None,
    ) -> "AgentLoadResult":
        """Create a successful load result."""
        return cls.create(
            load_id=load_id,
            launch_id=launch_id,
            plan_id=plan_id,
            config_fingerprint=config_fingerprint,
            component_statuses=component_statuses,
            start_time_ns=start_time_ns,
            end_time_ns=end_time_ns,
            primary_failure=None,
        )
    
    @classmethod
    def failure(
        cls,
        load_id: str,
        launch_id: str,
        plan_id: str,
        config_fingerprint: str,
        component_statuses: Tuple[AgentComponentLoadStatus, ...],
        primary_failure: str,
        secondary_failures: Optional[Tuple[str, ...]] = None,
        start_time_ns: int = 0,
    ) -> "AgentLoadResult":
        """Create a failed load result."""
        return cls.create(
            load_id=load_id,
            launch_id=launch_id,
            plan_id=plan_id,
            config_fingerprint=config_fingerprint,
            component_statuses=component_statuses,
            start_time_ns=start_time_ns,
            end_time_ns=None,
            primary_failure=primary_failure,
            secondary_failures=secondary_failures,
        )


# =============================================================================
# LOAD FAILURE (exceptional result)
# =============================================================================


@dataclass(frozen=True)
class AgentLoadFailure:
    """Immutable failure record for component loading.
    
    This is used when a critical error prevents normal result construction.
    """
    
    load_id: str
    """Unique load operation ID."""
    
    launch_id: str
    """Launch session ID from request."""
    
    plan_id: Optional[str]
    """Load plan ID if available."""
    
    failure_phase: str
    """Phase where failure occurred (planning, discovery, loading, etc.)."""
    
    primary_failure_message: str
    """Primary failure message."""
    
    primary_failure_type: Optional[str]
    """Exception type name if available."""
    
    secondary_failures: Tuple[str, ...]
    """Secondary failures that did not cascade."""
    
    partial_load_summary: str
    """Summary of what was loaded before failure."""
    
    retry_eligible: bool
    """Whether loading can be retried."""
    
    timestamp_ns: int
    """Unix timestamp in nanoseconds when failure occurred."""
    
    @classmethod
    def create(
        cls,
        load_id: str,
        launch_id: str,
        plan_id: Optional[str],
        failure_phase: str,
        primary_failure_message: str,
        secondary_failures: Optional[Tuple[str, ...]] = None,
        partial_load_summary: str = "none",
        retry_eligible: bool = False,
        primary_failure_type: Optional[str] = None,
    ) -> "AgentLoadFailure":
        """Create a new load failure record."""
        now_ns = int(datetime.now().timestamp() * 1_000_000_000)
        
        return cls(
            load_id=load_id,
            launch_id=launch_id,
            plan_id=plan_id,
            failure_phase=failure_phase,
            primary_failure_message=primary_failure_message,
            secondary_failures=secondary_failures or (),
            partial_load_summary=partial_load_summary,
            retry_eligible=retry_eligible,
            timestamp_ns=now_ns,
        )


# =============================================================================
# EXPORTS
# =============================================================================


__all__ = [
    "AgentComponentLoadStatus",
    "AgentLoadResult",
    "AgentLoadFailure",
]