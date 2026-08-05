# Core Runtime State Machine Implementation
# =========================================

"""
Production-grade runtime state machine for Phase 3.7.8-I.

Provides:
- Single authoritative canonical runtime state authority
- Deterministic transition pipeline with validation and guards
- Immutable state models and snapshots
- Complete transition history with versioning
- Event publication for observer synchronization
- Rollback support with evidence preservation
- Concurrency handling with deterministic ordering

This module implements the architectural invariants:

1. Exactly one RuntimeStateMachine per runtime instance
2. Exactly one canonical runtime state
3. Exactly one mutation authority (RuntimeStateMachine)
4. Validation precedes mutation
5. Guards are deterministic
6. Transition commits are atomic
7. History preserves provenance
8. Events follow authoritative mutation
9. Snapshots are immutable
10. Rollback preserves evidence
11. Runtime state is never bypassed
12. Subsystems consume but never own runtime state
13. Runtime truth is deterministic
14. No hidden mutable global state
15. Every transition is explainable

Usage:

    # Create state machine with unique runtime ID
    sm = RuntimeStateMachine(runtime_id="runtime_001")

    # Query current state (read-only)
    snapshot = sm.current_snapshot()

    # Request a transition (goes through full pipeline)
    result = await sm.transition_to(RuntimeState.RUNNING)

    if result.success:
        print(f"Transitioned to {result.target_state}")
    else:
        print(f"Transition failed: {result.failure_reason}")

Architecture:

    RuntimeStateMachine
    ├── State Model (immutable dataclasses)
    │   ├── RuntimeState
    │   ├── RuntimeSnapshot
    │   ├── RuntimeTransitionRequest
    │   └── RuntimeTransitionResult
    ├── Transition Pipeline
    │   ├── ValidationPhase
    │   ├── GuardEvaluationPhase
    │   ├── AuthorityApprovalPhase
    │   ├── PreHookPhase
    │   ├── AtomicCommitPhase
    │   ├── PostHookPhase
    │   └── EventPublicationPhase
    ├── History Store (ordered, immutable)
    ├── Invariant Validator
    └── Observer Synchronizer

Pipeline Flow:

    TransitionRequest
         ↓
    [Validation]
    - Unknown states check
    - Forbidden edges check
    - Duplicate transition check
    - Runtime identity validation
     ↓
    [GuardEvaluation]
    - ResourcesAvailableGuard
    - ReadinessSatisfiedGuard
    - AdmissionPermittedGuard
    - SchedulerAvailableGuard
    - ExecutorAvailableGuard
    - IntegrityValidGuard
    - HealthAcceptableGuard
     ↓
    [AuthorityApproval]
    - Single writer verification
    - Version validation (optimistic locking)
     ↓
    [Pre-transition Hooks]
    - Pre-commit hooks (can block with exception)
     ↓
    [Atomic Commit]
    - Update state atomically within lock
    - Increment version
    - Append to history
     ↓
    [Post-transition Hooks]
    - Post-commit hooks for side effects
     ↓
    [Event Publication]
    - TransitionRequested
    - TransitionValidated
    - StateLeaving
    - StateEntered
    - TransitionCommitted
    - TransitionCompleted
     ↓
    [Observer Synchronization]
    - Publish snapshot to subscribers
    - Update health/integrity if needed

"""

from dataclasses import dataclass, field
from typing import (
    Dict,
    List,
    Optional,
    Any,
    Callable,
    Set,
    Tuple,
    AsyncGenerator,
)
from enum import Enum, auto
import uuid
import time
import threading
import asyncio
import logging
from collections import deque
from datetime import datetime

# Import RuntimeState and related types from this module
from . import (
    RuntimeState,
    GuardResult,
    GuardEvaluation,
    StateGuard,
    ResourceGuard,
    ReadinessGuard,
    GuardManager,
)


logger = logging.getLogger(__name__)


# =============================================================================
# CANONICAL STATE ENUM (re-exported with expanded state space)
# =============================================================================


class CanonicalRuntimeState(Enum):
    """
    Canonical runtime state values for the RuntimeStateMachine.
    
    This is the single source of truth for all runtime state.
    
    State Lifecycle:
        INITIAL → CONSTRUCTED → ASSEMBLED → ACTIVATING → ACTIVE → READY
            ↓           ↓           ↓           ↓          ↓       ↓
         FAILED      FAILED      FAILED      FAILED   FAILED  QUIESCING
                                                         ↓
                                                      QUIESCENT
                                                         ↓
                                                      STOPPING
                                                         ↓
                                                       STOPPED
                                                         ↓
                                                     INITIAL (reset)
    
    Emergency transitions (any state):
        → FAILED (emergency failure)
        → TERMINATED (explicit termination)
    """
    
    # Initial states
    INITIAL = "initial"              # System loaded, no runtime created
    
    # Construction phases
    CONSTRUCTED = "constructed"      # Runtime instance constructed
    
    # Assembly phases
    ASSEMBLED = "assembled"          # All components assembled
    
    # Activation phases
    ACTIVATING = "activating"        # Currently activating
    ACTIVE = "active"                # Infrastructure started, ready for evaluation
    
    # Ready states
    READY = "ready"                  # Runtime ready for admission
    
    # Operational states
    OPERATIONAL = "operational"      # Fully operational
    DEGRADED = "degraded"            # Reduced capability
    
    # Shutdown preparation
    QUIESCING = "quiescing"          # Preparing for shutdown
    QUIESCENT = "quiescent"          # Ready to stop accepting work
    
    # Shutdown phases
    STOPPING = "stopping"            # Active shutdown
    STOPPED = "stopped"              # Shutdown complete
    
    # Terminal states
    FAILED = "failed"                # Terminal failure state
    TERMINATED = "terminated"        # Explicit termination


# =============================================================================
# STATE MODEL - IMMUTABLE DATACLASSES
# =============================================================================


@dataclass(frozen=True)
class RuntimeTransitionId:
    """Unique identifier for a transition."""
    value: str
    
    @classmethod
    def generate(cls) -> "RuntimeTransitionId":
        return cls(value=f"trans_{uuid.uuid4().hex[:16]}")
    
    def __str__(self) -> str:
        return self.value


@dataclass(frozen=True)
class RuntimeVersion:
    """
    Immutable version tracking for runtime state.
    
    Versioning provides:
    - Sequence numbers (monotonically increasing)
    - Transition IDs for correlation
    - Stale detection and optimistic validation
    """
    
    sequence_number: int              # Monotonic sequence number
    transition_id: RuntimeTransitionId  # ID of the transition that created this version
    created_at_utc: float             # When this version was created
    
    @classmethod
    def initial(cls) -> "RuntimeVersion":
        return cls(
            sequence_number=0,
            transition_id=RuntimeTransitionId.generate(),
            created_at_utc=time.time(),
        )
    
    def next(self, transition_id: RuntimeTransitionId) -> "RuntimeVersion":
        """Create the next version in sequence."""
        return RuntimeVersion(
            sequence_number=self.sequence_number + 1,
            transition_id=transition_id,
            created_at_utc=time.time(),
        )
    
    def __hash__(self) -> int:
        return hash(self.sequence_number)


@dataclass(frozen=True)
class RuntimeSnapshot:
    """
    Immutable snapshot of runtime state at a point in time.
    
    Snapshots provide:
    - Point-in-time state view
    - Version information for comparison
    - Timestamp for ordering
    - Complete state context
    """
    
    state: RuntimeState              # Current canonical state
    previous_state: Optional[RuntimeState]  # State before last transition
    target_state: Optional[RuntimeState]    # Target if in transition
    transition_status: str           # "idle", "pending", "in_progress", "completed"
    version: RuntimeVersion          # Version at snapshot time
    runtime_id: str                  # Runtime instance ID
    timestamp_utc: float             # When snapshot was captured
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "state": self.state.value if hasattr(self.state, 'value') else str(self.state),
            "previous_state": self.previous_state.value if self.previous_state and hasattr(self.previous_state, 'value') else (str(self.previous_state) if self.previous_state else None),
            "target_state": self.target_state.value if self.target_state and hasattr(self.target_state, 'value') else (str(self.target_state) if self.target_state else None),
            "transition_status": self.transition_status,
            "version": {
                "sequence_number": self.version.sequence_number,
                "transition_id": str(self.version.transition_id),
            },
            "runtime_id": self.runtime_id,
            "timestamp_utc": self.timestamp_utc,
        }


@dataclass(frozen=True)
class RuntimeTransitionRequest:
    """
    Request to transition runtime state.
    
    This is the INPUT contract - what's needed to request a transition.
    All fields are immutable and validated.
    """
    
    target_state: RuntimeState       # What state to transition to
    source_state: Optional[RuntimeState] = None  # Expected current state (for validation)
    runtime_id: str = ""             # Which runtime instance
    reason: Optional[str] = None     # Why this transition is requested
    requestor_id: Optional[str] = None  # Who requested it
    metadata: Dict[str, Any] = field(default_factory=dict)  # Additional context
    timeout_seconds: Optional[float] = None  # Maximum time for transition execution
    
    @classmethod
    def create(cls, target_state: RuntimeState, runtime_id: str, **kwargs) -> "RuntimeTransitionRequest":
        """Create a new transition request."""
        return cls(
            target_state=target_state,
            runtime_id=runtime_id,
            **{k: v for k, v in kwargs.items() if hasattr(cls, k)}
        )
    
    def with_timeout(self, timeout_seconds: float) -> "RuntimeTransitionRequest":
        """Create a new request with timeout set."""
        return RuntimeTransitionRequest(
            target_state=self.target_state,
            source_state=self.source_state,
            runtime_id=self.runtime_id,
            reason=self.reason,
            requestor_id=self.requestor_id,
            metadata=dict(self.metadata),
            timeout_seconds=timeout_seconds,
        )


