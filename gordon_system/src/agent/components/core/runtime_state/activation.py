# Core Runtime Activation Infrastructure
# ======================================

"""
Core runtime activation artifacts for Phase 3.7.5-I.

Provides:
- Immutable activation request/response types
- Activation graph with deterministic ordering
- Lifecycle state machine integration
- Rollback plans and results
- Activation events and diagnostics
"""

from dataclasses import dataclass, field
from typing import Dict, List, Tuple, Optional, Any
from enum import Enum
import uuid
import time

from ..types import (
    EntityId,
    ComponentId,
    ServiceId,
    RuntimeId,
    Timestamp,
    LifecycleEvent as BaseLifecycleEvent,
)
from . import RuntimeState, RuntimeStateTransition


# =============================================================================
# LIFECYCLE STATE MACHINE (Canonical)
# =============================================================================

class ActivationState(Enum):
    """Runtime activation lifecycle states."""
    
    # Pre-activation states
    CONSTRUCTED = "constructed"
    ASSEMBLED = "assembled"  # Fully assembled but inactive
    
    # Activation states
    ACTIVATING = "activating"  # Currently activating
    ACTIVE = "active"          # Infrastructure started, ready for evaluation
    
    # Post-activation states
    QUIESCING = "quiescing"
    STOPPING = "stopping"
    STOPPED = "stopped"
    
    # Error states
    FAILED = "failed"
    PARTIALLY_ACTIVATED = "partially_activated"  # Partial success state


class LifecycleTransition(Enum):
    """Valid lifecycle transitions."""
    
    ASSEMBLED_TO_ACTIVATING = ("assembled", "activating")
    ACTIVATING_TO_ACTIVE = ("activating", "active")
    ACTIVATING_TO_PARTIALLY_ACTIVATED = ("activating", "partially_activated")
    ACTIVE_TO_QUIESCING = ("active", "quiescing")
    QUIESCING_TO_STOPPING = ("quiescing", "stopping")
    STOPPING_TO_STOPPED = ("stopping", "stopped")
    ANY_TO_FAILED = ("*", "failed")
    
    @classmethod
    def is_valid(cls, from_state: ActivationState, to_state: ActivationState) -> bool:
        """Check if transition is valid."""
        from_val = from_state.value
        to_val = to_state.value
        
        for trans in cls:
            if (trans.value[0] == "*" or trans.value[0] == from_val) and trans.value[1] == to_val:
                return True
        return False


class LifecycleStateMachine:
    """
    Canonical lifecycle state machine for runtime activation.
    
    Provides:
    - Single authoritative source of truth for lifecycle transitions
    - Immutable transition history
    - Valid transition enforcement
    - Failure cause preservation
    
    This is ONE authority alongside RuntimeStateStore but specifically for
    the activation lifecycle phase.
    """
    
    def __init__(self, runtime_id: str) -> None:
        import threading
        self._runtime_id = runtime_id
        self._state = ActivationState.CONSTRUCTED  # Start at CONSTRUCTED
        self._history: List[Tuple[ActivationState, ActivationState, float]] = []
        self._failure_cause: Optional[Exception] = None
        self._lock = threading.Lock()
    
    @property
    def state(self) -> ActivationState:
        """Get current lifecycle state."""
        with self._lock:
            return self._state
    
    @property
    def failure_cause(self) -> Optional[Exception]:
        """Get failure cause if in FAILED state."""
        with self._lock:
            return self._failure_cause
    
    @property
    def history(self) -> List[Tuple[ActivationState, ActivationState, float]]:
        """Get transition history (immutable copy)."""
        with self._lock:
            return list(self._history)
    
    def can_transition(self, to_state: ActivationState) -> bool:
        """Check if transition is valid."""
        with self._lock:
            return LifecycleTransition.is_valid(self._state, to_state)
    
    def transition(self, to_state: ActivationState) -> bool:
        """
        Attempt state transition.
        
        Args:
            to_state: Target state
            
        Returns:
            True if transition succeeded
            
        Raises:
            ValueError: If transition is invalid
        """
        with self._lock:
            current = self._state
            
            if not LifecycleTransition.is_valid(current, to_state):
                raise ValueError(
                    f"Invalid transition from {current.value} to {to_state.value}"
                )
            
            # Record the transition
            timestamp = time.monotonic()
            self._history.append((current, to_state, timestamp))
            self._state = to_state
            
            return True
    
    def fail(self, cause: Exception) -> None:
        """Transition to FAILED state with preserved cause."""
        with self._lock:
            old_state = self._state
            self._failure_cause = cause
            self._history.append((old_state, ActivationState.FAILED, time.monotonic()))
            self._state = ActivationState.FAILED
    
    def get_snapshot(self) -> "LifecycleSnapshot":
        """Get immutable snapshot of lifecycle state."""
        with self._lock:
            return LifecycleSnapshot(
                runtime_id=self._runtime_id,
                current_state=self._state,
                history=list(self._history),
                failure_cause=self._failure_cause
            )


