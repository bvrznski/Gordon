# Gordon Phase 3.26: Core Lifecycle Foundations
# ================================================
#
# Canonical Lifecycle Philosophy, Terminology, and Architecture Boundaries

"""
Canonical Lifecycle Architecture - Foundations Module

This module establishes the philosophical and terminological foundation for
the canonical lifecycle architecture that governs all architectural entities
within the Gordon runtime.

ARCHITECTURAL PRINCIPLES:
========================

1. ONE CANONICAL ARCHITECTURE
   No subsystem shall implement an independent lifecycle framework.
   Every architectural entity participates in one deterministic lifecycle.

2. LIFECYCLE IS NOT EXECUTION
   Lifecycle governs participation, not behavior.
   - Lifecycle: When entities are active, ready, suspended
   - Execution: What entities do when active

3. TRANSITIONS ARE EXPLICIT AND VALIDATED
   No implicit state changes.
   Every transition is requested, validated, and committed.

4. OWNERSHIP IS SEMANTICALLY DISTINCT
   - Construction creates the entity
   - Initialization prepares it
   - Admission validates it
   - Activation enables participation

LIFECYCLE STATE MACHINE:
======================

Every architectural entity follows this canonical state flow:

    DISCOVERED → REGISTERED → COMPOSED → CONSTRUCTED → INITIALIZED
        ↓                                              ↓
      [VALIDATED] ←───────────────────────────────────┘
        ↓
    ADMITTED → READY → ACTIVATED → OPERATIONAL
        ↓                              ↓
    [SUSPENDED] ←─────────────────────┘ (optional)
        ↓
    REPLACED (optional)
        ↓
    RETIRED → SHUTDOWN → DESTROYED

Terminal states (FAILED, TERMINATED) may be reached from any state.

OWNERSHIP MODEL:
==============

Every lifecycle participant has explicit ownership:

    LifecycleOwner       - Who governs the lifecycle?
    ConstructionOwner    - Who creates the entity?
    InitializationOwner  - Who prepares it for use?
    AdmissionOwner       - Who validates it for participation?
    ActivationOwner      - Who enables it to participate?
    SuspensionOwner      - Who may suspend/resume it?
    ReplacementOwner     - Who may replace it?
    ShutdownOwner        - Who terminates it?
    DestructionOwner     - Who cleans up resources?

LIFECYCLE INTEGRATION:
====================

The canonical lifecycle integrates with:

    Phase 3.12: Core Architecture
    Phase 3.15: State (lifecycle as state transitions)
    Phase 3.16: Time (lifecycle timestamps, durations)
    Phase 3.17: Resources & Compute (resource lifecycle)
    Phase 3.18: Configuration & Policy (policy-driven transitions)
    Phase 3.19: Identity (identity persists through transitions)
    Phase 3.20: Concurrency (synchronized state changes)
    Phase 3.21: Communication (lifecycle events as messages)
    Phase 3.22: Security (admission validation, security checks)
    Phase 3.23: Reflection (introspection of lifecycle state)
    Phase 3.24: Validation (validation at each transition)
    Phase 3.25: Recovery & Resilience (recovery-aware transitions)

ARCHITECTURAL CONSTRAINTS:
========================

Lifecycle shall never:

    - Own runtime state
    - Execute business logic
    - Replace dependency management
    - Replace scheduling
    - Replace execution
    - Replace recovery
    - Replace configuration

Lifecycle governs PARTICIPATION, not behavior.
"""

from dataclasses import dataclass, field
from typing import Dict, Optional, Tuple, Any, Callable, TypeVar
from enum import Enum, auto
import time
import uuid

T = TypeVar('T')


# =============================================================================
# LIFECYCLE STATE ENUMERATION
# =============================================================================


