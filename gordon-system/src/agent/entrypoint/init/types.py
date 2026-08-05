"""Gordon Agent Initialization Type Definitions.

Phase 3.7.30: Agent Initialization Chain
========================================

Immutable type models for initialization operations.
"""
from __future__ import annotations

import uuid
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum, auto
from typing import (
    Any,
    Dict,
    List,
    Optional,
    Tuple,
)


# =============================================================================
# INITIALIZATION PHASES (canonical state machine)
# =============================================================================


class AgentInitializationPhase(Enum):
    """Canonical initialization phase enumeration.
    
    Defines the deterministic initialization sequence:
        CREATED -> VALIDATING_REQUEST -> RESOLVING_CONFIGURATION
        -> PREPARING_CONTEXT -> REQUESTING_LOAD_PLAN -> LOADING_COMPONENTS
        -> CONSTRUCTING_CORE -> ASSEMBLING_RUNTIME -> VERIFYING_STRUCTURE
        -> VERIFYING_INTEGRITY -> ACTIVATING_RUNTIME -> VERIFYING_ACTIVATION
        -> EVALUATING_READINESS -> OPENING_ADMISSION -> VERIFYING_ADMISSION
        -> COMPLETED
        
    Invalid transitions must be rejected and diagnosed.
    """
    
    # Initial state
    CREATED = auto()
    """Initializer instantiated but not started."""
    
    # Request validation phase
    VALIDATING_REQUEST = auto()
    """Validating initialization request structure and data."""
    
    # Configuration phase
    RESOLVING_CONFIGURATION = auto()
    """Resolving effective configuration from request."""
    
    PREPARING_CONTEXT = auto()
    """Preparing runtime-scoped initialization context."""
    
    PREFLIGHT_VALIDATION = auto()
    """Validating preflight result from canonical authority (Phase 3.7.32)."""
    
    # Loading phase (delegated to entrypoint/load/)
    REQUESTING_LOAD_PLAN = auto()
    """Requesting load plan from canonical loader."""
    
    LOADING_COMPONENTS = auto()
    """Loading and constructing components via loader."""
    
    # Core construction phase
    CONSTRUCTING_CORE = auto()
    """Constructing Agent Core authority."""
    
    # Assembly phase
    ASSEMBLING_RUNTIME = auto()
    """Assembling runtime with constructed components."""
    
    # Verification phases
    VERIFYING_STRUCTURE = auto()
    """Verifying structural integrity of assembly."""
    
    VERIFYING_INTEGRITY = auto()
    """Verifying runtime integrity via Core authority."""
    
    # Activation phase
    ACTIVATING_RUNTIME = auto()
    """Activating runtime infrastructure."""
    
    VERIFYING_ACTIVATION = auto()
    """Verifying activation was successful."""
    
    # Readiness and admission phases
    EVALUATING_READINESS = auto()
    """Evaluating Agent readiness to proceed."""
    
    OPENING_ADMISSION = auto()
    """Opening admission for work acceptance."""
    
    VERIFYING_ADMISSION = auto()
    """Verifying admission state."""
    
    # Terminal states
    COMPLETED = auto()
    """Initialization completed successfully."""
    
    CANCELLING = auto()
    """Cancellation initiated during initialization."""
    
    ROLLING_BACK = auto()
    """Rolling back partial initialization."""
    
    FAILED = auto()
    """Initialization failed (terminal)."""
    
    CANCELLED = auto()
    """Initialization was cancelled (terminal)."""


# =============================================================================
# INITIALIZATION RESULT TYPES
# =============================================================================


