# Canonical Cycle Architecture Package
# ====================================
#
# PHASE 3.10.6 - Cycle catalog for resolving cycle kinds to definitions.
# PHASE 3.10.9 - Concrete execution taxonomy implementation

"""
Canonical Cycle architecture for finite semantic execution units.

A Cycle is NOT:
    - An operating-system thread, coroutine, task, worker, process, or scheduler entry
    - A runtime execution unit (that belongs to Core)
    - An event loop, retry loop, or long-lived behavioral controller

A Cycle IS:
    - The smallest finite semantic execution unit belonging to a Thread
    - Selected by exactly one Loop decision
    - One complete bounded semantic pass with terminal outcome
    - Owner of Stage progression within its execution scope

Architecture:

    src/agent/execution/cycles/
        ├── __init__.py           # Package exports (this file)
        ├── base.py               # Abstract Cycle definition contracts
        ├── definition.py         # Reusable Cycle definitions
        ├── instance.py           # Concrete Cycle executions (instances)
        ├── context.py            # Ephemeral execution context
        ├── progression.py        # Progression state machine
        ├── outcome.py            # Terminal result types
        ├── stages.py             # Stage coordination model
        └── validation.py         # Invariant validators

Ownership Model:

    Thread: semantic continuity, identity, objectives, completion intent
    Loop: repetition policy, Cycle selection decision, continuation policy
    Cycle: finite semantic pass, Stage progression, outcome production
    Core: runtime scheduling, lifecycle state transitions, resource allocation

Architecture Invariants:
    C-001: Every Cycle belongs to exactly one Thread
    C-002: Every Cycle is selected by exactly one Loop decision
    C-003: Every Cycle operates against exactly one source Thread revision
    C-004: Every Cycle has a stable identity distinct from runtime handles
    C-005: Every Cycle is finite (must terminate with terminal outcome)
    C-006: Every Cycle produces exactly one terminal outcome
    C-007: A Cycle cannot mutate Thread state directly (Thread accepts deltas)
    C-008: A Cycle cannot select itself for another iteration (Loop owns policy)
    C-009: Runtime mechanics belong to Core, not Cycle logic
    C-010: Stage progression follows the Cycle definition explicitly
"""

from dataclasses import dataclass, field
from typing import Protocol, Optional, List, Dict, Any, Union, TypeVar, Generic
from enum import Enum, auto
import uuid

# Import base types from threads for use in cycles
# Note: types in cycles don't have direct access to Execution* prefixed types
# We need to import from threads.identity for ThreadId and use aliases
from ..threads.identity import ThreadId

# Use type aliases - these are the canonical execution ID types
ExecutionId = None  # Placeholder - not used in cycles
LoopId = None  # Placeholder
CycleId = None  # Placeholder  
StageId = None  # Placeholder
Timestamp = None  # Placeholder


# =============================================================================
# Progression States (Semantic - not runtime)
# =============================================================================


class CycleProgressionState(Enum):
    """
    Semantic progression states of a Cycle.
    
    These describe the logical state of cycle execution:
        - CREATED: Cycle artifact exists, not yet validated
        - VALIDATED: Preconditions satisfied, ready to execute
        - READY: Scheduled for execution (runtime may queue)
        - ACTIVE: Currently executing Stages
        - AWAITING_STAGE: Waiting for Stage result
        - EVALUATING_STAGE_RESULT: Interpreting Stage result
        - COMPLETING: Finalizing terminal outcome
        - TERMINAL STATES: completed, interrupted, failed, cancelled, etc.
    """
    
    # Initial states
    CREATED = "created"           # Cycle artifact exists, not yet validated
    VALIDATED = "validated"       # Preconditions satisfied, ready to execute
    
    # Scheduled states
    READY = "ready"               # Scheduled for execution (runtime may queue)
    
    # Active states
    ACTIVE = "active"             # Currently executing Stages
    AWAITING_STAGE = "awaiting_stage"      # Waiting for Stage result
    EVALUATING_STAGE_RESULT = "evaluating_stage_result"  # Interpreting Stage result
    
    # Finalizing state
    COMPLETING = "completing"     # Finalizing terminal outcome
    
    # Terminal states (success/failure/interruption)
    COMPLETED = "completed"       # Cycle finished successfully
    PARTIALLY_COMPLETED = "partially_completed"  # Partial progress recorded
    INTERRUPTED = "interrupted"   # Semantic interruption occurred
    FAILED = "failed"             # Semantic failure (not runtime error)
    CANCELLED = "cancelled"       # Runtime cancellation completed
    REJECTED = "rejected"         # Cycle rejected before execution
    SUPERSEDED = "superseded"     # Superseded by another cycle
    INVALIDATED = "invalidated"   # Source revision changed, invalid


