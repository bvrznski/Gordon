# Scenario Exploration - Phase 7.15 Part 2
# ==========================================

"""
Canonical Scenario Contract.

Scenario exploration evaluates boundary conditions, constraint relaxation,
constraint tightening, environmental variation, and unknown regions.
"""

from __future__ import annotations

import time
import uuid
from dataclasses import dataclass, field
from typing import Dict, List, Tuple, Optional, Any
from enum import Enum, auto


class ScenarioEnvironmentKind(Enum):
    """Kinds of environmental conditions."""
    
    NORMAL = "normal"                         # Standard operating conditions
    BOUNDARY = "boundary"                     # Edge cases and limits
    STRESS = "stress"                        # High-stress or adverse conditions
    ADVERSARIAL = "adversarial"              # Adversarial or hostile conditions
    UNKNOWN = "unknown"                      # Undefined or missing conditions


@dataclass(frozen=True)
class ScenarioIdentity:
    """
    Immutable identity for a scenario.
    
    Allows tracking scenarios across sessions.
    """
    
    semantic_identity: str                    # Stable identity across runs
    
    @classmethod
    def create(cls, semantic_identity: str) -> ScenarioIdentity:
        """Create a new scenario identity."""
        return cls(semantic_identity=semantic_identity)


@dataclass(frozen=True)
class EnvironmentalCondition:
    """
    A specific environmental condition in a scenario.
    
    Defines the context within which hypotheses are evaluated.
    """
    
    # Identity
    condition_id: str                         # Unique identifier
    
    # Content
    condition_name: str                       # e.g., "temperature", "load"
    condition_value: float                    # Numeric value or threshold
    condition_type: str = "numeric"           # "numeric", "categorical", "range"
    
    # Scope
    scope: str = "default"                    # Where this applies
    
    @classmethod
    def create(
        cls,
        condition_name: str,
        condition_value: float,
        condition_type: str = "numeric",
        scope: str = "default",
    ) -> EnvironmentalCondition:
        """Create a new environmental condition."""
        return cls(
            condition_id=f"condition:{uuid.uuid4().hex[:16]}",
            condition_name=condition_name,
            condition_value=condition_value,
            condition_type=condition_type,
            scope=scope,
        )


@dataclass(frozen=True)
class HypotheticalScenario:
    """
    A scenario for hypothetical reasoning exploration.
    
    A scenario contains:
        - Participating hypotheses
        - Environmental conditions
        - Assumptions underpinning the scenario
        - Provenance tracking
    
    Scenarios remain explicit and inspectable at all times.
    """
    
    # Identity
    scenario_id: str                          # Unique identifier
    semantic_identity: str                    # Semantic identity (stable across runs)
    
    # Contents
    participating_hypotheses: Tuple[ScenarioIdentity, ...]  # Hypotheses in this scenario
    
    # Environment
    environmental_conditions: Tuple[EnvironmentalCondition, ...] = ()  # Conditions
    
    # Assumptions
    assumptions: Tuple[str, ...] = ()         # Underlying assumptions
    
    # Provenance
    source_descriptor_id: Optional[str] = None   # If from a descriptor
    origin_context: str = "unknown"              # Where did scenario originate?
    
    # Metadata
    created_at_utc: float = field(default_factory=time.time)
    
    @property
    def total_hypotheses(self) -> int:
        """Return number of hypotheses in scenario."""
        return len(self.participating_hypotheses)
    
    @classmethod
    def create(
        cls,
        semantic_identity: str,
        hypotheses: Optional[List[ScenarioIdentity]] = None,
        environmental_conditions: Optional[List[EnvironmentalCondition]] = None,
        assumptions: Optional[List[str]] = None,
        origin_context: str = "unknown",
    ) -> HypotheticalScenario:
        """Create a new scenario."""
        return cls(
            scenario_id=f"scenario:{uuid.uuid4().hex[:16]}",
            semantic_identity=semantic_identity,
            participating_hypotheses=tuple(hypotheses or []),
            environmental_conditions=tuple(environmental_conditions or []),
            assumptions=tuple(assumptions or []),
            origin_context=origin_context,
        )
    
    def with_environmental_condition(self, condition: EnvironmentalCondition) -> "HypotheticalScenario":
        """Return a copy with the environmental condition added."""
        new_conditions = self.environmental_conditions + (condition,)
        return dataclass_replace(
            self,
            environmental_conditions=new_conditions,
        )


@dataclass(frozen=True)
class ScenarioExploration:
    """
    Record of scenario exploration.
    
    Tracks which scenarios were explored and their results.
    """
    
    # Identity
    exploration_id: str                       # Unique identifier
    
    # Scenarios explored
    participating_scenarios: Tuple[HypotheticalScenario, ...]  # All explored
    
    # Metrics
    exploration_metrics: Dict[str, Any] = field(default_factory=dict)  # Exploration stats
    
    # Resulting space
    resulting_space: str = "expanded"         # How did exploration change things?
    
    # Metadata
    created_at_utc: float = field(default_factory=time.time)
    
    @property
    def total_scenarios(self) -> int:
        """Return number of scenarios explored."""
        return len(self.participating_scenarios)
    
    @classmethod
    def create(
        cls,
        exploring_scenarios: List[HypotheticalScenario],
        exploration_metrics: Optional[Dict[str, Any]] = None,
        resulting_space: str = "expanded",
    ) -> ScenarioExploration:
        """Create a new scenario exploration record."""
        return cls(
            exploration_id=f"exploration:{uuid.uuid4().hex[:16]}",
            participating_scenarios=tuple(exploring_scenarios),
            exploration_metrics=exploration_metrics or {},
            resulting_space=resulting_space,
        )


def dataclass_replace(instance: Any, **kwargs: Any) -> Any:
    """Simple dataclass replace helper for frozen instances."""
    return instance.__class__(**{**instance.__dict__, **kwargs})


__all__ = [
    "ScenarioEnvironmentKind",
    "ScenarioIdentity",
    "EnvironmentalCondition",
    "HypotheticalScenario",
    "ScenarioExploration",
]