@dataclass(frozen=True)
class AgentInitializationResult:
    """Immutable result of a successful initialization.
    
    This is the canonical output contract for initialization. It contains
    all necessary information about the initialized Agent runtime without
    exposing mutable internal state.
    """
    
    # Identity and provenance
    init_id: str
    """Unique initialization operation ID."""
    
    launch_id: str
    """Launch session ID from request."""
    
    process_id: int
    """Process ID where initialization occurred."""
    
    runtime_id: str
    """Runtime identity assigned during initialization."""
    
    boot_session_id: str
    """Boot session identifier for this initialization."""
    
    # Phase information
    final_phase: AgentInitializationPhase
    """The final phase reached (should be COMPLETED)."""
    
    timestamp_ns: int
    """Unix timestamp in nanoseconds when completed."""
    
    # Configuration provenance
    config_fingerprint: str
    """Fingerprint of effective configuration used."""
    
    load_plan_id: Optional[str]
    """Load plan ID if components were loaded."""
    
    # Component summary
    loaded_components_count: int
    """Number of successfully loaded components."""
    
    failed_components_count: int
    """Number of components that failed to load."""
    
    unavailable_capabilities: Tuple[str, ...]
    """Capabilities marked as unavailable during loading."""
    
    optional_skipped_count: int
    """Number of skipped optional components."""
    
    # Core construction summary
    core_construction_status: str
    """Status string from Core construction (e.g., 'success', 'degraded')."""
    
    # Assembly summary
    assembly_status: str
    """Status string from runtime assembly."""
    
    # Verification results
    structural_verification_passed: bool
    """Whether structural verification passed."""
    
    integrity_verification_passed: bool
    """Whether integrity verification passed."""
    
    activation_passed: bool
    """Whether activation verification passed."""
    
    readiness_evaluated: bool
    """Whether readiness evaluation was performed."""
    
    admission_opened: bool
    """Whether admission was successfully opened."""
    
    # Operational interface (lightweight)
    operational_interface_type: str
    """Type of operational interface available."""
    
    # Degraded restrictions
    degraded_restrictions: Tuple[str, ...]
    """Any degradation restrictions applied."""
    
    # Diagnostics reference (bounded)
    diagnostics_ref: Optional[str]
    """Reference to detailed diagnostics if available."""
    
    @property
    def is_success(self) -> bool:
        """Check if initialization completed successfully."""
        return self.final_phase == AgentInitializationPhase.COMPLETED
    
    @classmethod
    def create(
        cls,
        init_id: str,
        launch_id: str,
        process_id: int,
        runtime_id: str,
        boot_session_id: str,
        final_phase: AgentInitializationPhase,
        config_fingerprint: str,
        loaded_components_count: int = 0,
        failed_components_count: int = 0,
        unavailable_capabilities: Optional[Tuple[str, ...]] = None,
        optional_skipped_count: int = 0,
        core_construction_status: str = "success",
        assembly_status: str = "complete",
        structural_verification_passed: bool = True,
        integrity_verification_passed: bool = True,
        activation_passed: bool = True,
        readiness_evaluated: bool = False,
        admission_opened: bool = False,
        degraded_restrictions: Optional[Tuple[str, ...]] = None,
    ) -> "AgentInitializationResult":
        """Create a new initialization result.
        
        Args:
            init_id: Unique initialization operation ID
            launch_id: Launch session ID from request
            process_id: Process ID where initialization occurred
            runtime_id: Runtime identity assigned during initialization
            boot_session_id: Boot session identifier for this initialization
            final_phase: The final phase reached (should be COMPLETED)
            config_fingerprint: Fingerprint of effective configuration used
            loaded_components_count: Number of successfully loaded components
            failed_components_count: Number of components that failed to load
            unavailable_capabilities: Capabilities marked as unavailable during loading
            optional_skipped_count: Number of skipped optional components
            core_construction_status: Status from Core construction
            assembly_status: Status from runtime assembly
            structural_verification_passed: Whether structural verification passed
            integrity_verification_passed: Whether integrity verification passed
            activation_passed: Whether activation verification passed
            readiness_evaluated: Whether readiness evaluation was performed
            admission_opened: Whether admission was successfully opened
            degraded_restrictions: Any degradation restrictions applied
            
        Returns:
            New AgentInitializationResult instance
        """
        now_ns = int(datetime.now().timestamp() * 1_000_000_000)
        
        return cls(
            init_id=init_id,
            launch_id=launch_id,
            process_id=process_id,
            runtime_id=runtime_id,
            boot_session_id=boot_session_id,
            final_phase=final_phase,
            timestamp_ns=now_ns,
            config_fingerprint=config_fingerprint,
            load_plan_id=None,  # Would be set in full implementation
            loaded_components_count=loaded_components_count,
            failed_components_count=failed_components_count,
            unavailable_capabilities=unavailable_capabilities or (),
            optional_skipped_count=optional_skipped_count,
            core_construction_status=core_construction_status,
            assembly_status=assembly_status,
            structural_verification_passed=structural_verification_passed,
            integrity_verification_passed=integrity_verification_passed,
            activation_passed=activation_passed,
            readiness_evaluated=readiness_evaluated,
            admission_opened=admission_opened,
            operational_interface_type="canonical",
            degraded_restrictions=degraded_restrictions or (),
            diagnostics_ref=None,
        )
    
    def with_load_plan_id(self, load_plan_id: str) -> "AgentInitializationResult":
        """Return a new result with the given load plan ID."""
        return dataclass_replace(self, load_plan_id=load_plan_id)


