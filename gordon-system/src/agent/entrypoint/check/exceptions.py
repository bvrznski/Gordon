"""Gordon Agent Preflight Exception Types.

Phase 3.7.32-I: Agent Startup Preflight and Compilation Checks
==============================================================

Typed exception types for preflight failures, preserving
failure context without runtime state.
"""

from __future__ import annotations

from typing import Dict, Any, Tuple, Optional


# =============================================================================
# Base Preflight Exceptions
# =============================================================================

class AgentPreflightError(Exception):
    """Base class for all preflight errors.
    
    Preserves preflight context while not exposing runtime objects.
    """
    
    def __init__(
        self,
        message: str,
        *,
        preflight_id: Optional[str] = None,
        launch_id: Optional[str] = None,
        process_id: Optional[int] = None,
        current_phase: Optional[str] = None,
        check_id: Optional[str] = None,
        target: Optional[str] = None,
        primary_cause: Optional[str] = None,
    ):
        super().__init__(message)
        self.message = message
        self.preflight_id = preflight_id
        self.launch_id = launch_id
        self.process_id = process_id
        self.current_phase = current_phase
        self.check_id = check_id
        self.target = target
        self.primary_cause = primary_cause
    
    def get_context(self) -> Dict[str, Any]:
        """Return error context without runtime state."""
        return {
            "preflight_id": self.preflight_id,
            "launch_id": self.launch_id,
            "process_id": self.process_id,
            "current_phase": self.current_phase,
            "check_id": self.check_id,
            "target": self.target,
            "primary_cause": self.primary_cause,
        }


class PreflightRequestError(AgentPreflightError):
    """Error in preflight request validation."""
    
    def __init__(
        self,
        message: str,
        *,
        field_name: Optional[str] = None,
        invalid_value: Any = None,
        **kwargs
    ):
        super().__init__(message, **kwargs)
        self.field_name = field_name
        self.invalid_value = invalid_value


class PreflightPolicyError(AgentPreflightError):
    """Error in policy interpretation or configuration."""
    
    def __init__(
        self,
        message: str,
        *,
        policy_name: Optional[str] = None,
        **kwargs
    ):
        super().__init__(message, **kwargs)
        self.policy_name = policy_name


class PreflightRootError(AgentPreflightError):
    """Error in root path resolution or validation."""
    
    def __init__(
        self,
        message: str,
        *,
        root_path: Optional[str] = None,
        expected_type: Optional[str] = None,
        **kwargs
    ):
        super().__init__(message, **kwargs)
        self.root_path = root_path
        self.expected_type = expected_type


class PreflightManifestError(AgentPreflightError):
    """Error in manifest validation."""
    
    def __init__(
        self,
        message: str,
        *,
        manifest_path: Optional[str] = None,
        manifest_version: Optional[str] = None,
        **kwargs
    ):
        super().__init__(message, **kwargs)
        self.manifest_path = manifest_path
        self.manifest_version = manifest_version


class PreflightFingerprintError(AgentPreflightError):
    """Error in fingerprint computation or validation."""
    
    def __init__(
        self,
        message: str,
        *,
        expected_fingerprint: Optional[str] = None,
        actual_fingerprint: Optional[str] = None,
        **kwargs
    ):
        super().__init__(message, **kwargs)
        self.expected_fingerprint = expected_fingerprint
        self.actual_fingerprint = actual_fingerprint


class PreflightCompilationError(AgentPreflightError):
    """Error in source compilation."""
    
    def __init__(
        self,
        message: str,
        *,
        source_path: Optional[str] = None,
        syntax_location: Optional[Tuple[int, int]] = None,
        error_type: Optional[str] = None,
        **kwargs
    ):
        super().__init__(message, **kwargs)
        self.source_path = source_path
        self.syntax_location = syntax_location
        self.error_type = error_type


class PreflightPackageLayoutError(AgentPreflightError):
    """Error in package layout validation."""
    
    def __init__(
        self,
        message: str,
        *,
        expected_path: Optional[str] = None,
        actual_paths: Tuple[str, ...] = (),
        **kwargs
    ):
        super().__init__(message, **kwargs)
        self.expected_path = expected_path
        self.actual_paths = actual_paths