@dataclass(frozen=True)
class LifecycleSnapshot:
    """Immutable snapshot of lifecycle state machine."""
    
    runtime_id: str
    current_state: ActivationState
    history: List[Tuple[ActivationState, ActivationState, float]]
    failure_cause: Optional[Exception]
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "runtime_id": self.runtime_id,
            "current_state": self.current_state.value,
            "history": [
                (f"({h[0].value}, {h[1].value})", h[2])
                for h in self.history
            ],
            "failure_cause": str(self.failure_cause) if self.failure_cause else None
        }


# =============================================================================
# ACTIVATION REQUEST AND CONTEXT
# =============================================================================

@dataclass(frozen=True)
class ActivationRequest:
    """
    Immutable request to activate a runtime.
    
    Provides:
    - Canonical activation identity
    - Source state validation
    - Deadline and cancellation support
    - Configuration fingerprint for idempotency
    
    All fields are immutable. This is the input contract.
    """
    
    activation_id: str  # UUID4 string
    runtime_id: str
    boot_session_id: Optional[str] = None
    requested_mode: str = "default"  # default, recovery, test
    expected_source_state: ActivationState = ActivationState.ASSEMBLED
    deadline: float = field(default_factory=lambda: time.monotonic() + 30.0)  # 30s default
    cancellation_requested: bool = False
    configuration_fingerprint: str = ""
    correlation_id: Optional[str] = None
    causation_id: Optional[str] = None
    provenance: Dict[str, Any] = field(default_factory=dict)
    
    @classmethod
    def create(cls, runtime_id: str, **kwargs) -> "ActivationRequest":
        """Create a new activation request with generated ID."""
        return cls(
            activation_id=str(uuid.uuid4()),
            runtime_id=runtime_id,
            **{k: v for k, v in kwargs.items() if hasattr(cls, k)}
        )
    
    def is_expired(self) -> bool:
        """Check if the request has passed its deadline."""
        return time.monotonic() > self.deadline
    
    def to_context(self) -> "ActivationContext":
        """Convert to activation context for use during execution."""
        return ActivationContext(
            activation_id=self.activation_id,
            runtime_id=self.runtime_id,
            boot_session_id=self.boot_session_id,
            mode=self.requested_mode,
            correlation_id=self.correlation_id,
            causation_id=self.causation_id,
            provenance=dict(self.provenance)
        )


@dataclass(frozen=True)
class ActivationContext:
    """
    Context for a single activation attempt.
    
    This is the runtime context passed to activation components.
    It's derived from ActivationRequest but doesn't include
    request-specific fields like deadline and cancellation flags.
    """
    
    activation_id: str
    runtime_id: str
    boot_session_id: Optional[str]
    mode: str
    correlation_id: Optional[str]
    causation_id: Optional[str]
    provenance: Dict[str, Any]


# =============================================================================
# ACTIVATION GRAPH
# =============================================================================

@dataclass(frozen=True)
class ActivationNode:
    """
    Node in the activation graph.
    
    Represents one lifecycle-managed entity that must be activated.
    """
    
    entity_id: EntityId
    entity_type: str  # "kernel", "lifecycle", "scheduler", "service"
    dependencies: Tuple[EntityId, ...] = field(default_factory=tuple)
    optional_dependencies: Tuple[EntityId, ...] = field(default_factory=tuple)
    activation_priority: int = 0  # Lower = starts earlier
    timeout_seconds: float = 30.0
    can_fail_gracefully: bool = False
    
    def __hash__(self) -> int:
        return hash(self.entity_id)


@dataclass(frozen=True)
class ActivationEdge:
    """
    Edge in the activation graph.
    
    Represents a dependency relationship between nodes.
    """
    
    from_node: EntityId  # Dependent
    to_node: EntityId    # Dependency
    required: bool = True
    reason: str = "dependency"
    
    def reverse(self) -> "ActivationEdge":
        """Return reversed edge."""
        return ActivationEdge(
            from_node=self.to_node,
            to_node=self.from_node,
            required=self.required,
            reason=f"reverse_of_{self.reason}"
        )


