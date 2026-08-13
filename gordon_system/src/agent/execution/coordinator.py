# Execution Coordinator Contract
# ===============================
#
# PHASE 3.10.10 - Agentic Execution Flow, Examples, and Guidelines

"""
Execution Coordinator - The top-level runtime advancement engine.

The Gordon agentic loop is NOT a concrete ExecutionLoop subtype.
It is the repeated orchestration of Threads through their active Loops,
one bounded Cycle at a time.

Ownership Model:
    Core / ExecutionCoordinator
        → runtime selection and activation

    ExecutionThread
        → semantic continuity and accepted state

    ExecutionLoop
        → continuation policy (which Cycle next?)

    ExecutionCycle
        → bounded semantic operation (Stage progression)

    ExecutionStage
        → bounded semantic transformation

The coordinator does NOT own:
    - Domain-specific planning, reasoning, conversation, recovery, or monitoring policy
    - Scheduling algorithms (that belongs to Core)
    - Resource arbitration (that belongs to Core)
    - Runtime execution mechanics (that belongs to Core)

The coordinator DOES own:
    - Selecting which Thread receives execution time
    - Advancing that Thread through its Loop and Cycle
    - Validating and applying proposed semantic deltas
    - Producing iteration results for traceability

Canonical Advancement Flow:
    1. Receive or select one runnable Thread
    2. Verify Thread is in advanceable lifecycle state
    3. Read immutable ThreadSnapshot
    4. Resolve Thread's active Loop
    5. Ask Loop for one LoopDecision
    6. If decision requests a Cycle:
          a. Materialize exactly one Cycle
          b. Bind to owning Thread and selecting Loop
          c. Execute its ordered Stages
          d. Produce exactly one CycleOutcome
          e. Produce exactly one proposed ThreadDelta
    7. Validate proposed ThreadDelta against expected Thread revision
    8. Commit or reject the ThreadDelta
    9. Give outcome and commit result back to Loop
    10. Obtain continuation decision from Loop
    11. Apply continuation decision to Thread
    12. Return ExecutionIterationResult to Core

One advancement must not execute an entire TaskThread to completion.
"""
from dataclasses import dataclass, field
from typing import Protocol, Optional, List, Dict, Any, Union, TypeVar, Generic
from enum import Enum, auto
import uuid


# =============================================================================
# Thread and Loop Identifiers (semantic)
# =============================================================================

class ThreadId(str):
    """Semantic identity for an ExecutionThread."""
    
    @classmethod
    def generate(cls) -> "ThreadId":
        return cls(uuid.uuid4().hex[:16])


class LoopId(str):
    """Semantic identity for an ExecutionLoop."""
    
    @classmethod
    def generate(cls) -> "LoopId":
        return cls(uuid.uuid4().hex[:16])


class CycleId(str):
    """Semantic identity for an ExecutionCycle."""
    
    @classmethod
    def generate(cls) -> "CycleId":
        return cls(uuid.uuid4().hex[:16])


# =============================================================================
# Loop Decision Types (Thread-local continuation)
# =============================================================================

class LoopDecisionKind(Enum):
    """
    Kinds of decisions a Loop can make about Thread continuation.
    
    These are Thread-local decisions, NOT global scheduling decisions:
        - START_CYCLE: Execute one Cycle with given definition
        - SWITCH_LOOP: Replace active Loop with new policy
        - AWAIT_INPUT: Wait for external input before continuing
        - AWAIT_CONDITION: Wait for a condition to become true
        - DELEGATE: Defer work to child Thread
        - YIELD: Give up execution time, allow other Threads
        - COMPLETE_THREAD: Mark Thread as completed successfully
        - FAIL_THREAD: Mark Thread as failed (recoverable)
        - TERMINATE_THREAD: Permanently terminate Thread
    
    A Loop decision must NOT:
        - Select another global Thread to run (coordinator does this)
        - Execute cycles directly (Cycles execute themselves)
        - Mutate Thread state directly (Thread accepts deltas)
    """
    
    START_CYCLE = "start_cycle"          # Start executing a Cycle
    SWITCH_LOOP = "switch_loop"          # Switch to different Loop policy
    AWAIT_INPUT = "await_input"          # Wait for external input
    AWAIT_CONDITION = "await_condition"  # Wait for condition to become true
    DELEGATE = "delegate"                # Defer to child Thread
    YIELD = "yield"                      # Yield execution time
    COMPLETE_THREAD = "complete_thread"  # Mark thread completed successfully
    FAIL_THREAD = "fail_thread"          # Mark thread failed (recoverable)
    TERMINATE_THREAD = "terminate_thread"  # Permanently terminate


