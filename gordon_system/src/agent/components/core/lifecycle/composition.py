# Gordon Phase 3.26: Runtime Composition Architecture
# =====================================================

"""
Canonical Runtime Composition Architecture.

Composition is the process of assembling architectural entities into a coherent runtime.
It governs how dependencies are identified, ordered, and assembled.

COMPOSITION PRINCIPLES:
======================

1. DETERMINISTIC ASSEMBLY
   Same inputs always produce same composition result.

2. DEPENDENCY-AWARE ORDERING
   Entities are composed in dependency order to ensure availability.

3. COMPOSITION IS NOT EXECUTION
   Composition prepares runtime, execution performs work.

4. TRANSFORMATIVE CHANGES
   Each composition step transforms the system state.

COMPOSITION FLOW:
=================

    PLAN         - Define what needs to be composed
        ↓
    DISCOVER     - Identify entities and dependencies
        ↓
    RESOLVE      - Resolve dependency graph (topological sort)
        ↓
    CONSTRUCT    - Instantiate entities in correct order
        ↓
    INITIALIZE   - Inject dependencies, configure
        ↓
    VALIDATE     - Verify composition integrity
        ↓
    COMMIT       - Finalize and make operational

COMPOSITION TYPES:
==================

    1. Subsystem Composition   - Core subsystems assembled first
    2. Service Composition     - Services depend on subsystems
    3. Capability Composition  - Capabilities use services
    4. Dependency Composition  - Entities depend on others
    5. Graph Composition       - Full topology constructed

COMPOSITION INTEGRATION:
========================

    - Phase 3.12: Core Architecture (composition scope)
    - Phase 3.15: State (composition as state changes)
    - Phase 3.16: Time (composition timestamps)
    - Phase 3.18: Configuration & Policy (composition rules)
    - Phase 3.20: Concurrency (synchronized composition)
"""

from dataclasses import dataclass, field
from typing import Dict, List, Tuple, Optional, Any, Set
from enum import Enum
import time


class CompositionPhase(Enum):
    """
    Phases of the composition process.
    
    PHASE FLOW:
        PLAN → DISCOVER → RESOLVE → CONSTRUCT → INITIALIZE → VALIDATE → COMMIT
    """
    PLAN = "plan"
    DISCOVER = "discover"
    RESOLVE = "resolve"
    CONSTRUCT = "construct"
    INITIALIZE = "initialize"
    VALIDATE = "validate"
    COMMIT = "commit"


@dataclass(frozen=True)
class CompositionDependency:
    """A single dependency relationship between entities."""
    from_entity: str
    to_entity: str  # from_entity depends on to_entity
    
    required: bool = True
    optional: bool = False
    
    def is_optional(self) -> bool:
        return self.optional and not self.required


@dataclass(frozen=True)
class CompositionPlan:
    """
    A plan for how entities should be composed.
    
    Contains:
        - Entity definitions (type, id, dependencies)
        - Dependency graph
        - Compose order (topological sort result)
    """
    
    entity_id: str
    entity_type: str
    
    # Dependencies this entity has
    dependencies: Tuple[CompositionDependency, ...] = field(default_factory=tuple)
    
    # Position in composition order
    compose_order: int = 0
    
    @property
    def dependency_count(self) -> int:
        return len([d for d in self.dependencies if d.required])


@dataclass(frozen=True)
class CompositionGraph:
    """
    The full composition graph showing all entity relationships.
    
    Used to:
        - Validate composition integrity
        - Determine compose order (topological sort)
        - Identify circular dependencies
    """
    
    # Entities by ID
    entities: Dict[str, CompositionPlan]
    
    def get_entity(self, entity_id: str) -> Optional[CompositionPlan]:
        return self.entities.get(entity_id)
    
    def get_dependents(self, entity_id: str) -> Tuple[str, ...]:
        """Get all entities that depend on the given entity."""
        result = []
        for eid, plan in self.entities.items():
            for dep in plan.dependencies:
                if dep.to_entity == entity_id:
                    result.append(eid)
        return tuple(result)
    
    def get_dependencies(self, entity_id: str) -> Tuple[str, ...]:
        """Get all entities that the given entity depends on."""
        plan = self.entities.get(entity_id)
        if not plan:
            return ()
        return tuple(d.to_entity for d in plan.dependencies)