@dataclass(frozen=True)
class ActivationGraph:
    """
    Immutable activation dependency graph.
    
    Built from runtime composition metadata. Used for:
    - Deterministic activation ordering
    - Cycle detection
    - Rollback planning
    
    All graphs are validated before use.
    """
    
    _nodes: Dict[EntityId, ActivationNode] = field(default_factory=dict)
    _edges: List[ActivationEdge] = field(default_factory=list)
    _validate_cycles: bool = True
    
    @classmethod
    def create(cls, nodes: List[ActivationNode], edges: List[ActivationEdge]) -> "ActivationGraph":
        """Create and validate a new activation graph."""
        node_dict = {n.entity_id: n for n in nodes}
        
        # Validate all edge endpoints reference existing nodes
        for edge in edges:
            if edge.from_node not in node_dict:
                raise ValueError(f"Edge from_node {edge.from_node} not found")
            if edge.to_node not in node_dict:
                raise ValueError(f"Edge to_node {edge.to_node} not found")
        
        graph = cls(
            _nodes=node_dict,
            _edges=list(edges),
            _validate_cycles=True
        )
        
        # Validate no cycles (for now - can be expensive on large graphs)
        if graph._validate_cycles:
            graph._validate_no_cycles()
        
        return graph
    
    def _validate_no_cycles(self) -> None:
        """Validate the graph has no cycles using DFS."""
        visited: set = set()
        rec_stack: set = set()
        
        def dfs(node_id: EntityId) -> bool:
            if node_id in rec_stack:
                return True  # Cycle detected
            if node_id in visited:
                return False
            
            visited.add(node_id)
            rec_stack.add(node_id)
            
            for edge in self._edges:
                if edge.from_node == node_id:
                    if dfs(edge.to_node):
                        return True
            
            rec_stack.remove(node_id)
            return False
        
        for node_id in self._nodes:
            if dfs(node_id):
                raise ValueError("Activation graph contains a cycle")
    
    @property
    def nodes(self) -> Tuple[ActivationNode, ...]:
        """Get all nodes (immutable tuple)."""
        return tuple(self._nodes.values())
    
    @property
    def edges(self) -> Tuple[ActivationEdge, ...]:
        """Get all edges (immutable tuple)."""
        return tuple(self._edges)
    
    def get_node(self, entity_id: EntityId) -> Optional[ActivationNode]:
        """Get a node by entity ID."""
        return self._nodes.get(entity_id)
    
    def get_dependencies(self, entity_id: EntityId) -> Tuple[EntityId, ...]:
        """Get entities that the given entity depends on."""
        result = []
        for edge in self._edges:
            if edge.from_node == entity_id and edge.required:
                result.append(edge.to_node)
        return tuple(result)
    
    def get_dependents(self, entity_id: EntityId) -> Tuple[EntityId, ...]:
        """Get entities that depend on the given entity."""
        result = []
        for edge in self._edges:
            if edge.to_node == entity_id and edge.required:
                result.append(edge.from_node)
        return tuple(result)
    
    def topological_sort(self) -> List[EntityId]:
        """
        Perform topological sort with deterministic tie-breaking.
        
        Returns entities in activation order (dependencies first).
        Uses priority-based tie-breaking for determinism.
        """
        # Kahn's algorithm with priority queue
        in_degree: Dict[EntityId, int] = {}
        dependents: Dict[EntityId, List[EntityId]] = {}
        
        # Initialize
        for node_id in self._nodes:
            in_degree[node_id] = 0
            dependents[node_id] = []
        
        # Build adjacency info
        for edge in self._edges:
            if edge.required and edge.to_node in self._nodes:  # Only required edges
                in_degree[edge.from_node] += 1
                dependents[edge.to_node].append(edge.from_node)
        
        # Priority queue - use list with sorting on each pop
        available: List[EntityId] = [
            n for n in self._nodes 
            if in_degree[n] == 0
        ]
        
        result: List[EntityId] = []
        
        while available:
            # Sort by priority (lower first), then by entity_id string for determinism
            available.sort(key=lambda x: (
                self._nodes[x].activation_priority,
                str(x)
            ))
            
            node_id = available.pop(0)
            result.append(node_id)
            
            # Update dependents
            for dependent in dependents.get(node_id, []):
                in_degree[dependent] -= 1
                if in_degree[dependent] == 0:
                    available.append(dependent)
        
        if len(result) != len(self._nodes):
            raise ValueError("Graph contains cycle - topological sort failed")
        
        return result
    
    def reverse_topological_sort(self, exclude: Optional[Tuple[EntityId, ...]] = None) -> List[EntityId]:
        """
        Get nodes in reverse dependency order (for rollback).
        
        Args:
            exclude: Entities to exclude from the result
        """
        forward_order = self.topological_sort()
        
        # Filter excluded nodes
        if exclude:
            exclude_set = set(exclude)
            forward_order = [n for n in forward_order if n not in exclude_set]
        
        return list(reversed(forward_order))
    
    def get_layers(self) -> List[List[EntityId]]:
        """
        Group entities by dependency levels.
        
        Returns:
            List of layers, where each layer contains entities
            that can be activated in parallel. Layer 0 has no dependencies,
            layer N depends only on nodes in layers < N.
        """
        # Calculate depth for each node
        depths: Dict[EntityId, int] = {}
        
        def get_depth(node_id: EntityId) -> int:
            if node_id in depths:
                return depths[node_id]
            
            deps = self.get_dependencies(node_id)
            if not deps:
                depths[node_id] = 0
            else:
                depths[node_id] = max(get_depth(d) for d in deps) + 1
            
            return depths[node_id]
        
        # Calculate all depths
        for node_id in self._nodes:
            get_depth(node_id)
        
        # Group by depth
        layers: Dict[int, List[EntityId]] = {}
        for node_id, depth in depths.items():
            if depth not in layers:
                layers[depth] = []
            layers[depth].append(node_id)
        
        # Sort each layer deterministically
        for depth in layers:
            layers[depth].sort(key=lambda x: (self._nodes[x].activation_priority, str(x)))
        
        # Return as list of lists sorted by depth
        return [layers[i] for i in sorted(layers.keys())]


