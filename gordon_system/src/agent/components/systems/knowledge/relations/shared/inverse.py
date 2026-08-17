# Knowledge Inverse Relations - Phase 6.5
# ======================================

"""
Inverse Relations: Reverse direction relations for semantic symmetry.

Every relation may have an inverse:
    PART_OF   <-> CONTAINS
    USES      <-> USED_BY
    OWNS      <-> OWNED_BY
    CAUSES    <-> CAUSED_BY
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Tuple, Optional, Any
from enum import Enum, auto
import time
import uuid


# =============================================================================
# INVERSE RELATION MAPPINGS - Forward -> Inverse mappings
# =============================================================================


INVERSE_RELATIONS: Dict[str, str] = {
    "part_of": "contains",
    "contains": "part_of",
    "uses": "used_by",
    "used_by": "uses",
    "depends_on": "dependency_of",
    "dependency_of": "depends_on",
    "causes": "caused_by",
    "caused_by": "causes",
    "precedes": "follows",
    "follows": "precedes",
    "before": "after",
    "after": "before",
    "left_of": "right_of",
    "right_of": "left_of",
    "above": "below",
    "below": "above",
    "inside": "outside",
    "outside": "inside",
    "is_a": "instance_of",
    "instance_of": "is_a",
}


# =============================================================================
# INVERSE RELATION - Canonical inverse definition
# =============================================================================


@dataclass(frozen=True)
class InverseRelation:
    """
    Definition of an inverse relation pair.
    
    Fields:
        inverse_identity:     Unique identifier for this inverse definition
        forward_relation:     The forward direction relation ID
        inverse_relation:     The inverse direction relation ID
        equivalence_constraints: Constraints that must hold between endpoints
        provenance:           Origin tracking records
    """
    
    inverse_identity: str                  # Unique ID for this inverse pair
    forward_relation: str                   # Forward relation identity
    inverse_relation: str                   # Inverse relation identity
    
    equivalence_constraints: Tuple[str, ...] = field(default_factory=tuple)
    
    provenance: Tuple[Dict[str, Any], ...] = field(default_factory=tuple)
    
    @property
    def is_valid(self) -> bool:
        return (
            len(self.inverse_identity) > 0 and
            len(self.forward_relation) > 0 and
            len(self.inverse_relation) > 0
        )
    
    @classmethod
    def create(
        cls,
        forward_kind: str,
        inverse_kind: Optional[str] = None,
        constraints: Optional[List[str]] = None,
        provenance_context: Optional[Dict[str, Any]] = None,
    ) -> "InverseRelation":
        initial_provenance = (
            {
                "provenance_identity": f"inverse-prov:{uuid.uuid4().hex[:16]}",
                "originating_request": provenance_context.get("request", "") if provenance_context else "",
                "originating_system": provenance_context.get("system", "unknown") if provenance_context else "unknown",
                "forward_relation": forward_kind,
                "inverse_relation": inverse_kind or INVERSE_RELATIONS.get(forward_kind, f"inverse_of_{forward_kind}"),
                "timestamp_utc": time.time(),
            },
        )
        
        return cls(
            inverse_identity=f"inverse:{uuid.uuid4().hex[:16]}",
            forward_relation=forward_kind,
            inverse_relation=inverse_kind or INVERSE_RELATIONS.get(forward_kind, f"inverse_of_{forward_kind}"),
            equivalence_constraints=tuple(constraints or []),
            provenance=initial_provenance,
        )
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "inverse_identity": self.inverse_identity,
            "forward_relation": self.forward_relation,
            "inverse_relation": self.inverse_relation,
            "equivalence_constraints": list(self.equivalence_constraints),
            "provenance": [p for p in self.provenance],
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "InverseRelation":
        provenance = []
        for p_data in data.get("provenance", []):
            if isinstance(p_data, dict):
                provenance.append(p_data)
        
        return cls(
            inverse_identity=data.get("inverse_identity", str(uuid.uuid4())),
            forward_relation=data.get("forward_relation", ""),
            inverse_relation=data.get("inverse_relation", ""),
            equivalence_constraints=tuple(data.get("equivalence_constraints", [])),
            provenance=tuple(provenance),
        )
    
    def get_inverse(self, relation_kind: str) -> Optional[str]:
        """Get the inverse of a given relation kind."""
        if relation_kind == self.forward_relation:
            return self.inverse_relation
        elif relation_kind == self.inverse_relation:
            return self.forward_relation
        return None


__all__ = [
    "INVERSE_RELATIONS",
    "InverseRelation",
]