class PreflightMetadataError(AgentPreflightError):
    """Error in metadata validation."""
    
    def __init__(
        self,
        message: str,
        *,
        metadata_file: Optional[str] = None,
        expected_field: Optional[str] = None,
        **kwargs
    ):
        super().__init__(message, **kwargs)
        self.metadata_file = metadata_file
        self.expected_field = expected_field


class PreflightStartupContractError(AgentPreflightError):
    """Error in startup contract validation."""
    
    def __init__(
        self,
        message: str,
        *,
        contract_type: Optional[str] = None,
        missing_symbol: Optional[str] = None,
        **kwargs
    ):
        super().__init__(message, **kwargs)
        self.contract_type = contract_type
        self.missing_symbol = missing_symbol


class PreflightDescriptorStaticError(AgentPreflightError):
    """Error in descriptor static validation."""
    
    def __init__(
        self,
        message: str,
        *,
        descriptor_path: Optional[str] = None,
        **kwargs
    ):
        super().__init__(message, **kwargs)
        self.descriptor_path = descriptor_path


class PreflightConfigurationAccessError(AgentPreflightError):
    """Error in configuration accessibility check."""
    
    def __init__(
        self,
        message: str,
        *,
        config_path: Optional[str] = None,
        config_key: Optional[str] = None,
        **kwargs
    ):
        super().__init__(message, **kwargs)
        self.config_path = config_path
        self.config_key = config_key


class PreflightEnvironmentError(AgentPreflightError):
    """Error in environment validation."""
    
    def __init__(
        self,
        message: str,
        *,
        env_key: Optional[str] = None,
        expected_value: Optional[str] = None,
        **kwargs
    ):
        super().__init__(message, **kwargs)
        self.env_key = env_key
        self.expected_value = expected_value


class PreflightFilesystemError(AgentPreflightError):
    """Error in filesystem validation."""
    
    def __init__(
        self,
        message: str,
        *,
        path: Optional[str] = None,
        expected_permission: Optional[str] = None,
        **kwargs
    ):
        super().__init__(message, **kwargs)
        self.path = path
        self.expected_permission = expected_permission


class PreflightExecutableError(AgentPreflightError):
    """Error in executable validation."""
    
    def __init__(
        self,
        message: str,
        *,
        executable_name: Optional[str] = None,
        found_path: Optional[str] = None,
        **kwargs
    ):
        super().__init__(message, **kwargs)
        self.executable_name = executable_name
        self.found_path = found_path


class PreflightNativeLibraryError(AgentPreflightError):
    """Error in native library validation."""
    
    def __init__(
        self,
        message: str,
        *,
        library_name: Optional[str] = None,
        **kwargs
    ):
        super().__init__(message, **kwargs)
        self.library_name = library_name


class PreflightComputeVisibilityError(AgentPreflightError):
    """Error in compute visibility validation."""
    
    def __init__(
        self,
        message: str,
        *,
        resource_type: Optional[str] = None,
        required_count: int = 0,
        visible_count: int = 0,
        **kwargs
    ):
        super().__init__(message, **kwargs)
        self.resource_type = resource_type
        self.required_count = required_count
        self.visible_count = visible_count


class PreflightResourceFeasibilityError(AgentPreflightError):
    """Error in resource feasibility validation."""
    
    def __init__(
        self,
        message: str,
        *,
        resource_type: Optional[str] = None,
        estimated_available: int = 0,
        required: int = 0,
        **kwargs
    ):
        super().__init__(message, **kwargs)
        self.resource_type = resource_type
        self.estimated_available = estimated_available
        self.required = required


class PreflightEndpointError(AgentPreflightError):
    """Error in endpoint validation."""
    
    def __init__(
        self,
        message: str,
        *,
        endpoint: Optional[str] = None,
        error_type: Optional[str] = None,
        **kwargs
    ):
        super().__init__(message, **kwargs)
        self.endpoint = endpoint
        self.error_type = error_type


