# Effect Propagation - Phase 7.5
# ==============================

"""
Canonical Effect Propagation.

Effects propagate through mechanisms according to causal rules.
"""

from __future__ import annotations

import time
import uuid
from dataclasses import dataclass, field
from typing import Dict, List, Tuple, Set, Optional, Any
from enum import Enum, auto


@dataclass(frozen=True)
class PropagationStep:
    """
    A single step in effect propagation.
    
    Shows how effects move from one state to another through mechanisms.
    """
    
    # Identity
    step_id: str                        # Unique step identifier
    
    # State at this step
    current_state: str                  # The state being propagated from
    
    # Mechanism that activates
    activated_mechanism: str            # Which mechanism is triggered?
    
    # Resulting effects
    resulting_effects: Tuple[str, ...]  # Effects produced by this step
    
    # Timestamp of propagation
    timestamp_utc: float = field(default_factory=time.time)
    
    @property
    def effect_count(self) -> int:
        """Number of effects produced at this step."""
        return len(self.resulting_effects)


@dataclass(frozen=True)
class EffectPropagation:
    """
    A complete path of effect propagation through mechanisms.
    
    Shows how a cause leads to an effect through intermediate states.
    """
    
    # Identity
    propagation_id: str                 # Unique propagation identifier
    
    # Originating event/state
    originating_event: str              # The initial cause
    
    # Propagation steps (ordered)
    propagation_steps: Tuple[PropagationStep, ...]  # Ordered path
    
    # Final effects
    final_effects: Tuple[str, ...]      # Ultimate consequences
    
    # Path information
    total_steps: int = 0                # Number of intermediate steps
    max_depth_reached: int = 0          # Deepest propagation reached
    
    # Provenance
    created_at_utc: float = field(default_factory=time.time)
    source_descriptor_id: Optional[str] = None
    
    @property
    def path_length(self) -> int:
        """Total number of steps in the propagation."""
        return len(self.propagation_steps)
    
    def get_effect_at_step(self, step_index: int) -> Tuple[str, ...]:
        """Get effects produced at a specific step index."""
        if 0 <= step_index < len(self.propagation_steps):
            return self.propagation_steps[step_index].resulting_effects
        return ()


@dataclass(frozen=True)
class PropagationPipeline:
    """
    A complete propagation pipeline with all stages.
    
    From initial cause to final effects, through intermediate states.
    """
    
    # Identity
    pipeline_id: str                    # Unique pipeline identifier
    
    # Pipeline stages
    input_events: Tuple[str, ...]       # Initial events/conditions
    activated_mechanisms: Tuple[str, ...]  # Mechanisms that fire
    intermediate_states: Tuple[str, ...]   # Intermediate states
    final_effects: Tuple[str, ...]      # Final consequences
    
    # Validation status
    validation_status: str = "pending"  # "valid", "invalid", "incomplete"
    
    # Provenance
    created_at_utc: float = field(default_factory=time.time)
    source_descriptor_id: Optional[str] = None


@dataclass(frozen=True)
class PropagationTrace:
    """
    A trace of effect propagation for debugging and verification.
    """
    
    # Identity
    trace_id: str                       # Unique trace identifier
    
    # Complete propagation path
    propagation_path: Tuple[PropagationStep, ...]
    
    # All states encountered
    all_states: Tuple[str, ...]         # All states in the path
    
    # Verification data
    verification_status: str = "verified"  # "verified", "incomplete"
    
    @property
    def is_complete(self) -> bool:
        """Check if propagation trace is complete."""
        return self.verification_status == "verified"


def make_effect_propagation(
    originating_event: str,
    steps: List[PropagationStep],
    final_effects: Tuple[str, ...],
) -> EffectPropagation:
    """Create a new effect propagation."""
    steps_tuple = tuple(steps)
    total_steps = len(steps_tuple)
    max_depth = max((i for i in range(total_steps)), default=0)
    
    return EffectPropagation(
        propagation_id=f"propagation:{uuid.uuid4().hex[:16]}",
        originating_event=originating_event,
        propagation_steps=steps_tuple,
        final_effects=final_effects,
        total_steps=total_steps,
        max_depth_reached=max_depth,
    )


def make_propagation_pipeline(
    pipeline_name: str,
    input_events: Tuple[str, ...],
    activated_mechanisms: Tuple[str, ...],
    intermediate_states: Tuple[str, ...],
    final_effects: Tuple[str, ...],
) -> PropagationPipeline:
    """Create a new propagation pipeline."""
    return PropagationPipeline(
        pipeline_id=f"pipeline:{uuid.uuid4().hex[:16]}",
        input_events=input_events,
        activated_mechanisms=activated_mechanisms,
        intermediate_states=intermediate_states,
        final_effects=final_effects,
    )


__all__ = [
    "PropagationStep",
    "EffectPropagation",
    "PropagationPipeline",
    "PropagationTrace",
]