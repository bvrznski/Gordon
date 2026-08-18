# Homeostasis Management - Phase 7.26
# ====================================

"""
Canonical Homeostasis Management.

Homeostasis evaluates resource balance, execution pressure, reasoning load,
memory utilization, and communication load to determine cognitive equilibrium.
"""

from __future__ import annotations

import uuid
import time
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any
from enum import Enum, auto


@dataclass(frozen=True)
class HomeostasisVariable:
    """
    A monitored variable in homeostasis evaluation.
    
    Variables include:
        - Resource utilization metrics (CPU, memory, etc.)
        - Execution pressure indicators
        - Reasoning load measures
        - Memory utilization stats
        - Communication load metrics
    """
    
    variable_id: str
    variable_name: str                    # Human-readable name
    current_value: float                  # Current measured value
    target_value: Optional[float] = None  # Target for equilibrium (None = no specific target)
    min_acceptable: Optional[float] = None   # Below this is problematic
    max_acceptable: Optional[float] = None   # Above this is problematic
    
    @property
    def deviation(self) -> float:
        """Calculate deviation from target."""
        if self.target_value is None:
            return 0.0
        return abs(self.current_value - self.target_value)
    
    def is_within_acceptable_range(self) -> bool:
        """Check if current value is within acceptable bounds."""
        if self.min_acceptable is not None and self.current_value < self.min_acceptable:
            return False
        if self.max_acceptable is not None and self.current_value > self.max_acceptable:
            return False
        return True


@dataclass(frozen=True)
class EquilibriumModel:
    """
    Model defining equilibrium metrics for homeostasis.
    
    Defines how variables interact to determine overall system equilibrium.
    """
    
    model_id: str
    model_name: str
    
    # Weighting of each variable type
    resource_weight: float = 1.0
    execution_weight: float = 1.0
    reasoning_weight: float = 1.0
    memory_weight: float = 1.0
    communication_weight: float = 1.0
    
    # Equilibrium thresholds
    acceptable_deviation_threshold: float = 0.1  # 10% deviation is acceptable


@dataclass(frozen=True)
class HomeostasisManagement:
    """
    Homeostasis management evaluates system equilibrium.
    
    Evaluates:
        - Resource equilibrium (CPU, memory, I/O)
        - Execution pressure (task queue length, pending operations)
        - Reasoning stability (reasoning load, hypothesis count)
        - Memory utilization (active memory, cache hit rates)
        - Communication load (message queue depth, latency)
    
    Homeostasis remains explicit and inspectable.
    """
    
    management_id: str
    homeostasis_identity: str
    
    # Monitored variables
    monitored_variables: List[HomeostasisVariable] = field(default_factory=list)
    
    # Equilibrium model
    equilibrium_model: Optional[EquilibriumModel] = None
    
    # Stability metrics
    stability_score: float = 1.0  # 0.0 to 1.0, where 1.0 is perfectly stable
    
    # Provenance
    provenance: str = "unknown"
    
    # Timing
    evaluated_at_utc: float = field(default_factory=time.time)
    
    @property
    def overall_deviation(self) -> float:
        """Calculate overall deviation from equilibrium."""
        if not self.monitored_variables:
            return 0.0
        
        total_deviation = sum(v.deviation for v in self.monitored_variables)
        return total_deviation / len(self.monitored_variables)
    
    @property
    def is_in_equilibrium(self) -> bool:
        """Check if system is in equilibrium."""
        if not self.monitored_variables:
            return True
        
        # All variables must be within acceptable range
        for v in self.monitored_variables:
            if not v.is_within_acceptable_range():
                return False
        
        return self.stability_score >= 0.8
    
    def to_stabilization_candidates(self) -> List[Dict[str, Any]]:
        """Convert homeostasis assessment to stabilization candidates."""
        candidates = []
        
        for variable in self.monitored_variables:
            if not variable.is_within_acceptable_range():
                candidate = {
                    "candidate_identity": f"homeo:{variable.variable_name}",
                    "stabilization_type": "resource_redistribution",
                    "expected_effect": f"Bring {variable.variable_name} within acceptable range",
                    "reversibility": "high",
                    "provenance": self.provenance,
                }
                candidates.append(candidate)
        
        return candidates
    
    @classmethod
    def create(
        cls,
        homeostasis_identity: str,
        monitored_variables: List[HomeostasisVariable],
        equilibrium_model: Optional[EquilibriumModel] = None,
        provenance: str = "unknown",
    ) -> HomeostasisManagement:
        """Create a new homeostasis management assessment."""
        
        # Calculate stability score
        total_deviation = sum(v.deviation for v in monitored_variables)
        avg_deviation = total_deviation / len(monitored_variables) if monitored_variables else 0.0
        
        # Score based on deviation (less deviation = higher score)
        stability_score = max(0.0, min(1.0, 1.0 - avg_deviation))
        
        return cls(
            management_id=f"homeo:{uuid.uuid4().hex[:16]}",
            homeostasis_identity=homeostasis_identity,
            monitored_variables=monitored_variables,
            equilibrium_model=equilibrium_model,
            stability_score=stability_score,
            provenance=provenance,
        )


__all__ = [
    "HomeostasisManagement",
    "HomeostasisVariable",
    "EquilibriumModel",
]