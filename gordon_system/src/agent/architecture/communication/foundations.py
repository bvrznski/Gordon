# Gordon Core - Communication Foundations (Phase 3.21.1)
# =======================================================
#
# Canonical Communication Philosophy, Terminology, and Architectural Boundaries
#
# This module establishes the immutable principles governing all communication
# within the Gordon Core architecture.
#
# COMMUNICATION IS INFRASTRUCTURE:
# - Communication transports immutable artifacts only
# - Communication never owns runtime state
# - Communication never performs business logic
# - Communication coordinates without replacing responsibilities

"""
Canonical Communication Foundations for Gordon Phase 3.21.1

This module establishes the immutable principles governing all communication
within the Gordon Core architecture.

PHILOSOPHICAL PRINCIPLES:
-------------------------
1. Explicit over Implicit
   - All communication contracts are explicit and typed
   - No hidden callbacks or undocumented side effects
   
2. Typed over Untyped
   - Every message has a precise type
   - Schema validation is mandatory
   
3. Deterministic over Probabilistic
   - Routing is deterministic based on policy
   - Delivery semantics are explicitly declared
   
4. Observable over Opaque
   - All communication is traceable
   - Diagnostic metadata is mandatory
   
5. Immutable over Mutable
   - Messages are immutable after publication
   - No shared mutable state in messages

ARCHITECTURAL INTEGRITY:
------------------------
- Communication is orthogonal to ownership
- Communication is orthogonal to execution
- Communication is orthogonal to persistence
- Communication is orthogonal to scheduling

Every architectural entity communicates through this canonical architecture.
No subsystem implements its own messaging framework.
"""

from dataclasses import dataclass, field
from typing import Dict, Any, Optional, Tuple, FrozenSet
from enum import Enum, auto
import time
import uuid


# =============================================================================
# COMMUNICATION PHILOSOPHY PRINCIPLES
# =============================================================================

class CommunicationPrinciple(Enum):
    """
    Canonical communication architectural principles.
    
    Every communication artifact shall adhere to these principles:
        - EXPLICIT: Contracts are typed and documented
        - VALIDATABLE: Messages can be validated before delivery
        - OBSERVABLE: Communication is traceable throughout lifecycle
        - DETERMINISTIC: Routing follows explicit policies
        - IMMUTABLE: Messages cannot be modified after publication
    """
    
    EXPLICIT = "explicit"           # Contracts are typed and documented
    VALIDATABLE = "validatable"     # Messages can be validated before delivery
    OBSERVABLE = "observable"       # Communication is traceable throughout lifecycle
    DETERMINISTIC = "deterministic" # Routing follows explicit policies
    IMMUTABLE = "immutable"         # Messages cannot be modified after publication


# =============================================================================
# OWNERSHIP MODEL
# =============================================================================

class CommunicationOwnership(Enum):
    """
    Canonical ownership model for communication artifacts.
    
    Every communication artifact shall possess exactly one owner:
        - SENDER: The entity that created and published the message
        - RECEIVER: The entity that receives the message (for point-to-point)
        - NO_OWNER: For broadcast/multicast where no single owner exists
    
    Invariants:
        - OWN-001: Every communication has exactly one owner at any time
        - OWN-002: Ownership is preserved throughout lifecycle
        - OWN-003: Ownership transfer requires explicit acknowledgment
    """
    
    SENDER = "sender"               # Original publisher/creator
    RECEIVER = "receiver"           # Intended recipient (point-to-point)
    NO_OWNER = "no_owner"           # Broadcast/multicast scenarios


@dataclass(frozen=True)
class CommunicationOwnershipRecord:
    """
    Immutable record of communication ownership.
    
    Args:
        owner_id: Unique identifier of the current owner
        owner_type: Category of the owner (runtime, component, service, etc.)
        transfer_history: List of previous owners in chronological order
    """
    
    owner_id: str
    owner_type: str  # runtime, component, service, capability, module
    transfer_history: Tuple[str, ...] = field(default_factory=tuple)
    
    def with_transfer(self, new_owner_id: str, new_owner_type: str) -> "CommunicationOwnershipRecord":
        """Create a new ownership record with transferred ownership."""
        return CommunicationOwnershipRecord(
            owner_id=new_owner_id,
            owner_type=new_owner_type,
            transfer_history=self.transfer_history + (f"{self.owner_id}->{new_owner_id}",),
        )


# =============================================================================
# LIFECYCLE MODEL
# =============================================================================

