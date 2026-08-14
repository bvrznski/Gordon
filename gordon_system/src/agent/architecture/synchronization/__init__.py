# Synchronization Architecture (Phase 3.14.12)
# ==============================================
#
# Synchronization establishes when architectural participants may progress.
#
# Canonical Model:
#     Execution → Synchronization → Coordination → Participants → Execution Continuation
#
# Synchronization PRINCIPLES:
# - Synchronization never performs computation
# - Synchronization never owns state
# - Synchronization determines readiness for progression
# - Synchronization preserves determinism

"""
Canonical Synchronization Architecture for Gordon Phase 3.14.12.

This module establishes the immutable contracts ensuring deterministic cooperation
between Execution, Streams Networks, Capabilities, Systems, and future
architectural domains through Synchronization primitives.
"""

from dataclasses import dataclass, field
from typing import Protocol, Any, Optional, List, Set, Tuple, Dict
from enum import Enum, auto
import uuid
import time


# =============================================================================
# SYNCHRONIZATION IDENTITY
# =============================================================================

@dataclass(frozen=True)
class SyncId:
    """Unique identifier for a synchronization primitive instance."""
    
    value: str
    
    @classmethod
    def generate(cls) -> "SyncId":
        """Generate a new unique synchronization ID."""
        return cls(value=f"sync_{uuid.uuid4().hex[:16]}")
    
    def __str__(self) -> str:
        return self.value


@dataclass(frozen=True)
class SyncEventId:
    """Unique identifier for a synchronization event."""
    
    value: str
    
    @classmethod
    def generate(cls) -> "SyncEventId":
        """Generate a new unique synchronization event ID."""
        return cls(value=f"sync_event_{uuid.uuid4().hex[:16]}")
    
    def __str__(self) -> str:
        return self.value


# =============================================================================
# SYNCHRONIZATION STATES
# =============================================================================

class SyncState(Enum):
    """
    Synchronization primitive states.
    
    Every synchronization primitive transitions through these states:
        PENDING → (waiting for conditions)
        READY → (conditions satisfied, may proceed)
        COMPLETED → (progression achieved)
        FAILED → (condition check failed or timeout)
        CANCELLED → (explicitly cancelled)
    """
    
    PENDING = "pending"      # Waiting for conditions
    READY = "ready"         # Conditions satisfied, ready to proceed
    COMPLETED = "completed" # Progression achieved
    FAILED = "failed"       # Condition check failed or timed out
    CANCELLED = "cancelled" # Explicitly cancelled


class SyncMode(Enum):
    """Synchronization execution modes."""
    
    BARRIER = "barrier"           # All must arrive before any proceed
    GATE = "gate"                 # One gate controls access for others
    LATCH = "latch"               # Count-based, opens after count reached
    CHECKPOINT = "checkpoint"     # Records and verifies execution point
    TOKEN = "token"               # Token-passing coordination
    PERMIT = "permit"             # Permit-based admission control
    RENDEZVOUS = "rendezvous"     # Two-party handoff synchronization
    COMPLETION_GROUP = "completion_group"  # Group completion tracking
    SEQUENCE_POINT = "sequence_point"      # Ordering enforcement point


# =============================================================================
# SYNCHRONIZATION PRIMITIVE PROTOCOLS
# =============================================================================

class SyncPrimitive(Protocol):
    """Base protocol for all synchronization primitives."""
    
    @property
    def sync_id(self) -> SyncId:
        """Unique identifier for this primitive."""
        ...
    
    @property
    def state(self) -> SyncState:
        """Current state of the primitive."""
        ...
    
    @property
    def timestamp_utc(self) -> float:
        """When this primitive was created (UTC monotonic)."""
        ...
    
    async def wait(self, timeout_seconds: Optional[float] = None) -> bool:
        """
        Wait for synchronization condition to be satisfied.
        
        Args:
            timeout_seconds: Maximum time to wait (None = wait forever)
            
        Returns:
            True if conditions satisfied, False if timed out or cancelled
        """
        ...
    
    async def signal(self) -> None:
        """Signal that this participant is ready."""
        ...
    
    async def release(self) -> None:
        """Release waiting participants."""
        ...
    
    async def cancel(self) -> None:
        """Cancel this synchronization."""
        ...


