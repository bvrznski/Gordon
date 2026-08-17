# Inference Rule - Phase 7.1
# ===========================

"""
Canonical Inference Rule Contract.

Inference Rules define valid logical inference patterns.
"""

from __future__ import annotations

import time
import uuid
from dataclasses import dataclass, field
from typing import Dict, List, Tuple, Optional, Any
from enum import Enum, auto


class RuleKind(Enum):
    """Kinds of inference rules."""
    
    # Propositional Logic Rules
    MODUS_PONENS = "modus_ponens"               # If P→Q and P, then Q
    MODUS_TOLLENS = "modus_tollens"             # If P→Q and ¬Q, then ¬P
    HYPOTHETICAL_SYLLOGISM = "hypothetical_syllogism"  # If P→Q and Q→R, then P→R
    DISJUNCTIVE_SYLLOGISM = "disjunctive_syllogism"    # If P∨Q and ¬P, then Q
    CONJUNCTION_INTRODUCTION = "conjunction_introduction"  # From P, Q infer P∧Q
    CONJUNCTION_ELIMINATION = "conjunction_elimination"    # From P∧Q infer P (or Q)
    DISJUNCTION_INTRODUCTION = "disjunction_introduction"  # From P infer P∨Q
    
    # Predicate Logic Rules
    UNIVERSAL_INSTANTIATION = "universal_instantiation"    # From ∀x.P(x) infer P(a)
    EXISTENTIAL_GENERALIZATION = "existential_generalization"  # From P(a) infer ∃x.P(x)
    EXISTS_ELIMINATION = "existential_elimination"          # Proof by cases
    
    # Equivalence Rules
    EQUIVALENCE_INTRODUCTION = "equivalence_introduction"  # From P→Q and Q→P, infer P↔Q
    EQUIVALENCE_ELIMINATION = "equivalence_elimination"    # From P↔Q, infer P→Q (and Q→P)
    
    # Negation Rules
    NEGATION_INTRODUCTION = "negation_introduction"         # Reductio ad absurdum
    NEGATION_ELIMINATION = "negation_elimination"           # Double negation elimination
    
    # Structural Rules
    WEAKENING = "weakening"                   # From P, infer Q→P (if Q not used)
    CONTRACTION = "contraction"               # From P∧P, infer P
    COMMUTATION = "commutation"               # From P∧Q, infer Q∧P
    
    # Special Rules
    IDENTITY_INTRODUCTION = "identity_introduction"         # Infer a=a
    SUBSTITUTION = "substitution"           # From a=b and P(a), infer P(b)


@dataclass(frozen=True)
class InferenceRule:
    """
    An inference rule for deductive reasoning.
    
    A rule contains:
        - Identity and provenance tracking
        - Rule kind (modus ponens, modus tollens, etc.)
        - Required premises (antecedents)
        - Produced conclusion (consequent)
        - Validity constraints (preconditions)
    
    Rules remain explicit; they are never fabricated during reasoning.
    """
    
    # Identity
    rule_id: str                            # Unique rule identifier
    semantic_identity: str                  # Stable identity for replay
    
    # Classification
    rule_kind: RuleKind                     # What kind of rule?
    
    # Required premises (what must be present to apply this rule)
    required_premises: Tuple[str, ...]      # e.g., ["P→Q", "P"]
    
    # Produced conclusion (what follows from satisfying requirements)
    produced_conclusion: str                # e.g., "Q"
    
    # Validity constraints
    validity_constraints: Tuple[str, ...] = ()  # e.g., ["P must be atomic", "no circular dependency"]
    
    # Scope
    scope: Tuple[str, ...] = ()             # Contextual applicability
    
    # Provenance
    created_at_utc: float = field(default_factory=time.time)
    origin_artifact: Optional[str] = None   # Where did this rule come from?
    
    @property
    def required_premise_count(self) -> int:
        """Count of required premises."""
        return len(self.required_premises)
    
    @classmethod
    def create(
        cls,
        rule_kind: RuleKind,
        required_premises: List[str],
        produced_conclusion: str,
        validity_constraints: Optional[List[str]] = None,
        scope: Optional[List[str]] = None,
        origin_artifact: Optional[str] = None,
    ) -> InferenceRule:
        """Create a new inference rule."""
        return cls(
            rule_id=f"rule:{uuid.uuid4().hex[:16]}",
            semantic_identity=f"rule:{rule_kind.value}:{hash(tuple(required_premises))}",
            rule_kind=rule_kind,
            required_premises=tuple(required_premises),
            produced_conclusion=produced_conclusion,
            validity_constraints=tuple(validity_constraints or []),
            scope=tuple(scope or []),
            origin_artifact=origin_artifact,
        )
    
    def with_scope(self, additional_scopes: List[str]) -> InferenceRule:
        """Return a copy with additional scope constraints."""
        return dataclass_replace(
            self,
            scope=self.scope + tuple(additional_scopes),
        )


def dataclass_replace(instance: Any, **kwargs: Any) -> Any:
    """Simple dataclass replace helper for frozen instances."""
    return instance.__class__(**{**instance.__dict__, **kwargs})


__all__ = [
    "InferenceRule",
    "RuleKind",
]