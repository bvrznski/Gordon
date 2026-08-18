# Experimental Reasoning - Interventions
# =======================================

"""
Canonical Intervention contracts.

Interventions describe deliberate manipulations for experimental testing.
"""

from __future__ import annotations

import time
import uuid
from dataclasses import dataclass, field
from typing import Dict, List, Tuple, Optional, Any
from enum import Enum, auto


class InterventionType(Enum):
    """Types of interventions that can be applied in experiments."""
    
    PARAMETER_CHANGE = "parameter_change"           # Modify system parameters
    ENVIRONMENTAL_MODIFICATION = "environmental_modification"  # Change environment
    STIMULUS_PRESENTATION = "stimulus_presentation"  # Present specific stimuli
    TOOL_INVOCATION = "tool_invocation"             # Invoke external tools
    CONTROLLED_PERTURBATION = "controlled_perturbation"  # Apply controlled perturbations
    DATA_INPUT_MODIFICATION = "data_input_modification"  # Modify input data


@dataclass(frozen=True)
class InterventionTarget:
    """
    Target of an intervention.
    
    Specifies what will be modified by the intervention.
    """
    
    # Target identification
    target_id: str                              # Unique identifier for target
    target_type: str                            # e.g., "system_parameter", "environmental_variable"
    target_name: Optional[str] = None           # Human-readable name
    
    # Target location/context
    domain: str = "unknown"                     # Domain where target exists
    context: Dict[str, Any] = field(default_factory=dict)  # Additional context
    
    @classmethod
    def create(
        cls,
        target_type: str,
        target_name: Optional[str] = None,
        domain: str = "unknown",
        context: Optional[Dict[str, Any]] = None,
    ) -> InterventionTarget:
        """Create a new intervention target."""
        return cls(
            target_id=f"target:{uuid.uuid4().hex[:8]}",
            target_type=target_type,
            target_name=target_name,
            domain=domain,
            context=context or {},
        )


@dataclass(frozen=True)
class Intervention:
    """
    An intervention - a deliberate manipulation for experimental testing.
    
    Interventions include:
        - Target of the manipulation
        - Type of manipulation
        - Expected effect
        - Constraints and safety conditions
    
    Interventions remain explicit and never imply execution automatically.
    """
    
    # Identity
    intervention_id: str                        # Unique identifier
    semantic_identity: str                      # Stable identity across runs
    
    # Target
    target: InterventionTarget                  # What will be modified?
    
    # Intervention details
    intervention_type: InterventionType         # How will it be modified?
    intervention_value: Any = None              # The value to set/modify
    
    # Expected effect
    expected_effect: str                        # What do we expect to observe?
    effect_magnitude: Optional[float] = None    # Estimated magnitude (if applicable)
    
    # Constraints and safety
    constraints: Tuple[str, ...] = ()           # Precondition constraints
    safety_conditions: Tuple[str, ...] = ()     # Safety requirements
    
    # Provenance
    created_at_utc: float = field(default_factory=time.time)
    source_descriptor_id: Optional[str] = None   # If this is a refinement
    origin_context: str = "unknown"              # Where did intervention originate?
    
    @classmethod
    def create(
        cls,
        target: InterventionTarget,
        intervention_type: InterventionType,
        expected_effect: str,
        intervention_value: Any = None,
        constraints: Optional[Tuple[str, ...]] = None,
        safety_conditions: Optional[Tuple[str, ...]] = None,
        origin_context: str = "unknown",
    ) -> Intervention:
        """Create a new intervention."""
        return cls(
            intervention_id=f"intervention:{uuid.uuid4().hex[:16]}",
            semantic_identity=f"{target.target_id}:{intervention_type.value}",
            target=target,
            intervention_type=intervention_type,
            expected_effect=expected_effect,
            intervention_value=intervention_value,
            constraints=constraints or (),
            safety_conditions=safety_conditions or (),
            origin_context=origin_context,
        )


@dataclass(frozen=True)
class InterventionAnalysis:
    """
    Analysis of an intervention's properties.
    
    Intervention analysis evaluates:
        - Causal influence on the target system
        - Variable isolation quality
        - Safety and feasibility
        - Resource requirements
        - Expected effect magnitude
    
    Analysis remains explicit and inspectable.
    """
    
    # Identity
    analysis_id: str                            # Unique identifier
    intervention_identity: str                  # Identity of analyzed intervention
    
    # Analysis results
    causal_influence_score: float = 0.0         # How strongly does this affect the target?
    variable_isolation_quality: float = 0.0     # How isolated are the variables?
    safety_score: float = 1.0                   # Safety assessment (0-1, higher is safer)
    feasibility_score: float = 1.0              # Feasibility assessment (0-1, higher is more feasible)
    
    # Resource requirements
    estimated_resources: Dict[str, float] = field(default_factory=dict)  # e.g., "time": 3600, "compute": 2
    
    # Justification
    justification: str = ""                     # Why was this intervention selected?
    
    # Provenance
    created_at_utc: float = field(default_factory=time.time)
    origin_context: str = "unknown"
    
    @classmethod
    def create(
        cls,
        intervention_identity: str,
        origin_context: str = "unknown",
    ) -> InterventionAnalysis:
        """Create a new intervention analysis."""
        return cls(
            analysis_id=f"intervention_analysis:{uuid.uuid4().hex[:16]}",
            intervention_identity=intervention_identity,
            origin_context=origin_context,
        )
    
    @property
    def overall_score(self) -> float:
        """Calculate overall intervention score (weighted combination)."""
        # Simple weighted average
        weights = {
            "causal_influence": 0.2,
            "variable_isolation": 0.15,
            "safety": 0.3,
            "feasibility": 0.35,
        }
        return (
            self.causal_influence_score * weights["causal_influence"] +
            self.variable_isolation_quality * weights["variable_isolation"] +
            self.safety_score * weights["safety"] +
            self.feasibility_score * weights["feasibility"]
        )


__all__ = [
    "InterventionType",
    "InterventionTarget",
    "Intervention",
    "InterventionAnalysis",
]