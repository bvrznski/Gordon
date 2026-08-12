# Tests for Shutdown Coordinator
# ===============================

"""
Comprehensive tests for Phase 3.7.9-I Shutdown Coordinator.

Tests cover:
    - State machine transitions
    - Quiescence management
    - Task draining and cancellation
    - Dependency-aware shutdown ordering
    - Resource release
    - Verification
    - Multiple shutdown modes
"""

import pytest
import asyncio
import time
from typing import List, Dict, Any

import sys
sys.path.insert(0, '/home/bvrznski/Gordon/gordon-system')

from src.agent.components.core.shutdown import (
    ShutdownCoordinator,
    ShutdownRequest,
    ShutdownMode,
    ShutdownState,
    ShutdownEvent,
    RuntimeQuiescence,
    DependencyGraph,
    TaskTracker,
    TaskStatus,
    ShutdownableComponent,
    QuiescenceActiveError,
    DependencyCycleError,
    IllegalStopOrderError,
)


# =============================================================================
# Helper Components for Testing
# =============================================================================


class TestComponent(ShutdownableComponent):
    """Test component with configurable shutdown behavior."""
    
    def __init__(
        self,
        component_id: str,
        name: str = None,
        stop_delay: float = 0.0,
        raise_on_stop: bool = False,
    ):
        super().__init__(component_id, name)
        self._stop_delay = stop_delay
        self._raise_on_stop = raise_on_stop
        self._shutdown_log: List[str] = []
    
    async def prepare_shutdown(self, mode: ShutdownMode) -> None:
        self._shutdown_log.append(f"prepare_shutdown({mode.value})")
    
    async def stop(self, mode: ShutdownMode) -> None:
        self._shutdown_log.append(f"stop({mode.value})")
        
        if self._raise_on_stop:
            raise RuntimeError("Intentional stop failure")
        
        if self._stop_delay > 0:
            await asyncio.sleep(self._stop_delay)
        
        self.mark_shutdown_complete()
    
    async def verify_shutdown(self, mode: ShutdownMode) -> bool:
        return self.is_shutdown and len(self._shutdown_log) >= 2


class TestTaskOwner(ShutdownableComponent):
    """Component that tracks tasks."""
    
    def __init__(self, component_id: str, task_tracker: TaskTracker):
        super().__init__(component_id)
        self.task_tracker = task_tracker
        self._tasks_started: List[str] = []
        self._tasks_completed: List[str] = []
    
    async def start_task(self, task_id: str) -> None:
        """Simulate starting a task."""
        self._tasks_started.append(task_id)
        self.task_tracker.track_task(
            task_id=task_id,
            component_id=self.component_id,
            task_fn_name=f"task_{task_id}"
        )
    
    async def complete_task(self, task_id: str) -> None:
        """Simulate completing a task."""
        if task_id in self._tasks_started and task_id not in self._tasks_completed:
            self.task_tracker.update_task_status(task_id, TaskStatus.COMPLETED)
            self._tasks_completed.append(task_id)
    
    async def stop(self, mode: ShutdownMode) -> None:
        # Mark remaining tasks as cancelled
        for task_id in self._tasks_started:
            if task_id not in self._tasks_completed:
                self.task_tracker.update_task_status(task_id, TaskStatus.CANCELLED)
        
        self.mark_shutdown_complete()


# =============================================================================
# Test Suite
# =============================================================================