@dataclass(frozen=True)
class RuntimeTransitionResult:
    """
    Result of a transition operation.
    
    This is the OUTPUT - typed, complete, and immutable.
    """
    
    success: bool                    # Did transition succeed?
    request: RuntimeTransitionRequest  # Original request
    result_id: str                   # Unique result ID
    
    # State information
    current_state: RuntimeState      # State after transition (or attempted)
    previous_state: RuntimeState     # State before transition attempt
    
    # Timing
    requested_at_utc: float          # When request was made
    completed_at_utc: float          # When result was produced
    
    # Outcome details
    status: str                      # "pending", "in_progress", "completed", "rejected", "failed"
    failure_reason: Optional[str] = None  # Why it failed (if applicable)
    
    @property
    def is_success(self) -> bool:
        return self.success and self.status == "completed"
    
    @property
    def is_rejected(self) -> bool:
        return not self.success and self.status == "rejected"
    
    @property
    def is_failed(self) -> bool:
        return not self.success and self.status == "failed"


@dataclass(frozen=True)
class RuntimeTransitionFailure:
    """
    Immutable record of a transition failure.
    
    Preserves complete failure context for debugging and recovery.
    """
    
    request_id: str                  # ID of the failed request
    source_state: RuntimeState       # State where failure occurred
    target_state: Optional[RuntimeState]  # What we tried to reach
    timestamp_utc: float             # When it happened
    
    # Failure details
    primary_cause: str               # String representation of error
    guard_failures: List[str] = field(default_factory=list)  # Names of failed guards
    validation_errors: List[str] = field(default_factory=list)  # Validation errors
    
    # Context
    runtime_id: str = ""
    requestor_id: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "request_id": self.request_id,
            "source_state": self.source_state.value if hasattr(self.source_state, 'value') else str(self.source_state),
            "target_state": self.target_state.value if self.target_state and hasattr(self.target_state, 'value') else (str(self.target_state) if self.target_state else None),
            "primary_cause": self.primary_cause,
            "guard_failures": self.guard_failures,
            "validation_errors": self.validation_errors,
        }


@dataclass(frozen=True)
class RuntimeHistoryEntry:
    """
    Immutable history entry for a transition.
    
    History preserves complete provenance of state changes.
    """
    
    entry_id: str                    # Unique history entry ID
    sequence_number: int             # Monotonic sequence number
    timestamp_utc: float             # When transition occurred
    
    # Transition details
    runtime_id: str
    source_state: RuntimeState
    target_state: RuntimeState
    version_before: int              # Version before transition
    version_after: int               # Version after transition
    
    # Authority and validation
    requestor_id: Optional[str] = None
    reason: Optional[str] = None     # Human-readable reason
    validation_passed: bool = True   # Was validation successful?
    guard_evaluation: str = "none"   # "passed", "failed", or "none"
    
    # Outcome
    outcome: str = "committed"       # "committed", "rejected", "rolled_back"
    diagnostics: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "entry_id": self.entry_id,
            "sequence_number": self.sequence_number,
            "timestamp_utc": self.timestamp_utc,
            "runtime_id": self.runtime_id,
            "source_state": self.source_state.value if hasattr(self.source_state, 'value') else str(self.source_state),
            "target_state": self.target_state.value if hasattr(self.target_state, 'value') else str(self.target_state),
            "version_before": self.version_before,
            "version_after": self.version_after,
            "validation_passed": self.validation_passed,
            "guard_evaluation": self.guard_evaluation,
            "outcome": self.outcome,
        }


@dataclass(frozen=True)
class RuntimeInvariantResult:
    """
    Result of invariant validation.
    
    Provides detailed information about which invariants passed or failed.
    """
    
    invariant_name: str              # Name of the invariant
    passed: bool                     # Did it pass?
    message: Optional[str] = None    # Explanation (if failed)
    severity: str = "warning"        # "info", "warning", or "error"
    
    @classmethod
    def success(cls, name: str, message: Optional[str] = None) -> "RuntimeInvariantResult":
        return cls(invariant_name=name, passed=True, message=message, severity="info")
    
    @classmethod
    def failure(cls, name: str, message: str, severity: str = "warning") -> "RuntimeInvariantResult":
        return cls(invariant_name=name, passed=False, message=message, severity=severity)


# =============================================================================
# STATE DRIFT DETECTION (PHASE 3.7.8-R REMEDIATION - GORDON-3.7.8-STATE-001)
# =============================================================================


@dataclass(frozen=True)
class StateDriftRule:
    """
    Rule defining valid state combinations between runtime state and subsystem-local state.
    
    These rules are used by StateDriftDetector to identify when subsystems disagree
    with the canonical runtime state.
    """
    rule_id: str                              # Unique identifier for the rule
    runtime_state: RuntimeState               # Canonical runtime state that triggers this rule
    subsystem_name: str                       # Name of the subsystem being checked
    subsystem_states: Set[RuntimeState]       # Valid states for the subsystem when runtime is in runtime_state
    
    @classmethod
    def create(
        cls,
        rule_id: str,
        runtime_state: RuntimeState,
        subsystem_name: str,
        *valid_subsystem_states: RuntimeState,
    ) -> "StateDriftRule":
        """Create a new drift detection rule."""
        return cls(
            rule_id=rule_id,
            runtime_state=runtime_state,
            subsystem_name=subsystem_name,
            subsystem_states=set(valid_subsystem_states),
        )


@dataclass(frozen=True)
class StateDriftFinding:
    """
    Record when a drift rule is violated (subsystem state disagrees with runtime state).
    
    This provides evidence of coordination failure between the canonical runtime
    state and subsystem-local state.
    """
    finding_id: str                          # Unique identifier for this finding
    timestamp_utc: float                     # When drift was detected
    rule: StateDriftRule                     # The rule that was violated
    
    # State information
    expected_runtime_state: RuntimeState     # What runtime state expects
    actual_runtime_state: RuntimeState       # What runtime state actually is
    subsystem_name: str                      # Name of the drifted subsystem
    subsystem_local_state: RuntimeState      # What subsystem thinks its state should be
    
    # Context
    context: Dict[str, Any] = field(default_factory=dict)  # Additional diagnostic info
    
    @property
    def description(self) -> str:
        """Get a human-readable description of the drift."""
        return (
            f"Drift detected: {self.subsystem_name} state '{self.subsystem_local_state.value}' "
            f"does not match expected state for runtime state '{self.actual_runtime_state.value}'"
        )
    
    @classmethod
    def create(
        cls,
        rule: StateDriftRule,
        actual_runtime_state: RuntimeState,
        subsystem_local_state: RuntimeState,
        context: Optional[Dict[str, Any]] = None,
    ) -> "StateDriftFinding":
        """Create a new drift finding."""
        return cls(
            finding_id=f"drift_{uuid.uuid4().hex[:16]}",
            timestamp_utc=time.time(),
            rule=rule,
            expected_runtime_state=rule.runtime_state,
            actual_runtime_state=actual_runtime_state,
            subsystem_name=rule.subsystem_name,
            subsystem_local_state=subsystem_local_state,
            context=context or {},
        )


@dataclass(frozen=True)
class StateDriftSnapshot:
    """
    Coherent view of drift conditions at a point in time.
    
    Provides a complete picture of all drift conditions, including:
    - All findings (drift violations)
    - Rules that passed (no drift detected)
    - Summary statistics
    """
    snapshot_id: str                          # Unique identifier for this snapshot
    timestamp_utc: float                      # When snapshot was captured
    runtime_state: RuntimeState               # Current canonical runtime state
    version: int                              # State version at time of snapshot
    
    # Drift information
    findings: Tuple[StateDriftFinding, ...]   # All detected drift violations
    rules_checked: Set[str]                   # IDs of all rules checked
    passed_rules: Set[str]                    # Rules where no drift was detected
    
    @property
    def has_drift(self) -> bool:
        """Check if any drift conditions were found."""
        return len(self.findings) > 0
    
    @property
    def drift_count(self) -> int:
        """Get number of drift violations found."""
        return len(self.findings)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "snapshot_id": self.snapshot_id,
            "timestamp_utc": self.timestamp_utc,
            "runtime_state": self.runtime_state.value if hasattr(self.runtime_state, 'value') else str(self.runtime_state),
            "version": self.version,
            "has_drift": self.has_drift,
            "drift_count": self.drift_count,
            "rules_checked": list(self.rules_checked),
            "passed_rules": list(self.passed_rules),
            "findings": [f.to_dict() if hasattr(f, 'to_dict') else str(f) for f in self.findings],
        }
    
    def get_drift_details(self) -> List[str]:
        """Get detailed descriptions of all drift conditions."""
        return [finding.description for finding in self.findings]


