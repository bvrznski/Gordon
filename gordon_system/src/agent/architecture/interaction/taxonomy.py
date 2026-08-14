# Interaction Taxonomy
# ====================
#
# PHASE 3.14.2 - Canonical Interaction Categories
#
# This module defines the canonical taxonomy of interactions in Gordon.
# Every interaction shall belong to exactly one primary semantic category.

"""
Canonical Interaction Taxonomy for Gordon Phase 3.14.2

This module establishes the authoritative categorization of all architectural
interactions. Every interaction belongs to exactly one primary semantic category,
which defines its semantic intent without implying implementation details.

Taxonomy Structure:

    Interaction
    ├─ Request        - asks another participant to perform work
    ├─ Response       - answers a Request, completes lifecycle
    ├─ Command        - expresses intent to perform an action
    ├─ Event          - describes something that already occurred
    ├─ Signal         - communicates runtime state
    ├─ Notification   - informs participants without expecting work
    ├─ Proposal       - recommends possible action
    ├─ Observation    - reports measured facts
    ├─ Query          - requests information only (no state change)
    ├─ Publication    - makes information available (no designated recipient)
    ├─ Subscription   - expresses interest in future Publications
    ├─ Checkpoint     - records recoverable execution point
    ├─ Heartbeat      - communicates liveness
    ├─ Synchronization - coordinates multiple participants
    ├─ Transaction    - groups interactions into atomic context
    └─ Recovery       - coordinates restoration after failure

Semantics are orthogonal to:
- Transport (Streams may carry any category)
- Execution (Execution schedules but doesn't redefine semantics)
- Ownership (Owner remains independent of category)
- Implementation (Category is semantic, not technical)

Invariants:
- Every interaction has exactly one primary category
- Category defines semantic intent, not implementation
- Category is immutable and preserved throughout lifetime
- Category is orthogonal to transport mechanism
"""

from dataclasses import dataclass, field
from typing import Dict, Tuple, Optional, Set, FrozenSet, Type, Any, Union
from enum import Enum, auto
import uuid
import time


# =============================================================================
# PRIMARY CATEGORY ENUMERATION (The Canonical Taxonomy)
# =============================================================================

class InteractionCategory(Enum):
    """
    Primary semantic categories for interactions.
    
    Every interaction belongs to exactly one primary category.
    
    Categories define semantic intent. They do not define:
        - Implementation
        - Transport mechanism
        - Ownership model
        - Execution semantics
    
    Categories are orthogonal to each other and shall never be combined.
    """
    
    # Exchange categories (request/response patterns)
    REQUEST = "request"           # Asks another participant to perform work
    RESPONSE = "response"         # Answers a Request, completes lifecycle
    
    # Action categories (intentional operations)
    COMMAND = "command"           # Expresses intent to perform an action
    EVENT = "event"               # Describes something that already occurred
    
    # Communication categories (state and notification)
    SIGNAL = "signal"             # Communicates runtime state
    NOTIFICATION = "notification" # Informs without expecting work
    
    # Information categories (query/recommendation patterns)
    PROPOSAL = "proposal"         # Recommends possible action
    OBSERVATION = "observation"   # Reports measured facts
    QUERY = "query"               # Requests information only (no state change)
    
    # Distribution categories (publication/subscription patterns)
    PUBLICATION = "publication"   # Makes information available
    SUBSCRIPTION = "subscription" # Expresses interest in future Publications
    
    # Coordination categories (synchronization and persistence)
    CHECKPOINT = "checkpoint"     # Records recoverable execution point
    HEARTBEAT = "heartbeat"       # Communicates liveness
    SYNCHRONIZATION = "synchronization"  # Coordinates multiple participants
    
    # Transactional categories
    TRANSACTION = "transaction"   # Groups interactions into atomic context
    RECOVERY = "recovery"         # Coordinates restoration after failure


# =============================================================================
# SECONDARY TRAITS (Behavioral modifiers)
# =============================================================================

