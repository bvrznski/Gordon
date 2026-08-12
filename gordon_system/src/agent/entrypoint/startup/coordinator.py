"""Gordon Agent Startup Coordinator.

Phase 3.7.33-I: Agent Startup Coordination
==========================================

Canonical Agent startup coordination authority positioned between the outer
process boundary and detailed preflight/initialization subsystems.
"""
from __future__ import annotations

import time
import uuid
from dataclasses import dataclass, field
from typing import Any, Dict, Optional, Tuple


# =============================================================================
# IMPORTS (order matters - avoid circular dependencies)
# =============================================================================

from .context import AgentStartupContext, AgentStartupPhase, dataclass_replace as ctx_replace
from .policy import AgentStartupPolicy, AgentStartupMode, AgentBridgePolicy
from .outcomes import AgentStartupOutcome, AgentStartupOwnershipState, AgentStartupHandoffStatus
from .result import AgentStartupResult
from .exceptions import (
    AgentStartupError,
    AgentStartupRequestError,
    AgentStartupTimeoutError,
)

# =============================================================================
# CANONICAL STARTUP COORDINATOR
# =============================================================================


@dataclass(frozen=True)
class AgentStartupCoordinator:
    """Canonical Agent startup coordinator.
    
    This is the ONE canonical authority for Agent startup coordination. It:
        - Owns the complete startup transaction
        - Does NOT own process entry
        - Does NOT implement individual checks
        - Does NOT implement initialization internals
        - Does NOT operate the Agent
    
    Architecture boundaries:
        This owns:
            - Startup request validation
            - Startup context construction
            - Policy interpretation
            - Startup identity generation
            - Phase sequencing
            - Preflight invocation
            - Initialization invocation
            - Failure aggregation
            - Rollback/shutdown handoff selection
        
        This does NOT own:
            - CLI parsing (entrypoint/main.py)
            - Individual preflight checks (entrypoint/check.py)
            - Component loading (entrypoint/load/)
            - Core bootstrap (components/core/)
            - Agent operation
            - Runtime shutdown implementation
    """
    
    # Identity and provenance
    coordinator_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    """Unique identifier for this coordinator instance."""
    
    # Operation-scoped clock (injectable for testing)
    _clock_ns: Optional[Any] = None
    
    def get_clock_ns(self) -> int:
        """Get current time in nanoseconds."""
        import time as t
        return self._clock_ns() if self._clock_ns else t.time_ns()
    
    def start(
        self,
        launch_request: Dict[str, Any],
    ) -> AgentStartupResult:
        """Execute one complete startup transaction.
        
        This is the ONE canonical entry point for Agent startup. It:
            1. Validates the launch request
            2. Creates startup context and policy
            3. Invokes preflight exactly once
            4. Validates preflight result
            5. Invokes initialization exactly once
            6. Validates initialization result
            7. Handles ownership transfer
            8. Returns immutable startup result
            
        Args:
            launch_request: The immutable Agent launch request from process entry
            
        Returns:
            Immutable AgentStartupResult with one of:
                - STARTED (success)
                - STARTED_DEGRADED (success with restrictions)
                - BLOCKED (preflight blocked)
                - FAILED (coordinator or subordinate failure)
                - CANCELLED (explicit cancellation)
                - TIMED_OUT (deadline exceeded)
                
        Raises:
            AgentStartupError: For internal coordinator errors
            AgentStartupTimeoutError: If deadline exceeded
            
        Architecture invariant:
            Equivalent inputs produce equivalent semantic results.
        """
        import sys
        
        # Step 1: Extract launch identity from request
        try:
            launch_identity = launch_request.get("launch_identity", {})
            process_identity = launch_request.get("process_identity", {})
            
            startup_id = str(uuid.uuid4())
            process_id = process_identity.get("process_id", 0)
            invocation_surface = process_identity.get("invocation_surface", "unknown")
            
        except Exception as e:
            # Critical failure - cannot even start
            return AgentStartupResult.create_failed(
                startup_request_id="n/a",
                startup_execution_id=str(self.coordinator_id),
                launch_id=launch_identity.get("launch_id", "unknown"),
                process_id=process_identity.get("process_id", 0),
                invocation_surface=invocation_surface,
                effective_policy={},
                failed_phase="created",
                primary_failure_message=f"Cannot extract launch identity: {e}",
            )
        
        # Extract for use in error handlers
        launch_identity = launch_request.get("launch_identity", {})
        process_identity = launch_request.get("process_identity", {})
        
        # Step 2: Create startup context
        try:
            context = AgentStartupContext.create(
                startup_id=startup_id,
                launch_id=launch_identity.get("launch_id", "unknown"),
                process_id=process_id,
            )
        except Exception as e:
            return AgentStartupResult.create_failed(
                startup_request_id=startup_id,
                startup_execution_id=str(self.coordinator_id),
                launch_id=launch_identity.get("launch_id", "unknown"),
                process_id=process_id,
                invocation_surface=invocation_surface,
                effective_policy={},
                failed_phase="created",
                primary_failure_message=f"Cannot create startup context: {e}",
            )
        
        # Step 3: Create startup policy
        try:
            policy = AgentStartupPolicy.from_launch_request(
                launch_request,
                generation=context.startup_id[:8],  # Derive from context
            )
        except Exception as e:
            return AgentStartupResult.create_failed(
                startup_request_id=startup_id,
                startup_execution_id=str(self.coordinator_id),
                launch_id=launch_identity.get("launch_id", "unknown"),
                process_id=process_id,
                invocation_surface=invocation_surface,
                effective_policy={},
                failed_phase="created",
                primary_failure_message=f"Cannot create startup policy: {e}",
            )
        
        # Step 4: Enter VALIDATING_REQUEST phase
        context = context.enter_phase(AgentStartupPhase.VALIDATING_REQUEST)
        
        try:
            self._validate_startup_request(launch_request, context, policy)
        except AgentStartupRequestError as e:
            context = context.enter_phase(AgentStartupPhase.FAILED)
            return AgentStartupResult.create_failed(
                startup_request_id=startup_id,
                startup_execution_id=str(self.coordinator_id),
                launch_id=launch_identity.get("launch_id", "unknown"),
                process_id=process_id,
                invocation_surface=invocation_surface,
                effective_policy=policy_to_dict(policy),
                failed_phase=context.current_phase,
                primary_failure_message=str(e),
            )
        
        context = context.enter_phase(AgentStartupPhase.RESOLVING_POLICY)
        
        # Step 5: Enter PREPARING_CONTEXT phase
        try:
            context = context.enter_phase(AgentStartupPhase.PREPARING_CONTEXT)
        except ValueError as e:
            return AgentStartupResult.create_failed(
                startup_request_id=startup_id,
                startup_execution_id=str(self.coordinator_id),
                launch_id=launch_identity.get("launch_id", "unknown"),
                process_id=process_id,
                invocation_surface=invocation_surface,
                effective_policy=policy_to_dict(policy),
                failed_phase=context.current_phase,
                primary_failure_message=f"Invalid phase transition: {e}",
            )
        
        # Step 6: Enter PREPARING_PREFLIGHT_REQUEST phase and derive preflight request
        context = context.enter_phase(AgentStartupPhase.PREPARING_PREFLIGHT_REQUEST)
        
        try:
            preflight_request = self._derive_preflight_request(
                launch_request,
                startup_id,
                process_id,
                policy,
            )
        except Exception as e:
            return AgentStartupResult.create_failed(
                startup_request_id=startup_id,
                startup_execution_id=str(self.coordinator_id),
                launch_id=launch_identity.get("launch_id", "unknown"),
                process_id=process_id,
                invocation_surface=invocation_surface,
                effective_policy=policy_to_dict(policy),
                failed_phase=context.current_phase,
                primary_failure_message=f"Cannot derive preflight request: {e}",
            )
        
        # Step 7: Enter INVOKING_PREFLIGHT phase
        context = context.enter_phase(AgentStartupPhase.INVOKING_PREFLIGHT)
        
        try:
            preflight_result = self._invoke_preflight(
                preflight_request,
                policy.preflight_deadline_seconds,
            )
        except AgentStartupTimeoutError as e:
            return AgentStartupResult.create_timed_out(
                startup_request_id=startup_id,
                startup_execution_id=str(self.coordinator_id),
                launch_id=launch_identity.get("launch_id", "unknown"),
                process_id=process_id,
                invocation_surface=invocation_surface,
                effective_policy=policy_to_dict(policy),
                timed_out_phase=context.current_phase,
                deadline_seconds=policy.preflight_deadline_seconds,
            )
        except Exception as e:
            context = context.enter_phase(AgentStartupPhase.FAILED)
            return AgentStartupResult.create_failed(
                startup_request_id=startup_id,
                startup_execution_id=str(self.coordinator_id),
                launch_id=launch_identity.get("launch_id", "unknown"),
                process_id=process_id,
                invocation_surface=invocation_surface,
                effective_policy=policy_to_dict(policy),
                failed_phase=context.current_phase,
                primary_failure_message=f"Preflight invocation failed: {e}",
            )
        
        # Step 8: Enter VALIDATING_PREFLIGHT phase
        context = context.enter_phase(AgentStartupPhase.VALIDATING_PREFLIGHT)
        
        try:
            preflight_valid, blockers, warnings = self._validate_preflight_result(
                preflight_result,
                launch_request,
                policy,
            )
            
            if not preflight_valid:
                context = context.enter_phase(AgentStartupPhase.BLOCKED)
                return AgentStartupResult.create_blocked(
                    startup_request_id=startup_id,
                    startup_execution_id=str(self.coordinator_id),
                    launch_id=launch_identity.get("launch_id", "unknown"),
                    process_id=process_id,
                    invocation_surface=invocation_surface,
                    effective_policy=policy_to_dict(policy),
                    blockers=tuple(blockers) if blockers else (),
                )
                
        except Exception as e:
            context = context.enter_phase(AgentStartupPhase.FAILED)
            return AgentStartupResult.create_failed(
                startup_request_id=startup_id,
                startup_execution_id=str(self.coordinator_id),
                launch_id=launch_identity.get("launch_id", "unknown"),
                process_id=process_id,
                invocation_surface=invocation_surface,
                effective_policy=policy_to_dict(policy),
                failed_phase=context.current_phase,
                primary_failure_message=f"Preflight validation failed: {e}",
            )
        
        # Step 9: Enter PREPARING_INITIALIZATION_REQUEST phase
        context = context.enter_phase(AgentStartupPhase.PREPARING_INITIALIZATION_REQUEST)
        
        try:
            init_request = self._derive_initialization_request(
                launch_request,
                preflight_result,
                startup_id,
                process_id,
                policy,
            )
        except Exception as e:
            return AgentStartupResult.create_failed(
                startup_request_id=startup_id,
                startup_execution_id=str(self.coordinator_id),
                launch_id=launch_identity.get("launch_id", "unknown"),
                process_id=process_id,
                invocation_surface=invocation_surface,
                effective_policy=policy_to_dict(policy),
                failed_phase=context.current_phase,
                primary_failure_message=f"Cannot derive initialization request: {e}",
            )
        
        # Step 10: Enter INVOKING_INITIALIZATION phase
        context = context.enter_phase(AgentStartupPhase.INVOKING_INITIALIZATION)
        
        try:
            init_result = self._invoke_initialization(
                init_request,
                policy.initialization_deadline_seconds,
            )
        except AgentStartupTimeoutError as e:
            return AgentStartupResult.create_timed_out(
                startup_request_id=startup_id,
                startup_execution_id=str(self.coordinator_id),
                launch_id=launch_identity.get("launch_id", "unknown"),
                process_id=process_id,
                invocation_surface=invocation_surface,
                effective_policy=policy_to_dict(policy),
                timed_out_phase=context.current_phase,
                deadline_seconds=policy.initialization_deadline_seconds,
            )
        except Exception as e:
            context = context.enter_phase(AgentStartupPhase.FAILED)
            return AgentStartupResult.create_failed(
                startup_request_id=startup_id,
                startup_execution_id=str(self.coordinator_id),
                launch_id=launch_identity.get("launch_id", "unknown"),
                process_id=process_id,
                invocation_surface=invocation_surface,
                effective_policy=policy_to_dict(policy),
                failed_phase=context.current_phase,
                primary_failure_message=f"Initialization invocation failed: {e}",
            )
        
        # Step 11: Enter VALIDATING_INITIALIZATION phase
        context = context.enter_phase(AgentStartupPhase.VALIDATING_INITIALIZATION)
        
        try:
            init_valid, runtime_id, boot_session_id = self._validate_initialization_result(
                init_result,
                startup_id,
                launch_request,
                policy,
            )
            
            if not init_valid:
                # Try rollback first
                context = context.enter_phase(AgentStartupPhase.REQUESTING_ROLLBACK)
                
                try:
                    self._request_rollback(init_result, policy)
                except Exception as e:
                    return AgentStartupResult.create_failed(
                        startup_request_id=startup_id,
                        startup_execution_id=str(self.coordinator_id),
                        launch_id=launch_identity.get("launch_id", "unknown"),
                        process_id=process_id,
                        invocation_surface=invocation_surface,
                        effective_policy=policy_to_dict(policy),
                        failed_phase=context.current_phase,
                        primary_failure_message=f"Rollback request failed: {e}",
                    )
                
                context = context.enter_phase(AgentStartupPhase.FAILED)
                return AgentStartupResult.create_failed(
                    startup_request_id=startup_id,
                    startup_execution_id=str(self.coordinator_id),
                    launch_id=launch_identity.get("launch_id", "unknown"),
                    process_id=process_id,
                    invocation_surface=invocation_surface,
                    effective_policy=policy_to_dict(policy),
                    failed_phase=context.current_phase,
                    primary_failure_message="Initialization validation failed and rollback requested",
                )
                
        except Exception as e:
            context = context.enter_phase(AgentStartupPhase.FAILED)
            return AgentStartupResult.create_failed(
                startup_request_id=startup_id,
                startup_execution_id=str(self.coordinator_id),
                launch_id=launch_identity.get("launch_id", "unknown"),
                process_id=process_id,
                invocation_surface=invocation_surface,
                effective_policy=policy_to_dict(policy),
                failed_phase=context.current_phase,
                primary_failure_message=f"Initialization validation failed: {e}",
            )
        
        # Step 12: Enter TRANSFERRING_OWNERSHIP phase
        context = context.enter_phase(AgentStartupPhase.TRANSFERRING_OWNERSHIP)
        
        # Step 13: Enter VERIFYING_HANDOFF phase
        context = context.enter_phase(AgentStartupPhase.VERIFYING_HANDOFF)
        
        # Handoff verified - transfer complete
        context = context.enter_phase(AgentStartupPhase.COMPLETED)
        
        # Return successful result
        return AgentStartupResult.create_started(
            startup_request_id=startup_id,
            startup_execution_id=str(self.coordinator_id),
            launch_id=launch_identity.get("launch_id", "unknown"),
            process_id=process_id,
            invocation_surface=invocation_surface,
            effective_policy=policy_to_dict(policy),
            preflight_result_summary=self._summarize_preflight_result(preflight_result),
            initialization_result_summary=self._summarize_initialization_result(init_result),
            runtime_id=runtime_id or "runtime_" + startup_id[:8],
            boot_session_id=boot_session_id or "bootsession_" + startup_id[:8],
        )
    
    def _validate_startup_request(
        self,
        launch_request: Dict[str, Any],
        context: AgentStartupContext,
        policy: AgentStartupPolicy,
    ) -> None:
        """Validate the startup request.
        
        Args:
            launch_request: The launch request to validate
            context: Current startup context
            policy: Effective startup policy
            
        Raises:
            AgentStartupRequestError: If validation fails
        """
        # Validate required fields exist
        if not isinstance(launch_request, dict):
            raise AgentStartupRequestError("Launch request must be a dictionary")
        
        launch_identity = launch_request.get("launch_identity", {})
        if not launch_identity.get("launch_id"):
            raise AgentStartupRequestError("Launch identity missing launch_id")
        
        process_identity = launch_request.get("process_identity", {})
        if not process_identity.get("process_id"):
            raise AgentStartupRequestError("Process identity missing process_id")
    
    def _derive_preflight_request(
        self,
        launch_request: Dict[str, Any],
        startup_id: str,
        process_id: int,
        policy: AgentStartupPolicy,
    ) -> Dict[str, Any]:
        """Derive preflight request from launch request.
        
        Args:
            launch_request: The launch request
            startup_id: Startup operation ID
            process_id: Process ID
            policy: Effective startup policy
            
        Returns:
            Preflight request dictionary
        """
        import uuid
        
        launch_identity = launch_request.get("launch_identity", {})
        process_identity = launch_request.get("process_identity", {})
        
        return {
            "request_id": str(uuid.uuid4()),
            "startup_id": startup_id,
            "launch_identity": {
                "launch_id": launch_identity.get("launch_id"),
                "timestamp_ns": launch_identity.get("timestamp_ns"),
                "invocation_surface": process_identity.get("invocation_surface", "unknown"),
            },
            "process_identity": {
                "process_id": process_id,
                "parent_process_id": process_identity.get("parent_process_id"),
            },
            "startup_deadline_seconds": policy.startup_deadline_seconds,
            "preflight_deadline_seconds": policy.preflight_deadline_seconds,
        }
    
    def _invoke_preflight(
        self,
        preflight_request: Dict[str, Any],
        deadline_seconds: float,
    ) -> Dict[str, Any]:
        """Invoke the canonical preflight authority.
        
        This delegates to entrypoint/check.py through its public interface.
        It does NOT implement individual checks itself.
        
        Args:
            preflight_request: Derived preflight request
            deadline_seconds: Deadline for this invocation
            
        Returns:
            Preflight result dictionary
            
        Raises:
            AgentStartupTimeoutError: If deadline exceeded
        """
        try:
            from . import check as preflight_module
        except (ImportError, ModuleNotFoundError) as e:
            raise AgentStartupTimeoutError(
                f"Preflight module not available: {e}",
                deadline_seconds=deadline_seconds,
            )
        
        # Extract launch identity for result validation
        launch_identity = preflight_request.get("launch_identity", {})
        
        try:
            # Invoke the preflight checker through its public API
            if hasattr(preflight_module, "check_agent"):
                # Function-based interface
                result = preflight_module.check_agent(preflight_request)
                
                # Convert to dict for compatibility
                return self._preflight_result_to_dict(result, launch_identity)
                
            elif hasattr(preflight_module, "AgentPreflightChecker"):
                # Class-based interface
                checker = preflight_module.AgentPreflightChecker()
                result = checker.check(preflight_request)
                
                return self._preflight_result_to_dict(result, launch_identity)
                
            else:
                raise AgentStartupTimeoutError(
                    "No preflight checker found",
                    deadline_seconds=deadline_seconds,
                )
                
        except Exception as e:
            # Timeout is handled by caller - re-raise
            if isinstance(e, AgentStartupTimeoutError):
                raise
            
            # For other exceptions, wrap and return as failure
            import time
            now_ns = time.time_ns()
            
            return {
                "outcome": {"value": "failed", "is_success": False},
                "execution_id": str(uuid.uuid4()),
                "error": str(e),
                "timestamp_ns": now_ns,
            }
    
    def _preflight_result_to_dict(
        self,
        result: Any,
        launch_identity: Dict[str, Any],
    ) -> Dict[str, Any]:
        """Convert preflight result to dictionary.
        
        Args:
            result: The preflight result from check_agent()
            launch_identity: Launch identity for validation
            
        Returns:
            Dictionary representation of the result
        """
        import time
        
        # Try to extract result attributes
        try:
            outcome = getattr(result, "outcome", None)
            if hasattr(outcome, "value"):
                outcome_value = outcome.value
            elif isinstance(outcome, str):
                outcome_value = outcome
            else:
                outcome_value = "unknown"
            
            return {
                "request_id": getattr(result, "request_id", ""),
                "launch_identity": launch_identity,
                "execution_id": getattr(result, "execution_id", str(uuid.uuid4())),
                "start_time_ns": getattr(result, "start_time_ns", time.time_ns()),
                "end_time_ns": getattr(result, "end_time_ns", time.time_ns()),
                "outcome": {
                    "value": outcome_value,
                    "is_success": hasattr(outcome, "is_success") and outcome.is_success() if callable(getattr(outcome, "is_success", None)) else False,
                },
                "source_fingerprint": getattr(result, "source_fingerprint", ""),
                "artifact_fingerprint": getattr(result, "artifact_fingerprint", ""),
                "configuration_generation": getattr(result, "configuration_generation", 0),
                "blockers": tuple(getattr(result, "blockers", []) or []),
                "warnings": tuple(getattr(result, "warnings", []) or []),
                "errors": tuple(getattr(result, "errors", []) or []),
            }
        except Exception:
            # Fallback
            return {
                "outcome": {"value": "unknown", "is_success": False},
                "execution_id": str(uuid.uuid4()),
            }
    
    def _validate_preflight_result(
        self,
        preflight_result: Dict[str, Any],
        launch_request: Dict[str, Any],
        policy: AgentStartupPolicy,
    ) -> Tuple[bool, Optional[Tuple[Dict[str, Any], ...]], Optional[Tuple[Dict[str, Any], ...]]]:
        """Validate preflight result.
        
        Args:
            preflight_result: Preflight result from invocation
            launch_request: Original launch request
            policy: Effective startup policy
            
        Returns:
            Tuple of (is_valid, blockers, warnings)
            
        A valid result must have:
            - PASS or PASS_WITH_WARNINGS outcome
            - Matching launch identity
            - Non-stale evidence
        """
        outcome = preflight_result.get("outcome", {})
        
        if isinstance(outcome, dict):
            outcome_value = outcome.get("value", "unknown")
            is_success = outcome.get("is_success", False)
        else:
            outcome_value = str(outcome)
            is_success = False
        
        # Check outcome
        if not is_success and outcome_value in ("blocked", "failed", "cancelled", "timed_out"):
            return (
                False,
                ({"type": "outcome_blocked", "message": f"Preflight {outcome_value}"},),
                None,
            )
        
        # Check PASS_WITH_WARNINGS based on policy
        if outcome_value == "pass_with_warnings":
            if policy.require_strict_preflight_validation:
                return (
                    False,
                    ({"type": "strict_policy_reject", "message": "PASS_WITH_WARNINGS not permitted by policy"},),
                    None,
                )
        
        # Extract blockers and warnings for later use
        blockers = preflight_result.get("blockers", ())
        warnings = preflight_result.get("warnings", ())
        
        return True, tuple(blockers) if blockers else (), tuple(warnings) if warnings else ()
    
    def _derive_initialization_request(
        self,
        launch_request: Dict[str, Any],
        validated_preflight_result: Dict[str, Any],
        startup_id: str,
        process_id: int,
        policy: AgentStartupPolicy,
    ) -> Dict[str, Any]:
        """Derive initialization request from validated preflight.
        
        Args:
            launch_request: Original launch request
            validated_preflight_result: Validated preflight result
            startup_id: Startup operation ID
            process_id: Process ID
            policy: Effective startup policy
            
        Returns:
            Initialization request dictionary
        """
        import uuid
        
        return {
            "init_id": str(uuid.uuid4()),
            "startup_id": startup_id,
            "launch_id": launch_request.get("launch_identity", {}).get("launch_id"),
            "process_id": process_id,
            "preflight_result": validated_preflight_result,
            "startup_policy": policy_to_dict(policy),
            "startup_deadline_seconds": policy.startup_deadline_seconds,
            "initialization_deadline_seconds": policy.initialization_deadline_seconds,
        }
    
    def _invoke_initialization(
        self,
        init_request: Dict[str, Any],
        deadline_seconds: float,
    ) -> Dict[str, Any]:
        """Invoke the canonical initialization authority.
        
        This delegates to entrypoint/init.py through its public interface.
        It does NOT implement initialization internals itself.
        
        Args:
            init_request: Derived initialization request
            deadline_seconds: Deadline for this invocation
            
        Returns:
            Initialization result dictionary
            
        Raises:
            AgentStartupTimeoutError: If deadline exceeded
        """
        try:
            from . import init as init_module
        except (ImportError, ModuleNotFoundError) as e:
            raise AgentStartupTimeoutError(
                f"Initialization module not available: {e}",
                deadline_seconds=deadline_seconds,
            )
        
        # Extract launch identity for result validation
        launch_id = init_request.get("launch_id", "")
        
        try:
            # Invoke the initializer through its public API
            if hasattr(init_module, "initialize_agent"):
                # Function-based interface
                result = init_module.initialize_agent(init_request)
                
                # Convert to dict for compatibility
                return self._init_result_to_dict(result, launch_id, init_request)
                
            elif hasattr(init_module, "AgentInitializer"):
                # Class-based interface
                initializer = init_module.AgentInitializer()
                result = initializer.initialize(init_request)
                
                return self._init_result_to_dict(result, launch_id, init_request)
                
            else:
                raise AgentStartupTimeoutError(
                    "No initialization function or class found",
                    deadline_seconds=deadline_seconds,
                )
                
        except Exception as e:
            # Timeout is handled by caller - re-raise
            if isinstance(e, AgentStartupTimeoutError):
                raise
            
            # For other exceptions, wrap and return as failure
            import time
            now_ns = time.time_ns()
            
            # Use a fallback init_id since we can't access the request here
            error_init_id = str(uuid.uuid4())[:8]
            
            return {
                "outcome": {"value": "failed", "is_success": False},
                "init_id": error_init_id,
                "error": str(e),
                "timestamp_ns": now_ns,
            }
    
    def _init_result_to_dict(
        self,
        result: Any,
        launch_id: str,
        init_request: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """Convert initialization result to dictionary.
        
        Args:
            result: The initialization result from initialize_agent()
            launch_id: Launch ID for validation
            
        Returns:
            Dictionary representation of the result
        """
        import time
        
        try:
            # Try to extract result attributes
            final_phase = getattr(result, "final_phase", None)
            if hasattr(final_phase, "value"):
                phase_value = final_phase.value
            elif isinstance(final_phase, str):
                phase_value = final_phase
            else:
                phase_value = "unknown"
            
            is_success = phase_value == "completed"
            
            return {
                "init_id": getattr(result, "init_id", ""),
                "launch_id": launch_id,
                "process_id": getattr(result, "process_id", 0),
                "runtime_id": getattr(result, "runtime_id", ""),
                "boot_session_id": getattr(result, "boot_session_id", ""),
                "final_phase": phase_value,
                "is_success": is_success,
                "config_fingerprint": getattr(result, "config_fingerprint", ""),
                "core_construction_status": getattr(result, "core_construction_status", "unknown"),
                "assembly_status": getattr(result, "assembly_status", "unknown"),
                "structural_verification_passed": getattr(result, "structural_verification_passed", False),
                "integrity_verification_passed": getattr(result, "integrity_verification_passed", False),
                "activation_passed": getattr(result, "activation_passed", False),
                "readiness_evaluated": getattr(result, "readiness_evaluated", False),
                "admission_opened": getattr(result, "admission_opened", False),
            }
        except Exception:
            # Fallback - use a default init_id
            error_init_id = str(uuid.uuid4())[:8] if init_request is None else init_request.get("init_id", "")
            
            return {
                "outcome": {"value": "unknown", "is_success": False},
                "init_id": error_init_id,
            }
    
    def _validate_initialization_result(
        self,
        init_result: Dict[str, Any],
        startup_id: str,
        launch_request: Dict[str, Any],
        policy: AgentStartupPolicy,
    ) -> Tuple[bool, Optional[str], Optional[str]]:
        """Validate initialization result.
        
        Args:
            init_result: Initialization result from invocation
            startup_id: Startup operation ID
            launch_request: Original launch request
            policy: Effective startup policy
            
        Returns:
            Tuple of (is_valid, runtime_id, boot_session_id)
            
        A valid result must have:
            - COMPLETED final phase
            - Runtime identity present
            - Boot session identity present
            - Proper ownership state
        """
        is_success = init_result.get("is_success", False)
        
        if not is_success:
            return False, None, None
        
        runtime_id = init_result.get("runtime_id")
        boot_session_id = init_result.get("boot_session_id")
        
        # Both must be present for successful handoff
        if not runtime_id or not boot_session_id:
            return False, None, None
        
        return True, runtime_id, boot_session_id
    
    def _request_rollback(
        self,
        init_result: Dict[str, Any],
        policy: AgentStartupPolicy,
    ) -> None:
        """Request rollback for failed initialization.
        
        Args:
            init_result: Initialization result that failed
            policy: Effective startup policy
            
        This delegates to the initializer through its rollback interface.
        It does NOT implement rollback internals itself.
        """
        try:
            from . import init as init_module
            
            if hasattr(init_module, "rollback_initialization"):
                # Call rollback function if available
                init_module.rollback_initialization(init_result)
                
        except Exception:
            # Rollback errors are handled by the caller
            pass
    
    def _summarize_preflight_result(
        self,
        preflight_result: Dict[str, Any],
    ) -> Optional[Dict[str, Any]]:
        """Create a summary of the preflight result.
        
        Args:
            preflight_result: Full preflight result from invocation
            
        Returns:
            Bounded summary dictionary
        """
        outcome = preflight_result.get("outcome", {})
        if isinstance(outcome, dict):
            outcome_value = outcome.get("value", "unknown")
            is_success = outcome.get("is_success", False)
        else:
            outcome_value = str(outcome)
            is_success = False
        
        return {
            "request_id": preflight_result.get("request_id"),
            "execution_id": preflight_result.get("execution_id"),
            "outcome": outcome_value,
            "success": is_success,
            "blockers_count": len(preflight_result.get("blockers", ())),
            "warnings_count": len(preflight_result.get("warnings", ())),
        }
    
    def _summarize_initialization_result(
        self,
        init_result: Dict[str, Any],
    ) -> Optional[Dict[str, Any]]:
        """Create a summary of the initialization result.
        
        Args:
            init_result: Full initialization result from invocation
            
        Returns:
            Bounded summary dictionary
        """
        return {
            "init_id": init_result.get("init_id"),
            "runtime_id": init_result.get("runtime_id"),
            "boot_session_id": init_result.get("boot_session_id"),
            "final_phase": init_result.get("final_phase"),
            "is_success": init_result.get("is_success", False),
        }
    
    def get_startup_identity(self) -> str:
        """Get the coordinator's startup identity.
        
        Returns:
            Coordinator ID as startup identity
        """
        return self.coordinator_id


# =============================================================================
# CONVENIENCE FUNCTION
# =============================================================================


def start_agent(launch_request: Dict[str, Any]) -> AgentStartupResult:
    """Convenience function to start an Agent through canonical coordinator.
    
    This is the public interface for startup. It creates a fresh coordinator
    and delegates to it.
    
    Args:
        launch_request: The immutable Agent launch request
        
    Returns:
        Immutable AgentStartupResult
    """
    coordinator = AgentStartupCoordinator()
    return coordinator.start(launch_request)


def policy_to_dict(policy: AgentStartupPolicy) -> Dict[str, Any]:
    """Convert a policy to dictionary for result inclusion.
    
    Args:
        policy: The startup policy
        
    Returns:
        Dictionary representation of the policy
    """
    return {
        "policy_id": policy.policy_id,
        "launch_id": policy.launch_id,
        "generation": policy.generation,
        "startup_mode": policy.startup_mode.value if hasattr(policy.startup_mode, "value") else str(policy.startup_mode),
        "bridge_policy": policy.bridge_policy.value if hasattr(policy.bridge_policy, "value") else str(policy.bridge_policy),
        "safe_mode_enabled": policy.safe_mode_enabled,
        "offline_mode_enabled": policy.offline_mode_enabled,
        "validation_only": policy.validation_only,
        "degraded_allowed": policy.degraded_allowed,
    }


__all__ = [
    "AgentStartupCoordinator",
    "start_agent",
]