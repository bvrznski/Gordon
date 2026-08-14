# Interaction Semantics - Phase 3.14.4
# =====================================
#
# Canonical semantics of Requests, Responses, and Commands.
#
# This module establishes immutable rules governing all Request, Response,
# and Command interactions throughout the repository.
#
# These interaction categories define intentional cooperation between
# architectural participants. They do not define ownership. They do not
# grant authority. They define communication semantics.

"""
Canonical Request, Response, and Command Semantics for Gordon Phase 3.14.4

This module establishes immutable rules governing all Request, Response,
and Command interactions throughout the repository.

These interaction categories define intentional cooperation between
architectural participants.

They do not define ownership.
They do not grant authority.
They do not define transport.
They define communication semantics.
"""

from dataclasses import dataclass, field
from typing import Dict, Any, Optional, Tuple, FrozenSet
from enum import Enum, auto
import uuid
import time

try:
    from .taxonomy import (
        Interaction,
        Request as TaxonomyRequest,
        Response as TaxonomyResponse,
        Command as TaxonomyCommand,
        InteractionId,
        InteractionCorrelation,
        InteractionCategory,
        InteractionTrait,
    )
except ModuleNotFoundError:
    try:
        from agent.architecture.interaction.taxonomy import (
        Interaction,
        Request as TaxonomyRequest,
        Response as TaxonomyResponse,
        Command as TaxonomyCommand,
        InteractionId,
        InteractionCorrelation,
        InteractionCategory,
            InteractionTrait,
        )
    except ModuleNotFoundError:
        from gordon_system.src.agent.architecture.interaction.taxonomy import (
            Interaction,
            Request as TaxonomyRequest,
            Response as TaxonomyResponse,
            Command as TaxonomyCommand,
            InteractionId,
            InteractionCorrelation,
            InteractionCategory,
            InteractionTrait,
        )


# =============================================================================
# REQUEST LIFECYCLE STATES
# =============================================================================

class RequestState(Enum):
    """
    Canonical Request lifecycle states.
    
    Lifecycle transitions shall remain deterministic:
        Created -> Validated -> Accepted -> Processing
            -> Completed | Rejected | Cancelled
    
    Invariants:
        - RQ-STATE-001: State progression is monotonically forward
        - RQ-STATE-002: Terminal states preserve provenance
        - RQ-STATE-003: No state transitions after terminal state
    """
    
    CREATED = "created"           # Request initiated, awaiting validation
    VALIDATED = "validated"       # Semantic and structural validation passed
    ACCEPTED = "accepted"         # Accepted for processing by recipient
    PROCESSING = "processing"     # Processing has begun
    COMPLETED = "completed"       # Successfully completed with response
    REJECTED = "rejected"         # Explicitly rejected by recipient
    CANCELLED = "cancelled"       # Cancelled before completion


# =============================================================================
# RESPONSE LIFECYCLE STATES
# =============================================================================

class ResponseState(Enum):
    """
    Canonical Response lifecycle states.
    
    Responses shall be produced only after a valid Request exists.
    
    Canonical states:
        - Pending: Waiting for response
        - Partial: Partial result delivered
        - Completed: Full result delivered
        - Failed: Execution failed with error
        - Cancelled: Request was cancelled
    
    Invariants:
        - RS-STATE-001: Response lifecycle depends on Request lifecycle
        - RS-STATE-002: Terminal states preserve provenance
        - RS-STATE-003: Every Response references exactly one Request
    """
    
    PENDING = "pending"           # Waiting for response delivery
    PARTIAL = "partial"           # Partial result delivered
    COMPLETED = "completed"       # Full result delivered
    FAILED = "failed"             # Execution failed with error
    CANCELLED = "cancelled"       # Request was cancelled


# =============================================================================
# COMMAND LIFECYCLE STATES
# =============================================================================

class CommandState(Enum):
    """
    Canonical Command lifecycle states.
    
    Authorization shall always precede execution:
        Created -> Validated -> Authorized -> Scheduled -> Executed -> Completed
    
    Invariants:
        - CMD-STATE-001: State progression is monotonically forward
        - CMD-STATE-002: Authorization precedes execution
        - CMD-STATE-003: No state transitions after terminal state
    """
    
    CREATED = "created"           # Command issued, awaiting validation
    VALIDATED = "validated"       # Semantic and structural validation passed
    AUTHORIZED = "authorized"     # Authority check passed
    SCHEDULED = "scheduled"       # Scheduled for execution
    EXECUTED = "executed"         # Execution has begun/completed
    COMPLETED = "completed"       # Command completed successfully
    REJECTED = "rejected"         # Rejected by executor (authority/validity)