# =============================================================================
# Outcome Status (Terminal)
# =============================================================================


class CycleOutcomeStatus(Enum):
    """
    Terminal status of a Cycle outcome.
    
    Every Cycle must produce exactly one terminal outcome with one of these
    statuses. These are semantic, not runtime states.
    """
    
    COMPLETED = "completed"           # All Stages completed successfully
    PARTIALLY_COMPLETED = "partially_completed"  # Some progress made
    INTERRUPTED = "interrupted"       # Semantic interruption occurred
    FAILED = "failed"                 # Semantic failure (preconditions, etc.)
    CANCELLED = "cancelled"           # Runtime cancellation
    REJECTED = "rejected"             # Rejected before execution
    SUPERSEDED = "superseded"         # Superseded by another cycle
    INVALIDATED = "invalidated"       # Source revision changed


# =============================================================================
# Stage Progression States
# =============================================================================


class StageProgressionState(Enum):
    """
    Progression state of a single Stage within a Cycle.
    
    Each Stage transitions through these states during execution:
        - CREATED: Stage defined
        - READY: Preconditions checked, ready to execute
        - ACTIVE: Currently executing
        - COMPLETED: Successfully finished
        - FAILED: Failed during execution
        - SKIPPED: Skipped due to prior failure or condition
    """
    
    CREATED = "created"      # Stage is defined but not yet evaluated
    READY = "ready"          # Preconditions satisfied, ready to execute
    ACTIVE = "active"        # Currently executing
    COMPLETED = "completed"  # Successfully finished
    FAILED = "failed"        # Failed during execution
    SKIPPED = "skipped"      # Skipped (no longer needed)


# =============================================================================
# Cycle Identity
# =============================================================================


@dataclass(frozen=True)
class CycleIdentity:
    """
    Immutable semantic identity of a Cycle.
    
    This is distinct from:
        - Thread identity (the thread this cycle belongs to)
        - Loop decision identity (which decision selected this cycle)
        - Runtime task ID (Core's execution handle)
        - Scheduler queue entry ID
    
    Invariants:
        CID-001: Identity is immutable once created
        CID-002: Identity is stable across suspension/resumption
        CID-003: Identity is unique within its Thread scope
    """
    
    value: str  # UUID string
    
    @classmethod
    def generate(cls) -> "CycleIdentity":
        """Generate a new unique Cycle identity."""
        return cls(value=str(uuid.uuid4()))
    
    def __str__(self) -> str:
        return self.value


# =============================================================================
# Thread Reference (for ownership verification)
# =============================================================================


@dataclass(frozen=True)
class ThreadReference:
    """
    Reference to the owning Thread for cycle ownership verification.
    
    Invariants:
        TR-001: Reference contains immutable Thread identity
        TR-002: Reference includes expected Thread revision for validation
        TR-003: Reference prevents stale cycle attachment to changed Threads
    """
    
    thread_id: str  # ThreadId.value
    expected_revision: int  # Thread semantic version when cycle was selected
    
    def is_valid(self, actual_revision: int) -> bool:
        """Check if the Thread revision matches the expected revision."""
        return actual_revision == self.expected_revision


# =============================================================================
# Loop Decision Reference (for ownership verification)
# =============================================================================


@dataclass(frozen=True)
class LoopDecisionReference:
    """
    Reference to the Loop decision that selected this Cycle.
    
    Invariants:
        LDR-001: Reference contains immutable decision identity
        LDR-002: Reference includes the selecting Thread revision
        LDR-003: Reference enables traceability of cycle selection
    """
    
    decision_id: str  # Unique identifier for the Loop decision
    thread_revision: int  # Thread version when decision was made
    
    @classmethod
    def from_decision(cls, decision_id: str, thread_revision: int) -> "LoopDecisionReference":
        """Create a reference from a decision."""
        return cls(decision_id=decision_id, thread_revision=thread_revision)


