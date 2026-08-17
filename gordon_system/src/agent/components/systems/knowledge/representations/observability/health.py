# Knowledge Representation Health - Phase 6.2
# ============================================

"""
Health monitoring for knowledge representations.

This module provides metrics for tracking representation system status:
    * Stale representations that need regeneration
    * Missing embeddings or other representation types
    * Alignment failures
    * Translation failures
    * Cache statistics
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Tuple, Optional, Any
import time
import uuid


# =============================================================================
# REPRESENTATION HEALTH - System status metrics
# =============================================================================


@dataclass(frozen=True)
class RepresentationHealth:
    """
    Health metrics for the representation system.
    
    Provides diagnostic information about representation quality and coverage.
    
    Fields:
        health_identity:      Unique identifier for this health record
        evaluated_scope:      What was evaluated (e.g., "all", "semantic_id:x")
        stale_representations: IDs of representations needing regeneration
        missing_representations: Expected but absent representations
        alignment_failures:   Alignment operations that failed
        regeneration_queue:   Representations queued for regeneration
        diagnostics:          Additional diagnostic information
    """
    
    # Identity (required)
    health_identity: str                   # Unique health ID
    
    evaluated_scope: str = "all"           # What was evaluated
    
    # Health metrics (optional, with defaults)
    stale_representations: Tuple[str, ...] = field(default_factory=tuple)
    missing_representations: Tuple[str, ...] = field(default_factory=tuple)
    alignment_failures: Tuple[Dict[str, Any], ...] = field(default_factory=tuple)
    regeneration_queue: Tuple[str, ...] = field(default_factory=tuple)
    
    diagnostics: Dict[str, Any] = field(default_factory=dict)
    
    created_at_utc: float = field(default_factory=time.time)
    
    @property
    def is_healthy(self) -> bool:
        """Check if representation system is healthy."""
        return (
            len(self.stale_representations) == 0 and
            len(self.missing_representations) == 0 and
            len(self.alignment_failures) == 0
        )
    
    @property
    def stale_count(self) -> int:
        """Get count of stale representations."""
        return len(self.stale_representations)
    
    @property
    def missing_count(self) -> int:
        """Get count of missing representations."""
        return len(self.missing_representations)
    
    @property
    def failure_count(self) -> int:
        """Get total count of failures (alignments + regeneration)."""
        return len(self.alignment_failures) + len(self.regeneration_queue)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert health record to dictionary for serialization."""
        return {
            "health_identity": self.health_identity,
            "evaluated_scope": self.evaluated_scope,
            "stale_representations": [r for r in self.stale_representations],
            "missing_representations": [r for r in self.missing_representations],
            "alignment_failures": [f for f in self.alignment_failures],
            "regeneration_queue": [q for q in self.regeneration_queue],
            "diagnostics": self.diagnostics,
            "created_at_utc": self.created_at_utc,
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "RepresentationHealth":
        """Create health record from dictionary."""
        return cls(
            health_identity=data.get("health_identity", str(uuid.uuid4())),
            evaluated_scope=data.get("evaluated_scope", "all"),
            stale_representations=tuple(data.get("stale_representations", [])),
            missing_representations=tuple(data.get("missing_representations", [])),
            alignment_failures=tuple(data.get("alignment_failures", [])),
            regeneration_queue=tuple(data.get("regeneration_queue", [])),
            diagnostics=data.get("diagnostics", {}),
            created_at_utc=float(data.get("created_at_utc", time.time())),
        )
    
    @classmethod
    def create_initial(
        cls,
        evaluated_scope: str = "all",
    ) -> "RepresentationHealth":
        """Create initial healthy state."""
        return cls(
            health_identity=f"health:{uuid.uuid4().hex[:16]}",
            evaluated_scope=evaluated_scope,
        )
    
    def with_stale(self, representation_id: str) -> "RepresentationHealth":
        """Mark a representation as stale."""
        return RepresentationHealth(
            health_identity=self.health_identity,
            evaluated_scope=self.evaluated_scope,
            stale_representations=self.stale_representations + (representation_id,),
            missing_representations=self.missing_representations,
            alignment_failures=self.alignment_failures,
            regeneration_queue=self.regeneration_queue,
            diagnostics={**self.diagnostics, "updated_at": time.time()},
        )
    
    def with_missing(self, representation_id: str) -> "RepresentationHealth":
        """Mark a representation as missing."""
        return RepresentationHealth(
            health_identity=self.health_identity,
            evaluated_scope=self.evaluated_scope,
            stale_representations=self.stale_representations,
            missing_representations=self.missing_representations + (representation_id,),
            alignment_failures=self.alignment_failures,
            regeneration_queue=self.regeneration_queue,
            diagnostics={**self.diagnostics, "updated_at": time.time()},
        )
    
    def with_failure(self, failure_info: Dict[str, Any]) -> "RepresentationHealth":
        """Add a failure to the health record."""
        return RepresentationHealth(
            health_identity=self.health_identity,
            evaluated_scope=self.evaluated_scope,
            stale_representations=self.stale_representations,
            missing_representations=self.missing_representations,
            alignment_failures=self.alignment_failures + (failure_info,),
            regeneration_queue=self.regeneration_queue,
            diagnostics={**self.diagnostics, "updated_at": time.time()},
        )


__all__ = [
    # Health records
    "RepresentationHealth",
]