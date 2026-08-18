# Execution Reasoning Adaptation - Phase 7.21
# ============================================

"""
Canonical Execution Adaptation for Phase 7.21.

Execution adaptation evaluates environmental changes, execution feedback,
resource failures, partial completion, and policy updates.
"""

from __future__ import annotations

import time
import uuid
from dataclasses import dataclass, field
from typing import Dict, List, Tuple, Optional, Any
from enum import Enum, auto


class AdaptationTrigger(Enum):
    """Triggers for execution adaptation."""
    
    ENVIRONMENT_CHANGE = "environment_change"   # External environment changed
    RESOURCE_FAILURE = "resource_failure"        # Resource became unavailable
    EXECUTION_FEEDBACK = "execution_feedback"    # Execution results indicated need for change
    PARTIAL_COMPLETION = "partial_completion"    # Some commands completed, others failed
    POLICY_UPDATE = "policy_update"              # Policy changed during execution


class AdaptationStrategy(Enum):
    """Strategies for adapting execution."""
    
    RESTART = "restart"                         # Restart from checkpoint
    RESUME = "resume"                          # Resume from current state
    RERUN_FAILED = "rerun_failed"              # Rerun only failed commands
    SKIP_FAILED = "skip_failed"                # Skip failed commands
    REDUCE_SCOPE = "reduce_scope"              # Reduce execution scope


@dataclass(frozen=True)
class ExecutionAdaptationPipeline:
    """
    Pipeline for execution adaptation decisions.
    
    Adaptation evaluates:
        - Environmental changes
        - Execution feedback
        - Resource failures
        - Partial completion
        - Policy updates
    
    Adaptation remains explicit and inspectable.
    """
    
    # Identity
    adaptation_identity: str                    # Unique adaptation identifier
    
    # Triggering conditions
    triggering_conditions: Tuple[str, ...]
    
    # Adaptation policy
    adaptation_strategy: AdaptationStrategy
    
    # Resulting execution state
    resulting_execution_state: str             # e.g., "recovered", "rolled_back"
    
    # Provenance
    created_at_utc: float = field(default_factory=time.time)
    
    @classmethod
    def create(
        cls,
        triggering_conditions: Tuple[str, ...],
        adaptation_strategy: AdaptationStrategy = AdaptationStrategy.RESTART,
        resulting_execution_state: str = "recovered",
    ) -> ExecutionAdaptationPipeline:
        """Create a new execution adaptation pipeline."""
        return cls(
            adaptation_identity=f"adapt:{uuid.uuid4().hex[:16]}",
            triggering_conditions=triggering_conditions,
            adaptation_strategy=adaptation_strategy,
            resulting_execution_state=resulting_execution_state,
        )


@dataclass(frozen=True)
class AdaptedExecutionState:
    """
    State after an adaptation decision.
    
    Represents the updated execution configuration after adaptation.
    """
    
    # Identity
    state_identity: str
    
    # Previous state reference
    previous_state_id: str                      # ID of the state before adaptation
    
    # New configuration
    new_command_sequence: Tuple[str, ...]      # Updated command sequence
    new_constraints: Tuple[str, ...] = ()       # Updated constraints
    
    @classmethod
    def create(
        cls,
        previous_state_id: str,
        new_command_sequence: Tuple[str, ...],
        new_constraints: Tuple[str, ...] = (),
    ) -> AdaptedExecutionState:
        """Create a new adapted execution state."""
        return cls(
            state_identity=f"adapted_state:{uuid.uuid4().hex[:16]}",
            previous_state_id=previous_state_id,
            new_command_sequence=new_command_sequence,
            new_constraints=new_constraints,
        )


def dataclass_replace(instance: Any, **kwargs: Any) -> Any:
    """Simple dataclass replace helper for frozen instances."""
    return instance.__class__(**{**instance.__dict__, **kwargs})


__all__ = [
    "ExecutionAdaptationPipeline",
    "AdaptationTrigger",
    "AdaptationStrategy",
    "AdaptedExecutionState",
]