class MessageLifecyclePhase(Enum):
    """
    Canonical message lifecycle phases.
    
    Lifecycle transitions are deterministic and validated:
        CREATED -> VALIDATED -> ROUTED -> DELIVERED -> ACKNOWLEDGED -> ARCHIVED
    
    Terminal states (cannot transition further):
        - COMPLETED: Successfully delivered and acknowledged
        - EXPIRED: Message lifetime exceeded
        - DROPPED: Message dropped due to policy violations
        - DEAD_LETTER: Message moved to dead-letter queue
    """
    
    CREATED = "created"             # Message created but not yet validated
    VALIDATED = "validated"         # Validation passed, ready for routing
    ROUTED = "routed"               # Routed to recipient(s)
    DELIVERED = "delivered"         # Delivered to recipient(s)
    ACKNOWLEDGED = "acknowledged"   # Received and acknowledged by recipient
    
    # Terminal states
    COMPLETED = "completed"         # Successfully completed lifecycle
    EXPIRED = "expired"             # Lifetime exceeded
    DROPPED = "dropped"             # Dropped due to policy violations
    DEAD_LETTER = "dead_letter"     # Moved to dead-letter queue


# =============================================================================
# COMMUNICATION BOUNDARIES
# =============================================================================

class CommunicationBoundary(Enum):
    """
    Canonical communication boundaries.
    
    These define the scope within which communication is valid:
        - RUNTIME: Within a single runtime instance
        - COMPONENT: Between components in same runtime
        - SERVICE: Between services in same cluster
        - NODE: Between nodes in distributed system
        - GLOBAL: System-wide (may span multiple runtimes)
    
    Invariants:
        - BND-001: Boundary defines maximum scope of communication
        - BND-002: Cross-boundary communication requires explicit handling
        - BND-003: Boundary is preserved throughout message lifetime
    """
    
    RUNTIME = "runtime"             # Within a single runtime instance
    COMPONENT = "component"         # Between components in same runtime
    SERVICE = "service"             # Between services in same cluster
    NODE = "node"                   # Between nodes in distributed system
    GLOBAL = "global"               # System-wide (may span multiple runtimes)


@dataclass(frozen=True)
class CommunicationBoundaryRecord:
    """
    Immutable record of communication boundary context.
    
    Args:
        boundary: The boundary within which this communication is valid
        source_runtime_id: Runtime where message originated
        target_runtime_ids: Target runtimes (empty = same as source)
        cluster_id: Optional cluster identifier for cross-runtime messaging
    """
    
    boundary: CommunicationBoundary
    source_runtime_id: str
    target_runtime_ids: Tuple[str, ...] = field(default_factory=tuple)
    cluster_id: Optional[str] = None


# =============================================================================
# COMMUNICATION RESPONSIBILITIES
# =============================================================================

@dataclass(frozen=True)
class CommunicationResponsibilities:
    """
    Canonical responsibilities for communication artifacts.
    
    Every communication shall define its responsibilities:
        - VALIDATION: Who validates the message?
        - ROUTING: How is routing determined?
        - DELIVERY: How is delivery guaranteed?
        - ACKNOWLEDGMENT: What acknowledgment is required?
        - OBSERVABILITY: What diagnostics are required?
    """
    
    validation_policy: str  # "strict", "relaxed", "disabled"
    routing_strategy: str   # "direct", "broadcast", "multicast", "anycast"
    delivery_mode: str      # "at-most-once", "at-least-once", "exactly-once"
    acknowledgment_mode: str  # "none", "receiver", "sender", "both"
    observability_level: str  # "minimal", "standard", "full"


# =============================================================================
# COMMUNICATION INTEGRITY GUARANTEES
# =============================================================================

@dataclass(frozen=True)
class IntegrityGuarantees:
    """
    Canonical integrity guarantees for communication.
    
    Each guarantee shall be explicitly declared:
        - SEQUENCE: Messages maintain order within a stream
        - DUPLICATE_DETECTION: Duplicates are detected and handled
        - REPLAY_PROTECTION: Replay attacks are prevented
        - AUTHENTICATION: Sender is authenticated
        - AUTHORIZATION: Sender has authority to send
    """
    
    sequence_integrity: bool = True     # Order preservation
    duplicate_detection: bool = True    # Duplicate detection enabled
    replay_protection: bool = True      # Replay protection enabled
    authentication_required: bool = False  # Sender authentication required
    authorization_required: bool = False   # Authorization check required


# =============================================================================
# TERMINAL STATES CHECKER
# =============================================================================

def is_terminal_lifecycle_state(phase: MessageLifecyclePhase) -> bool:
    """Check if the lifecycle phase is terminal (cannot transition further)."""
    return phase in (
        MessageLifecyclePhase.COMPLETED,
        MessageLifecyclePhase.EXPIRED,
        MessageLifecyclePhase.DROPPED,
        MessageLifecyclePhase.DEAD_LETTER,
    )