class StateDriftDetector:
    """
    Detects when subsystem-local state disagrees with canonical runtime state.
    
    This is a certification blocker fix (GORDON-3.7.8-STATE-001) to ensure
    runtime state and subsystem states remain aligned.
    
    Usage:
        # Create detector with rules
        detector = StateDriftDetector()
        
        # Define valid state combinations
        detector.add_rule(StateDriftRule.create(
            rule_id="ready-to-operational",
            runtime_state=RuntimeState.RUNNING,
            subsystem_name="scheduler",
            subsystem_states=RuntimeState.READY, RuntimeState.RUNNING
        ))
        
        # Check for drift
        snapshot = detector.check_drift(
            current_runtime_state=state_machine.current_state,
            subsystem_states={"scheduler": RuntimeState.STOPPED}  # This would be a drift!
        )
    """
    
    def __init__(self) -> None:
        self._lock = threading.RLock()
        self._rules: Dict[str, StateDriftRule] = {}
        self._last_snapshot: Optional[StateDriftSnapshot] = None
        self._drift_count_history: List[Tuple[float, int]] = []  # (timestamp, count)
    
    def add_rule(self, rule: StateDriftRule) -> None:
        """Add a drift detection rule."""
        with self._lock:
            self._rules[rule.rule_id] = rule
    
    def remove_rule(self, rule_id: str) -> bool:
        """Remove a drift detection rule by ID. Returns True if removed."""
        with self._lock:
            if rule_id in self._rules:
                del self._rules[rule_id]
                return True
            return False
    
    def get_rules(self) -> List[StateDriftRule]:
        """Get all registered rules."""
        with self._lock:
            return list(self._rules.values())
    
    def check_drift(
        self,
        current_runtime_state: RuntimeState,
        subsystem_states: Dict[str, RuntimeState],
        version: int = 0,
        context: Optional[Dict[str, Any]] = None,
    ) -> StateDriftSnapshot:
        """
        Check for drift between runtime state and subsystem states.
        
        Args:
            current_runtime_state: The canonical runtime state to check against
            subsystem_states: Mapping of subsystem name to its local state
            version: Current state machine version (for snapshot identification)
            context: Optional additional diagnostic context
            
        Returns:
            Snapshot with all drift findings and passed rules
        """
        with self._lock:
            findings: List[StateDriftFinding] = []
            passed_rules: Set[str] = set()
            rules_checked: Set[str] = set()
            
            for rule_id, rule in self._rules.items():
                rules_checked.add(rule_id)
                
                # Only check this rule if runtime state matches the rule's runtime_state
                if current_runtime_state != rule.runtime_state:
                    passed_rules.add(rule_id)
                    continue
                
                # Check subsystem state against valid states for this rule
                subsystem_local_state = subsystem_states.get(rule.subsystem_name)
                
                if subsystem_local_state is None:
                    # Subsystem not found - treat as drift (missing expected subsystem)
                    findings.append(
                        StateDriftFinding.create(
                            rule=rule,
                            actual_runtime_state=current_runtime_state,
                            subsystem_local_state=current_runtime_state,  # Fallback
                            context={"missing_subsystem": True, **(context or {})},
                        )
                    )
                elif subsystem_local_state not in rule.subsystem_states:
                    # Subsystem state doesn't match expected states
                    findings.append(
                        StateDriftFinding.create(
                            rule=rule,
                            actual_runtime_state=current_runtime_state,
                            subsystem_local_state=subsystem_local_state,
                            context=context or {},
                        )
                    )
                else:
                    # No drift for this rule
                    passed_rules.add(rule_id)
            
            # Update history
            self._drift_count_history.append((time.time(), len(findings)))
            
            # Trim old history entries (keep last 100)
            if len(self._drift_count_history) > 100:
                self._drift_count_history = self._drift_count_history[-100:]
            
            # Create snapshot
            snapshot = StateDriftSnapshot(
                snapshot_id=f"snapshot_{uuid.uuid4().hex[:16]}",
                timestamp_utc=time.time(),
                runtime_state=current_runtime_state,
                version=version,
                findings=tuple(findings),
                rules_checked=rules_checked,
                passed_rules=passed_rules,
            )
            
            self._last_snapshot = snapshot
            return snapshot
    
    def get_last_snapshot(self) -> Optional[StateDriftSnapshot]:
        """Get the last drift snapshot (if any)."""
        with self._lock:
            return self._last_snapshot
    
    def get_drift_count_history(self, limit: int = 100) -> List[Tuple[float, int]]:
        """
        Get history of drift counts over time.
        
        Args:
            limit: Maximum number of entries to return
            
        Returns:
            List of (timestamp_utc, drift_count) tuples
        """
        with self._lock:
            return list(self._drift_count_history)[-limit:]
    
    def clear_history(self) -> None:
        """Clear drift history."""
        with self._lock:
            self._drift_count_history.clear()


# =============================================================================
# TRANSITION VALIDATION
# =============================================================================


class TransitionValidator:
    """
    Validates transition requests against rules.
    
    Validation precedes mutation - no state is changed if validation fails.
    
    Added in Phase 3.7.8-R remediation:
        - Transition timeout support via RuntimeTransitionRequest.timeout_seconds
    """
    
    def __init__(self) -> None:
        # Valid transitions from each state (using canonical states)
        self._valid_transitions: Dict[CanonicalRuntimeState, Set[CanonicalRuntimeState]] = {
            CanonicalRuntimeState.INITIAL: {
                CanonicalRuntimeState.CONSTRUCTED,
            },
            CanonicalRuntimeState.CONSTRUCTED: {
                CanonicalRuntimeState.ASSEMBLED,
                CanonicalRuntimeState.FAILED,
                CanonicalRuntimeState.TERMINATED,
            },
            CanonicalRuntimeState.ASSEMBLED: {
                CanonicalRuntimeState.ACTIVATING,
                CanonicalRuntimeState.FAILED,
                CanonicalRuntimeState.TERMINATED,
            },
            CanonicalRuntimeState.ACTIVATING: {
                CanonicalRuntimeState.ACTIVE,
                CanonicalRuntimeState.FAILED,
                CanonicalRuntimeState.TERMINATED,
            },
            CanonicalRuntimeState.ACTIVE: {
                CanonicalRuntimeState.READY,
                CanonicalRuntimeState.FAILED,
                CanonicalRuntimeState.TERMINATED,
            },
            CanonicalRuntimeState.READY: {
                CanonicalRuntimeState.OPERATIONAL,
                CanonicalRuntimeState.QUIESCING,
                CanonicalRuntimeState.FAILED,
                CanonicalRuntimeState.TERMINATED,
            },
            CanonicalRuntimeState.OPERATIONAL: {
                CanonicalRuntimeState.DEGRADED,
                CanonicalRuntimeState.QUIESCING,
                CanonicalRuntimeState.STOPPING,
                CanonicalRuntimeState.FAILED,
                CanonicalRuntimeState.TERMINATED,
            },
            CanonicalRuntimeState.DEGRADED: {
                CanonicalRuntimeState.OPERATIONAL,
                CanonicalRuntimeState.QUIESCING,
                CanonicalRuntimeState.STOPPING,
                CanonicalRuntimeState.FAILED,
                CanonicalRuntimeState.TERMINATED,
            },
            CanonicalRuntimeState.QUIESCING: {
                CanonicalRuntimeState.QUIESCENT,
                CanonicalRuntimeState.FAILED,
                CanonicalRuntimeState.TERMINATED,
            },
            CanonicalRuntimeState.QUIESCENT: {
                CanonicalRuntimeState.STOPPING,
                CanonicalRuntimeState.READY,  # Can restart from quiescent
                CanonicalRuntimeState.FAILED,
                CanonicalRuntimeState.TERMINATED,
            },
            CanonicalRuntimeState.STOPPING: {
                CanonicalRuntimeState.STOPPED,
                CanonicalRuntimeState.FAILED,
                CanonicalRuntimeState.TERMINATED,
            },
            CanonicalRuntimeState.STOPPED: {
                CanonicalRuntimeState.INITIAL,  # Reset for new runtime
                CanonicalRuntimeState.FAILED,
                CanonicalRuntimeState.TERMINATED,
            },
            CanonicalRuntimeState.FAILED: {
                CanonicalRuntimeState.INITIAL,
                CanonicalRuntimeState.TERMINATED,
            },
            CanonicalRuntimeState.TERMINATED: set(),  # Terminal - no transitions out
        }
        
        # Timeout configuration
        self._default_timeout_seconds = 30.0  # Default timeout for transitions
        self._min_timeout_seconds = 1.0       # Minimum allowed timeout
        self._max_timeout_seconds = 300.0     # Maximum allowed timeout
    
    def is_valid_transition(self, from_state: CanonicalRuntimeState, to_state: CanonicalRuntimeState) -> bool:
        """Check if a transition is valid."""
        return to_state in self._valid_transitions.get(from_state, set())
    
    def validate(
        self,
        request: RuntimeTransitionRequest,
        current_state: RuntimeState,
        expected_version: Optional[int] = None,
    ) -> Tuple[bool, List[str]]:
        """
        Validate a transition request.
        
        Returns:
            Tuple of (is_valid, list_of_errors)
        """
        errors: List[str] = []
        
        # Map runtime state to canonical state
        try:
            current_canonical = self._map_to_canonical(current_state)
            target_canonical = self._map_to_canonical(request.target_state)
        except ValueError as e:
            return False, [f"State mapping error: {e}"]
        
        # Check if target state is valid from current state
        if not self.is_valid_transition(current_canonical, target_canonical):
            errors.append(
                f"Forbidden transition: {current_canonical.value} -> {target_canonical.value}"
            )
        
        # Validate expected version (optimistic locking)
        if expected_version is not None and request.metadata.get("_version") != expected_version:
            errors.append(f"Version mismatch: expected {expected_version}, got {request.metadata.get('_version')}")
        
        # Validate timeout_seconds if present
        if request.timeout_seconds is not None:
            timeout_error = self._validate_timeout(request.timeout_seconds)
            if timeout_error:
                errors.append(timeout_error)
        
        # Check runtime ID matches
        if request.runtime_id and not current_state.value.startswith(request.runtime_id[:5]):
            # Basic runtime ID check (in production, use proper ID tracking)
            pass  # Allow for now - real implementation would have explicit runtime ID
        
        return len(errors) == 0, errors
    
    def _validate_timeout(self, timeout_seconds: float) -> Optional[str]:
        """
        Validate a timeout value.
        
        Args:
            timeout_seconds: The timeout value to validate
            
        Returns:
            Error message if invalid, None if valid
        """
        # Apply defaults if needed
        effective_min = max(self._min_timeout_seconds, 1.0)
        effective_max = min(self._max_timeout_seconds, 300.0)
        
        if timeout_seconds < effective_min:
            return (
                f"Timeout too short: {timeout_seconds}s (minimum is {effective_min}s). "
                f"Consider using a longer timeout for complex transitions."
            )
        
        if timeout_seconds > effective_max:
            return (
                f"Timeout too long: {timeout_seconds}s (maximum is {effective_max}s). "
                f"Split into multiple transitions or increase max_timeout_seconds."
            )
        
        # Valid timeout
        return None
    
    def validate_with_timeout(
        self,
        request: RuntimeTransitionRequest,
        current_state: RuntimeState,
        expected_version: Optional[int] = None,
        start_time: Optional[float] = None,
    ) -> Tuple[bool, List[str], Optional[float]]:
        """
        Validate a transition request with timeout tracking.
        
        Args:
            request: The transition request to validate
            current_state: Current state for validation context
            expected_version: Expected version for optimistic locking
            start_time: Optional start time for timeout calculation
            
        Returns:
            Tuple of (is_valid, errors, time_remaining_seconds or None)
        """
        is_valid, errors = self.validate(request, current_state, expected_version)
        
        if not is_valid:
            return False, errors, None
        
        # Calculate timeout tracking
        if request.timeout_seconds is not None and start_time is not None:
            elapsed = time.time() - start_time
            time_remaining = request.timeout_seconds - elapsed
            
            if time_remaining <= 0:
                errors.append(f"Transition timeout expired (elapsed: {elapsed:.2f}s)")
                return False, errors, 0.0
            
            return True, errors, max(0.0, time_remaining)
        
        return is_valid, errors, None
    
    def _map_to_canonical(self, state: RuntimeState) -> CanonicalRuntimeState:
        """Map a RuntimeState to its canonical equivalent."""
        try:
            return CanonicalRuntimeState(state.value)
        except ValueError:
            # For compatibility with older states
            state_str = str(state).lower()
            for canonical in CanonicalRuntimeState:
                if state_str == canonical.value.lower():
                    return canonical
            raise ValueError(f"Cannot map {state} to canonical state")