@dataclass(frozen=True)
class AgentInitializationFailure:
    """Immutable failure record for initialization.
    
    This is the canonical output contract for failed initialization. It contains
    full diagnostic information while preserving the primary failure and
    maintaining rollback eligibility evidence.
    """
    
    # Identity
    init_id: str
    """Unique initialization operation ID."""
    
    launch_id: str
    """Launch session ID from request."""
    
    process_id: int
    """Process ID where failure occurred."""
    
    runtime_id: Optional[str]
    """Runtime identity (if assigned before failure)."""
    
    boot_session_id: Optional[str]
    """Boot session identifier (if created)."""
    
    # Failure classification
    failed_phase: AgentInitializationPhase
    """The phase that failed."""
    
    failure_category: str
    """Category of failure (configuration, loading, core, assembly, etc.)."""
    
    primary_failure_message: str
    """Primary failure message or exception description."""
    
    primary_failure_type: Optional[str]
    """Type/class name of the primary exception if available."""
    
    # Secondary failures (non-cascading)
    secondary_failures: Tuple[str, ...]
    """Secondary failure messages that did not cascade."""
    
    # Recovery evidence
    partial_construction_summary: str
    """Summary of what was partially constructed before failure."""
    
    rollback_eligible: bool
    """Whether rollback is eligible for this failure."""
    
    rollback_result: Optional[str]
    """Result of rollback attempt if performed."""
    
    retry_eligible: bool
    """Whether initialization can be retried."""
    
    # Diagnostics reference (bounded, secret-safe)
    diagnostics_ref: Optional[str]
    """Reference to detailed diagnostics if available."""
    
    # Provenance
    timestamp_ns: int
    """Unix timestamp in nanoseconds when failure occurred."""
    
    @classmethod
    def create(
        cls,
        init_id: str,
        launch_id: str,
        process_id: int,
        failed_phase: AgentInitializationPhase,
        failure_category: str,
        primary_failure_message: str,
        runtime_id: Optional[str] = None,
        boot_session_id: Optional[str] = None,
        secondary_failures: Optional[Tuple[str, ...]] = None,
        partial_construction_summary: str = "none",
        rollback_eligible: bool = True,
        rollback_result: Optional[str] = None,
        retry_eligible: bool = False,
    ) -> "AgentInitializationFailure":
        """Create a new initialization failure record.
        
        Args:
            init_id: Unique initialization operation ID
            launch_id: Launch session ID from request
            process_id: Process ID where failure occurred
            failed_phase: The phase that failed
            failure_category: Category of failure (configuration, loading, etc.)
            primary_failure_message: Primary failure message or exception description
            runtime_id: Runtime identity (if assigned before failure)
            boot_session_id: Boot session identifier (if created)
            secondary_failures: Secondary failure messages
            partial_construction_summary: Summary of what was partially constructed
            rollback_eligible: Whether rollback is eligible
            rollback_result: Result of rollback attempt if performed
            retry_eligible: Whether initialization can be retried
            
        Returns:
            New AgentInitializationFailure instance
        """
        now_ns = int(datetime.now().timestamp() * 1_000_000_000)
        
        return cls(
            init_id=init_id,
            launch_id=launch_id,
            process_id=process_id,
            runtime_id=runtime_id,
            boot_session_id=boot_session_id,
            failed_phase=failed_phase,
            failure_category=failure_category,
            primary_failure_message=primary_failure_message,
            primary_failure_type=None,  # Would be set in full implementation
            secondary_failures=secondary_failures or (),
            partial_construction_summary=partial_construction_summary,
            rollback_eligible=rollback_eligible,
            rollback_result=rollback_result,
            retry_eligible=retry_eligible,
            diagnostics_ref=None,
            timestamp_ns=now_ns,
        )


