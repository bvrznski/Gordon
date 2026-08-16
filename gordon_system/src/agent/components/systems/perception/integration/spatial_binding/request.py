# Spatial Binding Request - Phase 5.2.3
# =====================================

"""
Spatial Binding Request: Specification for spatial binding operations.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Tuple, Optional, Any
import time
import uuid


@dataclass(frozen=True)
class SpatialBindingRequest:
    """
    Request for spatial binding.
    
    Fields:
        request_identity: Unique identifier
        candidate_artifacts: Artifact IDs to bind in space
        aligned_reference_frames: Reference frames already aligned
        allowed_relation_kinds: Which spatial relations are permitted?
        topology_requirements: Topological constraints
        hierarchy_requirements: Hierarchical structure requirements
        occlusion_policy: How to handle occlusions?
    """
    
    request_identity: str
    
    candidate_artifacts: Tuple[str, ...]
    
    aligned_reference_frames: Dict[str, Dict[str, Any]] = field(default_factory=dict)  # frame -> transform
    allowed_relation_kinds: Tuple[str, ...] = field(default_factory=tuple)
    topology_requirements: Dict[str, Any] = field(default_factory=dict)
    hierarchy_requirements: Dict[str, Any] = field(default_factory=dict)
    
    occlusion_policy: str = "record"  # record, infer, or reject
    
    provenance: Dict[str, Any] = field(default_factory=dict)
    
    @classmethod
    def create(
        cls,
        artifact_ids: List[str],
        reference_frame: str = "global",
        allowed_relations: Optional[List[str]] = None,
    ) -> "SpatialBindingRequest":
        """Create a spatial binding request."""
        return cls(
            request_identity=f"spatial_binding_request:{uuid.uuid4().hex[:16]}",
            candidate_artifacts=tuple(artifact_ids),
            aligned_reference_frames={reference_frame: {"type": "coordinate_system"}},
            allowed_relation_kinds=tuple(allowed_relations or [
                "contains", "inside", "overlaps", "adjacent_to",
                "parent_of", "child_of", "member_of",
            ]),
            provenance={
                "origin": "system",
                "created_at_utc": time.time(),
            },
        )