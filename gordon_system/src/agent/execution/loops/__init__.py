# Execution Loops Package
# ======================

"""
Canonical Loop Architecture for Gordon's semantic execution layer.

A Loop is not a while loop, event loop, scheduler loop, or runtime dispatcher.
A Loop IS the behavioral policy controller of a Thread.

Loop Responsibilities:
- Behavioral policy: decide what to do next based on thread state + cycle outcome
- Cycle selection policy: choose which cycle to execute
- Continuation policy: decide whether to continue, suspend, complete, etc.
- Interpretation of Cycle outcomes
- Policy-local adaptation state

Loop Must NOT Own:
- Execute reasoning or planning algorithms (Capabilities do this)
- Invoke model runtimes directly (Core does this through Cycles)
- Own Thread continuity (Thread owns this)
- Mutate Thread state arbitrarily (Thread accepts deltas)
- Execute Stage logic (Cycles execute stages)
- Allocate runtime resources (Core does this)

Canonical Flow:
    Thread snapshot + previous Cycle outcome + external signals
        ↓
    Loop evaluates policy
        ↓
    Loop produces LoopDecision
        ↓
    Execution layer validates decision
        ↓
    Core is requested to support runtime execution
        ↓
    Selected Cycle executes
        ↓
    Cycle outcome returns
        ↓
    Loop interprets outcome
        ↓
    Thread accepts validated semantic delta

Package Structure:
    loops/
        ├── __init__.py           # Package exports
        ├── context.py            # Loop evaluation input (context)
        ├── decision.py           # Loop decision output hierarchy
        ├── policy.py             # Policy protocol and implementations
        ├── state.py              # Policy-local state only
        ├── modes.py              # Behavioral modes and transitions
        └── loop.py               # Canonical Loop coordinator
"""

from dataclasses import dataclass, field
from typing import Protocol, Optional, List, Dict, Any, Union
from enum import Enum, auto

# Import base types from threads for use in loops
from ..threads.identity import ThreadId


# =============================================================================
# Behavioral Modes (Policy State)
# =============================================================================


class LoopMode(Enum):
    """
    Behavioral modes that determine how a Loop makes decisions.
    
    These are policy states, NOT runtime scheduling states:
        - ACTIVE: Normal operation, responding to semantic inputs
        - EXPLORATORY: Experimenting with different approaches
        - DELIBERATIVE: Careful reasoning, weighing options
        - REACTIVE: Responding quickly to external events
        - MONITORING: Watching for conditions without acting
        - REFLECTIVE: Reviewing past performance
        - IDLE: Waiting for input or triggers
        - AWAITING_INPUT: Blocked on external input
        - RECOVERY: Attempting to recover from failure
        - DELEGATED: Delegating work to child threads
    """
    
    ACTIVE = "active"
    EXPLORATORY = "exploratory"
    DELIBERATIVE = "deliberative"
    REACTIVE = "reactive"
    MONITORING = "monitoring"
    REFLECTIVE = "reflective"
    IDLE = "idle"
    AWAITING_INPUT = "awaiting_input"
    RECOVERY = "recovery"
    DELEGATED = "delegated"


# =============================================================================
# Loop Decision Types
# =============================================================================


class DecisionType(Enum):
    """
    Types of decisions a Loop can make.
    
    Every decision must include:
        - Decision type (which kind of decision)
        - Rationale (why this decision was made)
        - Source thread revision (for validation)
        - Optional cycle definition (when applicable)
        - Expected preconditions
        - Policy metadata
    """
    
    CONTINUE = "continue"          # Continue with selected Cycle
    SUSPEND = "suspend"            # Suspend Thread temporarily
    AWAIT_INPUT = "await_input"    # Wait for external input
    COMPLETE = "complete"          # Complete Thread successfully
    TERMINATE = "terminate"        # Terminate Thread abruptly
    REJECT_OUTCOME = "reject_outcome"  # Reject current outcome, try again
    REQUEST_RECOVERY = "request_recovery"  # Request semantic recovery Cycle
    DELEGATE = "delegate"          # Defer to child thread
    SWITCH_MODE = "switch_mode"    # Switch behavioral mode
    REPLACE_POLICY = "replace_policy"  # Replace Loop policy