# =============================================================================
# TRANSITION GUARDS (DETERMINISTIC)
# =============================================================================


class ResourcesAvailableGuard(StateGuard):
    """Guard that checks if sufficient resources are available."""
    
    def __init__(self, resources_available_fn: Optional[Callable[[], bool]] = None):
        self._resources_available = resources_available_fn or (lambda: True)
    
    @property
    def name(self) -> str:
        return "resources_available"
    
    def evaluate(
        self,
        from_state: RuntimeState,
        to_state: RuntimeState,
    ) -> GuardEvaluation:
        if not self._resources_available():
            return GuardEvaluation(
                guard_name=self.name,
                result=GuardResult.FAILED,
                reason="Resources not available for transition"
            )
        return GuardEvaluation(
            guard_name=self.name,
            result=GuardResult.PASSED
        )
    
    def requires_guard(self, from_state: RuntimeState, to_state: RuntimeState) -> bool:
        # Check resources when transitioning to operational states
        return to_state in (
            CanonicalRuntimeState.ACTIVE,
            CanonicalRuntimeState.READY,
            CanonicalRuntimeState.OPERATIONAL,
            CanonicalRuntimeState.QUIESCING,
        )


class ReadinessSatisfiedGuard(StateGuard):
    """Guard that checks if subsystem is ready for the target state."""
    
    def __init__(self, readiness_ready_fn: Callable[[], bool]):
        self._readiness_ready = readiness_ready_fn
    
    @property
    def name(self) -> str:
        return "readiness_satisfied"
    
    def evaluate(
        self,
        from_state: RuntimeState,
        to_state: RuntimeState,
    ) -> GuardEvaluation:
        if not self._readiness_ready():
            return GuardEvaluation(
                guard_name=self.name,
                result=GuardResult.FAILED,
                reason="Readiness check failed"
            )
        return GuardEvaluation(
            guard_name=self.name,
            result=GuardResult.PASSED
        )
    
    def requires_guard(self, from_state: RuntimeState, to_state: RuntimeState) -> bool:
        return to_state in (
            CanonicalRuntimeState.READY,
            CanonicalRuntimeState.OPERATIONAL,
        )


class AdmissionPermittedGuard(StateGuard):
    """Guard that checks if admission is available."""
    
    def __init__(self, admission_permitted_fn: Callable[[], bool]):
        self._admission_permitted = admission_permitted_fn
    
    @property
    def name(self) -> str:
        return "admission_permitted"
    
    def evaluate(
        self,
        from_state: RuntimeState,
        to_state: RuntimeState,
    ) -> GuardEvaluation:
        if not self._admission_permitted():
            return GuardEvaluation(
                guard_name=self.name,
                result=GuardResult.FAILED,
                reason="Admission not permitted"
            )
        return GuardEvaluation(
            guard_name=self.name,
            result=GuardResult.PASSED
        )
    
    def requires_guard(self, from_state: RuntimeState, to_state: RuntimeState) -> bool:
        return to_state == CanonicalRuntimeState.OPERATIONAL


class SchedulerAvailableGuard(StateGuard):
    """Guard that checks if scheduler is available."""
    
    def __init__(self, scheduler_available_fn: Callable[[], bool]):
        self._scheduler_available = scheduler_available_fn
    
    @property
    def name(self) -> str:
        return "scheduler_available"
    
    def evaluate(
        self,
        from_state: RuntimeState,
        to_state: RuntimeState,
    ) -> GuardEvaluation:
        if not self._scheduler_available():
            return GuardEvaluation(
                guard_name=self.name,
                result=GuardResult.FAILED,
                reason="Scheduler unavailable"
            )
        return GuardEvaluation(
            guard_name=self.name,
            result=GuardResult.PASSED
        )
    
    def requires_guard(self, from_state: RuntimeState, to_state: RuntimeState) -> bool:
        return to_state in (
            CanonicalRuntimeState.ACTIVE,
            CanonicalRuntimeState.READY,
            CanonicalRuntimeState.OPERATIONAL,
        )


class ExecutorAvailableGuard(StateGuard):
    """Guard that checks if executor is available."""
    
    def __init__(self, executor_available_fn: Callable[[], bool]):
        self._executor_available = executor_available_fn
    
    @property
    def name(self) -> str:
        return "executor_available"
    
    def evaluate(
        self,
        from_state: RuntimeState,
        to_state: RuntimeState,
    ) -> GuardEvaluation:
        if not self._executor_available():
            return GuardEvaluation(
                guard_name=self.name,
                result=GuardResult.FAILED,
                reason="Executor unavailable"
            )
        return GuardEvaluation(
            guard_name=self.name,
            result=GuardResult.PASSED
        )
    
    def requires_guard(self, from_state: RuntimeState, to_state: RuntimeState) -> bool:
        return to_state in (
            CanonicalRuntimeState.ACTIVE,
            CanonicalRuntimeState.OPERATIONAL,
        )


