# Core Admission Infrastructure
# =============================

"""
Core admission infrastructure for Gordon runtime Phase 3.7.6-I.

Provides:
- Canonical AdmissionController (single authority)
- Immutable admission artifacts with deterministic decisions
- Explicit admission policies and gates
- Work acceptance/rejection with typed results
- Admission revocation support
- Multi-runtime isolation

Runtime Progression:
    Construction → Assembly → Activation → Readiness → Admission → Operational

Admission Gates (evaluated in order):
    1. Runtime readiness gate
    2. Operational state gate  
    3. Capability availability gate
    4. Resource capacity gate
    5. Queue pressure gate
    6. Deadline feasibility gate
    7. Caller authority gate
    8. Maintenance/recovery/shutdown gates
"""

from dataclasses import dataclass, field
from typing import Dict, List, Tuple, Optional, Any, Callable
from enum import Enum, auto
import uuid
import time
import threading


# =============================================================================
# ADMISSION STATUS VALUES
# =============================================================================

class AdmissionStatus(Enum):
    """
    Canonical admission status values.
    
    These are the authoritative states - NOT a Boolean!
    
    Transitions:
        CLOSED → OPEN (after readiness passes)
        OPEN → RESTRICTED (under pressure)
        OPEN/CLOSED/RESTRICTED → REVOKED (on failure)
        
    A runtime may be READY while admission remains closed for:
        - Maintenance
        - Operator policy
        - Resource pressure
        - Shutdown preparation
    """
    # Base states
    CLOSED = "closed"           # Initial state, no work accepted
    EVALUATING = "evaluating"   # Evaluating admission request
    OPEN = "open"               # Work is being accepted
    RESTRICTED = "restricted"   # Accepting only certain work
    
    # Terminal/transition states
    DRAINING = "draining"       # Closing but draining existing work
    REVOKED = "revoked"         # Was open, now revoked
    TERMINATED = "terminated"   # Permanently closed


# =============================================================================
# ADMISSION DECISION VALUES
# =============================================================================

class AdmissionDecision(Enum):
    """
    Typed admission decisions.
    
    Each decision includes detailed reason and guidance.
    """
    # Positive decisions
    ACCEPT = "accept"                     # Work accepted for scheduling
    ACCEPT_RESTRICTED = "accept_restricted"  # Accepted with restrictions
    ACCEPT_DEFERRED = "accept_deferred"   # Accepted but delayed
    
    # Negative decisions - retryable
    REJECT_RETRYABLE = "reject_retryable"     # Try again later
    REJECT_TEMPORARY = "reject_temporary"     # Temporary rejection
    
    # Negative decisions - final
    REJECT_FINAL = "reject_final"             # Never accept this work
    REJECT_NOT_READY = "reject_not_ready"     # Runtime not ready
    REJECT_CAPABILITY_MISSING = "reject_capability_missing"
    REJECT_CAPACITY = "reject_capacity"       # Queue full, no resources
    REJECT_MAINTENANCE = "reject_maintenance"
    REJECT_RECOVERY = "reject_recovery"
    REJECT_SHUTDOWN = "reject_shutdown"
    REJECT_UNAUTHORIZED = "reject_unauthorized"
    REJECT_INVALID = "reject_invalid"
    REJECT_STALE_RECEIPT = "reject_stale_receipt"


# =============================================================================
# ADMISSION GATE TYPES
# =============================================================================

class AdmissionGate(Enum):
    """
    Admission gates evaluated in order.
    
    Gates execute deterministically and must each pass for admission.
    """
    # Core gates (evaluated first)
    READINESS_GATE = "readiness"          # Runtime ready for this class?
    OPERATIONAL_GATE = "operational"      # Operational mode permits work?
    
    # Capability gates
    CAPABILITY_GATE = "capability"        # Required capabilities available?
    
    # Resource gates  
    RESOURCE_GATE = "resource"            # Sufficient resources available?
    QUEUE_CAPACITY_GATE = "queue_capacity"# Queue can accept more work?
    
    # Timing gates
    DEADLINE_GATE = "deadline"            # Can deadline be met?
    
    # Authority gates
    AUTHORITY_GATE = "authority"          # Caller authorized to submit work?
    
    # Special state gates
    MAINTENANCE_GATE = "maintenance"      # Maintenance mode active?
    RECOVERY_GATE = "recovery"            # Recovery in progress?
    SHUTDOWN_GATE = "shutdown"            # Shutdown pending or in progress?