class BarrierSync(Protocol):
    """
    Barrier synchronization primitive.
    
    All participating participants must reach the barrier before any may proceed.
    """
    
    @property
    def participant_count(self) -> int:
        """Total number of expected participants."""
        ...
    
    @property
    def arrived_count(self) -> int:
        """Number of participants that have reached barrier."""
        ...
    
    async def arrive(self, participant_id: str) -> bool:
        """
        Record arrival of a participant at the barrier.
        
        Returns True if all participants have arrived and this one may proceed.
        """
        ...


class GateSync(Protocol):
    """
    Gate synchronization primitive.
    
    Controls access for multiple participants through a single gate.
    """
    
    @property
    def is_open(self) -> bool:
        """Check if the gate is currently open."""
        ...
    
    async def open_gate(self) -> None:
        """Open the gate, allowing all waiting participants to proceed."""
        ...
    
    async def close_gate(self) -> None:
        """Close the gate, blocking new access until reopened."""
        ...


class LatchSync(Protocol):
    """
    Latch synchronization primitive.
    
    Count-based synchronization that opens after a count threshold is reached.
    """
    
    @property
    def threshold(self) -> int:
        """Count threshold to open latch."""
        ...
    
    @property
    def current_count(self) -> int:
        """Current count of arrivals."""
        ...
    
    async def count_down(self) -> bool:
        """
        Decrement counter and return True if latch opens.
        
        Returns True when threshold is reached (latch opens).
        """
        ...


class RendezvousSync(Protocol):
    """
    Two-party rendezvous synchronization primitive.
    
    Allows two participants to synchronize and exchange information.
    """
    
    async def await_arrival(self, participant_id: str) -> Optional[str]:
        """
        Wait for a second participant to arrive at the rendezvous point.
        
        Returns the other participant's ID if successful, None if cancelled.
        """
        ...


class CompletionGroupSync(Protocol):
    """
    Completion group synchronization primitive.
    
    Tracks completion of multiple concurrent operations.
    """
    
    @property
    def expected_count(self) -> int:
        """Total number of completions expected."""
        ...
    
    @property
    def completed_count(self) -> int:
        """Number of operations that have completed."""
        ...
    
    async def record_completion(self, operation_id: str) -> bool:
        """
        Record completion of an operation.
        
        Returns True if all operations are now complete.
        """
        ...


class CheckpointSync(Protocol):
    """
    Checkpoint synchronization primitive.
    
    Records and verifies execution points for determinism.
    """
    
    async def record_state(self, state_data: Dict[str, Any]) -> str:
        """Record current state at checkpoint. Returns checkpoint ID."""
        ...
    
    async def verify_state(self, expected_checkpoint_id: str) -> bool:
        """Verify that current state matches recorded checkpoint."""
        ...


# =============================================================================
# SYNCHRONIZATION EVENT
# =============================================================================

@dataclass(frozen=True)
class SyncEvent:
    """
    Event emitted during synchronization progression.
    
    Every synchronization action generates events for observability.
    """
    
    event_id: SyncEventId
    sync_id: SyncId
    timestamp_utc: float
    event_type: str  # "ARRIVED", "RELEASED", "COMPLETED", "FAILED", etc.
    participant_id: Optional[str] = None
    details: Dict[str, Any] = field(default_factory=dict)
    
    @property
    def is_replayable(self) -> bool:
        """Events are replayable if they contain deterministic data."""
        return True


# =============================================================================
# SYNCHRONIZATION CONTRACT
# =============================================================================

class SyncContract(Protocol):
    """
    Protocol for synchronization contracts that participants must satisfy.
    
    Every participant in a synchronization must fulfill its contract.
    """
    
    @property
    def participant_id(self) -> str:
        """Unique identifier for this participant."""
        ...
    
    async def is_ready(self) -> bool:
        """Check if this participant is ready to proceed."""
        ...
    
    async def declare_readiness(self) -> None:
        """Explicitly declare this participant as ready."""
        ...


# =============================================================================
# SYNCHRONIZATION PRIMITIVE FACTORY
# =============================================================================

