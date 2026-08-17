# Intervention Analysis - Phase 7.5
# =================================

"""
Canonical Intervention Analysis.

Interventions are hypothetical modifications to systems that we want to analyze.
"""

from __future__ import annotations

import time
import uuid
from dataclasses import dataclass, field
from typing import Dict, List, Tuple, Set, Optional, Any
from enum import Enum, auto


@dataclass(frozen=True)
class Intervention:
    """
    A hypothetical intervention on a system.
    
    Interventions remain hypothetical until explicitly executed elsewhere.
    They never modify the World Model directly during causal reasoning.
    """
    
    # Identity
    intervention_id: str                # Unique intervention identifier
    
    # Modified variables
    modified_variables: Tuple[str, ...]  # Variables that are干预 (intervened)
    
    # Intervention values (if known)
    variable_values: Dict[str, Any] = field(default_factory=dict)  # value per variable
    
    # Protected variables (cannot be modified by this intervention)
    protected_variables: Tuple[str, ...] = ()
    
    # Provenance
    created_at_utc: float = field(default_factory=time.time)
    source_descriptor_id: Optional[str] = None
    
    def get_modified_value(self, variable: str) -> Optional[Any]:
        """Get the modified value for a variable."""
        return self.variable_values.get(variable)


@dataclass(frozen=True)
class InterventionAnalysis:
    """
    Full analysis of an intervention's effects.
    
    Includes predicted effects and affected mechanisms.
    """
    
    # Identity
    analysis_id: str                    # Unique analysis identifier
    
    # The intervention being analyzed
    intervention: Intervention          # The hypothetical intervention
    
    # Predicted effects
    predicted_effects: Tuple[str, ...]  # Effects we predict will occur
    
    # Affected mechanisms
    affected_mechanisms: Tuple[str, ...]  # Mechanisms that would be involved
    
    # Confidence in predictions
    confidence: float = 1.0             # Prediction confidence (0-1)
    
    # Side effects
    side_effects: Tuple[str, ...] = ()  # Unintended consequences
    
    # Provenance
    created_at_utc: float = field(default_factory=time.time)
    source_descriptor_id: Optional[str] = None
    
    @property
    def is_harmless(self) -> bool:
        """Check if intervention has no harmful side effects."""
        return len(self.side_effects) == 0


@dataclass(frozen=True)
class InterventionSet:
    """
    A set of interventions to analyze together.
    
    Used for comparing multiple interventions.
    """
    
    # Identity
    intervention_set_id: str            # Unique set identifier
    
    # Interventions in the set
    interventions: Tuple[Intervention, ...]
    
    # Constraints on intervention combinations
    constraints: Tuple[str, ...] = ()   # e.g., "mutually_exclusive", "must_include_one"
    
    @property
    def intervention_count(self) -> int:
        """Number of interventions in the set."""
        return len(self.interventions)


def make_intervention(
    name: str,
    modified_variables: Tuple[str, ...],
    variable_values: Dict[str, Any] = None,
    protected_variables: Tuple[str, ...] = (),
) -> Intervention:
    """Create a new intervention."""
    if variable_values is None:
        variable_values = {}
    
    return Intervention(
        intervention_id=f"intervention:{uuid.uuid4().hex[:16]}",
        modified_variables=modified_variables,
        variable_values=variable_values,
        protected_variables=protected_variables,
    )


def make_intervention_analysis(
    intervention: Intervention,
    predicted_effects: Tuple[str, ...],
    affected_mechanisms: Tuple[str, ...],
    confidence: float = 1.0,
    side_effects: Tuple[str, ...] = (),
) -> InterventionAnalysis:
    """Create a new intervention analysis."""
    return InterventionAnalysis(
        analysis_id=f"analysis:{uuid.uuid4().hex[:16]}",
        intervention=intervention,
        predicted_effects=predicted_effects,
        affected_mechanisms=affected_mechanisms,
        confidence=confidence,
        side_effects=side_effects,
    )


__all__ = [
    "Intervention",
    "InterventionAnalysis",
    "InterventionSet",
]