# Gordon Workspace Network Audit Exceptions
# =========================================

"""
Exception types used throughout the Workspace Audit subsystem.
"""

from __future__ import annotations

from typing import Optional, Tuple


class AuditError(Exception):
    """
    Base exception for all audit-related errors.
    
    This is the parent class for all exceptions raised by the audit subsystem.
    """
    
    def __init__(self, message: str, *args, **kwargs):
        super().__init__(message, *args)
        self.message = message
        self.context = kwargs.get("context", {})
    
    def __str__(self) -> str:
        if self.context:
            return f"{self.message} (context: {self.context})"
        return self.message


class AuditValidationError(AuditError):
    """
    Exception raised when validation fails.
    
    This exception indicates that data or state being audited does not
    conform to expected invariants or constraints.
    """
    
    def __init__(
        self,
        message: str,
        validation_domain: Optional[str] = None,
        affected_objects: Optional[Tuple[str, ...]] = None,
        **kwargs,
    ):
        super().__init__(message, **kwargs)
        self.validation_domain = validation_domain
        self.affected_objects = affected_objects or ()


class AuditIntegrityError(AuditError):
    """
    Exception raised when graph integrity is compromised.
    
    This indicates structural corruption in the workspace that may affect
    correctness of audit results.
    """
    
    def __init__(
        self,
        message: str,
        corruption_type: Optional[str] = None,
        **kwargs,
    ):
        super().__init__(message, **kwargs)
        self.corruption_type = corruption_type


class AuditTimeoutError(AuditError):
    """
    Exception raised when an audit operation exceeds its time limit.
    
    This may indicate a performance issue or overly complex validation task.
    """
    
    def __init__(
        self,
        message: str,
        timeout_seconds: float,
        **kwargs,
    ):
        super().__init__(message, **kwargs)
        self.timeout_seconds = timeout_seconds


class AuditConfigurationError(AuditError):
    """
    Exception raised when audit configuration is invalid.
    
    This indicates misconfiguration of the audit subsystem that prevents
    proper operation.
    """
    
    def __init__(
        self,
        message: str,
        config_key: Optional[str] = None,
        **kwargs,
    ):
        super().__init__(message, **kwargs)
        self.config_key = config_key


class AuditEngineError(AuditError):
    """
    Exception raised when the audit engine encounters an error.
    
    This may indicate internal errors in the audit processing pipeline.
    """
    
    def __init__(
        self,
        message: str,
        engine_state: Optional[str] = None,
        **kwargs,
    ):
        super().__init__(message, **kwargs)
        self.engine_state = engine_state


class AuditValidatorError(AuditError):
    """
    Exception raised when a validator encounters an error.
    
    This exception may be raised by individual validators during their
    analysis phase. The audit engine should handle this gracefully.
    """
    
    def __init__(
        self,
        message: str,
        validator_name: Optional[str] = None,
        **kwargs,
    ):
        super().__init__(message, **kwargs)
        self.validator_name = validator_name


class AuditReportError(AuditError):
    """
    Exception raised when report generation fails.
    
    This may indicate issues in formatting or serialization of audit results.
    """
    
    def __init__(
        self,
        message: str,
        report_type: Optional[str] = None,
        **kwargs,
    ):
        super().__init__(message, **kwargs)
        self.report_type = report_type


class AuditHealthError(AuditError):
    """
    Exception raised when health assessment fails.
    
    This may indicate issues in collecting or aggregating subsystem health data.
    """
    
    def __init__(
        self,
        message: str,
        component_name: Optional[str] = None,
        **kwargs,
    ):
        super().__init__(message, **kwargs)
        self.component_name = component_name


# =============================================================================
# VALIDATION ERROR SPECIFICS
# =============================================================================

class NodeValidationError(AuditValidationError):
    """Exception raised when node validation fails."""


class EdgeValidationError(AuditValidationError):
    """Exception raised when edge validation fails."""


class ActivationValidationError(AuditValidationError):
    """Exception raised when activation validation fails."""


class SalienceValidationError(AuditValidationError):
    """Exception raised when salience validation fails."""


class ProvenanceValidationError(AuditValidationError):
    """Exception raised when provenance validation fails."""


class LifecycleValidationError(AuditValidationError):
    """Exception raised when lifecycle validation fails."""


# =============================================================================
# EXPORTS
# =============================================================================

__all__: Tuple[str, ...] = (
    "AuditError",
    "AuditValidationError",
    "AuditIntegrityError",
    "AuditTimeoutError",
    "AuditConfigurationError",
    "AuditEngineError",
    "AuditValidatorError",
    "AuditReportError",
    "AuditHealthError",
    "NodeValidationError",
    "EdgeValidationError",
    "ActivationValidationError",
    "SalienceValidationError",
    "ProvenanceValidationError",
    "LifecycleValidationError",
)