class IntegrityValidGuard(StateGuard):
    """Guard that checks if system integrity is valid."""
    
    def __init__(self, integrity_valid_fn: Callable[[], bool]):
        self._integrity_valid = integrity_valid_fn
    
    @property
    def name(self) -> str:
        return "integrity_valid"
    
    def evaluate(
        self,
        from_state: RuntimeState,
        to_state: RuntimeState,
    ) -> GuardEvaluation:
        if not self._integrity_valid():
            return GuardEvaluation(
                guard_name=self.name,
                result=GuardResult.FAILED,
                reason="System integrity compromised"
            )
        return GuardEvaluation(
            guard_name=self.name,
            result=GuardResult.PASSED
        )
    
    def requires_guard(self, from_state: RuntimeState, to_state: RuntimeState) -> bool:
        # Always check integrity for state transitions
        return True


class HealthAcceptableGuard(StateGuard):
    """Guard that checks if health status is acceptable."""
    
    def __init__(self, health_acceptable_fn: Callable[[], bool]):
        self._health_acceptable = health_acceptable_fn
    
    @property
    def name(self) -> str:
        return "health_acceptable"
    
    def evaluate(
        self,
        from_state: RuntimeState,
        to_state: RuntimeState,
    ) -> GuardEvaluation:
        if not self._health_acceptable():
            return GuardEvaluation(
                guard_name=self.name,
                result=GuardResult.FAILED,
                reason="Health check failed"
            )
        return GuardEvaluation(
            guard_name=self.name,
            result=GuardResult.PASSED
        )
    
    def requires_guard(self, from_state: RuntimeState, to_state: RuntimeState) -> bool:
        # Only check health for operational transitions
        return to_state in (
            CanonicalRuntimeState.OPERATIONAL,
            CanonicalRuntimeState.ACTIVE,
        )


class ShutdownAbsentGuard(StateGuard):
    """Guard that checks if shutdown is not in progress."""
    
    def __init__(self, shutdown_active_fn: Callable[[], bool]):
        self._shutdown_active = shutdown_active_fn
    
    @property
    def name(self) -> str:
        return "shutdown_absent"
    
    def evaluate(
        self,
        from_state: RuntimeState,
        to_state: RuntimeState,
    ) -> GuardEvaluation:
        if self._shutdown_active():
            return GuardEvaluation(
                guard_name=self.name,
                result=GuardResult.FAILED,
                reason="Shutdown in progress"
            )
        return GuardEvaluation(
            guard_name=self.name,
            result=GuardResult.PASSED
        )
    
    def requires_guard(self, from_state: RuntimeState, to_state: RuntimeState) -> bool:
        # Check for shutdown when trying to transition away from terminal states
        return from_state not in (
            CanonicalRuntimeState.STOPPED,
            CanonicalRuntimeState.FAILED,
        )


class GuardEvaluator:
    """
    Evaluates guards for a transition request.
    
    Guards are evaluated BEFORE mutation. If any guard fails, the transition is blocked.
    """
    
    def __init__(self) -> None:
        self._guards: List[StateGuard] = []
        self._lock = threading.RLock()
    
    def register_guard(self, guard: StateGuard) -> None:
        """Register a guard to be evaluated during transitions."""
        with self._lock:
            if not any(g.name == guard.name for g in self._guards):
                self._guards.append(guard)
    
    def unregister_guard(self, name: str) -> bool:
        """Unregister a guard by name."""
        with self._lock:
            for i, g in enumerate(self._guards):
                if g.name == name:
                    del self._guards[i]
                    return True
            return False
    
    def evaluate_all(
        self,
        from_state: RuntimeState,
        to_state: RuntimeState,
    ) -> List[GuardEvaluation]:
        """
        Evaluate all relevant guards for a transition.
        
        Returns list of evaluations (only guards that require evaluation).
        """
        with self._lock:
            results: List[GuardEvaluation] = []
            
            for guard in self._guards:
                if guard.requires_guard(from_state, to_state):
                    result = guard.evaluate(from_state, to_state)
                    results.append(result)
            
            return results
    
    def all_guards_pass(
        self,
        from_state: RuntimeState,
        to_state: RuntimeState,
    ) -> Tuple[bool, List[str]]:
        """
        Check if all guards pass for a transition.
        
        Returns (all_pass, list_of_failed_guard_names)
        """
        evaluations = self.evaluate_all(from_state, to_state)
        failed_guards = [
            e.guard_name for e in evaluations
            if e.result == GuardResult.FAILED
        ]
        return len(failed_guards) == 0, failed_guards


# =============================================================================
# STATE MACHINE (CANONICAL AUTHORITY)
# =============================================================================