class SyncPrimitiveFactory:
    """
    Factory for creating synchronization primitives.
    
    This factory ensures consistent primitive creation and proper ID generation.
    """
    
    def __init__(self):
        self._primitives: Dict[SyncId, SyncPrimitive] = {}
    
    def create_barrier(
        self,
        participant_count: int,
        timeout_seconds: Optional[float] = None
    ) -> "BarrierSynchronization":
        """Create a barrier synchronization primitive."""
        sync_id = SyncId.generate()
        primitive = BarrierSynchronization(
            sync_id=sync_id,
            participant_count=participant_count,
            timeout_seconds=timeout_seconds
        )
        self._primitives[sync_id] = primitive
        return primitive
    
    def create_gate(
        self,
        initial_state: bool = False,
        timeout_seconds: Optional[float] = None
    ) -> "GateSynchronization":
        """Create a gate synchronization primitive."""
        sync_id = SyncId.generate()
        primitive = GateSynchronization(
            sync_id=sync_id,
            initial_state=initial_state,
            timeout_seconds=timeout_seconds
        )
        self._primitives[sync_id] = primitive
        return primitive
    
    def create_latch(
        self,
        threshold: int,
        timeout_seconds: Optional[float] = None
    ) -> "LatchSynchronization":
        """Create a latch synchronization primitive."""
        sync_id = SyncId.generate()
        primitive = LatchSynchronization(
            sync_id=sync_id,
            threshold=threshold,
            timeout_seconds=timeout_seconds
        )
        self._primitives[sync_id] = primitive
        return primitive
    
    def create_rendezvous(
        self,
        timeout_seconds: Optional[float] = None
    ) -> "RendezvousSynchronization":
        """Create a rendezvous synchronization primitive."""
        sync_id = SyncId.generate()
        primitive = RendezvousSynchronization(
            sync_id=sync_id,
            timeout_seconds=timeout_seconds
        )
        self._primitives[sync_id] = primitive
        return primitive
    
    def create_completion_group(
        self,
        expected_count: int,
        timeout_seconds: Optional[float] = None
    ) -> "CompletionGroupSynchronization":
        """Create a completion group synchronization primitive."""
        sync_id = SyncId.generate()
        primitive = CompletionGroupSynchronization(
            sync_id=sync_id,
            expected_count=expected_count,
            timeout_seconds=timeout_seconds
        )
        self._primitives[sync_id] = primitive
        return primitive
    
    def create_checkpoint(self) -> "CheckpointSynchronization":
        """Create a checkpoint synchronization primitive."""
        sync_id = SyncId.generate()
        primitive = CheckpointSynchronization(sync_id=sync_id)
        self._primitives[sync_id] = primitive
        return primitive


# =============================================================================
# CONCRETE SYNCHRONIZATION PRIMITIVES
# =============================================================================

class BarrierSynchronization:
    """
    Barrier synchronization implementation.
    
    All participants must arrive at the barrier before any may proceed.
    """
    
    def __init__(
        self,
        sync_id: SyncId,
        participant_count: int,
        timeout_seconds: Optional[float] = None
    ):
        self._sync_id = sync_id
        self._participant_count = participant_count
        self._timeout_seconds = timeout_seconds
        self._arrived: Set[str] = set()
        self._state = SyncState.PENDING
        self._timestamp_utc = time.monotonic()
    
    @property
    def sync_id(self) -> SyncId:
        return self._sync_id
    
    @property
    def state(self) -> SyncState:
        return self._state
    
    @property
    def timestamp_utc(self) -> float:
        return self._timestamp_utc
    
    @property
    def participant_count(self) -> int:
        return self._participant_count
    
    @property
    def arrived_count(self) -> int:
        return len(self._arrived)
    
    async def arrive(self, participant_id: str) -> bool:
        """Record a participant's arrival at the barrier."""
        if self._state in (SyncState.COMPLETED, SyncState.CANCELLED):
            return False
        
        if participant_id in self._arrived:
            return True  # Already arrived
        
        self._arrived.add(participant_id)
        
        if len(self._arrived) >= self._participant_count:
            self._state = SyncState.READY
            return True
        
        return False
    
    async def wait(self, timeout_seconds: Optional[float] = None) -> bool:
        """Wait for barrier to open."""
        import asyncio
        
        effective_timeout = timeout_seconds or self._timeout_seconds
        
        if self._state == SyncState.READY:
            return True
        
        if self._state in (SyncState.COMPLETED, SyncState.CANCELLED):
            return False
        
        # In a real implementation, this would wait on an event
        # For now, simulate by checking state periodically
        if effective_timeout is None:
            while self._state != SyncState.READY and self._state not in (
                SyncState.COMPLETED, SyncState.CANCELLED
            ):
                await asyncio.sleep(0.01)
        else:
            start_time = time.monotonic()
            while time.monotonic() - start_time < effective_timeout:
                if self._state == SyncState.READY:
                    return True
                if self._state in (SyncState.COMPLETED, SyncState.CANCELLED):
                    return False
                await asyncio.sleep(0.01)
        
        # Timeout expired
        if self._state != SyncState.READY:
            self._state = SyncState.FAILED
        
        return self._state == SyncState.READY
    
    async def signal(self) -> None:
        """Signal readiness (for barrier, arrival signals this)."""
        pass  # Arrivals handle the signaling
    
    async def release(self) -> None:
        """Release waiting participants by marking as completed."""
        if self._state == SyncState.READY:
            self._state = SyncState.COMPLETED
    
    async def cancel(self) -> None:
        """Cancel this synchronization."""
        self._state = SyncState.CANCELLED