# =============================================================================
# ACTIVATION PLAN
# =============================================================================

@dataclass(frozen=True)
class ActivationStep:
    """
    A single step in the activation plan.
    
    One step may contain parallelizable entities that can be activated together.
    """
    
    step_id: int
    layer_index: int  # Which dependency layer this belongs to
    entity_ids: Tuple[EntityId, ...]
    timeout_seconds: float = 30.0
    
    def __hash__(self) -> int:
        return hash(self.step_id)


@dataclass(frozen=True)
class ActivationPlan:
    """
    Immutable activation plan compiled from an activation graph.
    
    Provides:
    - Ordered activation steps
    - Parallelization groups (layers)
    - Timeout configuration per step
    - Rollback ordering
    
    This is the executable artifact for activation.
    """
    
    runtime_id: str
    source_state: ActivationState
    target_state: ActivationState
    graph_version: int
    plan_version: int
    steps: Tuple[ActivationStep, ...]
    rollback_steps: Tuple[ActivationStep, ...]
    dependencies: Dict[EntityId, Tuple[EntityId, ...]]
    timeouts: Dict[int, float]  # step_id -> timeout
    
    @classmethod
    def compile(cls, graph: ActivationGraph, runtime_state: RuntimeState) -> "ActivationPlan":
        """
        Compile an activation plan from a graph and source state.
        
        Args:
            graph: The validated activation graph
            runtime_state: Current runtime state (must be ASSEMBLED or READY)
            
        Returns:
            A compiled activation plan
            
        Raises:
            ValueError: If runtime state is not valid for activation
        """
        # Validate source state
        if runtime_state not in (RuntimeState.ASSEMBLED, RuntimeState.READY):
            raise ValueError(
                f"Cannot activate from {runtime_state.value}; "
                f"must be ASSEMBLED or READY"
            )
        
        # Get deterministic ordering
        entity_ids = graph.topological_sort()
        
        # Get dependency mapping
        dependencies: Dict[EntityId, Tuple[EntityId, ...]] = {}
        for eid in entity_ids:
            deps = graph.get_dependencies(eid)
            dependencies[eid] = tuple(sorted(deps))  # Sort for determinism
        
        # Build steps from layers (each layer is one step with parallel entities)
        layers = graph.get_layers()
        steps: List[ActivationStep] = []
        
        for layer_idx, layer_entities in enumerate(layers):
            steps.append(ActivationStep(
                step_id=layer_idx,
                layer_index=layer_idx,
                entity_ids=tuple(layer_entities),
                timeout_seconds=layers[layer_idx][0].timeout_seconds if layer_entities else 30.0
            ))
        
        # Rollback order is reverse of activation
        rollback_steps = tuple(reversed(steps))
        
        # Build timeouts map
        timeouts: Dict[int, float] = {
            s.step_id: s.timeout_seconds for s in steps
        }
        
        return cls(
            runtime_id=graph.nodes[0].entity_id if graph.nodes else "unknown",
            source_state=runtime_state,
            target_state=ActivationState.ACTIVE,
            graph_version=id(graph),  # Use id as version (in real impl, use explicit version)
            plan_version=1,
            steps=tuple(steps),
            rollback_steps=rollback_steps,
            dependencies=dependencies,
            timeouts=timeouts
        )
    
    def get_step_for_entity(self, entity_id: EntityId) -> Optional[ActivationStep]:
        """Get the activation step that contains a given entity."""
        for step in self.steps:
            if entity_id in step.entity_ids:
                return step
        return None
    
    def is_entity_first_in_layer(self, entity_id: EntityId) -> bool:
        """Check if an entity is first (highest priority) in its layer."""
        step = self.get_step_for_entity(entity_id)
        if step and step.entity_ids:
            # Compare by activation_priority, then string
            entities = list(step.entity_ids)
            entities.sort(key=lambda x: (
                getattr(self._get_node_by_id(x), 'activation_priority', 0),
                str(x)
            ))
            return entities[0] == entity_id
        return False
    
    def _get_node_by_id(self, entity_id: EntityId) -> Optional[ActivationNode]:
        """Get the node for an entity ID."""
        # This would use the graph - stored in plan compilation context
        return None  # Placeholder