# =============================================================================
# INITIALIZATION REQUEST
# =============================================================================


@dataclass(frozen=True)
class AgentInitializationRequest:
    """Immutable initialization request.
    
    This is the canonical input contract for initialization. All fields are
    explicitly declared and validated before any initialization occurs.
    
    The request must be fully populated at construction time with no mutable
    state or runtime objects contained within.
    """
    
    # Identity and provenance
    init_id: str
    """Unique initialization operation ID."""
    
    launch_id: str
    """Launch session ID (from AgentLaunchRequest.launch_identity.launch_id)."""
    
    process_id: int
    """Process ID where initialization will occur."""
    
    invocation_surface: str
    """How the Agent was invoked (for context only)."""
    
    # Runtime identity reservation
    runtime_id_reservation: Optional[str]
    """Optional pre-reserved runtime ID for idempotency."""
    
    boot_session_id_reservation: Optional[str]
    """Optional pre-reserved boot session ID."""
    
    # Configuration reference
    config_fingerprint: str
    """Fingerprint of validated effective configuration."""
    
    config_provenance: Dict[str, Any]
    """Configuration provenance metadata (frozen, no secrets)."""
    
    # Mode and constraints
    run_mode: str
    """Operational mode string (default, safe, offline, validation_only)."""
    
    bridge_policy: str
    """Assistant bridge policy (required, optional, disabled)."""
    
    safe_mode_enabled: bool = False
    """Enable safe mode restrictions."""
    
    offline_mode_enabled: bool = False
    """Enable offline mode restrictions."""
    
    validation_only: bool = False
    """Validation-only mode (stop after certain phases)."""
    
    # Deadlines
    startup_deadline_seconds: float = 30.0
    """Maximum time allowed for initialization."""
    
    shutdown_deadline_seconds: float = 15.0
    """Maximum time allowed for graceful shutdown."""
    
    phase_timeouts: Dict[AgentInitializationPhase, float] = field(default_factory=dict)
    """Per-phase timeout overrides (optional)."""
    
    # Cancellation and correlation
    cancellation_token: Optional[str] = None
    """Optional cancellation token reference."""
    
    correlation_id: Optional[str] = None
    """Correlation context ID for tracing."""
    
    causation_id: Optional[str] = None
    """Causation event ID if invoked in response to another event."""
    
    # Provenance
    raw_arguments: Tuple[str, ...] = field(default_factory=tuple)
    """Raw command-line arguments as passed to main()."""
    
    parent_system_id: Optional[str] = None
    """Parent system ID if applicable."""
    
    @property
    def is_validation_only(self) -> bool:
        """Check if validation-only mode is enabled."""
        return self.validation_only
    
    @property
    def is_safe_mode(self) -> bool:
        """Check if safe mode is enabled."""
        return self.safe_mode_enabled
    
    @property
    def is_offline(self) -> bool:
        """Check if offline mode is enabled."""
        return self.offline_mode_enabled
    
    @classmethod
    def create(
        cls,
        launch_id: str,
        process_id: int,
        config_fingerprint: str,
        config_provenance: Optional[Dict[str, Any]] = None,
        run_mode: str = "default",
        bridge_policy: str = "optional",
        **kwargs
    ) -> "AgentInitializationRequest":
        """Create a new initialization request.
        
        Args:
            launch_id: Launch session ID from AgentLaunchRequest
            process_id: Process ID where initialization will occur
            config_fingerprint: Fingerprint of validated effective configuration
            config_provenance: Configuration provenance metadata (frozen, no secrets)
            run_mode: Operational mode string
            bridge_policy: Assistant bridge policy
            
        Additional kwargs:
            runtime_id_reservation, boot_session_id_reservation
            validation_only, safe_mode_enabled, offline_mode_enabled
            startup_deadline_seconds, shutdown_deadline_seconds
            cancellation_token, correlation_id, causation_id
            
        Returns:
            New AgentInitializationRequest instance
        """
        init_id = str(uuid.uuid4())
        
        return cls(
            init_id=init_id,
            launch_id=launch_id,
            process_id=process_id,
            invocation_surface=kwargs.get("invocation_surface", "unknown"),
            runtime_id_reservation=kwargs.get("runtime_id_reservation"),
            boot_session_id_reservation=kwargs.get("boot_session_id_reservation"),
            config_fingerprint=config_fingerprint,
            config_provenance=config_provenance or {},
            run_mode=run_mode,
            bridge_policy=bridge_policy,
            safe_mode_enabled=kwargs.get("safe_mode_enabled", False),
            offline_mode_enabled=kwargs.get("offline_mode_enabled", False),
            validation_only=kwargs.get("validation_only", False),
            startup_deadline_seconds=kwargs.get("startup_deadline_seconds", 30.0),
            shutdown_deadline_seconds=kwargs.get("shutdown_deadline_seconds", 15.0),
            phase_timeouts=kwargs.get("phase_timeouts", {}),
            cancellation_token=kwargs.get("cancellation_token"),
            correlation_id=kwargs.get("correlation_id"),
            causation_id=kwargs.get("causation_id"),
            raw_arguments=tuple(kwargs.get("raw_arguments", [])),
            parent_system_id=kwargs.get("parent_system_id"),
        )