@dataclass(frozen=True)
class LoopDecision:
    """
    A decision produced by a Loop about Thread continuation.
    
    This is the canonical output of Loop policy evaluation. It expresses
    what should happen next, without executing it directly.
    
    Invariants:
        D-001: Every decision references the thread revision it evaluated
        D-002: A terminal decision cannot select a Cycle
        D-003: Continuation decisions must include valid Cycle definition
        D-004: Decisions are validated before application
    
    Usage Examples:
        # Start executing a Cycle
        LoopDecision.start_cycle(
            cycle_definition=PlanningCycleDefinition(...),
        )
        
        # Switch to different Loop policy
        LoopDecision.switch_loop(
            target_loop=TaskLoopDefinition(...),
            reason="Plan committed successfully.",
        )
        
        # Wait for external input
        LoopDecision.await_input(
            reason="A required constraint remains unresolved.",
        )
    """
    
    # Core fields (required)
    decision_kind: LoopDecisionKind
    thread_id: str  # Which Thread is this affecting?
    thread_revision: int  # Which Thread revision was this evaluated against?
    
    # Rationale and metadata
    rationale: str = ""  # Why this decision was made
    
    # Optional payload based on kind
    cycle_definition: Optional[Any] = None  # For START_CYCLE decisions
    target_loop_definition: Optional[Any] = None  # For SWITCH_LOOP decisions
    condition: Optional["AwaitCondition"] = None  # For AWAIT_CONDITION decisions
    child_thread_id: Optional[str] = None  # For DELEGATE decisions
    
    @property
    def is_terminal(self) -> bool:
        """Check if this decision terminates the Thread."""
        return self.decision_kind in {
            LoopDecisionKind.COMPLETE_THREAD,
            LoopDecisionKind.FAIL_THREAD,
            LoopDecisionKind.TERMINATE_THREAD,
        }
    
    @property
    def is_continuation(self) -> bool:
        """Check if this decision continues with a Cycle."""
        return self.decision_kind == LoopDecisionKind.START_CYCLE
    
    # Factory methods for each decision kind
    @classmethod
    def start_cycle(
        cls,
        cycle_definition: Any,
        thread_id: str,
        thread_revision: int,
        rationale: str = "Starting Cycle execution",
    ) -> "LoopDecision":
        """Create a START_CYCLE decision."""
        return cls(
            decision_kind=LoopDecisionKind.START_CYCLE,
            thread_id=thread_id,
            thread_revision=thread_revision,
            rationale=rationale,
            cycle_definition=cycle_definition,
        )
    
    @classmethod
    def switch_loop(
        cls,
        target_loop_definition: Any,
        thread_id: str,
        thread_revision: int,
        reason: str = "Loop replacement requested",
    ) -> "LoopDecision":
        """Create a SWITCH_LOOP decision."""
        return cls(
            decision_kind=LoopDecisionKind.SWITCH_LOOP,
            thread_id=thread_id,
            thread_revision=thread_revision,
            rationale=reason,
            target_loop_definition=target_loop_definition,
        )
    
    @classmethod
    def await_input(
        cls,
        thread_id: str,
        thread_revision: int,
        reason: str = "Awaiting external input",
    ) -> "LoopDecision":
        """Create an AWAIT_INPUT decision."""
        return cls(
            decision_kind=LoopDecisionKind.AWAIT_INPUT,
            thread_id=thread_id,
            thread_revision=thread_revision,
            rationale=reason,
        )
    
    @classmethod
    def await_condition(
        cls,
        condition: "AwaitCondition",
        thread_id: str,
        thread_revision: int,
        reason: str = "Awaiting condition",
    ) -> "LoopDecision":
        """Create an AWAIT_CONDITION decision."""
        return cls(
            decision_kind=LoopDecisionKind.AWAIT_CONDITION,
            thread_id=thread_id,
            thread_revision=thread_revision,
            rationale=reason,
            condition=condition,
        )
    
    @classmethod
    def delegate(
        cls,
        child_thread_id: str,
        thread_id: str,
        thread_revision: int,
        reason: str = "Delegating work to child Thread",
    ) -> "LoopDecision":
        """Create a DELEGATE decision."""
        return cls(
            decision_kind=LoopDecisionKind.DELEGATE,
            thread_id=thread_id,
            thread_revision=thread_revision,
            rationale=reason,
            child_thread_id=child_thread_id,
        )
    
    @classmethod
    def yield_execution(
        cls,
        thread_id: str,
        thread_revision: int,
        reason: str = "Yielding execution time",
    ) -> "LoopDecision":
        """Create a YIELD decision."""
        return cls(
            decision_kind=LoopDecisionKind.YIELD,
            thread_id=thread_id,
            thread_revision=thread_revision,
            rationale=reason,
        )
    
    @classmethod
    def complete_thread(
        cls,
        thread_id: str,
        thread_revision: int,
        reason: str = "Thread completed successfully",
        outcome: Optional[Any] = None,
    ) -> "LoopDecision":
        """Create a COMPLETE_THREAD decision."""
        return cls(
            decision_kind=LoopDecisionKind.COMPLETE_THREAD,
            thread_id=thread_id,
            thread_revision=thread_revision,
            rationale=reason,
        )
    
    @classmethod
    def fail_thread(
        cls,
        thread_id: str,
        thread_revision: int,
        reason: str = "Thread failed",
        failure_reason: Optional[str] = None,
    ) -> "LoopDecision":
        """Create a FAIL_THREAD decision."""
        return cls(
            decision_kind=LoopDecisionKind.FAIL_THREAD,
            thread_id=thread_id,
            thread_revision=thread_revision,
            rationale=f"{reason}: {failure_reason or 'unknown'}",
        )
    
    @classmethod
    def terminate_thread(
        cls,
        thread_id: str,
        thread_revision: int,
        reason: str = "Thread terminated",
    ) -> "LoopDecision":
        """Create a TERMINATE_THREAD decision."""
        return cls(
            decision_kind=LoopDecisionKind.TERMINATE_THREAD,
            thread_id=thread_id,
            thread_revision=thread_revision,
            rationale=reason,
        )


