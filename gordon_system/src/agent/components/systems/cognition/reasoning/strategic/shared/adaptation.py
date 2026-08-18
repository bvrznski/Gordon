# Strategic Adaptation - Phase 7.18
# ==================================

"""
Canonical Strategic Adaptation for Phase 7.18.

Strategies evolve through environmental changes, mission changes, resource changes,
new evidence, and learning while maintaining strategic identity.
"""

from __future__ import annotations

import time
import uuid
from dataclasses import dataclass, field
from typing import Dict, List, Tuple, Optional, Any
from enum import Enum, auto


@dataclass(frozen=True)
class StrategicAdaptation:
    """
    Adaptation of a strategy to changing conditions.
    
    Adaptation preserves strategic identity while updating the strategy based on:
        - Environmental changes
        - Mission evolution
        - Resource availability changes
        - New evidence
        - Learning from experience
    
    Each adaptation is traced back to its original strategy for full lineage tracking.
    """
    
    # Identity
    adaptation_id: str                      # Unique adaptation identifier
    
    # Original strategy being adapted
    original_strategy_id: str               # Which strategy was adapted?
    
    # Previous state
    previous_strategy: Optional[Dict[str, Any]] = None  # Snapshot before change
    
    # Adapted state
    adapted_strategy: Dict[str, Any]        # Strategy after adaptation
    
    # Supporting changes (what changed)
    supporting_changes: List[str] = field(default_factory=list)  # e.g., "resource_increase", "new_evidence"
    
    # Triggering event
    adaptation_trigger: str = ""            # What triggered the change?
    
    # Rationale for the adaptation
    adaptation_rationale: str = ""          # Why was this adaptation made?
    
    # Provenance
    adapted_at_utc: float = field(default_factory=time.time)
    
    @property
    def is_minor(self) -> bool:
        """Check if this is a minor adaptation (no strategy change)."""
        return self.previous_strategy == self.adapted_strategy


@dataclass(frozen=True)
class StrategicAdaptationPipeline:
    """
    A pipeline of adaptations applied to a strategy over time.
    
    Each adaptation in the sequence is applied to the result of the previous,
    creating an evolution history that can be replayed deterministically.
    """
    
    # Identity
    pipeline_id: str
    
    # Original strategy
    original_strategy_identity: str
    
    # Sequence of adaptations (chronological, oldest first)
    adaptation_sequence: List[StrategicAdaptation]
    
    # Current state after all adaptations
    current_state: Dict[str, Any]
    
    # Timing
    created_at_utc: float = field(default_factory=time.time)
    last_adapted_at_utc: Optional[float] = None
    
    @property
    def adaptation_count(self) -> int:
        """Return the number of adaptations in this pipeline."""
        return len(self.adaptation_sequence)
    
    @property
    def is_stable(self) -> bool:
        """Check if strategy has stabilized (no recent changes)."""
        if self.adaptation_count < 3:
            return True
        
        # Check if last 2 adaptations were minor (no change)
        last_two = self.adaptation_sequence[-2:]
        return all(a.is_minor for a in last_two)


@dataclass(frozen=True)
class AdaptationFailure:
    """
    Record of a failed adaptation attempt.
    """
    
    # Identity
    failure_id: str
    
    # Input that failed
    strategy_id: str
    trigger_event: str                      # What event triggered the attempted adaptation?
    
    # Failure kind
    failure_kind: str                       # e.g., "incompatible_change", "resource_infeasible"
    
    # Diagnostics
    diagnostics: List[str] = field(default_factory=list)
    
    # Timing
    failed_at_utc: float = field(default_factory=time.time)


__all__ = [
    "StrategicAdaptation",
    "StrategicAdaptationPipeline",
    "AdaptationFailure",
]