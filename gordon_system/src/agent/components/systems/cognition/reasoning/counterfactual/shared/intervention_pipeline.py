# Intervention Pipeline - Phase 7.6
# ================================

"""
Intervention semantics for counterfactual reasoning.

Counterfactual interventions:
    - Remain hypothetical (never executed)
    - Modify specific variables in the reference world
    - Trigger causal propagation to generate alternative worlds
    - Are explicitly traceable and inspectable
"""

from __future__ import annotations

import time
import uuid
from dataclasses import dataclass, field
from typing import Dict, List, Tuple, Optional, Any


@dataclass(frozen=True)
class CounterfactualIntervention:
    """
    A hypothetical intervention applied to the reference world.
    
    An intervention:
        - Is purely hypothetical (never actually executed)
        - Modifies specific variables in the world state
        - Has a clear scope and activation point
        - Preserves complete provenance
    
    Examples of interventions:
        - "Component never failed"
        - "User clicked another button"
        - "Network remained available"
        - "Memory increased by 50%"
    """
    
    # Identity
    intervention_id: str                      # Unique intervention identifier
    
    # What was modified
    modified_variables: Dict[str, Any] = field(default_factory=dict)  # var_name -> new_value
    
    # Intervention scope
    intervention_scope: Tuple[str, ...] = ()  # Scope identifiers (e.g., "component_a", "user_session_123")
    
    # When the intervention takes effect
    activation_point: Optional[str] = None    # e.g., "before_event_x", "at_time_t"
    
    # Provenance
    created_at_utc: float = field(default_factory=time.time)
    source_descriptor_id: Optional[str] = None
    
    @classmethod
    def create(
        cls,
        modified_variables: Dict[str, Any],
        intervention_scope: Tuple[str, ...] = (),
        activation_point: Optional[str] = None,
    ) -> CounterfactualIntervention:
        """Create a new counterfactual intervention."""
        return cls(
            intervention_id=f"intervention:{uuid.uuid4().hex[:16]}",
            modified_variables=modified_variables,
            intervention_scope=intervention_scope,
            activation_point=activation_point,
        )
    
    def is_hypothetical(self) -> bool:
        """Interventions are always hypothetical - a fundamental invariant."""
        return True


@dataclass(frozen=True)
class InterventionPipeline:
    """
    Pipeline for applying interventions to generate alternative worlds.
    
    Pipeline flow:
        Reference State → Variable Modification → Mechanism Activation → Propagation → Alternative Outcome
    
    The pipeline executes conceptually - no actual mechanism is modified or executed.
    """
    
    # Identity
    pipeline_id: str                          # Unique pipeline identifier
    
    # Intervention being applied
    intervention: CounterfactualIntervention
    
    # Modified variables (before and after)
    modified_variables: Dict[str, Tuple[Any, Any]] = field(default_factory=dict)  # var -> (before, after)
    
    # Propagation tracking
    propagation_trace: Tuple[str, ...] = ()   # Mechanisms affected by propagation
    
    # Provenance
    created_at_utc: float = field(default_factory=time.time)
    
    @classmethod
    def create(
        cls,
        intervention: CounterfactualIntervention,
    ) -> InterventionPipeline:
        """Create a new intervention pipeline."""
        return cls(
            pipeline_id=f"intervention_pipeline:{uuid.uuid4().hex[:16]}",
            intervention=intervention,
            modified_variables={},
            propagation_trace=(),
        )
    
    def add_modification(self, var_name: str, before_value: Any, after_value: Any) -> InterventionPipeline:
        """Return a copy with a variable modification added."""
        new_mods = dict(self.modified_variables)
        new_mods[var_name] = (before_value, after_value)
        return dataclass_replace(
            self,
            modified_variables=new_mods,
        )
    
    def add_propagation_step(self, step: str) -> InterventionPipeline:
        """Return a copy with a propagation trace step added."""
        return dataclass_replace(
            self,
            propagation_trace=self.propagation_trace + (step,),
        )


def dataclass_replace(instance: Any, **kwargs: Any) -> Any:
    """Simple dataclass replace helper for frozen instances."""
    return instance.__class__(**{**instance.__dict__, **kwargs})


__all__ = [
    "CounterfactualIntervention",
    "InterventionPipeline",
]