@dataclass(frozen=True)
class AwaitCondition:
    """
    A condition that must become true before a Thread can continue.
    
    Examples:
        - Input arrived on a specific channel
        - Timer duration has elapsed
        - Child Thread completed with a result
        - External event occurred
    
    The Loop does NOT wait in place. The Coordinator suspends the Thread
    and later resumes it when the condition is satisfied.
    """
    
    condition_id: str = field(default_factory=lambda: uuid.uuid4().hex[:16])
    description: str = ""
    timeout_seconds: Optional[float] = None


# =============================================================================
# ThreadDeltaCommitResult (commit outcome)
# =============================================================================

class ThreadDeltaCommitResult(Enum):
    """
    Result of attempting to commit a proposed semantic delta.
    
    When a Cycle produces an outcome with a proposed ThreadDelta:
        - ACCEPTED: Delta was valid and applied
        - STALE_VERSION: Expected revision doesn't match current revision
        - INVALID_CONTENT: Content violates invariants or constraints
        - REJECTED: Loop rejected the delta for policy reasons
    
    The coordinator must NOT silently rewrite the expected revision.
    """
    
    ACCEPTED = "accepted"
    STALE_VERSION = "stale_version"
    INVALID_CONTENT = "invalid_content"
    REJECTED = "rejected"


@dataclass(frozen=True)
class CommitResult:
    """Result of attempting to commit a ThreadDelta."""
    
    result: ThreadDeltaCommitResult
    accepted_revision: Optional[int] = None  # If accepted, what's the new revision?
    rejection_reason: Optional[str] = None


# =============================================================================
# ExecutionIterationResult (one advancement outcome)
# =============================================================================

@dataclass(frozen=True)
class ExecutionIterationResult:
    """
    Result of one coordinator advancement.
    
    One advancement must execute at most one Cycle and produce exactly one
    result. This makes the execution deterministic, testable, and traceable.
    
    Fields:
        thread_id: Which Thread advanced?
        loop_id: Which Loop selected work? (None if no Loop attached)
        cycle_id: Which Cycle executed? (None if no Cycle executed)
        
        loop_decision: The initial decision from the Loop
        cycle_outcome: The outcome of the Cycle (if any)
        delta_commit_result: Did the proposed delta get accepted?
        continuation_decision: What should happen next? (from Loop after outcome)
        
        thread_revision_before: Revision at start of advancement
        thread_revision_after: Revision after advancement
        
        cycle_executed: True if a Cycle was executed this advancement
        loop_switched: True if the active Loop changed
        yielded: True if Thread yielded execution time
        suspended: True if Thread became suspended (awaiting input/condition)
        completed: True if Thread completed successfully
        failed: True if Thread failed
        
    Invariants:
        R-001: One advancement executes at most one Cycle
        R-002: One advancement produces exactly one result
        R-003: If cycle_executed is False, cycle_outcome must be None
        R-004: A terminal decision results in completed=True or failed=True
    """
    
    # Required fields first (no defaults)
    thread_id: str
    loop_decision: LoopDecision
    thread_revision_before: int
    thread_revision_after: int
    
    # Optional tracking IDs
    loop_id: Optional[LoopId] = None
    cycle_id: Optional[CycleId] = None
    
    # Optional outcomes and results
    cycle_outcome: Optional["CycleOutcome"] = None
    delta_commit_result: Optional[CommitResult] = None
    continuation_decision: Optional[LoopDecision] = None
    
    # Execution tracking (with defaults)
    cycle_executed: bool = False
    loop_switched: bool = False
    yielded: bool = False
    suspended: bool = False
    completed: bool = False
    failed: bool = False


