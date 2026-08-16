# Working Memory - Currently Active Cognitive Context
# =====================================================

"""
Working Memory: Exposes currently active cognitive context.

This form organizes artifacts according to:
    - Current activation and accessibility
    - Immediate cognitive relevance
    - Attentional focus
    - Task-relevant information

Admission Policy:
    - Selected artifacts only (not all available)
    - High-activation items
    - Currently attended information
    - Task-relevant data

Activation Characteristics:
    - Continuous, highly dynamic activation
    - Limited capacity (items fade when not attended)
"""

from __future__ import annotations

from typing import Dict, Any, Tuple
import time


class WorkingMemory:
    """Organizes currently active artifacts for immediate cognitive processing."""
    
    def __init__(self, name: str, kind: str):
        self._name = name
        self._kind = kind
        self._substrate: Any = None
        self._state = {"is_active": False, "artifact_count": 0}
        self._membership: Dict[str, Any] = {}
        self._activation: Dict[str, float] = {}  # artifact_id -> activation_level
        
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
        """Working memory can admit any artifact that is currently active."""
        # All artifacts are potentially admissible; activation determines membership
        return True
    
    def _organize_artifact(self, artifact: Any, activation_level: float = 1.0) -> Dict[str, Any]:
        """Organize artifact with its current activation level."""
        return {
            "form_kind": self._kind,
            "activation_level": activation_level,
            "admitted_at_utc": time.time(),
        }
    
    def add_artifact(self, artifact_id: str, activation_level: float = 1.0) -> bool:
        """
        Add artifact to working memory with specified activation.
        
        Args:
            artifact_id: ID of the artifact
            activation_level: Initial activation (0.0-1.0)
        """
        if self._substrate is None:
            return False
        
        get_method = getattr(self._substrate, 'get_artifact', lambda x: None)
        artifact = get_method(artifact_id)
        
        if artifact is None:
            return False
        
        organization = self._organize_artifact(artifact, activation_level)
        
        # Record membership with activation tracking
        self._membership[artifact_id] = {
            "organization": organization,
        }
        self._activation[artifact_id] = activation_level
        
        # Update state
        self._state["is_active"] = True
        self._state["artifact_count"] = len(self._membership)
        
        return True
    
    def remove_artifact(self, artifact_id: str) -> bool:
        """Remove artifact from working memory."""
        if artifact_id not in self._membership:
            return False
        
        del self._membership[artifact_id]
        if artifact_id in self._activation:
            del self._activation[artifact_id]
        
        self._state["artifact_count"] = len(self._membership)
        return True
    
    def update_activation(self, artifact_id: str, new_level: float) -> bool:
        """
        Update activation level for an artifact.
        
        Args:
            artifact_id: The artifact to update
            new_level: New activation (0.0-1.0)
            
        Returns:
            True if updated successfully
        """
        if artifact_id not in self._membership:
            return False
        
        self._activation[artifact_id] = new_level
        self._membership[artifact_id]["organization"]["activation_level"] = new_level
        return True
    
    def decay_activation(self, decay_rate: float = 0.1) -> int:
        """
        Apply temporal decay to all activations.
        
        Args:
            decay_rate: Amount to decrease each activation
            
        Returns:
            Number of artifacts whose activation dropped to zero
        """
        decayed_count = 0
        
        for artifact_id in list(self._activation.keys()):
            current = self._activation.get(artifact_id, 0.0)
            new_level = max(0.0, current - decay_rate)
            self._activation[artifact_id] = new_level
            
            if artifact_id in self._membership:
                self._membership[artifact_id]["organization"]["activation_level"] = new_level
            
            # Remove if fully decayed
            if new_level <= 0.0:
                del self._membership[artifact_id]
                decayed_count += 1
        
        self._state["artifact_count"] = len(self._membership)
        return decayed_count
    
    def get_projection(self) -> Dict[str, Any]:
        """Generate projection from working memory."""
        artifact_ids = list(self._membership.keys())
        
        # Sort by activation level (highest first)
        sorted_by_activation = sorted(
            self._activation.items(),
            key=lambda x: x[1],
            reverse=True
        )[:10]  # Top 10 most active
        
        return {
            "form_kind": self._kind,
            "name": self._name,
            "visible_artifacts": tuple(artifact_ids),
            "active_count": len(sorted_by_activation),
            "organization_type": "activation_based",
            "clusters": (),  # Working memory has no clusters by default
            "artifact_count": len(artifact_ids),
            "confidence": 1.0 if artifact_ids else 0.5,
            "generated_at_utc": time.time(),
        }
    
    def get_active_artifacts(self, min_activation: float = 0.5) -> Tuple[str, ...]:
        """Get artifacts with activation above threshold."""
        return tuple(
            aid for aid, level in self._activation.items()
            if level >= min_activation
        )
    
    def health(self) -> Dict[str, Any]:
        """Report form health."""
        return {
            "form_kind": self._kind,
            "name": self._name,
            "is_active": self.is_active,
            "artifact_count": self._state["artifact_count"],
            "activation_records": len(self._activation),
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


__all__ = ["WorkingMemory"]