class InteractionTrait(Enum):
    """
    Secondary behavioral traits that may modify primary category semantics.
    
    Traits are optional and can be combined with any primary category.
    They describe behavior patterns without changing semantic intent.
    """
    
    REPLAYABLE = "replayable"           # Can be reproduced without fabricating state
    OBSERVABLE = "observable"           # Exposes diagnostic metadata for monitoring
    ACKNOWLEDGED = "acknowledged"       # Requires explicit acknowledgment by recipient
    idempotent = "idempotent"          # Safe to retry with same effect
    PERSISTENT = "persistent"           # Stored durably beyond runtime lifetime
    TRANSIENT = "transient"             # May be lost without impact
    BOUNDED = "bounded"                 # Has clear start and end boundaries
    UNBOUNDED = "unbounded"             # Open-ended duration
    SYNCHRONOUS = "synchronous"         # Waits for immediate response
    ASYNCHRONOUS = "asynchronous"       # Does not wait for response


# =============================================================================
# INTERACTION IDENTITY
# =============================================================================

@dataclass(frozen=True, slots=True)
class InteractionId:
    """
    Unique identifier for an interaction.
    
    Identity Invariants:
        - I-001: Every interaction has exactly one unique identity
        - I-002: Identity is immutable once created
        - I-003: No two interactions share the same identity
        - I-004: Identity does not change during lifecycle transitions
    
    Note: InteractionId represents the logical identity, separate from
    the interaction's category and payload.
    """
    
    value: str  # Unique identifier string
    
    @classmethod
    def generate(cls) -> "InteractionId":
        """Generate a new unique interaction ID."""
        return cls(value=f"int_{uuid.uuid4().hex[:24]}")
    
    def __str__(self) -> str:
        return self.value


@dataclass(frozen=True, slots=True)
class InteractionCorrelation:
    """
    Correlation context for tracing interaction relationships.
    
    Enables causal and temporal tracking across the system:
        - correlation_id: One complete coordinator advancement
        - causation_id: What caused this interaction (parent)
        - parent_interaction_id: If child of another interaction
        - originating_thread_id: Which thread started the chain
    """
    
    correlation_id: str  # Coordinator advancement context
    causation_id: Optional[str] = None  # Direct cause
    
    # Hierarchy tracking
    parent_interaction_id: Optional[str] = None
    originating_thread_id: Optional[str] = None


# =============================================================================
# BASE INTERACTION TYPE
# =============================================================================

