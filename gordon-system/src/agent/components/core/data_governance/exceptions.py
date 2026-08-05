# Data Governance Exceptions
# ==========================

"""
Exception hierarchy for data governance operations.
"""

from typing import Optional, List, Any
from .models import LifecycleState


class DataGovernanceError(Exception):
    """Base exception for all data governance errors."""
    
    def __init__(self, message: str, *args: object, cause: Optional[Exception] = None) -> None:
        super().__init__(message, *args)
        self.message = message
        self.cause = cause
    
    def __str__(self) -> str:
        if self.cause:
            return f"{self.message} (caused by: {self.cause})"
        return self.message


class ClassificationError(DataGovernanceError):
    """Raised when classification operation fails."""
    
    def __init__(
        self,
        message: str,
        *args: object,
        information_id: Optional[str] = None,
        invalid_level: Optional[str] = None,
        cause: Optional[Exception] = None
    ) -> None:
        super().__init__(message, *args, cause=cause)
        self.information_id = information_id
        self.invalid_level = invalid_level


class OwnershipError(DataGovernanceError):
    """Raised when ownership operation fails."""
    
    def __init__(
        self,
        message: str,
        *args: object,
        information_id: Optional[str] = None,
        current_owner: Optional[str] = None,
        new_owner: Optional[str] = None,
        cause: Optional[Exception] = None
    ) -> None:
        super().__init__(message, *args, cause=cause)
        self.information_id = information_id
        self.current_owner = current_owner
        self.new_owner = new_owner


class LifecycleError(DataGovernanceError):
    """Raised when lifecycle transition is invalid."""
    
    def __init__(
        self,
        message: str,
        *args: object,
        information_id: Optional[str] = None,
        from_state: Optional[LifecycleState] = None,
        to_state: Optional[LifecycleState] = None,
        cause: Optional[Exception] = None
    ) -> None:
        super().__init__(message, *args, cause=cause)
        self.information_id = information_id
        self.from_state = from_state
        self.to_state = to_state


class MetadataError(DataGovernanceError):
    """Raised when metadata operation fails."""
    
    def __init__(
        self,
        message: str,
        *args: object,
        schema_id: Optional[str] = None,
        invalid_field: Optional[str] = None,
        cause: Optional[Exception] = None
    ) -> None:
        super().__init__(message, *args, cause=cause)
        self.schema_id = schema_id
        self.invalid_field = invalid_field


class PrivacyError(DataGovernanceError):
    """Raised when privacy policy violation occurs."""
    
    def __init__(
        self,
        message: str,
        *args: object,
        information_id: Optional[str] = None,
        policy_violated: Optional[str] = None,
        cause: Optional[Exception] = None
    ) -> None:
        super().__init__(message, *args, cause=cause)
        self.information_id = information_id
        self.policy_violated = policy_violated


class RetentionError(DataGovernanceError):
    """Raised when retention operation fails."""
    
    def __init__(
        self,
        message: str,
        *args: object,
        information_id: Optional[str] = None,
        policy_id: Optional[str] = None,
        cause: Optional[Exception] = None
    ) -> None:
        super().__init__(message, *args, cause=cause)
        self.information_id = information_id
        self.policy_id = policy_id


class ArchiveError(DataGovernanceError):
    """Raised when archive operation fails."""
    
    def __init__(
        self,
        message: str,
        *args: object,
        information_id: Optional[str] = None,
        archive_id: Optional[str] = None,
        cause: Optional[Exception] = None
    ) -> None:
        super().__init__(message, *args, cause=cause)
        self.information_id = information_id
        self.archive_id = archive_id


class DisposalError(DataGovernanceError):
    """Raised when disposal operation fails."""
    
    def __init__(
        self,
        message: str,
        *args: object,
        information_id: Optional[str] = None,
        disposal_id: Optional[str] = None,
        cause: Optional[Exception] = None
    ) -> None:
        super().__init__(message, *args, cause=cause)
        self.information_id = information_id
        self.disposal_id = disposal_id


class IntegrityError(DataGovernanceError):
    """Raised when data integrity verification fails."""
    
    def __init__(
        self,
        message: str,
        *args: object,
        information_id: Optional[str] = None,
        expected_hash: Optional[str] = None,
        actual_hash: Optional[str] = None,
        cause: Optional[Exception] = None
    ) -> None:
        super().__init__(message, *args, cause=cause)
        self.information_id = information_id
        self.expected_hash = expected_hash
        self.actual_hash = actual_hash


class DuplicateRecordError(DataGovernanceError):
    """Raised when attempting to create a duplicate record."""
    
    def __init__(
        self,
        message: str,
        *args: object,
        record_type: Optional[str] = None,
        record_id: Optional[str] = None,
        cause: Optional[Exception] = None
    ) -> None:
        super().__init__(message, *args, cause=cause)
        self.record_type = record_type
        self.record_id = record_id


__all__ = [
    "DataGovernanceError",
    "ClassificationError",
    "OwnershipError",
    "LifecycleError",
    "MetadataError",
    "PrivacyError",
    "RetentionError",
    "ArchiveError",
    "DisposalError",
    "IntegrityError",
    "DuplicateRecordError",
]