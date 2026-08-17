# Memory Evidence Response Contract
# ==================================

"""
Memory Evidence Response: Result from memory artifact retrieval.

This module defines the canonical response model for returning retained
memories as evidence with metadata about their status and quality.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Tuple, Optional, Any
from enum import Enum, auto
import time
import uuid


# =============================================================================
# RETRIEVAL STATUSES
# =============================================================================


class RetrievalStatus(Enum):
    """
    Status of memory evidence retrieval.
    
    Every retrieval operation shall have one explicit status that indicates
    what quality and completeness to expect from the returned artifacts.
    """
    
    COMPLETE = "complete"           # All requested artifacts retrieved
    PARTIAL = "partial"             # Some artifacts missing or delayed
    EMPTY = "empty"                 # No matching artifacts found
    STALE = "stale"                 # Artifacts may be outdated
    CONFLICTED = "conflicted"       # Conflicting evidence present
    RESTRICTED = "restricted"       # Limited by authorization
    FAILED = "failed"               # Retrieval operation failed
    UNKNOWN = "unknown"             # Status unknown


# =============================================================================
# SUPERSESION STATE - Supersession status for each artifact
# =============================================================================


class SupersessionState(Enum):
    """
    Supersession state of a memory artifact.
    
    Indicates whether an artifact has been superseded by a later revision.
    """
    
    CURRENT = "current"             # This is the current version
    SUPERSEDED = "superseded"       # This was superseded by a newer revision
    PARTIALLY_SUPERSEDED = "partially_superseded"  # Some fields superseded
    HISTORICAL_ONLY = "historical_only"  # Only for historical context


# =============================================================================
# CONFIDENCE BOUNDS - Confidence uncertainty ranges
# =============================================================================


@dataclass(frozen=True)
class ConfidenceBounds:
    """
    Confidence and uncertainty bounds for retrieved evidence.
    
    Each artifact may have different confidence levels depending on:
        - Memory retention quality
        - Retrieval accuracy
        - Source reliability
        - Temporal relevance
    """
    
    retention_confidence: float = 1.0      # How well was this retained?
    retrieval_confidence: float = 1.0      # How accurately was it retrieved?
    source_reliability: float = 1.0        # How reliable is the source?
    resulting_confidence: float = 1.0      # Combined confidence (0.0-1.0)
    
    retention_uncertainty: float = 0.0     # Uncertainty in retention
    retrieval_uncertainty: float = 0.0     # Uncertainty in retrieval
    resulting_uncertainty: float = 0.0     # Combined uncertainty
    
    confidence_basis: str = "combined"      # Why this confidence?
    
    def __post_init__(self):
        """Validate confidence bounds."""
        for field_name in ["retention_confidence", "retrieval_confidence", 
                          "source_reliability", "resulting_confidence"]:
            value = getattr(self, field_name)
            if not 0.0 <= value <= 1.0:
                raise ValueError(f"{field_name} must be 0.0-1.0, got {value}")
    
    @classmethod
    def from_sources(
        cls,
        retention: float,
        retrieval: float,
        source_reliability: float = 1.0,
    ) -> "ConfidenceBounds":
        """
        Create bounds from individual confidence sources.
        
        Combines multiple confidence factors into overall bounds.
        """
        # Combined confidence (geometric mean with weights)
        combined_conf = (retention * retrieval * source_reliability) ** (1/3)
        
        return cls(
            retention_confidence=retention,
            retrieval_confidence=retrieval,
            source_reliability=source_reliability,
            resulting_confidence=combined_conf,
            retention_uncertainty=1.0 - retention,
            retrieval_uncertainty=1.0 - retrieval,
            resulting_uncertainty=1.0 - combined_conf,
        )


# =============================================================================
# EVIDENCE RESPONSE - The canonical evidence response model
# =============================================================================


@dataclass(frozen=True)
class EvidenceResponse:
    """
    Response to a memory evidence retrieval request.
    
    Returns retained memory artifacts along with metadata about their
    status, quality, and relationships.
    
    Fields:
        response_identity:     Unique identifier for this response
        request_reference:     Reference to the originating request
        memory_artifacts:      Retrieved memory artifact IDs
        source_revisions:      Revision info for each artifact
        supersession_states:   Supersession status per artifact
        conflicts:             Explicit conflicts in evidence
        confidence:            Overall confidence bounds
        limitations:           Known limitations of this result
        retrieval_status:      Evidence retrieval status
        provenance:            Response origin tracking
    """
    
    # Identity and request reference (required)
    response_identity: str                  # Unique ID for this response
    request_reference: str                  # Request this responds to
    
    # Memory artifacts (references only, never direct access)
    memory_artifacts: Tuple[str, ...]       # Artifact IDs retrieved
    
    # Revision information per artifact
    source_revisions: Tuple[Dict[str, Any], ...] = field(default_factory=tuple)
    
    # Supersession status
    supersession_states: Tuple[Tuple[str, SupersessionState], ...] = field(
        default_factory=tuple  # (artifact_id, state) pairs
    )
    
    # Quality metrics
    confidence_bounds: ConfidenceBounds = field(default_factory=ConfidenceBounds)
    uncertainty: float = 0.0                # Overall uncertainty (0.0-1.0)
    
    # Error handling
    conflicts: Tuple[Dict[str, Any], ...] = field(default_factory=tuple)  # Conflicts
    contradictions: Tuple[Dict[str, Any], ...] = field(default_factory=tuple)  # Contradictions
    limitations: Tuple[str, ...] = field(default_factory=tuple)  # Known limitations
    
    # Synchronization and diagnostics
    retrieval_status: RetrievalStatus = RetrievalStatus.COMPLETE
    diagnostics: Tuple[str, ...] = field(default_factory=tuple)
    
    # Status (required)
    status: str = "complete"
    
    # Provenance tracking (required)
    provenance: Dict[str, Any] = field(default_factory=dict)
    
    @classmethod
    def success(
        cls,
        request_ref: str,
        memory_artifact_ids: List[str],
        confidence_bounds: Optional[ConfidenceBounds] = None,
        supersession_states: Optional[List[Tuple[str, SupersessionState]]] = None,
    ) -> "EvidenceResponse":
        """Create a successful evidence response."""
        return cls(
            response_identity=f"response:evidence:{uuid.uuid4().hex[:16]}",
            request_reference=request_ref,
            memory_artifacts=tuple(memory_artifact_ids),
            source_revisions=(),
            supersession_states=tuple(supersession_states or []),
            confidence_bounds=confidence_bounds or ConfidenceBounds(),
            status="complete",
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
        confidence_bounds: Optional[ConfidenceBounds] = None,
    ) -> "EvidenceResponse":
        """Create a partial evidence response."""
        return cls(
            response_identity=f"response:evidence:{uuid.uuid4().hex[:16]}",
            request_reference=request_ref,
            memory_artifacts=tuple(memory_artifact_ids),
            source_revisions=(),
            confidence_bounds=confidence_bounds or ConfidenceBounds(resulting_confidence=0.75),
            limitations=limitations,
            status="partial",
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
    ) -> "EvidenceResponse":
        """Create an empty evidence response."""
        return cls(
            response_identity=f"response:evidence:{uuid.uuid4().hex[:16]}",
            request_reference=request_ref,
            memory_artifacts=(),
            source_revisions=(),
            confidence_bounds=ConfidenceBounds(resulting_confidence=0.5),
            status="empty",
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
    ) -> "EvidenceResponse":
        """Create a failed evidence response."""
        return cls(
            response_identity=f"response:evidence:{uuid.uuid4().hex[:16]}",
            request_reference=request_ref,
            memory_artifacts=(),
            source_revisions=(),
            confidence_bounds=ConfidenceBounds(resulting_confidence=0.0),
            status="failed",
            diagnostics=(f"Failure: {failure_message}",),
            provenance={
                "created_at_utc": time.time(),
                "failure_message": failure_message,
            },
        )
    
    @property
    def is_success(self) -> bool:
        """Check if the response indicates successful completion."""
        return self.status in ("complete", "partial")
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert response to dictionary for serialization."""
        return {
            "response_identity": self.response_identity,
            "request_reference": self.request_reference,
            "memory_artifacts": list(self.memory_artifacts),
            "source_revisions": [r if isinstance(r, dict) else r.to_dict() if hasattr(r, 'to_dict') else {} for r in self.source_revisions],
            "supersession_states": [(aid, state.value) for aid, state in self.supersession_states],
            "confidence_bounds": {
                "retention_confidence": self.confidence_bounds.retention_confidence,
                "retrieval_confidence": self.confidence_bounds.retrieval_confidence,
                "source_reliability": self.confidence_bounds.source_reliability,
                "resulting_confidence": self.confidence_bounds.resulting_confidence,
                "retention_uncertainty": self.confidence_bounds.retention_uncertainty,
                "retrieval_uncertainty": self.confidence_bounds.retrieval_uncertainty,
                "resulting_uncertainty": self.confidence_bounds.resulting_uncertainty,
            },
            "uncertainty": self.uncertainty,
            "conflicts": list(self.conflicts),
            "contradictions": list(self.contradictions),
            "limitations": list(self.limitations),
            "retrieval_status": self.retrieval_status.value,
            "diagnostics": list(self.diagnostics),
            "status": self.status,
            "provenance": dict(self.provenance),
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "EvidenceResponse":
        """Create response from dictionary."""
        return cls(
            response_identity=data.get("response_identity", str(id(data))),
            request_reference=data.get("request_reference", ""),
            memory_artifacts=tuple(data.get("memory_artifacts", [])),
            source_revisions=tuple(data.get("source_revisions", [])),
            supersession_states=tuple(
                (item[0], SupersessionState(item[1])) if isinstance(item, tuple) 
                else ("unknown", SupersessionState.CURRENT)
                for item in data.get("supersession_states", [])
            ),
            confidence_bounds=ConfidenceBounds(
                retention_confidence=float(data.get("confidence_bounds", {}).get("retention_confidence", 1.0)),
                retrieval_confidence=float(data.get("confidence_bounds", {}).get("retrieval_confidence", 1.0)),
                source_reliability=float(data.get("confidence_bounds", {}).get("source_reliability", 1.0)),
            ),
            uncertainty=float(data.get("uncertainty", 0.0)),
            conflicts=tuple(data.get("conflicts", [])),
            contradictions=tuple(data.get("contradictions", [])),
            limitations=tuple(data.get("limitations", [])),
            retrieval_status=RetrievalStatus(data.get("retrieval_status", "complete")),
            diagnostics=tuple(data.get("diagnostics", [])),
            status=data.get("status", "complete"),
            provenance=dict(data.get("provenance", {})),
        )


__all__ = [
    "RetrievalStatus",
    "SupersessionState",
    "ConfidenceBounds",
    "EvidenceResponse",
]