# Memory-Perception Cross-System Response
# ========================================

"""
Memory-Perception Response: Result from cross-system integration operations.

Every request produces an immutable response that preserves the result, quality
metrics, and provenance information.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Tuple, Optional, Any
from enum import Enum, auto
import time
import uuid


# =============================================================================
# RESPONSE STATUSES
# =============================================================================


class ResponseStatus(Enum):
    """
    Status of a cross-system response.
    
    Every response shall have one explicit status that indicates whether the
    operation completed successfully and what quality to expect.
    """
    
    COMPLETE = "complete"                 # Full result available
    PARTIAL = "partial"                   # Partial result, some data unavailable
    AMBIGUOUS = "ambiguous"               # Multiple plausible interpretations
    CONFLICTED = "conflicted"             # Conflicting evidence present
    DEFERRED = "deferred"                 # Operation deferred to later
    EMPTY = "empty"                       # No matching results found
    RESTRICTED = "restricted"             # Results restricted by authorization
    REJECTED = "rejected"                 # Request rejected
    FAILED = "failed"                     # Operation failed
    UNKNOWN = "unknown"                   # Status unknown


# =============================================================================
# RESULT KINDS - What kind of result is returned?
# =============================================================================


class ResultKind(Enum):
    """
    Kinds of results that can be returned from integration.
    """
    
    # Admission results
    MEMORY_CANDIDATE = "memory_candidate"     # Prepared for Memory admission
    
    # Recognition and recollection results
    RECOGNITION_CANDIDATES = "recognition_candidates"  # Similar memories found
    RECOLLECTION_CONTEXT = "recollection_context"      # Contextual memories
    
    # Contextualization results
    CONTEXTUALIZED_VIEW = "contextualized_view"       # Perception + context
    
    # Expectation and mismatch results
    EXPECTATION = "expectation"             # Generated expectation
    MISMATCH_REPORT = "mismatch_report"     # Mismatch classification
    
    # Continuity and correspondence results
    CONTINUITY_CANDIDATE = "continuity_candidate"  # Entity continuity
    TEMPORAL_CORRESPONDENCE = "temporal_correspondence"  # Time alignment
    SPATIAL_CORRESPONDENCE = "spatial_correspondence"  # Space alignment
    
    # Identity results
    IDENTITY_CANDIDATE = "identity_candidate"         # Identity match candidate
    
    # Governance results
    PROVENANCE_TRACE = "provenance_trace"       # Traced provenance chain
    VALIDATION_RESULT = "validation_result"     # Validation outcome
    HEALTH_REPORT = "health_report"             # Integration health status


# =============================================================================
# CROSS-SYSTEM RESPONSE - The canonical response model
# =============================================================================


@dataclass(frozen=True)
class MemoryPerceptionResponse:
    """
    Response from cross-system Memory-Perception integration.
    
    Every request produces one immutable response. Responses are never modified
    after publication - new responses are created for revised results.
    
    Fields:
        response_identity:     Unique identifier for this response
        request_reference:     Reference to the originating request
        result_kind:           What kind of result is returned?
        payload:               The actual result data
        source_roles:          Source roles preserved through processing
        confidence:            Overall confidence (0.0-1.0)
        uncertainty:           Overall uncertainty (0.0-1.0)
        conflicts:             Explicit conflicts in the result
        alternatives:          Alternative interpretations considered
        limitations:           Known limitations of this result
        synchronization_state: Synchronization metadata
        diagnostics:           Diagnostic information
        status:                Result completion status
        provenance:            Response origin tracking
    """
    
    # Identity and request reference (required)
    response_identity: str                  # Unique ID for this response
    request_reference: str                  # Request this responds to
    
    # Result details
    result_kind: ResultKind                 # What kind of result?
    payload: Dict[str, Any]                 # The actual result data
    
    # Source roles preserved through processing (required)
    source_roles: Tuple[Dict[str, Any], ...]  # SourceRoleMetadata dicts
    
    # Quality metrics
    confidence: float = 1.0                 # Overall confidence (0.0-1.0)
    uncertainty: float = 0.0                # Overall uncertainty (0.0-1.0)
    
    # Error handling
    conflicts: Tuple[Dict[str, Any], ...] = field(default_factory=tuple)  # Conflict records
    alternatives: Tuple[Dict[str, Any], ...] = field(default_factory=tuple)  # Alternatives considered
    limitations: Tuple[str, ...] = field(default_factory=tuple)  # Known limitations
    
    # Synchronization and diagnostics
    synchronization_state: Dict[str, Any] = field(default_factory=dict)
    diagnostics: Tuple[str, ...] = field(default_factory=tuple)
    
    # Status (required)
    status: ResponseStatus = ResponseStatus.COMPLETE
    
    # Provenance tracking (required)
    provenance: Dict[str, Any] = field(default_factory=dict)
    
    @classmethod
    def success(
        cls,
        request_ref: str,
        result_kind: ResultKind,
        payload: Dict[str, Any],
        confidence: float = 1.0,
        uncertainty: float = 0.0,
    ) -> "MemoryPerceptionResponse":
        """Create a successful response."""
        return cls(
            response_identity=f"response:{uuid.uuid4().hex[:16]}",
            request_reference=request_ref,
            result_kind=result_kind,
            payload=payload,
            source_roles=(),
            confidence=confidence,
            uncertainty=uncertainty,
            status=ResponseStatus.COMPLETE,
            provenance={
                "created_at_utc": time.time(),
            },
        )
    
    @classmethod
    def partial(
        cls,
        request_ref: str,
        result_kind: ResultKind,
        payload: Dict[str, Any],
        limitations: Tuple[str, ...] = (),
        confidence: float = 0.75,
    ) -> "MemoryPerceptionResponse":
        """Create a partial response with known limitations."""
        return cls(
            response_identity=f"response:{uuid.uuid4().hex[:16]}",
            request_reference=request_ref,
            result_kind=result_kind,
            payload=payload,
            source_roles=(),
            confidence=confidence,
            uncertainty=1.0 - confidence,
            limitations=limitations,
            status=ResponseStatus.PARTIAL,
            provenance={
                "created_at_utc": time.time(),
                "partial_reasons": list(limitations),
            },
        )
    
    @classmethod
    def empty(
        cls,
        request_ref: str,
        result_kind: ResultKind,
        reason: str = "no_matching_evidence",
    ) -> "MemoryPerceptionResponse":
        """Create an empty response."""
        return cls(
            response_identity=f"response:{uuid.uuid4().hex[:16]}",
            request_reference=request_ref,
            result_kind=result_kind,
            payload={},
            source_roles=(),
            confidence=0.5,  # No evidence = low confidence
            uncertainty=0.5,
            status=ResponseStatus.EMPTY,
            diagnostics=(f"Empty result: {reason}",),
            provenance={
                "created_at_utc": time.time(),
                "empty_reason": reason,
            },
        )
    
    @classmethod
    def rejected(
        cls,
        request_ref: str,
        rejection_reason: str,
    ) -> "MemoryPerceptionResponse":
        """Create a rejected response."""
        return cls(
            response_identity=f"response:{uuid.uuid4().hex[:16]}",
            request_reference=request_ref,
            result_kind=ResultKind.MEMORY_CANDIDATE,  # Default kind
            payload={},
            source_roles=(),
            confidence=0.0,
            uncertainty=1.0,
            status=ResponseStatus.REJECTED,
            diagnostics=(f"Rejected: {rejection_reason}",),
            provenance={
                "created_at_utc": time.time(),
                "rejection_reason": rejection_reason,
            },
        )
    
    @classmethod
    def failed(
        cls,
        request_ref: str,
        failure_message: str,
    ) -> "MemoryPerceptionResponse":
        """Create a failed response."""
        return cls(
            response_identity=f"response:{uuid.uuid4().hex[:16]}",
            request_reference=request_ref,
            result_kind=ResultKind.MEMORY_CANDIDATE,  # Default kind
            payload={},
            source_roles=(),
            confidence=0.0,
            uncertainty=1.0,
            status=ResponseStatus.FAILED,
            diagnostics=(f"Failure: {failure_message}",),
            provenance={
                "created_at_utc": time.time(),
                "failure_message": failure_message,
            },
        )
    
    @property
    def is_success(self) -> bool:
        """Check if the response indicates successful completion."""
        return self.status in (ResponseStatus.COMPLETE, ResponseStatus.PARTIAL)
    
    @property
    def has_conflicts(self) -> bool:
        """Check if conflicts are present."""
        return len(self.conflicts) > 0
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert response to dictionary for serialization."""
        return {
            "response_identity": self.response_identity,
            "request_reference": self.request_reference,
            "result_kind": self.result_kind.value,
            "payload": dict(self.payload),
            "source_roles": [sr if isinstance(sr, dict) else sr.to_dict() if hasattr(sr, 'to_dict') else {} for sr in self.source_roles],
            "confidence": self.confidence,
            "uncertainty": self.uncertainty,
            "conflicts": list(self.conflicts),
            "alternatives": list(self.alternatives),
            "limitations": list(self.limitations),
            "synchronization_state": dict(self.synchronization_state),
            "diagnostics": list(self.diagnostics),
            "status": self.status.value,
            "provenance": dict(self.provenance),
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "MemoryPerceptionResponse":
        """Create response from dictionary."""
        return cls(
            response_identity=data.get("response_identity", str(id(data))),
            request_reference=data.get("request_reference", ""),
            result_kind=ResultKind(data.get("result_kind", "memory_candidate")),
            payload=dict(data.get("payload", {})),
            source_roles=tuple(data.get("source_roles", [])),
            confidence=float(data.get("confidence", 1.0)),
            uncertainty=float(data.get("uncertainty", 0.0)),
            conflicts=tuple(data.get("conflicts", [])),
            alternatives=tuple(data.get("alternatives", [])),
            limitations=tuple(data.get("limitations", [])),
            synchronization_state=dict(data.get("synchronization_state", {})),
            diagnostics=tuple(data.get("diagnostics", [])),
            status=ResponseStatus(data.get("status", "complete")),
            provenance=dict(data.get("provenance", {})),
        )


# =============================================================================
# CONFLICT RECORD - Explicit conflict in integration results
# =============================================================================


@dataclass(frozen=True)
class IntegrationConflict:
    """
    A conflict between different sources of information.
    
    Every material conflict shall become an explicit conflict record with
    the conflicting evidence preserved.
    """
    
    # Identity
    conflict_identity: str                  # Unique ID for this conflict
    
    # Source information
    source_artifact_ids: Tuple[str, ...]    # IDs of artifacts in conflict
    
    # Conflict details
    conflict_kind: str                      # "perception_memory", "recognition", etc.
    
    conflicting_fields: Tuple[str, ...]     # Which fields differ?
    
    # Context
    temporal_context: Dict[str, Any]        # Time context of conflict
    spatial_context: Dict[str, Any]         # Space context of conflict
    
    # Source roles at time of conflict
    source_roles: Tuple[Dict[str, Any], ...]
    
    # Quality metrics
    confidence: float = 0.5                 # Confidence in the conflict report
    uncertainty: float = 0.2                # Uncertainty about resolution
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "conflict_identity": self.conflict_identity,
            "source_artifact_ids": list(self.source_artifact_ids),
            "conflict_kind": self.conflict_kind,
            "conflicting_fields": list(self.conflicting_fields),
            "temporal_context": dict(self.temporal_context),
            "spatial_context": dict(self.spatial_context),
            "source_roles": [sr.to_dict() if hasattr(sr, 'to_dict') else sr for sr in self.source_roles],
            "confidence": self.confidence,
            "uncertainty": self.uncertainty,
        }


__all__ = [
    "ResponseStatus",
    "ResultKind",
    "MemoryPerceptionResponse",
    "IntegrationConflict",
]