# =============================================================================
# ADMISSION REQUEST
# =============================================================================

@dataclass(frozen=True)
class AdmissionRequest:
    """
    Immutable request for work admission.
    
    This is the INPUT contract - everything needed to evaluate whether
    a piece of work may enter the runtime system.
    """
    request_id: str                     # Unique ID for this request
    
    runtime_id: str                     # Which runtime is evaluating
    boot_session_id: str                # Boot session context
    
    operation_id: str                   # What operation is being requested
    caller_identity: str                # Who is submitting the work
    
    # Work characteristics
    work_kind: str                      # e.g., "normal", "high_cost", "external"
    required_capabilities: Tuple[str, ...]  # Capabilities needed
    required_readiness_class: str       # Which readiness class applies
    
    # Resource requirements
    resource_requirements: Dict[str, float] = field(default_factory=dict)  # resource -> amount
    estimated_duration_seconds: float = 0.0
    
    # Timing constraints
    deadline_utc: float = field(default_factory=lambda: time.time() + 60.0)
    
    # Meta
    priority: int = 0                   # Higher = more urgent
    idempotency_key: Optional[str] = None
    security_context_reference: Dict[str, Any] = field(default_factory=dict)
    
    correlation_id: Optional[str] = None
    causation_id: Optional[str] = None
    
    provenance: Dict[str, Any] = field(default_factory=dict)
    
    @property
    def is_expired(self) -> bool:
        """Check if request has passed its deadline."""
        return time.time() > self.deadline_utc


# =============================================================================
# ADMISSION GATE RESULT
# =============================================================================

@dataclass(frozen=True)
class AdmissionGateResult:
    """
    Result of evaluating one admission gate.
    
    Gates execute in order - failure at any gate rejects the request.
    """
    gate_id: str                        # Which gate evaluated
    gate_type: AdmissionGate
    
    passed: bool = False                # Did it pass?
    status: "GateStatus" = None  # Will be set by enum (forward ref handled)
    reason: str = ""                    # Why did it pass/fail?
    diagnostics: Tuple[str, ...] = field(default_factory=tuple)
    
    blocking: bool = True               # Does failure block admission?
    
    evaluated_at_utc: float = field(default_factory=time.time)
    
    @classmethod
    def passed(cls, gate_type: AdmissionGate) -> "AdmissionGateResult":
        return cls(
            gate_id=gate_type.value,
            gate_type=gate_type,
            passed=True,
            status=None  # Set by caller or default
        )
    
    @classmethod
    def failed(cls, gate_type: AdmissionGate, reason: str) -> "AdmissionGateResult":
        return cls(
            gate_id=gate_type.value,
            gate_type=gate_type,
            passed=False,
            status=None,
            reason=reason
        )
    
    @classmethod
    def unknown(cls, gate_type: AdmissionGate) -> "AdmissionGateResult":
        return cls(
            gate_id=gate_type.value,
            gate_type=gate_type,
            passed=False,
            status=None,
            reason="Insufficient information"
        )


class GateStatus(Enum):
    """Status of an admission gate evaluation."""
    PASSED = "passed"
    FAILED = "failed"
    UNKNOWN = "unknown"


# =============================================================================
# ADMISSION DECISION AND REJECTION
# =============================================================================

