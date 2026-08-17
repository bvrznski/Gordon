# Knowledge Assertions - Compound Assertion Contract - Phase 6.4
# ================================================================

"""
Compound Assertions: Multiple assertions composed into one semantic structure.

Compound Assertions preserve the identities of their component assertions while
forming a higher-level semantic structure.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Tuple, Optional, Any
from enum import Enum, auto
import time
import uuid


# =============================================================================
# LOGICAL STRUCTURE KINDS
# =============================================================================


class LogicalStructureKind(Enum):
    """Kinds of logical structures in compound assertions."""
    
    CONJUNCTIVE = "conjunctive"   # All components must be true (AND)
    DISJUNCTIVE = "disjunctive"   # At least one component must be true (OR)
    NEGATIVE = "negative"         # Component is false (NOT)
    IMPLICATIVE = "implicative"   # Antecedent implies consequent
    BICONDITIONAL = "biconditional"  # Equivalence (IFF)


# =============================================================================
# COMPOUND ASSERTION
# =============================================================================


@dataclass(frozen=True)
class CompoundAssertion:
    """
    Multiple Assertions composing one semantic structure.
    
    Compound Assertions preserve component identities. They form complex
    propositions from simpler ones while maintaining traceability.
    
    Fields:
        compound_identity:       Unique identifier for this compound assertion
        component_assertions:    List of component assertion IDs
        logical_structure:       The logical operator connecting components
        evaluation_strategy:     How to evaluate the compound (all, any, etc.)
        provenance:              Origin tracking information
    
    CONTRACT REQUIREMENTS:
        LOGIC-LAW-001: Logical operators shall remain explicit.
        LOGIC-LAW-003: Compound Assertions shall preserve participating Assertions.
        ASSERTION-LAW-004: Provenance preserved
        ASSERTION-LAW-007: Deterministic behavior
    """
    
    compound_identity: str
    component_assertions: Tuple[str, ...]
    logical_structure: LogicalStructureKind = LogicalStructureKind.CONJUNCTIVE
    evaluation_strategy: str = "all"  # all, any, ordered, weighted
    provenance: Dict[str, Any] = field(default_factory=dict)

    @property
    def is_conjunctive(self) -> bool:
        """Check if compound is conjunctive (AND)."""
        return self.logical_structure == LogicalStructureKind.CONJUNCTIVE

    @property
    def is_disjunctive(self) -> bool:
        """Check if compound is disjunctive (OR)."""
        return self.logical_structure == LogicalStructureKind.DISJUNCTIVE

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for deterministic serialization."""
        return {
            "compound_identity": self.compound_identity,
            "component_assertions": list(self.component_assertions),
            "logical_structure": self.logical_structure.value,
            "evaluation_strategy": self.evaluation_strategy,
            "provenance": dict(self.provenance),
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> CompoundAssertion:
        """Create from dictionary (deterministic)."""
        return cls(
            compound_identity=data.get("compound_identity", ""),
            component_assertions=tuple(data.get("component_assertions", [])),
            logical_structure=LogicalStructureKind(data.get("logical_structure", "conjunctive")),
            evaluation_strategy=data.get("evaluation_strategy", "all"),
            provenance=dict(data.get("provenance", {})),
        )

    @classmethod
    def and_compound(cls, *assertion_ids: str) -> CompoundAssertion:
        """Create a conjunctive (AND) compound assertion."""
        return cls(
            compound_identity=f"compound:{uuid.uuid4().hex[:16]}",
            component_assertions=assertion_ids,
            logical_structure=LogicalStructureKind.CONJUNCTIVE,
            evaluation_strategy="all",
            provenance={"created_at_utc": time.time()},
        )

    @classmethod
    def or_compound(cls, *assertion_ids: str) -> CompoundAssertion:
        """Create a disjunctive (OR) compound assertion."""
        return cls(
            compound_identity=f"compound:{uuid.uuid4().hex[:16]}",
            component_assertions=assertion_ids,
            logical_structure=LogicalStructureKind.DISJUNCTIVE,
            evaluation_strategy="any",
            provenance={"created_at_utc": time.time()},
        )

    @classmethod
    def not_compound(cls, assertion_id: str) -> CompoundAssertion:
        """Create a negative (NOT) compound assertion."""
        return cls(
            compound_identity=f"compound:{uuid.uuid4().hex[:16]}",
            component_assertions=(assertion_id,),
            logical_structure=LogicalStructureKind.NEGATIVE,
            evaluation_strategy="none",
            provenance={"created_at_utc": time.time()},
        )

    @classmethod
    def implies_compound(cls, antecedent: str, consequent: str) -> CompoundAssertion:
        """Create an implicative (IF...THEN) compound assertion."""
        return cls(
            compound_identity=f"compound:{uuid.uuid4().hex[:16]}",
            component_assertions=(antecedent, consequent),
            logical_structure=LogicalStructureKind.IMPLICATIVE,
            evaluation_strategy="ordered",
            provenance={"created_at_utc": time.time()},
        )

    def add_component(self, assertion_id: str) -> CompoundAssertion:
        """Add a new component to this compound assertion."""
        return CompoundAssertion(
            compound_identity=self.compound_identity,
            component_assertions=self.component_assertions + (assertion_id,),
            logical_structure=self.logical_structure,
            evaluation_strategy=self.evaluation_strategy,
            provenance={
                **self.provenance,
                "component_added_at_utc": time.time(),
                "new_component": assertion_id,
            },
        )

    def remove_component(self, assertion_id: str) -> CompoundAssertion:
        """Remove a component from this compound assertion."""
        new_components = tuple(c for c in self.component_assertions if c != assertion_id)
        return CompoundAssertion(
            compound_identity=self.compound_identity,
            component_assertions=new_components,
            logical_structure=self.logical_structure,
            evaluation_strategy=self.evaluation_strategy,
            provenance={
                **self.provenance,
                "component_removed_at_utc": time.time(),
                "removed_component": assertion_id,
            },
        )

    def negate(self) -> CompoundAssertion:
        """Create a negated version of this compound assertion."""
        return CompoundAssertion(
            compound_identity=f"compound:{uuid.uuid4().hex[:16]}",
            component_assertions=(self.compound_identity,),
            logical_structure=LogicalStructureKind.NEGATIVE,
            evaluation_strategy="none",
            provenance={
                **self.provenance,
                "negated_at_utc": time.time(),
            },
        )