# Semantic Memory - Concepts, Categories, and Meaning
# ====================================================

"""
Semantic Memory: Organizes artifacts according to meaning.

This form organizes artifacts according to:
    - Concepts and categories
    - Properties and relationships
    - Definitions and general knowledge
    - Conceptual neighborhoods

Admission Policy:
    - Stable semantic information
    - General knowledge (not specific events)
    - Concept definitions
    - Taxonomic relationships

Activation Triggers:
    - Concept retrieval requests
    - Reasoning operations
    - Language understanding
    - Knowledge queries
"""

from __future__ import annotations

from typing import Dict, Any, Tuple
import time


class SemanticMemory:
    """Organizes artifacts by semantic meaning and conceptual structure."""
    
    def __init__(self, name: str, kind: str):
        self._name = name
        self._kind = kind
        self._substrate: Any = None
        self._state = {"is_active": False, "artifact_count": 0}
        self._membership: Dict[str, Any] = {}
        self._concepts: Dict[str, list] = {}  # concept_id -> artifact_ids
        
        self._initialized_at_utc = time.time()
    
    @property
    def name(self) -> str:
        return self._name
    
    @property
    def kind(self) -> str:
        return self._kind
    
    @property
    def is_active(self) -> bool:
        return self._state["is_active"]
    
    def initialize(self, substrate: Any) -> bool:
        try:
            from ..foundations.substrate import MemorySubstrate as MS
            if isinstance(substrate, MS):
                self._substrate = substrate
                return True
        except ImportError:
            pass
        self._substrate = substrate
        return True
    
    def _is_admissible(self, artifact: Any) -> bool:
        """Check if artifact represents semantic information."""
        tags = getattr(artifact, 'tags', set())
        
        # Semantic indicators
        semantic_tags = {'concept', 'definition', 'knowledge', 'meaning'}
        if set(tags) & semantic_tags:
            return True
        
        # Check for general knowledge (not event-specific)
        content = str(getattr(artifact, 'semantic_content', {}))
        if any(kw in content.lower() for kw in ['is a', 'are', 'the definition']):
            return True
        
        return False
    
    def _organize_artifact(self, artifact: Any) -> Dict[str, Any]:
        """Organize artifact by semantic concept."""
        content = getattr(artifact, 'semantic_content', {})
        
        # Extract primary concept from content
        primary_concept = self._extract_concept(content)
        
        return {
            "form_kind": self._kind,
            "primary_concept": primary_concept,
            "admitted_at_utc": time.time(),
        }
    
    def _extract_concept(self, content: Dict[str, Any]) -> str:
        """Extract the primary concept from semantic content."""
        # Simple extraction - in practice would use NLP or embeddings
        content_str = str(content).lower()
        
        # Look for common conceptual patterns
        if 'is a' in content_str:
            parts = content_str.split('is a')
            if len(parts) > 1:
                return parts[0].strip()[:50]
        
        # Use first key as concept
        keys = list(content.keys())
        if keys:
            return str(keys[0])[:50]
        
        return "general"
    
    def add_artifact(self, artifact_id: str) -> bool:
        """Add artifact to semantic memory."""
        if self._substrate is None:
            return False
        
        get_method = getattr(self._substrate, 'get_artifact', lambda x: None)
        artifact = get_method(artifact_id)
        
        if artifact is None:
            return False
        
        if not self._is_admissible(artifact):
            return False
        
        organization = self._organize_artifact(artifact)
        concept = organization.get("primary_concept", "general")
        
        # Record membership
        self._membership[artifact_id] = {
            "organization": organization,
        }
        
        # Add to concept cluster
        if concept not in self._concepts:
            self._concepts[concept] = []
        self._concepts[concept].append(artifact_id)
        
        # Update state
        self._state["is_active"] = True
        self._state["artifact_count"] = len(self._membership)
        
        return True
    
    def remove_artifact(self, artifact_id: str) -> bool:
        """Remove artifact from semantic memory."""
        if artifact_id not in self._membership:
            return False
        
        concept = self._membership[artifact_id]["organization"].get("primary_concept")
        del self._membership[artifact_id]
        
        # Remove from concept cluster
        if concept and concept in self._concepts:
            self._concepts[concept] = [
                aid for aid in self._concepts[concept] if aid != artifact_id
            ]
        
        self._state["artifact_count"] = len(self._membership)
        return True
    
    def get_projection(self) -> Dict[str, Any]:
        """Generate projection from semantic memory."""
        artifact_ids = list(self._membership.keys())
        
        # Create concept clusters
        cluster_info = [
            {"concept": c, "count": len(members)}
            for c, members in self._concepts.items()
        ]
        
        return {
            "form_kind": self._kind,
            "name": self._name,
            "visible_artifacts": tuple(artifact_ids),
            "concept_count": len(self._concepts),
            "organization_type": "conceptual_semantic",
            "clusters": tuple(c["concept"] for c in cluster_info),
            "artifact_count": len(artifact_ids),
            "confidence": 1.0 if artifact_ids else 0.5,
            "generated_at_utc": time.time(),
        }
    
    def get_concept_members(self, concept: str) -> Tuple[str, ...]:
        """Get artifacts belonging to a specific concept."""
        return tuple(self._concepts.get(concept, []))
    
    def find_similar_artifacts(self, artifact_id: str, max_count: int = 5) -> Tuple[str, ...]:
        """Find artifacts with similar concepts."""
        if artifact_id not in self._membership:
            return tuple()
        
        current_concept = self._membership[artifact_id]["organization"].get("primary_concept")
        
        candidates = []
        for aid, org in self._membership.items():
            if aid != artifact_id:
                other_concept = org["organization"].get("primary_concept")
                if other_concept == current_concept:
                    candidates.append(aid)
        
        return tuple(candidates[:max_count])
    
    def health(self) -> Dict[str, Any]:
        """Report form health."""
        return {
            "form_kind": self._kind,
            "name": self._name,
            "is_active": self.is_active,
            "artifact_count": self._state["artifact_count"],
            "concept_count": len(self._concepts),
            "initialized_at_utc": self._initialized_at_utc,
        }
    
    def validate_membership(self) -> bool:
        """Validate all membership records."""
        for artifact_id in list(self._membership.keys()):
            if self._substrate is not None:
                get_method = getattr(self._substrate, 'get_artifact', lambda x: None)
                if get_method(artifact_id) is None:
                    del self._membership[artifact_id]
        
        return True


__all__ = ["SemanticMemory"]