# =============================================================================
# ThreadSnapshot (read-only view for Loop evaluation)
# =============================================================================

@dataclass(frozen=True)
class ThreadSnapshot:
    """
    Read-only snapshot of an ExecutionThread's state for Loop evaluation.
    
    Contains only semantic information needed for behavioral decisions.
    Does NOT contain runtime scheduling details or Core implementation references.
    
    Used by Loop to make cycle selection and continuation policy decisions.
    """
    
    thread_id: str
    thread_revision: int  # Semantic version
    
    # Lifecycle info
    lifecycle_state: str = "active"  # active, suspended, completed, etc.
    
    # Active components (at most one each)
    active_loop_id: Optional[str] = None
    active_cycle_id: Optional[str] = None
    
    # Semantic content (for policy decisions)
    purpose: Optional[str] = None
    active_objectives: List[str] = field(default_factory=list)
    
    # Relationships
    parent_thread_id: Optional[str] = None
    child_thread_ids: List[str] = field(default_factory=list)


# =============================================================================
# CycleOutcome (terminal result of one Cycle execution)
# =============================================================================

@dataclass(frozen=True)
class CycleOutcome:
    """
    Terminal outcome of a completed Cycle execution.
    
    Every Cycle must produce exactly one terminal outcome. This is the final
    semantic result that Loop interprets and Thread validates.
    
    Invariants:
        CO-001: Every Cycle produces exactly one outcome
        CO-002: Outcome is terminal (Cycle cannot continue from this)
        CO-003: Outcome contains proposed deltas (Thread must accept)
        CO-004: Outcome includes provenance for traceability
    """
    
    cycle_id: str
    thread_id: str
    
    # Status
    status: str  # completed, partially_completed, interrupted, failed
    
    # Source
    source_thread_revision: int
    loop_decision_id: Optional[str] = None
    
    # Semantic result
    semantic_delta: Optional["ThreadSemanticDelta"] = None
    completion_reason: str = ""
    
    # Stage results summary
    stage_results: List["StageResult"] = field(default_factory=list)
    stages_completed: int = 0


# =============================================================================
# ThreadSemanticDelta (proposed state change)
# =============================================================================

@dataclass(frozen=True)
class ThreadSemanticDelta:
    """
    Proposed change to Thread semantic state.
    
    A Cycle may propose changes to Thread state through deltas. The Thread
    validates and accepts or rejects these proposals - the Cycle cannot apply
    them directly.
    
    Invariants:
        SDT-001: Delta is proposed, not applied (Thread must accept)
        SDT-002: Delta references expected Thread revision for validation
        SDT-003: Delta contains only semantic information (no runtime state)
        SDT-004: Delta includes provenance for traceability
    """
    
    source_cycle_id: str  # Which Cycle produced this delta?
    expected_thread_revision: int  # Thread version at cycle start
    proposed_new_revision: int
    
    change_type: str  # e.g., "objective_completed", "fact_accepted"
    
    delta_id: str = field(default_factory=lambda: uuid.uuid4().hex[:16])
    changes: Dict[str, Any] = field(default_factory=dict)
    
    provenance: str = "cycle_outcome"


# =============================================================================
# StageResult (bounded transformation result)
# =============================================================================

@dataclass(frozen=True)
class StageResult:
    """
    Result of a single Stage execution within a Cycle.
    
    Invariants:
        SR-001: Each Stage produces exactly one result
        SR-002: Result is typed and semantically meaningful
        SR-003: Failure paths are explicit (no implicit exceptions)
        SR-004: Result contains only Stage-local information
    """
    
    stage_id: str
    cycle_id: str
    
    status: str  # completed, failed, skipped, interrupted
    semantic_output: Optional[Any] = None
    
    failure_reason: Optional[str] = None


# =============================================================================
# ExecutionCoordinator Contract (Protocol)
# =============================================================================

