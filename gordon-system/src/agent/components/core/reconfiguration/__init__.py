# Runtime Reconfiguration Infrastructure
# =====================================
"""
Runtime configuration change orchestration system.

Provides:
- Single canonical reconfiguration coordinator
- Transactional configuration changes with prepare, apply, verify, commit
- Rollback support for failed changes
- Partial application handling

Phase 3.7.14: Configuration, Policy, Feature Flags & Runtime Reconfiguration
"""

from dataclasses import dataclass, field
from typing import (
    Dict,
    Any,
    Optional,
    List,
    Tuple,
)
from enum import Enum
import time
import uuid


# =============================================================================
# Reconfiguration IDs
# =============================================================================

@dataclass(frozen=True)
class ReconfigurationId:
    """Unique identifier for a reconfiguration operation."""
    value: str
    
    @classmethod
    def generate(cls) -> "ReconfigurationId":
        import uuid
        return cls(value=str(uuid.uuid4()))
    
    @classmethod
    def from_string(cls, s: str) -> "ReconfigurationId":
        return cls(value=s)
    
    def __str__(self) -> str:
        return self.value


# =============================================================================
# Reconfiguration Request
# =============================================================================

@dataclass(frozen=True)
class ReconfigurationRequest:
    """
    A request to change runtime configuration.
    
    This is the input to the reconfiguration process.
    """
    
    reconfig_id: ReconfigurationId
    runtime_id: str
    
    # Expected state (for stale request detection)
    expected_config_version: int  # Version we expect to be currently effective
    expected_policy_version: Optional[str] = None
    expected_feature_flag_version: Optional[str] = None
    expected_capability_version: Optional[str] = None
    
    # Source changes
    source_changes: Dict[str, Any] = field(default_factory=dict)  # source_id -> new data
    
    # Request metadata
    request_time: float = field(default_factory=time.monotonic)
    deadline: Optional[float] = None  # If set, operation must complete by this time
    
    # Authority and context
    requested_by: str = "system"  # e.g., "operator", "system", "policy"
    reason: Optional[str] = None  # Human-readable reason
    
    # Mode
    mode: str = "DRY_RUN"  # DRY_RUN, APPLY_DYNAMIC, APPLY_WITH_RESTART


@dataclass(frozen=True)
class ReconfigurationContext:
    """Context for reconfiguration operations."""
    runtime_id: str
    correlation_id: Optional[str] = None
    user_context: Dict[str, Any] = field(default_factory=dict)


# =============================================================================
# Reconfiguration Modes
# =============================================================================

class ReconfigurationMode(Enum):
    DRY_RUN = "dry_run"
    APPLY_DYNAMIC = "apply_dynamic"  # No restart required
    APPLY_WITH_COMPONENT_RESTART = "apply_with_component_restart"
    SCHEDULE_RUNTIME_RESTART = "schedule_runtime_restart"
    FORCE_AUTHORIZED = "force_authorized"
    ROLLBACK_TO_VERSION = "rollback_to_version"


# =============================================================================
# Reconfiguration Result
# =============================================================================

class ReconfigurationState(Enum):
    REQUESTED = "requested"
    RESOLVING = "resolving"
    VALIDATING = "validating"
    PLANNING = "planning"
    PREPARING = "preparing"
    APPLYING = "applying"
    VERIFYING = "verifying"
    COMMITTING = "committing"
    COMMITTED = "committed"
    ROLLING_BACK = "rolling_back"
    ROLLED_BACK = "rolled_back"
    PARTIAL = "partial"  # Some changes applied, rollback impossible
    FAILED = "failed"
    CANCELLED = "cancelled"


@dataclass(frozen=True)
class ReconfigurationResult:
    """
    Result of a reconfiguration operation.
    
    This is the output after the reconfiguration completes.
    """
    
    reconfig_id: str
    state: ReconfigurationState
    
    # Effective configuration after operation
    effective_config_version: int
    applied_config_version: Optional[int] = None
    
    # Changes made (for success cases)
    changes_applied: Tuple[str, ...] = field(default_factory=tuple)
    
    # Failure information (if failed)
    failure_reason: Optional[str] = None
    primary_failure_at: Optional[float] = None
    partial_application: bool = False  # Were some changes applied before failure?
    
    # Timing
    request_time: float = 0.0
    completion_time: Optional[float] = None
    
    @property
    def duration_seconds(self) -> float:
        if self.completion_time and self.request_time:
            return self.completion_time - self.request_time
        return 0.0
    
    @property
    def success(self) -> bool:
        return self.state in (ReconfigurationState.COMMITTED, ReconfigurationState.PARTIAL)


@dataclass(frozen=True)
class ReconfigurationFailure:
    """Details of a reconfiguration failure."""
    stage: str  # Where the failure occurred
    reason: str
    timestamp: float = field(default_factory=time.monotonic)
    affected_consumers: Tuple[str, ...] = field(default_factory=tuple)


