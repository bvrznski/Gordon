# Reasoning Deliberation - Phase 7.0
# ====================================

"""
Canonical Deliberation Contract.

Deliberation compares alternatives and selects preferred ones.
"""

from __future__ import annotations

import time
import uuid
from dataclasses import dataclass, field
from typing import Dict, List, Tuple, Optional, Any


@dataclass(frozen=True)
class Deliberation:
    """
    Deliberation comparing alternatives and selecting a preferred one.
    
    A deliberation contains:
        - Identity and traceability
        - Alternatives that were compared
        - Evaluation strategy used
        - Selected alternative (if any)
        - Reasoning trace for how the selection was made
    
    Deliberation preserves explicit record of why an alternative was chosen.
    """
    
    # Identity
    deliberation_id: str                    # Unique identifier
    
    # Alternatives considered
    alternatives: Tuple[str, ...]           # Alternative IDs (or references)
    
    # Evaluation
    evaluation_strategy: str                # How were alternatives evaluated?
    criteria_used: Tuple[str, ...] = ()     # What criteria were applied?
    
    # Results
    selected_alternative: Optional[str] = None  # Which was chosen? (None if undecided)
    rejection_reasons: Dict[str, str] = field(default_factory=dict)  # alt_id -> reason
    
    # Trace
    reasoning_trace: Tuple[str, ...] = ()   # Key reasoning steps
    intermediate_results: Tuple[str, ...] = ()  # Step-by-step results
    
    # Timing
    started_at_utc: float = field(default_factory=time.time)
    completed_at_utc: Optional[float] = None
    
    # Provenance
    deliberated_by: str = "unknown"         # Who/what performed deliberation?
    provenance: Dict[str, str] = field(default_factory=dict)
    
    @property
    def is_completed(self) -> bool:
        """Check if deliberation produced a selection."""
        return self.selected_alternative is not None
    
    @property
    def alternatives_count(self) -> int:
        """Count of alternatives considered."""
        return len(self.alternatives)
    
    @classmethod
    def create(
        cls,
        alternative_ids: List[str],
        evaluation_strategy: str,
        criteria: Optional[List[str]] = None,
        deliberated_by: str = "unknown",
    ) -> Deliberation:
        """Create a new deliberation."""
        return cls(
            deliberation_id=f"deliberation:{uuid.uuid4().hex[:16]}",
            alternatives=tuple(alternative_ids),
            evaluation_strategy=evaluation_strategy,
            criteria_used=tuple(criteria or []),
            selected_alternative=None,
            deliberated_by=deliberated_by,
            started_at_utc=time.time(),
        )
    
    def record_rejection(self, alternative_id: str, reason: str) -> "Deliberation":
        """Record that an alternative was rejected."""
        new_rejections = dict(self.rejection_reasons)
        new_rejections[alternative_id] = reason
        return dataclass_replace(
            self,
            rejection_reasons=new_rejections,
        )
    
    def select_alternative(self, alternative_id: str, trace: Optional[List[str]] = None) -> "Deliberation":
        """Record selection of an alternative."""
        return dataclass_replace(
            self,
            selected_alternative=alternative_id,
            reasoning_trace=tuple(trace or []) + self.reasoning_trace,
            completed_at_utc=time.time(),
        )


@dataclass(frozen=True)
class DeliberationPipeline:
    """
    A complete deliberation pipeline execution.
    
    The pipeline follows the canonical flow:
        1. Generate Alternatives
        2. Evaluate Alternatives  
        3. Compare
        4. Rank
        5. Select
        6. Produce Recommendation
    
    Each stage produces observable artifacts.
    """
    
    # Identity
    pipeline_id: str                        # Unique identifier
    
    # Pipeline stages (in order)
    executed_steps: Tuple[str, ...] = ()    # Stage names in order
    step_results: Dict[str, Any] = field(default_factory=dict)  # Results per stage
    
    # Input/Output
    input_alternatives: Tuple[str, ...] = ()
    output_alternative: Optional[str] = None
    
    # Evaluation metrics
    evaluation_summary: Dict[str, float] = field(default_factory=dict)
    
    # Timing
    started_at_utc: float = field(default_factory=time.time)
    completed_at_utc: Optional[float] = None
    
    @property
    def is_completed(self) -> bool:
        """Check if pipeline completed successfully."""
        return "produce_recommendation" in self.executed_steps and self.output_alternative is not None
    
    @classmethod
    def create(cls, alternatives: List[str]) -> DeliberationPipeline:
        """Create a new deliberation pipeline."""
        return cls(
            pipeline_id=f"pipeline:{uuid.uuid4().hex[:16]}",
            input_alternatives=tuple(alternatives),
        )


def dataclass_replace(instance: Any, **kwargs: Any) -> Any:
    """Simple dataclass replace helper for frozen instances."""
    return instance.__class__(**{**instance.__dict__, **kwargs})


__all__ = [
    "Deliberation", 
    "DeliberationPipeline",
]