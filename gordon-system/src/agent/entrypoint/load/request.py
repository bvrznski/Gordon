"""Gordon Agent Load Request Models.

Phase 3.7.30: Agent Initialization Chain
========================================

Immutable models for component loading requests.
"""

from __future__ import annotations

import uuid
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum, auto
from typing import (
    Any,
    Dict,
    FrozenSet,
    List,
    Optional,
    Tuple,
)


# =============================================================================
# LOAD PLAN (returned from request_load_plan)
# =============================================================================


@dataclass(frozen=True)
class LoadPlan:
    """Immutable load plan specifying component construction order.
    
    A load plan is created by requesting a plan for a specific launch
    configuration. It contains the ordered sequence of components that
    must be loaded, including dependency information.
    
    The plan is:
    - Deterministic: same inputs produce identical plans
    - Immutable: cannot be modified after creation
    - Complete: all dependencies are included in the order
    """
    
    plan_id: str
    """Unique identifier for this load plan."""
    
    launch_id: str
    """Launch session ID this plan is for."""
    
    config_fingerprint: str
    """Fingerprint of configuration used to generate this plan."""
    
    component_order: Tuple[str, ...]
    """Ordered list of components to load (dependencies first)."""
    
    component_dependencies: Dict[str, Tuple[str, ...]]
    """Mapping from component name to its dependencies."""
    
    optional_components: FrozenSet[str]
    """Components that can be skipped if loading fails."""
    
    required_components: FrozenSet[str]
    """Components whose failure terminates initialization."""
    
    created_at_ns: int
    """Timestamp when plan was created (nanoseconds)."""
    
    @classmethod
    def create(
        cls,
        launch_id: str,
        config_fingerprint: str,
        component_order: Tuple[str, ...],
        component_dependencies: Dict[str, Tuple[str, ...]],
        optional_components: Optional[FrozenSet[str]] = None,
        required_components: Optional[FrozenSet[str]] = None,
    ) -> "LoadPlan":
        """Create a new load plan.
        
        Args:
            launch_id: Launch session ID
            config_fingerprint: Configuration fingerprint this plan is based on
            component_order: Ordered list of components to load (deps first)
            component_dependencies: Mapping from component name to dependencies
            optional_components: Components that can be skipped if loading fails
            required_components: Components whose failure terminates initialization
            
        Returns:
            New LoadPlan instance
        """
        now_ns = int(datetime.now().timestamp() * 1_000_000_000)
        
        return cls(
            plan_id="plan_" + str(uuid.uuid4()),
            launch_id=launch_id,
            config_fingerprint=config_fingerprint,
            component_order=component_order,
            component_dependencies=component_dependencies,
            optional_components=optional_components or frozenset(),
            required_components=required_components or frozenset(),
            created_at_ns=now_ns,
        )
    
    @classmethod
    def create_default(cls, launch_id: str) -> "LoadPlan":
        """Create a default load plan for testing.
        
        Args:
            launch_id: Launch session ID
            
        Returns:
            Default LoadPlan with no components
        """
        return cls.create(
            launch_id=launch_id,
            config_fingerprint="default",
            component_order=(),
            component_dependencies={},
        )


# =============================================================================
# LOAD REQUEST (input to load_components)
# =============================================================================


@dataclass(frozen=True)
class AgentLoadRequest:
    """Immutable request for component loading.
    
    This is the canonical input contract for loading components. All fields
    are explicitly declared and validated before any loading occurs.
    """
    
    # Identity
    plan_id: str
    """The load plan ID this request is based on."""
    
    launch_id: str
    """Launch session ID from AgentLaunchRequest."""
    
    config_fingerprint: str
    """Fingerprint of validated effective configuration."""
    
    # Mode constraints
    safe_mode_enabled: bool = False
    """Enable safe mode (skip optional components that might fail)."""
    
    offline_mode_enabled: bool = False
    """Enable offline mode (skip network-dependent components)."""
    
    validation_only: bool = False
    """Validation-only mode (do not actually load, just validate plan)."""
    
    # Deadlines
    startup_deadline_seconds: float = 30.0
    """Maximum time allowed for loading."""
    
    # Correlation
    correlation_id: Optional[str] = None
    """Correlation context ID for tracing."""
    
    causation_id: Optional[str] = None
    """Causation event ID if invoked in response to another event."""
    
    @property
    def is_validation_only(self) -> bool:
        """Check if validation-only mode is enabled."""
        return self.validation_only
    
    @property
    def is_safe_mode(self) -> bool:
        """Check if safe mode is enabled."""
        return self.safe_mode_enabled
    
    @property
    def is_offline(self) -> bool:
        """Check if offline mode is enabled."""
        return self.offline_mode_enabled
    
    @classmethod
    def create(
        cls,
        plan_id: str,
        launch_id: str,
        config_fingerprint: str,
        **kwargs
    ) -> "AgentLoadRequest":
        """Create a new load request.
        
        Args:
            plan_id: The load plan ID this request is based on
            launch_id: Launch session ID from AgentLaunchRequest
            config_fingerprint: Fingerprint of validated effective configuration
            
        Additional kwargs:
            safe_mode_enabled, offline_mode_enabled, validation_only
            startup_deadline_seconds, correlation_id, causation_id
            
        Returns:
            New AgentLoadRequest instance
        """
        return cls(
            plan_id=plan_id,
            launch_id=launch_id,
            config_fingerprint=config_fingerprint,
            safe_mode_enabled=kwargs.get("safe_mode_enabled", False),
            offline_mode_enabled=kwargs.get("offline_mode_enabled", False),
            validation_only=kwargs.get("validation_only", False),
            startup_deadline_seconds=kwargs.get("startup_deadline_seconds", 30.0),
            correlation_id=kwargs.get("correlation_id"),
            causation_id=kwargs.get("causation_id"),
        )


# =============================================================================
# EXPORTS
# =============================================================================


__all__ = [
    "LoadPlan",
    "AgentLoadRequest",
]