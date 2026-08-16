# Internal Episode Provenance Model
# ==================================

"""
Provenance model for internal episode coordination.

Tracks where information came from and its chain of custody.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Tuple, Optional


@dataclass(frozen=True, slots=True)
class InternalEpisodeProvenance:
    """
    Complete provenance record for an episode or piece of evidence.
    
    Provenance tracks the origin and chain of custody of information.
    """
    
    # Source identification
    source_type: str
    """Type of source (capability, projection, etc.)."""
    
    source_id: Optional[str] = None
    """ID of the specific source."""
    
    timestamp_utc: str = ""
    """When the provenance was recorded."""
    
    # Chain of custody
    previous_version_id: Optional[str] = None
    """ID of previous version (if derived from another)."""
    
    transformation_steps: Tuple[str, ...] = field(default_factory=tuple)
    """Steps applied to transform the source data."""
    
    # Verification
    verified_at_utc: Optional[str] = None
    """When this was last verified."""
    
    verification_confidence: float = 1.0
    """Confidence in the provenance record itself."""


@dataclass(frozen=True, slots=True)
class RequestProvenance:
    """
    Provenance for a capability request.
    
    Tracks how and why a request was made.
    """
    
    created_at_utc: str
    """When the request was created."""
    
    created_by: str  # InternalEpisodeRequester.*
    """Who/what created the request."""
    
    correlation_id: Optional[str] = None
    """Correlation ID for distributed tracing."""
    
    causation_id: Optional[str] = None
    """Causation ID if this request results from another event."""
    
    parent_request_id: Optional[str] = None
    """ID of the parent request (if any)."""
    
    child_count: int = 0
    """Number of child requests derived from this one."""


@dataclass(frozen=True, slots=True)
class ResultProvenance:
    """
    Provenance for a capability result.
    
    Tracks how and when a result was produced.
    """
    
    produced_at_utc: str
    """When the result was produced."""
    
    produced_by: str  # capability name or source identifier
    """What/who produced the result."""
    
    request_id: Optional[str] = None
    """ID of the request that produced this result."""
    
    confidence: float = 0.5
    """Confidence in the result quality."""
    
    side_effect_recorded: bool = False
    """Whether any side effects were recorded."""