# Knowledge Audit Exceptions - Phase 6.10
# =======================================

"""
Exception classes for the Knowledge Audit subsystem.
"""

from __future__ import annotations

from typing import Dict, List, Tuple, Any


# =============================================================================
# BASE EXCEPTION
# =============================================================================

class KnowledgeAuditError(Exception):
    """
    Base exception for all knowledge audit errors.
    
    All custom exceptions in the knowledge audit module inherit from this.
    """
    
    def __init__(self, message: str, *, details: Dict[str, Any] | None = None):
        """
        Initialize a knowledge audit error.
        
        Args:
            message: Human-readable error message
            details: Optional dictionary of additional context
        """
        super().__init__(message)
        self.message = message
        self.details = details or {}
    
    def __repr__(self) -> str:
        """Return detailed representation."""
        if self.details:
            return f"{self.__class__.__name__}({self.message!r}, details={self.details})"
        return f"{self.__class__.__name__}({self.message!r})"


# =============================================================================
# REQUEST ERRORS
# =============================================================================

class InvalidAuditRequest(KnowledgeAuditError):
    """
    Raised when an audit request is invalid or malformed.
    
    This exception indicates that the request cannot be processed due to:
        - Missing required fields
        - Invalid field values
        - Inconsistent parameters
    """
    
    def __init__(
        self,
        message: str = "Invalid audit request",
        *,
        errors: List[str] | None = None,
        invalid_fields: Dict[str, Any] | None = None,
    ):
        """
        Initialize an invalid audit request error.
        
        Args:
            message: Error message
            errors: List of specific validation errors
            invalid_fields: Fields that failed validation
        """
        details = {
            "errors": errors or [],
            "invalid_fields": invalid_fields or {},
        }
        super().__init__(message, details=details)
        self.errors = details["errors"]
        self.invalid_fields = details["invalid_fields"]


class AuditRequestTimeout(KnowledgeAuditError):
    """
    Raised when an audit request exceeds its timeout limit.
    """
    
    def __init__(
        self,
        message: str = "Audit request timed out",
        *,
        requested_timeout: float | None = None,
        elapsed_time: float | None = None,
    ):
        details = {
            "requested_timeout": requested_timeout,
            "elapsed_time": elapsed_time,
        }
        super().__init__(message, details=details)
        self.requested_timeout = details["requested_timeout"]
        self.elapsed_time = details["elapsed_time"]


# =============================================================================
# ENGINE ERRORS
# =============================================================================

class AuditEngineError(KnowledgeAuditError):
    """
    Raised when an audit engine encounters an error during execution.
    
    This indicates a failure in the audit logic itself, not invalid input.
    """
    
    def __init__(
        self,
        message: str = "Audit engine error",
        *,
        engine_name: str | None = None,
        failed_target_id: str | None = None,
    ):
        details = {
            "engine_name": engine_name,
            "failed_target_id": failed_target_id,
        }
        super().__init__(message, details=details)
        self.engine_name = details["engine_name"]
        self.failed_target_id = details["failed_target_id"]


class EngineConfigurationError(KnowledgeAuditError):
    """
    Raised when an audit engine is misconfigured.
    """
    
    def __init__(
        self,
        message: str = "Engine configuration error",
        *,
        engine_name: str | None = None,
        config_errors: List[str] | None = None,
    ):
        details = {
            "engine_name": engine_name,
            "config_errors": config_errors or [],
        }
        super().__init__(message, details=details)
        self.engine_name = details["engine_name"]
        self.config_errors = details["config_errors"]


# =============================================================================
# DATA ACCESS ERRORS
# =============================================================================

class ArtifactNotFoundError(KnowledgeAuditError):
    """
    Raised when a required knowledge artifact cannot be found.
    """
    
    def __init__(
        self,
        message: str = "Artifact not found",
        *,
        artifact_id: str | None = None,
        artifact_type: str | None = None,
    ):
        details = {
            "artifact_id": artifact_id,
            "artifact_type": artifact_type,
        }
        super().__init__(message, details=details)
        self.artifact_id = details["artifact_id"]
        self.artifact_type = details["artifact_type"]


