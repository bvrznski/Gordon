# Memory Audit Exceptions - Phase 5.1.9
# =======================================

"""
Exception types for the Memory Audit subsystem.

All audit exceptions inherit from MemoryAuditError to enable consistent
error handling throughout the subsystem.
"""

from __future__ import annotations


# =============================================================================
# BASE EXCEPTIONS
# =============================================================================


class MemoryAuditError(Exception):
    """
    Base exception for all memory audit errors.
    
    This is the parent class for all custom exceptions in the audit subsystem.
    Code catching MemoryAuditError will catch any audit-specific error.
    
    Anti-Patterns Rejected:
        - Generic Exception (use specific subclasses)
        - Silent failures (always raise with message)
    """
    
    def __init__(self, message: str):
        """
        Initialize the audit exception.
        
        Args:
            message: Human-readable error description
        """
        super().__init__(message)
        self.message = message


class MemoryAuditIntegrityError(MemoryAuditError):
    """
    Raised when memory integrity checks fail.
    
    This exception is raised when:
        - Memory data is corrupted or malformed
        - Checksums don't match expected values
        - Data appears truncated
    
    Anti-Patterns Rejected:
        - Hiding corruption (always raise this)
    """
    
    def __init__(self, memory_id: str, details: str):
        """
        Initialize a memory integrity error.
        
        Args:
            memory_id: ID of the affected memory artifact
            details: Specific integrity issue description
        """
        self.memory_id = memory_id
        self.details = details
        super().__init__(f"Memory integrity failure for '{memory_id}': {details}")


class MemoryAuditConsistencyError(MemoryAuditError):
    """
    Raised when consistency validation fails.
    
    This exception is raised when:
        - Cross-memory references are inconsistent
        - Knowledge contradictions are detected
        - Identity or temporal inconsistencies exist
    
    Anti-Patterns Rejected:
        - Silently allowing contradictions (always raise)
    """
    
    def __init__(self, finding: str):
        """
        Initialize a consistency error.
        
        Args:
            finding: Description of the inconsistency found
        """
        self.finding = finding
        super().__init__(f"Consistency violation: {finding}")


class MemoryAuditReferenceError(MemoryAuditError):
    """
    Raised when reference validation fails.
    
    This exception is raised when:
        - A reference points to non-existent memory
        - A circular reference is detected
        - An orphan node is found
    
    Anti-Patterns Rejected:
        - Following broken references (raise this instead)
    """
    
    def __init__(self, ref_type: str, source_id: str, target_id: str):
        """
        Initialize a reference error.
        
        Args:
            ref_type: Type of reference (parent, child, semantic, etc.)
            source_id: ID of the referencing artifact
            target_id: ID of the referenced artifact (or "missing" if not found)
        """
        self.ref_type = ref_type
        self.source_id = source_id
        self.target_id = target_id
        super().__init__(
            f"Reference {ref_type} from '{source_id}' to '{target_id}' is invalid"
        )


class MemoryAuditNotFoundError(MemoryAuditError):
    """
    Raised when memory cannot be found during audit.
    
    This exception is raised when:
        - A referenced memory artifact doesn't exist
        - An expected index or structure is missing
    
    Anti-Patterns Rejected:
        - Returning None (always raise this)
    """
    
    def __init__(self, search_type: str, search_key: str):
        """
        Initialize a not found error.
        
        Args:
            search_type: What was being searched (artifact_id, index_name, etc.)
            search_key: The key that wasn't found
        """
        self.search_type = search_type
        self.search_key = search_key
        super().__init__(f"{search_type} '{search_key}' not found")


# =============================================================================
# AUDIT RUNTIME EXCEPTIONS
# =============================================================================


class MemoryAuditRuntimeError(MemoryAuditError):
    """
    Raised for audit runtime failures.
    
    This exception is raised when:
        - An adapter fails to load
        - A validator is misconfigured
        - The audit engine encounters an unexpected state
    
    Anti-Patterns Rejected:
        - Crashing without context (always include details)
    """
    
    def __init__(self, operation: str, details: str):
        """
        Initialize a runtime error.
        
        Args:
            operation: What operation was being performed
            details: Specific failure description
        """
        self.operation = operation
        self.details = details
        super().__init__(f"Audit runtime error during '{operation}': {details}")


class MemoryAuditAdapterError(MemoryAuditRuntimeError):
    """
    Raised when an adapter fails.
    
    This exception is raised when:
        - An adapter cannot connect to memory
        - An adapter returns invalid data
        - Adapter configuration is invalid
    
    Anti-Patterns Rejected:
        - Swallowing adapter failures (always raise)
    """
    
    def __init__(self, adapter_name: str, details: str):
        """
        Initialize an adapter error.
        
        Args:
            adapter_name: Name of the failing adapter
            details: Specific failure description
        """
        self.adapter_name = adapter_name
        super().__init__(f"adapter '{adapter_name}'", details)


