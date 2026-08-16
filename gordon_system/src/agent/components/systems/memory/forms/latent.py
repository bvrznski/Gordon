# Latent Memory - Latent Semantic Representations
# ================================================

"""
Latent Memory: Organizes artifacts through latent semantic representations.

This form organizes artifacts according to:
    - Latent semantic similarity
    - Distributed representations
    - High-dimensional semantic structure

Admission Policy:
    - Potentially every artifact (broad coverage)
    - Artifacts with semantic content
    - Items that can be embedded in latent space

Activation Triggers:
    - Implicit semantic retrieval
    - Approximate similarity matching
    - Representation alignment

Important: Latent representations are retrieval aids only.
They never become the semantic authority.
"""

from __future__ import annotations

from typing import Dict, Any, Tuple, List
import time


class LatentMemory:
    """Organizes artifacts through latent semantic representations."""
    
    def __init__(self, name: str, kind: str):
        self._name = name
        self._kind = kind
        self._substrate: Any = None
        self._state = {"is_active": False, "artifact_count": 0}
        self._membership: Dict[str, Any] = {}
        # artifact_id -> latent_vector (list of floats)
        self._latent_vectors: Dict[str, List[float]] = {}
        # clusters by nearest neighbors
        self._clusters: Dict[str, List[str]] = {}
        
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
        """Latent memory accepts artifacts with semantic content."""
        # Accept any artifact that has semantic_content
        content = getattr(artifact, 'semantic_content', None)
        if content is not None and content:
            return True
        return False
    
    def _organize_artifact(self, artifact: Any) -> Dict[str, Any]:
        """Organize artifact with latent representation."""
        # Generate a simple latent vector based on content
        latent_vector = self._generate_latent_vector(artifact)
        
        return {
            "form_kind": self._kind,
            "latent_dimension": len(latent_vector),
            "admitted_at_utc": time.time(),
        }
    
    def _generate_latent_vector(self, artifact: Any) -> List[float]:
        """Generate a latent vector representation for an artifact."""
        content = getattr(artifact, 'semantic_content', {})
        
        # Simple vector generation based on content
        # In practice, this would use embeddings from a model
        
        # Create dimension 10 for demonstration
        vector = []
        
        # First few dimensions: length features
        content_str = str(content)
        vector.append(len(content_str) / 100.0)  # Length normalized
        
        # Check for content patterns
        vector.append(1.0 if 'concept' in content_str.lower() else 0.0)
        vector.append(1.0 if 'event' in content_str.lower() else 0.0)
        vector.append(1.0 if 'action' in content_str.lower() else 0.0)
        vector.append(1.0 if 'object' in content_str.lower() else 0.0)
        
        # Add random components for higher dimensions
        import hashlib
        content_hash = hashlib.md5(content_str.encode()).hexdigest()
        for i in range(5):
            vector.append((ord(content_hash[i]) % 100) / 100.0)
        
        return vector
    
    def _compute_similarity(self, vec1: List[float], vec2: List[float]) -> float:
        """Compute cosine similarity between two vectors."""
        if len(vec1) != len(vec2):
            return 0.0
        
        dot_product = sum(a * b for a, b in zip(vec1, vec2))
        norm1 = sum(a * a for a in vec1) ** 0.5
        norm2 = sum(b * b for b in vec2) ** 0.5
        
        if norm1 == 0 or norm2 == 0:
            return 0.0
        
        return dot_product / (norm1 * norm2)
    
    def add_artifact(self, artifact_id: str) -> bool:
        """Add artifact to latent memory."""
        if self._substrate is None:
            return False
        
        get_method = getattr(self._substrate, 'get_artifact', lambda x: None)
        artifact = get_method(artifact_id)
        
        if artifact is None:
            return False
        
        if not self._is_admissible(artifact):
            return False
        
        organization = self._organize_artifact(artifact)
        latent_vector = self._generate_latent_vector(artifact)
        
        # Record membership with latent vector
        self._membership[artifact_id] = {
            "organization": organization,
        }
        self._latent_vectors[artifact_id] = latent_vector
        
        # Update state
        self._state["is_active"] = True
        self._state["artifact_count"] = len(self._membership)
        
        return True
    
    def remove_artifact(self, artifact_id: str) -> bool:
        """Remove artifact from latent memory."""
        if artifact_id not in self._membership:
            return False
        
        del self._membership[artifact_id]
        if artifact_id in self._latent_vectors:
            del self._latent_vectors[artifact_id]
        
        self._state["artifact_count"] = len(self._membership)
        return True
    
    def get_projection(self) -> Dict[str, Any]:
        """Generate projection from latent memory."""
        artifact_ids = list(self._membership.keys())
        
        # Create clusters based on similarity
        if len(artifact_ids) >= 2:
            self._update_clusters()
        
        cluster_info = [
            {"cluster": c, "count": len(members)}
            for c, members in self._clusters.items()
        ]
        
        return {
            "form_kind": self._kind,
            "name": self._name,
            "visible_artifacts": tuple(artifact_ids),
            "latent_dimension": 10,  # Fixed dimension for simplicity
            "cluster_count": len(self._clusters),
            "organization_type": "latent_semantic",
            "clusters": tuple(c["cluster"] for c in cluster_info),
            "artifact_count": len(artifact_ids),
            "confidence": 1.0 if artifact_ids else 0.5,
            "generated_at_utc": time.time(),
        }
    
    def _update_clusters(self):
        """Update clusters based on current latent vectors."""
        self._clusters = {}
        
        artifact_ids = list(self._latent_vectors.keys())
        if len(artifact_ids) < 2:
            return
        
        # Simple clustering: group by similarity > threshold
        visited = set()
        cluster_id = 0
        
        for aid in artifact_ids:
            if aid in visited:
                continue
            
            vector = self._latent_vectors[aid]
            cluster_key = f"cluster_{cluster_id}"
            self._clusters[cluster_key] = [aid]
            visited.add(aid)
            
            # Find similar artifacts
            for other_id in artifact_ids:
                if other_id == aid or other_id in visited:
                    continue
                
                other_vector = self._latent_vectors[other_id]
                similarity = self._compute_similarity(vector, other_vector)
                
                if similarity > 0.5:  # Threshold
                    self._clusters[cluster_key].append(other_id)
                    visited.add(other_id)
            
            cluster_id += 1
    
    def find_similar(self, artifact_id: str, max_count: int = 5) -> Tuple[str, ...]:
        """Find similar artifacts based on latent vector similarity."""
        if artifact_id not in self._latent_vectors:
            return tuple()
        
        target_vector = self._latent_vectors[artifact_id]
        
        candidates = []
        for other_id, other_vector in self._latent_vectors.items():
            if other_id != artifact_id:
                similarity = self._compute_similarity(target_vector, other_vector)
                candidates.append((other_id, similarity))
        
        # Sort by similarity (descending) and return top results
        candidates.sort(key=lambda x: x[1], reverse=True)
        return tuple(cid for cid, _ in candidates[:max_count])
    
    def health(self) -> Dict[str, Any]:
        """Report form health."""
        return {
            "form_kind": self._kind,
            "name": self._name,
            "is_active": self.is_active,
            "artifact_count": self._state["artifact_count"],
            "latent_dimension": 10,
            "cluster_count": len(self._clusters),
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


__all__ = ["LatentMemory"]