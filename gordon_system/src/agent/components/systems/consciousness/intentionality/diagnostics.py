# Gordon Phase 5.7.3-I: Intentional Context Engine - Diagnostics
# ===============================================================================
#
# Passive metrics and health information for the intentional context.
#

"""
Intentional Context Diagnostics for the Intentional Context Engine.

Diagnostics provide operational insights without exposing private or sensitive
context content. They are safe for observability and monitoring systems.
"""

from __future__ import annotations

import time
from dataclasses import dataclass, field
from typing import Tuple, Optional


# =============================================================================
# INTENTIONAL CONTEXT DIAGNOSTICS SNAPSHOT
# =============================================================================

@dataclass(frozen=True)
class IntentionalContextDiagnosticsSnapshot:
    """
    Bounded diagnostics information for intentional context.
    
    Diagnostics provide operational insights without exposing private
    or sensitive context content. They are safe for observability and
    monitoring systems.
    """
    
    # Identity
    context_id: str = "intentionality-001"
    """Intentional context identity."""
    
    generation: int = 0
    """Current intentional context generation."""
    
    age_seconds: float = field(default_factory=time.time)
    """How long since last update (computed)."""
    
    # Object metrics
    registered_object_count: int = 0
    """Total registered intentional objects."""
    
    active_object_count: int = 0
    """Objects currently in use (active lifecycle state)."""
    
    kind_counts: Tuple[str, ...] = field(default_factory=tuple)
    """Object kind distribution."""
    
    # Relation metrics
    registered_relation_count: int = 0
    """Total registered intentional relations."""
    
    active_relation_count: int = 0
    """Relations currently in use (not expired)."""
    
    relation_kind_counts: Tuple[str, ...] = field(default_factory=tuple)
    """Relation kind distribution."""
    
    # Target metrics
    registered_target_count: int = 0
    """Total registered intentional targets."""
    
    active_target_count: int = 0
    """Targets currently in use (active/suspended status)."""
    
    target_status_counts: Tuple[str, ...] = field(default_factory=tuple)
    """Target status distribution."""
    
    # Transition metrics
    last_transition_id: Optional[str] = None
    """Last transition that completed."""
    
    last_transition_duration_seconds: float = 0.0
    """Duration of last transition."""
    
    last_transition_status: str = "completed"
    """Status of last transition."""
    
    pending_transition_count: int = 0
    """Transitions waiting for publication."""
    
    # Health indicators
    degradation_state: Tuple[str, ...] = field(default_factory=tuple)
    """Current degradation modes."""
    
    privacy_summary: str = "internal"
    """Privacy classification of current context."""
    
    trust_summary: str = "medium"
    """Trust classification of current context."""
    
    # Performance metrics
    query_count_1m: int = 0
    """Queries in last minute."""
    
    transition_count_1m: int = 0
    """Transitions in last minute."""
    
    error_count_1m: int = 0
    """Errors in last minute."""
    
    @property
    def is_ready(self) -> bool:
        """Check if intentional context is ready for operations."""
        return self.registered_object_count >= 0 and self.degradation_state == ()


# =============================================================================
# INTENTIONAL CONTEXT HEALTH SNAPSHOT
# =============================================================================

@dataclass(frozen=True)
class IntentionalContextHealthSnapshot:
    """
    Bounded health information for intentional context.
    
    Health reflects operational readiness, not context population.
    A populated context is not automatically healthy.
    An empty context may be valid during initialization or controlled operation.
    """
    
    # Identity
    context_id: str = "intentionality-001"
    """Intentional context identity."""
    
    state: str = "active"
    """Current health state (ready, active, degraded, failed)."""
    
    last_update_utc: float = field(default_factory=time.time)
    """When this health snapshot was generated."""
    
    # Readiness indicators
    initialized: bool = False
    """Whether intentional context is initialized."""
    
    ready: bool = False
    """Whether intentional context is ready for operations."""
    
    active: bool = False
    """Whether intentional context is actively processing."""
    
    # Dependency status
    required_objects_ready: Tuple[str, ...] = field(default_factory=tuple)
    """Required objects that are ready."""
    
    optional_objects_available: Tuple[str, ...] = field(default_factory=tuple)
    """Optional objects that are available."""
    
    # Failure information
    last_failure_category: Optional[str] = None
    """Category of last failure (if any)."""
    
    last_failure_timestamp: Optional[float] = None
    """Timestamp of last failure (if any)."""
    
    recovery_status: str = "none"
    """Current recovery status."""
    
    # Capacity
    pending_operations: int = 0
    """Number of pending operations."""
    
    max_capacity_reached: bool = False
    """Whether capacity limits have been reached."""


# =============================================================================
# EXPORTS
# =============================================================================

__all__: tuple[str, ...] = (
    "IntentionalContextDiagnosticsSnapshot",
    "IntentionalContextHealthSnapshot",
)