# =============================================================================
# ACTIVATION RESULT AND FAILURE
# =============================================================================

@dataclass(frozen=True)
class ActivationFailure:
    """
    Immutable failure record during activation.
    
    Preserves primary cause and collects secondary failures.
    """
    
    step_id: int
    entity_id: EntityId
    failed_transition: str
    primary_cause: Exception
    timestamp: float = field(default_factory=time.monotonic)
    secondary_failures: List[Tuple[str, Exception]] = field(default_factory=list)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "step_id": self.step_id,
            "entity_id": str(self.entity_id),
            "failed_transition": self.failed_transition,
            "primary_cause": str(self.primary_cause),
            "timestamp": self.timestamp,
            "secondary_failures": [
                (f"{f[0]}: {f[1]}",) for f in self.secondary_failures
            ]
        }


@dataclass(frozen=True)
class ActivationResult:
    """
    Immutable result of an activation attempt.
    
    This is the output contract for activation - always returns a typed result,
    never just True/False or raises generic errors for expected conditions.
    """
    
    activation_id: str
    runtime_id: str
    status: "ActivationStatus"
    source_state: ActivationState
    final_state: ActivationState
    activated_entity_ids: Tuple[EntityId, ...]
    rolled_back_entity_ids: Tuple[EntityId, ...] = field(default_factory=tuple)
    active_resource_ids: Tuple[str, ...] = field(default_factory=tuple)
    failed_entity_id: Optional[EntityId] = None
    primary_failure: Optional[ActivationFailure] = None
    rollback_failures: List[ActivationFailure] = field(default_factory=list)
    readiness_status: str = "unevaluated"  # unevaluated, ready, not_ready
    admission_status: str = "closed"
    elapsed_time_seconds: float = 0.0
    diagnostics: Dict[str, Any] = field(default_factory=dict)
    provenance: Dict[str, Any] = field(default_factory=dict)
    
    @property
    def success(self) -> bool:
        """Check if activation succeeded."""
        return self.status == ActivationStatus.COMPLETED
    
    @property
    def failed(self) -> bool:
        """Check if activation failed."""
        return self.status in (
            ActivationStatus.FAILED,
            ActivationStatus.PARTIAL_FAILURE
        )
    
    @property
    def partially_activated(self) -> bool:
        """Check if only partial activation occurred."""
        return self.status == ActivationStatus.PARTIAL_FAILURE
    
    @classmethod
    def success_result(
        cls,
        activation_id: str,
        runtime_id: str,
        activated_entities: List[EntityId],
        active_resources: List[str],
        diagnostics: Optional[Dict[str, Any]] = None,
        provenance: Optional[Dict[str, Any]] = None
    ) -> "ActivationResult":
        """Create a successful activation result."""
        return cls(
            activation_id=activation_id,
            runtime_id=runtime_id,
            status=ActivationStatus.COMPLETED,
            source_state=ActivationState.ASSEMBLED,
            final_state=ActivationState.ACTIVE,
            activated_entity_ids=tuple(activated_entities),
            active_resource_ids=tuple(active_resources),
            readiness_status="unevaluated",
            admission_status="closed",
            diagnostics=diagnostics or {},
            provenance=provenance or {}
        )
    
    @classmethod
    def failure_result(
        cls,
        activation_id: str,
        runtime_id: str,
        failed_entity: EntityId,
        primary_failure: ActivationFailure,
        activated_before_failure: List[EntityId],
        rolled_back_entities: List[EntityId],
        diagnostics: Optional[Dict[str, Any]] = None,
        provenance: Optional[Dict[str, Any]] = None
    ) -> "ActivationResult":
        """Create a failed activation result."""
        return cls(
            activation_id=activation_id,
            runtime_id=runtime_id,
            status=ActivationStatus.PARTIAL_FAILURE,
            source_state=ActivationState.ASSEMBLED,
            final_state=ActivationState.FAILED,
            activated_entity_ids=tuple(activated_before_failure),
            rolled_back_entity_ids=tuple(rolled_back_entities),
            failed_entity_id=failed_entity,
            primary_failure=primary_failure,
            readiness_status="unevaluated",
            admission_status="closed",
            diagnostics=diagnostics or {},
            provenance=provenance or {}
        )
    
    @classmethod
    def already_active_result(cls, activation_id: str, runtime_id: str) -> "ActivationResult":
        """Create idempotent success for already-active runtime."""
        return cls(
            activation_id=activation_id,
            runtime_id=runtime_id,
            status=ActivationStatus.IDEMPOTENT_SUCCESS,
            source_state=ActivationState.ACTIVE,
            final_state=ActivationState.ACTIVE,
            activated_entity_ids=(),
            active_resource_ids=(),
            readiness_status="unevaluated",
            admission_status="closed"
        )
    
    def to_snapshot(self) -> "ActivationSnapshot":
        """Convert to snapshot for observability."""
        return ActivationSnapshot(
            activation_id=self.activation_id,
            runtime_id=self.runtime_id,
            status=self.status.value,
            source_state=self.source_state.value,
            final_state=self.final_state.value,
            activated_entities=[str(eid) for eid in self.activated_entity_ids],
            failed_entity=str(self.failed_entity_id) if self.failed_entity_id else None,
            primary_failure=str(self.primary_failure) if self.primary_failure else None
        )


