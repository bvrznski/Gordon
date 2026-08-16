# Autobiographical Memory - Personal Timeline and Self-Continuity
# ===============================================================

"""
Autobiographical Memory: Preserves continuity of self through personal timeline.

This form organizes artifacts according to:
    - Personal timeline and chronological order
    - Self-relevance and identity relevance
    - Life narrative structure
    - Persistent relationships over time

Form Laws Complied:
    FORM-LAW-001: Organizes one semantic perspective (personal timeline)
    FORM-LAW-002: Never owns artifacts, only projects them
    FORM-LAW-003: Preserves artifact identity across projections
    FORM-LAW-004: Exposes immutable projections

Admission Policy:
    - Artifacts directly involving Gordon's self
    - Significantly modify self-model
    - Influence long-term identity
    - Define persistent personal history

Activation Triggers:
    - Self-reference in reasoning
    - Identity-related queries
    - Narrative reconstruction needs
"""

from __future__ import annotations

from typing import Dict, Any, Tuple, Optional
from dataclasses import dataclass
import time


# =============================================================================
# IMPORTS
# =============================================================================


def _import_substrate():
    """Import MemorySubstrate at runtime."""
    from ..foundations.substrate import MemorySubstrate
    return MemorySubstrate


# =============================================================================
# AUTOBIOGRAPHICAL MEMORY - Personal Timeline Organization
# =============================================================================


