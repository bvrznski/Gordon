# Internal Episode Dependency Model
# ================================

"""
Dependency model for episode plan steps.

Dependencies describe semantic relationships between coordination steps,
not runtime parallelism decisions.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Tuple, Optional


@dataclass(frozen=True, slots=True)
class InternalEpisodeDependency:
    """
    Dependency relationship between two plan steps.
    
    Dependencies describe semantic relationships without committing to
    runtime parallelism. Execution and Core decide actual concurrency.
    
    DEPENDENCY KINDS:
        • requires: This step requires the other to complete first (blocking)
        • optionally_uses: Can use results if available but doesn't require them
        • follows: This step follows in sequence (implied ordering)
        • may_parallelize: These steps may run concurrently when possible
        • blocks: This step blocks the other from starting
        • invalidates: This step invalidates results of the other
    """
    
    source_step_id: str
    """Step ID that is the dependency source."""
    
    target_step_id: str
    """Step ID that depends on the source."""
    
    kind: str  # DependencyKind.*
    """Type of dependency relationship."""
    
    optional: bool = False
    """Whether this dependency can be skipped."""
    
    reason: Optional[str] = None
    """Human-readable explanation of the dependency."""


DependencyKind = InternalEpisodeDependency.kind.__annotations__.get("kind", "str")
"""Alias for DependencyKind type."""