class ActivationStatus(Enum):
    """Status of an activation attempt."""
    
    REQUESTED = "requested"
    VALIDATING = "validating"
    PLANNING = "planning"
    ACTIVATING = "activating"
    VERIFYING = "verifying"
    COMMITTING = "committing"
    COMPLETED = "completed"  # Full success
    IDEMPOTENT_SUCCESS = "idempotent_success"  # Re-activation of active runtime
    PARTIAL_FAILURE = "partial_failure"  # Some entities activated, then failed
    FAILED = "failed"  # Complete failure before any entities
    ROLLING_BACK = "rolling_back"
    ROLLED_BACK = "rolled_back"
    CANCELLED = "cancelled"


@dataclass(frozen=True)
class ActivationSnapshot:
    """Immutable snapshot of activation state for observability."""
    
    activation_id: str
    runtime_id: str
    status: str
    source_state: str
    final_state: str
    activated_entities: List[str]
    failed_entity: Optional[str]
    primary_failure: Optional[str]
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "activation_id": self.activation_id,
            "runtime_id": self.runtime_id,
            "status": self.status,
            "source_state": self.source_state,
            "final_state": self.final_state,
            "activated_entities": self.activated_entities,
            "failed_entity": self.failed_entity,
            "primary_failure": self.primary_failure
        }


# =============================================================================
# ACTIVATION ROLLBACK PLAN AND RESULT
# =============================================================================

@dataclass(frozen=True)
class ActivationRollbackPlan:
    """
    Immutable rollback plan.
    
    Generated from the activation plan with reversed order and dependencies.
    """
    
    runtime_id: str
    activation_id: str
    entities_to_rollback: Tuple[EntityId, ...]
    resource_ids: Tuple[str, ...]
    rollback_order: Tuple[int, ...]  # Step IDs in reverse order
    
    @classmethod
    def from_plan(cls, plan: ActivationPlan) -> "ActivationRollbackPlan":
        """Create a rollback plan from an activation plan."""
        return cls(
            runtime_id=plan.runtime_id,
            activation_id="rollback_" + plan.graph_version,  # Would use original ID
            entities_to_rollback=tuple(reversed(plan.steps[0].entity_ids)) if plan.steps else (),
            resource_ids=(),  # Would extract from activated entities
            rollback_order=tuple(range(len(plan.steps) - 1, -1, -1))
        )


