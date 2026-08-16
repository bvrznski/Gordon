# Procedural Memory - Skills and Execution Patterns
# ===================================================

"""
Procedural Memory: Organizes retained procedures and skills.

This form organizes artifacts according to:
    - Skills and execution patterns
    - Behavioral routines
    - Compiled procedures
    - Task sequences

Admission Policy:
    - Procedural artifacts (how-to knowledge)
    - Execution experience records
    - Skill mastery data

Activation Triggers:
    - Action preparation
    - Skill execution needs
    - Task decomposition
"""

from __future__ import annotations

from typing import Dict, Any, Tuple
import time


class ProceduralMemory:
    """Organizes procedural knowledge and execution patterns."""
    
    def __init__(self, name: str, kind: str):
        self._name = name
        self._kind = kind
        self._substrate: Any = None
        self._state = {"is_active": False, "artifact_count": 0}
        self._membership: Dict[str, Any] = {}
        self._skills: Dict[str, list] = {}  # skill_id -> artifact_ids
        
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
        """Check if artifact represents procedural knowledge."""
        tags = getattr(artifact, 'tags', set())
        
        # Procedural indicators
        procedural_tags = {'procedure', 'skill', 'how-to', 'execute'}
        if set(tags) & procedural_tags:
            return True
        
        content = str(getattr(artifact, 'semantic_content', {}))
        if any(kw in content.lower() for kw in ['step', 'procedure', 'execute', 'sequence']):
            return True
        
        return False
    
    def _organize_artifact(self, artifact: Any) -> Dict[str, Any]:
        """Organize artifact by procedure/skill."""
        content = getattr(artifact, 'semantic_content', {})
        
        # Extract skill/procedure name
        skill_name = self._extract_skill(content)
        
        return {
            "form_kind": self._kind,
            "skill": skill_name,
            "admitted_at_utc": time.time(),
        }
    
    def _extract_skill(self, content: Dict[str, Any]) -> str:
        """Extract skill/procedure name from content."""
        content_str = str(content).lower()
        
        # Look for procedural patterns
        if 'step' in content_str or 'procedure' in content_str:
            return "general_procedure"
        
        keys = list(content.keys())
        if keys:
            return str(keys[0])[:50]
        
        return "unknown_procedure"
    
    def add_artifact(self, artifact_id: str) -> bool:
        """Add artifact to procedural memory."""
        if self._substrate is None:
            return False
        
        get_method = getattr(self._substrate, 'get_artifact', lambda x: None)
        artifact = get_method(artifact_id)
        
        if artifact is None:
            return False
        
        if not self._is_admissible(artifact):
            return False
        
        organization = self._organize_artifact(artifact)
        skill_name = organization.get("skill", "unknown")
        
        # Record membership
        self._membership[artifact_id] = {
            "organization": organization,
        }
        
        # Add to skill cluster
        if skill_name not in self._skills:
            self._skills[skill_name] = []
        self._skills[skill_name].append(artifact_id)
        
        # Update state
        self._state["is_active"] = True
        self._state["artifact_count"] = len(self._membership)
        
        return True
    
    def remove_artifact(self, artifact_id: str) -> bool:
        """Remove artifact from procedural memory."""
        if artifact_id not in self._membership:
            return False
        
        skill_name = self._membership[artifact_id]["organization"].get("skill")
        del self._membership[artifact_id]
        
        # Remove from skill cluster
        if skill_name and skill_name in self._skills:
            self._skills[skill_name] = [
                aid for aid in self._skills[skill_name] if aid != artifact_id
            ]
        
        self._state["artifact_count"] = len(self._membership)
        return True
    
    def get_projection(self) -> Dict[str, Any]:
        """Generate projection from procedural memory."""
        artifact_ids = list(self._membership.keys())
        
        skill_info = [
            {"skill": s, "count": len(members)}
            for s, members in self._skills.items()
        ]
        
        return {
            "form_kind": self._kind,
            "name": self._name,
            "visible_artifacts": tuple(artifact_ids),
            "skill_count": len(self._skills),
            "organization_type": "procedure_based",
            "clusters": tuple(s["skill"] for s in skill_info),
            "artifact_count": len(artifact_ids),
            "confidence": 1.0 if artifact_ids else 0.5,
            "generated_at_utc": time.time(),
        }
    
    def get_skill_members(self, skill: str) -> Tuple[str, ...]:
        """Get artifacts belonging to a specific skill."""
        return tuple(self._skills.get(skill, []))
    
    def health(self) -> Dict[str, Any]:
        """Report form health."""
        return {
            "form_kind": self._kind,
            "name": self._name,
            "is_active": self.is_active,
            "artifact_count": self._state["artifact_count"],
            "skill_count": len(self._skills),
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


__all__ = ["ProceduralMemory"]