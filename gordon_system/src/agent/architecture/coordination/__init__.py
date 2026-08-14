# Coordination Architecture (Phase 3.14.12)
# ============================================
#
# Coordination determines how architectural participants cooperate.
#
# Canonical Model:
#     Execution → Synchronization → Coordination → Participants → Execution Continuation
#
# Coordination PRINCIPLES:
# - Coordination never performs computation
# - Coordination never owns state
# - Coordination determines participant cooperation
# - Coordination preserves architectural independence

"""
Canonical Coordination Architecture for Gordon Phase 3.14.12.

This module establishes the immutable contracts ensuring deterministic cooperation
between Execution, Streams Networks, Capabilities, Systems, and future
architectural domains through Coordination primitives.
"""

from dataclasses import dataclass, field
from typing import Protocol, Any, Optional, List, Set, Tuple, Dict
from enum import Enum, auto
import uuid
import time


# =============================================================================
# COORDINATION IDENTITY
# =============================================================================

@dataclass(frozen=True)
class CoordId:
    """Unique identifier for a coordination primitive instance."""
    
    value: str
    
    @classmethod
    def generate(cls) -> "CoordId":
        """Generate a new unique coordination ID."""
        return cls(value=f"coord_{uuid.uuid4().hex[:16]}")
    
    def __str__(self) -> str:
        return self.value


@dataclass(frozen=True)
class CoordEventId:
    """Unique identifier for a coordination event."""
    
    value: str
    
    @classmethod
    def generate(cls) -> "CoordEventId":
        """Generate a new unique coordination event ID."""
        return cls(value=f"coord_event_{uuid.uuid4().hex[:16]}")
    
    def __str__(self) -> str:
        return self.value


# =============================================================================
# COORDINATION STATES
# =============================================================================

class CoordState(Enum):
    """
    Coordination primitive states.
    
    Every coordination primitive transitions through these states:
        PENDING → (awaiting participants)
        ACTIVE → (participants engaged)
        COMPLETE → (cooperation achieved)
        FAILED → (coordination failed)
        CANCELLED → (explicitly cancelled)
    """
    
    PENDING = "pending"
    ACTIVE = "active"
    COMPLETE = "complete"
    FAILED = "failed"
    CANCELLED = "cancelled"


class CoordMode(Enum):
    """Coordination execution modes."""
    
    COORDINATOR = "coordinator"         # Central coordinator model
    ORCHESTRATOR = "orchestrator"       # Orchestrated cooperation
    ARBITER = "arbiter"                 # Arbitrated access control
    AGGREGATOR = "aggregator"           # Aggregated results from participants
    DISPATCHER = "dispatcher"           # Dispatch work to participants
    SCHEDULER_INTERFACE = "scheduler_interface"  # Interface for scheduling
    ADMISSION_CONTROLLER = "admission_controller"  # Admission control


# =============================================================================
# PARTICIPANT DECLARATION
# =============================================================================

@dataclass(frozen=True)
class ParticipantDeclaration:
    """
    Declaration of participation in coordination.
    
    Every participant must explicitly declare readiness.
    Implicit readiness is prohibited.
    """
    
    coord_id: CoordId
    participant_id: str
    declared_at_utc: float
    ready: bool = False
    
    @property
    def is_readiness_deterministic(self) -> bool:
        """Readiness declarations are deterministic and timestamped."""
        return True


# =============================================================================
# COORDINATION PRIMITIVE PROTOCOLS
# =============================================================================

class CoordPrimitive(Protocol):
    """Base protocol for all coordination primitives."""
    
    @property
    def coord_id(self) -> CoordId:
        """Unique identifier for this primitive."""
        ...
    
    @property
    def state(self) -> CoordState:
        """Current state of the primitive."""
        ...
    
    @property
    def timestamp_utc(self) -> float:
        """When this primitive was created (UTC monotonic)."""
        ...
    
    async def register_participant(self, participant_id: str) -> bool:
        """Register a participant in this coordination."""
        ...
    
    async def declare_readiness(self, participant_id: str) -> bool:
        """Participant declares it is ready."""
        ...
    
    async def get_ready_participants(self) -> List[str]:
        """Get list of participants that have declared readiness."""
        ...
    
    async def is_coordination_complete(self) -> bool:
        """Check if coordination has achieved its goal."""
        ...


