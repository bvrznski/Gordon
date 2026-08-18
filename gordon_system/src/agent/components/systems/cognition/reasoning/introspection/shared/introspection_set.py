# Introspection Set - Phase 7.29
# ==============================

"""
Introspection Sets define the scope and constraints for introspection reasoning.

An introspection set defines:
    - Observed subsystems
    - Observation boundaries
    - Available telemetry
    - Publication policies
    - Consistency constraints

Introspection sets remain immutable during reasoning.
"""

from __future__ import annotations

import time
import uuid
from dataclasses import dataclass, field
from typing import Dict, List, Set, Tuple, Optional, Any
from enum import Enum, auto


class ObservationBoundary(Enum):
    """Boundaries for introspection observation."""
    
    ALL_SUBSYSTEMS = "all_subsystems"           # Observe all subsystems
    ACTIVE_GOALS = "active_goals"              # Observe active goals only
    REASONING_STACK = "reasoning_stack"        # Observe reasoning stack
    EXECUTION_STATE = "execution_state"        # Observe execution state
    MEMORY_UTILIZATION = "memory_utilization"  # Observe memory utilization


class PublicationPolicy(Enum):
    """Publication policies for introspection results."""
    
    INTERNAL_ONLY = "internal_only"             # Internal use only
    MONITORING = "monitoring"                   # Available to monitoring systems
    DIAGNOSTIC = "diagnostic"                   # Available for diagnostics
    PERSISTENT = "persistent"                   # Persisted for history


@dataclass(frozen=True)
class IntrospectionSet:
    """
    Set of subsystems and constraints for introspection reasoning.
    
    An introspection set contains:
        - Explicit identity
        - Participating subsystems
        - Observation boundaries
        - Operational constraints
        - Provenance tracking
    
    Introspection sets remain immutable during reasoning.
    """
    
    # Identity
    introspection_set_id: str                 # Unique identifier
    semantic_identity: str                    # Semantic identity for replay
    
    # Participating subsystems
    participating_subsystems: Set[str]        # Subsystems being observed
    
    # Observation boundaries
    observation_boundary: ObservationBoundary = ObservationBoundary.ALL_SUBSYSTEMS
    temporal_scope: Tuple[float, float] = (0.0, float('inf'))  # Time range
    
    # Available telemetry sources
    telemetry_sources: Dict[str, Any] = field(default_factory=dict)
    
    # Publication policy
    publication_policy: PublicationPolicy = PublicationPolicy.INTERNAL_ONLY
    
    # Consistency constraints
    min_confidence_required: float = 0.5      # Minimum confidence for assertions
    max_inconsistencies_allowed: int = 3      # Maximum before marking as inconsistent
    
    # Compatibility
    compatibility_revision: int = 1           # For schema evolution tracking
    
    # Metadata
    created_at_utc: float = field(default_factory=time.time)
    
    # Provenance
    source_descriptor_id: Optional[str] = None   # Where did this set originate?
    
    @classmethod
    def create(
        cls,
        semantic_identity: str,
        participating_subsystems: Set[str],
        observation_boundary: ObservationBoundary = ObservationBoundary.ALL_SUBSYSTEMS,
        publication_policy: PublicationPolicy = PublicationPolicy.INTERNAL_ONLY,
        source_descriptor_id: Optional[str] = None,
    ) -> IntrospectionSet:
        """Create a new introspection set."""
        return cls(
            introspection_set_id=f"introspection_set:{uuid.uuid4().hex[:16]}",
            semantic_identity=semantic_identity,
            participating_subsystems=participating_subsystems,
            observation_boundary=observation_boundary,
            publication_policy=publication_policy,
            source_descriptor_id=source_descriptor_id,
        )
    
    def with_subsystems(self, subsystems: Set[str]) -> IntrospectionSet:
        """Return a copy with updated subsystems."""
        return dataclass_replace(
            self,
            participating_subsystems=subsystems,
        )
    
    def with_boundary(self, boundary: ObservationBoundary) -> IntrospectionSet:
        """Return a copy with updated observation boundary."""
        return dataclass_replace(
            self,
            observation_boundary=boundary,
        )


@dataclass(frozen=True)
class TelemetrySource:
    """
    A source of telemetry data for introspection.
    
    Each source provides:
        - Data type
        - Freshness constraints
        - Accuracy guarantees
    """
    
    # Identity
    source_id: str                            # Unique identifier
    source_type: str                          # e.g., "cognitive_state", "resource_usage"
    
    # Telemetry properties
    data_type: str                            # Type of data provided
    freshness_seconds: float = 5.0            # Maximum acceptable age
    accuracy_minimum: float = 0.8             # Minimum accuracy guarantee
    
    # Constraints
    required_for_consistency: bool = True     # Must be available for consistency checks


def dataclass_replace(instance: Any, **kwargs: Any) -> Any:
    """Simple dataclass replace helper for frozen instances."""
    return instance.__class__(**{**instance.__dict__, **kwargs})


__all__ = [
    "IntrospectionSet",
    "ObservationBoundary",
    "PublicationPolicy",
    "TelemetrySource",
]