@dataclass(frozen=True)
class AdmissionDecisionRecord:
    """
    Immutable decision record for work admission.
    
    This is the OUTPUT - typed, complete, and immutable.
    """
    request_id: str
    runtime_id: str
    
    decision: AdmissionDecision         # The actual decision
    reason: str                         # Human-readable explanation
    
    blockers: Tuple[str, ...]           # What's blocking?
    warnings: Tuple[str, ...] = field(default_factory=tuple)
    
    # Gate results
    gate_results: Tuple[AdmissionGateResult, ...] = field(default_factory=tuple)
    
    # Context at time of decision
    readiness_snapshot_version: int = 0
    operational_state_version: int = 0
    admission_policy_version: int = 1
    
    evaluated_at_utc: float = field(default_factory=time.time)
    logical_sequence: int = 0
    provenance: Dict[str, Any] = field(default_factory=dict)
    
    @property
    def accepted(self) -> bool:
        """Check if work was accepted."""
        return self.decision in (
            AdmissionDecision.ACCEPT,
            AdmissionDecision.ACCEPT_RESTRICTED,
            AdmissionDecision.ACCEPT_DEFERRED
        )
    
    @property
    def retryable(self) -> bool:
        """Check if work can be retried."""
        return self.decision in (
            AdmissionDecision.REJECT_RETRYABLE,
            AdmissionDecision.REJECT_TEMPORARY,
            AdmissionDecision.ACCEPT_DEFERRED
        )
    
    @property
    def is_final_rejection(self) -> bool:
        """Check if this is a final rejection with no retry."""
        return self.decision in (
            AdmissionDecision.REJECT_FINAL,
            AdmissionDecision.REJECT_NOT_READY,
            AdmissionDecision.REJECT_CAPABILITY_MISSING,
            AdmissionDecision.REJECT_UNAUTHORIZED,
            AdmissionDecision.REJECT_INVALID,
            AdmissionDecision.REJECT_STALE_RECEIPT
        )


@dataclass(frozen=True)
class AdmissionRejection:
    """
    Immutable rejection record with full details.
    
    Used when admission is denied - provides actionable feedback to submitter.
    """
    request_id: str
    runtime_id: str
    
    decision: AdmissionDecision
    reason: str
    diagnostics: Tuple[str, ...] = field(default_factory=tuple)
    
    suggested_retry_utc: Optional[float] = None  # When to retry (if known)
    
    missing_capability: Optional[str] = None      # If capability issue
    readiness_blocker: Optional[str] = None       # If readiness issue
    capacity_blocker: Optional[str] = None        # If resource issue
    
    maintenance_status: bool = False
    recovery_status: bool = False
    shutdown_status: bool = False
    
    policy_reference: str = ""
    diagnostics_reference: str = ""
    
    evaluated_at_utc: float = field(default_factory=time.time)


# =============================================================================
# ADMISSION RECEIPT (for accepted work)
# =============================================================================

@dataclass(frozen=True)
class AdmissionReceipt:
    """
    Immutable receipt for accepted work.
    
    This binds admission authorization to the actual work submission.
    A stale receipt must be rejected - admission is not permanent!
    """
    request_id: str
    runtime_id: str
    
    # Decision binding
    decision_record: AdmissionDecisionRecord  # The authorization
    
    # Validity window
    issued_at_utc: float = field(default_factory=time.time)
    expires_at_utc: float = field(default_factory=lambda: time.time() + 30.0)
    
    # Runtime state at issue
    readiness_version: int = 0
    operational_state_version: int = 0
    
    @property
    def is_valid(self) -> bool:
        """Check if receipt has not expired."""
        return time.time() <= self.expires_at_utc
    
    @property
    def is_stale(self) -> bool:
        """Check if receipt is past its validity window."""
        return time.time() > self.expires_at_utc


# =============================================================================
# ADMISSION POLICY
# =============================================================================

@dataclass(frozen=True)
class AdmissionPolicy:
    """
    Immutable admission policy configuration.
    
    This determines how admission decisions are made.
    """
    requires_readiness: bool = True         # Must runtime be ready?
    max_queue_depth: int = 1000             # Max tasks in queue
    maintenance_mode: bool = False          # Maintenance mode active?
    
    # Gate ordering (deterministic)
    gate_order: Tuple[AdmissionGate, ...] = field(default_factory=lambda: (
        AdmissionGate.READINESS_GATE,
        AdmissionGate.OPERATIONAL_GATE,
        AdmissionGate.CAPABILITY_GATE,
        AdmissionGate.RESOURCE_GATE,
        AdmissionGate.QUEUE_CAPACITY_GATE,
        AdmissionGate.DEADLINE_GATE,
        AdmissionGate.AUTHORITY_GATE,
        AdmissionGate.MAINTENANCE_GATE,
        AdmissionGate.RECOVERY_GATE,
        AdmissionGate.SHUTDOWN_GATE
    ))
    
    # Timing
    default_receipt_lifetime_seconds: float = 30.0
    
    # Delegation
    can_delegate_admission: bool = False    # Allow other authorities?
    
    def should_evaluate_gate(self, gate_type: AdmissionGate) -> bool:
        """Check if a particular gate should be evaluated."""
        return gate_type in self.gate_order