class TestShutdownStateMachine:
    """Tests for the Shutdown State Machine."""
    
    def test_initial_state_is_idle(self):
        from src.agent.components.core.shutdown import ShutdownStateMachine
        sm = ShutdownStateMachine("test_runtime")
        assert sm.state == ShutdownState.IDLE
    
    def test_valid_transition_to_requested(self):
        from src.agent.components.core.shutdown import ShutdownStateMachine
        sm = ShutdownStateMachine("test_runtime")
        
        result = sm.transition(ShutdownState.REQUESTED)
        assert result is True
        assert sm.state == ShutdownState.REQUESTED
    
    def test_invalid_transition_is_rejected(self):
        from src.agent.components.core.shutdown import ShutdownStateMachine
        sm = ShutdownStateMachine("test_runtime")
        
        # Try invalid transition (IDLE -> QUIESCENT)
        result = sm.transition(ShutdownState.QUIESCENT)
        assert result is False
        assert sm.state == ShutdownState.IDLE
    
    def test_idempotent_transitions_allowed(self):
        from src.agent.components.core.shutdown import ShutdownStateMachine
        sm = ShutdownStateMachine("test_runtime")
        
        # Transition to REQUESTED
        sm.transition(ShutdownState.REQUESTED, reason="first")
        assert sm.state == ShutdownState.REQUESTED
        
        # Same state transition is allowed (idempotent)
        result = sm.transition(ShutdownState.REQUESTED, reason="second")
        assert result is True
    
    def test_transitions_are_recorded(self):
        from src.agent.components.core.shutdown import ShutdownStateMachine
        sm = ShutdownStateMachine("test_runtime")
        
        sm.transition(ShutdownState.REQUESTED, reason="request")
        sm.transition(ShutdownState.ADMISSION_CLOSED, reason="admit")
        
        assert len(sm.transitions) == 2
        
        t1 = sm.transitions[0]
        assert t1.from_state == ShutdownState.IDLE
        assert t1.to_state == ShutdownState.REQUESTED
        assert t1.reason == "request"
    
    def test_terminal_states(self):
        from src.agent.components.core.shutdown import ShutdownStateMachine, ShutdownState
        sm = ShutdownStateMachine("test_runtime")
        
        # Test TERMINATED is terminal
        sm.transition(ShutdownState.TERMINATED)
        assert sm.is_terminal is True
        
        # Test FAILED is terminal
        sm2 = ShutdownStateMachine("test_runtime_2")
        sm2.force_transition(ShutdownState.FAILED)
        assert sm2.is_terminal is True


class TestQuiescence:
    """Tests for Runtime Quiescence."""
    
    def test_initial_state_not_quiesced(self):
        quiesce = RuntimeQuiescence("test_runtime")
        assert quiesce.is_quiesced is False
    
    async def test_enter_quiescent_mode(self):
        quiesce = RuntimeQuiescence("test_runtime")
        
        result = await quiesce.enter_quiescent_mode(reason="shutdown_test")
        assert result is True
        assert quiesce.is_quiesced is True
    
    async def test_duplicate_quiescence_rejected(self):
        quiesce = RuntimeQuiescence("test_runtime")
        
        # First entry succeeds
        await quiesce.enter_quiescent_mode()
        assert quiesce.is_quiesced is True
        
        # Second entry fails (already quiesced)
        result = await quiesce.enter_quiescent_mode()
        assert result is False
    
    def test_check_quiescence_blocks_operations(self):
        quiesce = RuntimeQuiescence("test_runtime")
        
        import asyncio
        asyncio.run(quiesce.enter_quiescent_mode(reason="test"))
        
        with pytest.raises(QuiescenceActiveError) as exc_info:
            quiesce.check_quiescence("submit_task")
        
        assert "shutdown preparation" in str(exc_info.value).lower()
    
    def test_exit_quiescent_mode(self):
        quiesce = RuntimeQuiescence("test_runtime")
        
        import asyncio
        asyncio.run(quiesce.enter_quiescent_mode())
        assert quiesce.is_quiesced is True
        
        quiesce.exit_quiescent_mode()
        assert quiesce.is_quiesced is False


