"""Gordon Agent Initialization Exception Types.

Phase 3.7.30: Agent Initialization Chain
========================================

Typed exception hierarchy for initialization failures.
"""
from __future__ import annotations

from typing import Optional, Tuple


# =============================================================================
# BASE INITIALIZATION ERROR
# =============================================================================


class AgentInitializationError(Exception):
    """Base class for all initialization errors.
    
    All initialization-specific exceptions inherit from this base class,
    allowing callers to catch all initialization errors with a single except.
    
    This exception preserves:
        - The initialization ID where the error occurred
        - The phase during which it occurred
        - The primary failure message
        - Any secondary failures that did not cascade
    """
    
    def __init__(
        self,
        message: str,
        *,
        init_id: Optional[str] = None,
        launch_id: Optional[str] = None,
        failed_phase: Optional[str] = None,
        cause: Optional[Exception] = None,
        secondary_failures: Optional[Tuple[str, ...]] = None,
    ):
        """Initialize an initialization error.
        
        Args:
            message: Primary failure message
            init_id: Initialization operation ID (optional)
            launch_id: Launch session ID (optional)
            failed_phase: Phase during which error occurred (optional)
            cause: The underlying exception that caused this error (optional)
            secondary_failures: Secondary failures that did not cascade (optional)
        """
        super().__init__(message)
        self.message = message
        self.init_id = init_id
        self.launch_id = launch_id
        self.failed_phase = failed_phase
        self.__cause__ = cause
        self.secondary_failures = secondary_failures or ()
    
    @classmethod
    def from_failure_record(
        cls,
        failure: "AgentInitializationFailure",
    ) -> "AgentInitializationError":
        """Create an initialization error from a failure record.
        
        Args:
            failure: The failure record to convert
            
        Returns:
            A new AgentInitializationError instance
        """
        message = f"{failure.failure_category}: {failure.primary_failure_message}"
        return cls(
            message=message,
            init_id=failure.init_id,
            launch_id=failure.launch_id,
            failed_phase=failure.failed_phase.name if failure.failed_phase else None,
            cause=None,  # Would reconstruct from failure if available
            secondary_failures=failure.secondary_failures,
        )
    
    def with_init_id(self, init_id: str) -> "AgentInitializationError":
        """Return a new error with the given initialization ID."""
        return AgentInitializationError(
            message=self.message,
            init_id=init_id,
            launch_id=self.launch_id,
            failed_phase=self.failed_phase,
            cause=self.__cause__,
            secondary_failures=self.secondary_failures,
        )


# =============================================================================
# INITIALIZATION REQUEST ERRORS
# =============================================================================


class InitializationRequestError(AgentInitializationError):
    """Raised when initialization request validation fails."""
    
    def __init__(
        self,
        message: str,
        *,
        init_id: Optional[str] = None,
        launch_id: Optional[str] = None,
    ):
        super().__init__(message, init_id=init_id, launch_id=launch_id)


class InitializationRequestMissingField(InitializationRequestError):
    """Raised when a required field is missing from the request."""
    
    def __init__(
        self,
        field_name: str,
        *,
        init_id: Optional[str] = None,
        launch_id: Optional[str] = None,
    ):
        super().__init__(
            f"Missing required field: {field_name}",
            init_id=init_id,
            launch_id=launch_id,
        )


class InitializationRequestInvalidValue(InitializationRequestError):
    """Raised when a request field has an invalid value."""
    
    def __init__(
        self,
        field_name: str,
        expected_type: str,
        actual_value: Any = None,  # type: ignore
        *,
        init_id: Optional[str] = None,
        launch_id: Optional[str] = None,
    ):
        value_repr = repr(actual_value) if actual_value is not None else "None"
        super().__init__(
            f"Invalid value for field '{field_name}': expected {expected_type}, got {value_repr}",
            init_id=init_id,
            launch_id=launch_id,
        )


# =============================================================================
# INITIALIZATION CONFIGURATION ERRORS
# =============================================================================


