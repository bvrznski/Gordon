# Introspection Evolution - Phase 7.29
# =====================================

"""
Introspection Evolution tracks changes to Gordon's self-model over time.

Evolution is:
    Descriptive - It records how the self-model changed, not modifying it
    
An evolution record contains:
    - Explicit identity
    - Evolution history (sequence of self models)
    - Triggering events
    - Resulting self model
    - Provenance tracking

Identity remains stable across evolutions.
"""

from __future__ import annotations

import time
import uuid
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any


@dataclass(frozen=True)
class IntrospectionEvolution:
    """
    Evolution of introspective self-models over time.
    
    An evolution record contains:
        - Explicit identity
        - Evolution history (sequence of self models)
        - Triggering events
        - Resulting self model
        - Provenance tracking
    
    Identity remains stable across evolutions.
    """
    
    # Identity
    evolution_id: str                         # Unique identifier
    semantic_identity: str                    # Semantic identity for replay
    
    # Evolution history
    evolution_history: List[Dict[str, Any]] = field(default_factory=list)  # Past states
    
    # Triggering events
    triggering_events: List[str] = field(default_factory=list)  # What caused change?
    
    # Current state
    resulting_self_model: Optional[Any] = None   # Latest self model
    
    # Compatibility
    compatibility_revision: int = 1           # For schema evolution tracking
    
    # Metadata
    created_at_utc: float = field(default_factory=time.time)
    
    @classmethod
    def create(
        cls,
        semantic_identity: str,
    ) -> IntrospectionEvolution:
        """Create a new introspection evolution record."""
        return cls(
            evolution_id=f"evolution:{uuid.uuid4().hex[:16]}",
            semantic_identity=semantic_identity,
        )
    
    def with_history(self, history: List[Dict[str, Any]]) -> IntrospectionEvolution:
        """Return a copy with added history."""
        return dataclass_replace(
            self,
            evolution_history=self.evolution_history + history,
        )


def dataclass_replace(instance: Any, **kwargs: Any) -> Any:
    """Simple dataclass replace helper for frozen instances."""
    return instance.__class__(**{**instance.__dict__, **kwargs})


__all__ = [
    "IntrospectionEvolution",
]