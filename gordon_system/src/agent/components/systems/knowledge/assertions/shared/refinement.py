# Knowledge Assertions - Refinement Contract - Phase 6.4
# ========================================================

"""
Assertion Refinement: Evolution of assertions through predicate, condition,
scope, quantifier, and evidence refinement.

Identity remains stable during refinement as required.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Tuple, Optional, Any
from enum import Enum, auto
import time
import uuid


# =============================================================================
# REFINEMENT KINDS
# =============================================================================


class RefinementKind(Enum):
    """Kinds of assertion refinements."""
    
    PREDICATE = "predicate"       # Predicate refinement
    CONDITION = "condition"       # Condition refinement  
    SCOPE = "scope"               # Scope refinement
    QUANTIFIER = "quantifier"     # Quantifier refinement
    EVIDENCE = "evidence"         # Evidence refinement
    WORDING = "wording"           # Wording/clarification refinement


# =============================================================================
# ASSERTION REFINEMENT
# =============================================================================


@dataclass(frozen=True)
class AssertionRefinement:
    """
    Refinement of an assertion through revision.
    
    Refinements preserve the Semantic Identity while evolving the assertion.
    
    Fields:
        refinement_identity:  Unique identifier for this refinement record
        assertion:            The assertion being refined (reference to ID)
        previous_revision:    Previous revision state
        refined_revision:     New/updated revision state
        refinement_reason:    Why this refinement was made
        provenance:           Origin tracking information
    
    CONTRACT REQUIREMENTS:
        REVISION-LAW-001: Assertion revisions preserve Semantic Identity.
        REVISION-LAW-002: Historical revisions remain immutable.
        REVISION-LAW-003: Revision reasons remain explicit.
        REVISION-LAW-004: Revision provenance remains complete.
        REVISION-LAW-005: Superseded Assertions remain reconstructable.
        REVISION-LAW-006: Revision compatibility remains explicit.
        REVISION-LAW-007: Revision history remains inspectable.
        REVISION-LAW-008: Equivalent revision contexts behave deterministically.
    """
    
    refinement_identity: str
    assertion: str  # Reference to assertion being refined
    previous_revision: Dict[str, Any] = field(default_factory=dict)
    refined_revision: Dict[str, Any] = field(default_factory=dict)
    refinement_kind: RefinementKind = RefinementKind.WORDING
    refinement_reason: str = ""
    provenance: Dict[str, Any] = field(default_factory=dict)

    @property
    def is_predicate_refinement(self) -> bool:
        """Check if this is a predicate refinement."""
        return self.refinement_kind == RefinementKind.PREDICATE

    @property
    def is_condition_refinement(self) -> bool:
        """Check if this is a condition refinement."""
        return self.refinement_kind == RefinementKind.CONDITION

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for deterministic serialization."""
        return {
            "refinement_identity": self.refinement_identity,
            "assertion": self.assertion,
            "previous_revision": dict(self.previous_revision),
            "refined_revision": dict(self.refined_revision),
            "refinement_kind": self.refinement_kind.value,
            "refinement_reason": self.refinement_reason,
            "provenance": dict(self.provenance),
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> AssertionRefinement:
        """Create from dictionary (deterministic)."""
        return cls(
            refinement_identity=data.get("refinement_identity", ""),
            assertion=data.get("assertion", ""),
            previous_revision=dict(data.get("previous_revision", {})),
            refined_revision=dict(data.get("refined_revision", {})),
            refinement_kind=RefinementKind(data.get("refinement_kind", "wording")),
            refinement_reason=data.get("refinement_reason", ""),
            provenance=dict(data.get("provenance", {})),
        )

    @classmethod
    def predicate_refinement(
        cls,
        assertion_id: str,
        previous_predicate: str,
        refined_predicate: str,
        reason: str = "",
    ) -> AssertionRefinement:
        """Create a predicate refinement."""
        return cls(
            refinement_identity=f"refinement:{uuid.uuid4().hex[:16]}",
            assertion=assertion_id,
            previous_revision={"predicate": previous_predicate},
            refined_revision={"predicate": refined_predicate},
            refinement_kind=RefinementKind.PREDICATE,
            refinement_reason=reason or f"Changed predicate from '{previous_predicate}' to '{refined_predicate}'",
            provenance={
                "created_at_utc": time.time(),
                "kind": "predicate",
            },
        )

    @classmethod
    def condition_refinement(
        cls,
        assertion_id: str,
        previous_conditions: Tuple[str, ...],
        refined_conditions: Tuple[str, ...],
        reason: str = "",
    ) -> AssertionRefinement:
        """Create a condition refinement."""
        return cls(
            refinement_identity=f"refinement:{uuid.uuid4().hex[:16]}",
            assertion=assertion_id,
            previous_revision={"conditions": list(previous_conditions)},
            refined_revision={"conditions": list(refined_conditions)},
            refinement_kind=RefinementKind.CONDITION,
            refinement_reason=reason or "Updated conditions",
            provenance={
                "created_at_utc": time.time(),
                "kind": "condition",
            },
        )

    @classmethod
    def scope_refinement(
        cls,
        assertion_id: str,
        previous_scope: Tuple[str, ...],
        refined_scope: Tuple[str, ...],
        reason: str = "",
    ) -> AssertionRefinement:
        """Create a scope refinement."""
        return cls(
            refinement_identity=f"refinement:{uuid.uuid4().hex[:16]}",
            assertion=assertion_id,
            previous_revision={"scope": list(previous_scope)},
            refined_revision={"scope": list(refined_scope)},
            refinement_kind=RefinementKind.SCOPE,
            refinement_reason=reason or "Updated scope",
            provenance={
                "created_at_utc": time.time(),
                "kind": "scope",
            },
        )

    @classmethod
    def evidence_refinement(
        cls,
        assertion_id: str,
        previous_evidence: Tuple[str, ...],
        refined_evidence: Tuple[str, ...],
        reason: str = "",
    ) -> AssertionRefinement:
        """Create an evidence refinement."""
        return cls(
            refinement_identity=f"refinement:{uuid.uuid4().hex[:16]}",
            assertion=assertion_id,
            previous_revision={"evidence": list(previous_evidence)},
            refined_revision={"evidence": list(refined_evidence)},
            refinement_kind=RefinementKind.EVIDENCE,
            refinement_reason=reason or "Updated evidence",
            provenance={
                "created_at_utc": time.time(),
                "kind": "evidence",
            },
        )

    @classmethod
    def wording_refinement(
        cls,
        assertion_id: str,
        previous_statement: str,
        refined_statement: str,
        reason: str = "",
    ) -> AssertionRefinement:
        """Create a wording refinement."""
        return cls(
            refinement_identity=f"refinement:{uuid.uuid4().hex[:16]}",
            assertion=assertion_id,
            previous_revision={"statement": previous_statement},
            refined_revision={"statement": refined_statement},
            refinement_kind=RefinementKind.WORDING,
            refinement_reason=reason or f"Clarified statement: '{previous_statement}' -> '{refined_statement}'",
            provenance={
                "created_at_utc": time.time(),
                "kind": "wording",
            },
        )

    def is_earlier_than(self, other: AssertionRefinement) -> bool:
        """Check if this refinement occurred before another."""
        self_time = self.provenance.get("created_at_utc", 0)
        other_time = other.provenance.get("created_at_utc", float("inf"))
        return self_time < other_time

    def merge_with(self, other: AssertionRefinement) -> Optional[AssertionRefinement]:
        """
        Attempt to merge with another refinement.
        
        Returns None if refinements conflict or are incompatible.
        """
        # If refinements target different aspects, they can be combined
        if self.refinement_kind != other.refinement_kind:
            return None  # Different kinds - handle separately

        # Same kind - check if compatible
        if self.previous_revision == other.previous_revision:
            # Can combine refinements on same revision
            return AssertionRefinement(
                refinement_identity=self.refinement_identity,
                assertion=self.assertion,
                previous_revision=dict(self.previous_revision),
                refined_revision=dict(self.refined_revision),
                refinement_kind=self.refinement_kind,
                refinement_reason=f"{self.refinement_reason}; {other.refinement_reason}",
                provenance={
                    **self.provenance,
                    "merged_with": other.refinement_identity,
                    "combined_at_utc": time.time(),
                },
            )

        return None  # Incompatible refinements