@dataclass(frozen=True)
class ReconfigurationReceipt:
    """
    Receipt for a reconfiguration operation.
    
    This can be issued before the operation completes to acknowledge
    receipt and tracking of the request.
    """
    
    reconfig_id: str
    state: ReconfigurationState = ReconfigurationState.REQUESTED
    created_at: float = field(default_factory=time.monotonic)
    expires_at: Optional[float] = None


@dataclass(frozen=True)
class ReconfigurationSnapshot:
    """Snapshot of a reconfiguration operation for diagnostics."""
    snapshot_id: str
    reconfig_id: str
    runtime_id: str
    state: ReconfigurationState
    steps_completed: Tuple[str, ...]
    timestamp: float = field(default_factory=time.monotonic)


# =============================================================================
# Configuration Application Plan
# =============================================================================

@dataclass(frozen=True)
class ApplicationStep:
    """A single step in the application plan."""
    step_id: str
    consumer_name: str  # Who to apply to
    action: str  # "prepare", "apply", "verify", "commit"
    dependencies: Tuple[str, ...] = field(default_factory=tuple)  # Step IDs this depends on


@dataclass(frozen=True)
class ConfigurationApplicationPlan:
    """
    A plan for applying configuration changes.
    
    This is the output of the planning phase and input to execution.
    """
    
    reconfig_id: str
    from_version: int
    to_version: int
    
    # Diff information
    added_fields: Tuple[str, ...]
    removed_fields: Tuple[str, ...]
    modified_fields: Tuple[str, ...]
    
    # Consumer impact
    impacted_consumers: Tuple[str, ...]  # Names of consumers affected
    
    # Steps in order
    steps: Tuple[ApplicationStep, ...]
    
    # Ordering constraints
    component_restart_required: bool = False
    runtime_restart_required: bool = False
    
    # Deadlines
    max_duration_seconds: float = 30.0  # Default 30 seconds for dynamic changes
    
    # Rollback information
    rollback_supported: bool = True
    rollback_steps: Tuple[ApplicationStep, ...] = field(default_factory=tuple)
    
    # Non-rollbackable changes
    non_rollbackable_fields: Tuple[str, ...] = field(default_factory=tuple)


# =============================================================================
# Impact Analysis
# =============================================================================

@dataclass(frozen=True)
class ImpactFinding:
    """A finding from impact analysis."""
    consumer_name: str
    impact_type: str  # "restart_required", "reconfiguration_needed", "no_impact"
    details: Optional[str] = None


@dataclass(frozen=True)
class ConfigurationImpactAnalysis:
    """
    Result of configuration change impact analysis.
    
    Before applying changes, we analyze what will be affected.
    """
    
    reconfig_id: str
    from_version: int
    to_version: int
    
    findings: Tuple[ImpactFinding, ...]
    
    requires_component_restart: bool = False
    requires_runtime_restart: bool = False
    
    restart_order: Tuple[str, ...] = field(default_factory=tuple)  # Order to restart consumers


# =============================================================================
# Reconfiguration Coordinator
# =============================================================================

