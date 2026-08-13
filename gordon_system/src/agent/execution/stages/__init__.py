# Execution Stage Contracts
# =========================

"""
Execution stage contracts and base classes.

An ExecutionStage owns one bounded semantic transformation within an
ExecutionCycle. It is NOT:
    - A Python function or method (those belong to Capabilities)
    - An unbounded loop or iteration
    - A lifecycle manager

An ExecutionStage IS:
    - One bounded semantic transformation
    - Selected from a CycleDefinition
    - Executed within a Cycle context
    - Produces an immutable result
"""

from dataclasses import dataclass, field
from typing import Protocol, Optional, List, Dict, Any, TypeVar, Generic
from enum import Enum
import uuid


# =============================================================================
# Stage Status (semantic outcomes)
# =============================================================================


class StageStatus(Enum):
    """
    Semantic status of a Stage execution.
    
    These describe what happened during stage execution from a semantic
    perspective:
        - COMPLETED: Stage executed successfully and produced expected result
        - PARTIAL: Stage partially completed, more work needed later
        - SKIPPED: Stage was skipped (e.g., due to prior failure)
        - SEMANTIC_FAILURE: Execution failed due to invalid input or constraints
        - RUNTIME_FAILURE: Execution failed due to runtime issues (timeout, etc.)
        - INTERRUPTED: Execution was interrupted before completion
        - REJECTED: Stage result was rejected by Cycle validation
    """
    
    COMPLETED = "completed"
    PARTIAL = "partial"
    SKIPPED = "skipped"
    SEMANTIC_FAILURE = "semantic_failure"
    RUNTIME_FAILURE = "runtime_failure"
    INTERRUPTED = "interrupted"
    REJECTED = "rejected"


# =============================================================================
# Stage Identity
# =============================================================================


@dataclass(frozen=True)
class StageIdentity:
    """Unique semantic identity for a Stage."""
    
    value: str = field(default_factory=lambda: str(uuid.uuid4()))
    
    @classmethod
    def generate(cls) -> "StageIdentity":
        return cls(value=str(uuid.uuid4()))


# =============================================================================
# Stage Definition (reusable template)
# =============================================================================


@dataclass(frozen=True)
class ExecutionStageDefinition:
    """
    Reusable definition of a semantic Stage.
    
    A StageDefinition describes what work should be done but is not executed
    directly. Concrete Stage instances are created during cycle execution.
    
    Invariants:
        SD-001: Definition is immutable and reusable
        SD-002: Pre/postconditions describe semantic requirements
        SD-003: Capability requirements are contract references, not implementations
        SD-004: Input/output contracts define the data flow
    """
    
    # Identity (required)
    definition_id: str  # Unique identifier for this stage type
    
    # Semantic purpose
    name: str  # Human-readable name (e.g., "interpret_input", "reason", "decide")
    description: str = ""  # Detailed explanation
    
    # Input contract (what must be provided)
    input_contract: Optional[str] = None  # JSON schema or type description
    
    # Output contract (what will be produced)
    output_contract: Optional[str] = None  # JSON schema or type description
    
    # Semantic requirements
    precondition: Optional[str] = None  # What must be true before execution
    postcondition: Optional[str] = None  # What will be true after execution
    
    # Capability requirement (contract reference, not implementation)
    required_capability_id: Optional[str] = None
    
    # Progression constraints
    interruptible: bool = True  # Can this stage be interrupted?
    idempotent: bool = False  # Can this stage be safely repeated?
    
    def validate(self) -> "StageDefinitionValidation":
        """Validate the Stage definition."""
        errors = []
        
        if not self.definition_id:
            errors.append("definition_id is required")
        if not self.name:
            errors.append("name is required")
        
        return StageDefinitionValidation(is_valid=len(errors) == 0, errors=errors)


@dataclass(frozen=True)
class StageDefinitionValidation:
    """Result of validating a Stage definition."""
    
    is_valid: bool
    errors: List[str] = field(default_factory=list)


# =============================================================================
# Stage Context (execution-time state)
# =============================================================================


@dataclass(frozen=True)
class StageContext:
    """
    Execution-time context for a Stage.
    
    Contains only the information needed during stage execution:
        - Parent Cycle reference
        - Thread snapshot at cycle start
        - Local working memory
        - Observations made so far
    
    Invariants:
        STG-CTX-001: Context contains only execution-local information
        STG-CTX-002: Context is ephemeral (not persisted across cycles)
        STG-CTX-003: Context does not contain runtime scheduling details
    """
    
    # Identity and ownership
    stage_id: str  # The Stage this context belongs to
    cycle_id: str  # Parent Cycle
    thread_id: str  # Owning Thread
    
    # Source information
    source_revision: int  # Thread revision at cycle start
    
    # Local state (for this stage's execution)
    working_memory: Dict[str, Any] = field(default_factory=dict)
    observations: List[str] = field(default_factory=list)
    
    # Progression info
    input_data: Optional[Any] = None  # Input provided to this stage
    prior_stages_completed: int = 0


# =============================================================================
# Stage Result (bounded transformation result)
# =============================================================================


