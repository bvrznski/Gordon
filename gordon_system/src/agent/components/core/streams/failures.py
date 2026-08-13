# Stream Failure Taxonomy - Phase 3.11.2
# ======================================

"""
Typed failures for stream operations.

These failures integrate with Phase 3.7.35 ContractFailure system.
All failures preserve operation context, retryability, and diagnostic info.
"""

from dataclasses import dataclass, field
from enum import Enum, auto
from typing import Optional, Tuple

from .__init__ import (
    StreamId,
    StreamGenerationId,
    StreamRecordId,
    StreamCommitId,
    ProducerId,
    CorrelationId,
)


# =============================================================================
# Failure Categories (Neutral - no semantics)
# =============================================================================

class StreamFailureCategory(Enum):
    """Category of stream failure for classification."""
    
    # Identity validation failures
    INVALID_STREAM_ID = "invalid_stream_id"
    INVALID_GENERATION_ID = "invalid_generation_id"
    INVALID_RECORD_ID = "invalid_record_id"
    INVALID_COMMIT_ID = "invalid_commit_id"
    
    # Position and ordering failures
    INVALID_SEQUENCE_POSITION = "invalid_sequence_position"
    SEQUENCE_CONFLICT = "sequence_conflict"
    SEQUENCE_OVERFLOW = "sequence_overflow"
    INCOMPARABLE_POSITIONS = "incomparable_positions"
    
    # Generation state failures
    GENERATION_CLOSED = "generation_closed"
    GENERATION_LINEAGE_MISMATCH = "generation_lineage_mismatch"
    
    # Commit failures
    COMMIT_TIMEOUT = "commit_timeout"
    COMMIT_CANCELLED = "commit_cancelled"
    COMMIT_PUBLICATION_FAILED = "commit_publication_failed"
    
    # Validation failures
    INVALID_RECORD = "invalid_record"
    SCHEMA_MISMATCH = "schema_mismatch"
    CONTRACT_VERSION_MISMATCH = "contract_version_mismatch"
    
    # Duplicate detection failures
    DUPLICATE_RECORD = "duplicate_record"
    IDEMPOTENCY_CONFLICT = "idempotency_conflict"
    
    # Authorization failures
    PRODUCER_NOT_AUTHORIZED = "producer_not_authorized"
    IDENTITY_FORGED = "identity_forged"
    
    # Serialization failures
    SERIALIZATION_FAILURE = "serialization_failure"
    
    # Integrity failures
    INTEGRITY_CHECK_FAILED = "integrity_check_failed"
    ARTIFACT_UNAVAILABLE = "artifact_unavailable"
    
    # Resource failures
    RESOURCE_DENIED = "resource_denied"
    CAPACITY_EXCEEDED = "capacity_exceeded"
    
    # Infrastructure failures (translated from lower layer)
    INFRASTRUCTURE_FAILURE = "infrastructure_failure"


# =============================================================================
# Base Failure Type
# =============================================================================

class StreamError(Exception):
    """Base exception for stream operations."""
    pass


class StreamIdentitiesIncompatibleError(StreamError, ValueError):
    """Stream identities are incompatible for comparison or combination."""
    def __init__(self, stream_id1: str, stream_id2: str, reason: str):
        self.stream_id1 = stream_id1
        self.stream_id2 = stream_id2
        self.reason = reason
        super().__init__(
            f"Incompatible stream identities '{stream_id1}' and '{stream_id2}': {reason}"
        )


class StreamPositionValidationError(StreamError, ValueError):
    """Stream position validation failed."""
    def __init__(self, position: str, error: str):
        self.position = position
        self.error = error
        super().__init__(f"Invalid stream position '{position}': {error}")


# =============================================================================
# Identity Validation Failures
# =============================================================================

class InvalidStreamIdError(StreamError, ValueError):
    """Stream ID is invalid."""
    
    def __init__(self, value: str, reason: Optional[str] = None):
        self.value = value
        self.reason = reason or "invalid_format"
        super().__init__(f"Invalid StreamId '{value}': {reason}")