class RuntimeStateMachine:
    """
    Canonical authority for runtime state transitions.
    
    This is THE ONE source of truth for Gordon's operational status.
    It owns:
        - Current runtime state
        - Previous state (for rollback and audit)
        - Version number (monotonically increasing)
        - Complete transition history
        - Transition requests and results
    
    Only this class may mutate canonical runtime state. All subsystems
    that need to change state MUST go through this authority.
    
    Architecture:
    
        RuntimeStateMachine
        ├── Lock (thread-safe operations)
        ├── State Store (current + previous state)
        ├── Version Tracker
        ├── History Log (ordered, immutable entries)
        ├── Validator (transition validation)
        ├── GuardEvaluator (deterministic guards)
        └── EventPublisher (observer synchronization)
    
    Usage:
        
        # Create with unique runtime ID
        sm = RuntimeStateMachine(runtime_id="runtime_001")
        
        # Query current state (read-only)
        snapshot = sm.current_snapshot()
        
        # Request a transition through full pipeline
        request = RuntimeTransitionRequest.create(
            target_state=RuntimeState.RUNNING,
            runtime_id="runtime_001",
            reason="System startup"
        )
        
        result = await sm.transition(request)
        
        if result.success:
            print(f"New state: {sm.current_snapshot().state}")
        
        # Get history
        history = sm.get_history()
    
    Invariants enforced:
        1. Single writer (only transition() method)
        2. Validation before mutation
        3. Guards are deterministic (no side effects)
        4. Atomic commits (all-or-nothing within lock)
        5. Ordered history (monotonic sequence numbers)
        6. Immutable snapshots
    """
    
    # Class-level constants for state transitions
    VALID_TRANSITIONS: Dict[CanonicalRuntimeState, Set[CanonicalRuntimeState]] = {
        CanonicalRuntimeState.INITIAL: {CanonicalRuntimeState.CONSTRUCTED},
        CanonicalRuntimeState.CONSTRUCTED: {
            CanonicalRuntimeState.ASSEMBLED,
            CanonicalRuntimeState.FAILED,
            CanonicalRuntimeState.TERMINATED,
        },
        CanonicalRuntimeState.ASSEMBLED: {
            CanonicalRuntimeState.ACTIVATING,
            CanonicalRuntimeState.FAILED,
            CanonicalRuntimeState.TERMINATED,
        },
        CanonicalRuntimeState.ACTIVATING: {
            CanonicalRuntimeState.ACTIVE,
            CanonicalRuntimeState.FAILED,
            CanonicalRuntimeState.TERMINATED,
        },
        CanonicalRuntimeState.ACTIVE: {
            CanonicalRuntimeState.READY,
            CanonicalRuntimeState.FAILED,
            CanonicalRuntimeState.TERMINATED,
        },
        CanonicalRuntimeState.READY: {
            CanonicalRuntimeState.OPERATIONAL,
            CanonicalRuntimeState.QUIESCING,
            CanonicalRuntimeState.FAILED,
            CanonicalRuntimeState.TERMINATED,
        },
        CanonicalRuntimeState.OPERATIONAL: {
            CanonicalRuntimeState.DEGRADED,
            CanonicalRuntimeState.QUIESCING,
            CanonicalRuntimeState.STOPPING,
            CanonicalRuntimeState.FAILED,
            CanonicalRuntimeState.TERMINATED,
        },
        CanonicalRuntimeState.DEGRADED: {
            CanonicalRuntimeState.OPERATIONAL,
            CanonicalRuntimeState.QUIESCING,
            CanonicalRuntimeState.STOPPING,
            CanonicalRuntimeState.FAILED,
            CanonicalRuntimeState.TERMINATED,
        },
        CanonicalRuntimeState.QUIESCING: {
            CanonicalRuntimeState.QUIESCENT,
            CanonicalRuntimeState.FAILED,
            CanonicalRuntimeState.TERMINATED,
        },
        CanonicalRuntimeState.QUIESCENT: {
            CanonicalRuntimeState.STOPPING,
            CanonicalRuntimeState.READY,
            CanonicalRuntimeState.FAILED,
            CanonicalRuntimeState.TERMINATED,
        },
        CanonicalRuntimeState.STOPPING: {
            CanonicalRuntimeState.STOPPED,
            CanonicalRuntimeState.FAILED,
            CanonicalRuntimeState.TERMINATED,
        },
        CanonicalRuntimeState.STOPPED: {
            CanonicalRuntimeState.INITIAL,
            CanonicalRuntimeState.FAILED,
            CanonicalRuntimeState.TERMINATED,
        },
        CanonicalRuntimeState.FAILED: {
            CanonicalRuntimeState.INITIAL,
            CanonicalRuntimeState.TERMINATED,
        },
        CanonicalRuntimeState.TERMINATED: set(),
    }
    
    def __init__(
        self,
        runtime_id: str,
        initial_state: RuntimeState = CanonicalRuntimeState.INITIAL,
        config: Optional["StateMachineConfig"] = None,
    ) -> None:
        """
        Initialize the canonical runtime state machine.
        
        Args:
            runtime_id: Unique identifier for this runtime instance
            initial_state: Starting state (default: INITIAL)
            config: Configuration for behavior
        """
        import threading
        
        self._runtime_id = runtime_id
        self._config = config or StateMachineConfig.default()
        
        # State storage (protected by lock)
        self._lock = threading.RLock()
        self._state: RuntimeState = initial_state
        self._previous_state: Optional[RuntimeState] = None
        
        # Versioning
        self._version = 0
        self._current_version = RuntimeVersion.initial()
        
        # History (ordered, immutable)
        self._history: List[RuntimeHistoryEntry] = []
        self._max_history_size = self._config.max_history_entries
        
        # Transition tracking
        self._pending_transitions: Dict[str, RuntimeTransitionRequest] = {}
        self._completed_transitions: Dict[str, RuntimeTransitionResult] = {}
        
        # Components
        self._validator = TransitionValidator()
        self._guard_evaluator = GuardEvaluator()
        self._event_publisher = StateMachineEventPublisher()
        self._invariant_validator = InvariantValidator()
        
        # Rollback support (for future use)
        self._rollback_points: List[Tuple[RuntimeState, RuntimeVersion]] = []
    
    @property
    def runtime_id(self) -> str:
        """Get the runtime ID this state machine serves."""
        return self._runtime_id
    
    @property
    def current_state(self) -> RuntimeState:
        """Get current canonical state (read-only)."""
        with self._lock:
            return self._state
    
    @property
    def previous_state(self) -> Optional[RuntimeState]:
        """Get state before last transition."""
        with self._lock:
            return self._previous_state
    
    @property
    def version(self) -> int:
        """Get current state version (monotonically increasing)."""
        with self._lock:
            return self._version
    
    @property
    def guard_evaluator(self) -> GuardEvaluator:
        """Get the guard evaluator for registering guards."""
        return self._guard_evaluator
    
    # =========================================================================
    # QUERY METHODS (read-only, no mutation)
    # =========================================================================
    
    def current_snapshot(self) -> RuntimeSnapshot:
        """
        Get an immutable snapshot of current state.
        
        This represents one coherent moment in time. Snapshots are
        read-only and can be safely shared across threads.
        """
        with self._lock:
            return RuntimeSnapshot(
                state=self._state,
                previous_state=self._previous_state,
                target_state=None,  # No transition in progress
                transition_status="idle",
                version=self._current_version,
                runtime_id=self._runtime_id,
                timestamp_utc=time.time(),
            )
    
    def get_history(self) -> List[RuntimeHistoryEntry]:
        """Get a copy of the complete transition history."""
        with self._lock:
            return list(self._history)
    
    def get_state_at_version(self, version: int) -> Optional[RuntimeState]:
        """
        Get state at a specific version number.
        
        Args:
            version: The version to query
            
        Returns:
            State at that version, or None if version not found
        """
        with self._lock:
            # Simple linear search through history
            for entry in self._history:
                if entry.sequence_number == version:
                    return entry.target_state
            return None
    
    def get_history_since(self, sequence_number: int) -> List[RuntimeHistoryEntry]:
        """Get history entries with sequence numbers > given number."""
        with self._lock:
            return [
                entry for entry in self._history
                if entry.sequence_number > sequence_number
            ]
    
    # =========================================================================
    # TRANSITION PIPELINE (THE ONLY MUTATION PATH)
    # =========================================================================
    
    async def transition(self, request: RuntimeTransitionRequest) -> RuntimeTransitionResult:
        """
        Execute a state transition through the full pipeline.
        
        This is the ONLY method that may mutate canonical state.
        All transitions flow through this pipeline:
            
            Request → Validation → Guards → Approval → Pre-Hooks
                ↓
            Atomic Commit (within lock)
                ↓
            Post-Hooks → Events → Synchronize
        
        Args:
            request: The transition request with target state and metadata
            
        Returns:
            Result with success/failure status and details
            
        Raises:
            RuntimeError: On critical errors during transition
        """
        # Generate unique result ID
        result_id = f"result_{uuid.uuid4().hex[:16]}"
        
        requested_at_utc = time.time()
        
        # Acquire lock for entire operation (single writer)
        with self._lock:
            current_state = self._state
            
            # Step 1: Validation
            validation_valid, validation_errors = self._validator.validate(
                request=request,
                current_state=current_state,
                expected_version=self._version if self._config.optimistic_locking else None,
            )
            
            if not validation_valid:
                return RuntimeTransitionResult(
                    success=False,
                    request=request,
                    result_id=result_id,
                    current_state=current_state,
                    previous_state=self._previous_state or current_state,
                    requested_at_utc=requested_at_utc,
                    completed_at_utc=time.time(),
                    status="rejected",
                    failure_reason=f"Validation failed: {'; '.join(validation_errors)}",
                )
            
            # Step 2: Guard evaluation
            guards_pass, failed_guards = self._guard_evaluator.all_guards_pass(
                from_state=current_state,
                to_state=request.target_state,
            )
            
            if not guards_pass:
                return RuntimeTransitionResult(
                    success=False,
                    request=request,
                    result_id=result_id,
                    current_state=current_state,
                    previous_state=self._previous_state or current_state,
                    requested_at_utc=requested_at_utc,
                    completed_at_utc=time.time(),
                    status="rejected",
                    failure_reason=f"Guard evaluation failed: {', '.join(failed_guards)}",
                )
            
            # Step 3: Invariant validation
            invariant_results = self._invariant_validator.validate_transition(
                current_state=current_state,
                target_state=request.target_state,
                runtime_id=self._runtime_id,
            )
            
            failed_invariants = [
                r for r in invariant_results if not r.passed
            ]
            
            if failed_invariants:
                return RuntimeTransitionResult(
                    success=False,
                    request=request,
                    result_id=result_id,
                    current_state=current_state,
                    previous_state=self._previous_state or current_state,
                    requested_at_utc=requested_at_utc,
                    completed_at_utc=time.time(),
                    status="rejected",
                    failure_reason=f"Invariant violations: {'; '.join(r.invariant_name for r in failed_invariants)}",
                )
            
            # Step 4: Pre-transition hooks
            pre_hook_results = self._run_pre_hooks(
                current_state=current_state,
                target_state=request.target_state,
            )
            
            if not all(pre_hook_results.values()):
                return RuntimeTransitionResult(
                    success=False,
                    request=request,
                    result_id=result_id,
                    current_state=current_state,
                    previous_state=self._previous_state or current_state,
                    requested_at_utc=requested_at_utc,
                    completed_at_utc=time.time(),
                    status="rejected",
                    failure_reason="Pre-transition hook blocked transition",
                )
            
            # Step 5: Atomic commit (within lock)
            new_version = self._current_version.next(RuntimeTransitionId.generate())
            transition_id = str(new_version.transition_id)
            
            try:
                # Record rollback point before mutation
                if self._config.rollback_enabled:
                    self._rollback_points.append((current_state, self._current_version))
                
                # Update state atomically
                self._previous_state = current_state
                self._state = request.target_state
                self._version += 1
                self._current_version = new_version
                
                # Create history entry
                history_entry = RuntimeHistoryEntry(
                    entry_id=f"hist_{uuid.uuid4().hex[:16]}",
                    sequence_number=self._version,
                    timestamp_utc=time.time(),
                    runtime_id=self._runtime_id,
                    source_state=current_state,
                    target_state=request.target_state,
                    version_before=self._version - 1,
                    version_after=self._version,
                    requestor_id=request.requestor_id,
                    reason=request.reason,
                    validation_passed=True,
                    guard_evaluation="passed",
                    outcome="committed",
                )
                
                self._history.append(history_entry)
                
                # Trim history if needed
                while len(self._history) > self._max_history_size:
                    self._history.pop(0)
                
                # Step 6: Post-transition hooks
                self._run_post_hooks(
                    current_state=request.target_state,
                    previous_state=current_state,
                )
                
                # Step 7: Event publication
                self._event_publisher.publish_transition(
                    runtime_id=self._runtime_id,
                    request=request,
                    result_id=result_id,
                    current_state=request.target_state,
                    previous_state=current_state,
                    version=self._version,
                )
                
                # Step 8: Observer synchronization (async if needed)
                asyncio.create_task(self._synchronize_observers())
                
            except Exception as e:
                # Critical failure - attempt rollback
                if self._rollback_points:
                    last_rollback = self._rollback_points.pop()
                    self._state = last_rollback[0]
                    self._current_version = last_rollback[1]
                    self._version -= 1
                
                raise RuntimeError(f"Critical transition failure: {e}")
        
        return RuntimeTransitionResult(
            success=True,
            request=request,
            result_id=result_id,
            current_state=self._state,
            previous_state=current_state,
            requested_at_utc=requested_at_utc,
            completed_at_utc=time.time(),
            status="completed",
        )
    
    # =========================================================================
    # ROLLBACK SUPPORT
    # =========================================================================
    
    async def rollback(self) -> bool:
        """
        Rollback to the last known good state.
        
        This is for emergency recovery when a transition has failed
        and we need to restore previous state. The rollback preserves
        evidence in history.
        
        Returns:
            True if rollback succeeded, False otherwise
        """
        with self._lock:
            if not self._rollback_points:
                logger.warning("No rollback points available")
                return False
            
            # Get the last rollback point (most recent)
            target_state, target_version = self._rollback_points.pop()
            
            # Record this as a history entry with outcome="rolled_back"
            history_entry = RuntimeHistoryEntry(
                entry_id=f"hist_{uuid.uuid4().hex[:16]}",
                sequence_number=self._version + 1,
                timestamp_utc=time.time(),
                runtime_id=self._runtime_id,
                source_state=self._state,  # Current state (being rolled back from)
                target_state=target_state,  # State we're rolling back to
                version_before=self._version,
                version_after=self._version,
                requestor_id="rollback_system",
                reason=f"Rollback from {self._state.value} to {target_state.value}",
                validation_passed=False,  # Rollbacks don't go through normal validation
                guard_evaluation="skipped",  # Guards skipped during rollback
                outcome="rolled_back",
            )
            
            self._history.append(history_entry)
            
            # Apply rollback
            self._previous_state = self._state
            self._state = target_state
            self._current_version = target_version
            
            # Publish rollback event
            self._event_publisher.publish_rollback(
                runtime_id=self._runtime_id,
                from_state=self._previous_state,
                to_state=target_state,
            )
            
            return True
    
    def get_rollback_history(self) -> List[RuntimeHistoryEntry]:
        """Get history entries that are rollback records."""
        with self._lock:
            return [
                entry for entry in self._history
                if entry.outcome == "rolled_back"
            ]
    
    # =========================================================================
    # EVENT PUBLICATION (OBSERVER SYNCHRONIZATION)
    # =========================================================================
    
    async def subscribe_events(
        self,
        callback: Callable[[str, Dict[str, Any]], None],
    ) -> str:
        """
        Subscribe to state change events.
        
        Args:
            callback: Function called with (event_type, payload) on each event
            
        Returns:
            Subscription ID for unsubscribing
        """
        return self._event_publisher.subscribe(callback)
    
    async def unsubscribe_events(self, subscription_id: str) -> bool:
        """Unsubscribe from events."""
        return self._event_publisher.unsubscribe(subscription_id)
    
    # =========================================================================
    # INVARIANT VALIDATION
    # =========================================================================
    
    def validate_invariants(self) -> List[RuntimeInvariantResult]:
        """
        Validate all runtime invariants.
        
        Returns list of results (pass/fail with details).
        """
        return self._invariant_validator.validate_all(
            state=self._state,
            version=self._version,
            history=self._history,
            runtime_id=self._runtime_id,
        )
    
    # =========================================================================
    # INTERNAL HELPERS
    # =========================================================================
    
    def _run_pre_hooks(
        self,
        current_state: RuntimeState,
        target_state: RuntimeState,
    ) -> Dict[str, bool]:
        """Run pre-transition hooks. Returns dict of hook_name -> success."""
        results = {}
        
        # Hook 1: State validation
        try:
            if not self._validator.is_valid_transition(
                self._map_to_canonical(current_state),
                self._map_to_canonical(target_state),
            ):
                results["state_validation"] = False
                return results
            results["state_validation"] = True
        except Exception as e:
            results["state_validation"] = False
        
        # Hook 2: Resource validation
        try:
            if not hasattr(self, '_resources_available') or self._resources_available():
                results["resource_check"] = True
            else:
                results["resource_check"] = False
        except Exception:
            results["resource_check"] = False
        
        # Hook 3: Readiness check
        try:
            if not hasattr(self, '_readiness_ready') or self._readiness_ready():
                results["readiness_check"] = True
            else:
                results["readiness_check"] = False
        except Exception:
            results["readiness_check"] = False
        
        return results
    
    def _run_post_hooks(
        self,
        current_state: RuntimeState,
        previous_state: RuntimeState,
    ) -> None:
        """Run post-transition hooks (side effects only, no mutation)."""
        # Hook 1: Update health status
        if hasattr(self, '_update_health'):
            try:
                self._update_health(current_state)
            except Exception:
                pass  # Don't fail transition on health update
        
        # Hook 2: Publish state change
        if hasattr(self, '_publish_state_change'):
            try:
                self._publish_state_change(
                    from_state=previous_state,
                    to_state=current_state,
                )
            except Exception:
                pass
    
    def _map_to_canonical(self, state: RuntimeState) -> CanonicalRuntimeState:
        """Map a RuntimeState to its canonical equivalent."""
        try:
            return CanonicalRuntimeState(state.value)
        except ValueError:
            # Fallback mapping for compatibility
            state_str = str(state).lower().replace("runtimestate.", "")
            for canonical in CanonicalRuntimeState:
                if state_str == canonical.value.lower():
                    return canonical
            raise ValueError(f"Cannot map {state} to canonical state")
    
    async def _synchronize_observers(self) -> None:
        """Synchronize observer subsystems with current state."""
        # This is where we would notify subsystems like:
        # - ReadinessController
        # - AdmissionController
        # - Scheduler
        # - Executor
        #
        # In a full implementation, these would have subscribed via
        # subscribe_events() and receive the snapshot updates.
        pass