@dataclass(frozen=True)
class ActivationRollbackResult:
    """
    Immutable result of a rollback operation.
    
    Preserves original activation failure as primary cause.
    """
    
    runtime_id: str
    activation_id: str
    success: bool
    rolled_back_entities: Tuple[EntityId, ...]
    failed_rollback_entities: List[Tuple[EntityId, Exception]]
    original_activation_failure: Optional[str]  # String representation
    
    def to_snapshot(self) -> "RollbackSnapshot":
        """Convert to snapshot."""
        return RollbackSnapshot(
            runtime_id=self.runtime_id,
            activation_id=self.activation_id,
            success=self.success,
            rolled_back_count=len(self.rolled_back_entities),
            failed_rollback_count=len(self.failed_rollback_entities)
        )


@dataclass(frozen=True)
class RollbackSnapshot:
    """Immutable snapshot of rollback state."""
    
    runtime_id: str
    activation_id: str
    success: bool
    rolled_back_count: int
    failed_rollback_count: int


# =============================================================================
# ACTIVATION EVENTS
# =============================================================================

@dataclass(frozen=True)
class ActivationEvent:
    """
    Immutable event emitted during activation.
    
    Events observe transitions but don't own them. They're for observability only.
    """
    
    event_type: str  # e.g., "activation.started", "component_activated"
    runtime_id: str
    activation_id: str
    timestamp: float = field(default_factory=time.monotonic)
    sequence_number: int = 0
    entity_id: Optional[EntityId] = None
    source_state: Optional[str] = None
    target_state: Optional[str] = None
    payload: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "event_type": self.event_type,
            "runtime_id": self.runtime_id,
            "activation_id": self.activation_id,
            "timestamp": self.timestamp,
            "sequence_number": self.sequence_number,
            "entity_id": str(self.entity_id) if self.entity_id else None,
            "source_state": self.source_state,
            "target_state": self.target_state,
            "payload": self.payload
        }


class ActivationEvents:
    """Factory for activation events."""
    
    @staticmethod
    def requested(runtime_id: str, activation_id: str) -> ActivationEvent:
        return ActivationEvent(
            event_type="activation.requested",
            runtime_id=runtime_id,
            activation_id=activation_id
        )
    
    @staticmethod
    def validation_started(runtime_id: str, activation_id: str) -> ActivationEvent:
        return ActivationEvent(
            event_type="activation.validation.started",
            runtime_id=runtime_id,
            activation_id=activation_id
        )
    
    @staticmethod
    def plan_compiled(runtime_id: str, activation_id: str, graph_version: int) -> ActivationEvent:
        return ActivationEvent(
            event_type="activation.plan.compiled",
            runtime_id=runtime_id,
            activation_id=activation_id,
            payload={"graph_version": graph_version}
        )
    
    @staticmethod
    def started(runtime_id: str, activation_id: str) -> ActivationEvent:
        return ActivationEvent(
            event_type="activation.started",
            runtime_id=runtime_id,
            activation_id=activation_id
        )
    
    @staticmethod
    def component_started(runtime_id: str, activation_id: str, entity_id: EntityId) -> ActivationEvent:
        return ActivationEvent(
            event_type="component.activation.started",
            runtime_id=runtime_id,
            activation_id=activation_id,
            entity_id=entity_id
        )
    
    @staticmethod
    def component_activated(runtime_id: str, activation_id: str, entity_id: EntityId) -> ActivationEvent:
        return ActivationEvent(
            event_type="component.activated",
            runtime_id=runtime_id,
            activation_id=activation_id,
            entity_id=entity_id,
            payload={"timestamp": time.monotonic()}
        )
    
    @staticmethod
    def component_activation_failed(
        runtime_id: str, activation_id: str, entity_id: EntityId, error: Exception
    ) -> ActivationEvent:
        return ActivationEvent(
            event_type="component.activation.failed",
            runtime_id=runtime_id,
            activation_id=activation_id,
            entity_id=entity_id,
            payload={"error": str(error), "timestamp": time.monotonic()}
        )
    
    @staticmethod
    def verification_started(runtime_id: str, activation_id: str) -> ActivationEvent:
        return ActivationEvent(
            event_type="activation.verification.started",
            runtime_id=runtime_id,
            activation_id=activation_id
        )
    
    @staticmethod
    def rollback_started(runtime_id: str, activation_id: str) -> ActivationEvent:
        return ActivationEvent(
            event_type="activation.rollback.started",
            runtime_id=runtime_id,
            activation_id=activation_id
        )
    
    @staticmethod
    def component_rollback_started(runtime_id: str, activation_id: str, entity_id: EntityId) -> ActivationEvent:
        return ActivationEvent(
            event_type="component.rollback.started",
            runtime_id=runtime_id,
            activation_id=activation_id,
            entity_id=entity_id
        )
    
    @staticmethod
    def component_rolled_back(runtime_id: str, activation_id: str, entity_id: EntityId) -> ActivationEvent:
        return ActivationEvent(
            event_type="component.rolled_back",
            runtime_id=runtime_id,
            activation_id=activation_id,
            entity_id=entity_id,
            payload={"timestamp": time.monotonic()}
        )
    
    @staticmethod
    def component_rollback_failed(
        runtime_id: str, activation_id: str, entity_id: EntityId, error: Exception
    ) -> ActivationEvent:
        return ActivationEvent(
            event_type="component.rollback.failed",
            runtime_id=runtime_id,
            activation_id=activation_id,
            entity_id=entity_id,
            payload={"error": str(error), "timestamp": time.monotonic()}
        )
    
    @staticmethod
    def completed(runtime_id: str, activation_id: str, final_state: str) -> ActivationEvent:
        return ActivationEvent(
            event_type="activation.completed",
            runtime_id=runtime_id,
            activation_id=activation_id,
            target_state=final_state,
            payload={"timestamp": time.monotonic()}
        )
    
    @staticmethod
    def failed(runtime_id: str, activation_id: str, error: Exception) -> ActivationEvent:
        return ActivationEvent(
            event_type="activation.failed",
            runtime_id=runtime_id,
            activation_id=activation_id,
            payload={
                "error": str(error),
                "timestamp": time.monotonic()
            }
        )
    
    @staticmethod
    def cancelled(runtime_id: str, activation_id: str) -> ActivationEvent:
        return ActivationEvent(
            event_type="activation.cancelled",
            runtime_id=runtime_id,
            activation_id=activation_id,
            payload={"timestamp": time.monotonic()}
        )