@dataclass(frozen=True)
class ExecutionStageResult:
    """
    Result of a single Stage execution within a Cycle.
    
    A Stage produces exactly one result when it completes (successfully or
    with failure). This result updates Cycle-local context but does NOT
    directly mutate Thread state.
    
    Invariants:
        STG-RES-001: Each Stage produces exactly one result
        STG-RES-002: Result is typed and semantically meaningful
        STG-RES-003: Failure paths are explicit (no implicit exceptions)
        STG-RES-004: Result contains only Stage-local information
    """
    
    # Identity
    stage_id: str  # The Stage that produced this result
    cycle_id: str  # Parent Cycle
    
    # Status
    status: StageStatus  # Semantic outcome of the stage
    
    # Semantic output (if successful)
    semantic_output: Optional[Any] = None  # The actual meaningful result
    
    # Proposed local updates
    proposed_context_updates: Dict[str, Any] = field(default_factory=dict)
    
    # Observations made during execution
    observations: List[str] = field(default_factory=list)
    
    # Failure information (semantic vs runtime)
    failure_reason: Optional[str] = None  # Why did it fail?
    is_semantic_failure: bool = False  # True if semantic, False if runtime
    runtime_error_type: Optional[str] = None  # What kind of runtime error?
    
    # Provenance
    timestamp_utc: float = field(default_factory=lambda: 0.0)  # Completion time
    
    def is_success(self) -> bool:
        """Check if the Stage completed successfully."""
        return self.status in {StageStatus.COMPLETED, StageStatus.PARTIAL}
    
    def is_failure(self) -> bool:
        """Check if the Stage failed (semantic or runtime)."""
        return not self.is_success()


# =============================================================================
# Capability Request
# =============================================================================


@dataclass(frozen=True)
class CapabilityRequest:
    """
    Request for a Capability invocation.
    
    This is how a Stage asks for work to be done by a Capability. The
    Capability implementation handles the actual work.
    
    Invariants:
        CR-001: Request contains only semantic information (no runtime handles)
        CR-002: Request references expected capability contract
        CR-003: Request includes typed input data
    """
    
    # Identity and ownership
    stage_id: str  # Which Stage is making this request?
    cycle_id: str  # Parent Cycle
    
    # Capability reference (contract ID, not implementation)
    capability_id: str
    
    # Input data (typed, matching the Capability's input contract)
    input_data: Any


# =============================================================================
# Capability Outcome
# =============================================================================


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
# Capability Port Protocol
# =============================================================================


class CapabilityPort(Protocol):
    """
    Port for invoking Capabilities from Execution stages.
    
    Invariants:
        CAP-001: Stage requests capabilities, does not select implementations
        CAP-002: Capability returns typed results, not raw runtime objects
        CAP-003: Capability invocation is bounded (not infinite)
    """
    
    async def invoke(
        self,
        request: "CapabilityRequest",
    ) -> "CapabilityOutcome":
        """Invoke a Capability with given input. Return typed outcome."""
        ...


# =============================================================================
# Stage Protocol
# =============================================================================


class ExecutionStage(Protocol):
    """
    Protocol for a bounded semantic transformation within an ExecutionCycle.
    
    A Stage:
        - Has a well-defined input and output contract
        - Executes one bounded semantic transformation
        - Produces exactly one result
        - Does not own Thread state (only proposes updates)
        - Is selected from a CycleDefinition
    
    Invariants:
        STG-001: Each Stage produces exactly one result
        STG-002: Result is typed and semantically meaningful
        STG-003: Stage cannot directly mutate Thread state
        STG-004: Stage execution is bounded (not infinite)
    """
    
    @property
    def stage_id(self) -> str:
        """Get the unique Stage identity."""
        ...
    
    @property
    def definition(self) -> ExecutionStageDefinition:
        """Get the Stage definition (template)."""
        ...
    
    @property
    def cycle_id(self) -> str:
        """Get the parent Cycle ID."""
        ...
    
    @property
    def thread_id(self) -> str:
        """Get the Thread this Stage belongs to."""
        ...
    
    async def execute(
        self,
        context: StageContext,
        capability_port: Optional[CapabilityPort] = None,
    ) -> ExecutionStageResult:
        """
        Execute this Stage with given context.
        
        Args:
            context: Current execution context (Thread snapshot, local state)
            capability_port: Port for invoking Capabilities if needed
            
        Returns:
            The result of this Stage execution
            
        Raises:
            RuntimeError: If Stage cannot execute due to invalid state
        """
        ...
    
    def validate_precondition(self, context: StageContext) -> bool:
        """Check if preconditions are satisfied for this Stage."""
        ...


# =============================================================================
# Export all public symbols
# =============================================================================

__all__ = [
    # Status types
    "StageStatus",
    
    # Identity
    "StageIdentity",
    
    # Definition
    "ExecutionStageDefinition",
    "StageDefinitionValidation",
    
    # Context and result
    "StageContext",
    "ExecutionStageResult",
    
    # Capability request and outcome
    "CapabilityRequest",
    "CapabilityOutcome",
    
    # Protocol
    "ExecutionStage",
    "CapabilityPort",
]