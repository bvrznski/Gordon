# Reflection Set - Phase 7.28
# ===========================

"""
Reflection Set defines the scope of reflection.

A reflection set contains completed sessions for reflection analysis.
"""

from __future__ import annotations

import time
import uuid
from dataclasses import dataclass, field
from typing import Dict, List, Tuple, Optional, Any
from enum import Enum, auto


@dataclass(frozen=True)
class ReflectionSet:
    """
    Set of completed cognitive sessions for reflection analysis.
    
    A reflection set defines:
        - Participating completed sessions
        - Reflection scope (what to analyze)
        - Operational constraints (time range, confidence thresholds)
        - Provenance tracking
    
    Reflection sets remain immutable during reflection.
    """
    
    # Identity
    reflection_set_id: str                    # Unique set identifier
    semantic_identity: str                    # Semantic identity for replay
    
    # Participating sessions (completed cognitive activity to analyze)
    participating_sessions: List[str]         # Session IDs to reflect on
    
    # Reflection scope
    reflection_scope: str                     # What to focus reflection on?
    
    # Operational constraints
    min_confidence_threshold: float = 0.5     # Minimum confidence for inclusion
    max_time_range_seconds: Optional[float] = None  # Time range limit
    source_filter: List[str] = field(default_factory=list)  # Filter by source
    
    # Constraints and requirements
    min_evidence_required: int = 1            # Minimum evidence per candidate
    max_candidates: int = 20                  # Maximum candidates to consider
    
    # Compatibility
    compatibility_revision: int = 1           # For schema evolution tracking
    
    # Metadata
    created_at_utc: float = field(default_factory=time.time)
    
    # Provenance
    source_reflection_set_id: Optional[str] = None   # If this is a refinement
    origin_context: str = "unknown"                   # Where did reflection originate?
    
    @property
    def session_count(self) -> int:
        """Count of participating sessions."""
        return len(self.participating_sessions)
    
    @classmethod
    def create(
        cls,
        semantic_identity: str,
        participating_sessions: List[str],
        reflection_scope: str = "general",
        origin_context: str = "unknown",
        source_reflection_set_id: Optional[str] = None,
        min_confidence_threshold: float = 0.5,
    ) -> ReflectionSet:
        """Create a new reflection set."""
        return cls(
            reflection_set_id=f"reflection_set:{uuid.uuid4().hex[:16]}",
            semantic_identity=semantic_identity,
            participating_sessions=participating_sessions,
            reflection_scope=reflection_scope,
            origin_context=origin_context,
            source_reflection_set_id=source_reflection_set_id,
            min_confidence_threshold=min_confidence_threshold,
        )
    
    def with_participating_sessions(self, sessions: List[str]) -> ReflectionSet:
        """Return a copy with updated participating sessions."""
        return dataclass_replace(
            self,
            participating_sessions=sessions,
        )


def dataclass_replace(instance: Any, **kwargs: Any) -> Any:
    """Simple dataclass replace helper for frozen instances."""
    # For Python 3.12+, use dataclasses.replace
    # This is a simple implementation for compatibility
    return instance.__class__(**{**instance.__dict__, **kwargs})


__all__ = [
    "ReflectionSet",
]