class ExecutionCoordinator(Protocol):
    """
    Protocol for the top-level execution advancement engine.
    
    The coordinator answers:
        "Which Thread should advance now?"
    
    The active Loop answers:
        "What should this Thread do next?"
    
    These responsibilities must remain separate.
    
    Responsibilities:
        1. Select or accept one runnable Thread
        2. Verify the Thread is in an advanceable lifecycle state
        3. Read an immutable ThreadSnapshot
        4. Resolve the Thread's active Loop
        5. Request one LoopDecision from the active Loop
        6. If decision requests a Cycle:
              - Materialize exactly one Cycle
              - Bind it to the owning Thread and selecting Loop
              - Execute its ordered Stages
              - Produce exactly one CycleOutcome
              - Produce exactly one proposed ThreadDelta
        7. Validate the proposed ThreadDelta against expected revision
        8. Commit or reject the ThreadDelta
        9. Apply the Loop continuation decision to the Thread
        10. Return an ExecutionIterationResult to Core
    
    One advancement must not execute an entire TaskThread to completion.
    
    The coordinator does NOT own:
        - Domain-specific planning, reasoning, conversation, recovery, or monitoring policy
        - Scheduling algorithms (Core owns this)
        - Runtime execution mechanics (Core owns this)
        - Resource arbitration (Core owns this)
    """
    
    async def advance_thread(
        self,
        thread_id: str,
        context: Optional[Dict[str, Any]] = None,
    ) -> ExecutionIterationResult:
        """
        Advance one Thread by at most one Cycle.
        
        Args:
            thread_id: Which Thread to advance
            context: Optional execution context for the advancement
            
        Returns:
            One ExecutionIterationResult describing what happened
            
        Invariants:
            - Executes at most one Cycle per call
            - Produces exactly one result
            - Does not mutate Thread state directly (Thread accepts deltas)
        """
        ...
    
    async def select_next_thread(
        self,
        runnable_threads: List[str],
        context: Optional[Dict[str, Any]] = None,
    ) -> Optional[str]:
        """
        Select which Thread should receive execution time.
        
        This is the coordinator's global scheduling responsibility.
        
        Args:
            runnable_threads: List of thread IDs that are ready to advance
            context: Execution context for selection
            
        Returns:
            The ID of the selected Thread, or None if no Thread is ready
        """
        ...
    
    async def create_thread(
        self,
        thread_id: Optional[str] = None,
        lifecycle_state: str = "created",
        purpose: Optional[str] = None,
        loop_id: Optional[str] = None,
    ) -> str:
        """
        Create a new Thread and return its ID.
        
        Args:
            thread_id: Optional explicit ID (generated if not provided)
            lifecycle_state: Initial lifecycle state
            purpose: Semantic purpose of the Thread
            loop_id: Initial Loop to attach (optional)
            
        Returns:
            The ThreadId of the created Thread
        """
        ...
    
    async def get_thread_snapshot(
        self,
        thread_id: str,
    ) -> ThreadSnapshot:
        """
        Get a read-only snapshot of a Thread's state.
        
        Args:
            thread_id: Which Thread to snapshot
            
        Returns:
            A ThreadSnapshot for Loop evaluation
        """
        ...
    
    async def commit_delta(
        self,
        thread_id: str,
        delta: ThreadSemanticDelta,
        current_revision: int,
    ) -> CommitResult:
        """
        Attempt to apply a proposed semantic delta to a Thread.
        
        Args:
            thread_id: Which Thread to update
            delta: The proposed change
            current_revision: Current Thread revision (for validation)
            
        Returns:
            CommitResult indicating success/failure and reason
        """
        ...


# =============================================================================
# SimpleExecutionCoordinator (Concrete Implementation for Examples)
# =============================================================================