class MemoryAuditValidatorError(MemoryAuditRuntimeError):
    """
    Raised when a validator fails.
    
    This exception is raised when:
        - A validator encounters malformed data
        - Validator configuration is invalid
        - Validation logic cannot proceed
    
    Anti-Patterns Rejected:
        - Skipping validation (always raise)
    """
    
    def __init__(self, validator_name: str, details: str):
        """
        Initialize a validator error.
        
        Args:
            validator_name: Name of the failing validator
            details: Specific failure description
        """
        self.validator_name = validator_name
        super().__init__(f"validator '{validator_name}'", details)


# =============================================================================
# AUDIT STATE EXCEPTIONS
# =============================================================================


class MemoryAuditStateError(MemoryAuditError):
    """
    Raised when audit session is in invalid state.
    
    This exception is raised when:
        - Session is queried before completion
        - Operations are performed after report generation
        - Phase transitions are invalid
    
    Anti-Patterns Rejected:
        - Continuing with invalid state (always raise)
    """
    
    def __init__(self, current_state: str, expected_states: str, operation: str):
        """
        Initialize a state error.
        
        Args:
            current_state: Current session state
            expected_states: What states are valid for this operation
            operation: Operation that was attempted
        """
        self.current_state = current_state
        self.expected_states = expected_states
        super().__init__(
            f"Cannot perform '{operation}' in state '{current_state}'. "
            f"Expected states: {expected_states}"
        )


class MemoryAuditSessionError(MemoryAuditStateError):
    """
    Raised when audit session encounters an error.
    
    This exception is raised when:
        - Session ID is not unique
        - Session cannot transition between phases
        - Session state becomes corrupted
    
    Anti-Patterns Rejected:
        - Continuing with corrupted session (always raise)
    """
    
    def __init__(self, session_id: str, details: str):
        """
        Initialize a session error.
        
        Args:
            session_id: ID of the affected session
            details: Specific failure description
        """
        self.session_id = session_id
        super().__init__(
            f"session '{session_id}'", "valid session state", details
        )


# =============================================================================
# AUDIT REPORT EXCEPTIONS
# =============================================================================


class MemoryAuditReportError(MemoryAuditError):
    """
    Raised when report generation fails.
    
    This exception is raised when:
        - Report data is inconsistent
        - Required fields are missing
        - Report cannot be serialized
    
    Anti-Patterns Rejected:
        - Generating incomplete reports (always raise)
    """
    
    def __init__(self, details: str):
        """
        Initialize a report error.
        
        Args:
            details: Specific failure description
        """
        super().__init__(f"Report generation failed: {details}")


class MemoryAuditReportIntegrityError(MemoryAuditReportError):
    """
    Raised when report integrity checks fail.
    
    This exception is raised when:
        - Report was modified after creation (shouldn't happen with frozen dataclasses)
        - Report timestamps are inconsistent
        - Report references missing session or request
    
    Anti-Patterns Rejected:
        - Allowing corrupted reports (always raise)
    """
    
    def __init__(self, report_id: str, details: str):
        """
        Initialize a report integrity error.
        
        Args:
            report_id: ID of the affected report
            details: Specific integrity failure description
        """
        self.report_id = report_id
        super().__init__(f"Report '{report_id}' integrity failure: {details}")


# =============================================================================
# UTILITY FUNCTIONS
# =============================================================================


def raise_if(condition: bool, error_class, *args, **kwargs):
    """
    Raise an exception if condition is true.
    
    Args:
        condition: If True, raise the exception
        error_class: Exception class to instantiate
        *args, **kwargs: Arguments for exception constructor
    
    Anti-Patterns Rejected:
        - Using this instead of if statements (use directly when readable)
    """
    if condition:
        raise error_class(*args, **kwargs)


__all__ = [
    # Base exceptions
    "MemoryAuditError",
    "MemoryAuditIntegrityError",
    "MemoryAuditConsistencyError",
    "MemoryAuditReferenceError",
    "MemoryAuditNotFoundError",
    # Runtime exceptions
    "MemoryAuditRuntimeError",
    "MemoryAuditAdapterError",
    "MemoryAuditValidatorError",
    # State exceptions
    "MemoryAuditStateError",
    "MemoryAuditSessionError",
    # Report exceptions
    "MemoryAuditReportError",
    "MemoryAuditReportIntegrityError",
    # Utility functions
    "raise_if",
]