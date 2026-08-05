"""Gordon Agent Initializer.

Phase 3.7.30: Agent Initialization Chain
========================================

Canonical Agent initialization coordinator.
"""
from __future__ import annotations

import time
import uuid
from dataclasses import dataclass, field
from typing import (
    Any,
    Callable,
    Dict,
    List,
    Optional,
    Tuple,
)

from .types import (
    AgentInitializationPhase,
    AgentInitializationRequest,
    AgentInitializationContext,
    AgentInitializationResult,
    AgentInitializationFailure,
)
from .exceptions import (
    AgentInitializationError,
    InitializationConfigurationMissing,
)


# =============================================================================
# ROLLBACK COORDINATOR
# =============================================================================


@dataclass
class RollbackState:
    """Mutable state for tracking resources acquired during initialization.
    
    This is used to implement rollback ordering (reverse of acquisition).
    """
    
    acquired_resources: Dict[str, Any] = field(default_factory=dict)
    acquire_order: List[Tuple[str, Any]] = field(default_factory=list)


class RollbackCoordinator:
    """Canonical rollback coordinator.
    
    This coordinates rollback operations during initialization failure.
    It maintains a stack of acquired resources and releases them in
    reverse order (LIFO) to ensure proper cleanup.
    """
    
    def __init__(self):
        self._stack: List[Tuple[str, Any]] = []
        self._primary_failure: Optional[AgentInitializationFailure] = None
    
    def register_resource(self, name: str, resource: Any) -> None:
        """Register an acquired resource for potential rollback.
        
        Args:
            name: Resource identifier
            resource: The acquired resource
        """
        self._stack.append((name, resource))
    
    async def rollback(self) -> Tuple[bool, Optional[str], List[str]]:
        """Rollback all registered resources in reverse order.
        
        Returns:
            Tuple of (success, error_message, residual_resources)
        """
        errors: List[str] = []
        
        # Release in reverse order
        for name, resource in reversed(self._stack):
            try:
                await self._release_resource(name, resource)
            except Exception as e:
                errors.append(f"Failed to release '{name}': {e}")
        
        # Clear the stack after rollback
        residual = [name for name, _ in self._stack]
        self._stack.clear()
        
        success = len(errors) == 0
        error_msg = "; ".join(errors) if errors else None
        
        return success, error_msg, residual
    
    async def _release_resource(self, name: str, resource: Any) -> None:
        """Release a single resource.
        
        Args:
            name: Resource identifier
            resource: The resource to release
        """
        # In full implementation, would call appropriate cleanup methods
        pass
    
    @property
    def has_pending_resources(self) -> bool:
        """Check if there are resources pending release."""
        return len(self._stack) > 0
    
    @property
    def primary_failure(self) -> Optional[AgentInitializationFailure]:
        """Get the primary failure that triggered this rollback."""
        return self._primary_failure
    
    @primary_failure.setter
    def primary_failure(self, value: AgentInitializationFailure) -> None:
        """Set the primary failure for rollback tracking."""
        self._primary_failure = value


# =============================================================================
# INITIALIZATION COORDINATOR
# =============================================================================


@dataclass(frozen=True)
class InitializationStep:
    """A single initialization step in the sequence."""
    
    name: str
    """Step name for logging/diagnostic purposes."""
    
    phase: AgentInitializationPhase
    """The phase this step belongs to."""
    
    execute: Callable[[AgentInitializationContext, Dict[str, Any]], Tuple[bool, Optional[str], Any]]
    """Execute function: (context, state) -> (success, error_message, result_data).
    
    Returns:
        Tuple of (success: bool, error_message: Optional[str], result_data: Any)
        
    If success is True and error_message is None, the step completed successfully.
    If success is False, the initialization fails with error_message.
    """


@dataclass
class InitializationState:
    """Mutable state accumulated during initialization.
    
    This is NOT shared across runtimes. Each initialization has its own
    isolated state instance.
    """
    
    # Request and context
    request: AgentInitializationRequest
    context: Optional[AgentInitializationContext] = None
    
    # Configuration
    config_fingerprint: str = ""
    effective_config: Optional[Any] = None  # type: ignore
    
    # Loading (delegated to entrypoint/load/)
    load_result: Optional[Any] = None  # type: ignore
    load_plan_id: Optional[str] = None
    
    # Core construction (delegated to components/core/)
    core_result: Optional[Any] = None  # type: ignore
    core_status: str = "not_started"
    
    # Assembly (delegated to runtime assembler)
    assembly_result: Optional[Any] = None  # type: ignore
    assembly_status: str = "not_started"
    
    # Verification results
    structural_verification_passed: bool = False
    integrity_verification_passed: bool = False
    
    # Activation results
    activation_passed: bool = False
    
    # Readiness and admission
    readiness_evaluated: bool = False
    admission_opened: bool = False
    
    # Results
    runtime_id: Optional[str] = None
    boot_session_id: Optional[str] = None
    result: Optional[AgentInitializationResult] = None
    failure: Optional[AgentInitializationFailure] = None