@dataclass(frozen=True)
class CompositionResult:
    """
    Result of a composition operation.
    
    Contains both successful and failed composition information.
    """
    
    success: bool
    entity_id: str
    phase: CompositionPhase
    
    # Error information (if failure)
    error_message: Optional[str] = None
    errors: Tuple[str, ...] = field(default_factory=tuple)
    
    # Success metadata
    composed_at: float = field(default_factory=time.time)
    
    @property
    def is_success(self) -> bool:
        return self.success
    
    @property
    def is_failure(self) -> bool:
        return not self.success


class CompositionEngine:
    """
    Engine for composing entities into runtime.
    
    Responsibilities:
        - Build composition graph from plans
        - Validate dependency integrity
        - Determine compose order (topological sort)
        - Execute composition with validation at each step
    """
    
    def __init__(self) -> None:
        self._graph: Optional[CompositionGraph] = None
        self._compose_order: List[str] = []
        self._composition_results: Dict[str, CompositionResult] = {}

    def add_entity(self, plan: CompositionPlan) -> 'CompositionEngine':
        """Add an entity to the composition graph."""
        if self._graph is None:
            entities: Dict[str, CompositionPlan] = {plan.entity_id: plan}
            self._graph = CompositionGraph(entities=entities)
        else:
            entities = dict(self._graph.entities)
            entities[plan.entity_id] = plan
            self._graph = CompositionGraph(entities=entities)
        return self

    def build_graph(self) -> CompositionGraph:
        """Build and return the composition graph."""
        if self._graph is None:
            self._graph = CompositionGraph(entities={})
        return self._graph

    def resolve_compose_order(self) -> Tuple[str, ...]:
        """
        Determine entity compose order using topological sort.
        
        Entities with fewer dependencies are composed first.
        """
        if self._graph is None:
            return ()

        # Kahn's algorithm for topological sort
        in_degree: Dict[str, int] = {eid: 0 for eid in self._graph.entities}

        # Calculate in-degrees (how many entities depend on each)
        for entity_id, plan in self._graph.entities.items():
            in_degree[entity_id] = len([d for d in plan.dependencies if d.required])

        # Start with entities that have no required dependencies
        queue: List[str] = [eid for eid, deg in in_degree.items() if deg == 0]
        result: List[str] = []

        while queue:
            # Sort by dependency count to prefer simpler entities first
            queue.sort(key=lambda eid: len(self._graph.entities[eid].dependencies))
            current = queue.pop(0)
            result.append(current)

            # Decrease in-degree for dependents
            for dependent_id in self._graph.get_dependents(current):
                if dependent_id in in_degree:
                    in_degree[dependent_id] -= 1
                    if in_degree[dependent_id] == 0:
                        queue.append(dependent_id)

        # Check for circular dependencies
        if len(result) != len(self._graph.entities):
            missing = set(self._graph.entities.keys()) - set(result)
            raise ValueError(f"Circular dependency detected: {missing}")

        self._compose_order = result
        return tuple(result)

    def compose_entity(self, entity_id: str) -> CompositionResult:
        """Compose a single entity."""
        if self._graph is None or entity_id not in self._graph.entities:
            return CompositionResult(
                success=False,
                entity_id=entity_id,
                phase=CompositionPhase.CONSTRUCT,
                error_message=f"Entity {entity_id} not in composition graph",
            )

        # Check dependencies are satisfied
        plan = self._graph.entities[entity_id]
        for dep in plan.dependencies:
            if dep.required and dep.to_entity not in self._compose_order[:self._compose_order.index(entity_id)]:
                return CompositionResult(
                    success=False,
                    entity_id=entity_id,
                    phase=CompositionPhase.VALIDATE,
                    error_message=f"Dependency {dep.to_entity} not yet composed",
                )

        # Compose successfully
        result = CompositionResult(
            success=True,
            entity_id=entity_id,
            phase=CompositionPhase.COMMIT,
        )
        self._composition_results[entity_id] = result
        return result

    def compose_all(self) -> Tuple[bool, Dict[str, CompositionResult]]:
        """
        Compose all entities in order.
        
        Returns:
            (success, results_dict)
        """
        if self._graph is None:
            return False, {}

        success = True
        for entity_id in self.resolve_compose_order():
            result = self.compose_entity(entity_id)
            self._composition_results[entity_id] = result
            if not result.success:
                success = False

        return success, dict(self._composition_results)


__all__ = [
    "CompositionPhase",
    "CompositionDependency",
    "CompositionPlan",
    "CompositionGraph",
    "CompositionResult",
    "CompositionEngine",
]