class LifecycleState(Enum):
    """
    Canonical lifecycle states for all architectural entities.
    
    TRANSITION RULES:
        - Each transition must be explicitly requested and validated
        - Transitions may have prerequisites (preconditions)
        - Some transitions are terminal (cannot leave after reaching them)
        - Recovery policies determine allowed recovery paths
    
    STATE FLOW:
        [DISCOVERED] → [REGISTERED] → [COMPOSED]
            ↓              ↓               ↓
        [FAILED]      [FAILED]       [CONSTRUCTED]
                                         ↓
                                    [INITIALIZED]
                                         ↓
                                    [VALIDATED]
                                         ↓
                                    [ADMITTED]
                                         ↓
                                    [READY]
                                         ↓
                                    [ACTIVATED]
                                         ↓
                                    [OPERATIONAL]
                                         ↓
                                    [SUSPENDED] (optional)
                                         ↓
                                    [REPLACED] (optional)
                                         ↓
                                    [RETIRED]
                                         ↓
                                    [SHUTDOWN]
                                         ↓
                                    [DESTROYED]
    
    TERMINAL STATES:
        - DESTROYED: Entity permanently removed
        - FAILED: Entity entered error state
    """
    
    # Discovery states
    DISCOVERED = "discovered"           # Entity detected, metadata known
    REGISTERED = "registered"          # Entity registered in registry
    
    # Composition states
    COMPOSED = "composed"              # Dependencies identified and composed
    
    # Construction states
    CONSTRUCTED = "constructed"        # Entity instance created
    
    # Initialization states
    INITIALIZED = "initialized"        # Dependencies injected, prepared
    VALIDATED = "validated"            # Pre-conditions validated
    
    # Admission states
    ADMITTED = "admitted"              # Passed admission criteria
    READY = "ready"                    # Ready to participate in runtime
    
    # Activation states
    ACTIVATED = "activated"            # Participating in runtime
    OPERATIONAL = "operational"        # Fully operational, performing work
    
    # Optional transitions (policy-controlled)
    SUSPENDED = "suspended"            # Temporarily suspended
    REPLACED = "replaced"              # Replaced by newer version
    
    # Shutdown states
    RETIRED = "retired"                # Retired from active service
    SHUTDOWN = "shutdown"              # Shutdown in progress
    DESTROYED = "destroyed"            # Permanently destroyed
    
    # Error states (terminal)
    FAILED = "failed"                  # Failed during any phase


# =============================================================================
# LIFECYCLE EVENT TYPES
# =============================================================================


class LifecycleEvent(Enum):
    """
    Canonical lifecycle events that may be emitted during transitions.
    
    EVENTS ARE OBSERVABLE:
        - Emitted when state changes occur
        - May trigger other system components
        - Recorded in transition history
    """
    
    # Discovery
    DISCOVERED = "discovered"          # Entity discovered by runtime
    REGISTERED = "registered"         # Entity registered
    
    # Composition
    COMPOSED = "composed"             # Dependencies composed
    DEPENDENCY_ADDED = "dependency_added"
    DEPENDENCY_REMOVED = "dependency_removed"
    
    # Construction
    CONSTRUCTING = "constructing"     # Start of construction
    CONSTRUCTED = "constructed"       # Construction complete
    
    # Initialization
    INITIALIZING = "initializing"     # Start of initialization
    INITIALIZED = "initialized"       # Initialization complete
    INITIALIZATION_FAILED = "initialization_failed"
    
    # Validation
    VALIDATING = "validating"         # Start of validation
    VALIDATED = "validated"           # Validation passed
    VALIDATION_FAILED = "validation_failed"
    
    # Admission
    ADMITTING = "admitting"           # Start of admission
    ADMITTED = "admitted"             # Admitted to runtime
    ADMISSION_FAILED = "admission_failed"
    
    # Activation
    ACTIVATING = "activating"         # Start of activation
    ACTIVATED = "activated"           # Activation complete
    ACTIVATION_FAILED = "activation_failed"
    
    # Suspension
    SUSPENDING = "suspending"         # Start of suspension
    SUSPENDED = "suspended"           # Suspended
    RESUMING = "resuming"             # Start of resumption
    RESUMED = "resumed"               # Resumed
    
    # Replacement
    REPLACING = "replacing"           # Start of replacement
    REPLACED = "replaced"             # Replaced
    REPLACEMENT_FAILED = "replacement_failed"
    
    # Retirement
    RETIRING = "retiring"             # Start of retirement
    RETIRED = "retired"               # Retired
    
    # Shutdown
    SHUTDOWN_REQUESTED = "shutdown_requested"
    SHUTTING_DOWN = "shutting_down"
    SHUTDOWN = "shutdown"             # Complete shutdown
    DESTROYING = "destroying"         # Start of destruction
    DESTROYED = "destroyed"           # Destruction complete
    
    # Errors
    FAILED = "failed"                 # Entity failed


