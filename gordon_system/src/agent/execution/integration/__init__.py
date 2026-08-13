# Integration Layer for Execution Subsystem
# ============================================

"""
Integration layer providing composition and minimal integration paths.

This module provides:
    - Minimal execution flow implementations
    - Capability port interfaces
    - Runtime port interfaces
    - Composition root utilities

The integration layer connects the canonical Execution entities (Thread, Loop,
Cycle, Stage) with their runtime dependencies without creating circular
dependencies.
"""

from dataclasses import dataclass, field
from typing import Protocol, Optional, List, Dict, Any
from enum import Enum

# =============================================================================
# Capability Port (Execution → Runtime)
# =============================================================================


class CapabilityPort(Protocol):
    """
    Port for invoking Capabilities from Execution stages.
    
    Execution stages request capability invocations through this port.
    The Capability implementation handles the actual work.
    
    Invariants:
        CAP-001: Stage requests capabilities, does not select implementations
        CAP-002: Capability returns typed results, not raw runtime objects
        CAP-003: Capability invocation is bounded (not infinite)
    """
    
    async def invoke(
        self,
        capability_id: str,
        input_data: Any,
    ) -> "CapabilityOutcome":
        """Invoke a Capability with given input. Return typed outcome."""
        ...


@dataclass(frozen=True)
class CapabilityOutcome:
    """
    Result of a Capability invocation.
    
    This is what the Stage receives - a semantic result, not raw runtime output.
    """
    
    capability_id: str
    status: str  # "completed", "failed", "timeout"
    
    # Semantic result (not raw bytes/tensors)
    semantic_output: Optional[Any] = None
    
    # Failure information (semantic interpretation)
    failure_reason: Optional[str] = None
    is_runtime_failure: bool = False
    runtime_error_type: Optional[str] = None


# =============================================================================
# Runtime Port (Execution → Core)
# =============================================================================


class ExecutionRuntimePort(Protocol):
    """
    Port for requesting execution runtime support.
    
    This is how Execution requests runtime resources:
        - Submit work to Core scheduler
        - Request lifecycle transitions
        - Request checkpoints
    
    Invariants:
        RPT-001: Runtime requests are submitted, not commands
        RPT-002: Core decides scheduling and resource allocation
        RPT-003: Runtime does not own semantic state
    """
    
    async def submit_execution(
        self,
        execution_id: str,
        thread_revision: int,
        cycle_definition_id: str,
        stage_definitions: List["StageDefinition"],
    ) -> "ExecutionHandle":
        """Submit a Cycle for runtime execution."""
        ...
    
    async def request_lifecycle_transition(
        self,
        execution_id: str,
        from_state: str,
        to_state: str,
        reason: Optional[str] = None,
    ) -> "LifecycleTransitionResult":
        """Request a lifecycle state transition."""
        ...
    
    async def create_checkpoint(
        self,
        execution_id: str,
        snapshot_data: Dict[str, Any],
    ) -> str:
        """Create a checkpoint for persistence. Returns checkpoint ID."""
        ...


@dataclass(frozen=True)
class ExecutionHandle:
    """
    Handle for tracking runtime execution.
    
    This is Core's internal execution reference - not part of semantic state.
    """
    
    execution_id: str
    handle_id: str  # Core's runtime handle
    status: str  # One of RuntimeStatus values


@dataclass(frozen=True)
class LifecycleTransitionResult:
    """Result of a lifecycle transition request."""
    
    accepted: bool
    previous_state: Optional[str] = None
    current_state: Optional[str] = None
    rejection_reason: Optional[str] = None


# =============================================================================
# Stage Definition (for runtime integration)
# =============================================================================


@dataclass(frozen=True)
class StageDefinition:
    """
    Runtime stage definition for execution.
    
    This is the runtime-facing form of a Stage - it includes all information
    needed to execute the stage in the runtime environment.
    """
    
    stage_id: str
    name: str
    description: str = ""
    
    # Capability requirements (contract IDs, not implementations)
    required_capability_ids: List[str] = field(default_factory=list)
    
    # Pre/post conditions (for validation)
    precondition: Optional[str] = None
    postcondition: Optional[str] = None


# =============================================================================
# Minimal Execution Flow Components
# =============================================================================