@dataclass(frozen=True, slots=True)
class Interaction:
    """
    Base class for all interaction types.
    
    Every interaction is characterized by:
        - Primary category (defines semantic intent)
        - Identity (unique identifier)
        - Lifecycle state (progression through phases)
        - Participants (involved components)
        - Initiator (who triggered the interaction)
        - Timestamps (when it occurred)
        - Payload (data being transmitted)
    
    Invariants:
        - INTER-001: Exactly one primary category
        - INTER-002: Category is immutable
        - INTER-003: Identity is unique and immutable
        - INTER-004: Lifecycle progresses monotonically
        - INTER-005: Provenance is preserved throughout lifetime
    
    Examples:
        >>> # A Request interaction
        >>> request = Interaction(
        ...     category=InteractionCategory.REQUEST,
        ...     interaction_id=InteractionId.generate(),
        ...     initiator="coordinator",
        ...     participants=["worker"],
        ... )
        ...
        >>> # An Event interaction
        >>> event = Interaction(
        ...     category=InteractionCategory.EVENT,
        ...     interaction_id=InteractionId.generate(),
        ...     initiator="worker",
        ...     participants=["coordinator", "monitor"],
        ... )
    """
    
    # Identity (required first for dataclass field ordering)
    category: InteractionCategory
    interaction_id: InteractionId
    
    # Correlation context - must be before fields with defaults
    correlation_id: str = field(default_factory=lambda: uuid.uuid4().hex[:16])
    causation_id: Optional[str] = None  # Direct cause
    
    # Semantic participants - must come after all defaults
    initiator: str = "unknown"  # Who triggered this interaction
    participants: Tuple[str, ...] = field(default_factory=tuple)  # All involved components
    
    # Direction of semantic flow (initiator -> participants)
    direction: str = "forward"
    
    # Lifecycle state - timestamp with default
    timestamp_utc: float = field(default_factory=time.monotonic)  # When it started (UTC monotonic time)
    
    # Payload (data being transmitted)
    payload: Dict[str, Any] = field(default_factory=dict)
    
    # Optional metadata
    traits: FrozenSet[InteractionTrait] = field(default_factory=frozenset)
    correlation_context: Optional[InteractionCorrelation] = None
    
    def is_replayable(self) -> bool:
        """Check if this interaction is replayable."""
        return InteractionTrait.REPLAYABLE in self.traits
    
    def is_observable(self) -> bool:
        """Check if this interaction is observable."""
        return InteractionTrait.OBSERVABLE in self.traits
    
    def is_acknowledged(self) -> bool:
        """Check if this interaction requires acknowledgment."""
        return InteractionTrait.ACKNOWLEDGED in self.traits
    
    @property
    def category_name(self) -> str:
        """Return the name of the primary category."""
        return self.category.value
    
    @property
    def participant_count(self) -> int:
        """Return total number of participants including initiator."""
        return len(self.participants) + 1  # +1 for initiator
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert interaction to dictionary for serialization.
        
        Returns:
            Dictionary representation suitable for JSON serialization
        """
        return {
            "category": self.category.value,
            "interaction_id": self.interaction_id.value,
            "correlation_id": self.correlation_id,
            "causation_id": self.causation_id,
            "timestamp_utc": self.timestamp_utc,
            "initiator": self.initiator,
            "participants": list(self.participants),
            "direction": self.direction,
            "payload": dict(self.payload),
            "traits": [t.value for t in self.traits],
        }
    
    @classmethod
    def create(
        cls,
        category: InteractionCategory,
        initiator: str,
        participants: Optional[Tuple[str, ...]] = None,
        payload: Optional[Dict[str, Any]] = None,
        traits: Optional[FrozenSet[InteractionTrait]] = None,
        correlation_id: Optional[str] = None,
    ) -> "Interaction":
        """
        Create a new interaction with default values.
        
        Args:
            category: Primary semantic category
            initiator: Who triggered this interaction
            participants: Other components involved (default: empty tuple)
            payload: Data being transmitted (default: empty dict)
            traits: Optional behavioral traits
            correlation_id: Coordinator advancement context
            
        Returns:
            New Interaction instance with generated IDs and timestamps
        """
        now = time.monotonic()
        corr_id = correlation_id or uuid.uuid4().hex[:16]
        
        return cls(
            category=category,
            interaction_id=InteractionId.generate(),
            correlation_id=corr_id,
            timestamp_utc=now,
            initiator=initiator,
            participants=participants or (),
            payload=payload or {},
            traits=traits or frozenset(),
        )
    
    def with_participant(self, participant: str) -> "Interaction":
        """Create a new interaction with an additional participant."""
        return dataclass_replace(
            self,
            participants=self.participants + (participant,)
        )
    
    def with_trait(self, trait: InteractionTrait) -> "Interaction":
        """Create a new interaction with an additional trait."""
        return dataclass_replace(
            self,
            traits=self.traits | {trait}
        )


# =============================================================================
# CONCRETE INTERACTION TYPES
# =============================================================================

@dataclass(frozen=True, slots=True)
class Request(Interaction):
    """
    A Request interaction asks another participant to perform work.
    
    Semantic properties:
        - Does not imply success
        - Expects an outcome (Response)
        - May be acknowledged or unacknowledged
    
    Examples:
        >>> # Synchronous request expecting response
        >>> req = Request(
        ...     category=InteractionCategory.REQUEST,
        ...     interaction_id=InteractionId.generate(),
        ...     initiator="client",
        ...     participants=["server"],
        ...     payload={"action": "compute"},
        ... )
        ...
        >>> # One-way request (fire-and-forget)
        >>> fire_and_forget = Request(
        ...     category=InteractionCategory.REQUEST,
        ...     interaction_id=InteractionId.generate(),
        ...     initiator="monitor",
        ...     participants=["alerting"],
        ...     payload={"severity": "high"},
        ... )
    """
    
    # Category is fixed
    category: InteractionCategory = field(default=InteractionCategory.REQUEST, init=False)


@dataclass(frozen=True, slots=True)
class Response(Interaction):
    """
    A Response interaction answers a Request and completes its lifecycle.
    
    Semantic properties:
        - Contains outcome information (success/failure/partial)
        - Completes a Request's lifecycle
        - May include result payload
    
    Invariants:
        - RES-001: Responses correspond to Requests
        - RES-002: Response lifecycle depends on Request lifecycle
    """
    
    category: InteractionCategory = field(default=InteractionCategory.RESPONSE, init=False)
    
    # Response-specific fields
    success: bool = True
    result_type: str = "complete"  # complete, partial, error


@dataclass(frozen=True, slots=True)
class Command(Interaction):
    """
    A Command interaction expresses intent to perform an action.
    
    Semantic properties:
        - Authority is evaluated separately from the command itself
        - Execution is not guaranteed by sending a command
        - May be idempotent for safe retries
    
    Invariants:
        - CMD-001: Commands represent intent, not execution
        - CMD-002: Authority is separate from command semantics
    """
    
    category: InteractionCategory = field(default=InteractionCategory.COMMAND, init=False)
    
    # Command-specific fields
    is_idempotent: bool = False


@dataclass(frozen=True, slots=True)
class Event(Interaction):
    """
    An Event interaction describes something that already occurred.
    
    Semantic properties:
        - Immutable historical record
        - Describes facts about the past
        - Does not request work
    
    Invariants:
        - EVT-001: Events describe completed occurrences
        - EVT-002: Events are immutable records
        - EVT-003: Events do not request action from recipients
    """
    
    category: InteractionCategory = field(default=InteractionCategory.EVENT, init=False)
    
    # Event-specific fields
    event_time_utc: float = field(default_factory=time.monotonic)


@dataclass(frozen=True, slots=True)
class Signal(Interaction):
    """
    A Signal interaction communicates runtime state.
    
    Semantic properties:
        - May be transient or persistent
        - May be periodic or one-time
        - Communicates current or recent state
    
    Invariants:
        - SIG-001: Signals represent runtime state
        - SIG-002: Signals may be lost without impact (transient)
    """
    
    category: InteractionCategory = field(default=InteractionCategory.SIGNAL, init=False)
    
    # Signal-specific fields
    signal_type: str = "state_update"  # state_update, alert, threshold, etc.


@dataclass(frozen=True, slots=True)
class Notification(Interaction):
    """
    A Notification interaction informs participants without expecting work.
    
    Semantic properties:
        - Does not request work from recipients
        - Does not imply acknowledgment
        - One-way communication
    
    Invariants:
        - NOT-001: Notifications are one-way inform-only interactions
        - NOT-002: No work is expected from recipients
    """
    
    category: InteractionCategory = field(default=InteractionCategory.NOTIFICATION, init=False)
    
    # Notification-specific fields
    importance: str = "normal"  # low, normal, high, critical


@dataclass(frozen=True, slots=True)
class Proposal(Interaction):
    """
    A Proposal interaction recommends a possible action.
    
    Semantic properties:
        - Carries no authority
        - May be accepted or rejected by recipients
        - Suggests but does not command
    
    Invariants:
        - PRO-001: Proposals are recommendations, not commands
        - PRO-002: Recipients may accept or reject without consequence
    """
    
    category: InteractionCategory = field(default=InteractionCategory.PROPOSAL, init=False)
    
    # Proposal-specific fields
    recommendation: str = ""  # What is being recommended (empty for unspecified)


@dataclass(frozen=True, slots=True)
class Observation(Interaction):
    """
    An Observation interaction reports measured facts.
    
    Semantic properties:
        - Contains no decision or recommendation
        - Reports measured or computed values
        - Historical record of measurements
    
    Invariants:
        - OBS-001: Observations report measured facts only
        - OBS-002: Observations contain no recommendations
    """
    
    category: InteractionCategory = field(default=InteractionCategory.OBSERVATION, init=False)
    
    # Observation-specific fields
    measurement_value: float = 0.0
    unit: str = ""  # Measurement unit (e.g., "ms", "bytes", "percent")
    threshold: Optional[float] = None


@dataclass(frozen=True, slots=True)
class Query(Interaction):
    """
    A Query interaction requests information only without modifying state.
    
    Semantic properties:
        - Shall not modify system state
        - Requests read-only access to information
        - May return data or acknowledge absence of data
    
    Invariants:
        - QRY-001: Queries never modify state
        - QRY-002: Queries request information only
    """
    
    category: InteractionCategory = field(default=InteractionCategory.QUERY, init=False)
    
    # Query-specific fields
    query_type: str = ""  # e.g., "read", "lookup", "filter"
    result_expected: bool = True


@dataclass(frozen=True, slots=True)
class Publication(Interaction):
    """
    A Publication interaction makes information available with no designated recipient.
    
    Semantic properties:
        - Has no specific destination
        - Information is made broadly available
        - May have multiple subscribers
    
    Invariants:
        - PUB-001: Publications have no designated recipients
        - PUB-002: Subscribers receive publications by interest, not intent
    """
    
    category: InteractionCategory = field(default=InteractionCategory.PUBLICATION, init=False)
    
    # Publication-specific fields
    topic: str = ""  # Information category or subject area


@dataclass(frozen=True, slots=True)
class Subscription(Interaction):
    """
    A Subscription interaction expresses interest in future Publications.
    
    Semantic properties:
        - Expresses ongoing interest
        - May include filtering criteria
        - May have expiration
    
    Invariants:
        - SUB-001: Subscriptions express ongoing interest
        - SUB-002: Subscriptions may expire
    """
    
    category: InteractionCategory = field(default=InteractionCategory.SUBSCRIPTION, init=False)
    
    # Subscription-specific fields
    subscription_id: str = field(default_factory=lambda: f"sub_{uuid.uuid4().hex[:16]}")
    filter_criteria: Optional[Dict[str, Any]] = None
    expires_at_utc: Optional[float] = None


@dataclass(frozen=True, slots=True)
class Checkpoint(Interaction):
    """
    A Checkpoint interaction records a recoverable execution point.
    
    Semantic properties:
        - Records state at a moment in time
        - Enables restoration from failure
        - May include snapshot of relevant state
    
    Invariants:
        - CKP-001: Checkpoints enable recovery
        - CKP-002: Checkpoints record recoverable state
    """
    
    category: InteractionCategory = field(default=InteractionCategory.CHECKPOINT, init=False)
    
    # Checkpoint-specific fields
    checkpoint_id: str = field(default_factory=lambda: f"chk_{uuid.uuid4().hex[:16]}")
    revision: int = 0  # Version of the checkpoint


@dataclass(frozen=True, slots=True)
class Heartbeat(Interaction):
    """
    A Heartbeat interaction communicates liveness.
    
    Semantic properties:
        - Indicates participant is operational
        - May be periodic or event-driven
        - Typically low-overhead communication
    
    Invariants:
        - HBT-001: Heartbeats indicate liveness
        - HBT-002: Missing heartbeats may signal failure
    """
    
    category: InteractionCategory = field(default=InteractionCategory.HEARTBEAT, init=False)
    
    # Heartbeat-specific fields
    sequence_number: int = 0


@dataclass(frozen=True, slots=True)
class Synchronization(Interaction):
    """
    A Synchronization interaction coordinates multiple participants.
    
    Semantic properties:
        - Coordinates actions across participants
        - May involve consensus or agreement
        - Ensures consistent state or timing
    
    Invariants:
        - SYN-001: Synchronizations coordinate multiple participants
        - SYN-002: Synchronizations ensure consistency
    """
    
    category: InteractionCategory = field(default=InteractionCategory.SYNCHRONIZATION, init=False)
    
    # Synchronization-specific fields
    sync_type: str = ""  # e.g., "barrier", "consensus", "timing"
    participant_count: int = 0


@dataclass(frozen=True, slots=True)
class Transaction(Interaction):
    """
    A Transaction interaction groups multiple interactions into one atomic context.
    
    Semantic properties:
        - All interactions within succeed or fail together
        - Atomic semantics: all-or-nothing
        - May include commit or rollback
    
    Invariants:
        - TXN-001: Transactions are atomic contexts
        - TXN-002: All or nothing semantics
    """
    
    category: InteractionCategory = field(default=InteractionCategory.TRANSACTION, init=False)
    
    # Transaction-specific fields
    transaction_id: str = field(default_factory=lambda: f"txn_{uuid.uuid4().hex[:16]}")
    is_committed: bool = False


@dataclass(frozen=True, slots=True)
class Recovery(Interaction):
    """
    A Recovery interaction coordinates restoration after failure.
    
    Semantic properties:
        - Restores state after failure
        - May involve checkpoint replay
        - Coordinates recovery participants
    
    Invariants:
        - RCV-001: Recoveries restore state after failure
        - RCV-002: Recoveries coordinate restoration efforts
    """
    
    category: InteractionCategory = field(default=InteractionCategory.RECOVERY, init=False)
    
    # Recovery-specific fields
    recovery_id: str = field(default_factory=lambda: f"rcv_{uuid.uuid4().hex[:16]}")
    failure_reason: Optional[str] = None


# =============================================================================
# UTILITY FUNCTIONS
# =============================================================================

def dataclass_replace(obj: Any, **kwargs) -> Any:
    """Replace fields in a frozen dataclass."""
    import dataclasses
    if hasattr(obj, '__dataclass_fields__'):
        return dataclasses.replace(obj, **kwargs)
    raise TypeError(f"Cannot replace fields in {type(obj)}")


# =============================================================================
# CATEGORY RELATIONSHIPS
# =============================================================================

CATEGORY_RELATIONSHIPS: Dict[InteractionCategory, Tuple[str, ...]] = {
    # Exchange relationships
    InteractionCategory.REQUEST: ("Response",),  # Requests lead to Responses
    InteractionCategory.RESPONSE: ("Request",),  # Responses complete Requests
    
    # Action relationships
    InteractionCategory.COMMAND: (),  # Commands may produce Events
    InteractionCategory.EVENT: (),  # Events are historical
    
    # Communication relationships
    InteractionCategory.SIGNAL: (),  # Signals broadcast state
    InteractionCategory.NOTIFICATION: (),  # Notifications are one-way
    
    # Information relationships
    InteractionCategory.PROPOSAL: (),  # Proposals may lead to Commands
    InteractionCategory.OBSERVATION: (),  # Observations report facts
    InteractionCategory.QUERY: ("Observation",),  # Queries may receive Observations
    
    # Distribution relationships
    InteractionCategory.PUBLICATION: ("Subscription",),  # Publications have subscribers
    InteractionCategory.SUBSCRIPTION: ("Publication",),  # Subscriptions receive publications
    
    # Coordination relationships
    InteractionCategory.CHECKPOINT: (),  # Checkpoints enable Recovery
    InteractionCategory.HEARTBEAT: (),  # Heartbeats indicate liveness
    InteractionCategory.SYNCHRONIZATION: (),  # Synchronizations coordinate
    
    # Transactional relationships
    InteractionCategory.TRANSACTION: (),  # Transactions group other interactions
    InteractionCategory.RECOVERY: ("Checkpoint",),  # Recoveries may use Checkpoints
}


# =============================================================================
# TAXONOMY CONSTRAINTS
# =============================================================================

INCOMPATIBLE_PAIRS: Tuple[Tuple[InteractionCategory, ...], ...] = (
    # Request/Event pairs (mutually exclusive as primary category)
    (InteractionCategory.REQUEST, InteractionCategory.EVENT),
    
    # Response/Command pairs (different semantic intentions)
    (InteractionCategory.RESPONSE, InteractionCategory.COMMAND),
    
    # Proposal/Acceptance pairs
    (InteractionCategory.PROPOSAL, InteractionCategory.PROPOSAL),  # Cannot be same
    
    # Query/Transaction pairs (query is read-only, transaction may modify)
    (InteractionCategory.QUERY, InteractionCategory.TRANSACTION),
)


def are_categories_compatible(cat1: InteractionCategory, cat2: InteractionCategory) -> bool:
    """
    Check if two interaction categories can coexist in a relationship.
    
    Args:
        cat1: First interaction category
        cat2: Second interaction category
        
    Returns:
        True if compatible, False if incompatible pairs
        
    Note: This checks for semantic compatibility in relationships,
    not whether they can both exist in the system.
    """
    # Same category is always compatible (for grouping)
    if cat1 == cat2:
        return True
    
    # Check against incompatible pairs
    for pair in INCOMPATIBLE_PAIRS:
        if cat1 in pair and cat2 in pair:
            return False
    
    # Check relationship compatibility
    related = CATEGORY_RELATIONSHIPS.get(cat1, ())
    if cat2.name in [r.upper() for r in related]:
        return True
    
    return True  # Default to compatible if not explicitly incompatible


def is_primary_category_valid(category: InteractionCategory) -> bool:
    """
    Check if a category is a valid primary interaction category.
    
    Args:
        category: The category to validate
        
    Returns:
        True if valid, False otherwise
    """
    return category in InteractionCategory


# =============================================================================
# EXPORTS
# =============================================================================

__all__ = [
    # Primary categories (the taxonomy)
    "InteractionCategory",
    
    # Secondary traits
    "InteractionTrait",
    
    # Identity types
    "InteractionId",
    "InteractionCorrelation",
    
    # Base interaction type
    "Interaction",
    
    # Concrete types
    "Request",
    "Response",
    "Command",
    "Event",
    "Signal",
    "Notification",
    "Proposal",
    "Observation",
    "Query",
    "Publication",
    "Subscription",
    "Checkpoint",
    "Heartbeat",
    "Synchronization",
    "Transaction",
    "Recovery",
    
    # Utility functions
    "are_categories_compatible",
    "is_primary_category_valid",
    "CATEGORY_RELATIONSHIPS",
    "INCOMPATIBLE_PAIRS",
]