class InitializationConfigurationError(AgentInitializationError):
    """Raised when configuration validation fails."""
    
    def __init__(
        self,
        message: str,
        *,
        init_id: Optional[str] = None,
        launch_id: Optional[str] = None,
    ):
        super().__init__(message, init_id=init_id, launch_id=launch_id)


class InitializationConfigurationMissing(InitializationConfigurationError):
    """Raised when configuration cannot be loaded or is missing."""
    
    def __init__(
        self,
        message: str = "Configuration is required but not available",
        *,
        init_id: Optional[str] = None,
        launch_id: Optional[str] = None,
    ):
        super().__init__(message, init_id=init_id, launch_id=launch_id)


class InitializationConfigurationInvalid(InitializationConfigurationError):
    """Raised when configuration fails schema validation."""
    
    def __init__(
        self,
        errors: Tuple[str, ...],
        *,
        init_id: Optional[str] = None,
        launch_id: Optional[str] = None,
    ):
        error_str = "; ".join(errors)
        super().__init__(
            f"Configuration validation failed: {error_str}",
            init_id=init_id,
            launch_id=launch_id,
        )


# =============================================================================
# INITIALIZATION CONTEXT ERRORS
# =============================================================================


class InitializationContextError(AgentInitializationError):
    """Raised when initialization context creation fails."""
    
    def __init__(
        self,
        message: str,
        *,
        init_id: Optional[str] = None,
        launch_id: Optional[str] = None,
    ):
        super().__init__(message, init_id=init_id, launch_id=launch_id)


class InitializationContextAlreadyCreated(InitializationContextError):
    """Raised when trying to create a context for an already initialized request."""
    
    def __init__(
        self,
        *,
        init_id: Optional[str] = None,
        launch_id: Optional[str] = None,
    ):
        super().__init__(
            "Initialization context already exists",
            init_id=init_id,
            launch_id=launch_id,
        )


# =============================================================================
# INITIALIZATION LOAD ERRORS
# =============================================================================


class InitializationLoadError(AgentInitializationError):
    """Raised when component loading fails."""
    
    def __init__(
        self,
        message: str,
        *,
        init_id: Optional[str] = None,
        launch_id: Optional[str] = None,
        partial_load_result: Optional[Any] = None,  # type: ignore
    ):
        super().__init__(message, init_id=init_id, launch_id=launch_id)
        self.partial_load_result = partial_load_result


class InitializationLoadDescriptorNotFound(InitializationLoadError):
    """Raised when a component descriptor cannot be found."""
    
    def __init__(
        self,
        component_name: str,
        *,
        init_id: Optional[str] = None,
        launch_id: Optional[str] = None,
    ):
        super().__init__(
            f"Component descriptor not found for '{component_name}'",
            init_id=init_id,
            launch_id=launch_id,
        )


class InitializationLoadImportError(InitializationLoadError):
    """Raised when component implementation cannot be imported."""
    
    def __init__(
        self,
        component_name: str,
        *,
        init_id: Optional[str] = None,
        launch_id: Optional[str] = None,
    ):
        super().__init__(
            f"Failed to import implementation for '{component_name}'",
            init_id=init_id,
            launch_id=launch_id,
        )


class InitializationLoadDependencyError(InitializationLoadError):
    """Raised when component dependencies cannot be resolved."""
    
    def __init__(
        self,
        component_name: str,
        missing_dependencies: Tuple[str, ...],
        *,
        init_id: Optional[str] = None,
        launch_id: Optional[str] = None,
    ):
        deps_str = ", ".join(missing_dependencies)
        super().__init__(
            f"Failed to resolve dependencies for '{component_name}': missing {deps_str}",
            init_id=init_id,
            launch_id=launch_id,
        )


# =============================================================================
# INITIALIZATION CORE CONSTRUCTION ERRORS
# =============================================================================


class InitializationCoreConstructionError(AgentInitializationError):
    """Raised when Agent Core construction fails."""
    
    def __init__(
        self,
        message: str,
        *,
        init_id: Optional[str] = None,
        launch_id: Optional[str] = None,
    ):
        super().__init__(message, init_id=init_id, launch_id=launch_id)


