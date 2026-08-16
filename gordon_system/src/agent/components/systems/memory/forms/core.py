# Memory Forms Core - Shared Utilities
# =====================================

"""
Core utilities for Memory Form implementations.

This module provides:
    - Base class extensions
    - Common organization strategies
    - Projection helpers
"""

from __future__ import annotations

from typing import Dict, Any, Tuple, Optional
from dataclasses import dataclass, field
import time


@dataclass(frozen=True)
class ClusterDefinition:
    """
    Definition of an organizational cluster within a Memory Form.
    
    Fields:
        cluster_id:       Unique identifier for this cluster
        name:             Human-readable name
        description:      What defines this cluster?
        
        # Membership
        member_count:     Number of artifacts in this cluster
        
        # Statistics
        center_of_gravity: Where is the semantic center? (vector representation)
        
        # Timestamps
        formed_at_utc:    When was the cluster identified?
    """
    
    cluster_id: str
    name: str
    description: Optional[str] = None
    
    member_count: int = 0
    center_of_gravity: Tuple[float, ...] = field(default_factory=tuple)
    
    formed_at_utc: float = field(default_factory=time.time)


@dataclass(frozen=True)
class OrganizationRecord:
    """
    Record of how an artifact is organized within a form.
    
    Fields:
        artifact_id:      Which artifact?
        form_kind:        In which form?
        
        # Organization details
        organizing_principle: How is this organized?
        clusters:           Which clusters does this belong to?
        priority:           Relative importance (0.0-1.0)
        
        # Timestamps
        admitted_at_utc:  When added to form?
        last_accessed_utc: Last access time?
    """
    
    artifact_id: str
    form_kind: str
    
    organizing_principle: Optional[str] = None
    clusters: Tuple[str, ...] = field(default_factory=tuple)
    priority: float = 1.0
    
    admitted_at_utc: float = field(default_factory=time.time)
    last_accessed_utc: float = field(default_factory=time.time)


class FormOrganizationStrategy:
    """
    Base class for form-specific organization strategies.
    
    Each Memory Form can use a specialized strategy to organize artifacts
    according to its semantic principle.
    """
    
    def __init__(self, form_kind: str):
        self._form_kind = form_kind
    
    @property
    def form_kind(self) -> str:
        """Get the form kind this strategy serves."""
        return self._form_kind
    
    def is_admissible(self, artifact: Any) -> bool:
        """
        Check if an artifact is admissible to this organization strategy.
        
        Args:
            artifact: The MemoryArtifact to check
            
        Returns:
            True if admissible
        """
        # Base implementation - all artifacts are admissible
        return True
    
    def organize(self, artifact: Any) -> OrganizationRecord:
        """
        Organize an artifact according to this strategy's principle.
        
        Args:
            artifact: The MemoryArtifact to organize
            
        Returns:
            OrganizationRecord describing how the artifact is organized
        """
        return OrganizationRecord(
            artifact_id=getattr(artifact, 'identity', None),
            form_kind=self._form_kind,
            organizing_principle=self._get_organizing_principle(),
        )
    
    def _get_organizing_principle(self) -> Optional[str]:
        """Get the organizing principle for this strategy."""
        return None
    
    def cluster_artifact(self, artifact: Any, potential_clusters: Dict[str, ClusterDefinition]) -> Tuple[str, ...]:
        """
        Determine which clusters an artifact belongs to.
        
        Args:
            artifact: The MemoryArtifact
            potential_clusters: Available clusters
            
        Returns:
            Tuple of cluster IDs this artifact belongs to
        """
        # Base implementation - no clusters by default
        return tuple()


class TemporalOrganizationStrategy(FormOrganizationStrategy):
    """Organize artifacts by temporal sequence."""
    
    def __init__(self):
        super().__init__("temporal")
    
    def _get_organizing_principle(self) -> str:
        return "temporal_sequence"
    
    def organize(self, artifact: Any) -> OrganizationRecord:
        record = super().organize(artifact)
        created_at = getattr(artifact, 'created_at_utc', time.time())
        return dataclass_replace_organization(record, admitted_at_utc=created_at)


class SemanticOrganizationStrategy(FormOrganizationStrategy):
    """Organize artifacts by semantic meaning."""
    
    def __init__(self):
        super().__init__("semantic")
    
    def _get_organizing_principle(self) -> str:
        return "semantic_similarity"
    
    def cluster_artifact(self, artifact: Any, potential_clusters: Dict[str, ClusterDefinition]) -> Tuple[str, ...]:
        # For semantic organization, cluster by semantic identity
        semantic_id = getattr(artifact, 'identity', None)
        if hasattr(semantic_id, 'semantic_identity'):
            sid = semantic_id.semantic_identity
            # Simple hash-based clustering for demonstration
            cluster_hash = hash(sid) % len(potential_clusters) if potential_clusters else 0
            clusters = list(potential_clusters.keys())
            if cluster_hash < len(clusters):
                return (clusters[cluster_hash],)
        return tuple()


class EmotionalOrganizationStrategy(FormOrganizationStrategy):
    """Organize artifacts by affective significance."""
    
    def __init__(self):
        super().__init__("emotional")
    
    def _get_organizing_principle(self) -> str:
        return "affective_significance"
    
    def is_admissible(self, artifact: Any) -> bool:
        # Emotional form only admits artifacts with emotional content
        if hasattr(artifact, 'tags'):
            emotional_tags = {'emotional', 'significant', 'memory'}
            return bool(set(artifact.tags) & emotional_tags)
        return True  # Fallback - allow if no tags


class AutobiographicalOrganizationStrategy(FormOrganizationStrategy):
    """Organize artifacts by personal timeline and self-relevance."""
    
    def __init__(self):
        super().__init__("autobiographical")
    
    def _get_organizing_principle(self) -> str:
        return "personal_timeline"


# =============================================================================
# UTILITY FUNCTIONS
# =============================================================================


def dataclass_replace_organization(instance: OrganizationRecord, **kwargs) -> OrganizationRecord:
    """Replace fields in a frozen OrganizationRecord."""
    return OrganizationRecord(
        artifact_id=kwargs.get("artifact_id", instance.artifact_id),
        form_kind=kwargs.get("form_kind", instance.form_kind),
        organizing_principle=kwargs.get("organizing_principle", instance.organizing_principle),
        clusters=kwargs.get("clusters", instance.clusters),
        priority=kwargs.get("priority", instance.priority),
        admitted_at_utc=kwargs.get("admitted_at_utc", instance.admitted_at_utc),
        last_accessed_utc=kwargs.get("last_accessed_utc", instance.last_accessed_utc),
    )


def create_cluster(
    cluster_id: str,
    name: str,
    description: Optional[str] = None,
) -> ClusterDefinition:
    """
    Create a new cluster definition.
    
    Args:
        cluster_id: Unique identifier
        name: Human-readable name
        description: Optional description
        
    Returns:
        New ClusterDefinition
    """
    return ClusterDefinition(
        cluster_id=cluster_id,
        name=name,
        description=description,
        formed_at_utc=time.time(),
    )


__all__ = [
    "ClusterDefinition",
    "OrganizationRecord",
    "FormOrganizationStrategy",
    "TemporalOrganizationStrategy",
    "SemanticOrganizationStrategy",
    "EmotionalOrganizationStrategy",
    "AutobiographicalOrganizationStrategy",
    "dataclass_replace_organization",
    "create_cluster",
]