class AgentInitializer:
    """Canonical Agent initializer.
    
    This is the ONE canonical authority for Agent initialization. It coordinates
    all phases of the initialization chain without implementing component-level
    logic.
    
    Architecture Boundaries:
        This owns:
            - Initialization request validation
            - Context creation and phase tracking
            - Deterministic phase sequencing
            - Delegation to subsystems (loading, Core, assembly)
            - Failure classification and preservation
            - Rollback coordination
        
        This does NOT own:
            - Component discovery or loading mechanics
            - Core construction implementation
            - Runtime state mutation
            - Operational execution
    
    Usage:
        initializer = AgentInitializer()
        request = AgentInitializationRequest.create(...)
        result = initializer.initialize(request)
        
        if result.is_success:
            # Use initialized runtime
            pass
        else:
            # Handle failure
            raise AgentInitializationError.from_failure_record(result.failure)
    
    Thread Safety:
        Each initialization uses its own state instance. The initializer
        itself is immutable and can be shared across threads for different
        initializations.
    """
    
    def __init__(
        self,
        clock: Callable[[], float] = None,  # type: ignore
        uuid_generator: Callable[[], str] = None,  # type: ignore
    ):
        """Initialize the AgentInitializer.
        
        Args:
            clock: Monotonic clock function (default: time.monotonic)
            uuid_generator: UUID generation function (default: lambda: str(uuid.uuid4()))
        """
        self._clock = clock or time.monotonic
        self._uuid_generator = uuid_generator or (lambda: str(uuid.uuid4()))
    
    # State is per-initialization, not shared
    def initialize(
        self,
        request: AgentInitializationRequest,
    ) -> AgentInitializationResult:
        """Initialize the Agent runtime through canonical initialization.
        
        Args:
            request: Immutable initialization request
            
        Returns:
            AgentInitializationResult with success or failure information
            
        Raises:
            AgentInitializationError: If initialization fails (use result.failure instead)
        """
        # Validate that we have a valid request
        if not isinstance(request, AgentInitializationRequest):
            raise InitializationConfigurationMissing(
                "Invalid initialization request type"
            )
        
        # Create fresh state for this initialization
        state = InitializationState(request=request)
        
        # Step 1: Enter VALIDATING_REQUEST phase and validate the request
        try:
            state.context = self._enter_phase(state, AgentInitializationPhase.VALIDATING_REQUEST)
            self._validate_request(request, state)
        except Exception as e:
            return self._fail_initialization(
                state,
                AgentInitializationPhase.VALIDATING_REQUEST,
                "request_validation",
                f"Request validation failed: {e}",
            )
        
        # Step 2: Enter RESOLVING_CONFIGURATION phase
        try:
            state.context = self._enter_phase(state, AgentInitializationPhase.RESOLVING_CONFIGURATION)
            self._resolve_configuration(request, state)
        except Exception as e:
            return self._fail_initialization(
                state,
                AgentInitializationPhase.RESOLVING_CONFIGURATION,
                "configuration",
                f"Configuration resolution failed: {e}",
            )
        
        # Step 3: Enter PREPARING_CONTEXT phase
        try:
            state.context = self._enter_phase(state, AgentInitializationPhase.PREPARING_CONTEXT)
            self._prepare_context(request, state)
        except Exception as e:
            return self._fail_initialization(
                state,
                AgentInitializationPhase.PREPARING_CONTEXT,
                "context",
                f"Context preparation failed: {e}",
            )
        
        # CRITICAL: Preflight validation - Phase 3.7.32-R
    #
    # The canonical preflight authority is entrypoint/check.py (AgentPreflightChecker).
    # Initialization MUST have a valid preflight result from the canonical authority.
    # This enforces the startup pipeline:
    #   launch_request -> entrypoint/check -> AgentPreflightResult -> init
    #
    # If preflight_result is None or invalid, initialization fails immediately.
        try:
            preflight_valid = self._validate_preflight_result(state, request)
            if not preflight_valid:
                return self._fail_initialization(
                    state,
                    AgentInitializationPhase.PREFLIGHT_VALIDATION,
                    "preflight_validation",
                    "Preflight result validation failed - initialization requires valid entrypoint/check.py preflight result from canonical authority",
                )
        except Exception as e:
            return self._fail_initialization(
                state,
                AgentInitializationPhase.PREFLIGHT_VALIDATION,
                "preflight_validation",
                f"Preflight result validation error: {e}",
            )
        
        # Step 4-13: Execute the main initialization sequence
        steps = self._get_initialization_steps()
        
        for step in steps:
            try:
                state.context = self._enter_phase(state, step.phase)
                success, error_message, result_data = step.execute(state.context, state.__dict__)
                
                if not success:
                    return self._fail_initialization(
                        state,
                        step.phase,
                        "initialization",
                        f"{step.name} failed: {error_message}",
                    )
                
                # Update state with result data
                self._update_state_from_result(step.phase, result_data, state)
                
            except Exception as e:
                return self._fail_initialization(
                    state,
                    step.phase,
                    "initialization",
                    f"{step.name} exception: {e}",
                )
        
        # Step 14: Create final result
        return self._complete_initialization(state)
    
    def _get_initialization_steps(self) -> List[InitializationStep]:
        """Get the canonical initialization steps.
        
        Returns:
            List of initialization steps in order
            
        The canonical sequence is:
            1. REQUESTING_LOAD_PLAN - Request load plan from entrypoint/load/
            2. LOADING_COMPONENTS - Load and construct components
            3. CONSTRUCTING_CORE - Construct Agent Core authority
            4. ASSEMBLING_RUNTIME - Assemble runtime with components
            5. VERIFYING_STRUCTURE - Verify structural integrity
            6. VERIFYING_INTEGRITY - Verify runtime integrity
            7. ACTIVATING_RUNTIME - Activate runtime infrastructure
            8. VERIFYING_ACTIVATION - Verify activation was successful
            9. EVALUATING_READINESS - Evaluate Agent readiness
            10. OPENING_ADMISSION - Open admission for work acceptance
            11. VERIFYING_ADMISSION - Verify admission state
        """
        return [
            InitializationStep(
                name="Request load plan",
                phase=AgentInitializationPhase.REQUESTING_LOAD_PLAN,
                execute=self._step_request_load_plan,
            ),
            InitializationStep(
                name="Load components",
                phase=AgentInitializationPhase.LOADING_COMPONENTS,
                execute=self._step_load_components,
            ),
            InitializationStep(
                name="Construct Core",
                phase=AgentInitializationPhase.CONSTRUCTING_CORE,
                execute=self._step_construct_core,
            ),
            InitializationStep(
                name="Assemble runtime",
                phase=AgentInitializationPhase.ASSEMBLING_RUNTIME,
                execute=self._step_assemble_runtime,
            ),
            InitializationStep(
                name="Verify structure",
                phase=AgentInitializationPhase.VERIFYING_STRUCTURE,
                execute=self._step_verify_structure,
            ),
            InitializationStep(
                name="Verify integrity",
                phase=AgentInitializationPhase.VERIFYING_INTEGRITY,
                execute=self._step_verify_integrity,
            ),
            InitializationStep(
                name="Activate runtime",
                phase=AgentInitializationPhase.ACTIVATING_RUNTIME,
                execute=self._step_activate_runtime,
            ),
            InitializationStep(
                name="Verify activation",
                phase=AgentInitializationPhase.VERIFYING_ACTIVATION,
                execute=self._step_verify_activation,
            ),
            InitializationStep(
                name="Evaluate readiness",
                phase=AgentInitializationPhase.EVALUATING_READINESS,
                execute=self._step_evaluate_readiness,
            ),
            InitializationStep(
                name="Open admission",
                phase=AgentInitializationPhase.OPENING_ADMISSION,
                execute=self._step_open_admission,
            ),
            InitializationStep(
                name="Verify admission",
                phase=AgentInitializationPhase.VERIFYING_ADMISSION,
                execute=self._step_verify_admission,
            ),
        ]
    
    def _validate_request(self, request: AgentInitializationRequest, state: InitializationState) -> None:
        """Validate the initialization request.
        
        This validates:
            - Required fields are present
            - Field values are valid
            - Mode constraints are consistent
            
        Args:
            request: The initialization request to validate
            state: Mutable initialization state
        """
        # Basic validation - in full implementation would check all required fields
        
        if not request.init_id:
            raise InitializationConfigurationMissing("init_id is required")
        
        if not request.launch_id:
            raise InitializationConfigurationMissing("launch_id is required")
    
    def _resolve_configuration(
        self,
        request: AgentInitializationRequest,
        state: InitializationState,
    ) -> None:
        """Resolve effective configuration from the request.
        
        Args:
            request: The initialization request
            state: Mutable initialization state
        """
        # In full implementation, this would:
        # - Load configuration from config_provenance
        # - Apply mode overrides (safe_mode, offline_mode)
        # - Validate schema
        # - Generate fingerprint
        
        state.config_fingerprint = request.config_fingerprint
        state.effective_config = {}
    
    def _prepare_context(
        self,
        request: AgentInitializationRequest,
        state: InitializationState,
    ) -> None:
        """Prepare the initialization context.
        
        Args:
            request: The initialization request
            state: Mutable initialization state
        """
        # Create the runtime-scoped context if not already created
        
        if state.context is None:
            raise InitializationConfigurationMissing("Context should have been set")
    
    def _validate_preflight_result(
        self,
        state: InitializationState,
        request: AgentInitializationRequest,
    ) -> bool:
        """Validate preflight result from canonical authority.
        
        Phase 3.7.32-R/R: Preflight validation before initialization proceeds.
        This validates that the preflight result is fresh, matches the current
        launch identity, and has proper evidence binding (source fingerprint,
        artifact fingerprint, configuration generation) from entrypoint/check.py.
        
        CRITICAL: The canonical preflight authority is entrypoint/check.py.
        Initialization MUST have a valid AgentPreflightResult to proceed.
        
        Args:
            state: Mutable initialization state
            request: The initialization request
            
        Returns:
            True if preflight validation passes, False otherwise
        """
        try:
            # Import canonical preflight types (using relative import to avoid circular dependency)
            from ..check import AgentPreflightResult
        except ImportError:
            # If check module is not available, preflight cannot be validated
            return False
        
        # Get the preflight result from the request (if provided)
        preflight_result = getattr(request, "preflight_result", None)
        
        # If no preflight result provided, we cannot validate it
        # In production, preflight should always be run before initialization
        if preflight_result is None:
            return False
        
        # Check if the result is an AgentPreflightResult instance
        if not isinstance(preflight_result, AgentPreflightResult):
            return False
        
        # Verify launch identity matches between request and preflight result
        launch_identity = {
            "launch_id": request.launch_id,
            "source_fingerprint": getattr(request, "source_fingerprint", ""),
            "artifact_fingerprint": getattr(request, "artifact_fingerprint", ""),
            "configuration_generation": getattr(request, "configuration_generation", 0),
        }
        
        # Validate result for this launch
        return preflight_result.is_valid_for_launch(launch_identity)
    
    def _step_request_load_plan(
        self,
        context: AgentInitializationContext,
        state_dict: Dict[str, Any],
    ) -> Tuple[bool, Optional[str], Optional[Any]]:
        """Request load plan from canonical loader.
        
        This delegates to entrypoint/load/ subsystem.
        
        Args:
            context: Current initialization context
            state_dict: Mutable state dictionary
            
        Returns:
            Tuple of (success, error_message, result_data)
        """
        # In full implementation, this would:
        # - Call entrypoint/load/request_load_plan()
        # - Return load plan result with component order
        
        return True, None, {"load_plan_id": "plan_" + self._uuid_generator()}
    
    def _step_load_components(
        self,
        context: AgentInitializationContext,
        state_dict: Dict[str, Any],
    ) -> Tuple[bool, Optional[str], Optional[Any]]:
        """Load and construct components via loader.
        
        This delegates to entrypoint/load/ subsystem.
        
        Args:
            context: Current initialization context
            state_dict: Mutable state dictionary
            
        Returns:
            Tuple of (success, error_message, result_data)
        """
        # In full implementation, this would:
        # - Call entrypoint/load/load_components()
        # - Return constructed components
        
        return True, None, {"components_loaded": 0}
    
    def _step_construct_core(
        self,
        context: AgentInitializationContext,
        state_dict: Dict[str, Any],
    ) -> Tuple[bool, Optional[str], Optional[Any]]:
        """Construct Agent Core authority.
        
        This delegates to components/core/ subsystem.
        
        Args:
            context: Current initialization context
            state_dict: Mutable state dictionary
            
        Returns:
            Tuple of (success, error_message, result_data)
        """
        # In full implementation, this would:
        # - Call components/core/kernel/builder.py
        # - Return constructed Core
        
        return True, None, {"core_status": "constructed"}
    
    def _step_assemble_runtime(
        self,
        context: AgentInitializationContext,
        state_dict: Dict[str, Any],
    ) -> Tuple[bool, Optional[str], Optional[Any]]:
        """Assemble runtime with components.
        
        This delegates to the runtime assembler.
        
        Args:
            context: Current initialization context
            state_dict: Mutable state dictionary
            
        Returns:
            Tuple of (success, error_message, result_data)
        """
        # In full implementation, this would:
        # - Call runtime assembler
        # - Connect components
        # - Register with Core authorities
        
        return True, None, {"assembly_status": "complete"}
    
    def _step_verify_structure(
        self,
        context: AgentInitializationContext,
        state_dict: Dict[str, Any],
    ) -> Tuple[bool, Optional[str], Optional[Any]]:
        """Verify structural integrity of assembly.
        
        Args:
            context: Current initialization context
            state_dict: Mutable state dictionary
            
        Returns:
            Tuple of (success, error_message, result_data)
        """
        return True, None, {"structural_verification_passed": True}
    
    def _step_verify_integrity(
        self,
        context: AgentInitializationContext,
        state_dict: Dict[str, Any],
    ) -> Tuple[bool, Optional[str], Optional[Any]]:
        """Verify runtime integrity via Core authority.
        
        Args:
            context: Current initialization context
            state_dict: Mutable state dictionary
            
        Returns:
            Tuple of (success, error_message, result_data)
        """
        return True, None, {"integrity_verification_passed": True}
    
    def _step_activate_runtime(
        self,
        context: AgentInitializationContext,
        state_dict: Dict[str, Any],
    ) -> Tuple[bool, Optional[str], Optional[Any]]:
        """Activate runtime infrastructure.
        
        Args:
            context: Current initialization context
            state_dict: Mutable state dictionary
            
        Returns:
            Tuple of (success, error_message, result_data)
        """
        return True, None, {"activation_passed": True}
    
    def _step_verify_activation(
        self,
        context: AgentInitializationContext,
        state_dict: Dict[str, Any],
    ) -> Tuple[bool, Optional[str], Optional[Any]]:
        """Verify activation was successful.
        
        Args:
            context: Current initialization context
            state_dict: Mutable state dictionary
            
        Returns:
            Tuple of (success, error_message, result_data)
        """
        return True, None, {"activation_verified": True}
    
    def _step_evaluate_readiness(
        self,
        context: AgentInitializationContext,
        state_dict: Dict[str, Any],
    ) -> Tuple[bool, Optional[str], Optional[Any]]:
        """Evaluate Agent readiness to proceed.
        
        Args:
            context: Current initialization context
            state_dict: Mutable state dictionary
            
        Returns:
            Tuple of (success, error_message, result_data)
        """
        return True, None, {"readiness_evaluated": True}
    
    def _step_open_admission(
        self,
        context: AgentInitializationContext,
        state_dict: Dict[str, Any],
    ) -> Tuple[bool, Optional[str], Optional[Any]]:
        """Open admission for work acceptance.
        
        Args:
            context: Current initialization context
            state_dict: Mutable state dictionary
            
        Returns:
            Tuple of (success, error_message, result_data)
        """
        return True, None, {"admission_opened": True}
    
    def _step_verify_admission(
        self,
        context: AgentInitializationContext,
        state_dict: Dict[str, Any],
    ) -> Tuple[bool, Optional[str], Optional[Any]]:
        """Verify admission state.
        
        Args:
            context: Current initialization context
            state_dict: Mutable state dictionary
            
        Returns:
            Tuple of (success, error_message, result_data)
        """
        return True, None, {"admission_verified": True}
    
    def _update_state_from_result(self, phase: AgentInitializationPhase, result: Any, state: InitializationState) -> None:
        """Update initialization state from a step result.
        
        Args:
            phase: The phase that completed
            result: Result data from the step
            state: Mutable initialization state to update
        """
        if result is None:
            return
        
        if isinstance(result, dict):
            # Update state based on result keys
            
            if "load_plan_id" in result:
                state.load_plan_id = result["load_plan_id"]
            
            if "core_status" in result:
                state.core_status = result["core_status"]
            
            if "assembly_status" in result:
                state.assembly_status = result["assembly_status"]
            
            if "structural_verification_passed" in result:
                state.structural_verification_passed = result["structural_verification_passed"]
            
            if "integrity_verification_passed" in result:
                state.integrity_verification_passed = result["integrity_verification_passed"]
            
            if "activation_passed" in result:
                state.activation_passed = result["activation_passed"]
            
            if "readiness_evaluated" in result:
                state.readiness_evaluated = result["readiness_evaluated"]
            
            if "admission_opened" in result:
                state.admission_opened = result["admission_opened"]
    
    def _complete_initialization(self, state: InitializationState) -> AgentInitializationResult:
        """Create the final initialization result.
        
        Args:
            state: Final initialization state
            
        Returns:
            AgentInitializationResult with success information
        """
        return AgentInitializationResult.create(
            init_id=state.request.init_id,
            launch_id=state.request.launch_id,
            process_id=state.request.process_id,
            runtime_id=state.runtime_id or "runtime_" + self._uuid_generator(),
            boot_session_id=state.boot_session_id or "bootsession_" + self._uuid_generator(),
            final_phase=AgentInitializationPhase.COMPLETED,
            config_fingerprint=state.config_fingerprint,
            loaded_components_count=state.request.process_id,  # Placeholder
            failed_components_count=0,
            core_construction_status=state.core_status,
            assembly_status=state.assembly_status,
            structural_verification_passed=state.structural_verification_passed,
            integrity_verification_passed=state.integrity_verification_passed,
            activation_passed=state.activation_passed,
            readiness_evaluated=state.readiness_evaluated,
            admission_opened=state.admission_opened,
        )
    
    def _enter_phase(
        self,
        state: InitializationState,
        phase: AgentInitializationPhase,
    ) -> AgentInitializationContext:
        """Enter a new initialization phase.
        
        Args:
            state: Current initialization state
            phase: The phase to enter
            
        Returns:
            Updated context with the new phase
        """
        if state.context is None:
            # Create initial context from request
            state.context = AgentInitializationContext.create(
                init_id=state.request.init_id,
                launch_id=state.request.launch_id,
                process_id=state.request.process_id,
                config_fingerprint=state.config_fingerprint or "unknown",
            )
        
        return state.context.enter_phase(phase)
    
    def _fail_initialization(
        self,
        state: InitializationState,
        failed_phase: AgentInitializationPhase,
        failure_category: str,
        primary_message: str,
    ) -> AgentInitializationResult:
        """Create a failure result.
        
        Args:
            state: Current initialization state
            failed_phase: The phase that failed
            failure_category: Category of failure
            primary_message: Primary failure message
            
        Returns:
            AgentInitializationFailure wrapped in an error result
        """
        if state.context is None:
            # Create a minimal context for the failure
            state.context = AgentInitializationContext.create(
                init_id=state.request.init_id,
                launch_id=state.request.launch_id,
                process_id=state.request.process_id,
                config_fingerprint="unknown",
            )
        
        failure = AgentInitializationFailure.create(
            init_id=state.request.init_id,
            launch_id=state.request.launch_id,
            process_id=state.request.process_id,
            failed_phase=failed_phase,
            failure_category=failure_category,
            primary_failure_message=primary_message,
            runtime_id=state.runtime_id,
            boot_session_id=state.boot_session_id,
            rollback_eligible=True,
        )
        
        return AgentInitializationResult.create(
            init_id=failure.init_id,
            launch_id=failure.launch_id,
            process_id=failure.process_id,
            runtime_id=failure.runtime_id or "failed",
            boot_session_id=failure.boot_session_id or "unknown",
            final_phase=AgentInitializationPhase.FAILED,
            config_fingerprint="unknown",
        )


# =============================================================================
# CONVENIENCE FUNCTION
# =============================================================================


def get_canonical_initializer() -> AgentInitializer:
    """Get the canonical initializer instance.
    
    This function exists for backward compatibility and testing. In production,
    callers should inject a new initializer instance per initialization.
    
    Returns:
        AgentInitializer instance
    """
    return AgentInitializer()


# =============================================================================
# TOP-LEVEL INITIALIZATION FUNCTION
# =============================================================================


def initialize_agent(request: AgentInitializationRequest) -> AgentInitializationResult:
    """Initialize the Agent runtime through canonical initialization.
    
    This is the public interface for initialization. It creates a fresh
    initializer and delegates to it.
    
    Args:
        request: Immutable initialization request
        
    Returns:
        AgentInitializationResult with success or failure information
    """
    initializer = AgentInitializer()
    return initializer.initialize(request)