class SimpleExecutionCoordinator:
    """
    A simple concrete ExecutionCoordinator implementation.
    
    This demonstrates the canonical advancement algorithm without all the
    infrastructure complexity. It's designed for examples and testing,
    not production use.
    
    Invariants enforced:
        - One advancement executes at most one Cycle
        - Thread state changes only through delta application
        - Loop switching replaces, not nests, policies
    """
    
    def __init__(self):
        self._threads: Dict[str, Dict[str, Any]] = {}
        self._loop_policies: Dict[str, "ExecutionLoop"] = {}
    
    async def advance_thread(
        self,
        thread_id: str,
        context: Optional[Dict[str, Any]] = None,
    ) -> ExecutionIterationResult:
        """
        Advance one Thread by at most one Cycle.
        
        This is the core advancement algorithm from the spec:
            1. Read immutable ThreadSnapshot
            2. Resolve active Loop
            3. Get LoopDecision
            4. If START_CYCLE: execute Cycle, get outcome, apply delta
            5. Apply continuation decision
            6. Return result
        """
        # Step 1: Get current Thread state (snapshot)
        thread = self._threads.get(thread_id)
        if not thread:
            return ExecutionIterationResult(
                thread_id=thread_id,
                loop_id=None,
                cycle_id=None,
                loop_decision=self._create_noop_decision(thread_id, 0),
                cycle_outcome=None,
                delta_commit_result=None,
                continuation_decision=None,
                thread_revision_before=0,
                thread_revision_after=0,
                cycle_executed=False,
            )
        
        revision_before = thread.get("revision", 0)
        loop_id = thread.get("active_loop_id")
        
        # Step 2: Get active Loop (if any)
        active_loop = self._loop_policies.get(loop_id) if loop_id else None
        
        # Step 3: Create snapshot and ask Loop for decision
        snapshot = ThreadSnapshot(
            thread_id=thread_id,
            thread_revision=revision_before,
            lifecycle_state=thread.get("lifecycle_state", "active"),
            active_loop_id=loop_id,
        )
        
        if not active_loop:
            # No active loop - yield to allow other Threads
            return ExecutionIterationResult(
                thread_id=thread_id,
                loop_id=None,
                cycle_id=None,
                loop_decision=LoopDecision.yield_execution(
                    thread_id=thread_id,
                    thread_revision=revision_before,
                    reason="No active Loop",
                ),
                cycle_outcome=None,
                delta_commit_result=None,
                continuation_decision=None,
                thread_revision_before=revision_before,
                thread_revision_after=revision_before,
                cycle_executed=False,
            )
        
        # Step 4: Get LoopDecision
        loop_decision = active_loop.decide(snapshot)
        
        # Step 5: Process the decision
        if not loop_decision.is_continuation:
            # Non-cycle decision (await, complete, fail, etc.)
            return self._apply_non_cycle_decision(
                thread_id=thread_id,
                thread=thread,
                loop_id=loop_id,
                active_loop=active_loop,
                decision=loop_decision,
                revision_before=revision_before,
            )
        
        # Step 6: Start Cycle execution
        if not loop_decision.cycle_definition:
            return ExecutionIterationResult(
                thread_id=thread_id,
                loop_id=LoopId(loop_id) if loop_id else None,
                cycle_id=None,
                loop_decision=loop_decision,
                cycle_outcome=None,
                delta_commit_result=None,
                continuation_decision=None,
                thread_revision_before=revision_before,
                thread_revision_after=revision_before,
                cycle_executed=False,
            )
        
        # Create Cycle
        cycle = self._create_cycle(
            definition=loop_decision.cycle_definition,
            thread_id=thread_id,
            loop_id=loop_id,
            source_revision=revision_before,
        )
        
        # Execute Cycle (one bounded semantic pass)
        cycle_outcome = await self._execute_cycle(cycle, context or {})
        
        # Step 7: Apply delta from outcome
        commit_result = None
        if cycle_outcome and cycle_outcome.semantic_delta:
            commit_result = self.commit_delta(
                thread_id=thread_id,
                delta=cycle_outcome.semantic_delta,
                current_revision=revision_before,
            )
        
        # Step 8: Get continuation decision from Loop
        continuation_decision = active_loop.interpret_outcome(
            snapshot=snapshot,
            cycle_outcome=cycle_outcome,
            commit_result=commit_result,
        )
        
        # Apply continuation decision to Thread state
        if continuation_decision:
            thread["active_loop_id"] = self._apply_continuation(
                thread=thread,
                loop_id=loop_id,
                decision=continuation_decision,
            )
        
        revision_after = revision_before + 1
        
        return ExecutionIterationResult(
            thread_id=thread_id,
            loop_id=LoopId(loop_id) if loop_id else None,
            cycle_id=CycleId(cycle.cycle_id),
            loop_decision=loop_decision,
            cycle_outcome=cycle_outcome,
            delta_commit_result=commit_result,
            continuation_decision=continuation_decision,
            thread_revision_before=revision_before,
            thread_revision_after=revision_after,
            cycle_executed=True,
            loop_switched=False,  # In this simple implementation
        )
    
    def _apply_non_cycle_decision(
        self,
        thread_id: str,
        thread: Dict[str, Any],
        loop_id: Optional[str],
        active_loop: "ExecutionLoop",
        decision: LoopDecision,
        revision_before: int,
    ) -> ExecutionIterationResult:
        """Apply a non-cycle decision (await, complete, fail, etc.)."""
        
        # Apply the decision to thread state
        if decision.decision_kind == LoopDecisionKind.AWAIT_INPUT:
            thread["lifecycle_state"] = "awaiting_input"
        
        elif decision.decision_kind == LoopDecisionKind.COMPLETE_THREAD:
            thread["lifecycle_state"] = "completed"
        
        elif decision.decision_kind in {
            LoopDecisionKind.FAIL_THREAD,
            LoopDecisionKind.TERMINATE_THREAD,
        }:
            thread["lifecycle_state"] = "failed"
        
        # Get continuation from loop
        snapshot = ThreadSnapshot(
            thread_id=thread_id,
            thread_revision=revision_before,
            lifecycle_state=thread.get("lifecycle_state", "active"),
            active_loop_id=loop_id,
        )
        continuation_decision = active_loop.interpret_outcome(
            snapshot=snapshot,
            cycle_outcome=None,
            commit_result=None,
        )
        
        return ExecutionIterationResult(
            thread_id=thread_id,
            loop_id=LoopId(loop_id) if loop_id else None,
            cycle_id=None,
            loop_decision=decision,
            cycle_outcome=None,
            delta_commit_result=None,
            continuation_decision=continuation_decision,
            thread_revision_before=revision_before,
            thread_revision_after=revision_before,
            cycle_executed=False,
            yielded=decision.decision_kind == LoopDecisionKind.YIELD,
            suspended=decision.decision_kind in {
                LoopDecisionKind.AWAIT_INPUT,
                LoopDecisionKind.AWAIT_CONDITION,
            },
            completed=decision.decision_kind == LoopDecisionKind.COMPLETE_THREAD,
            failed=decision.decision_kind in {
                LoopDecisionKind.FAIL_THREAD,
                LoopDecisionKind.TERMINATE_THREAD,
            },
        )
    
    def _apply_continuation(
        self,
        thread: Dict[str, Any],
        loop_id: Optional[str],
        decision: LoopDecision,
    ) -> Optional[str]:
        """Apply a continuation decision to Thread state. Returns new loop_id if any."""
        
        if decision.decision_kind == LoopDecisionKind.SWITCH_LOOP:
            # Switch to new Loop
            return decision.target_loop_definition.loop_id if decision.target_loop_definition else None
        
        elif decision.decision_kind == LoopDecisionKind.YIELD:
            # Yield - keep same loop, but may be rescheduled later
            return loop_id
        
        # For other decisions, keep current loop (or None for terminal)
        if decision.is_terminal:
            return None
        
        return loop_id
    
    def _create_cycle(
        self,
        definition: Any,
        thread_id: str,
        loop_id: str,
        source_revision: int,
    ) -> "SimpleCycle":
        """Create a simple Cycle instance."""
        return SimpleCycle(
            cycle_id=CycleId.generate(),
            definition=definition,
            thread_id=thread_id,
            loop_id=loop_id,
            source_revision=source_revision,
        )
    
    async def _execute_cycle(
        self,
        cycle: "SimpleCycle",
        context: Dict[str, Any],
    ) -> Optional[CycleOutcome]:
        """Execute a Cycle and return its outcome."""
        
        # Simulate stage execution
        stages_completed = 0
        
        # In a real implementation, this would:
        # - Execute each Stage in order
        # - Collect StageResults
        # - Produce semantic deltas
        
        for i in range(cycle.stages_count):
            stages_completed += 1
        
        return CycleOutcome(
            cycle_id=cycle.cycle_id,
            thread_id=cycle.thread_id,
            status="completed",
            source_thread_revision=cycle.source_revision,
            loop_decision_id=None,
            semantic_delta=ThreadSemanticDelta(
                source_cycle_id=cycle.cycle_id,
                expected_thread_revision=cycle.source_revision,
                proposed_new_revision=cycle.source_revision + 1,
                change_type="cycle_completed",
                provenance="cycle_execution",
            ),
            completion_reason=f"Completed {stages_completed} stages",
            stage_results=[],
            stages_completed=stages_completed,
        )
    
    async def select_next_thread(
        self,
        runnable_threads: List[str],
        context: Optional[Dict[str, Any]] = None,
    ) -> Optional[str]:
        """Select next Thread to advance (round-robin in this simple implementation)."""
        if not runnable_threads:
            return None
        # Simple round-robin selection
        return runnable_threads[0]
    
    async def create_thread(
        self,
        thread_id: Optional[str] = None,
        lifecycle_state: str = "created",
        purpose: Optional[str] = None,
        loop_id: Optional[str] = None,
    ) -> str:
        """Create a new Thread."""
        actual_id = thread_id or str(ThreadId.generate())
        
        self._threads[actual_id] = {
            "lifecycle_state": lifecycle_state,
            "purpose": purpose,
            "active_loop_id": loop_id,
            "revision": 0,
        }
        
        return actual_id
    
    async def get_thread_snapshot(
        self,
        thread_id: str,
    ) -> ThreadSnapshot:
        """Get a snapshot of Thread state."""
        thread = self._threads.get(thread_id)
        if not thread:
            raise ValueError(f"Thread {thread_id} not found")
        
        return ThreadSnapshot(
            thread_id=thread_id,
            thread_revision=thread.get("revision", 0),
            lifecycle_state=thread.get("lifecycle_state", "active"),
            active_loop_id=thread.get("active_loop_id"),
            purpose=thread.get("purpose"),
        )
    
    async def commit_delta(
        self,
        thread_id: str,
        delta: ThreadSemanticDelta,
        current_revision: int,
    ) -> CommitResult:
        """Attempt to apply a semantic delta."""
        
        # Check version
        if delta.expected_thread_revision != current_revision:
            return CommitResult(
                result=ThreadDeltaCommitResult.STALE_VERSION,
                rejection_reason=f"Expected revision {delta.expected_thread_revision}, got {current_revision}",
            )
        
        # In real implementation, would validate content too
        
        # Accept and advance revision
        if thread_id in self._threads:
            self._threads[thread_id]["revision"] = current_revision + 1
        
        return CommitResult(
            result=ThreadDeltaCommitResult.ACCEPTED,
            accepted_revision=current_revision + 1,
        )
    
    def _create_noop_decision(self, thread_id: str, revision: int) -> LoopDecision:
        """Create a default decision for when no loop is active."""
        return LoopDecision.yield_execution(
            thread_id=thread_id,
            thread_revision=revision,
            reason="No active Loop",
        )