# =============================================================================
# Stage Definition (reusable stage template)
# =============================================================================


@dataclass(frozen=True)
class StageDefinition:
    """
    Reusable definition of a semantic Stage within a Cycle.
    
    A StageDefinition describes what work should be done but is not executed
    directly. Concrete Stage instances are created during cycle execution.
    
    Invariants:
        SD-001: Definition contains immutable semantic description
        SD-002: Pre/postconditions are declarative, not executable logic
        SD-003: Required capabilities are contract references, not implementations
    """
    
    stage_id: str  # Unique within cycle
    name: str  # Human-readable name (e.g., "observe", "reason", "decide")
    description: str = ""  # Detailed explanation
    
    # Semantic requirements
    precondition: Optional[str] = None  # What must be true before execution
    postcondition: Optional[str] = None  # What will be true after execution
    
    # Capability requirements (contract references, not implementations)
    required_capabilities: List[str] = field(default_factory=list)
    
    # Progression constraints
    interruptible: bool = True  # Can this stage be interrupted?
    idempotent: bool = False  # Can this stage be safely repeated?
    
    def validate(self) -> "StageDefinitionValidation":
        """Validate the Stage definition."""
        errors = []
        
        if not self.stage_id:
            errors.append("stage_id is required")
        if not self.name:
            errors.append("name is required")
        
        return StageDefinitionValidation(is_valid=len(errors) == 0, errors=errors)


@dataclass(frozen=True)
class StageDefinitionValidation:
    """Result of validating a Stage definition."""
    
    is_valid: bool
    errors: List[str] = field(default_factory=list)


# =============================================================================
# Cycle Definition (reusable template)
# =============================================================================

T = TypeVar('T')  # Input type
R = TypeVar('R')  # Result type


@dataclass(frozen=True)
class CycleDefinition(Generic[T, R]):
    """
    Reusable definition of a semantic Cycle.
    
    A CycleDefinition describes what semantic execution should occur without
    being an active execution instance. It contains:
        - Cycle type identity
        - Semantic objective
        - Ordered Stage definitions
        - Required capabilities (contracts, not implementations)
        - Expected outcome contract
    
    Invariants:
        CD-001: Definition is immutable and reusable
        CD-002: Stages are ordered and must complete in sequence
        CD-003: Capabilities are contracts, not concrete implementations
        CD-004: Pre/postconditions describe semantic requirements
    """
    
    # Identity (required)
    definition_id: str  # Unique identifier for this definition type
    
    # Semantic objective
    name: str  # Human-readable name
    description: str = ""  # Detailed explanation
    semantic_objective: str = ""  # What does this cycle accomplish semantically?
    
    # Stage definitions (ordered)
    stage_definitions: List[StageDefinition] = field(default_factory=list)
    
    # Capability requirements (contract references)
    required_capabilities: List[str] = field(default_factory=list)
    
    # Pre/postconditions
    precondition: Optional[str] = None  # What must be true before cycle starts
    postcondition: Optional[str] = None  # What will be true after cycle completes
    
    # Expected outcome contract
    expected_outcome_type: str = " CycleOutcome"  # Type of expected result
    
    def validate(self) -> "CycleDefinitionValidation":
        """Validate the Cycle definition."""
        errors = []
        
        if not self.definition_id:
            errors.append("definition_id is required")
        if not self.name:
            errors.append("name is required")
        
        for i, stage in enumerate(self.stage_definitions):
            validation = stage.validate()
            if not validation.is_valid:
                errors.append(f"Stage {i} ({stage.name}): {'; '.join(validation.errors)}")
        
        return CycleDefinitionValidation(is_valid=len(errors) == 0, errors=errors)


@dataclass(frozen=True)
class CycleDefinitionValidation:
    """Result of validating a Cycle definition."""
    
    is_valid: bool
    errors: List[str] = field(default_factory=list)


