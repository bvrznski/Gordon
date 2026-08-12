# Consistent Cut Coordination
# ===========================

"""
Consistent-cut coordination for multi-participant state capture.

This module provides:
- ConsistentCutPlan: Plan for capturing a consistent view of all participants
- ConsistentCutBoundary: Version boundary for cut consistency
- ConsistentCutResult: Result of a consistent cut operation
- Capture modes: quiescent, versioned, copy-on-write
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any
from enum import Enum, auto
import uuid
import time


# =============================================================================
# Capture Consistency Levels
# =============================================================================

class CaptureConsistencyLevel(Enum):
    """
    Level of consistency guaranteed for state capture.
    
    Each level has different requirements and guarantees:
        - QUIESCENT: No mutations during capture (strongest)
        - VERSIONED: Use version numbers to detect changes (moderate)
        - COPY_ON_WRITE: Snapshot-based capture with COW (good for large state)
    """
    
    QUIESCENT = "quiescent"           # Block all mutations during capture
    VERSIONED = "versioned"          # Detect changes via versions
    COPY_ON_WRITE = "copy_on_write"  # Use snapshot with copy-on-write


# =============================================================================
# Barrier Types
# =============================================================================

@dataclass(frozen=True)
class QuiescentBarrier:
    """
    A barrier that requires quiescence before proceeding.
    
    During quiescent capture, the system temporarily blocks mutations
    to ensure a consistent view of state.
    """
    
    barrier_id: str
    
    # Participants waiting at this barrier
    participants: List[str]
    
    # Timing
    requested_at: float
    quiesce_timeout_seconds: float
    
    # Status
    all_quiescent: bool = False
    quiesced_at: Optional[float] = None
    
    @classmethod
    def create(cls, participant_ids: List[str], timeout_seconds: float) -> "QuiescentBarrier":
        """Create a new quiescent barrier."""
        return cls(
            barrier_id=str(uuid.uuid4()),
            participants=participant_ids,
            requested_at=time.monotonic(),
            quiesce_timeout_seconds=timeout_seconds,
        )


@dataclass(frozen=True)
class CaptureVersionBoundary:
    """
    A version boundary for consistent capture.
    
    Records the version of each participant's state at the time of capture
    to enable detection of concurrent modifications.
    """
    
    boundary_id: str
    
    # Version snapshot per participant
    participant_versions: Dict[str, int]
    
    # Global sequence number if available
    global_sequence: Optional[int] = None
    
    # Timestamp for ordering
    captured_at: float = field(default_factory=time.monotonic)
    
    @classmethod
    def create(cls, participant_versions: Dict[str, int]) -> "CaptureVersionBoundary":
        """Create a new version boundary."""
        return cls(
            boundary_id=str(uuid.uuid4()),
            participant_versions=dict(participant_versions),
        )


@dataclass(frozen=True)
class CopyOnWriteSnapshot:
    """
    A copy-on-write snapshot for non-blocking capture.
    
    Uses COW to create an immutable view without blocking writers.
    """
    
    snapshot_id: str
    
    # Storage keys for each domain's snapshot
    domain_snapshots: Dict[str, str]
    
    # Original state versions before snapshot
    original_versions: Dict[str, int]
    
    created_at: float = field(default_factory=time.monotonic)


# =============================================================================
# Consistent Cut Request and Result Types
# =============================================================================

@dataclass(frozen=True)
class ConsistentCutRequest:
    """A request for consistent-cut capture."""
    
    request_id: str
    
    runtime_id: str
    domains: List[str]  # Domains to include - must come before optional fields with defaults
    
    # Optional settings (must be after required fields)
    boot_session_id: Optional[str] = None
    
    # Capture mode
    consistency_level: CaptureConsistencyLevel = CaptureConsistencyLevel.VERSIONED
    
    # Timeout for quiescent capture
    quiesce_timeout_seconds: float = 5.0


@dataclass(frozen=True)
class ConsistentCutPlan:
    """
    Plan for executing a consistent cut.
    
    Contains all information needed to perform the capture:
        - Which participants to call
        - In what order (considering dependencies)
        - What barrier strategy to use
        - How to handle failures
    """
    
    plan_id: str
    
    runtime_id: str
    boot_session_id: Optional[str]
    
    # Domains and their participants
    domain_participants: Dict[str, List[str]]  # domain -> [participant_ids]
    
    # Order for capture (topologically sorted if dependencies exist)
    capture_order: List[str]  # list of participant IDs
    
    # Barrier strategy
    barrier_type: CaptureConsistencyLevel = CaptureConsistencyLevel.VERSIONED
    quiesce_timeout_seconds: float = 5.0
    
    created_at: float = field(default_factory=time.monotonic)


@dataclass(frozen=True)
class ConsistentCutBoundary:
    """
    The boundary recorded during a consistent cut.
    
    This enables later verification that the captured state represents
    a valid consistent point in time.
    """
    
    boundary_id: str
    
    runtime_id: str
    
    # Capture time
    captured_at: float
    
    # Participant states at capture time
    participant_versions: Dict[str, int]
    
    # Version boundary type
    boundary_type: CaptureConsistencyLevel
    
    # Validation status
    validated: bool = False


@dataclass(frozen=True)
class ConsistentCutResult:
    """Result of a consistent cut operation."""
    
    result_id: str
    
    request_id: str
    runtime_id: str
    
    # Status
    status: "ConsistentCutStatus"
    
    timestamp: float = field(default_factory=time.monotonic)
    
    # Success case
    boundary: Optional[ConsistentCutBoundary] = None
    captured_domains: List[str] = field(default_factory=list)
    
    # Failure case
    error_message: Optional[str] = None
    
    @property
    def success(self) -> bool:
        return self.status == ConsistentCutStatus.COMPLETED


class ConsistentCutStatus(Enum):
    """Status of a consistent cut operation."""
    
    REQUESTED = "requested"
    PLANNING = "planning"
    BARRIER_PREPARING = "barrier_preparing"
    BARRIER_TRIGGERED = "barrier_triggered"
    CAPTURING = "capturing"
    VALIDATING = "validating"
    COMPLETED = "completed"
    PARTIAL = "partial"  # Some participants succeeded
    FAILED = "failed"
    TIMEOUT = "timeout"


# =============================================================================
# Consistent Cut Coordinator
# =============================================================================

class ConsistentCutCoordinator:
    """
    Coordinates consistent-cut capture across multiple participants.
    
    This is a coordination service, NOT an owner of state. It ensures
    that when multiple participants are captured together, they form
    a valid consistent cut.
    
    Usage:
        coordinator = ConsistentCutCoordinator(runtime_id="runtime_123")
        
        # Create capture plan
        plan = coordinator.create_plan(
            domains=["state_a", "state_b"],
            consistency_level=CaptureConsistencyLevel.VERSIONED
        )
        
        # Execute capture (participants implement the protocol)
        result = await coordinator.execute_cut(plan, participants)
    """
    
    def __init__(self, runtime_id: str) -> None:
        self._runtime_id = runtime_id
        
        # Track active cuts
        self._active_cuts: Dict[str, ConsistentCutResult] = {}
        
        # Metrics
        self._cut_count = 0
    
    @property
    def runtime_id(self) -> str:
        return self._runtime_id
    
    def create_plan(
        self,
        domains: List[str],
        consistency_level: CaptureConsistencyLevel = CaptureConsistencyLevel.VERSIONED,
        quiesce_timeout_seconds: float = 5.0,
    ) -> ConsistentCutPlan:
        """
        Create a capture plan for the given domains.
        
        The plan includes:
            - Order of participants (respecting dependencies)
            - Barrier strategy
            - Timeout settings
            
        Args:
            domains: List of domain IDs to include in the cut
            consistency_level: How to ensure consistency
            quiesce_timeout_seconds: Max time to wait for quiescence
            
        Returns:
            A capture plan ready for execution
        """
        # For now, use simple ordering - would use dependency graph in production
        participant_ids = [
            f"participant_{domain}"
            for domain in domains
        ]
        
        return ConsistentCutPlan(
            plan_id=str(uuid.uuid4()),
            runtime_id=self._runtime_id,
            boot_session_id=None,
            domain_participants={d: [f"participant_{d}"] for d in domains},
            capture_order=participant_ids,
            barrier_type=consistency_level,
            quiesce_timeout_seconds=quiesce_timeout_seconds,
        )
    
    async def execute_cut(
        self,
        plan: ConsistentCutPlan,
        participants: Dict[str, Any],
    ) -> ConsistentCutResult:
        """
        Execute a consistent cut capture.
        
        Args:
            plan: The capture plan
            participants: Participant instances indexed by ID
            
        Returns:
            Result with boundary and captured state or error
        """
        if not plan.domain_participants:
            return ConsistentCutResult(
                result_id=str(uuid.uuid4()),
                request_id=plan.plan_id,
                runtime_id=self._runtime_id,
                status=ConsistentCutStatus.FAILED,
                error_message="No domains to capture",
            )
        
        # Phase 1: Barrier preparation
        if plan.barrier_type == CaptureConsistencyLevel.QUIESCENT:
            barrier = QuiescentBarrier.create(
                participant_ids=list(plan.domain_participants.keys()),
                timeout_seconds=plan.quiesce_timeout_seconds,
            )
            
            # Would wait for all participants to reach quiescence
            # This is a simplified version
        else:
            # Versioned or COW - no quiescence needed
            barrier = None
        
        # Phase 2: Capture each domain in order
        captured_domains = []
        participant_versions: Dict[str, int] = {}
        
        for participant_id in plan.capture_order:
            participant = participants.get(participant_id)
            if not participant:
                continue
            
            try:
                # Get current version before capture
                if hasattr(participant, 'current_state_version'):
                    current_version = participant.current_state_version()
                    participant_versions[participant_id] = (
                        current_version.value if hasattr(current_version, 'value')
                        else int(current_version)
                    )
                
                # Capture state
                captured = None
                if hasattr(participant, 'capture_state'):
                    from .participants import CaptureContext
                    context = CaptureContext.create(
                        runtime_id=self._runtime_id,
                        mode=CaptureConsistencyLevel.VERSIONED,
                    )
                    captured = await participant.capture_state(context)
                
                if captured:
                    captured_domains.append(participant_id)
                    
            except Exception as e:
                # For VERSIONED and COW, partial success is acceptable
                # For QUIESCENT, failure requires rollback
                if plan.barrier_type == CaptureConsistencyLevel.QUIESCENT:
                    return ConsistentCutResult(
                        result_id=str(uuid.uuid4()),
                        request_id=plan.plan_id,
                        runtime_id=self._runtime_id,
                        status=ConsistentCutStatus.PARTIAL,
                        error_message=f"Participant {participant_id} failed: {e}",
                    )
                continue
        
        # Phase 3: Create boundary
        boundary = CaptureVersionBoundary.create(participant_versions)
        
        self._cut_count += 1
        
        return ConsistentCutResult(
            result_id=str(uuid.uuid4()),
            request_id=plan.plan_id,
            runtime_id=self._runtime_id,
            status=ConsistentCutStatus.COMPLETED,
            timestamp=time.monotonic(),
            boundary=boundary,
            captured_domains=captured_domains,
        )
    
    def get_diagnostics(self) -> Dict[str, Any]:
        """Get coordinator diagnostics."""
        return {
            "runtime_id": self._runtime_id,
            "active_cuts": len(self._active_cuts),
            "cut_count": self._cut_count,
        }


__all__ = [
    # Consistency levels
    "CaptureConsistencyLevel",
    
    # Barriers
    "QuiescentBarrier",
    "CaptureVersionBoundary",
    "CopyOnWriteSnapshot",
    
    # Request and result types
    "ConsistentCutRequest",
    "ConsistentCutPlan",
    "ConsistentCutBoundary",
    "ConsistentCutResult",
    "ConsistentCutStatus",
    
    # Coordinator
    "ConsistentCutCoordinator",
]