class GateSynchronization:
    """
    Gate synchronization implementation.
    
    Controls access through a single gate that participants must pass through.
    """
    
    def __init__(
        self,
        sync_id: SyncId,
        initial_state: bool = False,
        timeout_seconds: Optional[float] = None
    ):
        self._sync_id = sync_id
        self._is_open = initial_state
        self._timeout_seconds = timeout_seconds
        self._state = SyncState.PENDING if not initial_state else SyncState.READY
        self._timestamp_utc = time.monotonic()
    
    @property
    def sync_id(self) -> SyncId:
        return self._sync_id
    
    @property
    def state(self) -> SyncState:
        return self._state
    
    @property
    def timestamp_utc(self) -> float:
        return self._timestamp_utc
    
    @property
    def is_open(self) -> bool:
        return self._is_open
    
    async def wait(self, timeout_seconds: Optional[float] = None) -> bool:
        """Wait for gate to open."""
        import asyncio
        
        effective_timeout = timeout_seconds or self._timeout_seconds
        
        if self._state == SyncState.READY:
            return True
        
        if self._state in (SyncState.COMPLETED, SyncState.CANCELLED):
            return False
        
        # In a real implementation, this would wait on an event
        if effective_timeout is None:
            while not self._is_open and self._state not in (
                SyncState.COMPLETED, SyncState.CANCELLED
            ):
                await asyncio.sleep(0.01)
        else:
            start_time = time.monotonic()
            while time.monotonic() - start_time < effective_timeout:
                if self._is_open:
                    self._state = SyncState.READY
                    return True
                if self._state in (SyncState.COMPLETED, SyncState.CANCELLED):
                    return False
                await asyncio.sleep(0.01)
        
        # Timeout expired
        if not self._is_open:
            self._state = SyncState.FAILED
        
        return self._is_open
    
    async def open_gate(self) -> None:
        """Open the gate, allowing participants to proceed."""
        self._is_open = True
        self._state = SyncState.READY
    
    async def close_gate(self) -> None:
        """Close the gate."""
        self._is_open = False
        if self._state == SyncState.READY:
            self._state = SyncState.PENDING
    
    async def signal(self) -> None:
        pass  # Gate control is explicit
    
    async def release(self) -> None:
        """Release by opening the gate."""
        await self.open_gate()
    
    async def cancel(self) -> None:
        """Cancel this synchronization."""
        self._state = SyncState.CANCELLED