# =============================================================================
# ADMISSION REVOCATION
# =============================================================================

@dataclass(frozen=True)
class AdmissionRevocationRequest:
    """Request to revoke current admission authority."""
    runtime_id: str
    reason: str
    revocation_type: "AdmissionRevocationType"
    timestamp_utc: float = field(default_factory=time.time)


class AdmissionRevocationType(Enum):
    """Types of admission revocation."""
    READINESS_LOST = "readiness_lost"           # Runtime became not ready
    OPERATIONAL_STATE_CHANGE = "operational_state_change"  # Operational mode changed
    RESOURCE_PRESSURE = "resource_pressure"     # Too much work queued
    MAINTENANCE_START = "maintenance_start"
    RECOVERY_START = "recovery_start"
    SHUTDOWN_REQUEST = "shutdown_request"


@dataclass(frozen=True)
class AdmissionRevocationDecision:
    """Decision to revoke admission authority."""
    runtime_id: str
    request_id: str
    
    status_before: AdmissionStatus
    status_after: AdmissionStatus
    
    reason: str
    revocation_type: AdmissionRevocationType
    
    timestamp_utc: float = field(default_factory=time.time)
    
    @property
    def success(self) -> bool:
        """Check if revocation was successful."""
        return self.status_before != AdmissionStatus.REVOKED


# =============================================================================
# ADMISSION CONTROLLER (CANONICAL AUTHORITY)
# =============================================================================