# =============================================================================
# SimpleCycle (for examples)
# =============================================================================

class SimpleCycle:
    """A simple Cycle implementation for demonstration."""
    
    def __init__(
        self,
        cycle_id: str,
        definition: Any,
        thread_id: str,
        loop_id: str,
        source_revision: int,
    ):
        self.cycle_id = cycle_id
        self.definition = definition
        self.thread_id = thread_id
        self.loop_id = loop_id
        self.source_revision = source_revision
    
    @property
    def stages_count(self) -> int:
        """Number of Stages in this Cycle."""
        return 2  # Simplified - one bounded semantic pass


# =============================================================================
# SimpleLoop (for examples)
# =============================================================================

class ExecutionLoop:
    """
    A simple Loop implementation for demonstration.
    
    In production, use the canonical Loop from loops/__init__.py
    """
    
    def __init__(self, loop_id: str):
        self.loop_id = loop_id
    
    def decide(self, snapshot: ThreadSnapshot) -> LoopDecision:
        """Decide what should happen next."""
        
        # Simple policy: always continue with a default cycle definition
        
        return LoopDecision.start_cycle(
            thread_id=snapshot.thread_id,
            thread_revision=snapshot.thread_revision,
            cycle_definition={"definition_id": "default", "name": "DefaultCycle"},
            rationale="Continuing execution",
        )
    
    def interpret_outcome(
        self,
        snapshot: ThreadSnapshot,
        cycle_outcome: Optional[CycleOutcome],
        commit_result: Optional[CommitResult],
    ) -> LoopDecision:
        """Interpret a Cycle outcome and decide continuation."""
        
        if cycle_outcome and cycle_outcome.status == "failed":
            return LoopDecision.fail_thread(
                thread_id=snapshot.thread_id,
                thread_revision=snapshot.thread_revision,
                reason="Cycle failed",
                failure_reason=cycle_outcome.completion_reason,
            )
        
        # Default: yield to allow other Threads to run
        return LoopDecision.yield_execution(
            thread_id=snapshot.thread_id,
            thread_revision=snapshot.thread_revision,
            reason="Yielding after cycle completion",
        )


# =============================================================================
# Export public API
# =============================================================================

__all__ = [
    # Identifiers (semantic)
    "ThreadId",
    "LoopId",
    "CycleId",
    
    # Loop decisions (Thread-local continuation)
    "LoopDecisionKind",
    "LoopDecision",
    "AwaitCondition",
    
    # Thread state management
    "ThreadSnapshot",
    "ThreadSemanticDelta",
    "CommitResult",
    "ThreadDeltaCommitResult",
    
    # Cycle execution
    "CycleOutcome",
    "StageResult",
    
    # Coordinator protocol and implementation
    "ExecutionCoordinator",
    "SimpleExecutionCoordinator",
]