class InvalidGenerationIdError(StreamError, ValueError):
    """Generation ID is invalid."""
    
    def __init__(self, value: str, reason: Optional[str] = None):
        self.value = value
        self.reason = reason or "invalid_format"
        super().__init__(f"Invalid GenerationId '{value}': {reason}")


class InvalidRecordIdError(StreamError, ValueError):
    """Record ID is invalid."""
    
    def __init__(self, value: str, reason: Optional[str] = None):
        self.value = value
        self.reason = reason or "invalid_format"
        super().__init__(f"Invalid RecordId '{value}': {reason}")


class InvalidCommitIdError(StreamError, ValueError):
    """Commit ID is invalid."""
    
    def __init__(self, value: str, reason: Optional[str] = None):
        self.value = value
        self.reason = reason or "invalid_format"
        super().__init__(f"Invalid CommitId '{value}': {reason}")


# =============================================================================
# Sequence and Ordering Failures
# =============================================================================

class InvalidSequencePositionError(StreamError, ValueError):
    """Invalid sequence position for commit."""
    
    def __init__(
        self,
        generation_id: StreamGenerationId,
        expected: int,
        actual: int
    ):
        self.generation_id = generation_id
        self.expected = expected
        self.actual = actual
        super().__init__(
            f"Invalid sequence {actual} for generation {generation_id.value}. "
            f"Expected: {expected}"
        )


class SequenceConflictError(StreamError):
    """Sequence position conflict detected."""
    
    def __init__(
        self,
        stream_id: StreamId,
        generation_id: StreamGenerationId,
        conflicting_position: int,
        existing_record_id: Optional[StreamRecordId] = None
    ):
        self.stream_id = stream_id
        self.generation_id = generation_id
        self.conflicting_position = conflicting_position
        self.existing_record_id = existing_record_id
        super().__init__(
            f"Sequence conflict at position {conflicting_position} in "
            f"{stream_id.value}:{generation_id.number}"
            + (f" (existing: {existing_record_id.value})" if existing_record_id else "")
        )


class SequenceOverflowError(StreamError):
    """Sequence number overflow."""
    
    def __init__(
        self,
        stream_id: StreamId,
        generation_id: StreamGenerationId,
        max_sequence: int
    ):
        self.stream_id = stream_id
        self.generation_id = generation_id
        self.max_sequence = max_sequence
        super().__init__(
            f"Sequence overflow in {stream_id.value}:{generation_id.number}. "
            f"Maximum sequence is {max_sequence}"
        )


class IncomparableStreamPositionError(StreamError, ValueError):
    """Positions cannot be compared (different streams or generations)."""
    
    def __init__(self, message: str):
        super().__init__(message)


# =============================================================================
# Generation State Failures
# =============================================================================

class StreamGenerationClosedError(StreamError):
    """Attempt to commit to a closed generation."""
    
    def __init__(self, generation_id: StreamGenerationId):
        self.generation_id = generation_id
        super().__init__(
            f"Cannot commit to closed generation {generation_id.value}"
        )


class GenerationLineageMismatchError(StreamError):
    """Generation lineage is inconsistent."""
    
    def __init__(
        self,
        expected_lineage: Tuple[StreamGenerationId, ...],
        actual_generation: StreamGenerationId
    ):
        self.expected_lineage = expected_lineage
        self.actual_generation = actual_generation
        super().__init__(
            f"Generation lineage mismatch. Expected chain ending with "
            f"{expected_lineage[-1].value if expected_lineage else 'none'}, got {actual_generation.value}"
        )


# =============================================================================
# Commit Failures
# =============================================================================

class CommitTimeoutError(StreamError):
    """Commit operation timed out."""
    
    def __init__(
        self,
        stream_id: StreamId,
        generation_id: StreamGenerationId,
        timeout_seconds: float
    ):
        self.stream_id = stream_id
        self.generation_id = generation_id
        self.timeout_seconds = timeout_seconds
        super().__init__(
            f"Commit timed out after {timeout_seconds}s for "
            f"{stream_id.value}:{generation_id.number}"
        )