class AdmissionController:
    """
    Canonical authority for work admission decisions.
    
    This is THE ONE source of truth for whether work may enter the runtime.
    It owns:
    
    - Admission state
    - Policy evaluation
    - Gate execution (in deterministic order!)
    - Decision production
    - Receipt issuance and validation
    - Revocation handling
    
    No queue, scheduler, executor, API, plugin, or subsystem may independently
    admit normal production work.
    """
    
    def __init__(
        self,
        runtime_id: str,
        policy: Optional[AdmissionPolicy] = None
    ) -> None:
        """Initialize with runtime-scoped state."""
        self._runtime_id = runtime_id
        self._boot_session_id = str(uuid.uuid4())
        
        # State management
        self._lock = threading.Lock()
        self._status = AdmissionStatus.CLOSED  # Start closed
        self._state_version = 0
        
        # Policy
        self._policy = policy or AdmissionPolicy()
        
        # Receipt store (bounded)
        self._receipts: Dict[str, AdmissionReceipt] = {}
        self._max_receipts = 10000
        
        # Decision counter for sequence numbers
        self._decision_sequence = 0
        
        # Gate evaluators
        self._gate_evaluators: Dict[AdmissionGate, Callable[[str], bool]] = {
            AdmissionGate.READINESS_GATE: lambda rid: False,  # Will be set by caller
            AdmissionGate.OPERATIONAL_GATE: lambda rid: False,
            AdmissionGate.CAPABILITY_GATE: lambda rid: True,
            AdmissionGate.RESOURCE_GATE: lambda rid: True,
            AdmissionGate.QUEUE_CAPACITY_GATE: lambda rid: True,
            AdmissionGate.DEADLINE_GATE: lambda rid: True,
            AdmissionGate.AUTHORITY_GATE: lambda rid: True,
            AdmissionGate.MAINTENANCE_GATE: lambda rid: self._policy.maintenance_mode,
            AdmissionGate.RECOVERY_GATE: lambda rid: False,
            AdmissionGate.SHUTDOWN_GATE: lambda rid: False
        }
        
        # Event log (bounded)
        self._events: List[Dict[str, Any]] = []
        self._max_events = 1000
    
    @property
    def runtime_id(self) -> str:
        """Get the runtime ID this controller serves."""
        return self._runtime_id
    
    @property
    def boot_session_id(self) -> str:
        """Get the current boot session ID."""
        return self._boot_session_id
    
    @property
    def state_version(self) -> int:
        """Get current state version for synchronization."""
        with self._lock:
            return self._state_version
    
    @property
    def admission_status(self) -> AdmissionStatus:
        """Get current admission status."""
        with self._lock:
            return self._status
    
    # -------------------------------------------------------------------------
    # Policy Management (for runtime configuration)
    # -------------------------------------------------------------------------
    
    def set_policy(self, policy: AdmissionPolicy) -> None:
        """Update the admission policy."""
        with self._lock:
            self._policy = policy
            self._state_version += 1
    
    def set_gate_evaluator(
        self,
        gate_type: AdmissionGate,
        evaluator: Callable[[str], bool]
    ) -> None:
        """
        Register a gate evaluator function.
        
        The evaluator receives runtime_id and returns True if the gate passes.
        """
        with self._lock:
            self._gate_evaluators[gate_type] = evaluator
    
    # -------------------------------------------------------------------------
    # Admission State Management
    # -------------------------------------------------------------------------
    
    def open_admission(self) -> bool:
        """
        Open admission to accept work.
        
        Does NOT check readiness! That's the caller's responsibility.
        
        Returns:
            True if admission was opened, False if in terminal state
        """
        with self._lock:
            if self._status in (
                AdmissionStatus.TERMINATED,
                AdmissionStatus.REVOKED
            ):
                return False
            
            old_status = self._status
            self._status = AdmissionStatus.OPEN
            self._state_version += 1
            
            self._record_event("admission_opened", {
                "old_status": old_status.value,
                "new_status": self._status.value
            })
            
            return True
    
    def close_admission(self, reason: str = "") -> None:
        """
        Close admission to reject new work.
        
        Does NOT affect existing accepted work.
        """
        with self._lock:
            old_status = self._status
            
            # Only transition if not already in terminal state
            if old_status in (AdmissionStatus.TERMINATED, AdmissionStatus.REVOKED):
                return
            
            self._status = AdmissionStatus.CLOSED
            self._state_version += 1
            
            self._record_event("admission_closed", {
                "reason": reason,
                "old_status": old_status.value,
                "new_status": self._status.value
            })
    
    async def close_admission_on_revocation(
        self,
        reason: str = "",
        revocation_type: Optional[Any] = None
    ) -> None:
        """
        Close admission due to readiness revocation or other external trigger.
        
        This is called by the ReadinessController when readiness is revoked.
        It transitions through DRAINING state if currently OPEN.
        """
        with self._lock:
            old_status = self._status
            
            # Only transition if not already in terminal state
            if old_status in (AdmissionStatus.TERMINATED, AdmissionStatus.REVOKED):
                return
            
            # If OPEN, transition to DRAINING; otherwise close immediately
            if old_status == AdmissionStatus.OPEN:
                new_status = AdmissionStatus.DRAINING
            else:
                new_status = AdmissionStatus.CLOSED
            
            self._status = new_status
            self._state_version += 1
            
            revocation_type_str = revocation_type.value if hasattr(revocation_type, 'value') else str(revocation_type)
            
            self._record_event("admission_revoked_on_readiness", {
                "reason": reason,
                "revocation_type": revocation_type_str,
                "old_status": old_status.value,
                "new_status": new_status.value
            })
    
    def revoke_admission(self, reason: str = "") -> Optional[AdmissionRevocationDecision]:
        """
        Revoke current admission authority.
        
        Called when conditions change (readiness lost, shutdown requested, etc.)
        """
        with self._lock:
            old_status = self._status
            
            # Check if revocation needed
            if old_status in (AdmissionStatus.REVOKED, AdmissionStatus.TERMINATED):
                return None
            
            # Transition through intermediate states
            if old_status == AdmissionStatus.OPEN:
                new_status = AdmissionStatus.DRAINING
            else:
                new_status = AdmissionStatus.CLOSED
            
            self._status = new_status
            
            decision = AdmissionRevocationDecision(
                runtime_id=self._runtime_id,
                request_id=str(uuid.uuid4()),
                status_before=old_status,
                status_after=new_status,
                reason=reason,
                revocation_type=AdmissionRevocationType.READINESS_LOST
            )
            
            self._state_version += 1
            
            self._record_event("admission_revoked", {
                "decision": decision.to_dict() if hasattr(decision, 'to_dict') else str(decision)
            })
            
            return decision
    
    def terminate_admission(self) -> None:
        """Permanently terminate admission (cannot be reopened)."""
        with self._lock:
            old_status = self._status
            self._status = AdmissionStatus.TERMINATED
            self._state_version += 1
            
            self._record_event("admission_terminated", {
                "old_status": old_status.value,
                "new_status": self._status.value
            })
    
    # -------------------------------------------------------------------------
    # Gate Evaluation (deterministic order)
    # -------------------------------------------------------------------------
    
    async def evaluate_gates(
        self,
        request: AdmissionRequest
    ) -> Tuple[bool, Tuple[AdmissionGateResult, ...]]:
        """
        Evaluate all gates in deterministic order.
        
        Returns:
            Tuple of (all_passed, gate_results)
        """
        results: List[AdmissionGateResult] = []
        
        for gate_type in self._policy.gate_order:
            evaluator = self._gate_evaluators.get(gate_type)
            
            if not evaluator:
                # Missing evaluator - treat as unknown
                results.append(AdmissionGateResult.unknown(gate_type))
                continue
            
            try:
                passed = evaluator(self._runtime_id)
                
                if passed:
                    results.append(AdmissionGateResult.passed(gate_type))
                else:
                    results.append(AdmissionGateResult.failed(
                        gate_type,
                        f"Gate {gate_type.value} failed"
                    ))
                    
            except Exception as e:
                results.append(AdmissionGateResult.unknown(gate_type))
        
        all_passed = all(r.passed for r in results)
        
        return all_passed, tuple(results)
    
    # -------------------------------------------------------------------------
    # Work Admission (main entry point)
    # -------------------------------------------------------------------------
    
    async def evaluate_admission(
        self,
        request: AdmissionRequest
    ) -> AdmissionDecisionRecord:
        """
        Evaluate and decide on a work admission request.
        
        This is the canonical method. It:
        1. Validates request (not expired, valid format)
        2. Evaluates all gates in order
        3. Produces typed decision with full context
        
        Args:
            request: The admission request to evaluate
            
        Returns:
            AdmissionDecisionRecord with decision and diagnostics
            
        Raises:
            ValueError: If request is invalid or expired
        """
        # Validate request not expired
        if request.is_expired:
            raise ValueError("Admission request has expired")
        
        evaluation_id = str(uuid.uuid4())
        
        # Evaluate gates
        gates_passed, gate_results = await self.evaluate_gates(request)
        
        # Build decision
        with self._lock:
            self._decision_sequence += 1
            
            if not gates_passed:
                # Find first failing gate for primary reason
                failed_gates = [r for r in gate_results if not r.passed]
                
                # Determine rejection type based on first failure
                first_failure = failed_gates[0] if failed_gates else None
                
                if first_failure and "readiness" in first_failure.gate_type.value:
                    decision = AdmissionDecision.REJECT_NOT_READY
                elif self._policy.maintenance_mode:
                    decision = AdmissionDecision.REJECT_MAINTENANCE
                elif first_failure and "capability" in first_failure.gate_type.value:
                    decision = AdmissionDecision.REJECT_CAPABILITY_MISSING
                else:
                    decision = AdmissionDecision.REJECT_RETRYABLE
                
                blockers = tuple(r.reason for r in failed_gates) if failed_gates else ()
                
                return AdmissionDecisionRecord(
                    request_id=request.request_id,
                    runtime_id=self._runtime_id,
                    decision=decision,
                    reason=f"Admission gate {first_failure.gate_type.value if first_failure else 'unknown'} failed",
                    blockers=blockers,
                    gate_results=gate_results,
                    logical_sequence=self._decision_sequence,
                    readiness_snapshot_version=0,  # Would come from ReadinessController
                    operational_state_version=self.state_version
                )
            
            # All gates passed - accept
            receipt = self._issue_receipt(request)
            
            return AdmissionDecisionRecord(
                request_id=request.request_id,
                runtime_id=self._runtime_id,
                decision=AdmissionDecision.ACCEPT,
                reason="All admission gates passed",
                gate_results=gate_results,
                logical_sequence=self._decision_sequence,
                readiness_snapshot_version=0,  # Would come from ReadinessController
                operational_state_version=self.state_version,
                provenance={"receipt_id": receipt.request_id}
            )
    
    def _issue_receipt(self, request: AdmissionRequest) -> AdmissionReceipt:
        """Issue an admission receipt for accepted work."""
        receipt = AdmissionReceipt(
            request_id=request.request_id,
            runtime_id=self._runtime_id,
            decision_record=None,  # Would be filled by caller
            issued_at_utc=time.time(),
            expires_at_utc=time.time() + self._policy.default_receipt_lifetime_seconds,
            readiness_version=0,
            operational_state_version=self.state_version
        )
        
        # Store receipt (bounded)
        if len(self._receipts) >= self._max_receipts:
            # Remove oldest
            keys = list(self._receipts.keys())
            del self._receipts[keys[0]]
        
        self._receipts[request.request_id] = receipt
        
        return receipt
    
    def validate_receipt(
        self,
        request_id: str,
        runtime_id: str,
        expected_state_version: int
    ) -> bool:
        """
        Validate that a submission has a valid admission receipt.
        
        Used by scheduler/executor to verify work was properly admitted.
        """
        with self._lock:
            receipt = self._receipts.get(request_id)
            
            if not receipt:
                return False
            
            # Check runtime ID matches
            if receipt.runtime_id != runtime_id:
                return False
            
            # Check receipt not stale
            if receipt.is_stale:
                return False
            
            # Check state hasn't changed since admission
            if expected_state_version > receipt.operational_state_version:
                return False
            
            return True
    
    # -------------------------------------------------------------------------
    # State Query
    # -------------------------------------------------------------------------
    
    def get_snapshot(self) -> "AdmissionSnapshot":
        """Get an immutable snapshot of current state."""
        with self._lock:
            return AdmissionSnapshot(
                runtime_id=self._runtime_id,
                boot_session_id=self._boot_session_id,
                status=self._status,
                state_version=self._state_version,
                decision_count=self._decision_sequence,
                receipt_count=len(self._receipts)
            )
    
    def _record_event(self, event_type: str, payload: Dict[str, Any]) -> None:
        """Record an admission event (bounded)."""
        self._events.append({
            "event_type": event_type,
            "timestamp_utc": time.time(),
            "payload": payload
        })
        
        if len(self._events) > self._max_events:
            self._events = self._events[-self._max_events:]


# =============================================================================
# ADMISSION SNAPSHOT
# =============================================================================

@dataclass(frozen=True)
class AdmissionSnapshot:
    """Immutable snapshot of admission state for observability."""
    runtime_id: str
    boot_session_id: str
    status: AdmissionStatus
    state_version: int
    decision_count: int
    receipt_count: int


# =============================================================================
# PUBLIC API EXPORTS
# =============================================================================

__all__ = [
    # Status and decisions
    "AdmissionStatus",
    "AdmissionDecision",
    
    # Gates
    "AdmissionGate",
    "GateStatus",
    "AdmissionGateResult",
    
    # Request and decision records
    "AdmissionRequest",
    "AdmissionDecisionRecord",
    "AdmissionRejection",
    "AdmissionReceipt",
    
    # Policy and revocation
    "AdmissionPolicy",
    "AdmissionRevocationRequest",
    "AdmissionRevocationType",
    "AdmissionRevocationDecision",
    
    # Controller (THE authority)
    "AdmissionController",
    
    # Snapshot
    "AdmissionSnapshot",
]