# Intermodal Correspondence Request - Phase 5.2.3
# ===============================================

"""
Correspondence Request: Specification for what correspondences to evaluate.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Tuple, Optional, Any
import time
import uuid


@dataclass(frozen=True)
class IntermodalCorrespondenceRequest:
    """
    Request for intermodal correspondence evaluation.
    
    Fields:
        request_identity: Unique identifier
        candidate_artifacts: Artifact IDs to evaluate
        candidate_correspondence_kinds: What kinds of correspondences to consider?
        temporal_requirements: Temporal constraints
        spatial_requirements: Spatial constraints
        identity_requirements: Identity matching requirements
        source_dependency_reference: Reference to dependency assessment
        constraints: Additional constraints
    """
    
    request_identity: str
    
    candidate_artifacts: Tuple[str, ...]
    
    candidate_correspondence_kinds: Tuple[str, ...] = field(default_factory=tuple)
    temporal_requirements: Dict[str, Any] = field(default_factory=dict)
    spatial_requirements: Dict[str, Any] = field(default_factory=dict)
    identity_requirements: Dict[str, Any] = field(default_factory=dict)
    
    source_dependency_reference: Optional[str] = None
    constraints: Dict[str, Any] = field(default_factory=dict)
    
    provenance: Dict[str, Any] = field(default_factory=dict)
    
    @classmethod
    def create(
        cls,
        artifact_ids: List[str],
        correspondence_kinds: Optional[List[str]] = None,
        temporal_window: Optional[Dict[str, float]] = None,
        spatial_bounds: Optional[Dict[str, float]] = None,
    ) -> "IntermodalCorrespondenceRequest":
        """Create a new correspondence request."""
        return cls(
            request_identity=f"correspondence_request:{uuid.uuid4().hex[:16]}",
            candidate_artifacts=tuple(artifact_ids),
            candidate_correspondence_kinds=tuple(correspondence_kinds or [
                "same_entity_candidate",
                "same_event_candidate",
                "same_state_candidate",
            ]),
            temporal_requirements=temporal_window or {},
            spatial_requirements=spatial_bounds or {},
            provenance={
                "origin": "system",
                "created_at_utc": time.time(),
            },
        )