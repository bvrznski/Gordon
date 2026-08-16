# Perceptual Fusion Request - Phase 5.2.3
# =======================================

"""
Fusion Request: Specification for fusion operations.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Tuple, Optional, Any
import time
import uuid


@dataclass(frozen=True)
class PerceptualFusionRequest:
    """
    Request for perceptual fusion.
    
    Fields:
        request_identity: Unique identifier
        source_artifacts: Artifacts to fuse (references only)
        correspondence_references: Correspondence records that justify fusion
        temporal_binding_references: Temporal bindings to use
        spatial_binding_references: Spatial bindings to use
        source_dependency_references: Dependency assessments to consider
        fusion_strategy: How should artifacts be combined?
        field_policies: How to handle individual fields?
    """
    
    request_identity: str
    
    source_artifacts: Tuple[str, ...]
    
    correspondence_references: Tuple[Dict[str, Any], ...] = field(default_factory=tuple)
    temporal_binding_references: Tuple[Dict[str, Any], ...] = field(default_factory=tuple)
    spatial_binding_references: Tuple[Dict[str, Any], ...] = field(default_factory=tuple)
    source_dependency_references: Tuple[Dict[str, Any], ...] = field(default_factory=tuple)
    
    fusion_strategy: str = "complementary"  # See FusionStrategyKind
    field_policies: Dict[str, Any] = field(default_factory=dict)  # field -> policy
    
    provenance: Dict[str, Any] = field(default_factory=dict)
    
    @classmethod
    def create(
        cls,
        source_artifact_ids: List[str],
        fusion_strategy: str = "complementary",
        correspondence_refs: Optional[List[Dict[str, Any]]] = None,
        temporal_binding_refs: Optional[List[Dict[str, Any]]] = None,
        spatial_binding_refs: Optional[List[Dict[str, Any]]] = None,
    ) -> "PerceptualFusionRequest":
        """Create a fusion request."""
        return cls(
            request_identity=f"fusion_request:{uuid.uuid4().hex[:16]}",
            source_artifacts=tuple(source_artifact_ids),
            correspondence_references=tuple(correspondence_refs or []),
            temporal_binding_references=tuple(temporal_binding_refs or []),
            spatial_binding_references=tuple(spatial_binding_refs or []),
            fusion_strategy=fusion_strategy,
            provenance={
                "origin": "system",
                "created_at_utc": time.time(),
            },
        )