@dataclass(frozen=True)
class LoopDecision:
    """
    A decision produced by a Loop evaluation.
    
    This is the canonical output of Loop policy evaluation. It expresses
    what should happen next, without executing it directly.
    
    Invariants:
        D-001: Every decision must reference the thread revision it evaluated
        D-002: A terminal decision cannot select a Cycle
        D-003: Continuation decisions must include valid Cycle definition
        D-004: Decisions are validated before application
    """
    
    # Core fields (required)
    decision_type: DecisionType
    thread_revision: int  # Which Thread revision was this evaluated against?
    
    # Rationale and metadata
    rationale: str = ""  # Reason for decision (empty string if not specified)
    source_decision_id: Optional[str] = None
    
    # Cycle selection (only for CONTINUE decisions)
    cycle_definition: Optional[Any] = None  # Cycle type/class or factory
    
    # Expected preconditions (for validation before execution)
    expected_preconditions: List[str] = field(default_factory=list)
    
    # Policy metadata
    policy_id: Optional[str] = None
    mode: Optional[LoopMode] = None
    iteration_count: int = 0
    
    # Validation status
    is_valid: bool = True
    
    @property
    def is_terminal(self) -> bool:
        """Check if this decision terminates the Thread."""
        return self.decision_type in {
            DecisionType.COMPLETE,
            DecisionType.TERMINATE,
        }
    
    @property
    def is_continuation(self) -> bool:
        """Check if this decision continues with a Cycle."""
        return self.decision_type == DecisionType.CONTINUE


@dataclass(frozen=True)
class ContinueDecision(LoopDecision):
    """
    Decision to continue with a Cycle.
    
    This is the most common decision type when Thread has more work to do.
    """
    
    cycle_definition: Any  # Must be provided for CONTINUE decisions
    expected_outcome: Optional[str] = None  # What outcome is expected


@dataclass(frozen=True)
class SuspendDecision(LoopDecision):
    """
    Decision to suspend the Thread temporarily.
    
    The Thread identity and state are preserved. It may resume later.
    """
    
    reason: str = "Suspension requested by policy"
    resumption_trigger: Optional[str] = None


@dataclass(frozen=True)
class AwaitInputDecision(LoopDecision):
    """
    Decision to await external input before continuing.
    """
    
    waiting_for: str = ""  # What input is being waited for? (empty string means unknown)
    timeout_seconds: Optional[float] = None


@dataclass(frozen=True)
class CompleteDecision(LoopDecision):
    """
    Decision that the Thread has completed successfully.
    """
    
    completion_reason: str = ""  # Reason for completion (empty means not specified)
    semantic_summary: Optional[str] = None


@dataclass(frozen=True)
class TerminateDecision(LoopDecision):
    """
    Decision to terminate the Thread abruptly.
    """
    
    termination_reason: str = ""  # Reason for termination (empty means not specified)
    error_code: Optional[str] = None


@dataclass(frozen=True)
class RejectOutcomeDecision(LoopDecision):
    """
    Decision to reject current Cycle outcome and request another attempt.
    """
    
    rejection_reason: str = ""  # Reason for rejection (empty means not specified)
    suggested_remediation: Optional[str] = None


@dataclass(frozen=True)
class RequestRecoveryDecision(LoopDecision):
    """
    Decision that semantic recovery is needed.
    """
    
    recovery_type: str = ""  # Type of recovery (empty means not specified)
    context_hint: Optional[str] = None


@dataclass(frozen=True)
class DelegateDecision(LoopDecision):
    """
    Decision to delegate work to a child Thread.
    """
    
    delegation_target: Optional[Any] = None  # Child thread or factory (None means unknown)
    transfer_context: bool = True


@dataclass(frozen=True)
class SwitchModeDecision(LoopDecision):
    """
    Decision to switch behavioral mode.
    """
    
    target_mode: Optional[LoopMode] = None  # Target mode (None means unknown)
    transition_reason: str = ""  # Reason for transition (empty means not specified)


@dataclass(frozen=True)
class ReplacePolicyDecision(LoopDecision):
    """
    Decision to replace the current policy with a different one.
    """
    
    new_policy_id: str = ""  # New policy ID (empty means unknown)
    new_policy_type: str = ""  # Fully qualified class name (empty means unknown)


# =============================================================================
# Policy Protocol
# =============================================================================


