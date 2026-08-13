# Base Execution Components
# =========================

"""
Base classes and protocols for execution components.

These provide the foundation that concrete implementations build upon.
They are intentionally minimal - semantic behavior comes from composition,
not inheritance.
"""

from abc import ABC, abstractmethod
from typing import Protocol, Any, Optional, List, Dict
from dataclasses import dataclass, field
import uuid


# =============================================================================
# Base Thread
# =============================================================================

@dataclass
class ExecutionThread(ABC):
    """
    Abstract base class for execution threads.
    
    A thread is a long-lived semantic identity that owns:
        - Persistent identity (id, name, purpose)
        - Thread-local context (working memory, objectives)
        - Lifecycle intent (when to terminate)
        - Loop binding (which policy drives cycle selection)
    
    Core owns the actual scheduling and execution mechanics.
    
    Invariants:
        T-001: Every active thread has exactly one loop binding
        T-002: Thread state changes must be atomic and logged
        T-003: A thread may not directly invoke another thread's execution
    """
    
    # Identity (required - no defaults)
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    name: str = "unnamed_thread"
    
    # Purpose (what this thread is trying to accomplish)
    purpose: Optional[str] = None
    
    # Loop binding (policy for cycle selection)
    loop_binding: Optional[Any] = None  # Type will be determined by implementation
    
    # Lifecycle state
    active: bool = False
    paused: bool = False
    
    # Semantic state (owned by thread)
    working_memory: Dict[str, Any] = field(default_factory=dict)
    
    def __post_init__(self) -> None:
        """Initialize after dataclass fields are set."""
        if not self.id:
            self.id = str(uuid.uuid4())
    
    @property
    def is_running(self) -> bool:
        """Check if thread is actively running (not paused or terminated)."""
        return self.active and not self.paused
    
    @abstractmethod
    async def run(self) -> None:
        """
        Execute the thread's lifecycle.
        
        This method:
            - Runs until completion_condition() returns True
            - Uses loop_binding to select cycles
            - Updates working_memory based on cycle results
            - Requests lifecycle transitions through Core
        
        Note: This is NOT a while-true loop. It's one semantic pass.
              Repetition is the Loop's responsibility, not the Thread's.
        """
        ...
    
    @abstractmethod
    def completion_condition(self) -> bool:
        """
        Check if this thread has completed its purpose.
        
        Returns True when:
            - All objectives have been achieved
            - No more meaningful work can be done
            - External conditions indicate termination is appropriate
        
        This is the thread's semantic view of "done", not a runtime state.
        """
        ...
    
    @abstractmethod
    def local_context(self) -> Dict[str, Any]:
        """
        Return thread-local context for cycle execution.
        
        This includes:
            - Current objectives
            - Working memory snapshot
            - Relevant history
        
        The returned context should be immutable or a deep copy to prevent
        concurrent modification issues.
        """
        ...
    
    @abstractmethod
    def export_semantic_snapshot(self) -> Dict[str, Any]:
        """
        Export semantic state for persistence and recovery.
        
        This should include:
            - Thread identity (id, name, purpose)
            - Current objectives
            - Working memory that must survive restart
            - Continuation information (where to resume)
        
        Core handles the actual storage; this just provides the data.
        """
        ...
    
    def request_termination(self) -> None:
        """Request thread termination through lifecycle interface."""
        self.active = False
    
    def request_pause(self) -> None:
        """Request thread pause."""
        if self.active:
            self.paused = True
    
    def resume(self) -> None:
        """Resume a paused thread."""
        if self.paused:
            self.paused = False
            self.active = True


# =============================================================================
# Base Loop (DEPRECATED - Use canonical Loop from execution.loops)
# =============================================================================
#
# NOTE: This class is deprecated. The canonical Loop architecture has been
# implemented in src/agent/execution/loops/__init__.py with proper separation of:
#   - Behavioral policy (owned by Loop)
#   - Semantic computation (owned by Capabilities) 
#   - Runtime scheduling (owned by Core)
#
# Migration path: Replace imports from base.ExecutionLoop with:
#   from agent.execution.loops import ExecutionLoop, StandardPolicy, LoopContext

