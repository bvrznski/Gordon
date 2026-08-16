# Episodic Memory - Experienced Events and Episodes
# =================================================

"""
Episodic Memory: Preserves experienced events as bounded episodes.

This form organizes artifacts according to:
    - Bounded episode boundaries
    - Event sequences with participants, locations, actions
    - Temporal context and outcomes

Admission Policy:
    - Artifacts representing experienced events
    - Events with clear temporal bounds
    - Multi-part experiences with structure

Activation Triggers:
    - Event recall requests
    - Context similarity matching
    - Temporal proximity cues
"""

from __future__ import annotations

from typing import Dict, Any, Tuple, Optional
import time


class EpisodicMemory:
    """
    Organizes artifacts into experienced episodes.
    
    Each episode is a bounded sequence of related events with:
        - Participants (who was involved)
        - Location (where it happened)
        - Events (what occurred)
        - Actions (what was done)
        - Outcomes (result)
        - Context (when and how)
    """
    
    def __init__(self, name: str, kind: str):
        self._name = name
        self._kind = kind
        self._substrate: Optional[Any] = None
        self._state = {"is_active": False, "artifact_count": 0}
        self._membership: Dict[str, Any] = {}
        self._episodes: list = []
        
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
        """Check if artifact is admissible as an episode event."""
        # Artifacts with event-like content are admissible
        semantic_content = getattr(artifact, 'semantic_content', {})
        tags = getattr(artifact, 'tags', set())
        
        # Event indicators
        event_keywords = {'event', 'happened', 'occurred', 'experience'}
        if any(kw in str(semantic_content).lower() for kw in event_keywords):
            return True
        
        # Check for explicit event tags
        event_tags = {'event', 'episode', 'occurrence'}
        if set(tags) & event_tags:
            return True
        
        return False
    
    def _organize_artifact(self, artifact: Any) -> Dict[str, Any]:
        """Organize artifact within an episode."""
        created_at = getattr(artifact, 'created_at_utc', time.time())
        
        # Determine episode membership based on context
        episode_id = self._assign_episode(artifact)
        
        return {
            "form_kind": self._kind,
            "timestamp_utc": created_at,
            "episode_id": episode_id,
            "admitted_at_utc": time.time(),
        }
    
    def _assign_episode(self, artifact: Any) -> str:
        """Assign artifact to an appropriate episode."""
        # Simple strategy: group by temporal proximity
        timestamp = getattr(artifact, 'created_at_utc', time.time())
        
        for ep_id, (start, end, members) in enumerate(self._episodes):
            if start <= timestamp <= end:
                return f"episode_{ep_id}"
        
        # Create new episode if none found
        new_episode_id = len(self._episodes)
        self._episodes.append((timestamp - 1.0, timestamp + 60.0, []))
        return f"episode_{new_episode_id}"
    
    def add_artifact(self, artifact_id: str) -> bool:
        """Add artifact to episodic memory."""
        if self._substrate is None:
            return False
        
        get_method = getattr(self._substrate, 'get_artifact', lambda x: None)
        artifact = get_method(artifact_id)
        
        if artifact is None:
            return False
        
        if not self._is_admissible(artifact):
            return False
        
        organization = self._organize_artifact(artifact)
        
        # Record membership
        self._membership[artifact_id] = {
            "organization": organization,
        }
        
        # Add to episode members list
        episode_id = organization.get("episode_id", "unknown")
        for i, (start, end, members) in enumerate(self._episodes):
            if f"episode_{i}" == episode_id:
                self._episodes[i] = (start, end, members + [artifact_id])
        
        # Update state
        self._state["is_active"] = True
        self._state["artifact_count"] = len(self._membership)
        
        return True
    
    def remove_artifact(self, artifact_id: str) -> bool:
        """Remove artifact from episodic memory."""
        if artifact_id not in self._membership:
            return False
        
        del self._membership[artifact_id]
        self._state["artifact_count"] = len(self._membership)
        
        return True
    
    def get_projection(self) -> Dict[str, Any]:
        """Generate projection from episodic memory."""
        artifact_ids = list(self._membership.keys())
        episode_info = [{"id": f"episode_{i}", "count": len(members)} 
                       for i, (_, _, members) in enumerate(self._episodes)]
        
        return {
            "form_kind": self._kind,
            "name": self._name,
            "visible_artifacts": tuple(artifact_ids),
            "episode_count": len(self._episodes),
            "organization_type": "event_sequences",
            "clusters": tuple(e["id"] for e in episode_info),
            "artifact_count": len(artifact_ids),
            "confidence": 1.0 if artifact_ids else 0.5,
            "generated_at_utc": time.time(),
        }
    
    def get_episodes(self) -> Tuple[str, ...]:
        """Get all episode IDs."""
        return tuple(f"episode_{i}" for i in range(len(self._episodes)))
    
    def get_artifacts_in_episode(self, episode_id: str) -> Tuple[str, ...]:
        """Get artifacts belonging to a specific episode."""
        try:
            idx = int(episode_id.replace("episode_", ""))
            _, _, members = self._episodes[idx]
            return tuple(members)
        except (ValueError, IndexError):
            return tuple()
    
    def health(self) -> Dict[str, Any]:
        """Report form health."""
        return {
            "form_kind": self._kind,
            "name": self._name,
            "is_active": self.is_active,
            "artifact_count": self._state["artifact_count"],
            "episode_count": len(self._episodes),
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


__all__ = ["EpisodicMemory"]