class LoopPolicy(Protocol):
    """
    Protocol for Loop behavioral policies.
    
    A policy accepts semantic inputs and returns a Loop decision.
    Policies are replaceable - a Thread may switch policies according to
    explicit rules defined in its current policy.
    
    Invariants:
        P-001: Policy evaluation must be bounded (not infinite loops)
        P-002: Policies must return exactly one decision per evaluation
        P-003: Policies do not execute Cycles directly
        P-004: Policies do not mutate Thread state directly
    """
    
    @property
    def policy_id(self) -> str:
        """Unique identifier for this policy."""
        ...
    
    @property
    def current_mode(self) -> LoopMode:
        """Current behavioral mode of this policy."""
        ...
    
    def decide(self, context: "LoopContext") -> LoopDecision:
        """
        Evaluate the current state and produce a decision.
        
        Args:
            context: Input containing Thread snapshot + cycle outcome
            
        Returns:
            A single LoopDecision expressing what should happen next
            
        Raises:
            PolicyError: If evaluation fails (not a runtime error)
        """
        ...
    
    def transition_mode(self, target_mode: LoopMode) -> "LoopPolicy":
        """
        Return a new policy with the specified mode.
        
        This is for when mode transitions require policy changes.
        Some policies may support multiple modes; others create new instances.
        
        Args:
            target_mode: The desired behavioral mode
            
        Returns:
            A (possibly new) policy instance in the target mode
        """
        ...
    
    def get_state(self) -> "LoopState":
        """Get current policy-local state."""
        ...
    
    def update_state(self, state: "LoopState") -> None:
        """Update policy-local state from external source."""
        ...


# =============================================================================
# Loop Context (Evaluation Input)
# =============================================================================


@dataclass(frozen=True)
class LoopContext:
    """
    Input context for Loop evaluation.
    
    Contains only semantic information required for behavioral decisions.
    Does NOT contain runtime scheduling details, resource availability,
    or Core implementation objects.
    
    Invariants:
        CXT-001: Context contains only semantic information
        CXT-002: Thread snapshot is read-only (immutable view)
        CXT-003: Cycle outcome is typed and semantically meaningful
        CXT-004: Policy state is included for continuity across evaluations
    """
    
    # Thread snapshot (read-only view of current state)
    thread_id: str
    thread_revision: int  # Semantic version
    thread_purpose: Optional[str] = None
    thread_name: Optional[str] = None
    
    # Behavioral context
    current_mode: LoopMode = LoopMode.ACTIVE
    active_objectives: List[str] = field(default_factory=list)
    
    # Previous cycle outcome (what just happened?)
    previous_cycle_outcome: Optional["CycleOutcome"] = None
    previous_cycle_id: Optional[str] = None
    
    # Pending work
    pending_interruptions: List[str] = field(default_factory=list)
    pending_suspensions: List[str] = field(default_factory=list)
    
    # Policy state (for continuity across evaluations)
    policy_state: Dict[str, Any] = field(default_factory=dict)
    
    # Available Cycle definitions (what can be selected?)
    available_cycle_types: List[str] = field(default_factory=list)


@dataclass(frozen=True)
class CycleOutcome:
    """
    Result of a completed Cycle execution.
    
    Contains semantic interpretation of the Cycle result, not raw runtime
    outputs like tensors or token logits. Capabilities convert computational
    outputs into semantic outcomes before the Loop receives them.
    
    Invariants:
        OUT-001: Outcome is semantically meaningful (not raw data)
        OUT-002: Outcome indicates whether Thread should continue
        OUT-003: Outcome includes interpretation hints for next steps
    """
    
    cycle_id: str
    status: str  # e.g., "completed", "continued", "wait", "delegated", "failed"
    
    # Semantic result
    semantic_delta: Optional[Any] = None  # What changed semantically?
    new_facts: List[str] = field(default_factory=list)
    updated_objectives: List[str] = field(default_factory=list)
    
    # Continuation hints
    should_continue: bool = True
    continuation_hint: Optional[str] = None
    
    # Failure information (semantic, not runtime)
    failure_reason: Optional[str] = None
    recovery_suggestion: Optional[str] = None


# =============================================================================
# Loop State (Policy-Local State Only)
# =============================================================================