class AutobiographicalMemory:
    """
    Organizes artifacts according to personal timeline and self-continuity.
    
    This form maintains the narrative of Gordon's existence over time,
    connecting events, experiences, and knowledge into a coherent life story.
    
    Key Characteristics:
        - Temporal organization (when things happened)
        - Self-relevance filtering
        - Narrative coherence maintenance
        - Identity-preserving projection
    
    Form Laws Implemented:
        FORM-LAW-001: One semantic perspective (personal timeline)
        FORM-LAW-002: No artifact ownership, only projection
        FORM-LAW-003: Artifact identity preserved
        FORM-LAW-004: Immutable projections exposed
    """
    
    def __init__(self, name: str, kind: str):
        """
        Initialize Autobiographical Memory.
        
        Args:
            name: Unique identifier for this form instance
            kind: Form kind (should be 'autobiographical')
        """
        self._name = name
        self._kind = kind
        self._substrate: Optional[Any] = None
        self._state = {"is_active": False, "artifact_count": 0}
        self._membership: Dict[str, Any] = {}
        self._timeline: list = []  # Chronological ordering
        
        # Timestamps for form lifecycle
        self._initialized_at_utc = time.time()
        self._activated_at_utc: Optional[float] = None
    
    @property
    def name(self) -> str:
        """Get the form's unique name."""
        return self._name
    
    @property
    def kind(self) -> str:
        """Get the form's kind."""
        return self._kind
    
    @property
    def is_active(self) -> bool:
        """Check if this form is currently active."""
        return self._state["is_active"]
    
    def initialize(self, substrate: Any) -> bool:
        """
        Initialize with substrate reference.
        
        Args:
            substrate: The MemorySubstrate instance
            
        Returns:
            True if initialization succeeded
        """
        try:
            from ..foundations.substrate import MemorySubstrate as MS
            self._substrate = substrate
            return True
        except ImportError:
            self._substrate = substrate
            return True
    
    def _is_admissible(self, artifact: Any) -> bool:
        """
        Check if artifact is admissible to autobiographical memory.
        
        Admissibility criteria for autobiographical form:
            - Has 'self' or 'gordon' relevance in tags or content
            - Represents a personal experience or event
            - Significantly modifies self-model
            
        Args:
            artifact: The MemoryArtifact to check
            
        Returns:
            True if admissible
        """
        # Get artifact properties with fallbacks
        tags = getattr(artifact, 'tags', set())
        semantic_content = getattr(artifact, 'semantic_content', {})
        
        # Check for self-relevance in tags
        self_tags = {'self', 'gordon', 'personal', 'life', 'identity'}
        if set(tags) & self_tags:
            return True
        
        # Check content for self-reference
        content_str = str(semantic_content).lower()
        self_keywords = ['i ', 'my ', 'mine ', 'gordon', 'me ', 'myself']
        if any(keyword in content_str for keyword in self_keywords):
            return True
        
        # Check artifact kind for personal events
        artifact_kind = getattr(artifact, 'artifact_kind', None)
        if artifact_kind:
            kind_value = str(getattr(artifact_kind, 'value', '')).lower()
            if any(kw in kind_value for kw in ['experience', 'event', 'conversation']):
                return True
        
        # Default: allow if no explicit exclusion
        return True
    
    def _organize_artifact(self, artifact: Any) -> Dict[str, Any]:
        """
        Organize artifact within autobiographical form.
        
        Creates timeline entry with self-relevance scoring.
        
        Args:
            artifact: The MemoryArtifact to organize
            
        Returns:
            Organization data including timeline position
        """
        # Get timestamp for ordering
        created_at = getattr(artifact, 'created_at_utc', time.time())
        
        # Calculate self-relevance score (0.0-1.0)
        relevance_score = self._calculate_relevance(artifact)
        
        return {
            "form_kind": self._kind,
            "timeline_position": len(self._timeline),
            "timestamp_utc": created_at,
            "self_relevance": relevance_score,
            "admitted_at_utc": time.time(),
        }
    
    def _calculate_relevance(self, artifact: Any) -> float:
        """
        Calculate how relevant an artifact is to self-continuity.
        
        Args:
            artifact: The MemoryArtifact
            
        Returns:
            Relevance score (0.0-1.0)
        """
        # Base relevance
        base_score = 0.5
        
        # Increase for personal tags
        tags = getattr(artifact, 'tags', set())
        personal_tags = {'self', 'gordon', 'personal', 'identity'}
        tag_matches = len(set(tags) & personal_tags)
        base_score += min(tag_matches * 0.1, 0.3)
        
        # Increase for self-referential content
        content_str = str(getattr(artifact, 'semantic_content', {})).lower()
        if any(kw in content_str for kw in ['i ', 'my ', 'gordon']):
            base_score += 0.2
        
        return min(base_score, 1.0)
    
    def add_artifact(self, artifact_id: str) -> bool:
        """
        Add artifact to autobiographical memory.
        
        This does NOT create a new artifact - only adds it to this form's
        projection with timeline organization.
        
        Args:
            artifact_id: ID of the artifact to add
            
        Returns:
            True if added successfully
        """
        # Get artifact from substrate
        if self._substrate is None:
            return False
        
        get_method = getattr(self._substrate, 'get_artifact', None)
        if not get_method:
            return False
            
        artifact = get_method(artifact_id)
        
        if artifact is None:
            return False
        
        # Check admissibility
        if not self._is_admissible(artifact):
            return False
        
        # Organize and record
        organization = self._organize_artifact(artifact)
        
        # Insert into timeline (maintain chronological order)
        timestamp = organization.get("timestamp_utc", time.time())
        inserted = False
        for i, (existing_id, existing_org) in enumerate(self._timeline):
            if timestamp <= existing_org.get("timestamp_utc", 0):
                self._timeline.insert(i, (artifact_id, organization))
                inserted = True
                break
        
        if not inserted:
            self._timeline.append((artifact_id, organization))
        
        # Record membership
        self._membership[artifact_id] = {
            "organization": organization,
            "timeline_index": len(self._timeline) - 1,
        }
        
        # Update state
        self._state["is_active"] = True
        self._state["artifact_count"] = len(self._timeline)
        
        if self._activated_at_utc is None:
            self._activated_at_utc = time.time()
        
        return True
    
    def remove_artifact(self, artifact_id: str) -> bool:
        """
        Remove artifact from this form's projection.
        
        Does NOT delete the artifact - only removes it from this form's view.
        
        Args:
            artifact_id: ID to remove
            
        Returns:
            True if removed successfully
        """
        if artifact_id not in self._membership:
            return False
        
        # Remove from timeline
        for i, (aid, _) in enumerate(self._timeline):
            if aid == artifact_id:
                self._timeline.pop(i)
                break
        
        del self._membership[artifact_id]
        
        # Update state
        self._state["artifact_count"] = len(self._timeline)
        
        return True
    
    def get_projection(self) -> Dict[str, Any]:
        """
        Generate projection from autobiographical memory.
        
        Returns:
            Projection data including timeline and artifacts
        """
        # Get artifact IDs in chronological order
        artifact_ids = [aid for aid, _ in self._timeline]
        
        # Calculate clusters (e.g., by year/month)
        clusters = self._collect_clusters()
        
        return {
            "form_kind": self._kind,
            "name": self._name,
            "visible_artifacts": tuple(artifact_ids),
            "timeline_count": len(self._timeline),
            "organization_type": "temporal_with_self_relevance",
            "clusters": clusters,
            "artifact_count": len(artifact_ids),
            "confidence": 1.0 if artifact_ids else 0.5,
            "generated_at_utc": time.time(),
        }
    
    def _collect_clusters(self) -> Tuple[str, ...]:
        """Collect cluster information based on timeline grouping."""
        # Group artifacts by year for simple clustering
        clusters_by_year: Dict[int, list] = {}
        
        for artifact_id, org in self._timeline:
            ts = org.get("timestamp_utc", time.time())
            year = int(ts)
            if year not in clusters_by_year:
                clusters_by_year[year] = []
            clusters_by_year[year].append(artifact_id)
        
        # Return cluster IDs
        return tuple(f"year_{y}" for y in sorted(clusters_by_year.keys()))
    
    def get_timeline(self) -> Tuple[Tuple[str, Dict[str, Any]], ...]:
        """Get the complete timeline of organized artifacts."""
        return tuple(self._timeline)
    
    def get_artifacts_in_range(
        self,
        start_time: float,
        end_time: float,
    ) -> Tuple[str, ...]:
        """
        Get artifact IDs within a time range.
        
        Args:
            start_time: Start timestamp (UTC)
            end_time: End timestamp (UTC)
            
        Returns:
            Tuple of artifact IDs
        """
        result = []
        for artifact_id, org in self._timeline:
            ts = org.get("timestamp_utc", 0)
            if start_time <= ts <= end_time:
                result.append(artifact_id)
        return tuple(result)
    
    def get_self_relevance(self, artifact_id: str) -> float:
        """
        Get the self-relevance score for an artifact.
        
        Args:
            artifact_id: The artifact ID
            
        Returns:
            Relevance score (0.0-1.0)
        """
        if artifact_id not in self._membership:
            return 0.0
        org = self._membership[artifact_id]["organization"]
        return org.get("self_relevance", 0.5)
    
    def health(self) -> Dict[str, Any]:
        """Report form health."""
        return {
            "form_kind": self._kind,
            "name": self._name,
            "is_active": self.is_active,
            "artifact_count": self._state["artifact_count"],
            "timeline_entries": len(self._timeline),
            "initialized_at_utc": self._initialized_at_utc,
            "activated_at_utc": self._activated_at_utc,
        }
    
    def validate_membership(self) -> bool:
        """
        Validate all membership records.
        
        Returns:
            True if valid
        """
        for artifact_id, _ in list(self._timeline):
            if self._substrate is not None:
                get_method = getattr(self._substrate, 'get_artifact', lambda x: None)
                if get_method(artifact_id) is None:
                    # Artifact doesn't exist - remove from timeline
                    self.remove_artifact(artifact_id)
        
        return True


__all__ = ["AutobiographicalMemory"]