# =============================================================================
# CONFIGURATION
# =============================================================================

@dataclass(frozen=True)
class ActivationConcurrencyConfig:
    """Configuration for parallel activation."""
    
    max_parallel: int = 4  # Max entities to activate in parallel
    layer_timeout_multiplier: float = 1.5  # Multiplier for layer timeouts
    
    @classmethod
    def default(cls) -> "ActivationConcurrencyConfig":
        return cls()
    
    @classmethod
    def strict(cls) -> "ActivationConcurrencyConfig":
        """Strict config - sequential activation."""
        return cls(max_parallel=1)


@dataclass(frozen=True)
class ActivationTimeoutConfig:
    """Configuration for timeouts during activation."""
    
    default_timeout: float = 30.0
    layer_timeout: Optional[float] = None
    component_timeout_multiplier: float = 2.0
    
    def get_component_timeout(self, base_timeout: Optional[float] = None) -> float:
        """Get timeout for a single component."""
        base = base_timeout or self.default_timeout
        return base * self.component_timeout_multiplier


@dataclass(frozen=True)
class ActivationConfig:
    """
    Immutable configuration for activation.
    
    All values are validated and immutable.
    """
    
    concurrency: ActivationConcurrencyConfig = field(default_factory=ActivationConcurrencyConfig.default)
    timeouts: ActivationTimeoutConfig = field(default_factory=ActivationTimeoutConfig)
    verify_activation: bool = True  # Whether to verify after each component
    rollback_enabled: bool = True
    events_enabled: bool = True
    
    @classmethod
    def default(cls) -> "ActivationConfig":
        return cls()


# =============================================================================
# PUBLIC API
# =============================================================================

__all__ = [
    # Lifecycle state machine
    "ActivationState",
    "LifecycleTransition",
    "LifecycleStateMachine",
    "LifecycleSnapshot",
    
    # Request and context
    "ActivationRequest",
    "ActivationContext",
    
    # Graph
    "ActivationNode",
    "ActivationEdge",
    "ActivationGraph",
    
    # Plan
    "ActivationStep",
    "ActivationPlan",
    
    # Result and failure
    "ActivationFailure",
    "ActivationResult",
    "ActivationStatus",
    "ActivationSnapshot",
    
    # Rollback
    "ActivationRollbackPlan",
    "ActivationRollbackResult",
    "RollbackSnapshot",
    
    # Events
    "ActivationEvent",
    "ActivationEvents",
    
    # Configuration
    "ActivationConcurrencyConfig",
    "ActivationTimeoutConfig",
    "ActivationConfig",
]