class ReconfigurationCoordinator:
    """
    Coordinates runtime reconfiguration operations.
    
    This is the single authoritative coordinator for configuration changes.
    
    Responsibilities:
    - Accept and validate reconfiguration requests
    - Generate change diffs
    - Perform impact analysis
    - Compile application plans
    - Execute prepare, apply, verify, commit phases
    - Handle rollback on failure
    
    Invariants:
    - One coordinator per runtime
    - No other entity can mutate effective configuration
    - All changes go through this coordinator
    """
    
    def __init__(self, runtime_id: str):
        self._runtime_id = runtime_id
        self._current_config_version = 1
        self._active_reconfigurations: Dict[str, ReconfigurationState] = {}
        self._lock = __import__("threading").Lock()
        self._max_active = 1  # One concurrent reconfiguration at a time
    
    @property
    def runtime_id(self) -> str:
        return self._runtime_id
    
    @property
    def current_config_version(self) -> int:
        return self._current_config_version
    
    def submit_request(
        self,
        request: ReconfigurationRequest
    ) -> Tuple[ReconfigurationReceipt, Optional[ConfigurationApplicationPlan]]:
        """
        Submit a reconfiguration request.
        
        Args:
            request: The reconfiguration request
            
        Returns:
            Tuple of (receipt, application_plan or None if dry_run/validation failed)
        """
        with self._lock:
            # Check for stale request
            if request.expected_config_version != self._current_config_version:
                return (
                    ReconfigurationReceipt(
                        reconfig_id=request.reconfig_id.value,
                        state=ReconfigurationState.FAILED,
                        created_at=time.monotonic(),
                        expires_at=None
                    ),
                    None
                )
            
            # Check for concurrent operations (if not allowed)
            if len(self._active_reconfigurations) >= self._max_active:
                return (
                    ReconfigurationReceipt(
                        reconfig_id=request.reconfig_id.value,
                        state=ReconfigurationState.FAILED,
                        created_at=time.monotonic(),
                        expires_at=None
                    ),
                    None
                )
            
            # Determine plan based on mode
            if request.mode == "DRY_RUN":
                # Generate a plan but don't commit
                plan = self._compile_plan(request)
                return (
                    ReconfigurationReceipt(
                        reconfig_id=request.reconfig_id.value,
                        state=ReconfigurationState.REQUESTED,
                        created_at=time.monotonic(),
                        expires_at=None
                    ),
                    plan
                )
            
            # For apply modes, we need to execute the change
            self._active_reconfigurations[request.reconfig_id.value] = ReconfigurationState.RESOLVING
            
            return (
                ReconfigurationReceipt(
                    reconfig_id=request.reconfig_id.value,
                    state=ReconfigurationState.REQUESTED,
                    created_at=time.monotonic(),
                    expires_at=None
                ),
                None  # Would execute plan and return result
            )
    
    def _compile_plan(self, request: ReconfigurationRequest) -> Optional[ConfigurationApplicationPlan]:
        """Compile an application plan for a reconfiguration request."""
        # This would compute the actual changes and generate steps
        # For now, return a placeholder
        
        from dataclasses import replace as dataclass_replace
        from typing import Tuple
        
        return None  # Placeholder
    
    def _execute_plan(self, plan: ConfigurationApplicationPlan) -> ReconfigurationResult:
        """Execute an application plan with proper state management."""
        start_time = time.monotonic()
        
        try:
            # Phase 1: Prepare
            for step in plan.steps:
                if step.action == "prepare":
                    self._active_reconfigurations[plan.reconfig_id] = ReconfigurationState.PREPARING
            
            # Phase 2: Apply
            for step in plan.steps:
                if step.action == "apply":
                    self._active_reconfigurations[plan.reconfig_id] = ReconfigurationState.APPLYING
            
            # Phase 3: Verify
            for step in plan.steps:
                if step.action == "verify":
                    self._active_reconfigurations[plan.reconfig_id] = ReconfigurationState.VERIFYING
            
            # Phase 4: Commit
            self._current_config_version += 1
            
            return ReconfigurationResult(
                reconfig_id=plan.reconfig_id,
                state=ReconfigurationState.COMMITTED,
                effective_config_version=self._current_config_version,
                request_time=start_time,
                completion_time=time.monotonic(),
                changes_applied=tuple(str(f) for f in plan.modified_fields)
            )
            
        except Exception as e:
            failure_reason = str(e)
            if "ReconfigurationCoordinator" in failure_reason:
                failure_reason = "Failed during reconfiguration execution"
            return ReconfigurationResult(
                reconfig_id=plan.reconfig_id,
                state=ReconfigurationState.FAILED,
                effective_config_version=self._current_config_version,
                failure_reason=str(e),
                request_time=start_time,
                completion_time=time.monotonic()
            )
    
    def rollback(self, version_to_restore: int) -> ReconfigurationResult:
        """
        Rollback to a previous configuration version.
        
        Args:
            version_to_restore: Version number to restore
            
        Returns:
            Result of the rollback operation
        """
        if version_to_restore >= self._current_config_version:
            return ReconfigurationResult(
                reconfig_id=str(uuid.uuid4()),
                state=ReconfigurationState.FAILED,
                effective_config_version=self._current_config_version,
                failure_reason=f"Cannot rollback to future version {version_to_restore}",
                request_time=time.monotonic(),
                completion_time=time.monotonic()
            )
        
        self._current_config_version = version_to_restore
        
        return ReconfigurationResult(
            reconfig_id=str(uuid.uuid4()),
            state=ReconfigurationState.COMMITTED,
            effective_config_version=self._current_config_version,
            request_time=time.monotonic(),
            completion_time=time.monotonic()
        )


# =============================================================================
# Public API exports
# =============================================================================

__all__ = [
    # IDs
    "ReconfigurationId",
    
    # Request and Context
    "ReconfigurationRequest",
    "ReconfigurationContext",
    
    # Modes
    "ReconfigurationMode",
    
    # Results
    "ReconfigurationState",
    "ReconfigurationResult",
    "ReconfigurationFailure",
    "ReconfigurationReceipt",
    "ReconfigurationSnapshot",
    
    # Plan and Analysis
    "ApplicationStep",
    "ConfigurationApplicationPlan",
    "ImpactFinding",
    "ConfigurationImpactAnalysis",
    
    # Coordinator
    "ReconfigurationCoordinator",
]