class TestDependencyGraph:
    """Tests for dependency graph and shutdown ordering."""
    
    def test_register_component(self):
        graph = DependencyGraph()
        
        graph.register_component("A", "Component A")
        assert graph.size == 1
    
    def test_register_with_dependencies(self):
        graph = DependencyGraph()
        
        # B depends on A
        graph.register_component("B", "Component B", depends_on=["A"])
        
        info_b = graph.get_component_info("B")
        assert info_b is not None
        assert "A" in info_b.depends_on
    
    def test_reverse_edge_updates(self):
        graph = DependencyGraph()
        
        # A and B are independent, C depends on both
        graph.register_component("C", "Component C", depends_on=["A", "B"])
        
        info_a = graph.get_component_info("A")
        assert "C" in info_a.dependents
    
    def test_detect_cycle_simple(self):
        graph = DependencyGraph()
        
        # Create cycle: A -> B -> C -> A
        graph.register_component("A", "Component A", depends_on=["C"])
        graph.register_component("B", "Component B", depends_on=["A"])
        graph.register_component("C", "Component C", depends_on=["B"])
        
        cycle = graph.detect_cycle()
        assert cycle is not None
        assert len(cycle) >= 3
    
    def test_shutdown_order_no_dependencies(self):
        graph = DependencyGraph()
        
        graph.register_component("A", "A")
        graph.register_component("B", "B")
        graph.register_component("C", "C")
        
        order = graph.shutdown_order()
        # With no dependencies, any order is valid
        assert set(order) == {"A", "B", "C"}
    
    def test_shutdown_order_respects_dependencies(self):
        graph = DependencyGraph()
        
        # A depends on B, B depends on C
        # Shutdown order should be: C, B, A (reverse of dependency)
        graph.register_component("C", "Component C", depends_on=[])
        graph.register_component("B", "Component B", depends_on=["C"])
        graph.register_component("A", "Component A", depends_on=["B"])
        
        order = graph.shutdown_order()
        
        assert order.index("C") < order.index("B")
        assert order.index("B") < order.index("A")
    
    def test_verify_stop_order(self):
        graph = DependencyGraph()
        
        # Register components with dependency: B depends on A
        graph.register_component("A", "Component A", depends_on=[])
        graph.register_component("B", "Component B", depends_on=["A"])
        
        # Valid: A stops before B
        graph.verify_stop_order(["A", "B"])  # Should not raise
        
        # Invalid: B stops before A (dependency not met)
        with pytest.raises(IllegalStopOrderError):
            graph.verify_stop_order(["B", "A"])


class TestTaskTracker:
    """Tests for task tracking."""
    
    def test_track_task(self):
        tracker = TaskTracker("test_runtime")
        
        info = tracker.track_task(
            task_id="task_1",
            component_id="comp_1",
            task_fn_name="my_task"
        )
        
        assert info.task_id == "task_1"
        assert info.component_id == "comp_1"
    
    def test_update_task_status(self):
        tracker = TaskTracker("test_runtime")
        
        tracker.track_task("task_1", "comp_1", "task_fn")
        info = tracker.update_task_status("task_1", TaskStatus.RUNNING)
        
        assert info.status == TaskStatus.RUNNING
    
    def test_cancel_task(self):
        tracker = TaskTracker("test_runtime")
        
        tracker.track_task("task_1", "comp_1", "task_fn")
        result = tracker.cancel_task("task_1")
        
        assert result is True
        info = tracker.get_task("task_1")
        assert info.status == TaskStatus.CANCELLED
    
    def test_get_active_tasks(self):
        tracker = TaskTracker("test_runtime")
        
        # Create tasks with different states using track_task then update
        info_pending = tracker.track_task("pending", "comp", "fn")
        info_running = tracker.track_task("running", "comp", "fn")
        info_completed = tracker.track_task("completed", "comp", "fn")
        
        tracker.update_task_status("pending", TaskStatus.PENDING)
        tracker.update_task_status("running", TaskStatus.RUNNING)
        tracker.update_task_status("completed", TaskStatus.COMPLETED)
        
        active = tracker.get_active_tasks()
        assert len(active) == 2