# =============================================================================
# Cycle Context (ephemeral execution state)
# =============================================================================


@dataclass(frozen=True)
class CycleContext:
    """
    Ephemeral semantic context during Cycle execution.
    
    This contains only temporary state needed for the current cycle execution:
        - Current Stage being executed
        - Prior Stage results
        - Intermediate semantic representations
        - Local observations and proposed deltas
    
    Invariants:
        CCXT-001: Context is ephemeral (does not persist across cycles)
        CCXT-002: Context does not become Thread state without explicit delta
        CCXT-003: Context contains only cycle-local information
        CCXT-004: Context is updated atomically during execution
    """
    
    # Identity and ownership
    cycle_id: str  # The Cycle this context belongs to
    thread_id: str  # Owning Thread
    source_revision: int  # Thread revision at cycle start
    
    # Stage progression
    current_stage_index: int = 0
    stage_states: Dict[str, StageProgressionState] = field(default_factory=dict)
    
    # Execution results
    prior_results: List["StageResult"] = field(default_factory=list)
    current_result: Optional["StageResult"] = None
    
    # Semantic state
    observations: List[str] = field(default_factory=list)
    proposed_deltas: List["SemanticDelta"] = field(default_factory=list)
    
    # Error tracking
    errors: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    
    # Provenance
    timestamp_utc: float = 0.0  # Start time
    
    def advance_stage(self, new_index: int) -> "CycleContext":
        """Create new context with advanced stage index."""
        return dataclass_replace(self, current_stage_index=new_index)
    
    def record_result(self, result: "StageResult") -> "CycleContext":
        """Record a Stage result and update context."""
        new_results = self.prior_results + [result]
        new_states = dict(self.stage_states)
        if result.stage_id in self.stage_states:
            new_states[result.stage_id] = (
                StageProgressionState.COMPLETED if result.status == "completed"
                else StageProgressionState.FAILED
            )
        
        return dataclass_replace(
            self,
            prior_results=new_results,
            stage_states=new_states,
            current_result=None,  # Result has been recorded
        )
    
    def add_observation(self, observation: str) -> "CycleContext":
        """Add an observation to the context."""
        return dataclass_replace(
            self, observations=self.observations + [observation]
        )
    
    def add_delta(self, delta: "SemanticDelta") -> "CycleContext":
        """Add a proposed semantic delta to the context."""
        return dataclass_replace(
            self, proposed_deltas=self.proposed_deltas + [delta]
        )


def dataclass_replace(obj: Any, **kwargs) -> Any:
    """Replace fields in a frozen dataclass (similar to dataclasses.replace)."""
    import dataclasses
    if hasattr(obj, '__dataclass_fields__'):
        return dataclasses.replace(obj, **kwargs)
    raise TypeError(f"Cannot replace fields in {type(obj)}")


# =============================================================================
# Stage Result (bounded transformation result)
# =============================================================================


@dataclass(frozen=True)
class StageResult:
    """
    Result of a single Stage execution within a Cycle.
    
    A Stage produces exactly one result when it completes (successfully or
    with failure). This result updates Cycle-local context but does NOT
    directly mutate Thread state.
    
    Invariants:
        SR-001: Each Stage produces exactly one result
        SR-002: Result is typed and semantically meaningful
        SR-003: Failure paths are explicit (no implicit exceptions)
        SR-004: Result contains only Stage-local information (no Thread state)
    """
    
    # Identity
    stage_id: str  # The Stage that produced this result
    cycle_id: str  # Parent Cycle
    
    # Status
    status: str  # "completed", "failed", "skipped", "interrupted"
    
    # Semantic output
    semantic_output: Optional[Any] = None  # The actual meaningful result
    
    # Progression updates
    proposed_context_updates: Dict[str, Any] = field(default_factory=dict)
    
    # Observations
    observations: List[str] = field(default_factory=list)
    
    # Failure information (semantic, not runtime)
    failure_reason: Optional[str] = None  # Why did it fail?
    is_semantic_failure: bool = False  # True if semantic, False if runtime
    
    # Provenance
    timestamp_utc: float = 0.0  # Completion time
    
    def is_success(self) -> bool:
        """Check if the Stage completed successfully."""
        return self.status == "completed"
    
    def is_failure(self) -> bool:
        """Check if the Stage failed (semantic or runtime)."""
        return not self.is_success()