class ExecutionLoop(ABC):
    """
    Abstract base class for execution loops.
    
    DEPRECATED: This class uses an older API pattern.
    Use src/agent/execution/loops/__init__.py instead.
    
    Canonical Loop Responsibilities:
        - Behavioral policy: decide what to do next based on thread state + cycle outcome
        - Cycle selection policy: choose which cycle to execute  
        - Continuation policy: decide whether to continue, suspend, complete, etc.
        - Interpretation of Cycle outcomes
        - Policy-local adaptation state
    
    Canonical Loop Must NOT Own:
        - Execute reasoning or planning algorithms (Capabilities do this)
        - Invoke model runtimes directly (Core does this through Cycles)
        - Own Thread continuity (Thread owns this)
        - Mutate Thread state arbitrarily (Thread accepts deltas)
        - Execute Stage logic (Cycles execute stages)
        - Allocate runtime resources (Core does this)
    """
    
    # This base class is kept for backward compatibility but should not be used
    # for new implementations. All Loop functionality is now in:
    #   src/agent/execution/loops/__init__.py
    


# =============================================================================
# Base Cycle
# =============================================================================

@dataclass
class ExecutionStage:
    """
    A single semantic stage within a cycle.
    
    Each stage has:
        - Name and description
        - Preconditions (must be true before execution)
        - Execute function (performs the work)
        - Postconditions (must be true after execution)
    """
    
    name: str  # e.g., "observe", "reason", "decide"
    preconditions: Any = None  # Callable or predicate
    execute: Any = None  # Callable that performs the stage
    postconditions: Any = None  # Callable or predicate
    
    # Whether this stage can be interrupted
    interruptible: bool = True


class ExecutionCycle(ABC):
    """
    Abstract base class for execution cycles.
    
    A cycle is a finite, ordered sequence of semantic stages that:
        - Has explicit preconditions and postconditions
        - Performs one complete semantic pass over a task graph
        - Returns a result enum (COMPLETED, CONTINUE, WAIT, DELEGATE, FAIL)
    
    Invariants:
        S-001: Each stage must be reversible in intent (not necessarily state)
        S-002: Postcondition of S_i must imply precondition of S_{i+1}
    
    State machine:
        [READY] → [STAGE_0]
                   ↓
               [STAGE_i] ⇄ [INTERRUPTIBLE]
                   ↓
            [POSTCONDITION_CHECK]
                   ↓
          {COMPLETED, CONTINUE, WAIT, DELEGATE, FAIL}
    """
    
    # Identity (required - no defaults)
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    
    @property
    @abstractmethod
    def stages(self) -> List[ExecutionStage]:
        """
        Return the ordered list of semantic stages.
        
        Each stage must have:
            - A valid preconditions check
            - An executable function
            - A postconditions check
        
        The postcondition of each stage (except last) must imply
        the precondition of the next stage.
        """
        ...
    
    @property
    def current_stage_index(self) -> int:
        """Get index of currently executing stage."""
        return getattr(self, "_current_stage", 0)
    
    @abstractmethod
    async def execute(
        self,
        context: Dict[str, Any]
    ) -> str:
        """
        Execute all stages in sequence.
        
        Args:
            context: Working memory and execution context
        
        Returns:
            CycleResult value:
                - "completed": All stages completed successfully
                - "continue": May continue with another cycle
                - "wait": Cannot proceed, waiting for external event
                - "delegate": Defer to another unit
                - "fail": Execution failed
        
        This method handles:
            - Stage progression
            - Pre/post condition checks
            - Interruption handling
            - Result production
        """
        ...
    
    @abstractmethod
    def preconditions_met(self) -> bool:
        """Check if all preconditions for the cycle are satisfied."""
        ...
    
    @abstractmethod
    def postconditions_satisfied(self, result: Any) -> bool:
        """Check if postconditions are satisfied given a result."""
        ...
    
    def interrupt_at_boundary(self) -> None:
        """Mark current stage as interrupted at safe boundary."""
        pass
    
    def export_progress_state(self) -> Dict[str, Any]:
        """
        Export progress state for checkpointing.
        
        This includes:
            - Current stage index
            - Partial results from completed stages
            - Context needed to resume
        """
        return {
            "stage_index": self.current_stage_index,
        }


__all__ = [
    # Base classes
    "ExecutionThread",
    "ExecutionLoop",
    "ExecutionCycle",
    
    # Stage class
    "ExecutionStage",
]