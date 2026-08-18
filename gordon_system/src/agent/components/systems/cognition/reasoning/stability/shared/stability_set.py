# Stability Set - Phase 7.26
# ===========================

"""
Canonical Stability Set.

A stability set defines the monitored subsystems and their stability constraints.
"""

from __future__ import annotations

import uuid
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any
from enum import Enum, auto


class SubsystemKind(Enum):
    """Kinds of monitored subsystems."""
    
    MEMORY = "memory"
    EXECUTION = "execution"
    REASONING = "reasoning"
    COMMUNICATION = "communication"
    RESOURCE_MANAGEMENT = "resource_management"


@dataclass(frozen=True)
class StabilityConstraint:
    """
    A stability constraint defines acceptable operational bounds for a subsystem.
    
    Constraints include:
        - Thresholds for monitored variables
        - Maximum tolerable degradation
        - Required containment policies
        - Recovery constraints
    """
    
    constraint_id: str
    subsystem_kind: SubsystemKind
    variable_name: str                    # The variable being constrained
    min_value: Optional[float] = None     # Lower bound (None = no lower bound)
    max_value: Optional[float] = None     # Upper bound (None = no upper bound)
    critical_threshold: Optional[float] = None  # If exceeded, immediate containment required
    
    def is_within_bounds(self, value: float) -> bool:
        """Check if a value is within acceptable bounds."""
        if self.min_value is not None and value < self.min_value:
            return False
        if self.max_value is not None and value > self.max_value:
            return False
        return True
    
    def is_critical(self, value: float) -> bool:
        """Check if a value exceeds critical threshold."""
        if self.critical_threshold is None:
            return False
        return value > self.critical_threshold


@dataclass(frozen=True)
class StabilitySet:
    """
    A stability set defines the complete scope of stability reasoning.
    
    A stability set includes:
        - Monitored subsystems and their states
        - Stability constraints for each subsystem
        - Operational scope (which parts are being analyzed)
        - Containment policies to be applied when needed
    
    Stability Sets remain immutable during reasoning to ensure deterministic
    analysis results.
    """
    
    stability_set_id: str                         # Unique identifier
    participating_subsystems: List[SubsystemKind]  # Which subsystems are monitored?
    operational_scope: str                        # Scope of the analysis (e.g., "global", "session_123")
    
    # Constraints for each subsystem
    constraints: Dict[SubsystemKind, List[StabilityConstraint]] = field(default_factory=dict)
    
    # Containment policies
    containment_policy: Optional[str] = None      # Name of containment policy to apply
    
    # Provenance
    provenance: str = "unknown"                   # Source of this stability set
    
    def get_constraints(self, subsystem_kind: SubsystemKind) -> List[StabilityConstraint]:
        """Get constraints for a specific subsystem kind."""
        return self.constraints.get(subsystem_kind, [])
    
    def add_constraint(self, constraint: StabilityConstraint) -> StabilitySet:
        """Return a new StabilitySet with the added constraint."""
        constraints = dict(self.constraints)
        if constraint.subsystem_kind not in constraints:
            constraints[constraint.subsystem_kind] = []
        constraints[constraint.subsystem_kind].append(constraint)
        
        return dataclass_replace(
            self,
            constraints=constraints,
        )
    
    @classmethod
    def create(
        cls,
        operational_scope: str,
        participating_subsystems: List[SubsystemKind],
        containment_policy: Optional[str] = None,
        provenance: str = "unknown",
    ) -> StabilitySet:
        """Create a new stability set."""
        return cls(
            stability_set_id=f"stability-set:{uuid.uuid4().hex[:16]}",
            operational_scope=operational_scope,
            participating_subsystems=participating_subsystems,
            containment_policy=containment_policy,
            provenance=provenance,
        )


def dataclass_replace(instance: Any, **kwargs: Any) -> Any:
    """Simple dataclass replace helper for frozen instances."""
    return instance.__class__(**{**instance.__dict__, **kwargs})


__all__ = [
    "StabilitySet",
    "StabilityConstraint",
    "SubsystemKind",
]