def is_valid_lifecycle_transition(current: MessageLifecyclePhase, next: MessageLifecyclePhase) -> bool:
    """
    Check if a lifecycle transition is valid.
    
    Valid transitions:
        CREATED -> VALIDATED
        VALIDATED -> ROUTED
        ROUTED -> DELIVERED
        DELIVERED -> ACKNOWLEDGED
        ACKNOWLEDGED -> COMPLETED
        
        Any state -> EXPIRED (timeout)
        Any state -> DROPPED (policy violation)
        Any state -> DEAD_LETTER (delivery failed repeatedly)
    """
    valid_transitions = {
        MessageLifecyclePhase.CREATED: {MessageLifecyclePhase.VALIDATED},
        MessageLifecyclePhase.VALIDATED: {MessageLifecyclePhase.ROUTED},
        MessageLifecyclePhase.ROUTED: {MessageLifecyclePhase.DELIVERED},
        MessageLifecyclePhase.DELIVERED: {MessageLifecyclePhase.ACKNOWLEDGED},
        MessageLifecyclePhase.ACKNOWLEDGED: {MessageLifecyclePhase.COMPLETED},
    }
    
    # Check for explicit transition
    if next in valid_transitions.get(current, set()):
        return True
    
    # Check for terminal transitions (any state can go to terminal)
    if is_terminal_lifecycle_state(next):
        return True
    
    return False


# =============================================================================
# CANONICAL COMMUNICATION MODEL (Phase 3.21 Foundation)
# =============================================================================

@dataclass(frozen=True, slots=True)
class CanonicalCommunicationMetadata:
    """
    Immutable metadata for canonical communication artifacts.
    
    This is the single source of truth for all communication context.
    
    Required fields for every communication:
        - message_id: Unique identifier for this message instance
        - correlation_id: Links related messages (request-response chains)
        - timestamp_utc: When this was created (UTC wall time)
        - lifecycle_phase: Current phase in lifecycle
        
    Optional but recommended:
        - provenance: Where this message came from (system, component, user)
        - ownership: Who owns this communication artifact
        - boundary: What scope this communication is valid within
        - guarantees: What integrity guarantees apply
    """
    
    # Identity and correlation
    message_id: str
    correlation_id: str
    
    # Timestamps (UTC monotonic time for consistency)
    timestamp_utc: float = field(default_factory=time.time)
    monotonic_time: float = field(default_factory=time.monotonic)
    
    # Lifecycle tracking
    lifecycle_phase: MessageLifecyclePhase = MessageLifecyclePhase.CREATED
    
    # Ownership and boundaries
    ownership_record: Optional[CommunicationOwnershipRecord] = None
    boundary_record: Optional[CommunicationBoundaryRecord] = None
    responsibilities: Optional[CommunicationResponsibilities] = None
    
    # Integrity guarantees
    integrity_guarantees: IntegrityGuarantees = field(default_factory=IntegrityGuarantees)
    
    # Provenance
    source_runtime_id: str = ""
    originating_thread_id: Optional[str] = None
    
    # Payload metadata (for validation and tracing)
    payload_type: Optional[str] = None
    payload_size_bytes: int = 0
    
    def with_lifecycle_phase(self, new_phase: MessageLifecyclePhase) -> "CanonicalCommunicationMetadata":
        """Create a new metadata instance with updated lifecycle phase."""
        if not is_valid_lifecycle_transition(self.lifecycle_phase, new_phase):
            raise ValueError(
                f"Invalid lifecycle transition from {self.lifecycle_phase} to {new_phase}"
            )
        
        return CanonicalCommunicationMetadata(
            message_id=self.message_id,
            correlation_id=self.correlation_id,
            timestamp_utc=self.timestamp_utc,
            monotonic_time=self.monotonic_time,
            lifecycle_phase=new_phase,
            ownership_record=self.ownership_record,
            boundary_record=self.boundary_record,
            responsibilities=self.responsibilities,
            integrity_guarantees=self.integrity_guarantees,
            source_runtime_id=self.source_runtime_id,
            originating_thread_id=self.originating_thread_id,
            payload_type=self.payload_type,
            payload_size_bytes=self.payload_size_bytes,
        )
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert metadata to dictionary for serialization."""
        return {
            "message_id": self.message_id,
            "correlation_id": self.correlation_id,
            "timestamp_utc": self.timestamp_utc,
            "lifecycle_phase": self.lifecycle_phase.value,
            "source_runtime_id": self.source_runtime_id,
        }


# =============================================================================
# PUBLIC API
# =============================================================================

__all__ = [
    # Philosophical principles
    "CommunicationPrinciple",
    
    # Ownership model
    "CommunicationOwnership",
    "CommunicationOwnershipRecord",
    
    # Lifecycle model
    "MessageLifecyclePhase",
    "is_terminal_lifecycle_state",
    "is_valid_lifecycle_transition",
    
    # Boundary model
    "CommunicationBoundary",
    "CommunicationBoundaryRecord",
    
    # Responsibilities
    "CommunicationResponsibilities",
    
    # Integrity guarantees
    "IntegrityGuarantees",
    
    # Canonical communication metadata (foundation)
    "CanonicalCommunicationMetadata",
]