class ExecutionFlow:
    """
    Base class for minimal execution flows.
    
    These provide the complete path from Thread to Outcome without requiring
    all the complex infrastructure.
    """
    
    def __init__(self, thread_id: str):
        self.thread_id = thread_id
        self._current_revision = 0
    
    @property
    def current_revision(self) -> int:
        """Get the current Thread revision."""
        return self._current_revision
    
    def _advance_revision(self) -> None:
        """Advance the Thread revision after accepting a delta."""
        self._current_revision += 1


class MinimalThread(ExecutionFlow):
    """
    Minimal ExecutionThread implementation for demonstration.
    
    This implements the canonical ExecutionThread interface with minimal
    dependencies. It's designed to demonstrate the integration flow, not
    be a production-ready implementation.
    """
    
    def __init__(self, thread_id: Optional[str] = None):
        super().__init__(thread_id or "minimal-thread")
        self._lifecycle_state = "created"
        self._active_loop_id: Optional[str] = None
        self._active_cycle_id: Optional[str] = None
    
    @property
    def lifecycle_state(self) -> str:
        """Get current lifecycle state."""
        return self._lifecycle_state
    
    @property
    def active_loop_id(self) -> Optional[str]:
        """Get the active Loop ID (if any)."""
        return self._active_loop_id
    
    @property
    def active_cycle_id(self) -> Optional[str]:
        """Get the active Cycle ID (if any)."""
        return self._active_cycle_id
    
    def activate(self, loop_id: str) -> None:
        """Activate this thread with a Loop."""
        if self._lifecycle_state != "created":
            raise ValueError(f"Cannot activate thread in state {self._lifecycle_state}")
        
        self._lifecycle_state = "active"
        self._active_loop_id = loop_id
    
    def complete(self) -> None:
        """Complete the thread successfully."""
        self._lifecycle_state = "completed"


