# Dialectical Descriptor - Phase 7.17
# ====================================

"""
Canonical Dialectical Descriptor.

A descriptor exposes dialectical metadata independently of execution.
"""

from __future__ import annotations

import time
import uuid
from dataclasses import dataclass, field
from typing import Dict, List, Tuple, Optional, Any
from enum import Enum, auto


class DialecticalState(Enum):
    """Dialectical session lifecycle states."""

    CREATED = "created"
    INITIALIZING = "initializing"
    ARGUMENT_GENERATION = "argument_generation"
    CONFLICT_ANALYSIS = "conflict_analysis"
    SYNTHESIS = "synthesis"
    CONSENSUS = "consensus"
    VALIDATING = "validating"
    COMPLETED = "completed"
    FAILED = "failed"
    ARCHIVED = "archived"


@dataclass(frozen=True)
class DialecticalDescriptor:
    """
    Descriptor exposing dialectical metadata independently of execution.

    A descriptor contains:
        - Semantic identity (immutable, persistent across runs)
        - Reasoning goal
        - Dialectical mode
        - Lifecycle state
        - Compatibility information
        - Provenance tracking

    Descriptors allow inspection of what dialectics occurred without
    needing to execute the full reasoning process again.
    """

    # Identity
    descriptor_id: str                      # Unique descriptor identifier
    semantic_identity: str                  # Semantic identity (stable across runs)

    # Reasoning goal
    reasoning_goal: str                     # What are we trying to resolve?

    # Dialectical mode
    dialectical_mode: str = "dialectical"   # e.g., "dialectical", "multi-perspective"

    # Lifecycle state
    lifecycle_state: DialecticalState = DialecticalState.CREATED

    # Compatibility
    compatibility_revision: int = 1         # For schema evolution tracking

    # Timing
    created_at_utc: float = field(default_factory=time.time)
    started_at_utc: Optional[float] = None
    completed_at_utc: Optional[float] = None

    # Provenance
    source_descriptor_id: Optional[str] = None   # If this is a refinement
    origin_context: str = "unknown"              # Where did dialectics originate?

    @property
    def duration_seconds(self) -> float:
        """Calculate duration if completed."""
        if self.started_at_utc and self.completed_at_utc:
            return self.completed_at_utc - self.started_at_utc
        if self.started_at_utc:
            return time.time() - self.started_at_utc
        return 0.0

    @property
    def is_completed(self) -> bool:
        """Check if dialectics completed."""
        return self.lifecycle_state == DialecticalState.COMPLETED

    @property
    def is_failed(self) -> bool:
        """Check if dialectics failed."""
        return self.lifecycle_state == DialecticalState.FAILED

    @property
    def is_archived(self) -> bool:
        """Check if dialectics is archived."""
        return self.lifecycle_state == DialecticalState.ARCHIVED

    @classmethod
    def create(
        cls,
        semantic_identity: str,
        reasoning_goal: str,
        origin_context: str = "unknown",
        source_descriptor_id: Optional[str] = None,
    ) -> DialecticalDescriptor:
        """Create a new dialectical descriptor."""
        return cls(
            descriptor_id=f"dialectical_descriptor:{uuid.uuid4().hex[:16]}",
            semantic_identity=semantic_identity,
            reasoning_goal=reasoning_goal,
            origin_context=origin_context,
            source_descriptor_id=source_descriptor_id,
            started_at_utc=time.time(),
        )

    def to_state(self, new_state: DialecticalState) -> DialecticalDescriptor:
        """Return a copy with updated state."""
        return dataclass_replace(
            self,
            lifecycle_state=new_state,
            completed_at_utc=time.time() if new_state == DialecticalState.COMPLETED else None,
        )


def dataclass_replace(instance: Any, **kwargs: Any) -> Any:
    """Simple dataclass replace helper for frozen instances."""
    # For Python 3.12+, use dataclasses.replace
    # This is a simple implementation for compatibility
    return instance.__class__(**{**instance.__dict__, **kwargs})


__all__ = [
    "DialecticalDescriptor",
    "DialecticalState",
]