# =============================================================================
# LIFECYCLE CONTEXT
# =============================================================================


@dataclass(frozen=True)
class LifecycleContext:
    """
    Immutable context for lifecycle operations.
    
    Context provides the environment in which lifecycle decisions are made.
    It includes timing, ownership, policy, and operational information.
    """
    
    # Identity
    entity_id: str                      # Which entity?
    entity_type: str                    # What type of entity?
    
    # Lifecycle state
    current_state: LifecycleState       # Current state before transition
    
    # Timestamps (UTC epoch seconds)
    created_at: float                   # When entity was created
    last_transition_at: Optional[float] = None  # Last state change
    transition_count: int = 0           # Total transitions so far
    
    # Ownership (with defaults for optional fields)
    lifecycle_owner_id: Optional[str] = None  # Who owns the lifecycle?
    construction_owner_id: Optional[str] = None   # Who constructed it?
    initialization_owner_id: Optional[str] = None  # Who initialized it?
    admission_owner_id: Optional[str] = None      # Who admitted it?
    activation_owner_id: Optional[str] = None     # Who activated it?
    
    # Operational context
    runtime_instance_id: Optional[str] = None  # Which runtime instance?
    scope: str = "global"               # Scope: global, user, session, etc.
    
    # Policy reference
    policy_name: Optional[str] = None   # Name of lifecycle policy to apply
    
    def with_state(self, new_state: LifecycleState) -> 'LifecycleContext':
        """Create new context with updated state."""
        return dataclass_replace(self, 
                                current_state=new_state,
                                last_transition_at=time.time(),
                                transition_count=self.transition_count + 1)
    
    @property
    def is_terminal(self) -> bool:
        """Check if entity is in a terminal state."""
        return self.current_state in {
            LifecycleState.DESTROYED,
            LifecycleState.FAILED,
        }
    
    @property
    def is_operational(self) -> bool:
        """Check if entity is operational (may be suspended)."""
        return self.current_state in {
            LifecycleState.OPERATIONAL,
            LifecycleState.SUSPENDED,
        }


# =============================================================================
# LIFECYCLE TRANSITION REQUEST
# =============================================================================


