# Knowledge Assertions - Conditional Assertion Contract - Phase 6.4
# ==================================================================

"""
Conditional Assertions: Assertions with explicit conditions on applicability.

Conditions restrict the scope of assertions and never become evidence.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Tuple, Optional, Any
from enum import Enum, auto
import time
import uuid


# =============================================================================
# CONDITION KINDS
# =============================================================================


class ConditionKind(Enum):
    """Kinds of conditions."""
    
    IF = "if"                 # Standard conditional: if A then B
    UNLESS = "unless"         # Negated antecedent: unless A, B
    ONLY_IF = "only_if"       # Necessary condition: B only if A
    WHEN = "when"             # Temporal condition: when A happens
    WHILE = "while"           # Persistent condition: while A holds
    BEFORE = "before"         # Temporal before: B before A
    AFTER = "after"           # Temporal after: B after A


# =============================================================================
# CONDITIONAL ASSERTION
# =============================================================================


@dataclass(frozen=True)
class ConditionalAssertion:
    """
    Conditional Assertion - assertion with condition on applicability.
    
    Conditions restrict the applicability of assertions. They never become
    evidence - they specify when an assertion holds.
    
    Fields:
        conditional_identity:   Unique identifier for this conditional
        antecedent:             Assertion ID that triggers the condition
        consequent:             Assertion ID that is conditional
        condition_kind:         The kind of condition (IF, UNLESS, etc.)
        applicability_scope:    Scope where condition applies
        provenance:             Origin tracking information
    
    CONTRACT REQUIREMENTS:
        CONDITION-LAW-001: Conditions shall remain explicit semantic constraints.
        CONDITION-LAW-002: Conditions shall never become supporting evidence.
        CONDITION-LAW-003: Applicability scope shall remain explicit.
        CONDITION-LAW-004: Condition revisions shall preserve lineage.
        CONDITION-LAW-005: Condition provenance shall remain complete.
        CONDITION-LAW-006: Nested conditions shall remain representable.
        CONDITION-LAW-007: Condition evaluation shall remain inspectable.
        CONDITION-LAW-008: Equivalent conditions evaluate deterministically.
    """
    
    conditional_identity: str
    antecedent: str  # The condition that must hold
    consequent: str  # The assertion that is conditional
    condition_kind: ConditionKind = ConditionKind.IF
    applicability_scope: Tuple[str, ...] = field(default_factory=tuple)
    provenance: Dict[str, Any] = field(default_factory=dict)

    @property
    def is_if_condition(self) -> bool:
        """Check if this is an IF condition."""
        return self.condition_kind == ConditionKind.IF

    @property
    def is_unless_condition(self) -> bool:
        """Check if this is an UNLESS condition."""
        return self.condition_kind == ConditionKind.UNLESS

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for deterministic serialization."""
        return {
            "conditional_identity": self.conditional_identity,
            "antecedent": self.antecedent,
            "consequent": self.consequent,
            "condition_kind": self.condition_kind.value,
            "applicability_scope": list(self.applicability_scope),
            "provenance": dict(self.provenance),
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> ConditionalAssertion:
        """Create from dictionary (deterministic)."""
        return cls(
            conditional_identity=data.get("conditional_identity", ""),
            antecedent=data.get("antecedent", ""),
            consequent=data.get("consequent", ""),
            condition_kind=ConditionKind(data.get("condition_kind", "if")),
            applicability_scope=tuple(data.get("applicability_scope", [])),
            provenance=dict(data.get("provenance", {})),
        )

    @classmethod
    def if_condition(cls, antecedent: str, consequent: str) -> ConditionalAssertion:
        """Create an IF condition."""
        return cls(
            conditional_identity=f"conditional:{uuid.uuid4().hex[:16]}",
            antecedent=antecedent,
            consequent=consequent,
            condition_kind=ConditionKind.IF,
            provenance={"created_at_utc": time.time()},
        )

    @classmethod
    def unless_condition(cls, antecedent: str, consequent: str) -> ConditionalAssertion:
        """Create an UNLESS condition."""
        return cls(
            conditional_identity=f"conditional:{uuid.uuid4().hex[:16]}",
            antecedent=antecedent,
            consequent=consequent,
            condition_kind=ConditionKind.UNLESS,
            provenance={"created_at_utc": time.time()},
        )

    @classmethod
    def only_if_condition(cls, necessary: str, sufficient: str) -> ConditionalAssertion:
        """
        Create a ONLY_IF condition.
        
        'B only if A' means A is necessary for B.
        If consequent depends on antecedent being true.
        """
        return cls(
            conditional_identity=f"conditional:{uuid.uuid4().hex[:16]}",
            antecedent=necessary,
            consequent=sufficient,
            condition_kind=ConditionKind.ONLY_IF,
            provenance={"created_at_utc": time.time()},
        )

    @classmethod
    def when_condition(cls, trigger: str, conditional: str) -> ConditionalAssertion:
        """Create a WHEN condition (temporal)."""
        return cls(
            conditional_identity=f"conditional:{uuid.uuid4().hex[:16]}",
            antecedent=trigger,
            consequent=conditional,
            condition_kind=ConditionKind.WHEN,
            provenance={"created_at_utc": time.time()},
        )

    def negate(self) -> ConditionalAssertion:
        """Create a negated version of this conditional."""
        # NOT (if A then B) = A and NOT B
        return cls(
            conditional_identity=f"conditional:{uuid.uuid4().hex[:16]}",
            antecedent=self.antecedent,
            consequent=f"NOT:{self.consequent}",
            condition_kind=ConditionKind.IF,
            provenance={
                **self.provenance,
                "negated_at_utc": time.time(),
            },
        )

    def flip(self) -> ConditionalAssertion:
        """
        Flip the antecedent and consequent (for IFF conditions).
        
        NOT a logical negation, just swapping positions.
        """
        return cls(
            conditional_identity=self.conditional_identity,
            antecedent=self.consequent,
            consequent=self.antecedent,
            condition_kind=self.condition_kind,
            applicability_scope=self.applicability_scope,
            provenance={
                **self.provenance,
                "flipped_at_utc": time.time(),
            },
        )

    def add_scope(self, scope_id: str) -> ConditionalAssertion:
        """Add a scope to the applicability scope."""
        return ConditionalAssertion(
            conditional_identity=self.conditional_identity,
            antecedent=self.antecedent,
            consequent=self.consequent,
            condition_kind=self.condition_kind,
            applicability_scope=self.applicability_scope + (scope_id,),
            provenance={
                **self.provenance,
                "scope_added_at_utc": time.time(),
                "new_scope": scope_id,
            },
        )