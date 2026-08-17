# Knowledge-Memory Cross-System Response
# =======================================

"""
Knowledge-Memory Response: Result from cross-system integration operations.

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
    DEGRADED = "degraded"                 # Result available but with known limitations
    AMBIGUOUS = "ambiguous"               # Multiple plausible interpretations
    CONFLICTED = "conflicted"             # Conflicting evidence present
    EMPTY = "empty"                       # No matching results found
    DEFERRED = "deferred"                 # Operation deferred to later
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
    
    # Evidence retrieval results
    MEMORY_EVIDENCE = "memory_evidence"           # Retrieved memory artifacts
    
    # Extraction results
    SEMANTIC_CANDIDATES = "semantic_candidates"   # Extracted semantic candidates
    
    # Grounding results
    GROUNDING_ASSESSMENT = "grounding_assessment"  # Grounding evaluation
    
    # Persistence results
    PERSISTENCE_RESPONSE = "persistence_response"   # Memory admission result
    
    # Reconstruction results
    RECONSTRUCTION_CANDIDATE = "reconstruction_candidate"  # Reconstructed Knowledge
    
    # Revision results
    REVISION_RESPONSE = "revision_response"         # Revision persistence result
    
    # Supersession results
    SUPERSESSION_RECORD = "supersession_record"     # Superseding revision record
    
    # Merge/Split results
    CONCEPT_MERGE_RESULT = "concept_merge_result"   # Concept merge result
    CONCEPT_SPLIT_RESULT = "concept_split_result"   # Concept split result
    
    # Consolidation results
    CONSOLIDATION_RESULT = "consolidation_result"   # Semantic consolidation result
    
    # Contradiction results
    CONTRADICTION_RECORD = "contradiction_record"   # Contradiction detection result
    
    # Synchronization results
    SYNCHRONIZATION_STATE = "synchronization_state"  # Synchronization metadata
    
    # Governance results
    REVALIDATION_RESULT = "revalidation_result"     # Revalidation outcome
    HEALTH_REPORT = "health_report"                 # Integration health status


# =============================================================================
# EVIDENCE RETRIEVAL RESPONSE - Memory Evidence Response
# =============================================================================


@dataclass(frozen=True)
class KnowledgeMemoryEvidenceResponse:
    """
    Response to a memory evidence retrieval request.
    
    Fields:
        response_identity:     Unique identifier for this response
        request_reference:     Reference to the originating request
        memory_artifacts:      Retrieved memory artifacts (references only)
        source_roles:          Source roles preserved through processing
        supersession_states:   Supersession information for each artifact
        conflicts:             Explicit conflicts in evidence
        confidence:            Overall confidence (0.0-1.0)
        uncertainty:           Overall uncertainty (0.0-1.0)
        limitations:           Known limitations of this result
        retrieval_status:      Evidence retrieval status
        provenance:            Response origin tracking
    """
    
    # Identity and request reference (required)
    response_identity: str                  # Unique ID for this response
    request_reference: str                  # Request this responds to
    
    # Memory artifacts (references only, never direct access)
    memory_artifacts: Tuple[str, ...]       # Artifact IDs retrieved
    
    # Source roles preserved through processing (required)
    source_roles: Tuple[Dict[str, Any], ...]  # SourceRoleMetadata dicts
    
    # Quality metrics
    confidence: float = 1.0                 # Overall confidence (0.0-1.0)
    uncertainty: float = 0.0                # Overall uncertainty (0.0-1.0)
    
    # Error handling
    conflicts: Tuple[Dict[str, Any], ...] = field(default_factory=tuple)  # Conflict records
    limitations: Tuple[str, ...] = field(default_factory=tuple)  # Known limitations
    
    # Synchronization and diagnostics
    supersession_states: Tuple[Dict[str, Any], ...] = field(default_factory=tuple)
    retrieval_status: str = "complete"
    
    # Status (required)
    status: ResponseStatus = ResponseStatus.COMPLETE
    
    # Provenance tracking (required)
    provenance: Dict[str, Any] = field(default_factory=dict)
    
    @classmethod
    def success(
        cls,
        request_ref: str,
        memory_artifact_ids: List[str],
        confidence: float = 1.0,
        uncertainty: float = 0.0,
    ) -> "KnowledgeMemoryEvidenceResponse":
        """Create a successful evidence response."""
        return cls(
            response_identity=f"response:evidence:{uuid.uuid4().hex[:16]}",
            request_reference=request_ref,
            memory_artifacts=tuple(memory_artifact_ids),
            source_roles=(),
            confidence=confidence,
            uncertainty=uncertainty,
            status=ResponseStatus.COMPLETE,
            provenance={
                "created_at_utc": time.time(),
                "artifact_count": len(memory_artifact_ids),
            },
        )
    
    @classmethod
    def partial(
        cls,
        request_ref: str,
        memory_artifact_ids: List[str],
        limitations: Tuple[str, ...] = (),
        confidence: float = 0.75,
    ) -> "KnowledgeMemoryEvidenceResponse":
        """Create a partial evidence response."""
        return cls(
            response_identity=f"response:evidence:{uuid.uuid4().hex[:16]}",
            request_reference=request_ref,
            memory_artifacts=tuple(memory_artifact_ids),
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
        reason: str = "no_matching_evidence",
    ) -> "KnowledgeMemoryEvidenceResponse":
        """Create an empty evidence response."""
        return cls(
            response_identity=f"response:evidence:{uuid.uuid4().hex[:16]}",
            request_reference=request_ref,
            memory_artifacts=(),
            source_roles=(),
            confidence=0.5,
            uncertainty=0.5,
            status=ResponseStatus.EMPTY,
            provenance={
                "created_at_utc": time.time(),
                "empty_reason": reason,
            },
        )
    
    @classmethod
    def failed(
        cls,
        request_ref: str,
        failure_message: str,
    ) -> "KnowledgeMemoryEvidenceResponse":
        """Create a failed evidence response."""
        return cls(
            response_identity=f"response:evidence:{uuid.uuid4().hex[:16]}",
            request_reference=request_ref,
            memory_artifacts=(),
            source_roles=(),
            confidence=0.0,
            uncertainty=1.0,
            status=ResponseStatus.FAILED,
            provenance={
                "created_at_utc": time.time(),
                "failure_message": failure_message,
            },
        )
    
    @property
    def is_success(self) -> bool:
        """Check if the response indicates successful completion."""
        return self.status in (ResponseStatus.COMPLETE, ResponseStatus.PARTIAL)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert response to dictionary for serialization."""
        return {
            "response_identity": self.response_identity,
            "request_reference": self.request_reference,
            "memory_artifacts": list(self.memory_artifacts),
            "source_roles": [sr if isinstance(sr, dict) else sr.to_dict() if hasattr(sr, 'to_dict') else {} for sr in self.source_roles],
            "confidence": self.confidence,
            "uncertainty": self.uncertainty,
            "conflicts": list(self.conflicts),
            "limitations": list(self.limitations),
            "supersession_states": [s if isinstance(s, dict) else s.to_dict() if hasattr(s, 'to_dict') else {} for s in self.supersession_states],
            "retrieval_status": self.retrieval_status,
            "status": self.status.value,
            "provenance": dict(self.provenance),
        }


