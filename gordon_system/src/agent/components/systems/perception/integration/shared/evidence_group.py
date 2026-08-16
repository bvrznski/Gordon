# Perception Evidence Group - Phase 5.2.3
# ========================================

"""
Evidence Group: A candidate grouping of artifacts for integration.

An EvidenceGroup proposes which artifacts may participate in one integration operation.
It does not imply that the artifacts refer to the same entity or event.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Tuple, Optional, Any
import time
import uuid


# =============================================================================
# GROUPING BASIS - Why are these artifacts grouped together?
# =============================================================================


class GroupingBasis(Enum):
    """
    Basis for grouping artifacts.
    
    Bases:
        TEMPORAL_PROXIMITY: Artifacts close in time
        SPATIAL_PROXIMITY: Artifacts close in space
        SHARED_IDENTIFIER: Artifacts share an identifier
        SHARED_SOURCE_EPISODE: Artifacts from same event source
        SHARED_PROCESS_CONTEXT: Artifacts from same process context
        SHARED_FILE_CONTEXT: Artifacts related to same file
        SHARED_UTTERANCE_CONTEXT: Artifacts from same utterance
        SHARED_APPLICATION_CONTEXT: Artifacts from same application
        SHARED_INTERACTION_CONTEXT: Artifacts from same interaction
        EXPLICIT_EXTERNAL_CORRELATION: External correlation provided
    """
    
    TEMPORAL_PROXIMITY = "temporal_proximity"
    SPATIAL_PROXIMITY = "spatial_proximity"
    SHARED_IDENTIFIER = "shared_identifier"
    SHARED_SOURCE_EPISODE = "shared_source_episode"
    SHARED_PROCESS_CONTEXT = "shared_process_context"
    SHARED_FILE_CONTEXT = "shared_file_context"
    SHARED_UTTERANCE_CONTEXT = "shared_utterance_context"
    SHARED_APPLICATION_CONTEXT = "shared_application_context"
    SHARED_INTERACTION_CONTEXT = "shared_interaction_context"
    EXPLICIT_EXTERNAL_CORRELATION = "explicit_external_correlation"


# =============================================================================
# SOURCE DEPENDENCY SUMMARY - Summary of dependency analysis
# =============================================================================


@dataclass(frozen=True)
class DependencySummary:
    """
    Summary of source dependency assessment.
    
    Fields:
        total_sources: Total number of sources in the group
        independent_count: Sources that are fully independent
        partially_dependent_count: Sources with partial dependencies
        common_source_count: Sources from same underlying source
        dependency_kind: Overall dependency classification
    """
    
    total_sources: int = 0
    independent_count: int = 0
    partially_dependent_count: int = 0
    common_source_count: int = 0
    
    dependency_kind: str = "unknown"  # independent, partially_dependent, derived_from_common


# =============================================================================
# PERCEPTUAL EVIDENCE GROUP - Candidate grouping for integration
# =============================================================================


@dataclass(frozen=True)
class PerceptualEvidenceGroup:
    """
    A candidate group of artifacts proposed for integration.
    
    Fields:
        group_identity:     Unique identifier for this group
        member_artifacts:   Artifact IDs in this group (references only)
        grouping_basis:     Why were these grouped together?
        temporal_extent:    Temporal span of the group (optional)
        spatial_extent:     Spatial span of the group (optional)
        shared_context:     Common context shared by members (optional)
        participating_modalities: Modalities represented in this group
        source_dependency_summary: Dependency analysis results
        confidence:         Confidence in grouping validity
        uncertainty:        Known limitations
    """
    
    group_identity: str                    # Unique ID
    
    member_artifacts: Tuple[str, ...]      # Artifact IDs in the group
    
    grouping_basis: GroupingBasis          # Why grouped together?
    
    temporal_extent: Optional[Dict[str, Any]] = None  # {start, end, duration}
    spatial_extent: Optional[Dict[str, Any]] = None   # {bounds, region}
    
    shared_context: Dict[str, Any] = field(default_factory=dict)  # Common context
    
    participating_modalities: Tuple[str, ...] = field(default_factory=tuple)
    
    source_dependency_summary: DependencySummary = field(default_factory=DependencySummary)
    
    confidence: float = 0.5               # 0.0-1.0
    uncertainty: float = 0.5              # 0.0-1.0
    
    provenance: Dict[str, Any] = field(default_factory=dict)  # Grouping origin
    
    @property
    def size(self) -> int:
        """Number of artifacts in this group."""
        return len(self.member_artifacts)
    
    def has_modality(self, modality: str) -> bool:
        """Check if a specific modality is represented."""
        return modality in self.participating_modalities
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert evidence group to dictionary."""
        return {
            "group_identity": self.group_identity,
            "member_artifacts_count": len(self.member_artifacts),
            "member_artifacts": list(self.member_artifacts),
            "grouping_basis": self.grouping_basis.value if hasattr(self.grouping_basis, 'value') else str(self.grouping_basis),
            "temporal_extent": dict(self.temporal_extent) if self.temporal_extent else None,
            "spatial_extent": dict(self.spatial_extent) if self.spatial_extent else None,
            "shared_context": dict(self.shared_context),
            "participating_modalities": list(self.participating_modalities),
            "source_dependency_summary": {
                "total_sources": self.source_dependency_summary.total_sources,
                "independent_count": self.source_dependency_summary.independent_count,
                "partially_dependent_count": self.source_dependency_summary.partially_dependent_count,
                "common_source_count": self.source_dependency_summary.common_source_count,
                "dependency_kind": self.source_dependency_summary.dependency_kind,
            },
            "confidence": self.confidence,
            "uncertainty": self.uncertainty,
            "provenance": dict(self.provenance),
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "PerceptualEvidenceGroup":
        """Create evidence group from dictionary."""
        return cls(
            group_identity=data.get("group_identity", str(uuid.uuid4())),
            member_artifacts=tuple(data.get("member_artifacts", [])),
            grouping_basis=GroupingBasis(data.get("grouping_basis", "temporal_proximity")),
            temporal_extent=dict(data.get("temporal_extent", {})) if data.get("temporal_extent") else None,
            spatial_extent=dict(data.get("spatial_extent", {})) if data.get("spatial_extent") else None,
            shared_context=dict(data.get("shared_context", {})),
            participating_modalities=tuple(data.get("participating_modalities", [])),
        )


# =============================================================================
# UTILITY FUNCTIONS
# =============================================================================


try:
    from enum import Enum
except ImportError:
    # Python 2 fallback
    class Enum:
        def __init__(self, **kwargs):
            for k, v in kwargs.items():
                setattr(self, k, v)


def create_evidence_group(
    artifact_ids: List[str],
    grouping_basis: GroupingBasis = GroupingBasis.TEMPORAL_PROXIMITY,
    modalities: Optional[List[str]] = None,
) -> PerceptualEvidenceGroup:
    """
    Create a new evidence group.
    
    Args:
        artifact_ids: Artifact IDs to include in the group
        grouping_basis: Basis for grouping (optional)
        modalities: Modalities represented (optional)
        
    Returns:
        New PerceptualEvidenceGroup
    """
    return PerceptualEvidenceGroup(
        group_identity=f"evidence_group:{uuid.uuid4().hex[:16]}",
        member_artifacts=tuple(artifact_ids),
        grouping_basis=grouping_basis,
        participating_modalities=tuple(modalities or ["unknown"]),
        provenance={
            "origin": "system",
            "created_at_utc": time.time(),
        },
    )