# Knowledge Relation Governance - Phase 6.5
# =========================================

"""
Relation Governance: Quality assurance and consistency checks for Relations.

Governance evaluates:
    - Duplicate relations
    - Inconsistent directionality
    - Broken inverses
    - Constraint violations
    - Orphan relations
    - Cyclic hierarchies
    - Redundant relations

Governance remains observational - it does not modify Relations directly.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Tuple, Optional, Any, Set
from enum import Enum, auto
import time
import uuid


class GovernanceKind(Enum):
    """Types of governance checks that can be performed."""
    DUPLICATE_DETECTION = "duplicate"
    DIRECTIONALITY_CHECK = "directionality"
    INVERSE_VALIDATION = "inverse_validation"
    CONSTRAINT_VIOLATION = "constraint_violation"
    ORPHAN_DETECTION = "orphan_detection"
    CYCLE_DETECTION = "cycle_detection"
    REDUNDANCY_DETECTION = "redundancy"


@dataclass(frozen=True)
class RelationGovernance:
    """
    Governance evaluation for Relations.
    
    Fields:
        governance_identity:    Unique identifier for this governance evaluation
        evaluated_relations:    IDs of relations that were evaluated
        findings:               List of findings from the evaluation
        violations:             List of constraint violations detected
        recommendations:        Actionable recommendations based on findings
        provenance:             Origin tracking records
    """
    
    governance_identity: str
    evaluated_relations: Tuple[str, ...] = field(default_factory=tuple)
    
    findings: Tuple[Dict[str, Any], ...] = field(default_factory=tuple)
    violations: Tuple[Dict[str, Any], ...] = field(default_factory=tuple)
    recommendations: Tuple[str, ...] = field(default_factory=tuple)
    
    provenance: Tuple[Dict[str, Any], ...] = field(default_factory=tuple)
    
    @property
    def is_valid(self) -> bool:
        return len(self.governance_identity) > 0
    
    @classmethod
    def create(
        cls,
        relation_ids: List[str],
        findings: Optional[List[Dict[str, Any]]] = None,
        violations: Optional[List[Dict[str, Any]]] = None,
        recommendations: Optional[List[str]] = None,
        provenance_context: Optional[Dict[str, Any]] = None,
    ) -> "RelationGovernance":
        initial_provenance = (
            {
                "provenance_identity": f"governance-prov:{uuid.uuid4().hex[:16]}",
                "originating_request": provenance_context.get("request", "") if provenance_context else "",
                "originating_system": provenance_context.get("system", "unknown") if provenance_context else "unknown",
                "evaluated_count": len(relation_ids),
                "findings_count": len(findings or []),
                "violations_count": len(violations or []),
                "timestamp_utc": time.time(),
            },
        )
        
        return cls(
            governance_identity=f"governance:{uuid.uuid4().hex[:16]}",
            evaluated_relations=tuple(relation_ids),
            findings=tuple(findings or []),
            violations=tuple(violations or []),
            recommendations=tuple(recommendations or []),
            provenance=initial_provenance,
        )
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "governance_identity": self.governance_identity,
            "evaluated_relations": list(self.evaluated_relations),
            "findings": [f for f in self.findings],
            "violations": [v for v in self.violations],
            "recommendations": list(self.recommendations),
            "provenance": [p for p in self.provenance],
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "RelationGovernance":
        provenance = []
        for p_data in data.get("provenance", []):
            if isinstance(p_data, dict):
                provenance.append(p_data)
        
        return cls(
            governance_identity=data.get("governance_identity", str(uuid.uuid4())),
            evaluated_relations=tuple(data.get("evaluated_relations", [])),
            findings=tuple(data.get("findings", [])),
            violations=tuple(data.get("violations", [])),
            recommendations=tuple(data.get("recommendations", [])),
            provenance=tuple(provenance),
        )


def detect_duplicates(relations: List[Dict[str, Any]]) -> Tuple[Dict[str, Any], ...]:
    """Detect duplicate relations based on source-target-kind."""
    seen = {}
    duplicates = []
    
    for rel in relations:
        key = (rel.get("source"), rel.get("kind"), rel.get("target"))
        if key in seen:
            duplicates.append({
                "type": "duplicate",
                "relation_id": rel.get("identity"),
                "original_id": seen[key],
                "key": key,
            })
        else:
            seen[key] = rel.get("identity")
    
    return tuple(duplicates)


def detect_cycles(relations: List[Tuple[str, str, str]]) -> Tuple[Dict[str, Any], ...]:
    """Detect cyclic relations in the graph."""
    # Build adjacency list
    adj: Dict[str, List[str]] = {}
    for s, kind, t in relations:
        if s not in adj:
            adj[s] = []
        adj[s].append(t)
    
    visited = set()
    rec_stack = set()
    cycles = []
    
    def dfs(node: str, path: List[str]) -> None:
        if node in rec_stack:
            # Found a cycle
            cycle_start = path.index(node)
            cycles.append({
                "type": "cycle",
                "nodes": path[cycle_start:] + [node],
                "length": len(path) - cycle_start,
            })
            return
        
        if node in visited:
            return
        
        visited.add(node)
        rec_stack.add(node)
        path.append(node)
        
        for neighbor in adj.get(node, []):
            dfs(neighbor, path.copy())
        
        rec_stack.remove(node)
    
    for node in adj:
        dfs(node, [])
    
    return tuple(cycles)


__all__ = [
    "GovernanceKind",
    "RelationGovernance",
    "detect_duplicates",
    "detect_cycles",
]