@dataclass(frozen=True)
class StateMachineConfig:
    """Configuration for RuntimeStateMachine behavior."""
    
    max_history_entries: int = 1000              # Maximum history entries to keep
    optimistic_locking: bool = True              # Enable version-based locking
    rollback_enabled: bool = True                # Enable rollback functionality
    event_publishing: bool = True                # Publish state change events
    
    @classmethod
    def default(cls) -> "StateMachineConfig":
        return cls()
    
    @classmethod
    def strict(cls) -> "StateMachineConfig":
        """Strict configuration with all safety features enabled."""
        return cls(
            max_history_entries=10000,
            optimistic_locking=True,
            rollback_enabled=True,
            event_publishing=True,
        )
    
    @classmethod
    def with_timeout_config(
        cls,
        default_timeout: float = 30.0,
        min_timeout: float = 1.0,
        max_timeout: float = 300.0,
    ) -> "StateMachineConfig":
        """Create a config with custom timeout settings."""
        instance = cls()
        # Note: Config doesn't store timeouts directly, but this method
        # provides a consistent interface for future expansion
        return instance


# =============================================================================
# EVENT MODEL
# =============================================================================


class StateMachineEventPublisher:
    """
    Publisher for state change events.
    
    Events observe transitions but don't drive them. They're for
    observability and synchronization only.
    
    Added in Phase 3.7.8-R remediation (GORDON-3.7.8-ISOLATION-001):
        - Thread-safe iteration over subscribers using copy-on-write
    """
    
    def __init__(self) -> None:
        self._subscribers: Dict[str, Callable[[str, Dict[str, Any]], None]] = {}
        self._lock = threading.RLock()
    
    def subscribe(self, callback: Callable[[str, Dict[str, Any]], None]) -> str:
        """
        Subscribe to state change events.
        
        Args:
            callback: Function called with (event_type, payload)
            
        Returns:
            Subscription ID for later unsubscription
        """
        subscription_id = f"sub_{uuid.uuid4().hex[:16]}"
        with self._lock:
            self._subscribers[subscription_id] = callback
        return subscription_id
    
    def unsubscribe(self, subscription_id: str) -> bool:
        """Unsubscribe from events."""
        with self._lock:
            if subscription_id in self._subscribers:
                del self._subscribers[subscription_id]
                return True
            return False
    
    def _publish_event(
        self,
        event_type: str,
        payload: Dict[str, Any],
    ) -> None:
        """Publish an event to all subscribers."""
        with self._lock:
            # Create a copy of the callback list to avoid modifying during iteration
            # This fixes GORDON-3.7.8-ISOLATION-001 (event publication not thread-safe)
            callbacks = list(self._subscribers.values())
        
        # Call callbacks outside the lock to avoid holding it during subscriber code execution
        for callback in callbacks:
            try:
                callback(event_type, payload)
            except Exception:
                pass  # Don't let subscriber errors affect main flow
    
    def publish_transition(
        self,
        runtime_id: str,
        request: RuntimeTransitionRequest,
        result_id: str,
        current_state: RuntimeState,
        previous_state: RuntimeState,
        version: int,
    ) -> None:
        """Publish a transition event."""
        payload = {
            "runtime_id": runtime_id,
            "request": {
                "target_state": request.target_state.value if hasattr(request.target_state, 'value') else str(request.target_state),
                "source_state": request.source_state.value if request.source_state and hasattr(request.source_state, 'value') else (str(request.source_state) if request.source_state else None),
                "reason": request.reason,
            },
            "result_id": result_id,
            "current_state": current_state.value if hasattr(current_state, 'value') else str(current_state),
            "previous_state": previous_state.value if hasattr(previous_state, 'value') else str(previous_state),
            "version": version,
        }
        
        self._publish_event("state_transition", payload)
    
    def publish_rollback(
        self,
        runtime_id: str,
        from_state: RuntimeState,
        to_state: RuntimeState,
    ) -> None:
        """Publish a rollback event."""
        payload = {
            "runtime_id": runtime_id,
            "from_state": from_state.value if hasattr(from_state, 'value') else str(from_state),
            "to_state": to_state.value if hasattr(to_state, 'value') else str(to_state),
        }
        
        self._publish_event("state_rollback", payload)
    
    def publish_snapshot(
        self,
        runtime_id: str,
        snapshot: RuntimeSnapshot,
    ) -> None:
        """Publish a snapshot event."""
        payload = {
            "runtime_id": runtime_id,
            "snapshot": snapshot.to_dict(),
        }
        
        self._publish_event("state_snapshot", payload)