class CommitCancelledError(StreamError):
    """Commit operation was cancelled."""
    
    def __init__(
        self,
        stream_id: StreamId,
        generation_id: StreamGenerationId,
        cancellation_reason: Optional[str] = None
    ):
        self.stream_id = stream_id
        self.generation_id = generation_id
        self.cancellation_reason = cancellation_reason
        super().__init__(
            f"Commit cancelled for {stream_id.value}:{generation_id.number}"
            + (f": {cancellation_reason}" if cancellation_reason else "")
        )


class CommitPublicationFailedError(StreamError):
    """Record committed but passive publication failed."""
    
    def __init__(
        self,
        stream_id: StreamId,
        generation_id: StreamGenerationId,
        record_id: StreamRecordId,
        failure_description: str
    ):
        self.stream_id = stream_id
        self.generation_id = generation_id
        self.record_id = record_id
        self.failure_description = failure_description
        super().__init__(
            f"Commit succeeded but publication failed for {record_id.value}: "
            f"{failure_description}"
        )


# =============================================================================
# Validation Failures
# =============================================================================

class InvalidRecordError(StreamError):
    """Record fails validation."""
    
    def __init__(self, record: Optional[StreamRecordId], errors: Tuple[str, ...]):
        self.record = record
        self.errors = errors
        super().__init__(
            f"Invalid record{f' {record.value}' if record else ''}: "
            f"{'; '.join(errors)}"
        )


class SchemaMismatchError(StreamError):
    """Schema validation failed."""
    
    def __init__(
        self,
        stream_id: StreamId,
        generation_id: StreamGenerationId,
        expected_schema: str,
        actual_schema: str
    ):
        self.stream_id = stream_id
        self.generation_id = generation_id
        self.expected_schema = expected_schema
        self.actual_schema = actual_schema
        super().__init__(
            f"Schema mismatch in {stream_id.value}:{generation_id.number}. "
            f"Expected: {expected_schema}, got: {actual_schema}"
        )


class ContractVersionMismatchError(StreamError):
    """Contract version incompatible."""
    
    def __init__(
        self,
        stream_id: StreamId,
        expected_version: str,
        actual_version: str
    ):
        self.stream_id = stream_id
        self.expected_version = expected_version
        self.actual_version = actual_version
        super().__init__(
            f"Contract version mismatch for {stream_id.value}. "
            f"Expected: {expected_version}, got: {actual_version}"
        )


# =============================================================================
# Duplicate Detection Failures
# =============================================================================

class DuplicateRecordError(StreamError):
    """Duplicate record detected."""
    
    def __init__(
        self,
        existing_record_id: StreamRecordId,
        duplicate_policy: str,
        correlation_id: Optional[CorrelationId] = None
    ):
        self.existing_record_id = existing_record_id
        self.duplicate_policy = duplicate_policy
        self.correlation_id = correlation_id
        super().__init__(
            f"Duplicate record {existing_record_id.value}. "
            f"Policy: {duplicate_policy}"
            + (f". Correlation: {correlation_id.value}" if correlation_id else "")
        )


class IdempotencyConflictError(StreamError):
    """Idempotency key conflict."""
    
    def __init__(
        self,
        idempotency_key: str,
        stream_id: StreamId,
        existing_content_hash: Optional[str],
        proposed_content_hash: Optional[str]
    ):
        self.idempotency_key = idempotency_key
        self.stream_id = stream_id
        self.existing_content_hash = existing_content_hash
        self.proposed_content_hash = proposed_content_hash
        super().__init__(
            f"Idempotency conflict for key '{idempotency_key}' in "
            f"{stream_id.value}. Content mismatch: "
            f"{existing_content_hash} != {proposed_content_hash}"
        )


# =============================================================================
# Authorization Failures
# =============================================================================

class ProducerNotAuthorizedError(StreamError, PermissionError):
    """Producer not authorized for stream."""
    
    def __init__(
        self,
        producer_id: ProducerId,
        stream_id: StreamId,
        required_scope: Optional[str] = None
    ):
        self.producer_id = producer_id
        self.stream_id = stream_id
        self.required_scope = required_scope
        super().__init__(
            f"Producer {producer_id.value} not authorized for {stream_id.value}"
            + (f" (scope: {required_scope})" if required_scope else "")
        )


