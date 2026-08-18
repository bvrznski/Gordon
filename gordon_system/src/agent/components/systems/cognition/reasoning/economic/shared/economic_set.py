# Economic Set - Phase 7.48 Part 1
# =================================

"""
Economic Set.

Economic Reasoning operates over explicit Economic Sets.
Economic Sets define:
    - available resources
    - economic agents
    - allocation constraints
    - utility functions
    - market assumptions

Economic Sets remain immutable during reasoning.
"""

from __future__ import annotations

import uuid
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any
from enum import Enum

from gordon_system.src.agent.components.systems.cognition.reasoning.economic.shared.descriptor import (
    EconomicLifecycleState,
)


class EconomicSetKind(Enum):
    """Kinds of economic sets."""
    
    RESOURCE_INVENTORY = "resource_inventory"     # What resources are available?
    UTILITY_SPACE = "utility_space"               # What utilities exist?
    ALLOCATION_PROBLEM = "allocation_problem"     # Allocation constraints
    MARKET_ENVIRONMENT = "market_environment"     # Market assumptions


@dataclass(frozen=True)
class ResourceEntry:
    """A single resource entry in the inventory."""
    
    resource_id: str                    # Unique resource identifier
    resource_type: str                  # Type of resource (compute, memory, etc.)
    quantity: float                     # Available quantity
    capacity: Optional[float] = None    # Maximum capacity if applicable
    origin: Optional[str] = None        # Source of the resource


@dataclass(frozen=True)
class AgentEntry:
    """An economic agent."""
    
    agent_id: str                       # Unique agent identifier
    agent_type: str                     # Type of agent (user, process, system)
    preferences: Dict[str, float]       # Utility weights per objective
    budget: Optional[float] = None      # Budget constraint if applicable


@dataclass(frozen=True)
class AllocationConstraint:
    """An allocation constraint."""
    
    constraint_id: str                  # Unique constraint identifier
    constraint_type: str                # Type (hard, soft, optimization_target)
    expression: str                     # Constraint expression (e.g., "x + y <= 10")
    description: Optional[str] = None   # Human-readable description


@dataclass(frozen=True)
class UtilityFunction:
    """A utility function over allocations."""
    
    utility_id: str                     # Unique utility identifier
    utility_type: str                   # Type (linear, Cobb-Douglas, etc.)
    parameters: Dict[str, Any]          # Function parameters
    domain_resources: List[str]         # Resources this utility depends on


@dataclass(frozen=True)
class MarketAssumptions:
    """Market environment assumptions."""
    
    market_kind: str                    # Perfect competition, oligopoly, etc.
    price_assumptions: Dict[str, float] # Price expectations per resource
    coordination_mechanism: str         # Market, hierarchy, network


@dataclass(frozen=True)
class EconomicSet:
    """
    Immutable economic environment specification.
    
    An Economic Set contains:
        - Resource inventory
        - Agents with preferences
        - Allocation constraints
        - Utility functions
        - Market assumptions
    
    The set remains immutable during reasoning to ensure reproducibility.
    """
    
    # Identity
    economic_set_id: str                # Unique economic set identifier
    semantic_identity: str              # Semantic identity for the problem
    
    # Components
    resource_inventory: Dict[str, ResourceEntry]
    agents: Dict[str, AgentEntry]
    
    # Constraints and preferences
    allocation_constraints: List[AllocationConstraint]
    utility_functions: List[UtilityFunction]
    
    # Market environment
    market_assumptions: Optional[MarketAssumptions] = None
    
    # Lifecycle
    lifecycle_state: EconomicLifecycleState = EconomicLifecycleState.CREATED
    
    @classmethod
    def create(
        cls,
        semantic_identity: str,
        resources: Dict[str, ResourceEntry],
        agents: Dict[str, AgentEntry],
        constraints: Optional[List[AllocationConstraint]] = None,
        utilities: Optional[List[UtilityFunction]] = None,
        market_assumptions: Optional[MarketAssumptions] = None,
    ) -> EconomicSet:
        """Create a new economic set."""
        return cls(
            economic_set_id=f"economic_set:{uuid.uuid4().hex[:16]}",
            semantic_identity=semantic_identity,
            resource_inventory=resources,
            agents=agents,
            allocation_constraints=constraints or [],
            utility_functions=utilities or [],
            market_assumptions=market_assumptions,
        )


__all__ = [
    "EconomicSet",
    "EconomicSetKind",
    "ResourceEntry",
    "AgentEntry",
    "AllocationConstraint",
    "UtilityFunction",
    "MarketAssumptions",
]