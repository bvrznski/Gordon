# Core Runtime Lifecycle Coordinator
# ==================================

"""
Canonical runtime-wide lifecycle coordination for Phase 3.7.5-I.

Provides:
- Single authoritative coordinator for runtime activation
- Activation graph compilation and ordering
- Component delegation with dependency-aware scheduling
- Rollback coordination
- Event emission for observability
"""

from dataclasses import dataclass, field
from typing import Dict, List, Tuple, Optional, Any, Set
from enum import Enum
import asyncio
import threading
import time

from .activation import (
    ActivationState,
    ActivationNode,
    ActivationEdge,
    ActivationGraph,
    ActivationPlan,
    ActivationRequest,
    ActivationContext,
    ActivationResult,
    ActivationFailure,
    ActivationStatus,
    ActivationEvent,
    ActivationEvents,
    ActivationConfig,
    EntityId,
)


# =============================================================================
# COMPONENT LIFECYCLE CONTRACT
# =============================================================================

class LifecycleManagedEntity:
    """
    Protocol for lifecycle-managed entities that can be activated.
    
    This is the contract between the coordinator and individual components.
    Components must implement these methods to participate in runtime activation.
    """
    
    @property
    def entity_id(self) -> str:
        """Return unique entity identifier."""
        raise NotImplementedError
    
    @property
    def entity_type(self) -> str:
        """Return entity type (e.g., 'kernel', 'lifecycle', 'scheduler')."""
        raise NotImplementedError
    
    async def validate_activation(self, context: ActivationContext) -> bool:
        """
        Validate that this component can be activated.
        
        Returns:
            True if activation is valid, False otherwise
        """
        return True
    
    async def activate(self, context: ActivationContext) -> Tuple[bool, Optional[str]]:
        """
        Activate this component.
        
        Args:
            context: Activation context
            
        Returns:
            Tuple of (success, resource_id_if_any)
            
        Raises:
            Exception: On failure
        """
        raise NotImplementedError
    
    async def verify_activation(self, context: ActivationContext) -> bool:
        """
        Verify that activation was successful.
        
        This is called after the component is activated to confirm it's ready.
        
        Returns:
            True if verified, False otherwise
        """
        return True
    
    async def deactivate(self, context: ActivationContext) -> None:
        """
        Deactivate this component (for rollback).
        
        Args:
            context: Activation context
        """
        pass
    
    @property
    def activation_timeout(self) -> float:
        """Return timeout for activation in seconds."""
        return 30.0
    
    @property
    def dependencies(self) -> List[str]:
        """Return list of entity IDs this component depends on."""
        return []
    
    @property
    def is_critical(self) -> bool:
        """Return True if this component must succeed for overall activation."""
        return True
    
    @property
    def can_rollback(self) -> bool:
        """Return True if this component supports rollback."""
        return False


# =============================================================================
# ACTIVATION TRANSACTION
# =============================================================================

class ActivationTransactionState(Enum):
    """States of an activation transaction."""
    
    REQUESTED = "requested"
    VALIDATING = "validating"
    PLANNING = "planning"
    GRAPH_VERIFIED = "graph_verified"
    PLAN_COMMITTED = "plan_committed"
    ACTIVATING = "activating"
    VERIFYING = "verifying"
    COMMITTING = "committing"
    COMPLETED = "completed"
    ROLLING_BACK = "rolling_back"
    ROLLED_BACK = "rolled_back"
    FAILED = "failed"
    CANCELLED = "cancelled"


@dataclass(frozen=True)
class ActivationTransaction:
    """
    Represents one activation attempt as a transaction-like object.
    
    Tracks state, entities activated, failures, and rollback status.
    """
    
    transaction_id: str
    runtime_id: str
    activation_request: ActivationRequest
    state: ActivationTransactionState
    
    # Tracking
    activated_entities: Set[str] = field(default_factory=set)
    rolled_back_entities: Set[str] = field(default_factory=set)
    active_resources: List[Tuple[str, str]] = field(default_factory=list)  # (entity_id, resource_id)
    
    # Failures
    primary_failure: Optional[ActivationFailure] = None
    secondary_failures: List[ActivationFailure] = field(default_factory=list)
    
    # Timing
    start_time: float = field(default_factory=time.monotonic)
    end_time: Optional[float] = None
    
    def to_snapshot(self) -> "TransactionSnapshot":
        """Get immutable snapshot."""
        return TransactionSnapshot(
            transaction_id=self.transaction_id,
            runtime_id=self.runtime_id,
            state=self.state.value,
            activation_request=self.activation_request,
            activated_entities=list(self.activated_entities),
            rolled_back_entities=list(self.rolled_back_entities),
            active_resources=dict(self.active_resources) if self.active_resources else {},
            primary_failure=str(self.primary_failure) if self.primary_failure else None,
            elapsed_time=time.monotonic() - self.start_time
        )