class IdentityForgeAttemptError(StreamError, PermissionError):
    """Detected attempt to forge identity."""
    
    def __init__(
        self,
        forged_identity: str,
        identity_type: str,
        stream_id: Optional[StreamId] = None
    ):
        self.forged_identity = forged_identity
        self.identity_type = identity_type
        self.stream_id = stream_id
        super().__init__(
            f"Identity forgery detected for {identity_type}: {forged_identity}"
            + (f" in {stream_id.value}" if stream_id else "")
        )


# =============================================================================
# Serialization Failures
# =============================================================================

class SerializationError(StreamError):
    """Serialization/deserialization failure."""
    
    def __init__(
        self,
        message: str,
        format_type: Optional[str] = None,
        partial_data: bool = False
    ):
        self.format_type = format_type
        self.partial_data = partial_data
        super().__init__(
            f"Serialization error{f' ({format_type})' if format_type else ''}: {message}"
        )


class DeserializationError(SerializationError):
    """Deserialization failure."""
    
    def __init__(self, message: str, format_type: Optional[str] = None):
        super().__init__(f"Deserialization failed: {message}", format_type)


# =============================================================================
# Integrity Failures
# =============================================================================

class IntegrityCheckFailedError(StreamError):
    """Integrity check (hash verification) failed."""
    
    def __init__(
        self,
        record_id: StreamRecordId,
        expected_hash: str,
        actual_hash: str
    ):
        self.record_id = record_id
        self.expected_hash = expected_hash
        self.actual_hash = actual_hash
        super().__init__(
            f"Integrity check failed for {record_id.value}. "
            f"Expected hash: {expected_hash}, got: {actual_hash}"
        )


class ArtifactUnavailableError(StreamError):
    """Artifact reference cannot be resolved."""
    
    def __init__(self, artifact_reference_id: str, stream_id: Optional[StreamId] = None):
        self.artifact_reference_id = artifact_reference_id
        self.stream_id = stream_id
        super().__init__(
            f"Artifact {artifact_reference_id} unavailable"
            + (f" in {stream_id.value}" if stream_id else "")
        )


# =============================================================================
# Resource Failures
# =============================================================================

class CapacityExceededError(StreamError):
    """Stream capacity exceeded."""
    
    def __init__(
        self,
        stream_id: StreamId,
        resource_name: str,
        limit: int,
        current_usage: int
    ):
        self.stream_id = stream_id
        self.resource_name = resource_name
        self.limit = limit
        self.current_usage = current_usage
        super().__init__(
            f"Capacity exceeded for {stream_id.value}: {resource_name} "
            f"{current_usage}/{limit}"
        )


# =============================================================================
# Infrastructure Failures (Translated from Lower Layers)
# =============================================================================

class InfrastructureFailureError(StreamError):
    """Infrastructure failure (translated from lower layer)."""
    
    def __init__(
        self,
        message: str,
        original_error: Optional[Exception] = None,
        infrastructure_layer: Optional[str] = None
    ):
        self.original_error = original_error
        self.infrastructure_layer = infrastructure_layer
        super().__init__(
            f"Infrastructure failure{f' in {infrastructure_layer}' if infrastructure_layer else ''}: "
            f"{message}"
        )


# =============================================================================
# Contract Failure Container (Integration with Phase 3.7.35)
# =============================================================================

