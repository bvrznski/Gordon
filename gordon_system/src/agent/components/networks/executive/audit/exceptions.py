# Audit Exceptions - Gordon Executive Network Audit Subsystem
# =============================================================

"""
Exception types for the Executive Audit subsystem.
"""

from typing import Optional, Any


class AuditError(Exception):
    """
    Base exception for all audit-related errors.
    
    This is the parent class for all custom exceptions raised by the
    audit subsystem. All exceptions in this module inherit from this base.
    
    Attributes:
        message: Human-readable error description
        code: Optional error code for programmatic handling
    """
    
    def __init__(
        self,
        message: str,
        code: Optional[str] = None,
        details: Optional[dict] = None,
    ):
        """
        Initialize an AuditError.
        
        Args:
            message: Human-readable error description
            code: Optional error code for programmatic handling
            details: Optional dictionary of additional context data
        """
        super().__init__(message)
        self.message = message
        self.code = code or "AUDIT_ERROR"
        self.details = details or {}
    
    def to_dict(self) -> dict:
        """Convert exception to a dictionary for serialization."""
        return {
            "error": True,
            "type": type(self).__name__,
            "code": self.code,
            "message": self.message,
            "details": self.details,
        }


class AuditNotFoundError(AuditError):
    """
    Raised when an audit resource is not found.
    
    This exception is raised when attempting to access an audit session,
    report, or other resource that does not exist in the system.
    
    Attributes:
        resource_id: The ID of the missing resource
        resource_type: The type of resource (e.g., 'session', 'report')
    """
    
    def __init__(
        self,
        resource_id: str,
        resource_type: str = "resource",
        message: Optional[str] = None,
    ):
        """Initialize an AuditNotFoundError."""
        if message is None:
            message = f"{resource_type.capitalize()} '{resource_id}' not found"
        super().__init__(message, code="AUDIT_NOT_FOUND")
        self.resource_id = resource_id
        self.resource_type = resource_type


class AuditValidationError(AuditError):
    """
    Raised when audit data validation fails.
    
    This exception is raised when the audit engine encounters data that
    does not conform to expected formats or constraints.
    
    Attributes:
        field: The field or context where validation failed
        value: The invalid value
        reason: Explanation of why validation failed
    """
    
    def __init__(
        self,
        message: str,
        field: Optional[str] = None,
        value: Optional[Any] = None,
    ):
        """Initialize an AuditValidationError."""
        details = {"field": field, "value": repr(value)} if field else {}
        super().__init__(message, code="AUDIT_VALIDATION_ERROR", details=details)
        self.field = field
        self.value = value


class AuditTimeoutError(AuditError):
    """
    Raised when an audit operation exceeds its timeout.
    
    This exception is raised when the audit engine cannot complete an
    operation within the configured time limit.
    
    Attributes:
        operation: The name of the timed-out operation
        timeout_seconds: The timeout that was exceeded
    """
    
    def __init__(
        self,
        operation: str,
        timeout_seconds: float,
        message: Optional[str] = None,
    ):
        """Initialize an AuditTimeoutError."""
        if message is None:
            message = f"Audit operation '{operation}' timed out after {timeout_seconds}s"
        super().__init__(message, code="AUDIT_TIMEOUT")
        self.operation = operation
        self.timeout_seconds = timeout_seconds


class AuditIntegrityError(AuditError):
    """
    Raised when audit subsystem integrity is compromised.
    
    This exception indicates that the audit subsystem's internal state
    may be corrupted or inconsistent, potentially compromising audit quality.
    """
    
    def __init__(self, message: str, details: Optional[dict] = None):
        """Initialize an AuditIntegrityError."""
        super().__init__(
            message,
            code="AUDIT_INTEGRITY_ERROR",
            details=details or {},
        )


class AuditDegradationWarning(AuditError):
    """
    Raised when audit functionality is degraded but still operational.
    
    This exception indicates that some audit capabilities are unavailable
    due to missing dependencies or configuration issues, but the audit
    can continue with reduced functionality.
    
    Attributes:
        degraded_components: List of components that are unavailable
        fallback_applied: Description of fallback behavior used
    """
    
    def __init__(
        self,
        degraded_components: list,
        fallback_applied: str = "no_fallback",
        message: Optional[str] = None,
    ):
        """Initialize an AuditDegradationWarning."""
        if message is None:
            message = f"Audit functionality degraded due to missing components: {degraded_components}"
        super().__init__(
            message,
            code="AUDIT_DEGRADATION_WARNING",
            details={"components": degraded_components, "fallback": fallback_applied},
        )
        self.degraded_components = degraded_components
        self.fallback_applied = fallback_applied


class AuditEngineError(AuditError):
    """
    Raised when the audit engine encounters an internal error.
    
    This exception indicates a problem with the audit engine itself,
    not necessarily with the data being audited.
    """
    
    def __init__(self, message: str, operation: Optional[str] = None):
        """Initialize an AuditEngineError."""
        details = {"operation": operation} if operation else {}
        super().__init__(message, code="AUDIT_ENGINE_ERROR", details=details)


class AuditReportError(AuditError):
    """
    Raised when audit report generation fails.
    
    This exception indicates a problem with formatting or serializing
    the audit findings and recommendations into a report.
    """
    
    def __init__(self, message: str, report_id: Optional[str] = None):
        """Initialize an AuditReportError."""
        details = {"report_id": report_id} if report_id else {}
        super().__init__(message, code="AUDIT_REPORT_ERROR", details=details)