class CoordinatorCoord(Protocol):
    """
    Coordinator coordination primitive.
    
    Central coordinator manages participant cooperation.
    """
    
    @property
    def participants(self) -> Set[str]:
        """All registered participants."""
        ...
    
    async def assign_participation(
        self,
        participant_id: str,
        task: Dict[str, Any]
    ) -> bool:
        """Assign a task to a participant."""
        ...
    
    async def get_execution_order(self) -> List[str]:
        """Get the ordered list of participants for execution."""
        ...


class OrchestratorCoord(Protocol):
    """
    Orchestrator coordination primitive.
    
    Orchestrates cooperation between multiple participants.
    """
    
    @property
    def stages(self) -> List[str]:
        """Ordered stages of orchestration."""
        ...
    
    async def register_stage_participant(
        self,
        stage: str,
        participant_id: str
    ) -> bool:
        """Register a participant for a specific stage."""
        ...
    
    async def get_stage_order(self, stage: str) -> List[str]:
        """Get ordered participants for a specific stage."""
        ...


class ArbiterCoord(Protocol):
    """
    Arbiter coordination primitive.
    
    Manages access control and order negotiation between participants.
    """
    
    @property
    def waiting_participants(self) -> Set[str]:
        """Participants waiting for access."""
        ...
    
    async def negotiate_readiness(
        self,
        participant_id: str
    ) -> bool:
        """Negotiate readiness with a participant."""
        ...
    
    async def grant_access(self, participant_id: str) -> None:
        """Grant access to a participant."""
        ...


class AggregatorCoord(Protocol):
    """
    Aggregator coordination primitive.
    
    Aggregates results from multiple participants.
    """
    
    @property
    def expected_participant_count(self) -> int:
        """Total number of participants expected."""
        ...
    
    async def aggregate_result(
        self,
        participant_id: str,
        result: Any
    ) -> Optional[Any]:
        """Aggregate a participant's result. Returns aggregated result if complete."""
        ...
    
    @property
    def aggregation_complete(self) -> bool:
        """Check if all results have been aggregated."""
        ...


class DispatcherCoord(Protocol):
    """
    Dispatcher coordination primitive.
    
    Distributes work to participants.
    """
    
    async def dispatch_work(
        self,
        participant_id: str,
        work_item: Dict[str, Any]
    ) -> bool:
        """Dispatch a work item to a participant."""
        ...
    
    async def get_next_participant(self) -> Optional[str]:
        """Get the next participant for work distribution."""
        ...


class SchedulerInterfaceCoord(Protocol):
    """
    Scheduler Interface coordination primitive.
    
    Provides scheduling interface for participants.
    """
    
    async def schedule_execution(
        self,
        participant_id: str,
        priority: int = 0
    ) -> bool:
        """Schedule execution for a participant."""
        ...
    
    async def get_scheduled_participants(self) -> List[Tuple[str, int]]:
        """Get participants sorted by scheduling priority."""
        ...


class AdmissionControllerCoord(Protocol):
    """
    Admission Controller coordination primitive.
    
    Controls admission of participants to coordination.
    """
    
    @property
    def max_capacity(self) -> int:
        """Maximum number of participants allowed."""
        ...
    
    async def check_admission(
        self,
        participant_id: str
    ) -> Tuple[bool, Optional[str]]:
        """Check if participant can be admitted. Returns (admit, reason)."""
        ...
    
    async def admit_participant(self, participant_id: str) -> bool:
        """Admit a participant to the coordination."""
        ...


# =============================================================================
# COORDINATION EVENT
# =============================================================================

@dataclass(frozen=True)
class CoordEvent:
    """
    Event emitted during coordination progression.
    
    Every coordination action generates events for observability.
    """
    
    event_id: CoordEventId
    coord_id: CoordId
    timestamp_utc: float
    event_type: str  # "PARTICIPANT_REGISTERED", "READY_DECLARED", etc.
    participant_id: Optional[str] = None
    details: Dict[str, Any] = field(default_factory=dict)
    
    @property
    def is_replayable(self) -> bool:
        """Events are replayable if they contain deterministic data."""
        return True