# =============================================================================
# INITIALIZATION CONTEXT
# =============================================================================


@dataclass(frozen=True)
class AgentInitializationContext:
    """Runtime-scoped initialization context.
    
    This is created by the initializer once the request has been validated.
    It provides a narrow interface for subsystems to access initialization
    state without exposing mutable globals or service-locator capabilities.
    
    The context is scoped to one initialization operation and must not be
    shared across runtimes.
    """
    
    # Identity
    init_id: str
    """Unique initialization operation ID."""
    
    launch_id: str
    """Launch session ID from request."""
    
    process_id: int
    """Process ID where initialization is occurring."""
    
    runtime_id_reservation: Optional[str]
    """Optional pre-reserved runtime ID."""
    
    boot_session_id_reservation: Optional[str]
    """Optional pre-reserved boot session ID."""
    
    # Configuration reference (validated)
    config_fingerprint: str
    """Fingerprint of validated effective configuration."""
    
    # Phase tracking (must come before fields with defaults)
    current_phase: AgentInitializationPhase = field()
    """Current initialization phase."""
    
    completed_phases: Tuple[AgentInitializationPhase, ...] = field(default_factory=tuple)
    """Phases that have been successfully completed."""
    
    pending_phases: Tuple[AgentInitializationPhase, ...] = field(default_factory=tuple)
    """Phases remaining in the sequence."""
    
    # Phase ordering (for validation)
    _phase_order: Tuple[AgentInitializationPhase, ...] = field(default_factory=tuple)
    
    # Time tracking
    start_time_ns: int = 0
    """Start time in nanoseconds."""
    
    current_phase_start_ns: int = 0
    """Time when current phase began."""
    
    @property
    def duration_seconds(self) -> float:
        """Return elapsed time since initialization started."""
        import time
        return (time.time_ns() - self.start_time_ns) / 1_000_000_000
    
    @property
    def is_complete(self) -> bool:
        """Check if initialization has completed."""
        return self.current_phase in (
            AgentInitializationPhase.COMPLETED,
            AgentInitializationPhase.CANCELLED,
            AgentInitializationPhase.FAILED,
        )
    
    @classmethod
    def create(
        cls,
        init_id: str,
        launch_id: str,
        process_id: int,
        config_fingerprint: str,
        runtime_id_reservation: Optional[str] = None,
        boot_session_id_reservation: Optional[str] = None,
        current_phase: AgentInitializationPhase = AgentInitializationPhase.CREATED,
    ) -> "AgentInitializationContext":
        """Create a new initialization context.
        
        Args:
            init_id: Unique initialization operation ID
            launch_id: Launch session ID from request
            process_id: Process ID where initialization is occurring
            config_fingerprint: Fingerprint of validated effective configuration
            runtime_id_reservation: Optional pre-reserved runtime ID
            boot_session_id_reservation: Optional pre-reserved boot session ID
            
        Returns:
            New AgentInitializationContext instance in CREATED state
        """
        now_ns = int(datetime.now().timestamp() * 1_000_000_000)
        
        return cls(
            init_id=init_id,
            launch_id=launch_id,
            process_id=process_id,
            runtime_id_reservation=runtime_id_reservation,
            boot_session_id_reservation=boot_session_id_reservation,
            config_fingerprint=config_fingerprint,
            current_phase=current_phase,
            completed_phases=(),
            pending_phases=(),  # Will be set in full implementation
            _phase_order=(),  # Will be set in full implementation
            start_time_ns=now_ns,
            current_phase_start_ns=now_ns,
        )
    
    def enter_phase(self, new_phase: AgentInitializationPhase) -> "AgentInitializationContext":
        """Enter a new initialization phase.
        
        Validates that the transition is allowed and returns a new context.
        
        Args:
            new_phase: The phase to enter
            
        Returns:
            New AgentInitializationContext with updated phase state
            
        Raises:
            ValueError: If the phase transition is invalid
        """
        current = self.current_phase
        
        # Define valid transitions (deterministic)
        valid_transitions: Dict[AgentInitializationPhase, Tuple[AgentInitializationPhase, ...]] = {
            AgentInitializationPhase.CREATED: (
                AgentInitializationPhase.VALIDATING_REQUEST,
            ),
            AgentInitializationPhase.VALIDATING_REQUEST: (
                AgentInitializationPhase.RESOLVING_CONFIGURATION,
                AgentInitializationPhase.FAILED,
            ),
            AgentInitializationPhase.RESOLVING_CONFIGURATION: (
                AgentInitializationPhase.PREPARING_CONTEXT,
                AgentInitializationPhase.FAILED,
            ),
            AgentInitializationPhase.PREPARING_CONTEXT: (
                AgentInitializationPhase.PREFLIGHT_VALIDATION,
                AgentInitializationPhase.FAILED,
            ),
            AgentInitializationPhase.PREFLIGHT_VALIDATION: (
                AgentInitializationPhase.REQUESTING_LOAD_PLAN,
                AgentInitializationPhase.FAILED,
            ),
            AgentInitializationPhase.REQUESTING_LOAD_PLAN: (
                AgentInitializationPhase.LOADING_COMPONENTS,
                AgentInitializationPhase.FAILED,
            ),
            AgentInitializationPhase.LOADING_COMPONENTS: (
                AgentInitializationPhase.CONSTRUCTING_CORE,
                AgentInitializationPhase.FAILED,
            ),
            AgentInitializationPhase.CONSTRUCTING_CORE: (
                AgentInitializationPhase.ASSEMBLING_RUNTIME,
                AgentInitializationPhase.FAILED,
            ),
            AgentInitializationPhase.ASSEMBLING_RUNTIME: (
                AgentInitializationPhase.VERIFYING_STRUCTURE,
                AgentInitializationPhase.FAILED,
            ),
            AgentInitializationPhase.VERIFYING_STRUCTURE: (
                AgentInitializationPhase.VERIFYING_INTEGRITY,
                AgentInitializationPhase.FAILED,
            ),
            AgentInitializationPhase.VERIFYING_INTEGRITY: (
                AgentInitializationPhase.ACTIVATING_RUNTIME,
                AgentInitializationPhase.FAILED,
            ),
            AgentInitializationPhase.ACTIVATING_RUNTIME: (
                AgentInitializationPhase.VERIFYING_ACTIVATION,
                AgentInitializationPhase.FAILED,
            ),
            AgentInitializationPhase.VERIFYING_ACTIVATION: (
                AgentInitializationPhase.EVALUATING_READINESS,
                AgentInitializationPhase.FAILED,
            ),
            AgentInitializationPhase.EVALUATING_READINESS: (
                AgentInitializationPhase.OPENING_ADMISSION,
                AgentInitializationPhase.FAILED,
            ),
            AgentInitializationPhase.OPENING_ADMISSION: (
                AgentInitializationPhase.VERIFYING_ADMISSION,
                AgentInitializationPhase.FAILED,
            ),
            AgentInitializationPhase.VERIFYING_ADMISSION: (
                AgentInitializationPhase.COMPLETED,
                AgentInitializationPhase.FAILED,
            ),
            AgentInitializationPhase.COMPLETED: (),
            AgentInitializationPhase.CANCELLING: (
                AgentInitializationPhase.ROLLING_BACK,
                AgentInitializationPhase.CANCELLED,
            ),
            AgentInitializationPhase.ROLLING_BACK: (
                AgentInitializationPhase.FAILED,
                AgentInitializationPhase.CANCELLED,
            ),
            AgentInitializationPhase.FAILED: (),
            AgentInitializationPhase.CANCELLED: (),
        }
        
        valid_next = valid_transitions.get(current, ())
        
        if new_phase not in valid_next and new_phase != current:
            raise ValueError(
                f"Invalid phase transition from {current} to {new_phase}"
            )
        
        # Update completed and pending phases
        completed = tuple(set(self.completed_phases) | {current})
        pending_list = list(self.pending_phases)
        if current in pending_list:
            pending_list.remove(current)
        if new_phase not in completed and new_phase not in pending_list:
            pending_list.insert(0, new_phase)
        
        now_ns = int(datetime.now().timestamp() * 1_000_000_000)
        
        return dataclass_replace(
            self,
            current_phase=new_phase,
            completed_phases=completed,
            pending_phases=tuple(pending_list),
            current_phase_start_ns=now_ns,
        )
    
    def rollback(self) -> "AgentInitializationContext":
        """Return context for rollback phase.
        
        Returns:
            New AgentInitializationContext with ROLLING_BACK phase
        """
        return self.enter_phase(AgentInitializationPhase.ROLLING_BACK)
    
    def cancel(self) -> "AgentInitializationContext":
        """Return context for cancellation.
        
        Returns:
            New AgentInitializationContext with CANCELLING phase
        """
        return self.enter_phase(AgentInitializationPhase.CANCELLING)


# =============================================================================
# UTILITY FUNCTIONS
# =============================================================================


def dataclass_replace(instance: Any, **kwargs: Any) -> Any:
    """Replacement for dataclasses.replace that handles frozen dataclasses.
    
    Since our dataclasses are @dataclass(frozen=True), we need a way to create
    modified copies. This uses the underlying __dict__ to create new instances.
    """
    import copy
    
    cls = type(instance)
    new_dict = copy.copy(instance.__dict__)
    new_dict.update(kwargs)
    
    return cls(**new_dict)


# =============================================================================
# EXPORTS
# =============================================================================


__all__ = [
    # Phase model
    "AgentInitializationPhase",
    # Result types
    "AgentInitializationResult",
    "AgentInitializationFailure",
    # Request and context
    "AgentInitializationRequest",
    "AgentInitializationContext",
    # Utilities
    "dataclass_replace",
]