@dataclass(frozen=True)
class TransactionSnapshot:
    """Immutable snapshot of activation transaction."""
    
    transaction_id: str
    runtime_id: str
    state: str
    activation_request: ActivationRequest
    activated_entities: List[str]
    rolled_back_entities: List[str]
    active_resources: Dict[str, str]
    primary_failure: Optional[str]
    elapsed_time: float


# =============================================================================
# LIFECYCLE COORDINATOR
# =============================================================================

class RuntimeLifecycleCoordinator:
    """
    Canonical runtime-wide lifecycle coordinator.
    
    This is the SINGLE canonical authority for:
    - Runtime activation coordination
    - Component ordering and scheduling
    - Rollback execution
    - State transition orchestration
    
    The coordinator:
    1. Builds the activation graph from entity metadata
    2. Compiles an immutable plan from the graph
    3. Executes the plan with dependency-aware ordering
    4. Handles failures and rollback
    5. Emits events for observability
    
    This is ONE authority alongside RuntimeStateStore. The coordinator
    manages lifecycle transitions; the state store records them.
    """
    
    def __init__(
        self,
        runtime_id: str,
        entities: Optional[List[LifecycleManagedEntity]] = None,
        config: Optional[ActivationConfig] = None
    ) -> None:
        import uuid
        
        self._runtime_id = runtime_id
        self._entities_by_id: Dict[str, LifecycleManagedEntity] = {}
        
        for entity in entities or []:
            self._entities_by_id[entity.entity_id] = entity
        
        self._config = config or ActivationConfig()
        self._lock = threading.Lock()
        
        # Transaction state
        self._current_transaction: Optional[ActivationTransaction] = None
        
        # Event queue (in real impl, would be a proper event bus)
        self._events: List[ActivationEvent] = []
    
    @property
    def runtime_id(self) -> str:
        """Get runtime ID."""
        return self._runtime_id
    
    @property
    def is_activated(self) -> bool:
        """Check if any transaction has completed activation."""
        with self._lock:
            if self._current_transaction:
                return self._current_transaction.state in (
                    ActivationTransactionState.COMPLETED,
                    ActivationTransactionState.ROLLED_BACK
                )
            return False
    
    @property
    def is_active(self) -> bool:
        """Check if runtime is currently active."""
        with self._lock:
            if self._current_transaction:
                return self._current_transaction.state == ActivationTransactionState.COMMITTED
            return False
    
    def register_entity(self, entity: LifecycleManagedEntity) -> None:
        """Register a lifecycle-managed entity."""
        with self._lock:
            self._entities_by_id[entity.entity_id] = entity
    
    def unregister_entity(self, entity_id: str) -> bool:
        """Unregister an entity by ID."""
        with self._lock:
            if entity_id in self._entities_by_id:
                del self._entities_by_id[entity_id]
                return True
            return False
    
    # ------------------------------------------------------------------
    # Graph Building
    # ------------------------------------------------------------------
    
    def build_activation_graph(self) -> ActivationGraph:
        """
        Build an activation graph from registered entities.
        
        Returns:
            A validated activation graph
            
        Raises:
            ValueError: If graph has cycles or invalid dependencies
        """
        nodes: List[ActivationNode] = []
        edges: List[ActivationEdge] = []
        
        for entity_id, entity in self._entities_by_id.items():
            # Create node
            node = ActivationNode(
                entity_id=entity.entity_id,
                entity_type=entity.entity_type,
                dependencies=tuple(entity.dependencies),
                activation_priority=0 if entity.is_critical else 100,
                timeout_seconds=entity.activation_timeout
            )
            nodes.append(node)
            
            # Create edges for each dependency
            for dep_id in entity.dependencies:
                edge = ActivationEdge(
                    from_node=entity_id,
                    to_node=dep_id,
                    required=True,
                    reason=f"{entity_id} depends on {dep_id}"
                )
                edges.append(edge)
        
        return ActivationGraph.create(nodes, edges)
    
    def compile_activation_plan(self) -> ActivationPlan:
        """
        Compile an activation plan from the current state.
        
        Returns:
            A compiled activation plan
            
        Raises:
            ValueError: If no entities registered or graph is invalid
        """
        if not self._entities_by_id:
            raise ValueError("No entities registered for activation")
        
        # Build and validate graph
        graph = self.build_activation_graph()
        
        # Compile plan from graph
        return ActivationPlan.compile(graph, ActivationState.ASSEMBLED)
    
    # ------------------------------------------------------------------
    # Activation Entry Points
    # ------------------------------------------------------------------
    
    async def request_activation(
        self,
        request: Optional[ActivationRequest] = None
    ) -> Tuple[ActivationTransaction, ActivationResult]:
        """
        Request runtime activation.
        
        This is the canonical entry point for activation. It:
        1. Validates the request
        2. Builds/validates the graph
        3. Compiles a plan
        4. Executes the plan
        
        Args:
            request: Optional activation request (creates one if not provided)
            
        Returns:
            Tuple of (transaction, result)
        """
        # Create default request if none provided
        if request is None:
            request = ActivationRequest.create(self._runtime_id)
        
        with self._lock:
            # Check for concurrent activation attempt
            if self._current_transaction and self._current_transaction.state in (
                ActivationTransactionState.ACTIVATING,
                ActivationTransactionState.ROLLING_BACK
            ):
                raise RuntimeError(
                    f"Activation already in progress: {self._current_transaction.transaction_id}"
                )
            
            # Create new transaction
            transaction = ActivationTransaction(
                transaction_id=f"{request.activation_id}",
                runtime_id=self._runtime_id,
                activation_request=request,
                state=ActivationTransactionState.REQUESTED
            )
            self._current_transaction = transaction
        
        try:
            # Step 1: Validate request
            transaction = self._validate_request(transaction, request)
            
            # Step 2: Build graph and validate
            transaction = self._build_and_validate_graph(transaction)
            
            # Step 3: Compile plan
            plan = self.compile_activation_plan()
            
            # Emit plan compiled event
            if self._config.events_enabled:
                event = ActivationEvents.plan_compiled(
                    runtime_id=self._runtime_id,
                    activation_id=request.activation_id,
                    graph_version=plan.graph_version
                )
                self._events.append(event)
            
            # Step 4: Execute activation plan
            result = await self._execute_plan(transaction, plan)
            
            return transaction, result
            
        except Exception as e:
            # Handle failure - transition to FAILED state
            with self._lock:
                if self._current_transaction:
                    self._current_transaction.state = ActivationTransactionState.FAILED
                    self._current_transaction.primary_failure = ActivationFailure(
                        step_id=-1,
                        entity_id=self._runtime_id,
                        failed_transition="activation_failed",
                        primary_cause=e
                    )
            
            # Emit failure event
            if self._config.events_enabled:
                event = ActivationEvents.failed(
                    runtime_id=self._runtime_id,
                    activation_id=request.activation_id,
                    error=e
                )
                self._events.append(event)
            
            return transaction, self._failure_result_from_error(e)
    
    def _validate_request(
        self,
        transaction: ActivationTransaction,
        request: ActivationRequest
    ) -> ActivationTransaction:
        """Validate the activation request."""
        with self._lock:
            # Check deadline
            if request.is_expired():
                raise RuntimeError(f"Activation request expired")
            
            # Check cancellation
            if request.cancellation_requested:
                transaction.state = ActivationTransactionState.CANCELLED
                return transaction
            
            # Check runtime state (would use state store in real impl)
            # For now, assume ASSEMBLED is valid source state
            
            transaction.state = ActivationTransactionState.VALIDATING
            return transaction
    
    def _build_and_validate_graph(
        self,
        transaction: ActivationTransaction
    ) -> ActivationTransaction:
        """Build and validate the activation graph."""
        try:
            graph = self.build_activation_graph()
            
            # Validate no cycles (already done by create() but double-check)
            if hasattr(graph, '_validate_no_cycles'):
                graph._validate_no_cycles()
            
            transaction.state = ActivationTransactionState.GRAPH_VERIFIED
            return transaction
            
        except ValueError as e:
            raise RuntimeError(f"Invalid activation graph: {e}")
    
    async def _execute_plan(
        self,
        transaction: ActivationTransaction,
        plan: ActivationPlan
    ) -> ActivationResult:
        """Execute the compiled activation plan."""
        with self._lock:
            transaction.state = ActivationTransactionState.ACTIVATING
        
        if self._config.events_enabled:
            event = ActivationEvents.started(
                runtime_id=self._runtime_id,
                activation_id=transaction.activation_request.activation_id
            )
            self._events.append(event)
        
        activated_entities: List[str] = []
        rollback_entities: List[str] = []
        errors: Dict[str, Exception] = {}
        
        try:
            # Execute each layer in order
            for step in plan.steps:
                if transaction.state == ActivationTransactionState.CANCELLED:
                    raise RuntimeError("Activation cancelled")
                
                # Check deadline
                if transaction.activation_request.is_expired():
                    raise RuntimeError("Activation deadline exceeded")
                
                # Execute entities in this step (parallel within layer, but
                # since we don't have full async parallelism here, we'll do sequential)
                for entity_id in step.entity_ids:
                    entity = self._entities_by_id.get(str(entity_id))
                    if not entity:
                        continue
                    
                    context = transaction.activation_request.to_context()
                    
                    # Validate before activation
                    if not await entity.validate_activation(context):
                        raise RuntimeError(f"Entity {entity_id} validation failed")
                    
                    # Activate with timeout
                    try:
                        if self._config.events_enabled:
                            event = ActivationEvents.component_started(
                                runtime_id=self._runtime_id,
                                activation_id=context.activation_id,
                                entity_id=entity.entity_id
                            )
                            self._events.append(event)
                        
                        success, resource_id = await asyncio.wait_for(
                            entity.activate(context),
                            timeout=step.timeout_seconds
                        )
                        
                        if not success:
                            raise RuntimeError(f"Entity {entity_id} activation failed")
                        
                        # Verify activation
                        if self._config.verify_activation:
                            if not await entity.verify_activation(context):
                                raise RuntimeError(f"Entity {entity_id} verification failed")
                        
                        activated_entities.append(str(entity_id))
                        
                        if resource_id:
                            with self._lock:
                                transaction.active_resources.append((str(entity_id), resource_id))
                        
                        if self._config.events_enabled:
                            event = ActivationEvents.component_activated(
                                runtime_id=self._runtime_id,
                                activation_id=context.activation_id,
                                entity_id=entity.entity_id
                            )
                            self._events.append(event)
                    
                    except asyncio.TimeoutError as e:
                        errors[str(entity_id)] = e
                        if entity.is_critical:
                            raise
                    except Exception as e:
                        errors[str(entity_id)] = e
                        if entity.is_critical:
                            raise
                
                # Check if any critical entities failed in this layer
                for eid, err in errors.items():
                    if self._entities_by_id.get(str(eid), None):
                        if self._entities_by_id[str(eid)].is_critical:
                            raise err
            
            # Commit to ACTIVE state
            with self._lock:
                transaction.state = ActivationTransactionState.COMMITTING
            
            with self._lock:
                transaction.state = ActivationTransactionState.COMPLETED
            
            # Emit completion event
            if self._config.events_enabled:
                event = ActivationEvents.completed(
                    runtime_id=self._runtime_id,
                    activation_id=transaction.activation_request.activation_id,
                    final_state="active"
                )
                self._events.append(event)
            
            return ActivationResult.success_result(
                activation_id=transaction.activation_request.activation_id,
                runtime_id=self._runtime_id,
                activated_entities=[str(eid) for eid in plan.steps[0].entity_ids if str(eid) in activated_entities],
                active_resources=[r for _, r in transaction.active_resources]
            )
            
        except Exception as e:
            # Activation failed - initiate rollback
            return await self._handle_activation_failure(
                transaction, plan, activated_entities, errors, e
            )
    
    async def _handle_activation_failure(
        self,
        transaction: ActivationTransaction,
        plan: ActivationPlan,
        activated_entities: List[str],
        errors: Dict[str, Exception],
        primary_error: Exception
    ) -> ActivationResult:
        """Handle activation failure with rollback."""
        with self._lock:
            if not transaction.primary_failure:
                transaction.primary_failure = ActivationFailure(
                    step_id=-1,
                    entity_id=self._runtime_id,
                    failed_transition="activation_failed",
                    primary_cause=primary_error
                )
        
        # Rollback activated entities in reverse order
        rollback_entities: List[str] = []
        
        if self._config.events_enabled:
            event = ActivationEvents.rollback_started(
                runtime_id=self._runtime_id,
                activation_id=transaction.activation_request.activation_id
            )
            self._events.append(event)
        
        try:
            # Rollback in reverse order (reverse topological sort)
            rollback_order = list(reversed(activated_entities))
            
            for entity_id in rollback_order:
                if entity_id not in self._entities_by_id:
                    continue
                
                entity = self._entities_by_id[entity_id]
                
                if self._config.events_enabled:
                    event = ActivationEvents.component_rollback_started(
                        runtime_id=self._runtime_id,
                        activation_id=transaction.activation_request.activation_id,
                        entity_id=EntityId(entity_id)
                    )
                    self._events.append(event)
                
                try:
                    context = transaction.activation_request.to_context()
                    
                    if await asyncio.wait_for(
                        entity.deactivate(context),
                        timeout=30.0
                    ):
                        rollback_entities.append(entity_id)
                        
                        if self._config.events_enabled:
                            event = ActivationEvents.component_rolled_back(
                                runtime_id=self._runtime_id,
                                activation_id=context.activation_id,
                                entity_id=EntityId(entity_id)
                            )
                            self._events.append(event)
                except Exception as de:
                    # Record rollback failure but don't stop
                    with self._lock:
                        transaction.secondary_failures.append(ActivationFailure(
                            step_id=-1,
                            entity_id=EntityId(entity_id),
                            failed_transition="rollback_failed",
                            primary_cause=de
                        ))
            
            with self._lock:
                for eid in rollback_entities:
                    transaction.rolled_back_entities.add(eid)
        
        except Exception as e:
            # Rollback itself failed - this is severe
            pass
        
        # Return partial failure result
        return ActivationResult.failure_result(
            activation_id=transaction.activation_request.activation_id,
            runtime_id=self._runtime_id,
            failed_entity=EntityId(str(primary_error)[:50]),
            primary_failure=transaction.primary_failure,
            activated_before_failure=activated_entities,
            rolled_back_entities=rollback_entities
        )
    
    def _failure_result_from_error(self, error: Exception) -> ActivationResult:
        """Create a failure result from an exception."""
        return ActivationResult.failure_result(
            activation_id="unknown",
            runtime_id=self._runtime_id,
            failed_entity=EntityId("runtime"),
            primary_failure=ActivationFailure(
                step_id=-1,
                entity_id=EntityId("runtime"),
                failed_transition="activation_failed",
                primary_cause=error
            ),
            activated_before_failure=[],
            rolled_back_entities=[]
        )
    
    # ------------------------------------------------------------------
    # Rollback Entry Point
    # ------------------------------------------------------------------
    
    async def request_rollback(self) -> ActivationResult:
        """
        Request rollback of the current activation.
        
        Returns:
            Result of rollback operation
        """
        with self._lock:
            if not self._current_transaction:
                return ActivationResult(
                    activation_id="none",
                    runtime_id=self._runtime_id,
                    status=ActivationStatus.COMPLETED,
                    source_state=ActivationState.ASSEMBLED,
                    final_state=ActivationState.STOPPED,
                    activated_entity_ids=(),
                    rolled_back_entity_ids=(),
                    active_resource_ids=()
                )
            
            transaction = self._current_transaction
            if transaction.state == ActivationTransactionState.ROLLED_BACK:
                return ActivationResult(
                    activation_id=transaction.activation_request.activation_id,
                    runtime_id=self._runtime_id,
                    status=ActivationStatus.COMPLETED,
                    source_state=transaction.activation_request.expected_source_state,
                    final_state=ActivationState.STOPPED,
                    activated_entity_ids=tuple(transaction.activated_entities),
                    rolled_back_entity_ids=tuple(transaction.rolled_back_entities),
                    active_resource_ids=tuple(r for _, r in transaction.active_resources)
                )
        
        # Build rollback plan and execute
        try:
            graph = self.build_activation_graph()
            plan = ActivationPlan.compile(graph, ActivationState.ACTIVE)
            
            with self._lock:
                transaction.state = ActivationTransactionState.ROLLING_BACK
            
            # Get rollback entities
            entities_to_rollback = list(reversed(list(transaction.activated_entities)))
            
            for entity_id in entities_to_rollback:
                if entity_id not in self._entities_by_id:
                    continue
                
                entity = self._entities_by_id[entity_id]
                
                try:
                    await entity.deactivate(
                        transaction.activation_request.to_context()
                    )
                except Exception as e:
                    with self._lock:
                        transaction.secondary_failures.append(ActivationFailure(
                            step_id=-1,
                            entity_id=EntityId(entity_id),
                            failed_transition="rollback_failed",
                            primary_cause=e
                        ))
            
            with self._lock:
                for eid in entities_to_rollback:
                    transaction.rolled_back_entities.add(eid)
                
                transaction.state = ActivationTransactionState.ROLLED_BACK
            
            return ActivationResult(
                activation_id=transaction.activation_request.activation_id,
                runtime_id=self._runtime_id,
                status=ActivationStatus.COMPLETED,
                source_state=transaction.activation_request.expected_source_state,
                final_state=ActivationState.STOPPED,
                activated_entity_ids=tuple(transaction.activated_entities),
                rolled_back_entity_ids=tuple(entities_to_rollback),
                active_resource_ids=tuple(r for _, r in transaction.active_resources)
            )
            
        except Exception as e:
            with self._lock:
                if not transaction.primary_failure:
                    transaction.primary_failure = ActivationFailure(
                        step_id=-1,
                        entity_id=EntityId("runtime"),
                        failed_transition="rollback_failed",
                        primary_cause=e
                    )
            
            return ActivationResult.failure_result(
                activation_id=transaction.activation_request.activation_id,
                runtime_id=self._runtime_id,
                failed_entity=EntityId("runtime"),
                primary_failure=transaction.primary_failure,
                activated_before_failure=list(transaction.activated_entities),
                rolled_back_entities=list(transaction.rolled_back_entities)
            )
    
    # ------------------------------------------------------------------
    # Query Methods
    # ------------------------------------------------------------------
    
    def get_transaction(self) -> Optional[ActivationTransaction]:
        """Get current transaction (if any)."""
        with self._lock:
            return self._current_transaction
    
    def get_events(self, since_timestamp: Optional[float] = None) -> List[ActivationEvent]:
        """Get events, optionally filtered by timestamp."""
        with self._lock:
            if since_timestamp is None:
                return list(self._events)
            
            return [e for e in self._events if e.timestamp >= since_timestamp]
    
    def get_snapshot(self) -> "LifecycleCoordinatorSnapshot":
        """Get immutable snapshot of coordinator state."""
        with self._lock:
            transaction = self._current_transaction
            
            return LifecycleCoordinatorSnapshot(
                runtime_id=self._runtime_id,
                entity_count=len(self._entities_by_id),
                has_active_transaction=transaction is not None,
                transaction_state=transaction.state.value if transaction else None,
                transaction_id=transaction.transaction_id if transaction else None,
                event_count=len(self._events),
                activated_entity_ids=list(transaction.activated_entities) if transaction else [],
                rolled_back_entity_ids=list(transaction.rolled_back_entities) if transaction else []
            )


@dataclass(frozen=True)
class LifecycleCoordinatorSnapshot:
    """Immutable snapshot of lifecycle coordinator state."""
    
    runtime_id: str
    entity_count: int
    has_active_transaction: bool
    transaction_state: Optional[str]
    transaction_id: Optional[str]
    event_count: int
    activated_entity_ids: List[str]
    rolled_back_entity_ids: List[str]


# =============================================================================
# PUBLIC API
# =============================================================================

__all__ = [
    # Protocol
    "LifecycleManagedEntity",
    
    # Transaction
    "ActivationTransactionState",
    "ActivationTransaction",
    "TransactionSnapshot",
    
    # Coordinator
    "RuntimeLifecycleCoordinator",
    "LifecycleCoordinatorSnapshot",
]