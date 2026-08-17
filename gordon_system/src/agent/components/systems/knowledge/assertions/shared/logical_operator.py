# Knowledge Assertions - Logical Operator Contract - Phase 6.4
# ==============================================================

"""
Logical Operators: Explicit semantic operators connecting assertions.

Operators remain explicit and preserve semantic structure as required by:
    LOGIC-LAW-001: Logical operators shall remain explicit.
    LOGIC-LAW-002: Operator precedence shall remain explicit.
    LOGIC-LAW-003: Compound Assertions shall preserve participating Assertions.
    LOGIC-LAW-004: Logical simplification shall preserve semantic equivalence.
    LOGIC-LAW-005: Logical provenance shall remain complete.
    LOGIC-LAW-006: Operator revisions shall preserve lineage.
    LOGIC-LAW-007: Logical evaluation shall remain inspectable.
    LOGIC-LAW-008: Equivalent logical structures shall evaluate deterministically.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Tuple, Optional, Any
from enum import Enum, auto
import time
import uuid


# =============================================================================
# LOGICAL OPERATOR KINDS
# =============================================================================


class LogicalOperatorKind(Enum):
    """Kinds of logical operators."""
    
    AND = "and"
    OR = "or"
    NOT = "not"
    XOR = "xor"
    IMPLIES = "implies"
    IFF = "iff"  # If and only if


# =============================================================================
# LOGICAL OPERATOR
# =============================================================================


@dataclass(frozen=True)
class LogicalOperator:
    """
    Logical operator connecting assertions.
    
    Operators remain explicit and preserve semantic structure. Each operator
    has an identity, kind, participating assertions, and precedence.
    
    Fields:
        operator_identity:       Unique identifier for this operator
        operator_kind:           The kind of logical operator (AND, OR, etc.)
        participating_assertions: Assertion IDs involved in this operator
        precedence:              Operator precedence (higher = binds tighter)
        provenance:              Origin tracking information
    
    CONTRACT REQUIREMENTS:
        LOGIC-LAW-001: Logical operators shall remain explicit.
        LOGIC-LAW-002: Operator precedence shall remain explicit.
        LOGIC-LAW-003: Compound Assertions shall preserve participating Assertions.
        LOGIC-LAW-004: Logical simplification shall preserve semantic equivalence.
        LOGIC-LAW-005: Logical provenance shall remain complete.
        LOGIC-LAW-006: Operator revisions shall preserve lineage.
        LOGIC-LAW-007: Logical evaluation shall remain inspectable.
        LOGIC-LAW-008: Equivalent logical structures shall evaluate deterministically.
    """
    
    operator_identity: str
    operator_kind: LogicalOperatorKind
    participating_assertions: Tuple[str, ...]
    precedence: int = 10
    provenance: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for deterministic serialization."""
        return {
            "operator_identity": self.operator_identity,
            "operator_kind": self.operator_kind.value,
            "participating_assertions": list(self.participating_assertions),
            "precedence": self.precedence,
            "provenance": dict(self.provenance),
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> LogicalOperator:
        """Create from dictionary (deterministic)."""
        return cls(
            operator_identity=data.get("operator_identity", ""),
            operator_kind=LogicalOperatorKind(data.get("operator_kind", "and")),
            participating_assertions=tuple(data.get("participating_assertions", [])),
            precedence=int(data.get("precedence", 10)),
            provenance=dict(data.get("provenance", {})),
        )

    @classmethod
    def create(
        cls,
        operator_kind: LogicalOperatorKind,
        *assertion_ids: str,
        precedence: int = 10,
    ) -> LogicalOperator:
        """Create a new logical operator."""
        return cls(
            operator_identity=f"operator:{uuid.uuid4().hex[:8]}",
            operator_kind=operator_kind,
            participating_assertions=assertion_ids,
            precedence=precedence,
            provenance={"created_at_utc": time.time()},
        )

    @classmethod
    def and_operator(cls, *assertion_ids: str) -> LogicalOperator:
        """Create an AND operator with highest binding (precedence 20)."""
        return cls(
            operator_identity=f"operator:{uuid.uuid4().hex[:8]}",
            operator_kind=LogicalOperatorKind.AND,
            participating_assertions=assertion_ids,
            precedence=20,
            provenance={"created_at_utc": time.time()},
        )

    @classmethod
    def or_operator(cls, *assertion_ids: str) -> LogicalOperator:
        """Create an OR operator (precedence 10)."""
        return cls(
            operator_identity=f"operator:{uuid.uuid4().hex[:8]}",
            operator_kind=LogicalOperatorKind.OR,
            participating_assertions=assertion_ids,
            precedence=10,
            provenance={"created_at_utc": time.time()},
        )

    @classmethod
    def not_operator(cls, assertion_id: str) -> LogicalOperator:
        """Create a NOT operator (unary, precedence 30)."""
        return cls(
            operator_identity=f"operator:{uuid.uuid4().hex[:8]}",
            operator_kind=LogicalOperatorKind.NOT,
            participating_assertions=(assertion_id,),
            precedence=30,
            provenance={"created_at_utc": time.time()},
        )

    @classmethod
    def implies(cls, antecedent: str, consequent: str) -> LogicalOperator:
        """Create an IMPLIES operator (precedence 5)."""
        return cls(
            operator_identity=f"operator:{uuid.uuid4().hex[:8]}",
            operator_kind=LogicalOperatorKind.IMPLIES,
            participating_assertions=(antecedent, consequent),
            precedence=5,
            provenance={"created_at_utc": time.time()},
        )

    @classmethod
    def iff(cls, assertion_a: str, assertion_b: str) -> LogicalOperator:
        """Create an IFF (if and only if) operator (precedence 4)."""
        return cls(
            operator_identity=f"operator:{uuid.uuid4().hex[:8]}",
            operator_kind=LogicalOperatorKind.IFF,
            participating_assertions=(assertion_a, assertion_b),
            precedence=4,
            provenance={"created_at_utc": time.time()},
        )

    def negate(self) -> LogicalOperator:
        """
        Create a negated version of this operator.
        
        Returns a NOT operator wrapping this one.
        LOGIC-LAW-003: Preserves participating Assertions.
        """
        return cls(
            operator_identity=f"operator:{uuid.uuid4().hex[:8]}",
            operator_kind=LogicalOperatorKind.NOT,
            participating_assertions=(self.operator_identity,),
            precedence=self.precedence + 10,  # Higher precedence for negation
            provenance={
                **self.provenance,
                "negated_at_utc": time.time(),
            },
        )

    def is_unary(self) -> bool:
        """Check if operator has only one operand."""
        return len(self.participating_assertions) == 1

    def is_binary(self) -> bool:
        """Check if operator has two operands."""
        return len(self.participating_assertions) == 2