# System Set - Phase 7.38
# =======================

"""
Canonical System Set.

System Sets define:
    - system boundaries
    - participating components
    - interaction assumptions
    - environment
    - analysis constraints

System Sets remain immutable during reasoning.
"""

from __future__ import annotations

import time
import uuid
from dataclasses import dataclass, field
from typing import Dict, List, Tuple, Optional, Any
from enum import Enum, auto


@dataclass(frozen=True)
class ComponentModel:
    """
    Model of a system component.
    
    Each component is characterized by:
        - Identity and classification
        - Internal state representation
        - Behavior specification
        - Interfaces for interaction
    """
    
    # Identity
    component_id: str                           # Unique component identifier
    component_name: str                         # Human-readable name
    
    # Classification
    component_type: str = "general"             # e.g., "actor", "process", "device"
    role_in_system: Optional[str] = None        # e.g., "controller", "sensor", "actuator"
    
    # State representation
    state_space: Optional[List[str]] = None     # List of state variables
    initial_state: Dict[str, Any] = field(default_factory=dict)
    
    # Behavior specification
    behavior_model: Optional[str] = None        # Description or reference to behavior spec
    
    # Interfaces
    input_interfaces: List[str] = field(default_factory=list)   # Inputs from environment
    output_interfaces: List[str] = field(default_factory=list)  # Outputs to environment


@dataclass(frozen=True)
class InteractionAssumption:
    """
    Assumptions about interactions between components.
    
    Defines the interaction semantics:
        - Type of interaction (communication, resource, control)
        - Directionality
        - Constraints and invariants
    """
    
    # Identity
    assumption_id: str                          # Unique identifier
    
    # Interaction characteristics
    source_component: str                       # Source component ID
    target_component: str                       # Target component ID
    interaction_type: str = "general"           # e.g., "communication", "resource", "control"
    
    # Directionality and constraints
    bidirectional: bool = False                 # Is interaction symmetric?
    strength: float = 1.0                       # Interaction strength [0, 1]
    
    # Invariants and constraints
    min_frequency: Optional[float] = None       # Minimum interaction rate
    max_frequency: Optional[float] = None       # Maximum interaction rate
    reliability: float = 1.0                    # Communication reliability


@dataclass(frozen=True)
class SystemSet:
    """
    Immutable set of components and assumptions for systems reasoning.
    
    A system set defines the complete scope of a systems reasoning session:
        - Boundary definition (which components are inside/outside)
        - Component inventory with models
        - Interaction assumptions
        - Environment context
        - Analysis constraints
    
    The system set remains immutable during reasoning to ensure deterministic results.
    """
    
    # Identity
    system_set_id: str                          # Unique identifier for this set
    
    # Scope definition
    system_name: str                            # Human-readable system name
    system_boundary: List[str]                  # Component IDs inside the boundary
    external_components: List[str] = field(default_factory=list)  # Outside components
    
    # Component inventory
    component_models: Dict[str, ComponentModel] = field(default_factory=dict)
    
    # Interaction assumptions
    interaction_assumptions: List[InteractionAssumption] = field(default_factory=list)
    
    # Environment context
    environment_context: Optional[Dict[str, Any]] = None
    
    # Analysis constraints
    analysis_constraints: Dict[str, Any] = field(default_factory=dict)  # e.g., "max_interactions": 100
    
    # Provenance
    created_at_utc: float = field(default_factory=time.time)
    source_descriptor_id: Optional[str] = None
    
    @classmethod
    def create(
        cls,
        system_name: str,
        component_ids: List[str],
        assumptions: Optional[List[InteractionAssumption]] = None,
        environment_context: Optional[Dict[str, Any]] = None,
    ) -> SystemSet:
        """Create a new system set."""
        return cls(
            system_set_id=f"systemset:{uuid.uuid4().hex[:16]}",
            system_name=system_name,
            system_boundary=component_ids,
            component_models={
                cid: ComponentModel(component_id=cid, component_name=cid)
                for cid in component_ids
            },
            interaction_assumptions=assumptions or [],
            environment_context=environment_context,
        )
    
    def add_component(self, component_model: ComponentModel) -> SystemSet:
        """Return a new system set with the component added."""
        new_models = dict(self.component_models)
        new_models[component_model.component_id] = component_model
        return dataclass_replace(
            self,
            component_models=new_models,
        )
    
    def add_assumption(self, assumption: InteractionAssumption) -> SystemSet:
        """Return a new system set with the assumption added."""
        return dataclass_replace(
            self,
            interaction_assumptions=self.interaction_assumptions + [assumption],
        )


def dataclass_replace(instance: Any, **kwargs: Any) -> Any:
    """Simple dataclass replace helper for frozen instances."""
    # For Python 3.12+, use dataclasses.replace
    # This is a simple implementation for compatibility
    return instance.__class__(**{**instance.__dict__, **kwargs})


__all__ = [
    "SystemSet",
    "ComponentModel",
    "InteractionAssumption",
]