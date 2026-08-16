# Emotional Memory - Affective Significance and Valence
# ======================================================

"""
Emotional Memory: Organizes artifacts by affective significance.

This form organizes artifacts according to:
    - Valence (positive/negative)
    - Arousal level
    - Motivational importance
    - Persistent affective associations

Admission Policy:
    - Emotionally significant experiences
    - Artifacts with strong affective tags
    - Events tied to reward/prediction

Activation Triggers:
    - Motivational context
    - Reward prediction
    - Threat assessment
"""

from __future__ import annotations

from typing import Dict, Any, Tuple
import time


class EmotionalMemory:
    """Organizes artifacts by affective significance and emotional valence."""
    
    def __init__(self, name: str, kind: str):
        self._name = name
        self._kind = kind
        self._substrate: Any = None
        self._state = {"is_active": False, "artifact_count": 0}
        self._membership: Dict[str, Any] = {}
        self._affect: Dict[str, Dict[str, float]] = {}  # artifact_id -> {valence, arousal}
        
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
        """Check if artifact has emotional content."""
        tags = getattr(artifact, 'tags', set())
        content = str(getattr(artifact, 'semantic_content', {}))
        
        # Emotional indicators
        emotional_tags = {'emotional', 'affective', 'significant', 'memory'}
        if set(tags) & emotional_tags:
            return True
        
        # Check for affective content
        if any(kw in content.lower() for kw in ['feel', 'emotion', 'valence', 'arousal']):
            return True
        
        return False
    
    def _organize_artifact(
        self,
        artifact: Any,
        valence: float = 0.0,
        arousal: float = 0.5,
    ) -> Dict[str, Any]:
        """Organize artifact with affective coordinates."""
        return {
            "form_kind": self._kind,
            "valence": valence,      # -1.0 (negative) to +1.0 (positive)
            "arousal": arousal,      # 0.0 (calm) to 1.0 (excited)
            "intensity": max(abs(valence), arousal),
            "admitted_at_utc": time.time(),
        }
    
    def add_artifact(
        self,
        artifact_id: str,
        valence: float = 0.0,
        arousal: float = 0.5,
    ) -> bool:
        """
        Add artifact with specified affective values.
        
        Args:
            artifact_id: ID of the artifact
            valence: Emotional valence (-1.0 to +1.0)
            arousal: Arousal level (0.0 to 1.0)
        """
        if self._substrate is None:
            return False
        
        get_method = getattr(self._substrate, 'get_artifact', lambda x: None)
        artifact = get_method(artifact_id)
        
        if artifact is None:
            return False
        
        if not self._is_admissible(artifact):
            return False
        
        organization = self._organize_artifact(artifact, valence, arousal)
        
        # Record membership
        self._membership[artifact_id] = {
            "organization": organization,
        }
        self._affect[artifact_id] = {"valence": valence, "arousal": arousal}
        
        # Update state
        self._state["is_active"] = True
        self._state["artifact_count"] = len(self._membership)
        
        return True
    
    def remove_artifact(self, artifact_id: str) -> bool:
        """Remove artifact from emotional memory."""
        if artifact_id not in self._membership:
            return False
        
        del self._membership[artifact_id]
        if artifact_id in self._affect:
            del self._affect[artifact_id]
        
        self._state["artifact_count"] = len(self._membership)
        return True
    
    def get_projection(self) -> Dict[str, Any]:
        """Generate projection from emotional memory."""
        artifact_ids = list(self._membership.keys())
        
        # Group by valence
        positive = [aid for aid in artifact_ids if self._affect.get(aid, {}).get("valence", 0.0) > 0]
        negative = [aid for aid in artifact_ids if self._affect.get(aid, {}).get("valence", 0.0) < 0]
        
        return {
            "form_kind": self._kind,
            "name": self._name,
            "visible_artifacts": tuple(artifact_ids),
            "positive_count": len(positive),
            "negative_count": len(negative),
            "organization_type": "affective_space",
            "clusters": ("positive", "negative") if (positive and negative) else (),
            "artifact_count": len(artifact_ids),
            "confidence": 1.0 if artifact_ids else 0.5,
            "generated_at_utc": time.time(),
        }
    
    def get_valence(self, artifact_id: str) -> float:
        """Get valence for an artifact."""
        return self._affect.get(artifact_id, {}).get("valence", 0.0)
    
    def get_arousal(self, artifact_id: str) -> float:
        """Get arousal level for an artifact."""
        return self._affect.get(artifact_id, {}).get("arousal", 0.5)
    
    def get_positive_artifacts(self) -> Tuple[str, ...]:
        """Get artifacts with positive valence."""
        return tuple(
            aid for aid in self._membership.keys()
            if self._affect.get(aid, {}).get("valence", 0.0) > 0
        )
    
    def get_negative_artifacts(self) -> Tuple[str, ...]:
        """Get artifacts with negative valence."""
        return tuple(
            aid for aid in self._membership.keys()
            if self._affect.get(aid, {}).get("valence", 0.0) < 0
        )
    
    def health(self) -> Dict[str, Any]:
        """Report form health."""
        return {
            "form_kind": self._kind,
            "name": self._name,
            "is_active": self.is_active,
            "artifact_count": self._state["artifact_count"],
            "affect_records": len(self._affect),
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


__all__ = ["EmotionalMemory"]