# =============================================================================
# OUTCOME TYPES
# =============================================================================

class Outcome(Enum):
    """
    Canonical outcome types for interactions.
    
    Every terminal interaction shall have an explicit outcome.
    """
    
    SUCCESS = "success"
    FAILURE = "failure"
    PARTIAL = "partial"           # Some work completed before failure
    CANCELLED = "cancelled"
    REJECTED = "rejected"         # Explicitly rejected by recipient
    TIMEOUT = "timeout"


# =============================================================================
# DIAGNOSTIC METADATA
# =============================================================================

@dataclass(frozen=True, slots=True)
class DiagnosticMetadata:
    """
    Diagnostic metadata for interaction observability.
    
    Required fields for every observable interaction:
        - interaction_id: Unique identifier for the interaction
        - correlation_id: Coordinator advancement context
        - timestamp_utc: When the interaction occurred
        - lifecycle_state: Current phase in lifecycle
    
    Invariants:
        - DIAG-001: All required fields shall be present
        - DIAG-002: Timestamps are monotonic
        - DIAG-003: No sensitive information is exposed
    """
    
    interaction_id: InteractionId
    correlation_id: str
    timestamp_utc: float
    
    # Lifecycle tracking
    lifecycle_state: RequestState  # For Request/Response, this tracks the request lifecycle
    originating_thread_id: Optional[str] = None
    
    # Execution context
    execution_context: Dict[str, Any] = field(default_factory=dict)
    
    # Outcome (for terminal states)
    outcome: Optional[Outcome] = None
    error_message: Optional[str] = None
    error_code: Optional[str] = None
    
    def is_terminal(self) -> bool:
        """Check if this interaction has reached a terminal state."""
        return self.lifecycle_state in (
            RequestState.COMPLETED,
            RequestState.REJECTED,
            RequestState.CANCELLED,
        )
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert diagnostic metadata to dictionary for serialization."""
        result = {
            "interaction_id": self.interaction_id.value,
            "correlation_id": self.correlation_id,
            "timestamp_utc": self.timestamp_utc,
            "lifecycle_state": self.lifecycle_state.value,
            "execution_context": dict(self.execution_context),
        }
        
        if self.originating_thread_id:
            result["originating_thread_id"] = self.originating_thread_id
        
        if self.outcome:
            result["outcome"] = self.outcome.value
        
        if self.error_message:
            result["error_message"] = self.error_message
        
        if self.error_code:
            result["error_code"] = self.error_code
        
        return result


# =============================================================================
# REQUEST SEMANTICS
# =============================================================================

@dataclass(frozen=True, slots=True)
class Request(Interaction):
    """
    A Request interaction asks another participant to perform work.
    
    Semantic properties (canonical Phase 3.14.4 definition):
        - Does not imply approval or success
        - Does not grant authority
        - Does not transfer ownership
        - Expects an outcome (Response)
        - May be acknowledged or unacknowledged
    
    Request lifecycle:
        Created -> Validated -> Accepted -> Processing -> Completed | Rejected | Cancelled
    
    Invariants:
        - RQ-001: Every Request has exactly one primary recipient
        - RQ-002: Request semantics are independent of transport
        - RQ-003: Authority is evaluated separately from the request
        - RQ-004: Ownership is preserved throughout lifecycle
        - RQ-005: Correlation ID links to Response lifecycle
    """
    
    # Category is fixed to REQUEST
    category: InteractionCategory = field(default=InteractionCategory.REQUEST, init=False)
    
    # Identity (inherited from Interaction)
    interaction_id: InteractionId
    
    # Semantic participants (must come after all defaults from base class)
    participants: Tuple[str, ...] = field(default_factory=tuple)  # All involved components (initiator included in context)
    
    # Request-specific properties - these need defaults too since they follow base class defaults
    initiator: str = "unknown"  # Who initiated the request
    recipient: str = ""  # Primary recipient of the request (empty for broadcast/subscription patterns)
    purpose: str = ""  # What the request aims to achieve (empty for unspecified)
    execution_context: Dict[str, Any] = field(default_factory=dict)  # Execution context for this request
    
    # Lifecycle state (canonical Phase 3.14.4 requirement)
    lifecycle_state: RequestState = RequestState.CREATED
    timestamp_utc: float = field(default_factory=time.monotonic)
    
    # Correlation context (canonical Phase 3.14.4 requirement)
    correlation_id: str = field(default_factory=lambda: uuid.uuid4().hex[:16])
    causation_id: Optional[str] = None
    
    # Payload
    payload: Dict[str, Any] = field(default_factory=dict)
    
    # Optional metadata
    traits: FrozenSet[InteractionTrait] = field(default_factory=frozenset)
    
    # Response tracking
    response_expected: bool = True  # Whether a Response is expected
    correlation_context: Optional[InteractionCorrelation] = None
    
    def is_replayable(self) -> bool:
        """Check if this request is replayable."""
        return InteractionTrait.REPLAYABLE in self.traits
    
    def is_observable(self) -> bool:
        """Check if this request is observable."""
        return InteractionTrait.OBSERVABLE in self.traits
    
    def with_state(self, new_state: RequestState) -> "Request":
        """Create a new request with updated lifecycle state."""
        return dataclass_replace(
            self,
            lifecycle_state=new_state
        )
    
    def to_diagnostic_metadata(self) -> DiagnosticMetadata:
        """Convert this Request to diagnostic metadata for observability."""
        return DiagnosticMetadata(
            interaction_id=self.interaction_id,
            correlation_id=self.correlation_id,
            timestamp_utc=self.timestamp_utc,
            lifecycle_state=self.lifecycle_state,
            originating_thread_id=self.correlation_context.originating_thread_id if self.correlation_context else None,
            execution_context=dict(self.execution_context),
            outcome=None  # Non-terminal state
        )


# =============================================================================
# RESPONSE SEMANTICS
# =============================================================================

@dataclass(frozen=True, slots=True)
class Response(Interaction):
    """
    A Response interaction answers a Request and completes its lifecycle.
    
    Semantic properties (canonical Phase 3.14.4 definition):
        - Contains outcome information (success/failure/partial)
        - Completes a Request's lifecycle
        - References exactly one originating Request
        - Never exists independently without an originating Request
    
    Response lifecycle:
        Pending -> Completed | Failed | Cancelled
    
    Invariants:
        - RS-001: Every Response references exactly one originating Request
        - RS-002: Response lifecycle depends on Request lifecycle
        - RS-003: Responses never imply approval or authority
        - RS-004: Ownership is preserved throughout lifecycle
        - RS-005: Provenance is preserved in terminal states
    """
    
    # Category is fixed to RESPONSE
    category: InteractionCategory = field(default=InteractionCategory.RESPONSE, init=False)
    
    # Identity (inherited from Interaction)
    interaction_id: InteractionId
    
    # Semantic participants - must come after all defaults from base class
    participants: Tuple[str, ...] = field(default_factory=tuple)  # All involved components (initiator included in context)
    
    # Response-specific fields with defaults to maintain dataclass ordering
    responder: str = ""  # Who responded (empty for unspecified)
    requester: str = ""  # Original request initiator (empty for unspecified)
    
    # Request correlation (canonical Phase 3.14.4 requirement)
    originating_request_id: InteractionId = field(default_factory=lambda: InteractionId(value=f"int_{uuid.uuid4().hex[:24]}"))  # Exactly one Request referenced
    originating_correlation_id: str = ""  # Correlation ID from Request
    
    # Response-specific properties - outcome with default for non-terminal states
    outcome: Outcome = Outcome.SUCCESS  # Completion state (default to SUCCESS for non-terminal states)
    completion_state: str = "complete"  # complete, partial, error
    timestamps: Dict[str, float] = field(default_factory=dict)  # timing information
    
    # Diagnostic metadata (canonical Phase 3.14.4 requirement)
    diagnostic_metadata: Dict[str, Any] = field(default_factory=dict)
    
    # Lifecycle state
    lifecycle_state: ResponseState = ResponseState.PENDING
    timestamp_utc: float = field(default_factory=time.monotonic)
    
    # Correlation context
    correlation_id: str = field(default_factory=lambda: uuid.uuid4().hex[:16])
    causation_id: Optional[str] = None
    
    # Payload (result data)
    payload: Dict[str, Any] = field(default_factory=dict)
    
    # Optional metadata
    traits: FrozenSet[InteractionTrait] = field(default_factory=frozenset)
    correlation_context: Optional[InteractionCorrelation] = None
    
    def is_replayable(self) -> bool:
        """Check if this response is replayable."""
        return InteractionTrait.REPLAYABLE in self.traits
    
    def is_observable(self) -> bool:
        """Check if this response is observable."""
        return InteractionTrait.OBSERVABLE in self.traits
    
    @property
    def success(self) -> bool:
        """Return True if the response indicates successful completion."""
        return self.outcome == Outcome.SUCCESS
    
    def to_diagnostic_metadata(self) -> DiagnosticMetadata:
        """Convert this Response to diagnostic metadata for observability."""
        outcome = (
            self.outcome 
            if self.lifecycle_state in (ResponseState.COMPLETED, ResponseState.FAILED, ResponseState.CANCELLED)
            else None
        )
        
        error_message = None
        error_code = None
        
        if outcome == Outcome.FAILURE and "error" in self.diagnostic_metadata:
            error_info = self.diagnostic_metadata["error"]
            if isinstance(error_info, dict):
                error_message = error_info.get("message")
                error_code = error_info.get("code")
            else:
                error_message = str(error_info)
        
        return DiagnosticMetadata(
            interaction_id=self.interaction_id,
            correlation_id=self.correlation_id,
            timestamp_utc=self.timestamp_utc,
            lifecycle_state=RequestState.COMPLETED if outcome and outcome != Outcome.CANCELLED else RequestState.CANCELLED,
            originating_thread_id=self.correlation_context.originating_thread_id if self.correlation_context else None,
            execution_context={
                "response_to": self.originating_request_id.value,
                "outcome": self.outcome.value
            },
            outcome=outcome,
            error_message=error_message,
            error_code=error_code,
        )


# =============================================================================
# COMMAND SEMANTICS
# =============================================================================

@dataclass(frozen=True, slots=True)
class Command(Interaction):
    """
    A Command interaction expresses the intent that an action should occur.
    
    Semantic properties (canonical Phase 3.14.4 definition):
        - Expresses intent to perform an action
        - Authority is evaluated separately from command semantics
        - Whether the Command is executed depends entirely upon authority validation
        - Commands are independent interactions (not Request/Response pairs)
    
    Command lifecycle:
        Created -> Validated -> Authorized -> Scheduled -> Executed -> Completed
    
    Invariants:
        - CMD-001: Commands express intent, not execution
        - CMD-002: Authority is evaluated separately from command semantics
        - CMD-003: Execution does not redefine command semantics
        - CMD-004: Ownership is preserved throughout lifecycle
        - CMD-005: No authority is granted by sending a Command
    """
    
    # Category is fixed to COMMAND
    category: InteractionCategory = field(default=InteractionCategory.COMMAND, init=False)
    
    # Identity (inherited from Interaction)
    interaction_id: InteractionId
    
    # Semantic participants - must come after all defaults from base class
    participants: Tuple[str, ...] = field(default_factory=tuple)  # All involved components
    
    # Command-specific properties (canonical Phase 3.14.4 requirement)
    issuer: str = ""  # Who issued the command (empty for unspecified)
    intended_executor: str = ""  # Intended recipient of the command
    requested_action: str = ""  # What action is being commanded (empty for unspecified)
    execution_context: Dict[str, Any] = field(default_factory=dict)
    
    # Lifecycle state (canonical Phase 3.14.4 requirement)
    lifecycle_state: CommandState = CommandState.CREATED
    timestamp_utc: float = field(default_factory=time.monotonic)
    
    # Correlation context (canonical Phase 3.14.4 requirement)
    correlation_id: str = field(default_factory=lambda: uuid.uuid4().hex[:16])
    causation_id: Optional[str] = None
    
    # Authority tracking
    authority_verified: bool = False  # Whether authority has been verified
    authorization_context: Dict[str, Any] = field(default_factory=dict)
    
    # Payload
    payload: Dict[str, Any] = field(default_factory=dict)
    
    # Optional metadata
    traits: FrozenSet[InteractionTrait] = field(default_factory=frozenset)
    correlation_context: Optional[InteractionCorrelation] = None
    
    def is_replayable(self) -> bool:
        """Check if this command is replayable."""
        return InteractionTrait.REPLAYABLE in self.traits
    
    def is_observable(self) -> bool:
        """Check if this command is observable."""
        return InteractionTrait.OBSERVABLE in self.traits
    
    def with_state(self, new_state: CommandState) -> "Command":
        """Create a new command with updated lifecycle state."""
        return dataclass_replace(
            self,
            lifecycle_state=new_state
        )
    
    def to_diagnostic_metadata(self) -> DiagnosticMetadata:
        """Convert this Command to diagnostic metadata for observability."""
        outcome = None
        
        if self.lifecycle_state in (CommandState.COMPLETED,):
            outcome = Outcome.SUCCESS
        elif self.lifecycle_state == CommandState.REJECTED:
            outcome = Outcome.REJECTED
        
        return DiagnosticMetadata(
            interaction_id=self.interaction_id,
            correlation_id=self.correlation_id,
            timestamp_utc=self.timestamp_utc,
            lifecycle_state=RequestState.CREATED,  # Commands don't have Request states
            originating_thread_id=self.correlation_context.originating_thread_id if self.correlation_context else None,
            execution_context={
                **dict(self.execution_context),
                "command_action": self.requested_action,
                "authority_verified": self.authority_verified,
            },
            outcome=outcome,
        )


# =============================================================================
# UTILITY FUNCTIONS
# =============================================================================

def dataclass_replace(obj: Any, **kwargs) -> Any:
    """Replace fields in a frozen dataclass."""
    if hasattr(obj, '__dataclass_fields__'):
        import dataclasses
        return dataclasses.replace(obj, **kwargs)
    raise TypeError(f"Cannot replace fields in {type(obj)}")


# =============================================================================
# SEMANTIC RELATIONSHIPS
# =============================================================================

def are_semantic_categories_compatible(cat1: InteractionCategory, cat2: InteractionCategory) -> bool:
    """
    Check if two interaction categories can coexist semantically.
    
    Canonical compatibility rules (Phase 3.14.4):
        - Request/Response: Compatible (complementary lifecycle)
        - Command independent: No inherent relationship
        - Event independent: Historical record
    
    Args:
        cat1: First interaction category
        cat2: Second interaction category
        
    Returns:
        True if compatible, False otherwise
    """
    # Same category is always compatible
    if cat1 == cat2:
        return True
    
    # Request and Response are complementary
    request_response_pairs = {
        (InteractionCategory.REQUEST, InteractionCategory.RESPONSE),
        (InteractionCategory.RESPONSE, InteractionCategory.REQUEST),
    }
    
    if (cat1, cat2) in request_response_pairs:
        return True
    
    return True  # Default: compatible


def get_request_state_for_response(response_state: ResponseState) -> RequestState:
    """
    Map Response lifecycle state to Request lifecycle state.
    
    This enables correlation between Request and Response lifecycles.
    
    Args:
        response_state: The current Response lifecycle state
        
    Returns:
        Corresponding Request lifecycle state
    """
    mapping = {
        ResponseState.PENDING: RequestState.PROCESSING,
        ResponseState.COMPLETED: RequestState.COMPLETED,
        ResponseState.FAILED: RequestState.REJECTED,
        ResponseState.CANCELLED: RequestState.CANCELLED,
    }
    
    return mapping.get(response_state, RequestState.PROCESSING)


# =============================================================================
# EXPORTS
# =============================================================================

__all__ = [
    # Lifecycle states
    "RequestState",
    "ResponseState",
    "CommandState",
    
    # Outcome types
    "Outcome",
    
    # Diagnostic metadata
    "DiagnosticMetadata",
    
    # Semantic types (canonical Phase 3.14.4 definitions)
    "Request",
    "Response",
    "Command",
    
    # Utility functions
    "dataclass_replace",
    "are_semantic_categories_compatible",
    "get_request_state_for_response",
]