class InitializationCoreAuthorityError(InitializationCoreConstructionError):
    """Raised when Core authority construction fails."""
    
    def __init__(
        self,
        authority_name: str,
        *,
        init_id: Optional[str] = None,
        launch_id: Optional[str] = None,
    ):
        super().__init__(
            f"Failed to construct Core authority: {authority_name}",
            init_id=init_id,
            launch_id=launch_id,
        )


# =============================================================================
# INITIALIZATION ASSEMBLY ERRORS
# =============================================================================


class InitializationAssemblyError(AgentInitializationError):
    """Raised when runtime assembly fails."""
    
    def __init__(
        self,
        message: str,
        *,
        init_id: Optional[str] = None,
        launch_id: Optional[str] = None,
    ):
        super().__init__(message, init_id=init_id, launch_id=launch_id)


class InitializationAssemblyConnectionError(InitializationAssemblyError):
    """Raised when component connections fail during assembly."""
    
    def __init__(
        self,
        source_component: str,
        target_component: str,
        connection_type: str,
        *,
        init_id: Optional[str] = None,
        launch_id: Optional[str] = None,
    ):
        super().__init__(
            f"Failed to connect '{source_component}' to '{target_component}' "
            f"(connection type: {connection_type})",
            init_id=init_id,
            launch_id=launch_id,
        )


# =============================================================================
# INITIALIZATION VERIFICATION ERRORS
# =============================================================================


class InitializationVerificationError(AgentInitializationError):
    """Base class for verification failures."""
    
    def __init__(
        self,
        message: str,
        *,
        init_id: Optional[str] = None,
        launch_id: Optional[str] = None,
    ):
        super().__init__(message, init_id=init_id, launch_id=launch_id)


class InitializationStructureError(InitializationVerificationError):
    """Raised when structural verification fails."""
    
    def __init__(
        self,
        issues: Tuple[str, ...],
        *,
        init_id: Optional[str] = None,
        launch_id: Optional[str] = None,
    ):
        issue_str = "; ".join(issues)
        super().__init__(
            f"Structural verification failed: {issue_str}",
            init_id=init_id,
            launch_id=launch_id,
        )


class InitializationIntegrityError(InitializationVerificationError):
    """Raised when integrity verification fails."""
    
    def __init__(
        self,
        message: str,
        *,
        init_id: Optional[str] = None,
        launch_id: Optional[str] = None,
    ):
        super().__init__(message, init_id=init_id, launch_id=launch_id)


# =============================================================================
# INITIALIZATION ACTIVATION ERRORS
# =============================================================================


class InitializationActivationError(AgentInitializationError):
    """Raised when runtime activation fails."""
    
    def __init__(
        self,
        message: str,
        *,
        init_id: Optional[str] = None,
        launch_id: Optional[str] = None,
    ):
        super().__init__(message, init_id=init_id, launch_id=launch_id)


class InitializationActivationTimeout(InitializationActivationError):
    """Raised when activation times out."""
    
    def __init__(
        self,
        component_name: str,
        *,
        init_id: Optional[str] = None,
        launch_id: Optional[str] = None,
    ):
        super().__init__(
            f"Component '{component_name}' activation timed out",
            init_id=init_id,
            launch_id=launch_id,
        )


# =============================================================================
# INITIALIZATION READINESS ERRORS
# =============================================================================


class InitializationReadinessError(AgentInitializationError):
    """Raised when readiness evaluation fails."""
    
    def __init__(
        self,
        message: str,
        *,
        init_id: Optional[str] = None,
        launch_id: Optional[str] = None,
    ):
        super().__init__(message, init_id=init_id, launch_id=launch_id)


class InitializationReadinessNotMet(InitializationReadinessError):
    """Raised when readiness requirements are not met."""
    
    def __init__(
        self,
        missing_requirements: Tuple[str, ...],
        *,
        init_id: Optional[str] = None,
        launch_id: Optional[str] = None,
    ):
        req_str = ", ".join(missing_requirements)
        super().__init__(
            f"Readiness requirements not met: {req_str}",
            init_id=init_id,
            launch_id=launch_id,
        )


