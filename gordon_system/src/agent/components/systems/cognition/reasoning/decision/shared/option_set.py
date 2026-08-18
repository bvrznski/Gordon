# Decision Option Set - Phase 7.19
# =================================

"""
Canonical Decision Option Set Contract.

Option Sets define the candidate options for a decision.
"""

from __future__ import annotations

import time
import uuid
from dataclasses import dataclass, field
from typing import Dict, List, Tuple, Optional, Any
from enum import Enum, auto


@dataclass(frozen=True)
class DecisionOption:
    """
    A decision option representing a candidate commitment.
    
    Options remain explicit; they never imply selection automatically.
    """
    
    # Identity
    option_id: str                          # Unique identifier
    
    # Option details
    option_description: str                 # Human-readable description
    expected_utility: float = 0.0           # Expected utility value
    
    # Constraints
    constraints: Tuple[str, ...] = ()       # Explicit constraints
    hard_constraints_violated: bool = False # Are hard constraints violated?
    
    # Provenance
    created_at_utc: float = field(default_factory=time.time)
    provenance: Dict[str, str] = field(default_factory=dict)


@dataclass(frozen=True)
class OptionSet:
    """
    A set of decision options for evaluation.
    
    Option Sets define:
        - candidate options
        - evaluation constraints
        - decision policies
        - resource limits
        - termination criteria
    
    Option Sets remain immutable during evaluation.
    """
    
    # Identity
    option_set_id: str                      # Unique identifier
    
    # Options
    participating_options: Tuple[DecisionOption, ...]  # All candidate options
    
    # Decision scope
    decision_scope: str = "unknown"         # What is being decided?
    evaluation_constraints: Tuple[str, ...] = ()        # Evaluation constraints
    
    # Resource limits
    max_time_seconds: float = 300.0         # Maximum evaluation time
    max_iterations: int = 100               # Maximum iterations
    
    # Termination criteria
    min_confidence_required: float = 0.85   # Minimum confidence for commitment
    utility_threshold: Optional[float] = None  # Utility must exceed this
    
    # Provenance
    created_at_utc: float = field(default_factory=time.time)
    provenance: Dict[str, str] = field(default_factory=dict)
    
    @property
    def option_count(self) -> int:
        """Count of options in the set."""
        return len(self.participating_options)
    
    @classmethod
    def create(
        cls,
        options: List[DecisionOption],
        decision_scope: str = "unknown",
        constraints: Optional[List[str]] = None,
    ) -> OptionSet:
        """Create a new option set."""
        return cls(
            option_set_id=f"option_set:{uuid.uuid4().hex[:16]}",
            participating_options=tuple(options),
            decision_scope=decision_scope,
            evaluation_constraints=tuple(constraints or []),
        )
    
    def with_option(self, option: DecisionOption) -> OptionSet:
        """Return a copy with an additional option."""
        new_options = list(self.participating_options)
        new_options.append(option)
        return dataclass_replace(
            self,
            participating_options=tuple(new_options),
        )
    
    def without_option(self, option_id: str) -> OptionSet:
        """Return a copy with an option removed."""
        new_options = tuple(o for o in self.participating_options if o.option_id != option_id)
        return dataclass_replace(
            self,
            participating_options=new_options,
        )


def dataclass_replace(instance: Any, **kwargs: Any) -> Any:
    """Simple dataclass replace helper for frozen instances."""
    return instance.__class__(**{**instance.__dict__, **kwargs})


__all__ = [
    "DecisionOption",
    "OptionSet",
]