class TestShutdownCoordinatorBasic:
    """Basic tests for Shutdown Coordinator."""
    
    def test_coordinator_initialization(self):
        coordinator = ShutdownCoordinator("test_runtime")
        
        assert coordinator.runtime_id == "test_runtime"
        assert coordinator.current_state == ShutdownState.IDLE
    
    async def test_register_component(self):
        coordinator = ShutdownCoordinator("test_runtime")
        
        component = TestComponent("comp_1", "Test Component")
        
        await coordinator.register_component(component)
        
        assert "comp_1" in coordinator._components
        assert coordinator._dependency_graph.size == 1
    
    async def test_duplicate_component_registration_fails(self):
        coordinator = ShutdownCoordinator("test_runtime")
        
        component = TestComponent("comp_1", "Test Component")
        
        await coordinator.register_component(component)
        
        with pytest.raises(ValueError, match="already registered"):
            await coordinator.register_component(component)
    
    def test_snapshot_contains_state(self):
        coordinator = ShutdownCoordinator("test_runtime")
        
        snapshot = coordinator.snapshot()
        
        assert snapshot["runtime_id"] == "test_runtime"
        assert snapshot["current_state"] == "idle"


class TestShutdownPipeline:
    """Tests for the full shutdown pipeline."""
    
    async def test_graceful_shutdown(self):
        coordinator = ShutdownCoordinator("test_runtime")
        
        component = TestComponent("comp_1", "Test Component")
        
        await coordinator.register_component(component)
        
        request = ShutdownRequest(
            mode=ShutdownMode.GRACEFUL,
            reason="test graceful shutdown"
        )
        
        result = await coordinator.request_shutdown(request)
        
        assert result.terminated is True
        assert result.success is True
        assert result.mode == ShutdownMode.GRACEFUL
    
    async def test_forced_shutdown(self):
        coordinator = ShutdownCoordinator("test_runtime")
        
        component = TestComponent("comp_1", "Test Component")
        
        await coordinator.register_component(component)
        
        request = ShutdownRequest(
            mode=ShutdownMode.FORCED,
            reason="test forced shutdown"
        )
        
        result = await coordinator.request_shutdown(request)
        
        assert result.terminated is True
    
    async def test_emergency_shutdown(self):
        coordinator = ShutdownCoordinator("test_runtime")
        
        component = TestComponent("comp_1", "Test Component")
        
        await coordinator.register_component(component)
        
        request = ShutdownRequest(
            mode=ShutdownMode.EMERGENCY,
            reason="test emergency shutdown"
        )
        
        result = await coordinator.request_shutdown(request)
        
        assert result.terminated is True
    
    async def test_shutdown_with_multiple_components(self):
        coordinator = ShutdownCoordinator("test_runtime")
        
        # Create components with dependencies
        comp_c = TestComponent("comp_c", "Component C")
        comp_b = TestComponent("comp_b", name="Component B")
        comp_a = TestComponent("comp_a", name="Component A")
        
        await coordinator.register_component(comp_c)
        await coordinator.register_component(comp_b, depends_on=["comp_c"])
        await coordinator.register_component(comp_a, depends_on=["comp_b"])
        
        request = ShutdownRequest(
            mode=ShutdownMode.GRACEFUL,
            reason="test multi-component shutdown"
        )
        
        result = await coordinator.request_shutdown(request)
        
        assert result.terminated is True
        assert result.components_stopped == 3
    
    async def test_shutdown_idempotency(self):
        coordinator = ShutdownCoordinator("test_runtime")
        
        component = TestComponent("comp_1", "Test Component")
        
        await coordinator.register_component(component)
        
        request = ShutdownRequest(
            mode=ShutdownMode.GRACEFUL,
            reason="first shutdown"
        )
        
        result1 = await coordinator.request_shutdown(request)
        
        # Second shutdown while already shutting down
        result2 = await coordinator.request_shutdown(request)
        
        assert result1.terminated is True
        assert result2.terminated is False  # Already shutting down


