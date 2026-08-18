# Dialectical Refinement - Phase 7.17
# ===================================

"""
Canonical Dialectical Refinement Contract.

Dialectical models evolve through:
    - New evidence
    - New arguments
    - Better synthesis
    - Improved conflict analysis
    - Updated assumptions
"""

from __future__ import annotations

import time
import uuid
from dataclasses import dataclass, field
from typing import Dict, List, Tuple, Optional, Any


@dataclass(frozen=True)
class DialecticalRefinement:
    """
    A dialectical refinement process.

    Refinement preserves historical arguments while incorporating new information.

    Refinement may include:
        - New evidence incorporated
        - New arguments integrated
        - Better syntheses constructed
        - Improved conflict analyses performed
        - Updated assumptions made
    """

    # Identity (remains stable across refinements)
    refinement_id: str                      # Unique identifier

    # Previous model (what was refined?)
    previous_model: Dict[str, Any]

    # Refined model (what is the result?)
    refined_model: Dict[str, Any]

    # Supporting changes (how did it change?)
    supporting_changes: Tuple[Dict[str, Any], ...] = ()

    # Timing
    applied_at_utc: float = field(default_factory=time.time)

    # Provenance
    origin_context: str = "unknown"

    @classmethod
    def create(
        cls,
        previous_model: Dict[str, Any],
        refined_model: Dict[str, Any],
        origin_context: str = "unknown",
    ) -> DialecticalRefinement:
        """Create a new refinement record."""
        return cls(
            refinement_id=f"dialectical_refinement:{uuid.uuid4().hex[:16]}",
            previous_model=previous_model,
            refined_model=refined_model,
            origin_context=origin_context,
        )

    def with_change(self, change: Dict[str, Any]) -> DialecticalRefinement:
        """Record a supporting change."""
        return dataclass_replace(
            self,
            supporting_changes=self.supporting_changes + (change,),
        )


def dataclass_replace(instance: Any, **kwargs: Any) -> Any:
    """Simple dataclass replace helper for frozen instances."""
    return instance.__class__(**{**instance.__dict__, **kwargs})


__all__ = [
    "DialecticalRefinement",
]