class MinimalLoop(ExecutionFlow):
    """
    Minimal ExecutionLoop implementation for demonstration.
    
    This provides a simple policy that produces valid decisions based on
    available cycle definitions.
    """
    
    def __init__(self, thread_id: str, loop_id: Optional[str] = None):
        super().__init__(thread_id)
        self.loop_id = loop_id or "minimal-loop"
        self._current_mode = "active"
        self._iteration_count = 0
    
    @property
    def current_mode(self) -> str:
        """Get current behavioral mode."""
        return self._current_mode
    
    def evaluate(
        self,
        cycle_definitions: List[str],
        has_outcome: bool = False,
        outcome_status: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Evaluate the current state and produce a decision.
        
        This implements the canonical Loop evaluation behavior:
            - If no cycles available but objectives exist → request recovery
            - If cycle outcome indicates failure → terminate
            - If completion conditions met → complete thread
            - Otherwise → continue with first available cycle
        """
        self._iteration_count += 1
        
        if not has_outcome and cycle_definitions:
            # First iteration - start with first available cycle
            return {
                "decision_type": "CONTINUE",
                "cycle_definition_id": cycle_definitions[0],
                "thread_revision": self.current_revision,
                "rationale": "Starting thread execution",
            }
        
        if has_outcome and outcome_status == "failed":
            # Cycle failed - terminate the thread
            return {
                "decision_type": "TERMINATE",
                "thread_revision": self.current_revision,
                "rationale": f"Cycle failed: {outcome_status}",
            }
        
        if has_outcome and outcome_status == "completed":
            # Cycle completed successfully
            if self._iteration_count >= 1:
                # After one cycle, consider completion
                return {
                    "decision_type": "COMPLETE",
                    "thread_revision": self.current_revision,
                    "rationale": "Thread completed its purpose",
                }
        
        # Default: continue with available cycles
        if cycle_definitions:
            return {
                "decision_type": "CONTINUE",
                "cycle_definition_id": cycle_definitions[0],
                "thread_revision": self.current_revision,
                "rationale": "Continuing thread execution",
            }
        
        # No cycles and no clear direction - suspend
        return {
            "decision_type": "SUSPEND",
            "thread_revision": self.current_revision,
            "rationale": "No cycles available, suspending",
        }


class MinimalCycle(ExecutionFlow):
    """
    Minimal ExecutionCycle implementation for demonstration.
    
    This executes a simple sequence of stages and produces an outcome.
    """
    
    def __init__(
        self,
        cycle_id: Optional[str] = None,
        definition_id: str = "default-cycle",
        thread_id: Optional[str] = None,
        loop_decision_id: Optional[str] = None,
        source_revision: int = 0,
    ):
        super().__init__(thread_id or "minimal-cycle")
        self.cycle_id = cycle_id or "cycle-" + str(id(self))
        self.definition_id = definition_id
        self.loop_decision_id = loop_decision_id
        self.source_revision = source_revision
        
        self._stages: List[str] = ["stage-1", "stage-2"]
        self._current_stage_index = 0
        self._outcome_status = "pending"
    
    @property
    def current_stage_index(self) -> int:
        """Get the current stage index."""
        return self._current_stage_index
    
    def execute_stages(self) -> Dict[str, Any]:
        """
        Execute all stages in sequence and produce an outcome.
        
        Returns a dictionary with the cycle outcome including:
            - status: completion status
            - proposed_deltas: list of semantic deltas to propose to Thread
            - stage_results: results from each stage
        """
        stage_results = []
        
        for i, stage_id in enumerate(self._stages):
            self._current_stage_index = i
            
            # Simulate stage execution (in real implementation, this would
            # invoke capabilities and produce typed results)
            stage_result = {
                "stage_id": stage_id,
                "status": "completed",
                "semantic_output": f"Result from {stage_id}",
            }
            stage_results.append(stage_result)
        
        self._outcome_status = "completed"
        
        return {
            "cycle_id": self.cycle_id,
            "thread_id": self.thread_id,
            "source_thread_revision": self.source_revision,
            "status": "COMPLETED",
            "semantic_delta": {"changes": {"facts_accepted": ["cycle executed successfully"]}},
            "stage_results": stage_results,
        }


# =============================================================================
# Integration Utilities
# =============================================================================


def create_minimal_flow() -> Dict[str, Any]:
    """
    Create and execute a minimal complete execution flow.
    
    This demonstrates the full integration path:
        1. Create a Thread
        2. Attach a Loop to it
        3. The Loop evaluates and selects a Cycle definition
        4. Execute the Cycle
        5. Produce an outcome with deltas
        6. The Thread accepts deltas (advancing revision)
    
    Returns a dictionary containing:
        - thread: The final Thread state
        - loop: The Loop state
        - cycle: The Cycle execution result
        - deltas: Proposed deltas from the Cycle
        - new_revision: Updated Thread revision after accepting deltas
    """
    # Step 1: Create the Thread
    thread = MinimalThread()
    
    # Step 2: Attach a Loop to it
    loop = MinimalLoop(thread_id=thread.thread_id)
    thread.activate(loop.loop_id)  # This sets active_loop_id
    
    # Step 3: The Loop evaluates (first iteration, no prior outcome)
    initial_decision = loop.evaluate(
        cycle_definitions=["default-cycle", "interpretation"],
        has_outcome=False,
    )
    
    # Step 4: Execute the selected Cycle
    cycle = MinimalCycle(
        definition_id=initial_decision.get("cycle_definition_id", "default-cycle"),
        thread_id=thread.thread_id,
        source_revision=thread.current_revision,
    )
    
    outcome = cycle.execute_stages()
    
    # Step 5: Update Thread revision based on accepted deltas
    new_revision = thread.current_revision + len(outcome.get("semantic_delta", {}).get("changes", {}))
    thread._advance_revision()  # Actually advance the revision
    
    return {
        "thread": {
            "id": thread.thread_id,
            "lifecycle_state": thread.lifecycle_state,
            "revision": new_revision,
            "active_loop_id": thread.active_loop_id,
        },
        "loop": {
            "id": loop.loop_id,
            "current_mode": loop.current_mode,
            "iteration_count": loop._iteration_count,
        },
        "cycle": {
            "id": cycle.cycle_id,
            "definition_id": cycle.definition_id,
            "outcome_status": outcome.get("status"),
        },
        "deltas": outcome.get("semantic_delta", {}),
        "new_revision": new_revision,
    }


__all__ = [
    # Ports
    "CapabilityPort",
    "CapabilityOutcome",
    "ExecutionRuntimePort",
    
    # Runtime types
    "ExecutionHandle",
    "LifecycleTransitionResult",
    "StageDefinition",
    
    # Integration components
    "ExecutionFlow",
    "MinimalThread",
    "MinimalLoop",
    "MinimalCycle",
    
    # Utilities
    "create_minimal_flow",
]