@dataclass(frozen=True)
class LoopState:
    """
    Policy-local state owned by the Loop.
    
    This is narrow state used for behavioral policy decisions only.
    It does NOT duplicate Thread continuity, memory, or persistent semantic state.
    
    Invariants:
        ST-001: State contains only policy-local data
        ST-002: No thread identity, memory, or objectives
        ST-003: State is immutable (use builder for changes)
    """
    
    current_mode: LoopMode = LoopMode.ACTIVE
    
    # Iteration tracking
    iteration_count: int = 0
    consecutive_same_outcome: int = 0  # Detection of repeated outcomes
    
    # Backoff state
    backoff_level: int = 0
    last_backoff_seconds: float = 0.0
    
    # Strategy tracking
    current_strategy_id: Optional[str] = None
    strategy_successes: int = 0
    strategy_failures: int = 0
    
    # Completion confidence
    completion_confidence: float = 0.0  # 0.0 to 1.0
    
    # Delegation state
    has_pending_delegation: bool = False
    
    def with_iteration(self, count: int) -> "LoopState":
        """Create new state with updated iteration count."""
        return dataclass_replace(self, iteration_count=count)
    
    def with_backoff(self, level: int, seconds: float = 0.0) -> "LoopState":
        """Create new state with backoff information."""
        return dataclass_replace(
            self,
            backoff_level=level,
            last_backoff_seconds=seconds
        )
    
    def with_strategy(self, strategy_id: Optional[str]) -> "LoopState":
        """Create new state with strategy tracking."""
        return dataclass_replace(
            self,
            current_strategy_id=strategy_id
        )


def dataclass_replace(obj: Any, **kwargs) -> Any:
    """Replace fields in a frozen dataclass."""
    import dataclasses
    if hasattr(obj, '__dataclass_fields__'):
        return dataclasses.replace(obj, **kwargs)
    raise TypeError(f"Cannot replace fields in {type(obj)}")


# =============================================================================
# Loop Coordinator (The "Loop" Entity)
# =============================================================================


class ExecutionLoop:
    """
    Canonical Loop coordinator that owns behavioral policy.
    
    This is the concrete implementation that Threads use. It:
        - Maintains association with one Thread
        - Owns a LoopPolicy for decision-making
        - Produces LoopDecisions based on evaluation
        - Manages policy-local state
    
    Invariants:
        L-001: Every active Loop belongs to exactly one Thread
        L-002: A Thread has at most one authoritative active Loop
        L-003: Loop evaluation is bounded (not infinite)
        L-004: One evaluation produces exactly one decision
        L-005: Loop does not mutate Thread state directly
        L-006: Loop does not execute Cycle stages
    """
    
    def __init__(self, thread_id: str, policy: Optional[LoopPolicy] = None):
        """
        Initialize a Loop for the given Thread.
        
        Args:
            thread_id: The Thread this Loop serves
            policy: Policy for decision-making (defaults to standard policy)
        """
        self._thread_id = thread_id
        self._policy = policy or StandardPolicy()
        self._state = LoopState(current_mode=self._policy.current_mode)
    
    @property
    def thread_id(self) -> str:
        """Get the Thread this Loop serves."""
        return self._thread_id
    
    @property
    def current_policy(self) -> LoopPolicy:
        """Get the current policy."""
        return self._policy
    
    @property
    def current_mode(self) -> LoopMode:
        """Get current behavioral mode."""
        return self._state.current_mode
    
    def evaluate(self, context: LoopContext) -> LoopDecision:
        """
        Evaluate current state and produce a decision.
        
        Args:
            context: Thread snapshot + cycle outcome
            
        Returns:
            A single LoopDecision
        """
        # Validate context
        if context.thread_id != self._thread_id:
            raise ValueError(
                f"Context thread_id ({context.thread_id}) does not match "
                f"Loop's thread_id ({self._thread_id})"
            )
        
        # Policy evaluation (bounded, deterministic)
        decision = self._policy.decide(context)
        
        # Update state from decision
        if decision.mode:
            self._state = dataclass_replace(self._state, current_mode=decision.mode)
        self._state = dataclass_replace(
            self._state,
            iteration_count=self._state.iteration_count + 1
        )
        
        return decision
    
    def switch_policy(self, new_policy: LoopPolicy) -> None:
        """
        Replace the current policy with a new one.
        
        Args:
            new_policy: The new policy to adopt
        """
        # Validate mode compatibility (optional)
        if new_policy.current_mode != self._state.current_mode:
            # Mode change may require additional validation
            pass
        
        self._policy = new_policy
        self._state = dataclass_replace(
            self._state,
            current_mode=new_policy.current_mode
        )
    
    def get_state(self) -> LoopState:
        """Get current policy-local state."""
        return self._state
    
    # Convenience methods for common decision types
    @staticmethod
    def continue_decision(
        thread_revision: int,
        cycle_definition: Any,
        rationale: str = "Continuing with next Cycle"
    ) -> ContinueDecision:
        """
        Create a CONTINUE decision.
        
        Args:
            thread_revision: Current Thread semantic version
            cycle_definition: The Cycle to execute next
            rationale: Why this decision was made
            
        Returns:
            A ContinueDecision
        """
        return ContinueDecision(
            decision_type=DecisionType.CONTINUE,
            thread_revision=thread_revision,
            cycle_definition=cycle_definition,
            rationale=rationale,
            is_valid=True
        )
    
    @staticmethod
    def complete_decision(
        thread_revision: int,
        reason: str = "Thread completed its purpose"
    ) -> CompleteDecision:
        """
        Create a COMPLETE decision.
        
        Args:
            thread_revision: Current Thread semantic version
            reason: Why the Thread should complete
            
        Returns:
            A CompleteDecision
        """
        return CompleteDecision(
            decision_type=DecisionType.COMPLETE,
            thread_revision=thread_revision,
            completion_reason=reason,
            is_valid=True
        )
    
    @staticmethod
    def suspend_decision(
        thread_revision: int,
        reason: str = "Suspended by policy"
    ) -> SuspendDecision:
        """
        Create a SUSPEND decision.
        
        Args:
            thread_revision: Current Thread semantic version
            reason: Why the Thread should be suspended
            
        Returns:
            A SuspendDecision
        """
        return SuspendDecision(
            decision_type=DecisionType.SUSPEND,
            thread_revision=thread_revision,
            rationale=reason,
            is_valid=True
        )
    
    @staticmethod
    def terminate_decision(
        thread_revision: int,
        reason: str = "Thread terminated by policy"
    ) -> TerminateDecision:
        """
        Create a TERMINATE decision.
        
        Args:
            thread_revision: Current Thread semantic version
            reason: Why the Thread should be terminated
            
        Returns:
            A TerminateDecision
        """
        return TerminateDecision(
            decision_type=DecisionType.TERMINATE,
            thread_revision=thread_revision,
            termination_reason=reason,
            is_valid=True
        )