# =============================================================================
# Semantic Delta (proposed Thread state change)
# =============================================================================


@dataclass(frozen=True)
class SemanticDelta:
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
    
    # Identity and ownership
    delta_id: str  # Unique identifier for this delta
    source_cycle_id: str  # Which Cycle produced this delta?
    
    # Version validation
    expected_thread_revision: int  # Thread version at cycle start
    proposed_new_revision: int  # What revision will this produce?
    
    # Changes
    change_type: str  # e.g., "objective_completed", "fact_added"
    changes: Dict[str, Any] = field(default_factory=dict)
    
    # Provenance
    provenance: str = "cycle_outcome"  # How was this delta derived?
    
    def is_stale(self, current_revision: int) -> bool:
        """Check if the delta is stale (expected revision doesn't match)."""
        return current_revision != self.expected_thread_revision
    
    def to_validation_result(self, accepted: bool) -> "DeltaValidationResult":
        """Convert to a validation result."""
        return DeltaValidationResult(
            is_valid=accepted,
            code="ACCEPTED" if accepted else "REJECTED",
            message="Delta accepted" if accepted else "Delta rejected",
        )


# =============================================================================
# Outcome Validation Result
# =============================================================================


@dataclass(frozen=True)
class DeltaValidationResult:
    """Result of validating a semantic delta."""
    
    is_valid: bool
    code: str  # Machine-readable result code
    message: str = ""  # Human-readable explanation


