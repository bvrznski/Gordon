# Counterfactual Failure - Phase 7.6
# ==================================

"""
Counterfactual failure handling and diagnostics.

Failures include:
    - Invalid intervention (malformed or impossible)
    - Unknown mechanisms (causal model gaps)
    - Inconsistent causal model (logical contradictions)
    - Branch explosion (too many worlds generated)
    - Resource exhaustion (time/memory limits)

All failures remain explicit for inspection.
"""

from __future__ import annotations

import time
import uuid
from dataclasses import dataclass, field
from typing import Dict, List, Tuple, Optional, Any
from enum import Enum, auto


@dataclass(frozen=True)
class CounterfactualFailure:
    """
    A failure that occurred during counterfactual reasoning.
    
    Failures include invalid interventions, unknown mechanisms,
    inconsistent causal models, branch explosion, and resource exhaustion.
    
    All failures remain explicit and identifiable.
    """
    
    # Identity
    failure_id: str                           # Unique failure identifier
    
    # Failure type
    failure_kind: FailureKind                 # What kind of failure?
    
    # Diagnostics (what went wrong)
    diagnostics: str                          # Detailed explanation
    
    # Recovery options (if any)
    recovery_options: Tuple[str, ...] = ()    # How might we recover?
    
    # Provenance
    created_at_utc: float = field(default_factory=time.time)
    
    @classmethod
    def create(
        cls,
        failure_kind: FailureKind,
        diagnostics: str,
    ) -> CounterfactualFailure:
        """Create a new counterfactual failure."""
        return cls(
            failure_id=f"failure:{uuid.uuid4().hex[:16]}",
            failure_kind=failure_kind,
            diagnostics=diagnostics,
        )
    
    def with_recovery_option(self, option: str) -> CounterfactualFailure:
        """Return a copy with an additional recovery option."""
        return dataclass_replace(
            self,
            recovery_options=self.recovery_options + (option,),
        )


class FailureKind(Enum):
    """Kinds of counterfactual failures."""
    
    INVALID_INTERVENTION = "invalid_intervention"
    UNKNOWN_MECHANISM = "unknown_mechanism"
    INCONSISTENT_CAUSAL_MODEL = "inconsistent_causal_model"
    BRANCH_EXPLOSION = "branch_explosion"
    RESOURCE_EXHAUSTED = "resource_exhausted"
    INVALID_BRANCH_ANCESTRY = "invalid_branch_ancestry"
    DIVERGENCE_ERROR = "divergence_error"


@dataclass(frozen=True)
class FailureMode:
    """
    A failure mode that can occur during counterfactual reasoning.
    
    Failure modes define what can go wrong and how to detect them.
    """
    
    # Failure identifier
    failure_id: str                           # Unique failure mode identifier
    
    # Mode name
    failure_name: str                         # e.g., "Branch Explosion"
    
    # Description
    failure_description: str                  # What is this failure?
    
    # Triggers (conditions that cause the failure)
    trigger_conditions: Tuple[str, ...] = ()  # e.g., ["branch_count > max", "depth > limit"]
    
    # Observable symptoms
    observable_symptoms: Tuple[str, ...] = () # How can we detect it?
    
    # Severity (low, medium, high, critical)
    severity: str = "medium"
    
    @classmethod
    def create(
        cls,
        failure_name: str,
        failure_description: str,
    ) -> FailureMode:
        """Create a new failure mode."""
        return cls(
            failure_id=f"failure_mode:{uuid.uuid4().hex[:16]}",
            failure_name=failure_name,
            failure_description=failure_description,
        )


def dataclass_replace(instance: Any, **kwargs: Any) -> Any:
    """Simple dataclass replace helper for frozen instances."""
    return instance.__class__(**{**instance.__dict__, **kwargs})


__all__ = [
    "CounterfactualFailure",
    "FailureKind",
    "FailureMode",
]