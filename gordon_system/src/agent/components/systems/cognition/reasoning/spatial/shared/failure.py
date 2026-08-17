# Spatial Failure - Phase 7.9
# ==========================

"""
Canonical Spatial Failure.

Spatial failures include:
    missing reference frames, invalid geometry, inconsistent coordinates,
    topological conflicts, resource exhaustion.
    
Failures remain explicit and reconstructable.
"""

from __future__ import annotations

import time
import uuid
from dataclasses import dataclass, field
from typing import Dict, List, Tuple, Optional, Any
from enum import Enum, auto


@dataclass(frozen=True)
class SpatialFailure:
    """
    Record of a spatial failure during reasoning.
    
    Failures remain explicit and never silently discard spatial entities.
    """
    
    # Identity
    failure_id: str                         # Unique identifier
    
    # Failure kind
    failure_kind: str                       # e.g., "missing_frame", "invalid_geometry"
    
    # Diagnostics
    diagnostics: Tuple[str, ...] = ()       # Detailed diagnostic info
    
    # Recovery options (what could be done?)
    recovery_options: Tuple[str, ...] = ()  # Possible recovery strategies
    
    # Context
    failed_entity_ids: Tuple[str, ...] = ()
    context_description: str = ""
    
    # Provenance
    created_at_utc: float = field(default_factory=time.time)
    source_descriptor_id: str = ""
    
    @property
    def has_diagnostics(self) -> bool:
        """Check if diagnostics are available."""
        return len(self.diagnostics) > 0
    
    @property
    def has_recovery_options(self) -> bool:
        """Check if recovery options are available."""
        return len(self.recovery_options) > 0


class FailureKind(Enum):
    """Kinds of spatial failures."""
    
    MISSING_REFERENCE_FRAME = "missing_reference_frame"       # Frame not found
    INVALID_GEOMETRY = "invalid_geometry"                     # Geometry malformed
    INCONSISTENT_COORDINATES = "inconsistent_coordinates"     # Coordinates conflict
    TOPOLOGICAL_CONFLICT = "topological_conflict"             # Topology invalid
    RESOURCE_EXHAUSTION = "resource_exhaustion"               # Out of memory/time
    TRANSFORM_INVERTIBLE = "transform_invertible"             # Transform not invertible
    UNRESOLVABLE_RELATION = "unresolvable_relation"           # Cannot determine relation


def dataclass_replace(instance: Any, **kwargs: Any) -> Any:
    """Simple dataclass replace helper for frozen instances."""
    return instance.__class__(**{**instance.__dict__, **kwargs})


__all__ = [
    "SpatialFailure", 
    "FailureKind",
]