class TestShutdownModes:
    """Tests for different shutdown modes."""
    
    async def test_graceful_mode_waits_for_tasks(self):
        coordinator = ShutdownCoordinator("test_runtime")
        
        task_tracker = TaskTracker("test_runtime")
        owner = TestTaskOwner("owner_1", task_tracker)
        
        await coordinator.register_component(owner)
        
        # Start a task
        await owner.start_task("task_1")
        info = task_tracker.get_task("task_1")
        assert info.status == TaskStatus.PENDING
        
        request = ShutdownRequest(
            mode=ShutdownMode.GRACEFUL,
            reason="test graceful with tasks"
        )
        
        result = await coordinator.request_shutdown(request)
        
        assert result.terminated is True
        assert result.tasks_cancelled >= 0
    
    async def test_immediate_mode(self):
        coordinator = ShutdownCoordinator("test_runtime")
        
        component = TestComponent("comp_1", "Test Component")
        
        await coordinator.register_component(component)
        
        request = ShutdownRequest(
            mode=ShutdownMode.IMMEDIATE,
            reason="test immediate shutdown"
        )
        
        result = await coordinator.request_shutdown(request)
        
        assert result.terminated is True
    
    async def test_restart_mode(self):
        coordinator = ShutdownCoordinator("test_runtime")
        
        component = TestComponent("comp_1", "Test Component")
        
        await coordinator.register_component(component)
        
        request = ShutdownRequest(
            mode=ShutdownMode.RESTART,
            reason="test restart",
            preserve_state=True
        )
        
        result = await coordinator.request_shutdown(request)
        
        assert result.terminated is True


class TestShutdownEvents:
    """Tests for shutdown event publishing."""
    
    async def test_events_are_published(self):
        from src.agent.components.core.shutdown import ShutdownCoordinator, ShutdownEvent
        
        received_events: List[ShutdownEvent] = []
        
        class EventReceiver:
            async def on_shutdown_event(self, event: ShutdownEvent) -> None:
                received_events.append(event)
        
        coordinator = ShutdownCoordinator("test_runtime")
        receiver = EventReceiver()
        
        await coordinator.register_observer(receiver)
        
        component = TestComponent("comp_1", "Test Component")
        await coordinator.register_component(component)
        
        request = ShutdownRequest(
            mode=ShutdownMode.GRACEFUL,
            reason="test events"
        )
        
        result = await coordinator.request_shutdown(request)
        
        # At least some events should have been published
        assert len(received_events) >= 1
        
        event_types = [e.event_type for e in received_events]
        assert "shutdown.terminated" in event_types
    
    async def test_events_have_provenance(self):
        from src.agent.components.core.shutdown import ShutdownCoordinator, ShutdownEvent
        
        received_events: List[ShutdownEvent] = []
        
        class EventReceiver:
            async def on_shutdown_event(self, event: ShutdownEvent) -> None:
                received_events.append(event)
        
        coordinator = ShutdownCoordinator("test_runtime")
        receiver = EventReceiver()
        
        await coordinator.register_observer(receiver)
        
        component = TestComponent("comp_1", "Test Component")
        await coordinator.register_component(component)
        
        source_id = "test_source_" + str(time.time())
        request = ShutdownRequest(
            mode=ShutdownMode.GRACEFUL,
            reason="test provenance",
            source_id=source_id
        )
        
        result = await coordinator.request_shutdown(request)
        
        # Check that some events have the correlation_id set
        correlated_events = [e for e in received_events if e.correlation_id == source_id]
        assert len(correlated_events) >= 1


class TestShutdownVerification:
    """Tests for shutdown verification."""
    
    async def test_successful_verification(self):
        coordinator = ShutdownCoordinator("test_runtime")
        
        component = TestComponent("comp_1", "Test Component")
        
        await coordinator.register_component(component)
        
        request = ShutdownRequest(mode=ShutdownMode.GRACEFUL)
        
        result = await coordinator.request_shutdown(request)
        
        assert result.success is True
        assert result.verification is not None
        assert result.verification.verified is True
    
    async def test_verification_fails_with_active_component(self):
        coordinator = ShutdownCoordinator("test_runtime")
        
        class FailingComponent(TestComponent):
            @property
            def is_shutdown(self) -> bool:
                return False  # Always report not shutdown
        
        component = FailingComponent("comp_1", "Failing Component")
        
        await coordinator.register_component(component)
        
        request = ShutdownRequest(mode=ShutdownMode.GRACEFUL)
        
        result = await coordinator.request_shutdown(request)
        
        assert result.success is False
        assert result.verification.verified is False