# =============================================================================
# Standard Policy Implementation
# =============================================================================


class StandardPolicy(LoopPolicy):
    """
    Standard Loop policy with basic behavioral logic.
    
    This policy implements straightforward decision-making:
        - Continue if Thread has active objectives and cycle succeeded
        - Complete if no active objectives remain
        - Suspend or wait for input on specific signals
        - Terminate on clear failure conditions
    
    For more sophisticated behavior, custom policies can be implemented.
    """
    
    def __init__(self):
        self._policy_id = "standard-1.0"
        self._current_mode = LoopMode.ACTIVE
    
    @property
    def policy_id(self) -> str:
        return self._policy_id
    
    @property
    def current_mode(self) -> LoopMode:
        return self._current_mode
    
    def decide(self, context: LoopContext) -> LoopDecision:
        """
        Evaluate context and produce a decision.
        
        Basic logic:
            1. Check for interruptions/suspensions → suspend/await
            2. Check previous cycle outcome → continue/complete/terminate
            3. If no cycle outcome (first iteration), select initial Cycle
            4. Default: continue with available Cycle
        """
        # Check for pending interruptions
        if context.pending_interruptions:
            return SuspendDecision(
                decision_type=DecisionType.SUSPEND,
                thread_revision=context.thread_revision,
                rationale=f"Pending interruptions: {', '.join(context.pending_interruptions)}",
                is_valid=True
            )
        
        # Check previous cycle outcome
        if context.previous_cycle_outcome:
            return self._decide_from_outcome(
                context.previous_cycle_outcome,
                context.thread_revision
            )
        
        # No previous outcome - select initial Cycle
        if context.available_cycle_types:
            # Use first available type as default
            return ContinueDecision(
                decision_type=DecisionType.CONTINUE,
                thread_revision=context.thread_revision,
                cycle_definition=context.available_cycle_types[0],
                rationale="Starting Thread execution with initial Cycle",
                is_valid=True
            )
        
        # No Cycles available - can't continue
        if context.active_objectives:
            return RequestRecoveryDecision(
                decision_type=DecisionType.REQUEST_RECOVERY,
                thread_revision=context.thread_revision,
                recovery_type="cycle_selection",
                rationale="No available Cycle types but Thread has active objectives",
                is_valid=True
            )
        
        # No objectives and no cycles - complete
        return CompleteDecision(
            decision_type=DecisionType.COMPLETE,
            thread_revision=context.thread_revision,
            completion_reason="No active objectives and no Cycles available",
            is_valid=True
        )
    
    def _decide_from_outcome(self, outcome: CycleOutcome, thread_revision: int) -> LoopDecision:
        """Make a decision based on a Cycle outcome."""
        
        # Failed outcome
        if outcome.status == "failed":
            return TerminateDecision(
                decision_type=DecisionType.TERMINATE,
                thread_revision=thread_revision,
                termination_reason=f"Cycle failed: {outcome.failure_reason or 'unknown'}",
                is_valid=True
            )
        
        # Completed with no continuation needed
        if not outcome.should_continue:
            if self._should_complete(thread_revision):
                return CompleteDecision(
                    decision_type=DecisionType.COMPLETE,
                    thread_revision=thread_revision,
                    completion_reason="Cycle completed and Thread purpose fulfilled",
                    is_valid=True
                )
            else:
                return SuspendDecision(
                    decision_type=DecisionType.SUSPEND,
                    thread_revision=thread_revision,
                    rationale="Cycle completed but Thread awaiting resumption trigger",
                    is_valid=True
                )
        
        # Cycle succeeded, should continue
        if outcome.semantic_delta or outcome.new_facts:
            return ContinueDecision(
                decision_type=DecisionType.CONTINUE,
                thread_revision=thread_revision,
                cycle_definition=outcome.continuation_hint or "next_cycle",
                rationale="Cycle succeeded and Thread has more work to do",
                is_valid=True
            )
        
        # Unknown outcome - continue with hint
        if outcome.continuation_hint:
            return ContinueDecision(
                decision_type=DecisionType.CONTINUE,
                thread_revision=thread_revision,
                cycle_definition=outcome.continuation_hint,
                rationale="Continuing based on continuation hint",
                is_valid=True
            )
        
        # Default: continue with same or different Cycle
        return ContinueDecision(
            decision_type=DecisionType.CONTINUE,
            thread_revision=thread_revision,
            cycle_definition="default_cycle",
            rationale="Default continuation behavior",
            is_valid=True
        )
    
    def _should_complete(self, thread_revision: int) -> bool:
        """Heuristic for determining if Thread should complete."""
        # For now, simple heuristic based on completion confidence
        return True  # Simplified - could use more sophisticated logic
    
    def transition_mode(self, target_mode: LoopMode) -> "StandardPolicy":
        """Return new policy with specified mode."""
        new_policy = StandardPolicy()
        new_policy._current_mode = target_mode
        return new_policy
    
    def get_state(self) -> LoopState:
        return LoopState(current_mode=self._current_mode)
    
    def update_state(self, state: LoopState) -> None:
        self._current_mode = state.current_mode


# =============================================================================
# Policy Errors
# =============================================================================


class PolicyError(Exception):
    """Error during policy evaluation."""
    pass


class InvalidModeTransitionError(PolicyError):
    """Mode transition is not allowed."""
    pass


# =============================================================================
# Export all public symbols
# =============================================================================

__all__ = [
    # Modes
    "LoopMode",
    
    # Decisions
    "DecisionType",
    "LoopDecision",
    "ContinueDecision",
    "SuspendDecision",
    "AwaitInputDecision",
    "CompleteDecision",
    "TerminateDecision",
    "RejectOutcomeDecision",
    "RequestRecoveryDecision",
    "DelegateDecision",
    "SwitchModeDecision",
    "ReplacePolicyDecision",
    
    # Protocol
    "LoopPolicy",
    
    # Context and state
    "LoopContext",
    "CycleOutcome",
    "LoopState",
    
    # Coordinator
    "ExecutionLoop",
    
    # Policy implementations
    "StandardPolicy",
    
    # Errors
    "PolicyError",
    "InvalidModeTransitionError",
]