# =============================================================================
# INITIALIZATION ADMISSION ERRORS
# =============================================================================


class InitializationAdmissionError(AgentInitializationError):
    """Raised when admission opening fails."""
    
    def __init__(
        self,
        message: str,
        *,
        init_id: Optional[str] = None,
        launch_id: Optional[str] = None,
    ):
        super().__init__(message, init_id=init_id, launch_id=launch_id)


# =============================================================================
# INITIALIZATION CANCELLATION ERRORS
# =============================================================================


class InitializationCancellationError(AgentInitializationError):
    """Raised when initialization is cancelled."""
    
    def __init__(
        self,
        message: str = "Initialization was cancelled",
        *,
        init_id: Optional[str] = None,
        launch_id: Optional[str] = None,
    ):
        super().__init__(message, init_id=init_id, launch_id=launch_id)


# =============================================================================
# INITIALIZATION TIMEOUT ERRORS
# =============================================================================


class InitializationTimeoutError(AgentInitializationError):
    """Raised when initialization exceeds the configured timeout."""
    
    def __init__(
        self,
        phase: str,
        timeout_seconds: float,
        *,
        init_id: Optional[str] = None,
        launch_id: Optional[str] = None,
    ):
        super().__init__(
            f"Initialization exceeded timeout in phase '{phase}' "
            f"(timeout: {timeout_seconds}s)",
            init_id=init_id,
            launch_id=launch_id,
        )


# =============================================================================
# INITIALIZATION ROLLBACK ERRORS
# =============================================================================


class InitializationRollbackError(AgentInitializationError):
    """Raised when initialization rollback fails."""
    
    def __init__(
        self,
        message: str,
        *,
        init_id: Optional[str] = None,
        launch_id: Optional[str] = None,
        partial_rollback: bool = False,
    ):
        super().__init__(message, init_id=init_id, launch_id=launch_id)
        self.partial_rollback = partial_rollback


# =============================================================================
# INITIALIZATION INTERNAL ERRORS
# =============================================================================


class InitializationInternalError(AgentInitializationError):
    """Raised for internal initialization errors (programming errors)."""
    
    def __init__(
        self,
        message: str,
        *,
        init_id: Optional[str] = None,
        launch_id: Optional[str] = None,
    ):
        super().__init__(message, init_id=init_id, launch_id=launch_id)


# =============================================================================
# EXPORTS
# =============================================================================


__all__ = [
    # Base class
    "AgentInitializationError",
    # Request errors
    "InitializationRequestError",
    "InitializationRequestMissingField",
    "InitializationRequestInvalidValue",
    # Configuration errors
    "InitializationConfigurationError",
    "InitializationConfigurationMissing",
    "InitializationConfigurationInvalid",
    # Context errors
    "InitializationContextError",
    "InitializationContextAlreadyCreated",
    # Load errors
    "InitializationLoadError",
    "InitializationLoadDescriptorNotFound",
    "InitializationLoadImportError",
    "InitializationLoadDependencyError",
    # Core construction errors
    "InitializationCoreConstructionError",
    "InitializationCoreAuthorityError",
    # Assembly errors
    "InitializationAssemblyError",
    "InitializationAssemblyConnectionError",
    # Verification errors
    "InitializationVerificationError",
    "InitializationStructureError",
    "InitializationIntegrityError",
    # Activation errors
    "InitializationActivationError",
    "InitializationActivationTimeout",
    # Readiness errors
    "InitializationReadinessError",
    "InitializationReadinessNotMet",
    # Admission errors
    "InitializationAdmissionError",
    # Cancellation errors
    "InitializationCancellationError",
    # Timeout errors
    "InitializationTimeoutError",
    # Rollback errors
    "InitializationRollbackError",
    # Internal errors
    "InitializationInternalError",
]