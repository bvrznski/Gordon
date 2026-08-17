# Knowledge Relation Algebra - Phase 6.5
# =====================================

"""
Relation Algebra: Operations on Relations.

Relations may participate in algebraic operations including:
    - Composition: Combining relations to form new ones
    - Inversion: Reversing the direction of a relation
    - Projection: Extracting subsets of relations
    - Intersection: Finding common relations between sets
    - Union: Combining relations from multiple sets
    - Difference: Finding unique relations in one set
    - Closure: Computing transitive closures

Relation algebra remains explicit and rule-based.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Tuple, Optional, Any, Set
from enum import Enum, auto
import time
import uuid


# =============================================================================
# RELATION ALGEBRA OPERATIONS - Supported operations
# =============================================================================


class RelationAlgebraOperation(Enum):
    """
    Algebraic operations that can be performed on Relations.
    
    Defines the available set and relational algebra operations:
        COMPOSITION   -> Combine two relations into one
        INVERSION     -> Reverse the direction of a relation
        PROJECTION    -> Extract subset based on criteria
        INTERSECTION  -> Find common elements between sets
        UNION         -> Combine all elements from both sets
        DIFFERENCE    -> Find elements unique to first set
        CLOSURE       -> Compute transitive closure
        COMPLEMENT    -> Find relations not in the set
    """
    
    COMPOSITION = "composition"
    INVERSION = "inversion"
    PROJECTION = "projection"
    INTERSECTION = "intersection"
    UNION = "union"
    DIFFERENCE = "difference"
    CLOSURE = "closure"
    COMPLEMENT = "complement"


# =============================================================================
# RELATION ALGEBRA - Canonical algebra expression
# =============================================================================


@dataclass(frozen=True)
class RelationAlgebra:
    """
    Algebraic expression for operations on Relations.
    
    Represents a single algebra operation with its inputs and outputs.
    Every algebra expression has:
        - Unique identity
        - Operation type
        - Participating relations (inputs)
        - Resulting relation(s) (outputs)
        - Information loss metrics (if applicable)
        - Provenance tracking
    
    Fields:
        algebra_identity:       Unique identifier for this algebra operation
        participating_relations: IDs of relations involved in the operation
        operation:              Type of algebraic operation
        resulting_relation:     Result relation ID(s) from the operation
        information_loss:       Metrics about any information lost during operation
        constraints_applied:    Constraints that were applied
        provenance:             Origin tracking records
    """
    
    # Identity and metadata (required)
    algebra_identity: str                   # Unique ID for this algebra op
    
    # Operation definition (required)
    participating_relations: Tuple[str, ...]  # Input relations
    operation: RelationAlgebraOperation       # Type of operation
    
    # Result tracking (optional with defaults)
    resulting_relation: Optional[str] = None  # Output relation(s)
    
    # Quality metrics
    information_loss: Dict[str, Any] = field(default_factory=dict)
    constraints_applied: Tuple[str, ...] = field(default_factory=tuple)
    
    # Provenance
    provenance: Tuple[Dict[str, Any], ...] = field(default_factory=tuple)
    
    @property
    def is_valid(self) -> bool:
        """Check if algebra expression has valid foundational data."""
        return (
            len(self.algebra_identity) > 0 and
            self.operation is not None and
            len(self.participating_relations) > 0
        )
    
    @classmethod
    def create(
        cls,
        operation: RelationAlgebraOperation,
        relation_ids: List[str],
        resulting_relation_id: Optional[str] = None,
        information_loss: Optional[Dict[str, Any]] = None,
        constraints: Optional[List[str]] = None,
        provenance_context: Optional[Dict[str, Any]] = None,
    ) -> "RelationAlgebra":
        """
        Create a new relation algebra expression.
        
        Args:
            operation: Type of algebraic operation
            relation_ids: IDs of relations involved in the operation
            resulting_relation_id: ID of the result (optional)
            information_loss: Metrics about information loss (optional)
            constraints: Constraints applied during operation (optional)
            provenance_context: Initial provenance context (optional)
            
        Returns:
            New RelationAlgebra instance
        """
        initial_provenance = (
            {
                "provenance_identity": f"algebra-prov:{uuid.uuid4().hex[:16]}",
                "originating_request": provenance_context.get("request", "") if provenance_context else "",
                "originating_system": provenance_context.get("system", "unknown") if provenance_context else "unknown",
                "operation": operation.value,
                "input_relations_count": len(relation_ids),
                "timestamp_utc": time.time(),
            },
        )
        
        return cls(
            algebra_identity=f"algebra:{uuid.uuid4().hex[:16]}",
            participating_relations=tuple(relation_ids),
            operation=operation,
            resulting_relation=resulting_relation_id,
            information_loss=information_loss or {},
            constraints_applied=tuple(constraints or []),
            provenance=initial_provenance,
        )
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert algebra expression to dictionary for serialization."""
        return {
            "algebra_identity": self.algebra_identity,
            "participating_relations": list(self.participating_relations),
            "operation": self.operation.value,
            "resulting_relation": self.resulting_relation,
            "information_loss": dict(self.information_loss),
            "constraints_applied": list(self.constraints_applied),
            "provenance": [p for p in self.provenance],
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "RelationAlgebra":
        """Create algebra expression from dictionary."""
        provenance = []
        for p_data in data.get("provenance", []):
            if isinstance(p_data, dict):
                provenance.append(p_data)
        
        try:
            operation = RelationAlgebraOperation(data.get("operation", "unknown"))
        except ValueError:
            operation = RelationAlgebraOperation.COMPOSITION
        
        return cls(
            algebra_identity=data.get("algebra_identity", str(uuid.uuid4())),
            participating_relations=tuple(data.get("participating_relations", [])),
            operation=operation,
            resulting_relation=data.get("resulting_relation"),
            information_loss=dict(data.get("information_loss", {})),
            constraints_applied=tuple(data.get("constraints_applied", [])),
            provenance=tuple(provenance),
        )


# =============================================================================
# COMPOSITION RULES - Rules for combining relations
# =============================================================================


class CompositionRule(Enum):
    """
    Rules for relation composition operations.
    
    Defines how two relations may be combined:
        TRANSITIVE_COMPOSE -> A R B, B R C => A R C (transitive)
        CHAIN_COMPOSE      -> A R B, B S C => A T C (different relations)
        CONJUNCTIVE_COMPOSE-> A R B, A S B => A (R AND S) B
        DISJUNCTIVE_COMPOSE-> A R B OR A S B => A (R OR S) B
    """
    
    TRANSITIVE_COMPOSE = "transitive"
    CHAIN_COMPOSE = "chain"
    CONJUNCTIVE_COMPOSE = "conjunctive"
    DISJUNCTIVE_COMPOSE = "disjunctive"


@dataclass(frozen=True)
class RelationCompositionRule:
    """
    Rule for composing two relations.
    
    Fields:
        rule_identity:       Unique identifier for this rule
        input_relation_1:    First relation's identity
        input_relation_2:    Second relation's identity
        composition_rule:    Type of composition to apply
        output_relation:     Resulting relation type
        preconditions:       Required conditions for application
        postconditions:      Guaranteed outcomes after application
    """
    
    rule_identity: str                    # Unique ID for this rule
    input_relation_1: str                 # First relation identity
    input_relation_2: str                 # Second relation identity
    
    composition_rule: CompositionRule     # How to compose them
    output_relation_kind: Optional[str]   # Resulting relation type (if applicable)
    
    preconditions: Tuple[str, ...] = field(default_factory=tuple)
    postconditions: Tuple[str, ...] = field(default_factory=tuple)


# =============================================================================
# ALGEBRA OPERATIONS - Convenience functions for common operations
# =============================================================================


def compose_relations(
    relations: List[Tuple[str, str, str]],  # [(source, relation_kind, target), ...]
) -> Optional[Tuple[str, str, str]]:
    """
    Attempt to compose a set of relations.
    
    For transitive composition:
        (A, R, B) and (B, R, C) => (A, R, C)
    
    Args:
        relations: List of (source, relation_kind, target) tuples
        
    Returns:
        Composed relation if possible, None otherwise
    """
    if len(relations) < 2:
        return None
    
    # Look for adjacent relations that can be composed
    for i in range(len(relations)):
        for j in range(i + 1, len(relations)):
            source1, kind1, target1 = relations[i]
            source2, kind2, target2 = relations[j]
            
            # Check if they can be composed (target1 == source2)
            if target1 == source2 and kind1 == kind2:
                return (source1, kind1, target2)
    
    return None


def invert_relation(
    relation: Tuple[str, str, str],  # (source, relation_kind, target)
) -> Tuple[str, str, str]:
    """
    Invert a relation by swapping source and target.
    
    Args:
        relation: (source, relation_kind, target) tuple
        
    Returns:
        Inverted (target, relation_kind_inverse, source) tuple
    """
    source, kind, target = relation
    
    # Simple inverse mapping
    inverse_kinds = {
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
    }
    
    inverse_kind = inverse_kinds.get(kind, kind)
    
    return (target, inverse_kind, source)


def compute_closure(
    relations: List[Tuple[str, str, str]],  # [(source, relation_kind, target), ...]
    transitive_kinds: Optional[Set[str]] = None,
) -> List[Tuple[str, str, str]]:
    """
    Compute the transitive closure of a set of relations.
    
    Args:
        relations: List of (source, relation_kind, target) tuples
        transitive_kinds: Set of relation kinds that are transitive (optional)
        
    Returns:
        Original relations plus all inferred transitive relations
    """
    if transitive_kinds is None:
        transitive_kinds = {"part_of", "is_a", "ancester_of"}
    
    result = list(relations)
    added = True
    
    while added:
        added = False
        new_relations = []
        
        for r1 in result:
            for r2 in result:
                source1, kind1, target1 = r1
                source2, kind2, target2 = r2
                
                # Check if they can be composed
                if (target1 == source2 and 
                    kind1 == kind2 and 
                    kind1 in transitive_kinds):
                    
                    new_rel = (source1, kind1, target2)
                    if new_rel not in result:
                        new_relations.append(new_rel)
        
        result.extend(new_relations)
        added = len(new_relations) > 0
    
    return result


__all__ = [
    # Algebra operation types
    "RelationAlgebraOperation",
    # Composition rule types
    "CompositionRule",
    # Main classes
    "RelationAlgebra",
    "RelationCompositionRule",
    # Convenience functions
    "compose_relations",
    "invert_relation",
    "compute_closure",
]