# Spatial Memory - Spatial Relationships and Navigation
# =======================================================

"""
Spatial Memory: Organizes artifacts by spatial relationships.

This form organizes artifacts according to:
    - Location and geometry
    - Navigation routes
    - Topological relationships
    - Maps and scene structure

Admission Policy:
    - Spatial observations and experiences
    - Map data
    - Location-based records

Activation Triggers:
    - Navigation requests
    - Scene understanding
    - Localization needs
"""

from __future__ import annotations

from typing import Dict, Any, Tuple
import time


class SpatialMemory:
    """Organizes artifacts by spatial relationships and location."""
    
    def __init__(self, name: str, kind: str):
        self._name = name
        self._kind = kind
        self._substrate: Any = None
        self._state = {"is_active": False, "artifact_count": 0}
        self._membership: Dict[str, Any] = {}
        self._locations: Dict[str, list] = {}  # location_id -> artifact_ids
        
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
        """Check if artifact has spatial content."""
        tags = getattr(artifact, 'tags', set())
        
        # Spatial indicators
        spatial_tags = {'location', 'space', 'spatial', 'position'}
        if set(tags) & spatial_tags:
            return True
        
        content = str(getattr(artifact, 'semantic_content', {}))
        if any(kw in content.lower() for kw in ['near', 'far', 'left', 'right', 'above', 'below']):
            return True
        
        # Check for coordinate-like data
        if 'lat' in content.lower() or 'lng' in content.lower():
            return True
        
        return False
    
    def _organize_artifact(self, artifact: Any) -> Dict[str, Any]:
        """Organize artifact by location."""
        content = getattr(artifact, 'semantic_content', {})
        
        # Extract location
        location = self._extract_location(content)
        
        return {
            "form_kind": self._kind,
            "location": location,
            "admitted_at_utc": time.time(),
        }
    
    def _extract_location(self, content: Dict[str, Any]) -> str:
        """Extract location from spatial content."""
        content_str = str(content).lower()
        
        # Look for common location patterns
        if 'location' in content_str:
            return "general_location"
        
        keys = list(content.keys())
        for key in keys:
            if any(c in key.lower() for c in ['lat', 'lng', 'x', 'y', 'z']):
                return "coordinate_based"
        
        return "unknown_location"
    
    def add_artifact(self, artifact_id: str) -> bool:
        """Add artifact to spatial memory."""
        if self._substrate is None:
            return False
        
        get_method = getattr(self._substrate, 'get_artifact', lambda x: None)
        artifact = get_method(artifact_id)
        
        if artifact is None:
            return False
        
        if not self._is_admissible(artifact):
            return False
        
        organization = self._organize_artifact(artifact)
        location = organization.get("location", "unknown")
        
        # Record membership
        self._membership[artifact_id] = {
            "organization": organization,
        }
        
        # Add to location cluster
        if location not in self._locations:
            self._locations[location] = []
        self._locations[location].append(artifact_id)
        
        # Update state
        self._state["is_active"] = True
        self._state["artifact_count"] = len(self._membership)
        
        return True
    
    def remove_artifact(self, artifact_id: str) -> bool:
        """Remove artifact from spatial memory."""
        if artifact_id not in self._membership:
            return False
        
        location = self._membership[artifact_id]["organization"].get("location")
        del self._membership[artifact_id]
        
        # Remove from location cluster
        if location and location in self._locations:
            self._locations[location] = [
                aid for aid in self._locations[location] if aid != artifact_id
            ]
        
        self._state["artifact_count"] = len(self._membership)
        return True
    
    def get_projection(self) -> Dict[str, Any]:
        """Generate projection from spatial memory."""
        artifact_ids = list(self._membership.keys())
        
        location_info = [
            {"location": loc, "count": len(members)}
            for loc, members in self._locations.items()
        ]
        
        return {
            "form_kind": self._kind,
            "name": self._name,
            "visible_artifacts": tuple(artifact_ids),
            "location_count": len(self._locations),
            "organization_type": "spatial_topology",
            "clusters": tuple(l["location"] for l in location_info),
            "artifact_count": len(artifact_ids),
            "confidence": 1.0 if artifact_ids else 0.5,
            "generated_at_utc": time.time(),
        }
    
    def get_location_members(self, location: str) -> Tuple[str, ...]:
        """Get artifacts at a specific location."""
        return tuple(self._locations.get(location, []))
    
    def health(self) -> Dict[str, Any]:
        """Report form health."""
        return {
            "form_kind": self._kind,
            "name": self._name,
            "is_active": self.is_active,
            "artifact_count": self._state["artifact_count"],
            "location_count": len(self._locations),
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


__all__ = ["SpatialMemory"]