class PreflightLockStateError(AgentPreflightError):
    """Error in lock state validation."""
    
    def __init__(
        self,
        message: str,
        *,
        lock_path: Optional[str] = None,
        lock_state: Optional[str] = None,
        **kwargs
    ):
        super().__init__(message, **kwargs)
        self.lock_path = lock_path
        self.lock_state = lock_state


class PreflightShutdownEvidenceError(AgentPreflightError):
    """Error in previous shutdown evidence validation."""
    
    def __init__(
        self,
        message: str,
        *,
        evidence_type: Optional[str] = None,
        **kwargs
    ):
        super().__init__(message, **kwargs)
        self.evidence_type = evidence_type


class PreflightMigrationError(AgentPreflightError):
    """Error in migration compatibility validation."""
    
    def __init__(
        self,
        message: str,
        *,
        migration_name: Optional[str] = None,
        required_version: Optional[int] = None,
        current_version: Optional[int] = None,
        **kwargs
    ):
        super().__init__(message, **kwargs)
        self.migration_name = migration_name
        self.required_version = required_version
        self.current_version = current_version


class PreflightSchemaCompatibilityError(AgentPreflightError):
    """Error in schema compatibility validation."""
    
    def __init__(
        self,
        message: str,
        *,
        schema_type: Optional[str] = None,
        expected_version: Optional[str] = None,
        actual_version: Optional[str] = None,
        **kwargs
    ):
        super().__init__(message, **kwargs)
        self.schema_type = schema_type
        self.expected_version = expected_version
        self.actual_version = actual_version


class PreflightArchitectureBoundaryError(AgentPreflightError):
    """Error in architectural boundary validation."""
    
    def __init__(
        self,
        message: str,
        *,
        boundary_name: Optional[str] = None,
        violation_type: Optional[str] = None,
        **kwargs
    ):
        super().__init__(message, **kwargs)
        self.boundary_name = boundary_name
        self.violation_type = violation_type


class PreflightCancellationError(AgentPreflightError):
    """Error when preflight is cancelled."""
    
    def __init__(
        self,
        message: str,
        *,
        cancel_reason: Optional[str] = None,
        **kwargs
    ):
        super().__init__(message, **kwargs)
        self.cancel_reason = cancel_reason


class PreflightTimeoutError(AgentPreflightError):
    """Error when preflight exceeds deadline."""
    
    def __init__(
        self,
        message: str,
        *,
        elapsed_seconds: float = 0.0,
        timeout_seconds: float = 0.0,
        **kwargs
    ):
        super().__init__(message, **kwargs)
        self.elapsed_seconds = elapsed_seconds
        self.timeout_seconds = timeout_seconds


class PreflightInternalError(AgentPreflightError):
    """Error in preflight mechanism itself (not a blocker finding)."""
    
    def __init__(
        self,
        message: str,
        *,
        internal_error_type: Optional[str] = None,
        traceback: Optional[str] = None,
        **kwargs
    ):
        super().__init__(message, **kwargs)
        self.internal_error_type = internal_error_type
        self.traceback = traceback


# =============================================================================
# Helper Functions
# =============================================================================

def error_from_exception(
    exc: Exception,
    *,
    preflight_id: Optional[str] = None,
    launch_id: Optional[str] = None,
    process_id: Optional[int] = None,
) -> AgentPreflightError:
    """Convert an arbitrary exception to a typed preflight error.
    
    Preserves exception message and context without runtime state.
    """
    if isinstance(exc, AgentPreflightError):
        return exc
    
    # Map common exception types
    error_map: Dict[str, type] = {
        "ValueError": PreflightRequestError,
        "FileNotFoundError": PreflightRootError,
        "PermissionError": PreflightFilesystemError,
        "SyntaxError": PreflightCompilationError,
    }
    
    exc_type = type(exc).__name__
    error_class = error_map.get(exc_type, AgentPreflightError)
    
    return error_class(
        str(exc),
        preflight_id=preflight_id,
        launch_id=launch_id,
        process_id=process_id,
    )