@dataclass(frozen=True)
class LifecycleTransitionRequest:
    """
    Request to perform a lifecycle state transition.
    
    Every transition must be:
        - Explicitly requested with full context
        - Validated against rules and policies
        - Authenticated by proper owner
        - Committed atomically
    
    TRANSITION FLOW:
        1. Request is created with from_state, to_state, and metadata
        2. Validation checks preconditions and policy compliance
        3. If valid, transition is committed
        4. Post-transition actions are triggered
    """
    
    # Identity
    entity_id: str                      # Target entity ID
    
    # State information
    from_state: LifecycleState          # Expected current state
    to_state: LifecycleState            # Requested target state
    
    # Validation context
    validation_context: Dict[str, Any] = field(default_factory=dict)
    
    # Ownership tracking (with defaults for optional fields)
    requested_by: Optional[str] = None  # Who requested the transition?
    authority_id: Optional[str] = None  # Who has authority?
    
    # Metadata
    reason: Optional[str] = None        # Why is this transition needed?
    timestamp: float = field(default_factory=time.time)  # Request time
    
    # Policy override (optional, for exceptional cases)
    policy_override: bool = False       # Bypass normal policy checks?
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert request to dictionary for serialization."""
        return {
            "entity_id": self.entity_id,
            "from_state": self.from_state.value,
            "to_state": self.to_state.value,
            "requested_by": self.requested_by,
            "reason": self.reason,
            "timestamp": self.timestamp,
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'LifecycleTransitionRequest':
        """Create request from dictionary."""
        return cls(
            entity_id=data.get("entity_id", ""),
            from_state=LifecycleState(data.get("from_state", "discovered")),
            to_state=LifecycleState(data.get("to_state", "registered")),
            requested_by=data.get("requested_by", ""),
            reason=data.get("reason"),
            timestamp=float(data.get("timestamp", 0)),
        )


# =============================================================================
# LIFECYCLE TRANSITION RESULT
# =============================================================================


@dataclass(frozen=True)
class LifecycleTransitionResult:
    """
    Result of a lifecycle transition request.
    
    Contains both success and failure information:
        - accepted/rejected status
        - new state (if accepted)
        - rejection reason (if rejected)
        - timestamp and metadata
    
    RESULTS ARE IMMUTABLE:
        - Once created, result cannot be changed
        - Results are recorded in history for audit
    """
    
    # Required fields
    entity_id: str
    transition_request: LifecycleTransitionRequest
    accepted: bool
    
    # State information
    previous_state: Optional[LifecycleState] = None  # Before transition
    current_state: Optional[LifecycleState] = None   # After transition
    
    # Validation results
    validation_passed: bool = True
    rejection_reasons: Tuple[str, ...] = field(default_factory=tuple)
    
    # Timing
    requested_at: float = field(default_factory=time.time)
    processed_at: float = field(default_factory=time.time)
    committed_at: Optional[float] = None  # When state actually changed
    
    # Metadata
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def with_committed_state(self, new_state: LifecycleState) -> 'LifecycleTransitionResult':
        """Create result with committed state updated."""
        return dataclass_replace(self,
                                current_state=new_state,
                                committed_at=time.time())
    
    @property
    def is_success(self) -> bool:
        """Check if transition was successful."""
        return self.accepted and self.validation_passed
    
    @property
    def is_failure(self) -> bool:
        """Check if transition failed."""
        return not self.accepted or not self.validation_passed


# =============================================================================
# LIFECYCLE SNAPSHOT
# =============================================================================


@dataclass(frozen=True)
class LifecycleSnapshot:
    """
    Immutable snapshot of an entity's lifecycle state at a point in time.
    
    Used for:
        - Persistence and recovery
        - Read-only inspection without locking
        - Historical analysis
    
    Contains only bounded metadata, no live objects or locks.
    """
    
    # Identity
    entity_id: str
    entity_type: str
    
    # Current state
    lifecycle_state: LifecycleState
    lifecycle_version: int              # For optimistic concurrency
    
    # Timestamps (UTC epoch)
    created_at: float
    last_transition_at: Optional[float]
    transition_count: int
    
    # Ownership
    lifecycle_owner_id: str
    construction_owner_id: Optional[str]
    initialization_owner_id: Optional[str]
    admission_owner_id: Optional[str]
    activation_owner_id: Optional[str]
    
    # Runtime context
    runtime_instance_id: str
    scope: str
    
    # Additional information
    policy_name: Optional[str] = None
    dependencies: Tuple[str, ...] = field(default_factory=tuple)
    status_message: Optional[str] = None
    
    @classmethod
    def from_context(cls, ctx: LifecycleContext) -> 'LifecycleSnapshot':
        """Create snapshot from lifecycle context."""
        return cls(
            entity_id=ctx.entity_id,
            entity_type=ctx.entity_type,
            lifecycle_state=ctx.current_state,
            lifecycle_version=1,  # Will be updated by owner
            created_at=ctx.created_at,
            last_transition_at=ctx.last_transition_at,
            transition_count=ctx.transition_count,
            lifecycle_owner_id=ctx.lifecycle_owner_id,
            construction_owner_id=ctx.construction_owner_id,
            initialization_owner_id=ctx.initialization_owner_id,
            admission_owner_id=ctx.admission_owner_id,
            activation_owner_id=ctx.activation_owner_id,
            runtime_instance_id=ctx.runtime_instance_id,
            scope=ctx.scope,
        )


# =============================================================================
# LIFECYCLE HISTORY
# =============================================================================


@dataclass(frozen=True)
class LifecycleHistoryEntry:
    """
    Single entry in the lifecycle transition history.
    
    History is append-only and immutable. Each entry represents one state change.
    """
    
    # Identity
    entity_id: str
    entity_type: str
    
    # Transition details
    sequence_number: int                # Order in history
    from_state: LifecycleState
    to_state: LifecycleState
    
    # Timing
    requested_at: float
    committed_at: float
    
    # Request details
    requested_by: str
    reason: Optional[str]
    
    # Validation and authority
    validation_passed: bool
    authority_id: Optional[str]
    
    def is_failure(self) -> bool:
        """Check if this transition resulted in failure state."""
        return self.to_state == LifecycleState.FAILED


@dataclass(frozen=True)
class LifecycleHistory:
    """
    Immutable history of all lifecycle transitions for an entity.
    
    History provides:
        - Full provenance of state changes
        - Audit trail for compliance
        - Debugging information
    
    Operations on history are non-mutating (return new histories).
    """
    
    entity_id: str
    entity_type: str
    
    # Ordered sequence of entries (oldest first)
    entries: Tuple[LifecycleHistoryEntry, ...]
    
    @property
    def current_state(self) -> LifecycleState:
        """Get the current state from the last entry."""
        if not self.entries:
            return LifecycleState.DISCOVERED  # Default initial state
        return self.entries[-1].to_state
    
    @property
    def first_entry(self) -> Optional[LifecycleHistoryEntry]:
        """Get the first history entry."""
        return self.entries[0] if self.entries else None
    
    @property
    def last_entry(self) -> Optional[LifecycleHistoryEntry]:
        """Get the most recent history entry."""
        return self.entries[-1] if self.entries else None
    
    def with_entry_added(self, entry: LifecycleHistoryEntry) -> 'LifecycleHistory':
        """Add a new entry to history (returns new instance)."""
        return dataclass_replace(
            self,
            entries=self.entries + (entry,)
        )
    
    @classmethod
    def empty(cls, entity_id: str, entity_type: str) -> 'LifecycleHistory':
        """Create empty history for new entity."""
        return cls(entity_id=entity_id, entity_type=entity_type, entries=())


# =============================================================================
# UTILITY FUNCTIONS
# =============================================================================


def dataclass_replace(obj: Any, **kwargs) -> Any:
    """
    Replace fields in a frozen dataclass.
    
    Creates a new instance with specified fields updated.
    Works with both standard and attrs-style dataclasses.
    """
    if hasattr(obj, "__dataclass_fields__"):
        # Standard library dataclass
        field_dict = {f.name: getattr(obj, f.name) 
                     for f in obj.__dataclass_fields__.values()}
        field_dict.update(kwargs)
        return type(obj)(**field_dict)
    
    # Try __dict__ replacement for other classes
    if hasattr(obj, "__dict__"):
        new_obj = object.__new__(type(obj))
        new_dict = dict(obj.__dict__)
        new_dict.update(kwargs)
        new_obj.__dict__.update(new_dict)
        return new_obj
    
    raise TypeError(f"Cannot replace fields in {type(obj)}")


def validate_transition(from_state: LifecycleState, 
                        to_state: LifecycleState,
                        policy_name: Optional[str] = None) -> Tuple[bool, Optional[str]]:
    """
    Validate if a state transition is allowed.
    
    Returns:
        (is_valid, reason) tuple
    """
    # Cannot transition from terminal states
    if from_state == LifecycleState.DESTROYED:
        return False, "Cannot transition from DESTROYED"
    
    if from_state == LifecycleState.FAILED:
        # Failed state may only recover to certain states (policy-dependent)
        # For now, allow recovery paths but log warning
        pass
    
    # No self-transitions allowed (except FAILED for error updates)
    if from_state == to_state and to_state != LifecycleState.FAILED:
        return False, "Self-transition not allowed"
    
    return True, None


# =============================================================================
# EXPORTS
# =============================================================================

__all__ = [
    # State enumeration
    "LifecycleState",
    
    # Event types
    "LifecycleEvent",
    
    # Context and data structures
    "LifecycleContext",
    "LifecycleTransitionRequest",
    "LifecycleTransitionResult",
    "LifecycleSnapshot",
    "LifecycleHistory",
    "LifecycleHistoryEntry",
    
    # Utility functions
    "dataclass_replace",
    "validate_transition",
]