@dataclass(frozen=True)
class StreamContractFailure:
    """
    Structured stream failure for Core-Execution boundary.
    
    This is what gets returned from stream contracts instead of raw exceptions.
    """
    
    code: str
    category: StreamFailureCategory
    message: str
    retryable: bool
    
    # Context information
    stream_id: Optional[StreamId] = None
    generation_id: Optional[StreamGenerationId] = None
    record_id: Optional[StreamRecordId] = None
    commit_id: Optional[StreamCommitId] = None
    producer_id: Optional[ProducerId] = None
    
    # Diagnostics
    correlation_id: Optional[str] = None
    causation_id: Optional[str] = None
    partial_commit_status: bool = False  # Partial success after some records committed
    
    # Retry information
    retry_after_seconds: Optional[float] = None
    max_retries: Optional[int] = None
    
    def to_dict(self) -> dict:
        """Convert failure to dictionary for serialization."""
        return {
            "code": self.code,
            "category": self.category.value if hasattr(self.category, 'value') else str(self.category),
            "message": self.message,
            "retryable": self.retryable,
            "stream_id": self.stream_id.value if self.stream_id else None,
            "generation_id": self.generation_id.value if self.generation_id else None,
            "record_id": self.record_id.value if self.record_id else None,
            "commit_id": self.commit_id.value if self.commit_id else None,
            "producer_id": self.producer_id.value if self.producer_id else None,
            "correlation_id": self.correlation_id,
            "causation_id": self.causation_id,
            "partial_commit_status": self.partial_commit_status,
            "retry_after_seconds": self.retry_after_seconds,
            "max_retries": self.max_retries,
        }
    
    @classmethod
    def from_exception(cls, exc: Exception) -> "StreamContractFailure":
        """Create a StreamContractFailure from an exception."""
        
        # Map common exception types to contract failures
        category_map = {
            InvalidStreamIdError: StreamFailureCategory.INVALID_STREAM_ID,
            InvalidGenerationIdError: StreamFailureCategory.INVALID_GENERATION_ID,
            InvalidRecordIdError: StreamFailureCategory.INVALID_RECORD_ID,
            InvalidSequencePositionError: StreamFailureCategory.INVALID_SEQUENCE_POSITION,
            SequenceConflictError: StreamFailureCategory.SEQUENCE_CONFLICT,
            StreamGenerationClosedError: StreamFailureCategory.GENERATION_CLOSED,
            CommitTimeoutError: StreamFailureCategory.COMMIT_TIMEOUT,
            InvalidRecordError: StreamFailureCategory.INVALID_RECORD,
            DuplicateRecordError: StreamFailureCategory.DUPLICATE_RECORD,
            ProducerNotAuthorizedError: StreamFailureCategory.PRODUCER_NOT_AUTHORIZED,
            SerializationError: StreamFailureCategory.SERIALIZATION_FAILURE,
        }
        
        category = category_map.get(type(exc), StreamFailureCategory.INFRASTRUCTURE_FAILURE)
        
        return cls(
            code=category.value.upper().replace("_", " "),
            category=category,
            message=str(exc),
            retryable=False,  # Most stream failures are not retryable
        )


__all__ = [
    # Categories
    "StreamFailureCategory",
    
    # Base exceptions
    "StreamError",
    "StreamIdentitiesIncompatibleError",
    "StreamPositionValidationError",
    
    # Identity validation
    "InvalidStreamIdError",
    "InvalidGenerationIdError",
    "InvalidRecordIdError",
    "InvalidCommitIdError",
    
    # Sequence and ordering
    "InvalidSequencePositionError",
    "SequenceConflictError",
    "SequenceOverflowError",
    "IncomparableStreamPositionError",
    
    # Generation state
    "StreamGenerationClosedError",
    "GenerationLineageMismatchError",
    
    # Commit failures
    "CommitTimeoutError",
    "CommitCancelledError",
    "CommitPublicationFailedError",
    
    # Validation
    "InvalidRecordError",
    "SchemaMismatchError",
    "ContractVersionMismatchError",
    
    # Duplicate detection
    "DuplicateRecordError",
    "IdempotencyConflictError",
    
    # Authorization
    "ProducerNotAuthorizedError",
    "IdentityForgeAttemptError",
    
    # Serialization
    "SerializationError",
    "DeserializationError",
    
    # Integrity
    "IntegrityCheckFailedError",
    "ArtifactUnavailableError",
    
    # Resource
    "CapacityExceededError",
    
    # Infrastructure
    "InfrastructureFailureError",
    
    # Contract failure container
    "StreamContractFailure",
]