class LatchSynchronization:
    """
    Latch synchronization implementation.
    
    Count-based synchronization that opens after threshold is reached.
    """
    
    def __init__(
        self,
        sync_id: SyncId,
        threshold: int,
        timeout_seconds: Optional[float] = None
    ):
        self._sync_id = sync_id
        self._threshold = threshold
        self._timeout_seconds = timeout_seconds
        self._count = 0
        self._state = SyncState.PENDING
        self._timestamp_utc = time.monotonic()
    
    @property
    def sync_id(self) -> SyncId:
        return self._sync_id
    
    @property
    def state(self) -> SyncState:
        return self._state
    
    @property
    def timestamp_utc(self) -> float:
        return self._timestamp_utc
    
    @property
    def threshold(self) -> int:
        return self._threshold
    
    @property
    def current_count(self) -> int:
        return self._count
    
    async def count_down(self) -> bool:
        """Decrement counter and check if latch should open."""
        if self._state == SyncState.READY:
            return True
        
        self._count += 1
        
        if self._count >= self._threshold:
            self._state = SyncState.READY
            return True
        
        return False
    
    async def wait(self, timeout_seconds: Optional[float] = None) -> bool:
        """Wait for latch to open."""
        import asyncio
        
        effective_timeout = timeout_seconds or self._timeout_seconds
        
        if self._state == SyncState.READY:
            return True
        
        if self._state in (SyncState.COMPLETED, SyncState.CANCELLED):
            return False
        
        # In a real implementation, this would wait on an event
        if effective_timeout is None:
            while self._state != SyncState.READY and self._state not in (
                SyncState.COMPLETED, SyncState.CANCELLED
            ):
                await asyncio.sleep(0.01)
        else:
            start_time = time.monotonic()
            while time.monotonic() - start_time < effective_timeout:
                if self._state == SyncState.READY:
                    return True
                if self._state in (SyncState.COMPLETED, SyncState.CANCELLED):
                    return False
                await asyncio.sleep(0.01)
        
        # Timeout expired
        if self._state != SyncState.READY:
            self._state = SyncState.FAILED
        
        return self._state == SyncState.READY
    
    async def signal(self) -> None:
        pass  # Count_down handles the signaling
    
    async def release(self) -> None:
        """Release by marking as completed."""
        if self._state == SyncState.READY:
            self._state = SyncState.COMPLETED
    
    async def cancel(self) -> None:
        """Cancel this synchronization."""
        self._state = SyncState.CANCELLED


class RendezvousSynchronization:
    """
    Two-party rendezvous synchronization implementation.
    
    Allows two participants to synchronize and exchange information.
    """
    
    def __init__(
        self,
        sync_id: SyncId,
        timeout_seconds: Optional[float] = None
    ):
        self._sync_id = sync_id
        self._timeout_seconds = timeout_seconds
        self._first_arrival: Optional[str] = None
        self._state = SyncState.PENDING
        self._timestamp_utc = time.monotonic()
    
    @property
    def sync_id(self) -> SyncId:
        return self._sync_id
    
    @property
    def state(self) -> SyncState:
        return self._state
    
    @property
    def timestamp_utc(self) -> float:
        return self._timestamp_utc
    
    async def await_arrival(self, participant_id: str) -> Optional[str]:
        """Wait for a second participant to arrive."""
        import asyncio
        
        if self._first_arrival is None:
            self._first_arrival = participant_id
            self._state = SyncState.PENDING
            
            # Wait for second arrival
            effective_timeout = self._timeout_seconds
            
            if effective_timeout is None:
                while self._state == SyncState.PENDING:
                    await asyncio.sleep(0.01)
            else:
                start_time = time.monotonic()
                while time.monotonic() - start_time < effective_timeout:
                    if self._state != SyncState.PENDING:
                        break
                    await asyncio.sleep(0.01)
            
            # Check result
            if self._state == SyncState.COMPLETED:
                return self._first_arrival  # Return the other participant
            
        elif self._state == SyncState.PENDING:
            self._state = SyncState.COMPLETED
            return self._first_arrival
        
        return None
    
    async def wait(self, timeout_seconds: Optional[float] = None) -> bool:
        """Wait for rendezvous to complete."""
        import asyncio
        
        effective_timeout = timeout_seconds or self._timeout_seconds
        
        if self._state == SyncState.COMPLETED:
            return True
        
        if self._state in (SyncState.FAILED, SyncState.CANCELLED):
            return False
        
        # In a real implementation, this would wait on an event
        if effective_timeout is None:
            while self._state != SyncState.COMPLETED and self._state not in (
                SyncState.FAILED, SyncState.CANCELLED
            ):
                await asyncio.sleep(0.01)
        else:
            start_time = time.monotonic()
            while time.monotonic() - start_time < effective_timeout:
                if self._state == SyncState.COMPLETED:
                    return True
                if self._state in (SyncState.FAILED, SyncState.CANCELLED):
                    return False
                await asyncio.sleep(0.01)
        
        # Timeout expired
        if self._state != SyncState.COMPLETED:
            self._state = SyncState.FAILED
        
        return self._state == SyncState.COMPLETED
    
    async def signal(self) -> None:
        pass  # Arrival handling handles signaling
    
    async def release(self) -> None:
        """Release by completing the rendezvous."""
        if self._state == SyncState.PENDING and self._first_arrival is not None:
            self._state = SyncState.COMPLETED
    
    async def cancel(self) -> None:
        """Cancel this synchronization."""
        self._state = SyncState.CANCELLED