class DependencyNotFoundError(KnowledgeAuditError):
    """
    Raised when a dependency cannot be resolved.
    """
    
    def __init__(
        self,
        message: str = "Dependency not found",
        *,
        missing_dependency: str | None = None,
        referencing_artifact: str | None = None,
    ):
        details = {
            "missing_dependency": missing_dependency,
            "referencing_artifact": referencing_artifact,
        }
        super().__init__(message, details=details)
        self.missing_dependency = details["missing_dependency"]
        self.referencing_artifact = details["referencing_artifact"]


# =============================================================================
# REPORT ERRORS
# =============================================================================

class ReportSerializationError(KnowledgeAuditError):
    """
    Raised when audit report serialization fails.
    """
    
    def __init__(
        self,
        message: str = "Report serialization error",
        *,
        report_id: str | None = None,
        format_type: str | None = None,
    ):
        details = {
            "report_id": report_id,
            "format_type": format_type,
        }
        super().__init__(message, details=details)
        self.report_id = details["report_id"]
        self.format_type = details["format_type"]


class ReportDeserializationError(KnowledgeAuditError):
    """
    Raised when audit report deserialization fails.
    """
    
    def __init__(
        self,
        message: str = "Report deserialization error",
        *,
        data_source: str | None = None,
        format_type: str | None = None,
    ):
        details = {
            "data_source": data_source,
            "format_type": format_type,
        }
        super().__init__(message, details=details)
        self.data_source = details["data_source"]
        self.format_type = details["format_type"]


# =============================================================================
# SESSION ERRORS
# =============================================================================

class AuditSessionError(KnowledgeAuditError):
    """
    Raised when an audit session encounters an error.
    """
    
    def __init__(
        self,
        message: str = "Audit session error",
        *,
        session_id: str | None = None,
    ):
        details = {
            "session_id": session_id,
        }
        super().__init__(message, details=details)
        self.session_id = details["session_id"]


class SessionAlreadyActive(AuditSessionError):
    """
    Raised when attempting to start a session that is already active.
    """
    
    def __init__(
        self,
        message: str = "Audit session already active",
        *,
        session_id: str | None = None,
    ):
        super().__init__(message, session_id=session_id)


class SessionNotActive(AuditSessionError):
    """
    Raised when attempting to use an inactive audit session.
    """
    
    def __init__(
        self,
        message: str = "Audit session not active",
        *,
        session_id: str | None = None,
    ):
        super().__init__(message, session_id=session_id)


# =============================================================================
# INTEGRITY ERRORS
# =============================================================================

class IntegrityCheckError(KnowledgeAuditError):
    """
    Raised when an integrity check fails.
    """
    
    def __init__(
        self,
        message: str = "Integrity check failed",
        *,
        check_name: str | None = None,
        failed_items: List[str] | None = None,
    ):
        details = {
            "check_name": check_name,
            "failed_items": failed_items or [],
        }
        super().__init__(message, details=details)
        self.check_name = details["check_name"]
        self.failed_items = details["failed_items"]


# =============================================================================
# EXPORTS
# =============================================================================

__all__ = [
    # Base exception
    "KnowledgeAuditError",
    
    # Request errors
    "InvalidAuditRequest",
    "AuditRequestTimeout",
    
    # Engine errors
    "AuditEngineError",
    "EngineConfigurationError",
    
    # Data access errors
    "ArtifactNotFoundError",
    "DependencyNotFoundError",
    
    # Report errors
    "ReportSerializationError",
    "ReportDeserializationError",
    
    # Session errors
    "AuditSessionError",
    "SessionAlreadyActive",
    "SessionNotActive",
    
    # Integrity errors
    "IntegrityCheckError",
]