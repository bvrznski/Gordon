# Knowledge Relation Closure - Phase 6.5
# =====================================

"""
Relation Closure: Transitive closure computation for Relations.

Some relations support transitive closure:
    A R B, B R C => A R C (for transitive R)

Closure is derived through inference, never stored as canonical truth
unless explicitly materialized.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Tuple, Optional, Any, Set
from enum import Enum, auto
import time
import uuid


class ClosureKind(Enum):
    """Kinds of transitive closure that may be computed."""
    TRANSITIVE = "transitive"
    REFLEXIVE_TRANSITIVE = "reflexive_transitive"
    SYMMETRIC_TRANSITIVE = "symmetric_transitive"


@dataclass(frozen=True)
class RelationClosure:
    """
    Transitive closure computation for relations.
    
    Fields:
        closure_identity:     Unique identifier for this closure
        root_relation:        The original relation that started the closure
        inferred_relations:   All relations derived through closure
        inference_depth:      Maximum depth of inference chain
        materialized:         Whether this closure was materialized to storage
        provenance:           Origin tracking records
    """
    
    closure_identity: str
    root_relation: str
    
    inferred_relations: Tuple[str, ...] = field(default_factory=tuple)
    inference_depth: int = 1
    
    materialized: bool = False
    
    provenance: Tuple[Dict[str, Any], ...] = field(default_factory=tuple)
    
    @property
    def is_valid(self) -> bool:
        return (
            len(self.closure_identity) > 0 and
            len(self.root_relation) > 0 and
            self.inference_depth >= 1
        )
    
    @classmethod
    def create(
        cls,
        root_relation: str,
        inferred_relations: List[str],
        inference_depth: int = 1,
        materialized: bool = False,
        provenance_context: Optional[Dict[str, Any]] = None,
    ) -> "RelationClosure":
        initial_provenance = (
            {
                "provenance_identity": f"closure-prov:{uuid.uuid4().hex[:16]}",
                "originating_request": provenance_context.get("request", "") if provenance_context else "",
                "originating_system": provenance_context.get("system", "unknown") if provenance_context else "unknown",
                "root_relation": root_relation,
                "inferred_count": len(inferred_relations),
                "depth": inference_depth,
                "materialized": materialized,
                "timestamp_utc": time.time(),
            },
        )
        
        return cls(
            closure_identity=f"closure:{uuid.uuid4().hex[:16]}",
            root_relation=root_relation,
            inferred_relations=tuple(inferred_relations),
            inference_depth=inference_depth,
            materialized=materialized,
            provenance=initial_provenance,
        )
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "closure_identity": self.closure_identity,
            "root_relation": self.root_relation,
            "inferred_relations": list(self.inferred_relations),
            "inference_depth": self.inference_depth,
            "materialized": self.materialized,
            "provenance": [p for p in self.provenance],
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "RelationClosure":
        provenance = []
        for p_data in data.get("provenance", []):
            if isinstance(p_data, dict):
                provenance.append(p_data)
        
        return cls(
            closure_identity=data.get("closure_identity", str(uuid.uuid4())),
            root_relation=data.get("root_relation", ""),
            inferred_relations=tuple(data.get("inferred_relations", [])),
            inference_depth=int(data.get("inference_depth", 1)),
            materialized=bool(data.get("materialized", False)),
            provenance=tuple(provenance),
        )


def compute_transitive_closure(
    relations: List[Tuple[str, str, str]],  # [(source, kind, target), ...]
    transitive_kinds: Set[str],
) -> Tuple[List[Tuple[str, str, str]], int]:
    """
    Compute transitive closure for a set of relations.
    
    Returns:
        (all_relations, max_depth)
    """
    result = list(relations)
    depth = 1
    changed = True
    
    while changed:
        changed = False
        new_rels = []
        
        for r1 in result:
            for r2 in result:
                s1, k1, t1 = r1
                s2, k2, t2 = r2
                
                if (t1 == s2 and 
                    k1 == k2 and 
                    k1 in transitive_kinds):
                    
                    new_rel = (s1, k1, t2)
                    if new_rel not in result:
                        new_rels.append(new_rel)
        
        if new_rels:
            result.extend(new_rels)
            depth += 1
            changed = True
    
    return result, depth


def compute_reflexive_closure(
    relations: List[Tuple[str, str, str]],
    all_entities: Set[str],
) -> List[Tuple[str, str, str]]:
    """Add reflexive relations (A R A) for all entities."""
    result = list(relations)
    
    # Add reflexive self-relations for each entity
    for entity in all_entities:
        rel = (entity, "reflexive", entity)
        if rel not in result:
            result.append(rel)
    
    return result


__all__ = [
    "ClosureKind",
    "RelationClosure",
    "compute_transitive_closure",
    "compute_reflexive_closure",
]