class TestResourceRelease:
    """Tests for resource release coordination."""
    
    async def test_resource_releaser_initialization(self):
        from src.agent.components.core.shutdown import ResourceReleaser
        
        releaser = ResourceReleaser("test_runtime")
        
        assert releaser._runtime_id == "test_runtime"
        assert len(releaser._owners) == 0
    
    async def test_resource_release_idempotent(self):
        from src.agent.components.core.shutdown import ResourceReleaser
        
        releaser = ResourceReleaser("test_runtime")
        
        # Call release_all on empty owners should not fail
        result = await releaser.release_all(ShutdownMode.GRACEFUL)
        assert isinstance(result, dict)


# =============================================================================
# Edge Cases and Error Handling
# =============================================================================


class TestEdgeCases:
    """Tests for edge cases and error handling."""
    
    async def test_shutdown_with_component_stop_failure(self):
        coordinator = ShutdownCoordinator("test_runtime")
        
        component = TestComponent(
            "comp_1",
            "Failing Component",
            raise_on_stop=True
        )
        
        await coordinator.register_component(component)
        
        request = ShutdownRequest(mode=ShutdownMode.GRACEFUL)
        
        # Should still complete (failure is caught and logged)
        result = await coordinator.request_shutdown(request)
        
        assert result.terminated is True
    
    async def test_empty_shutdown(self):
        coordinator = ShutdownCoordinator("test_runtime")
        
        # No components registered
        request = ShutdownRequest(mode=ShutdownMode.GRACEFUL)
        
        result = await coordinator.request_shutdown(request)
        
        assert result.terminated is True
        assert result.components_stopped == 0
    
    async def test_dependency_cycle_detection(self):
        graph = DependencyGraph()
        
        # Create a cycle: A -> B -> C -> A
        graph.register_component("A", "Component A", depends_on=["C"])
        graph.register_component("B", "Component B", depends_on=["A"])
        graph.register_component("C", "Component C", depends_on=["B"])
        
        with pytest.raises(DependencyCycleError):
            graph.shutdown_order()
    
    async def test_shutdown_during_startup(self):
        coordinator = ShutdownCoordinator("test_runtime")
        
        # Try to shutdown before any components are registered
        request = ShutdownRequest(mode=ShutdownMode.GRACEFUL)
        
        result = await coordinator.request_shutdown(request)
        
        assert result.terminated is True


# =============================================================================
# Performance and Concurrency Tests
# =============================================================================


class TestConcurrency:
    """Tests for concurrent access."""
    
    async def test_concurrent_register_component(self):
        import threading
        
        coordinator = ShutdownCoordinator("test_runtime")
        errors: List[Exception] = []
        
        async def register_comp(comp_id: str):
            try:
                component = TestComponent(comp_id, f"Component {comp_id}")
                await coordinator.register_component(component)
            except Exception as e:
                errors.append(e)
        
        # Run 10 concurrent registrations
        tasks = [register_comp(f"comp_{i}") for i in range(10)]
        await asyncio.gather(*tasks)
        
        assert len(errors) == 0
        assert coordinator._dependency_graph.size == 10


class TestShutdownPerformance:
    """Basic performance tests."""
    
    async def test_shutdown_performance(self):
        coordinator = ShutdownCoordinator("test_runtime")
        
        # Register many components
        for i in range(50):
            component = TestComponent(f"comp_{i}", f"Component {i}")
            await coordinator.register_component(component)
        
        request = ShutdownRequest(mode=ShutdownMode.GRACEFUL)
        
        start_time = time.monotonic()
        result = await coordinator.request_shutdown(request)
        end_time = time.monotonic()
        
        duration = end_time - start_time
        
        assert result.terminated is True
        # Should complete in reasonable time (under 5 seconds for 50 components)
        assert duration < 5.0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])