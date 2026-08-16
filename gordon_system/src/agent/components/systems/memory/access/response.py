# Memory Access Response - Phase 5.1.3 Canonical Access Result
# =============================================================

"""
Memory Access Response: Result of a memory access operation.

Every response contains:
    - projection (the visible artifacts after filtering)
    - visibility metadata (what was filtered and why)
    - confidence (certainty about results)
    - limitations (constraints that were applied)
    - diagnostics (execution details)

Response Laws:
    RESPONSE-LAW-001: Every response includes a projection
    RESPONSE-LAW-002: Responses never expose implementation internals
    RESPONSE-RULE-003: Visibility metadata is explicit
    RESPONSE-RULE-004: Confidence levels are reported
    RESPONSE-RULE-005: Limitations are documented
    RESPONSE-RULE-006: Diagnostics are available for debugging
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Tuple, Optional, Any, Union
from enum import Enum, auto
import time


# =============================================================================
# AUTHORIZATION OUTCOME - Was access granted?
# =============================================================================


class AuthorizationOutcome(Enum):
    """
    Result of authorization evaluation.
    
    | Outcome  | Description                                  |
    |----------|---------------------------------------------|
    | ALLOW    | Access fully authorized                      |
    | DENY     | Access denied completely                     |
    | LIMIT    | Access granted with limitations              |
    | UNKNOWN  | Authorization could not be determined        |
    """
    
    ALLOW = "allow"
    DENY = "deny"
    LIMIT = "limit"
    UNKNOWN = "unknown"


# =============================================================================
# ACCESS RESPONSE - Result of access request
# =============================================================================


@dataclass(frozen=True)
class MemoryAccessResponse:
    """
    Result of processing a memory access request.
    
    Fields:
        response_id:         Unique identifier for this response
        
        # Authorization result
        outcome:             Was access granted? (allow, deny, limit)
        authorization_notes: Explanation of decision
        
        # Projection - the visible content
        projection:          Tuple of visible artifacts
        total_count:         Total matches before visibility filtering
        filtered_count:      How many were hidden by visibility?
        
        # Metadata
        confidence:          Belief in result correctness (0.0-1.0)
        limitations:         Constraints that affected results
        
        # Diagnostics
        execution_time_ms:   How long did processing take?
        warnings:            Non-critical issues encountered
        diagnostics:         Detailed diagnostic information
        
        # Projection details
        projection_type:     What kind of projection was generated?
        timestamp_utc:       When was response generated?
        
        # Provenance
        generated_by:        Who/what processed this request?
    """
    
    # Core identity (required)
    response_id: str
    
    # Authorization result
    outcome: AuthorizationOutcome = AuthorizationOutcome.ALLOW
    authorization_notes: Optional[str] = None
    
    # Projection - the visible content
    projection: Tuple[Any, ...] = field(default_factory=tuple)  # MemoryArtifact or projections
    total_count: int = 0                # Total matches before visibility
    filtered_count: int = 0             # Hidden by visibility filters
    
    # Metadata
    confidence: float = 1.0             # 0.0-1.0 certainty
    limitations: Tuple[str, ...] = field(default_factory=tuple)  # Applied constraints
    
    # Diagnostics
    execution_time_ms: float = 0.0      # Processing time in ms
    warnings: Tuple[str, ...] = field(default_factory=tuple)
    diagnostics: Dict[str, Any] = field(default_factory=dict)
    
    # Projection details
    projection_type: str = "unknown"
    timestamp_utc: float = field(default_factory=time.time)
    
    # Provenance
    generated_by: Optional[str] = None  # Who processed this?
    
    @property
    def is_empty(self) -> bool:
        """Check if the response contains no visible artifacts."""
        return len(self.projection) == 0
    
    @property
    def has_artifacts(self) -> bool:
        """Check if any artifacts are in the projection."""
        return len(self.projection) > 0
    
    @property
    def is_denied(self) -> bool:
        """Check if access was denied."""
        return self.outcome == AuthorizationOutcome.DENY
    
    @property
    def is_limited(self) -> bool:
        """Check if access was granted with limitations."""
        return self.outcome == AuthorizationOutcome.LIMIT
    
    def with_confidence(self, confidence: float) -> MemoryAccessResponse:
        """Return a copy with updated confidence."""
        return dataclass_replace(self, confidence=confidence)
    
    def add_warning(self, warning: str) -> MemoryAccessResponse:
        """Add a warning to the response."""
        new_warnings = self.warnings + (warning,)
        return dataclass_replace(self, warnings=new_warnings)
    
    def add_limitation(self, limitation: str) -> MemoryAccessResponse:
        """Add a limitation note."""
        new_limitations = self.limitations + (limitation,)
        return dataclass_replace(self, limitations=new_limitations)
    
    def add_diagnostic(self, key: str, value: Any) -> MemoryAccessResponse:
        """Add a diagnostic entry."""
        new_diagnostics = dict(self.diagnostics)
        new_diagnostics[key] = value
        return dataclass_replace(self, diagnostics=new_diagnostics)
    
    @classmethod
    def for_allowed(
        cls,
        projection: Tuple[Any, ...],
        total_count: int,
        generated_by: Optional[str] = None,
    ) -> MemoryAccessResponse:
        """
        Create a response with allowed access.
        
        Args:
            projection: Visible artifacts
            total_count: Total matches before filtering
            generated_by: Who processed this? (optional)
            
        Returns:
            New MemoryAccessResponse with ALLOW outcome
        """
        return cls(
            response_id=str(time.time_ns()),
            outcome=AuthorizationOutcome.ALLOW,
            projection=projection,
            total_count=total_count,
            filtered_count=max(0, total_count - len(projection)),
            generated_by=generated_by,
        )
    
    @classmethod
    def for_denied(
        cls,
        reason: str,
        generated_by: Optional[str] = None,
    ) -> MemoryAccessResponse:
        """
        Create a response with denied access.
        
        Args:
            reason: Why was access denied?
            generated_by: Who processed this? (optional)
            
        Returns:
            New MemoryAccessResponse with DENY outcome
        """
        return cls(
            response_id=str(time.time_ns()),
            outcome=AuthorizationOutcome.DENY,
            authorization_notes=reason,
            generated_by=generated_by,
        )
    
    @classmethod
    def for_limited(
        cls,
        projection: Tuple[Any, ...],
        total_count: int,
        limitations: Tuple[str, ...],
        generated_by: Optional[str] = None,
    ) -> MemoryAccessResponse:
        """
        Create a response with limited access.
        
        Args:
            projection: Visible artifacts (partial)
            total_count: Total matches before filtering
            limitations: What constraints were applied?
            generated_by: Who processed this? (optional)
            
        Returns:
            New MemoryAccessResponse with LIMIT outcome
        """
        return cls(
            response_id=str(time.time_ns()),
            outcome=AuthorizationOutcome.LIMIT,
            projection=projection,
            total_count=total_count,
            filtered_count=max(0, total_count - len(projection)),
            limitations=limitations,
            generated_by=generated_by,
        )


# =============================================================================
# ACCESS RESPONSE BUILDER - Mutable builder
# =============================================================================


class MemoryAccessResponseBuilder:
    """
    Mutable builder for constructing access responses.
    
    Allows incremental configuration before producing an immutable response.
    """
    
    def __init__(self):
        self._response_id: Optional[str] = None
        
        # Authorization result
        self._outcome: AuthorizationOutcome = AuthorizationOutcome.ALLOW
        self._authorization_notes: Optional[str] = None
        
        # Projection
        self._projection: List[Any] = []
        self._total_count: int = 0
        self._filtered_count: int = 0
        
        # Metadata
        self._confidence: float = 1.0
        self._limitations: List[str] = []
        
        # Diagnostics
        self._execution_time_ms: float = 0.0
        self._warnings: List[str] = []
        self._diagnostics: Dict[str, Any] = {}
        
        # Projection details
        self._projection_type: str = "unknown"
        self._timestamp_utc: float = time.time()
        
        # Provenance
        self._generated_by: Optional[str] = None
    
    def set_response_id(self, response_id: str) -> "MemoryAccessResponseBuilder":
        """Set the response ID."""
        self._response_id = response_id
        return self
    
    def set_outcome(self, outcome: AuthorizationOutcome) -> "MemoryAccessResponseBuilder":
        """Set the authorization outcome."""
        self._outcome = outcome
        return self
    
    def set_authorization_notes(self, notes: str) -> "MemoryAccessResponseBuilder":
        """Set authorization explanation."""
        self._authorization_notes = notes
        return self
    
    def add_projection_item(self, item: Any) -> "MemoryAccessResponseBuilder":
        """Add an artifact to the projection."""
        self._projection.append(item)
        return self
    
    def set_total_count(self, count: int) -> "MemoryAccessResponseBuilder":
        """Set total matches before visibility filtering."""
        self._total_count = max(0, count)
        return self
    
    def set_confidence(self, confidence: float) -> "MemoryAccessResponseBuilder":
        """Set result confidence (0.0-1.0)."""
        self._confidence = max(0.0, min(1.0, confidence))
        return self
    
    def add_limitation(self, limitation: str) -> "MemoryAccessResponseBuilder":
        """Add a constraint that affected results."""
        if limitation not in self._limitations:
            self._limitations.append(limitation)
        return self
    
    def set_execution_time_ms(self, time_ms: float) -> "MemoryAccessResponseBuilder":
        """Set processing time in milliseconds."""
        self._execution_time_ms = max(0.0, time_ms)
        return self
    
    def add_warning(self, warning: str) -> "MemoryAccessResponseBuilder":
        """Add a non-critical issue."""
        if warning not in self._warnings:
            self._warnings.append(warning)
        return self
    
    def set_diagnostic(self, key: str, value: Any) -> "MemoryAccessResponseBuilder":
        """Set a diagnostic entry."""
        self._diagnostics[key] = value
        return self
    
    def set_projection_type(self, projection_type: str) -> "MemoryAccessResponseBuilder":
        """Set the type of projection generated."""
        self._projection_type = projection_type
        return self
    
    def set_generated_by(self, generated_by: str) -> "MemoryAccessResponseBuilder":
        """Set who/what processed this request."""
        self._generated_by = generated_by
        return self
    
    def build(self) -> MemoryAccessResponse:
        """
        Build an immutable MemoryAccessResponse.
        
        Returns:
            New MemoryAccessResponse with all settings applied
        """
        # Calculate filtered count
        filtered_count = max(0, self._total_count - len(self._projection))
        
        return MemoryAccessResponse(
            response_id=self._response_id or str(time.time_ns()),
            outcome=self._outcome,
            authorization_notes=self._authorization_notes,
            projection=tuple(self._projection),
            total_count=self._total_count,
            filtered_count=filtered_count,
            confidence=self._confidence,
            limitations=tuple(self._limitations),
            execution_time_ms=self._execution_time_ms,
            warnings=tuple(self._warnings),
            diagnostics=dict(self._diagnostics),
            projection_type=self._projection_type,
            timestamp_utc=self._timestamp_utc,
            generated_by=self._generated_by,
        )


# =============================================================================
# UTILITY FUNCTIONS
# =============================================================================


def dataclass_replace(instance: MemoryAccessResponse, **kwargs) -> MemoryAccessResponse:
    """Replace fields in a frozen dataclass."""
    return MemoryAccessResponse(
        response_id=instance.response_id,
        outcome=kwargs.get("outcome", instance.outcome),
        authorization_notes=kwargs.get("authorization_notes", instance.authorization_notes),
        projection=kwargs.get("projection", instance.projection),
        total_count=kwargs.get("total_count", instance.total_count),
        filtered_count=kwargs.get("filtered_count", instance.filtered_count),
        confidence=kwargs.get("confidence", instance.confidence),
        limitations=kwargs.get("limitations", instance.limitations),
        execution_time_ms=kwargs.get("execution_time_ms", instance.execution_time_ms),
        warnings=kwargs.get("warnings", instance.warnings),
        diagnostics=dict(instance.diagnostics) if "diagnostics" not in kwargs else kwargs["diagnostics"],
        projection_type=kwargs.get("projection_type", instance.projection_type),
        timestamp_utc=kwargs.get("timestamp_utc", instance.timestamp_utc),
        generated_by=kwargs.get("generated_by", instance.generated_by),
    )


# =============================================================================
# EXPORTS
# =============================================================================

__all__ = [
    "MemoryAccessResponse",
    "AuthorizationOutcome",
    "MemoryAccessResponseBuilder",
    "dataclass_replace",
]