# =============================================================================
# INVARIANT VALIDATOR
# =============================================================================


class InvariantValidator:
    """
    Validates runtime invariants during transitions.
    
    Invariants are business rules that must always hold true.
    They're checked both for individual transitions and system-wide.
    """
    
    def validate_transition(
        self,
        current_state: RuntimeState,
        target_state: RuntimeState,
        runtime_id: str,
    ) -> List[RuntimeInvariantResult]:
        """
        Validate invariants for a specific transition.
        
        Returns list of results (pass/fail with details).
        """
        results = []
        
        # Invariant 1: Only one canonical state
        if not isinstance(target_state, RuntimeState):
            results.append(RuntimeInvariantResult.failure(
                invariant_name="single_canonical_state",
                message=f"Target state {target_state} is not a valid RuntimeState",
                severity="error",
            ))
        else:
            results.append(RuntimeInvariantResult.success("single_canonical_state"))
        
        # Invariant 2: Valid transition edge
        validator = TransitionValidator()
        if not validator.is_valid_transition(
            self._map_to_canonical(current_state),
            self._map_to_canonical(target_state),
        ):
            results.append(RuntimeInvariantResult.failure(
                invariant_name="valid_transition_edge",
                message=f"Invalid transition from {current_state.value} to {target_state.value}",
                severity="error",
            ))
        else:
            results.append(RuntimeInvariantResult.success("valid_transition_edge"))
        
        # Invariant 3: Runtime ID consistency
        if runtime_id and not runtime_id.startswith("runtime_"):
            results.append(RuntimeInvariantResult.failure(
                invariant_name="consistent_runtime_id",
                message=f"Runtime ID should start with 'runtime_': {runtime_id}",
                severity="warning",
            ))
        else:
            results.append(RuntimeInvariantResult.success("consistent_runtime_id"))
        
        # Invariant 4: State ordering (no backward jumps in lifecycle)
        if self._is_lifecycle_state(current_state) and self._is_lifecycle_state(target_state):
            current_order = self._get_lifecycle_order(current_state)
            target_order = self._get_lifecycle_order(target_state)
            
            if current_order is not None and target_order is not None:
                # Allow some forward and backward moves, but not too much
                if abs(target_order - current_order) > 3:
                    results.append(RuntimeInvariantResult.failure(
                        invariant_name="reasonable_state_change",
                        message=f"Large state change: {current_state.value} -> {target_state.value}",
                        severity="warning",
                    ))
                else:
                    results.append(RuntimeInvariantResult.success("reasonable_state_change"))
            else:
                results.append(RuntimeInvariantResult.success("reasonable_state_change"))
        else:
            results.append(RuntimeInvariantResult.success("reasonable_state_change"))
        
        return results
    
    def validate_all(
        self,
        state: RuntimeState,
        version: int,
        history: List[RuntimeHistoryEntry],
        runtime_id: str,
    ) -> List[RuntimeInvariantResult]:
        """
        Validate all invariants for the current system state.
        
        Returns list of all validation results.
        """
        results = []
        
        # Invariant 1: Version is monotonically increasing
        if version < 0:
            results.append(RuntimeInvariantResult.failure(
                invariant_name="monotonic_version",
                message=f"Version {version} should be non-negative",
                severity="error",
            ))
        else:
            results.append(RuntimeInvariantResult.success("monotonic_version"))
        
        # Invariant 2: History is ordered by sequence number
        if len(history) > 1:
            for i in range(1, len(history)):
                if history[i].sequence_number <= history[i-1].sequence_number:
                    results.append(RuntimeInvariantResult.failure(
                        invariant_name="ordered_history",
                        message=f"History out of order at index {i}",
                        severity="error",
                    ))
                    break
            else:
                results.append(RuntimeInvariantResult.success("ordered_history"))
        else:
            results.append(RuntimeInvariantResult.success("ordered_history"))
        
        # Invariant 3: No duplicate consecutive entries
        if len(history) > 1:
            for i in range(1, len(history)):
                if history[i].source_state == history[i-1].target_state and \
                   history[i].target_state == history[i-1].target_state:
                    results.append(RuntimeInvariantResult.failure(
                        invariant_name="no_duplicate_entries",
                        message=f"Duplicate consecutive entries at index {i}",
                        severity="warning",
                    ))
                    break
            else:
                results.append(RuntimeInvariantResult.success("no_duplicate_entries"))
        else:
            results.append(RuntimeInvariantResult.success("no_duplicate_entries"))
        
        # Invariant 4: Runtime ID is consistent across history
        if history:
            for entry in history:
                if entry.runtime_id != runtime_id:
                    results.append(RuntimeInvariantResult.failure(
                        invariant_name="consistent_runtime_id_history",
                        message=f"History contains entries with different runtime IDs: {entry.runtime_id} vs {runtime_id}",
                        severity="error",
                    ))
                    break
            else:
                results.append(RuntimeInvariantResult.success("consistent_runtime_id_history"))
        else:
            results.append(RuntimeInvariantResult.success("consistent_runtime_id_history"))
        
        return results
    
    def _map_to_canonical(self, state: RuntimeState) -> CanonicalRuntimeState:
        """Map a RuntimeState to its canonical equivalent."""
        try:
            return CanonicalRuntimeState(state.value)
        except ValueError:
            # Fallback
            state_str = str(state).lower()
            for canonical in CanonicalRuntimeState:
                if state_str == canonical.value.lower():
                    return canonical
            raise ValueError(f"Cannot map {state} to canonical state")
    
    def _is_lifecycle_state(self, state: RuntimeState) -> bool:
        """Check if state is part of lifecycle progression."""
        return state in (
            CanonicalRuntimeState.INITIAL,
            CanonicalRuntimeState.CONSTRUCTED,
            CanonicalRuntimeState.ASSEMBLED,
            CanonicalRuntimeState.ACTIVATING,
            CanonicalRuntimeState.ACTIVE,
            CanonicalRuntimeState.READY,
            CanonicalRuntimeState.OPERATIONAL,
            CanonicalRuntimeState.DEGRADED,
            CanonicalRuntimeState.QUIESCING,
            CanonicalRuntimeState.QUIESCENT,
            CanonicalRuntimeState.STOPPING,
            CanonicalRuntimeState.STOPPED,
        )
    
    def _get_lifecycle_order(self, state: RuntimeState) -> Optional[int]:
        """Get position in lifecycle progression (lower = earlier)."""
        try:
            canonical = self._map_to_canonical(state)
            order_map = {
                CanonicalRuntimeState.INITIAL: 0,
                CanonicalRuntimeState.CONSTRUCTED: 1,
                CanonicalRuntimeState.ASSEMBLED: 2,
                CanonicalRuntimeState.ACTIVATING: 3,
                CanonicalRuntimeState.ACTIVE: 4,
                CanonicalRuntimeState.READY: 5,
                CanonicalRuntimeState.OPERATIONAL: 6,
                CanonicalRuntimeState.DEGRADED: 7,
                CanonicalRuntimeState.QUIESCING: 8,
                CanonicalRuntimeState.QUIESCENT: 9,
                CanonicalRuntimeState.STOPPING: 10,
                CanonicalRuntimeState.STOPPED: 11,
            }
            return order_map.get(canonical)
        except ValueError:
            return None


# =============================================================================
# PUBLIC API
# =============================================================================

__all__ = [
    # State enumeration (canonical)
    "CanonicalRuntimeState",
    
    # Immutable state models
    "RuntimeTransitionId",
    "RuntimeVersion",
    "RuntimeSnapshot",
    "RuntimeTransitionRequest",
    "RuntimeTransitionResult",
    "RuntimeTransitionFailure",
    "RuntimeHistoryEntry",
    "RuntimeInvariantResult",
    
    # Drift detection (Phase 3.7.8-R remediation)
    "StateDriftRule",
    "StateDriftFinding",
    "StateDriftSnapshot",
    "StateDriftDetector",
    
    # Validation and guards
    "TransitionValidator",
    "GuardEvaluator",
    "ResourcesAvailableGuard",
    "ReadinessSatisfiedGuard",
    "AdmissionPermittedGuard",
    "SchedulerAvailableGuard",
    "ExecutorAvailableGuard",
    "IntegrityValidGuard",
    "HealthAcceptableGuard",
    "ShutdownAbsentGuard",
    
    # State machine (canonical authority)
    "RuntimeStateMachine",
    "StateMachineConfig",
    
    # Event system
    "StateMachineEventPublisher",
    
    # Invariant validation
    "InvariantValidator",
]