class CompletionGroupSynchronization:
    """
    Completion group synchronization implementation.
    
    Tracks completion of multiple concurrent operations.
    """
    
    def __init__(
        self,
        sync_id: SyncId,
        expected_count: int,
        timeout_seconds: Optional[float] = None
    ):
        self._sync_id = sync_id
        self._expected_count = expected_count
        self._timeout_seconds = timeout_seconds
        self._completed_operations: Set[str] = set()
        self._state = SyncState.PENDING
        self._timestamp_utc = time.monotonic()
    
    @property
    def sync_id(self) -> SyncId:
        return self._sync_id
    
    @property
    def state(self) -> SyncState:
        return self._state
    
    @property
    def timestamp_utc(self) -> float:
        return self._timestamp_utc
    
    @property
    def expected_count(self) -> int:
        return self._expected_count
    
    @property
    def completed_count(self) -> int:
        return len(self._completed_operations)
    
    async def record_completion(self, operation_id: str) -> bool:
        """Record completion of an operation."""
        if self._state == SyncState.COMPLETED:
            return True
        
        self._completed_operations.add(operation_id)
        
        if len(self._completed_operations) >= self._expected_count:
            self._state = SyncState.READY
            return True
        
        return False
    
    async def wait(self, timeout_seconds: Optional[float] = None) -> bool:
        """Wait for all operations to complete."""
        import asyncio
        
        effective_timeout = timeout_seconds or self._timeout_seconds
        
        if self._state == SyncState.READY:
            return True
        
        if self._state in (SyncState.COMPLETED, SyncState.CANCELLED):
            return False
        
        # In a real implementation, this would wait on an event
        if effective_timeout is None:
            while self._state != SyncState.READY and self._state not in (
                SyncState.COMPLETED, SyncState.CANCELLED
            ):
                await asyncio.sleep(0.01)
        else:
            start_time = time.monotonic()
            while time.monotonic() - start_time < effective_timeout:
                if self._state == SyncState.READY:
                    return True
                if self._state in (SyncState.COMPLETED, SyncState.CANCELLED):
                    return False
                await asyncio.sleep(0.01)
        
        # Timeout expired
        if self._state != SyncState.READY:
            self._state = SyncState.FAILED
        
        return self._state == SyncState.READY
    
    async def signal(self) -> None:
        pass  # Completion recording handles signaling
    
    async def release(self) -> None:
        """Release by marking as completed."""
        if self._state == SyncState.READY:
            self._state = SyncState.COMPLETED
    
    async def cancel(self) -> None:
        """Cancel this synchronization."""
        self._state = SyncState.CANCELLED