# =============================================================================
# INTEGRATION RESPONSE - The canonical response model
# =============================================================================


@dataclass(frozen=True)
class KnowledgeMemoryResponse:
    """
    Response from cross-system Knowledge-Memory integration.
    
    Every request produces one immutable response. Responses are never modified
    after publication - new responses are created for revised results.
    
    Fields:
        response_identity:     Unique identifier for this response
        request_reference:     Reference to the originating request
        result_kind:           What kind of result is returned?
        payload:               The actual result data
        source_roles:          Source roles preserved through processing
        knowledge_revisions:   Knowledge revision metadata
        memory_revisions:      Memory revision metadata
        confidence:            Overall confidence (0.0-1.0)
        uncertainty:           Overall uncertainty (0.0-1.0)
        contradictions:        Explicit conflicts in the result
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
    contradictions: Tuple[Dict[str, Any], ...] = field(default_factory=tuple)  # Contradiction records
    limitations: Tuple[str, ...] = field(default_factory=tuple)  # Known limitations
    
    # Synchronization and diagnostics
    knowledge_revisions: Tuple[Dict[str, Any], ...] = field(default_factory=tuple)
    memory_revisions: Tuple[Dict[str, Any], ...] = field(default_factory=tuple)
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
    ) -> "KnowledgeMemoryResponse":
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
    ) -> "KnowledgeMemoryResponse":
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
    ) -> "KnowledgeMemoryResponse":
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
    ) -> "KnowledgeMemoryResponse":
        """Create a rejected response."""
        return cls(
            response_identity=f"response:{uuid.uuid4().hex[:16]}",
            request_reference=request_ref,
            result_kind=ResultKind.MEMORY_EVIDENCE,  # Default kind
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
    ) -> "KnowledgeMemoryResponse":
        """Create a failed response."""
        return cls(
            response_identity=f"response:{uuid.uuid4().hex[:16]}",
            request_reference=request_ref,
            result_kind=ResultKind.MEMORY_EVIDENCE,  # Default kind
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
        """Check if contradictions are present."""
        return len(self.contradictions) > 0
    
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
            "contradictions": list(self.contradictions),
            "limitations": list(self.limitations),
            "knowledge_revisions": [r if isinstance(r, dict) else r.to_dict() if hasattr(r, 'to_dict') else {} for r in self.knowledge_revisions],
            "memory_revisions": [r if isinstance(r, dict) else r.to_dict() if hasattr(r, 'to_dict') else {} for r in self.memory_revisions],
            "synchronization_state": dict(self.synchronization_state),
            "diagnostics": list(self.diagnostics),
            "status": self.status.value,
            "provenance": dict(self.provenance),
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "KnowledgeMemoryResponse":
        """Create response from dictionary."""
        return cls(
            response_identity=data.get("response_identity", str(id(data))),
            request_reference=data.get("request_reference", ""),
            result_kind=ResultKind(data.get("result_kind", "memory_evidence")),
            payload=dict(data.get("payload", {})),
            source_roles=tuple(data.get("source_roles", [])),
            confidence=float(data.get("confidence", 1.0)),
            uncertainty=float(data.get("uncertainty", 0.0)),
            contradictions=tuple(data.get("contradictions", [])),
            limitations=tuple(data.get("limitations", [])),
            knowledge_revisions=tuple(data.get("knowledge_revisions", [])),
            memory_revisions=tuple(data.get("memory_revisions", [])),
            synchronization_state=dict(data.get("synchronization_state", {})),
            diagnostics=tuple(data.get("diagnostics", [])),
            status=ResponseStatus(data.get("status", "complete")),
            provenance=dict(data.get("provenance", {})),
        )


__all__ = [
    "ResponseStatus",
    "ResultKind",
    "KnowledgeMemoryEvidenceResponse",
    "KnowledgeMemoryResponse",
]