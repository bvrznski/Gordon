# Perception Scene - Phase 5.2 Organized Percept Collection
# =========================================================

"""
Perception Scene: A coherent collection of percepts organized across space and time.

A Scene preserves context and relationships between percepts.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Tuple, Optional, Any
import time
import uuid


@dataclass(frozen=True)
class Scene:
    """
    Coherent collection of Percepts organized across space and time.
    
    Scenes preserve context - not merely collections.
    
    Scene Properties:
        identity:         Unique identifier
        timestamp_utc:    When scene was constructed
        contained_percepts: List of percept IDs in this scene
        spatial_organization: Spatial relationships (optional)
        temporal_ordering: Temporal sequence information
        
        confidence:       Confidence in scene interpretation 0.0-1.0
        provenance:       Origin tracking
    """
    
    identity: str                      # Unique identifier
    
    timestamp_utc: float               # When scene was constructed
    
    contained_percepts: Tuple[str, ...] = field(default_factory=tuple)  # Percept IDs
    
    spatial_organization: Optional[Dict[str, Any]] = None  # Spatial relationships
    temporal_ordering: Optional[Tuple[int, ...]] = None    # Order of percepts
    
    confidence: float = 1.0           # Scene interpretation confidence
    uncertainty: float = 0.0          # Known limitations
    
    provenance: Dict[str, Any] = field(default_factory=dict)  # Origin tracking
    
    @property
    def is_valid(self) -> bool:
        """Check if scene has minimal required data."""
        return (
            len(self.identity) > 0 and
            self.timestamp_utc > 0.0
        )
    
    @classmethod
    def from_percepts(
        cls,
        percept_ids: List[str],
        timestamp_utc: Optional[float] = None,
