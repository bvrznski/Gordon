# Integration Response - Phase 5.1.7 Canonical Response Interface
# ================================================================

"""
Memory Integration Response: Response format for subsystem communication.

Every response from Memory includes:
    - projection (the visible artifacts after filtering)
    - limitations (constraints that were applied)
    - diagnostics (execution details)
    - confidence (certainty about results)
    - provenance (how results were derived)

Response Laws:
    RESPONSE-LAW-001: Every response contains a projection
    RESPONSE-LAW-002: Responses never expose implementation internals
    RESPONSE-RULE-003: Limitations are explicit
    RESPONSE-RULE-004: Confidence levels are reported
    RESPONSE-RULE-005: Provenance is preserved
    RESPONSE-RULE-006: Responses are immutable after publication
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Tuple, Optional, Any
from enum import Enum, auto
import time
import uuid


# =============================================================================
# PROJECTION TYPES - What kind of projection?
# =============================================================================


class ProjectionType(Enum):
    """
    Types of projections that can be returned.
    
    | Type         | Description                                        |
    |--------------|----------------------------------------------------|
    | FULL         | Complete artifact data with all fields             |
    | SUMMARY      | Summary statistics only                            |
    | IDENTIFIERS  | Artifact IDs only                                  |
    | METADATA     | Metadata and provenance only                       |
    | RELATIONSHIP | Relationships between artifacts                    |
    | CONTEXT      | Context bundle for working memory                  |
    | EVIDENCE     | Supporting evidence for reasoning                  |
    """
    
    FULL = "full"
    SUMMARY = "summary"
    IDENTIFIERS = "identifiers"
    METADATA = "metadata"
    RELATIONSHIP = "relationship"
    CONTEXT = "context"
    EVIDENCE = "evidence"


# =============================================================================
# RESPONSE OUTCOMES
# =============================================================================


class ResponseOutcome(Enum):
    """
    Result of a response processing.
    
    | Outcome      | Description                                        |
    |--------------|----------------------------------------------------|
    | SUCCESS      | Request completed successfully                     |
    | PARTIAL      | Partial results returned                           |
    | NOT_FOUND    | No matching artifacts found                        |
    | UNAUTHORIZED | Access not authorized                              |
    | INVALID      | Request was invalid                                |
    | TIMEOUT      | Processing timed out                               |
    """
    
    SUCCESS = "success"
    PARTIAL = "partial"
    NOT_FOUND = "not_found"
    UNAUTHORIZED = "unauthorized"
    INVALID = "invalid"
    TIMEOUT = "timeout"


# =============================================================================
# PROVENANCE RECORD
# =============================================================================


@dataclass(frozen=True)
class ProvenanceRecord:
    """
    Record of how a response was generated.
    
    Fields:
        source:           Source of the information
        method:         How was it derived?
        timestamp_utc:  When was it generated?
        
        # Lineage
        parent_ids:     IDs of artifacts this depends on
        derivation_path: How was this reached?
    """
    
    source: str                             # Where did this come from?
    method: str = "direct"                  # How was it derived?
    timestamp_utc: float = field(default_factory=time.time)
    
    parent_ids: Tuple[str, ...] = field(default_factory=tuple)
    derivation_path: Tuple[str, ...] = field(default_factory=tuple)


# =============================================================================
# LIMITATION RECORD
# =============================================================================


@dataclass(frozen=True)
class ResponseLimitation:
    """
    Record of limitations applied to a response.
    
    Fields:
        limitation_type:  What kind of limitation?
        value:          What was the limit value?
        reason:         Why was this limitation applied?
        
        # Scope
        artifact_count: How many artifacts were affected?
    """
    
    limitation_type: str                    # e.g., "limit", "filter", "visibility"
    value: Any                              # The limit value
    reason: str = ""                        # Explanation
    
    artifact_count: int = 0


# =============================================================================
# INTEGRATION RESPONSE
# =============================================================================


@dataclass(frozen=True)
class MemoryIntegrationResponse:
    """
    Complete integration response from Memory.
    
    Every response contains projections only - never the implementation.
    
    Fields:
        response_id:         Unique identifier for this response
        
        # Request correlation
        request_id:          ID of the request this responds to
        requester:           Who made the request?
        
        # Content
        outcome:             Was the request successful?
        projection_type:     What kind of projection is returned?
        projection_data:     The actual projection data
        
        # Metadata
        count:               Number of items in projection
        limitations:         Any constraints that were applied
        total_count:         Total matches before filtering
        
        # Quality
        confidence:          Belief in correctness (0.0-1.0)
        
        # Diagnostics
        latency_ms:          How long did processing take?
        warnings:            Non-critical issues encountered
        diagnostics:         Detailed diagnostic information
        
        # Provenance
        generated_at_utc:    When was this response generated?
        provenance:          How was this derived?
    """
    
    response_id: str                        # Unique identifier
    
    # Request correlation
    request_id: str                         # ID of original request
    requester: str                          # Consumer subsystem name
    
    # Content
    outcome: ResponseOutcome = ResponseOutcome.SUCCESS
    projection_type: ProjectionType = ProjectionType.FULL
    projection_data: Dict[str, Any]
    
    # Metadata
    count: int = 0
    limitations: Tuple[ResponseLimitation, ...] = field(default_factory=tuple)
    total_count: int = 0
    
    # Quality
    confidence: float = 1.0
    
    # Diagnostics
    latency_ms: float = 0.0
    warnings: Tuple[str, ...] = field(default_factory=tuple)
    diagnostics: Dict[str, Any] = field(default_factory=dict)
    
    # Provenance
    generated_at_utc: float = field(default_factory=time.time)
    provenance: Tuple[ProvenanceRecord, ...] = field(default_factory=tuple)
    
    def has_limitations(self) -> bool:
        """Check if any limitations were applied."""
        return len(self.limitations) > 0
    
    def is_complete(self) -> bool:
        """Check if all results were returned (no truncation)."""
        return self.count >= self.total_count or self.total_count == 0


def create_response(
    request_id: str,
    requester: str,
    projection_data: Dict[str, Any],
    projection_type: ProjectionType = ProjectionType.FULL,
    outcome: ResponseOutcome = ResponseOutcome.SUCCESS
) -> MemoryIntegrationResponse:
    """
    Create a new integration response.
    
    Args:
        request_id:      ID of the original request
        requester:       Who made the request?
        projection_data: The projection payload
        projection_type: Type of projection
        outcome:         Response outcome
        
    Returns:
        A new MemoryIntegrationResponse with generated IDs.
    """
    return MemoryIntegrationResponse(
        response_id=str(uuid.uuid4()),
        request_id=request_id,
        requester=requester,
        projection_data=projection_data,
        projection_type=projection_type,
        outcome=outcome,
        count=len(projection_data) if isinstance(projection_data, (dict, list)) else 0
    )


# =============================================================================
# PROJECTION BUILDER
# =============================================================================


class ProjectionBuilder:
    """
    Builder for constructing projections.
    
    Ensures that projections are built correctly and validated
    before publication.
    
    Usage:
        builder = ProjectionBuilder()
        builder.add_artifact("id1", data1)
        builder.add_artifact("id2", data2)
        projection = builder.build()
    """
    
    def __init__(self, projection_type: ProjectionType = ProjectionType.FULL):
        self.projection_type = projection_type
        self._artifacts: Dict[str, Dict[str, Any]] = {}
        self._metadata: Dict[str, Any] = {}
        self._limitations: List[ResponseLimitation] = []
        self._warnings: List[str] = []
    
    def add_artifact(self, artifact_id: str, data: Dict[str, Any]) -> ProjectionBuilder:
        """Add an artifact to the projection."""
        self._artifacts[artifact_id] = data
        return self
    
    def add_metadata(self, key: str, value: Any) -> ProjectionBuilder:
        """Add metadata to the projection."""
        self._metadata[key] = value
        return self
    
    def add_limitation(self, limitation: ResponseLimitation) -> ProjectionBuilder:
        """Record a limitation that was applied."""
        self._limitations.append(limitation)
        return self
    
    def add_warning(self, warning: str) -> ProjectionBuilder:
        """Add a warning message."""
        self._warnings.append(warning)
        return self
    
    def set_total_count(self, count: int) -> ProjectionBuilder:
        """Set the total count before filtering."""
        self._metadata["total_count"] = count
        return self
    
    def build(self) -> MemoryIntegrationResponse:
        """Build and return the final projection."""
        data: Dict[str, Any] = {"artifacts": self._artifacts}
        
        if self._metadata:
            data["metadata"] = self._metadata
        
        if self.projection_type == ProjectionType.IDENTIFIERS:
            data = list(self._artifacts.keys())
        elif self.projection_type == ProjectionType.SUMMARY:
            data = {
                "count": len(self._artifacts),
                "total": self._metadata.get("total_count", len(self._artifacts))
            }
        
        response = create_response(
            request_id=self._metadata.get("request_id", ""),
            requester=self._metadata.get("requester", "unknown"),
            projection_data=data,
            projection_type=self.projection_type
        )
        
        return dataclass_replace(response, 
                                 limitations=tuple(self._limitations),
                                 warnings=tuple(self._warnings))


def dataclass_replace(instance: Any, **kwargs) -> Any:
    """Replacement for dataclasses.replace (Python 3.7 compatible)."""
    fields = instance.__dataclass_fields__
    return type(instance)(
        **{f.name: kwargs.get(f.name, getattr(instance, f.name)) 
           for f in fields.values()}
     )
