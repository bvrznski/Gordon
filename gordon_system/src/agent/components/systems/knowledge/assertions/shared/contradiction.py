# Knowledge Assertions - Contradiction Contract - Phase 6.4
# ===========================================================

"""
Assertion Contradictions: First-class semantic artifacts representing conflicts.

Contradictions preserve both conflicting assertions as required.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Tuple, Optional, Any
from enum import Enum, auto
import time
import uuid


# =============================================================================
# CONTRADICTION KINDS
# =============================================================================


class ContradictionKind(Enum):
    """Kinds of contradictions."""
    
    DIRECT = "direct"           # Direct logical contradiction (P and NOT P)
    SEMANTIC = "semantic"       # Semantic inconsistency
    EVIDENTIAL = "evidential"   # Conflicting evidence sources
    TEMPORAL = "temporal"       # Temporal inconsistency
    SCOPE = "scope"             # Scope violation


# =============================================================================
# ASSERTION CONTRADICTION
# =============================================================================


@dataclass(frozen=True)
class AssertionContradiction:
    """
    Contradiction between two assertions.
    
    Contradictions preserve both conflicting Assertions and never remove them.
    They become first-class semantic artifacts in their own right.
    
    Fields:
        contradiction_identity: Unique identifier for this contradiction
        conflicting_assertions: The pair of conflicting assertion IDs
        contradiction_kind:     Type of contradiction (DIRECT, SEMANTIC, etc.)
        contradiction_scope:    Scope where contradiction applies
        supporting_evidence:    Evidence supporting each side
        provenance:             Origin tracking information
    
    CONTRACT REQUIREMENTS:
        CONTRADICTION-LAW-001: Contradictions shall remain first-class semantic artifacts.
        CONTRADICTION-LAW-002: Contradictions shall never remove Assertions.
        CONTRADICTION-LAW-003: Both conflicting Assertions shall remain preserved.
        CONTRADICTION-LAW-004: Contradiction scope shall remain explicit.
        CONTRADICTION-LAW-005: Supporting evidence for each side shall remain explicit.
        CONTRADICTION-LAW-006: Contradiction provenance shall remain complete.
        CONTRADICTION-LAW-007: Contradictions shall remain independently inspectable.
        CONTRADICTION-LAW-008: Equivalent contradictions are represented identically.
    """
    
    contradiction_identity: str
    conflicting_assertions: Tuple[str, str]  # (assertion_a, assertion_b)
    contradiction_kind: ContradictionKind = ContradictionKind.DIRECT
    contradiction_scope: Tuple[str, ...] = field(default_factory=tuple)
    supporting_evidence: Dict[str, List[str]] = field(default_factory=dict)  # assertion_id -> evidence_ids
    provenance: Dict[str, Any] = field(default_factory=dict)

    @property
    def assertion_a(self) -> str:
        """First conflicting assertion."""
        return self.conflicting_assertions[0]

    @property
    def assertion_b(self) -> str:
        """Second conflicting assertion."""
        return self.conflicting_assertions[1]

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for deterministic serialization."""
        return {
            "contradiction_identity": self.contradiction_identity,
            "conflicting_assertions": list(self.conflicting_assertions),
            "contradiction_kind": self.contradiction_kind.value,
            "contradiction_scope": list(self.contradiction_scope),
            "supporting_evidence": {k: list(v) for k, v in self.supporting_evidence.items()},
            "provenance": dict(self.provenance),
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> AssertionContradiction:
        """Create from dictionary (deterministic)."""
        return cls(
            contradiction_identity=data.get("contradiction_identity", ""),
            conflicting_assertions=tuple(data.get("conflicting_assertions", ["", ""])),
            contradiction_kind=ContradictionKind(data.get("contradiction_kind", "direct")),
            contradiction_scope=tuple(data.get("contradiction_scope", [])),
            supporting_evidence={k: list(v) for k, v in data.get("supporting_evidence", {}).items()},
            provenance=dict(data.get("provenance", {})),
        )

    @classmethod
    def direct_contradiction(
        cls,
        assertion_a: str,
        assertion_b: str,
        scope: Tuple[str, ...] = (),
    ) -> AssertionContradiction:
        """
        Create a direct logical contradiction.
        
        Example: "Sky is blue" and "Sky is not blue"
        """
        return cls(
            contradiction_identity=f"contradiction:{uuid.uuid4().hex[:16]}",
            conflicting_assertions=(assertion_a, assertion_b),
            contradiction_kind=ContradictionKind.DIRECT,
            contradiction_scope=scope,
            provenance={
                "created_at_utc": time.time(),
                "kind": "direct",
            },
        )

    @classmethod
    def semantic_contradiction(
        cls,
        assertion_a: str,
        assertion_b: str,
        scope: Tuple[str, ...] = (),
    ) -> AssertionContradiction:
        """
        Create a semantic contradiction.
        
        Example: "X is a cat" and "X is a dog" (mutually exclusive categories)
        """
        return cls(
            contradiction_identity=f"contradiction:{uuid.uuid4().hex[:16]}",
            conflicting_assertions=(assertion_a, assertion_b),
            contradiction_kind=ContradictionKind.SEMANTIC,
            contradiction_scope=scope,
            provenance={
                "created_at_utc": time.time(),
                "kind": "semantic",
            },
        )

    @classmethod
    def evidential_contradiction(
        cls,
        assertion_a: str,
        evidence_a: Tuple[str, ...],
        assertion_b: str,
        evidence_b: Tuple[str, ...],
        scope: Tuple[str, ...] = (),
    ) -> AssertionContradiction:
        """
        Create an evidential contradiction.
        
        Both assertions may be supported by different evidence.
        """
        return cls(
            contradiction_identity=f"contradiction:{uuid.uuid4().hex[:16]}",
            conflicting_assertions=(assertion_a, assertion_b),
            contradiction_kind=ContradictionKind.EVIDENTIAL,
            contradiction_scope=scope,
            supporting_evidence={
                assertion_a: list(evidence_a),
                assertion_b: list(evidence_b),
            },
            provenance={
                "created_at_utc": time.time(),
                "kind": "evidential",
            },
        )

    def add_supporting(self, assertion_id: str, evidence_ids: Tuple[str, ...]) -> AssertionContradiction:
        """Add supporting evidence for one side of the contradiction."""
        new_evidence = dict(self.supporting_evidence)
        current = new_evidence.get(assertion_id, [])
        new_evidence[assertion_id] = list(set(current + list(evidence_ids)))

        return AssertionContradiction(
            contradiction_identity=self.contradiction_identity,
            conflicting_assertions=self.conflicting_assertions,
            contradiction_kind=self.contradiction_kind,
            contradiction_scope=self.contradiction_scope,
            supporting_evidence=new_evidence,
            provenance={
                **self.provenance,
                "evidence_added_at_utc": time.time(),
                "assertion_id": assertion_id,
                "new_evidence_ids": list(evidence_ids),
            },
        )

    def resolve(self, resolution_reason: str = "") -> AssertionContradiction:
        """
        Mark this contradiction as resolved (without removing assertions).
        
        Returns a new contradiction with resolved status.
        """
        return AssertionContradiction(
            contradiction_identity=self.contradiction_identity,
            conflicting_assertions=self.conflicting_assertions,
            contradiction_kind=ContradictionKind(self.contradiction_kind),
            contradiction_scope=self.contradiction_scope,
            supporting_evidence=dict(self.supporting_evidence),
            provenance={
                **self.provenance,
                "resolved_at_utc": time.time(),
                "resolution_reason": resolution_reason,
            },
        )