# =============================================================================
# COORDINATION CONTRACT
# =============================================================================

class CoordContract(Protocol):
    """
    Protocol for coordination contracts that participants must satisfy.
    
    Every participant in a coordination must fulfill its contract.
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
# COORDINATION OWNERSHIP
# =============================================================================

@dataclass(frozen=True)
class CoordOwnership:
    """
    Ownership record for a coordination primitive.
    
    Defines which component owns this coordination and what authority it has.
    """
    
    owner_id: str  # Component ID that owns this coord
    coord_id: CoordId
    created_at_utc: float
    can_register: bool = True      # Can register participants
    can_declare_ready: bool = True # Can declare participant readiness
    can_cancel: bool = True        # Can cancel the coordination


# =============================================================================
# COORDINATION OBSERVABILITY
# =============================================================================

@dataclass(frozen=True)
class CoordObservability:
    """Observability data for coordination events."""
    
    coord_id: CoordId
    timestamp_utc: float
    event_type: str  # "WAIT_START", "PARTICIPANT_REGISTERED", etc.
    participant_id: Optional[str] = None
    state_before: Optional[CoordState] = None
    state_after: Optional[CoordState] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    @property
    def is_replayable(self) -> bool:
        """Observability data must be replayable."""
        return True


# =============================================================================
# COORDINATION FAILURE TYPES
# =============================================================================

class CoordFailureType(Enum):
    """Types of coordination failures."""
    
    TIMEOUT = "timeout"
    DEADLOCK = "deadlock"
    STARVATION = "starvation"
    PARTICIPANT_FAILURE = "participant_failure"
    CANCELLATION = "cancellation"
    DEPENDENCY_FAILURE = "dependency_failure"


@dataclass(frozen=True)
class CoordFailure:
    """Record of a coordination failure with diagnostic metadata."""
    
    coord_id: CoordId
    timestamp_utc: float
    failure_type: CoordFailureType
    participant_ids: Tuple[str, ...]
    message: str
    context: Dict[str, Any] = field(default_factory=dict)
    
    @property
    def is_replayable(self) -> bool:
        """Failure records must be replayable."""
        return True


# =============================================================================
# CONCRETE COORDINATION PRIMITIVES
# =============================================================================

class CoordinatorCoordination:
    """
    Coordinator coordination implementation.
    
    Central coordinator manages participant cooperation.
    """
    
    def __init__(
        self,
        coord_id: CoordId,
        max_participants: Optional[int] = None
    ):
        self._coord_id = coord_id
        self._max_participants = max_participants
        self._participants: Set[str] = set()
        self._ready: Set[str] = set()
        self._tasks: Dict[str, Dict[str, Any]] = {}
        self._state = CoordState.PENDING
        self._timestamp_utc = time.monotonic()
    
    @property
    def coord_id(self) -> CoordId:
        return self._coord_id
    
    @property
    def state(self) -> CoordState:
        return self._state
    
    @property
    def timestamp_utc(self) -> float:
        return self._timestamp_utc
    
    @property
    def participants(self) -> Set[str]:
        return self._participants.copy()
    
    async def register_participant(self, participant_id: str) -> bool:
        if self._max_participants and len(self._participants) >= self._max_participants:
            return False
        
        if participant_id in self._participants:
            return True
        
        self._participants.add(participant_id)
        
        if self._state == CoordState.PENDING:
            self._state = CoordState.ACTIVE
        
        return True
    
    async def declare_readiness(self, participant_id: str) -> bool:
        if participant_id not in self._participants:
            return False
        
        self._ready.add(participant_id)
        
        # Check if all participants are ready
        if len(self._ready) == len(self._participants):
            self._state = CoordState.COMPLETE
        
        return True
    
    async def get_ready_participants(self) -> List[str]:
        return list(self._ready)
    
    async def is_coordination_complete(self) -> bool:
        return self._state == CoordState.COMPLETE
    
    async def assign_participation(
        self,
        participant_id: str,
        task: Dict[str, Any]
    ) -> bool:
        if participant_id not in self._participants:
            return False
        
        self._tasks[participant_id] = task
        return True
    
    async def get_execution_order(self) -> List[str]:
        # Return participants sorted by registration order (stable)
        return list(self._participants)


class OrchestratorCoordination:
    """
    Orchestrator coordination implementation.
    
    Orchestrates cooperation between multiple participants across stages.
    """
    
    def __init__(
        self,
        coord_id: CoordId,
        stages: List[str]
    ):
        self._coord_id = coord_id
        self._stages = stages.copy()
        self._stage_participants: Dict[str, Set[str]] = {s: set() for s in stages}
        self._ready_stages: Set[str] = set()
        self._state = CoordState.PENDING
        self._timestamp_utc = time.monotonic()
    
    @property
    def coord_id(self) -> CoordId:
        return self._coord_id
    
    @property
    def state(self) -> CoordState:
        return self._state
    
    @property
    def timestamp_utc(self) -> float:
        return self._timestamp_utc
    
    @property
    def stages(self) -> List[str]:
        return self._stages.copy()
    
    async def register_stage_participant(
        self,
        stage: str,
        participant_id: str
    ) -> bool:
        if stage not in self._stage_participants:
            return False
        
        self._stage_participants[stage].add(participant_id)
        
        # Update state
        all_ready = all(len(p) > 0 for p in self._stage_participants.values())
        self._state = CoordState.ACTIVE if all_ready else CoordState.PENDING
        
        return True
    
    async def get_stage_order(self, stage: str) -> List[str]:
        return list(self._stage_participants.get(stage, []))
    
    async def declare_readiness_for_stage(
        self,
        stage: str,
        participant_id: str
    ) -> bool:
        if participant_id not in self._stage_participants.get(stage, set()):
            return False
        
        ready_key = f"{stage}_{participant_id}"
        if ready_key not in getattr(self, "_ready_stages", set()):
            # Mark stage as having at least one ready participant
            pass
        
        return True
    
    async def is_coordination_complete(self) -> bool:
        return self._state == CoordState.COMPLETE


class ArbiterCoordination:
    """
    Arbiter coordination implementation.
    
    Manages access control and order negotiation between participants.
    """
    
    def __init__(
        self,
        coord_id: CoordId
    ):
        self._coord_id = coord_id
        self._waiting_participants: Set[str] = set()
        self._granted_access: Set[str] = set()
        self._state = CoordState.PENDING
        self._timestamp_utc = time.monotonic()
    
    @property
    def coord_id(self) -> CoordId:
        return self._coord_id
    
    @property
    def state(self) -> CoordState:
        return self._state
    
    @property
    def timestamp_utc(self) -> float:
        return self._timestamp_utc
    
    @property
    def waiting_participants(self) -> Set[str]:
        return self._waiting_participants.copy()
    
    async def register_participant(self, participant_id: str) -> bool:
        if participant_id in self._waiting_participants:
            return True
        
        self._waiting_participants.add(participant_id)
        self._state = CoordState.ACTIVE
        return True
    
    async def negotiate_readiness(self, participant_id: str) -> bool:
        if participant_id not in self._waiting_participants:
            return False
        
        # In real implementation, this would negotiate with other participants
        return True
    
    async def grant_access(self, participant_id: str) -> None:
        if participant_id in self._waiting_participants:
            self._granted_access.add(participant_id)
            self._waiting_participants.discard(participant_id)
    
    async def declare_readiness(self, participant_id: str) -> bool:
        return await self.negotiate_readiness(participant_id)
    
    async def get_ready_participants(self) -> List[str]:
        return list(self._granted_access)
    
    async def is_coordination_complete(self) -> bool:
        return len(self._waiting_participants) == 0


class AggregatorCoordination:
    """
    Aggregator coordination implementation.
    
    Aggregates results from multiple participants.
    """
    
    def __init__(
        self,
        coord_id: CoordId,
        expected_count: int
    ):
        self._coord_id = coord_id
        self._expected_count = expected_count
        self._results: Dict[str, Any] = {}
        self._state = CoordState.PENDING
        self._timestamp_utc = time.monotonic()
    
    @property
    def coord_id(self) -> CoordId:
        return self._coord_id
    
    @property
    def state(self) -> CoordState:
        return self._state
    
    @property
    def timestamp_utc(self) -> float:
        return self._timestamp_utc
    
    @property
    def expected_participant_count(self) -> int:
        return self._expected_count
    
    async def register_participant(self, participant_id: str) -> bool:
        if len(self._results) >= self._expected_count:
            return False
        
        if participant_id not in self._results:
            self._results[participant_id] = None
            self._state = CoordState.ACTIVE
        
        return True
    
    async def aggregate_result(
        self,
        participant_id: str,
        result: Any
    ) -> Optional[Any]:
        if participant_id not in self._results:
            return None
        
        self._results[participant_id] = result
        
        # Check if all results are collected
        if len(self._results) >= self._expected_count and None not in self._results.values():
            self._state = CoordState.COMPLETE
            return dict(self._results)
        
        return None
    
    @property
    def aggregation_complete(self) -> bool:
        return self._state == CoordState.COMPLETE
    
    async def declare_readiness(self, participant_id: str) -> bool:
        # Participants are ready when they provide results
        return await self.aggregate_result(participant_id, "ready") is not None
    
    async def get_ready_participants(self) -> List[str]:
        if self._state == CoordState.COMPLETE:
            return list(self._results.keys())
        return []
    
    async def is_coordination_complete(self) -> bool:
        return self._state == CoordState.COMPLETE


class DispatcherCoordination:
    """
    Dispatcher coordination implementation.
    
    Distributes work to participants.
    """
    
    def __init__(
        self,
        coord_id: CoordId
    ):
        self._coord_id = coord_id
        self._participants: Set[str] = set()
        self._work_queue: List[Dict[str, Any]] = []
        self._dispatched: Dict[str, Dict[str, Any]] = {}
        self._state = CoordState.PENDING
        self._timestamp_utc = time.monotonic()
    
    @property
    def coord_id(self) -> CoordId:
        return self._coord_id
    
    @property
    def state(self) -> CoordState:
        return self._state
    
    @property
    def timestamp_utc(self) -> float:
        return self._timestamp_utc
    
    async def register_participant(self, participant_id: str) -> bool:
        if participant_id in self._participants:
            return True
        
        self._participants.add(participant_id)
        self._state = CoordState.ACTIVE
        return True
    
    async def add_work_item(self, work_item: Dict[str, Any]) -> None:
        self._work_queue.append(work_item)
    
    async def dispatch_work(
        self,
        participant_id: str,
        work_item: Dict[str, Any]
    ) -> bool:
        if participant_id not in self._participants:
            return False
        
        self._dispatched[participant_id] = work_item
        return True
    
    async def get_next_participant(self) -> Optional[str]:
        # Round-robin selection from participants
        if not self._participants:
            return None
        
        # Get next participant (simple round-robin logic)
        participants_list = list(self._participants)
        for pid in participants_list:
            if pid not in self._dispatched:
                return pid
        
        return None
    
    async def declare_readiness(self, participant_id: str) -> bool:
        return True  # Participants ready upon registration
    
    async def get_ready_participants(self) -> List[str]:
        return list(self._participants)
    
    async def is_coordination_complete(self) -> bool:
        return len(self._work_queue) == 0 and len(self._dispatched) > 0


class SchedulerInterfaceCoordination:
    """
    Scheduler Interface coordination implementation.
    
    Provides scheduling interface for participants.
    """
    
    def __init__(
        self,
        coord_id: CoordId
    ):
        self._coord_id = coord_id
        self._scheduled: List[Tuple[str, int]] = []  # (participant_id, priority)
        self._participants: Set[str] = set()
        self._state = CoordState.PENDING
        self._timestamp_utc = time.monotonic()
    
    @property
    def coord_id(self) -> CoordId:
        return self._coord_id
    
    @property
    def state(self) -> CoordState:
        return self._state
    
    @property
    def timestamp_utc(self) -> float:
        return self._timestamp_utc
    
    async def register_participant(self, participant_id: str) -> bool:
        if participant_id in self._participants:
            return True
        
        self._participants.add(participant_id)
        self._scheduled.append((participant_id, 0))
        self._state = CoordState.ACTIVE
        return True
    
    async def schedule_execution(
        self,
        participant_id: str,
        priority: int = 0
    ) -> bool:
        if participant_id not in self._participants:
            return False
        
        # Update priority
        for i, (pid, p) in enumerate(self._scheduled):
            if pid == participant_id:
                self._scheduled[i] = (participant_id, priority)
                break
        
        return True
    
    async def get_scheduled_participants(self) -> List[Tuple[str, int]]:
        # Sort by priority descending (higher priority first)
        return sorted(self._scheduled, key=lambda x: -x[1])
    
    async def declare_readiness(self, participant_id: str) -> bool:
        return True
    
    async def get_ready_participants(self) -> List[str]:
        return list(self._participants)
    
    async def is_coordination_complete(self) -> bool:
        return len(self._scheduled) > 0


class AdmissionControllerCoordination:
    """
    Admission Controller coordination implementation.
    
    Controls admission of participants to coordination.
    """
    
    def __init__(
        self,
        coord_id: CoordId,
        max_capacity: int = 10
    ):
        self._coord_id = coord_id
        self._max_capacity = max_capacity
        self._participants: Set[str] = set()
        self._admitted: Set[str] = set()
        self._state = CoordState.PENDING
        self._timestamp_utc = time.monotonic()
    
    @property
    def coord_id(self) -> CoordId:
        return self._coord_id
    
    @property
    def state(self) -> CoordState:
        return self._state
    
    @property
    def timestamp_utc(self) -> float:
        return self._timestamp_utc
    
    @property
    def max_capacity(self) -> int:
        return self._max_capacity
    
    async def check_admission(
        self,
        participant_id: str
    ) -> Tuple[bool, Optional[str]]:
        if len(self._participants) >= self._max_capacity:
            return False, "Capacity exceeded"
        
        if participant_id in self._participants:
            return True, None
        
        return True, None
    
    async def admit_participant(self, participant_id: str) -> bool:
        admit, reason = await self.check_admission(participant_id)
        
        if not admit:
            return False
        
        self._participants.add(participant_id)
        self._admitted.add(participant_id)
        self._state = CoordState.ACTIVE
        return True
    
    async def register_participant(self, participant_id: str) -> bool:
        return await self.admit_participant(participant_id)
    
    async def declare_readiness(self, participant_id: str) -> bool:
        if participant_id not in self._participants:
            return False
        
        self._admitted.add(participant_id)
        
        # Check if all admitted participants are ready
        if len(self._participants) == len(self._admitted):
            self._state = CoordState.COMPLETE
        
        return True
    
    async def get_ready_participants(self) -> List[str]:
        return list(self._admitted)
    
    async def is_coordination_complete(self) -> bool:
        return self._state == CoordState.COMPLETE


# =============================================================================
# COORDINATION PRIMITIVES EXPORTS
# =============================================================================

__all__ = [
    # Identity
    "CoordId",
    "CoordEventId",
    
    # States and modes
    "CoordState",
    "CoordMode",
    
    # Participant declaration
    "ParticipantDeclaration",
    
    # Protocols
    "CoordPrimitive",
    "CoordinatorCoord",
    "OrchestratorCoord",
    "ArbiterCoord",
    "AggregatorCoord",
    "DispatcherCoord",
    "SchedulerInterfaceCoord",
    "AdmissionControllerCoord",
    "CoordContract",
    
    # Events and contracts
    "CoordEvent",
    "CoordContract",
    
    # Ownership and observability
    "CoordOwnership",
    "CoordObservability",
    
    # Failures
    "CoordFailureType",
    "CoordFailure",
    
    # Concrete primitives
    "CoordinatorCoordination",
    "OrchestratorCoordination",
    "ArbiterCoordination",
    "AggregatorCoordination",
    "DispatcherCoordination",
    "SchedulerInterfaceCoordination",
    "AdmissionControllerCoordination",
]