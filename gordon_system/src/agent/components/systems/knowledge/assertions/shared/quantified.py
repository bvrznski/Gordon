# Knowledge Assertions - Quantified Assertion Contract - Phase 6.4
# =================================================================

"""
Quantified Assertions: Assertions with explicit quantifiers.

Quantifiers apply to propositions and remain explicit as per QUANTIFIER-LAW-001.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Tuple, Optional, Any
from enum import Enum, auto
import time
import uuid


# =============================================================================
# QUANTIFIER KINDS
# =============================================================================


class QuantifierKind(Enum):
    """Kinds of quantifiers."""
    
    ALL = "all"              # Universal quantification
    EVERY = "every"          # Universal (emphatic)
    SOME = "some"            # Existential
    NONE = "none"            # Negated existential
    EXACTLY_ONE = "exactly_one"
    AT_LEAST = "at_least"    # At least N
    AT_MOST = "at_most"      # At most N
    BETWEEN = "between"      # Between N and M


# =============================================================================
# QUANTIFIED ASSERTION
# =============================================================================


@dataclass(frozen=True)
class QuantifiedAssertion:
    """
    Assertion with quantifier applied.
    
    Quantifiers remain explicit as required by QUANTIFIER-LAW-001.
    
    Fields:
        quantified_identity:  Unique identifier for this quantified assertion
        base_assertion_id:    ID of the base assertion being quantified
        quantifier:           The quantifier kind (ALL, SOME, etc.)
        quantified_scope:     Scope of quantification (concept IDs)
        provenance:           Origin tracking information
    
    CONTRACT REQUIREMENTS:
        QUANTIFIER-LAW-001: Quantifiers shall remain explicit.
        QUANTIFIER-LAW-002: Quantified scope shall remain explicit.
        QUANTIFIER-LAW-003: Quantifier revisions shall preserve history.
        QUANTIFIER-LAW-004: Quantifier provenance shall remain complete.
        QUANTIFIER-LAW-005: Quantifier interpretation shall remain inspectable.
        QUANTIFIER-LAW-006: Nested quantifiers shall remain representable.
        QUANTIFIER-LAW-007: Quantifier ambiguity shall remain explicit.
        QUANTIFIER-LAW-008: Equivalent quantified Assertions evaluate deterministically.
    """
    
    quantified_identity: str
    base_assertion_id: str
    quantifier_kind: QuantifierKind = QuantifierKind.ALL
    quantified_scope: Tuple[str, ...] = field(default_factory=tuple)
    provenance: Dict[str, Any] = field(default_factory=dict)

    @property
    def is_universal(self) -> bool:
        """Check if this is a universal quantification."""
        return self.quantifier_kind in (QuantifierKind.ALL, QuantifierKind.EVERY)

    @property
    def is_existential(self) -> bool:
        """Check if this is an existential quantification."""
        return self.quantifier_kind == QuantifierKind.SOME

    @property
    def is_negative(self) -> bool:
        """Check if this is a negative quantification."""
        return self.quantifier_kind in (QuantifierKind.NONE,)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for deterministic serialization."""
        return {
            "quantified_identity": self.quantified_identity,
            "base_assertion_id": self.base_assertion_id,
            "quantifier_kind": self.quantifier_kind.value,
            "quantified_scope": list(self.quantified_scope),
            "provenance": dict(self.provenance),
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> QuantifiedAssertion:
        """Create from dictionary (deterministic)."""
        return cls(
            quantified_identity=data.get("quantified_identity", ""),
            base_assertion_id=data.get("base_assertion_id", ""),
            quantifier_kind=QuantifierKind(data.get("quantifier_kind", "all")),
            quantified_scope=tuple(data.get("quantified_scope", [])),
            provenance=dict(data.get("provenance", {})),
        )

    @classmethod
    def all(cls, assertion_id: str, scope: Tuple[str, ...] = ()) -> QuantifiedAssertion:
        """Create a universal (ALL) quantified assertion."""
        return cls(
            quantified_identity=f"quantified:{uuid.uuid4().hex[:16]}",
            base_assertion_id=assertion_id,
            quantifier_kind=QuantifierKind.ALL,
            quantified_scope=scope,
            provenance={"created_at_utc": time.time()},
        )

    @classmethod
    def some(cls, assertion_id: str, scope: Tuple[str, ...] = ()) -> QuantifiedAssertion:
        """Create an existential (SOME) quantified assertion."""
        return cls(
            quantified_identity=f"quantified:{uuid.uuid4().hex[:16]}",
            base_assertion_id=assertion_id,
            quantifier_kind=QuantifierKind.SOME,
            quantified_scope=scope,
            provenance={"created_at_utc": time.time()},
        )

    @classmethod
    def none(cls, assertion_id: str, scope: Tuple[str, ...] = ()) -> QuantifiedAssertion:
        """Create a negative (NONE) quantified assertion."""
        return cls(
            quantified_identity=f"quantified:{uuid.uuid4().hex[:16]}",
            base_assertion_id=assertion_id,
            quantifier_kind=QuantifierKind.NONE,
            quantified_scope=scope,
            provenance={"created_at_utc": time.time()},
        )

    @classmethod
    def at_least(cls, assertion_id: str, n: int) -> QuantifiedAssertion:
        """Create an AT_LEAST N quantified assertion."""
        return cls(
            quantified_identity=f"quantified:{uuid.uuid4().hex[:16]}",
            base_assertion_id=assertion_id,
            quantifier_kind=QuantifierKind.AT_LEAST,
            provenance={
                "created_at_utc": time.time(),
                "value": n,
            },
        )

    @classmethod
    def at_most(cls, assertion_id: str, n: int) -> QuantifiedAssertion:
        """Create an AT_MOST N quantified assertion."""
        return cls(
            quantified_identity=f"quantified:{uuid.uuid4().hex[:16]}",
            base_assertion_id=assertion_id,
            quantifier_kind=QuantifierKind.AT_MOST,
            provenance={
                "created_at_utc": time.time(),
                "value": n,
            },
        )

    @classmethod
    def exactly_one(cls, assertion_id: str) -> QuantifiedAssertion:
        """Create an EXACTLY ONE quantified assertion."""
        return cls(
            quantified_identity=f"quantified:{uuid.uuid4().hex[:16]}",
            base_assertion_id=assertion_id,
            quantifier_kind=QuantifierKind.EXACTLY_ONE,
            provenance={"created_at_utc": time.time()},
        )

    def negate(self) -> QuantifiedAssertion:
        """Create the negation of this quantified assertion."""
        # ALL x P(x) becomes SOME x NOT P(x)
        # SOME x P(x) becomes NONE x P(x)
        if self.quantifier_kind == QuantifierKind.ALL:
            new_quantifier = QuantifierKind.SOME
        elif self.quantifier_kind == QuantifierKind.SOME:
            new_quantifier = QuantifierKind.NONE
        elif self.quantifier_kind == QuantifierKind.NONE:
            new_quantifier = QuantifierKind.ALL
        else:
            new_quantifier = self.quantifier_kind

        return cls(
            quantified_identity=f"quantified:{uuid.uuid4().hex[:16]}",
            base_assertion_id=self.base_assertion_id,
            quantifier_kind=new_quantifier,
            quantified_scope=self.quantified_scope,
            provenance={
                **self.provenance,
                "negated_at_utc": time.time(),
            },
        )