class CheckpointSynchronization:
    """
    Checkpoint synchronization implementation.
    
    Records and verifies execution points for determinism.
    """
    
    def __init__(
        self,
        sync_id: SyncId
    ):
        self._sync_id = sync_id
        self._checkpoint_state: Optional[Dict[str, Any]] = None
        self._state = SyncState.PENDING
        self._timestamp_utc = time.monotonic()
        self._checkpoint_id = f"chk_{uuid.uuid4().hex[:16]}"
    
    @property
    def sync_id(self) -> SyncId:
        return self._sync_id
    
    @property
    def state(self) -> SyncState:
        return self._state
    
    @property
    def timestamp_utc(self) -> float:
        return self._timestamp_utc
    
    async def record_state(self, state_data: Dict[str, Any]) -> str:
        """Record current state at checkpoint."""
        self._checkpoint_state = dict(state_data)
        self._state = SyncState.READY
        return self._checkpoint_id
    
    async def verify_state(self, expected_checkpoint_id: str) -> bool:
        """Verify that current state matches recorded checkpoint."""
        if self._checkpoint_id != expected_checkpoint_id:
            return False
        
        # In a real implementation, this would verify actual state
        self._state = SyncState.COMPLETED
        return True
    
    async def wait(self, timeout_seconds: Optional[float] = None) -> bool:
        """Wait for checkpoint to be recorded."""
        if self._state in (SyncState.READY, SyncState.COMPLETED):
            return True
        
        return False
    
    async def signal(self) -> None:
        pass  # State recording handles the signaling
    
    async def release(self) -> None:
        """Release by marking as completed."""
        if self._state == SyncState.READY:
            self._state = SyncState.COMPLETED
    
    async def cancel(self) -> None:
        """Cancel this synchronization."""
        self._state = SyncState.CANCELLED


# =============================================================================
# SYNCHRONIZATION OWNERSHIP
# =============================================================================

@dataclass(frozen=True)
class SyncOwnership:
    """
    Ownership record for a synchronization primitive.
    
    Defines which component owns this synchronization and what authority it has.
    """
    
    owner_id: str  # Component ID that owns this sync
    sync_id: SyncId
    created_at_utc: float
    can_signal: bool = True   # Can signal progression
    can_release: bool = True  # Can release waiters
    can_cancel: bool = True   # Can cancel the synchronization


# =============================================================================
# SYNCHRONIZATION OBSERVABILITY
# =============================================================================

@dataclass(frozen=True)
class SyncObservability:
    """Observability data for synchronization events."""
    
    sync_id: SyncId
    timestamp_utc: float
    event_type: str  # "WAIT_START", "ARRIVED", "RELEASED", etc.
    participant_id: Optional[str] = None
    state_before: Optional[SyncState] = None
    state_after: Optional[SyncState] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    @property
    def is_replayable(self) -> bool:
        """Observability data must be replayable."""
        return True


# =============================================================================
# SYNCHRONIZATION FAILURE TYPES
# =============================================================================

class SyncFailureType(Enum):
    """Types of synchronization failures."""
    
    TIMEOUT = "timeout"
    DEADLOCK = "deadlock"
    STARVATION = "starvation"
    READINESS_FAILURE = "readiness_failure"
    PARTICIPANT_FAILURE = "participant_failure"
    CANCELLATION = "cancellation"
    DEPENDENCY_FAILURE = "dependency_failure"


@dataclass(frozen=True)
class SyncFailure:
    """Record of a synchronization failure with diagnostic metadata."""
    
    sync_id: SyncId
    timestamp_utc: float
    failure_type: SyncFailureType
    participant_ids: Tuple[str, ...]
    message: str
    context: Dict[str, Any] = field(default_factory=dict)
    
    @property
    def is_replayable(self) -> bool:
        """Failure records must be replayable."""
        return True


# =============================================================================
# SYNCHRONIZATION PRIMITIVES EXPORTS
# =============================================================================

__all__ = [
    # Identity
    "SyncId",
    "SyncEventId",
    
    # States and modes
    "SyncState",
    "SyncMode",
    
    # Protocols
    "SyncPrimitive",
    "BarrierSync",
    "GateSync",
    "LatchSync",
    "RendezvousSync",
    "CompletionGroupSync",
    "CheckpointSync",
    "SyncContract",
    "SyncPrimitiveFactory",
    
    # Concrete primitives
    "BarrierSynchronization",
    "GateSynchronization",
    "LatchSynchronization",
    "RendezvousSynchronization",
    "CompletionGroupSynchronization",
    "CheckpointSynchronization",
    
    # Events and contracts
    "SyncEvent",
    "SyncContract",
    
    # Ownership and observability
    "SyncOwnership",
    "SyncObservability",
    
    # Failures
    "SyncFailureType",
    "SyncFailure",
]