# =============================================================================
# Cycle Outcome (terminal result)
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
        CO-005: Runtime failures are explicitly translated to semantic outcomes
    """
    
    # Identity (required - no defaults)
    cycle_id: str  # Which Cycle produced this outcome?
    thread_id: str  # Owning Thread
    status: CycleOutcomeStatus  # One of the terminal statuses above
    
    # Source information (required - no defaults)
    source_thread_revision: int  # Thread revision at cycle start
    
    # Selection reference (optional - has default)
    loop_decision_id: Optional[str] = None  # Which decision selected this cycle?
    
    # Semantic result
    semantic_result: Optional[Any] = None  # The actual meaningful result
    completion_reason: str = ""  # Why did it complete (or fail)?
    
    # Proposed changes to Thread state
    proposed_deltas: List[SemanticDelta] = field(default_factory=list)
    
    # Stage results summary
    stage_results: List[StageResult] = field(default_factory=list)
    stages_completed: int = 0  # Number of Stages that completed
    
    # Failure information (semantic vs runtime)
    failure_reason: Optional[str] = None  # Why did it fail?
    interruption_reason: Optional[str] = None  # Why was it interrupted?
    is_runtime_failure: bool = False  # True if translated from Core runtime
    runtime_error_type: Optional[str] = None  # What kind of runtime error?
    
    # Progression state at completion
    final_progression_state: CycleProgressionState = CycleProgressionState.COMPLETED
    
    # Provenance
    timestamp_utc: float = 0.0  # Completion time
    
    def is_success(self) -> bool:
        """Check if the Cycle completed successfully."""
        return self.status in {
            CycleOutcomeStatus.COMPLETED,
            CycleOutcomeStatus.PARTIALLY_COMPLETED,
        }
    
    def is_failure(self) -> bool:
        """Check if the Cycle failed (semantic or runtime)."""
        return not self.is_success()
    
    def get_summary(self) -> str:
        """Get a human-readable summary of the outcome."""
        parts = [f"Cycle {self.cycle_id[:8]}..."]
        
        if self.status == CycleOutcomeStatus.COMPLETED:
            parts.append("completed successfully")
        elif self.status == CycleOutcomeStatus.PARTIALLY_COMPLETED:
            parts.append(f"partially completed ({self.stages_completed} stages)")
        else:
            parts.append(f"{self.status.value}")
            if self.failure_reason:
                parts.append(f": {self.failure_reason}")
        
        return " ".join(parts)


# =============================================================================
# Interruption Reason (semantic vs runtime)
# =============================================================================


class CycleInterruptionReason(Enum):
    """
    Reasons for Cycle interruption.
    
    Distinguishes semantic interruptions (Loop/Thread decides) from runtime
    cancellations (Core stops execution).
    """
    
    # Semantic interruption (policy-driven)
    LOOP_POLICY_CHANGE = "loop_policy_change"
    THREAD_OBJECTIVE_COMPLETED = "thread_objective_completed"
    THREAD_SUSPENDED = "thread_suspended"
    THREAD_TERMINATED = "thread_terminated"
    
    # Runtime cancellation
    TIMEOUT = "timeout"
    RESOURCE_EXHAUSTED = "resource_exhausted"
    PARENT_CANCELLED = "parent_cancelled"
    SYSTEM_SHUTDOWN = "system_shutdown"


# =============================================================================
# Validation helpers
# =============================================================================


@dataclass(frozen=True)
class CycleValidationResult:
    """Result of validating a Cycle instance."""
    
    is_valid: bool
    code: str  # Machine-readable validation code
    message: str = ""  # Human-readable explanation
    details: List[str] = field(default_factory=list)


def validate_cycle_ownership(
    cycle_thread_id: str,
    thread_reference: ThreadReference
) -> CycleValidationResult:
    """Validate that a Cycle is owned by the correct Thread."""
    if cycle_thread_id != thread_reference.thread_id:
        return CycleValidationResult(
            is_valid=False,
            code="THREAD_MISMATCH",
            message=f"Cycle thread_id ({cycle_thread_id}) does not match "
                    f"expected thread_id ({thread_reference.thread_id})"
        )
    
    return CycleValidationResult(is_valid=True, code="VALID", message="Ownership validated")


# =============================================================================
# PHASE 3.10.9 - Concrete Cycle Types
# =============================================================================

from .concrete import (
    # Interpretation cycle (Conversation)
    InterpretationStage,
    InterpretationCycle,
    
    # Response cycle (Conversation)
    ResponseStage,
    ResponseCycle,
    
    # Planning cycle (Task)
    PlanningStage,
    PlanningCycle,
    
    # Execution cycle (Task)
    ExecutionStage,
    ExecutionCycle,
    
    # Evaluation cycle (Task)
    EvaluationStage,
    EvaluationCycle,
    
    # Observation cycle (Monitoring)
    ObservationStage,
    ObservationCycle,
    
    # Reflection cycle (Internal)
    ReflectionStage,
    ReflectionCycle,
    
    create_cycle_from_kind,
)

# =============================================================================
# Export all public symbols
# =============================================================================

__all__ = [
    # Progression states (semantic)
    "CycleProgressionState",
    "StageProgressionState",
    
    # Outcome status (terminal)
    "CycleOutcomeStatus",
    
    # Identity types
    "CycleIdentity",
    "ThreadReference",
    "LoopDecisionReference",
    
    # Definition types
    "StageDefinition",
    "StageDefinitionValidation",
    "CycleDefinition",
    "CycleDefinitionValidation",
    
    # Context and result types
    "CycleContext",
    "StageResult",
    "SemanticDelta",
    "DeltaValidationResult",
    "CycleOutcome",
    
    # Failure/interruption
    "CycleInterruptionReason",
    
    # Validation
    "CycleValidationResult",
    "validate_cycle_ownership",
    
    # =============================================================================
    # PHASE 3.10.9 - Concrete Cycle Types
    # =============================================================================
    
    # Interpretation cycle (Conversation)
    "InterpretationStage",
    "InterpretationCycle",
    
    # Response cycle (Conversation)
    "ResponseStage",
    "ResponseCycle",
    
    # Planning cycle (Task)
    "PlanningStage",
    "PlanningCycle",
    
    # Execution cycle (Task)
    "ExecutionStage",
    "ExecutionCycle",
    
    # Evaluation cycle (Task)
    "EvaluationStage",
    "EvaluationCycle",
    
    # Observation cycle (Monitoring)
    "ObservationStage",
    "ObservationCycle",
    
    # Reflection cycle (Internal)
    "ReflectionStage",
    "ReflectionCycle",
    
    # Utility
    "create_cycle_from_kind",
]