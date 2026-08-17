# Deduction Premise Set - Phase 7.1
# ===================================

"""
Canonical Premise Set Contract.

Premise Sets define accepted premises, assumptions, constraints for deduction.
"""

from __future__ import annotations

import time
import uuid
from dataclasses import dataclass, field
from typing import Dict, List, Tuple, Optional, Any
from enum import Enum, auto


class PremiseKind(Enum):
    """Kinds of premises in a premise set."""
    
    BELIEF = "belief"                   # Accepted belief from knowledge base
    DEFINITION = "definition"           # Explicit definition
    AXIOM = "axiom"                     # Assumed true without proof
    VALIDATED_CONCLUSION = "validated_conclusion"  # Previously validated conclusion
    WORKING_ASSUMPTION = "working_assumption"      # Temporary assumption for deduction
    CONTEXTUAL_PREMISE = "contextual_premise"      # Context-dependent premise


@dataclass(frozen=True)
class DeductionPremise:
    """
    A single premise accepted for deductive reasoning.
    
    A premise contains:
        - Identity and provenance tracking
        - Kind of premise (belief, definition, axiom, etc.)
        - The premise content itself
        - Acceptance basis (why is this accepted?)
        - Scope and context
    
    Premises remain explicit; they are never inferred implicitly.
    """
    
    # Identity
    premise_id: str                         # Unique premise identifier
    semantic_identity: str                  # Stable identity for replay
    
    # Content
    premise_content: str                    # What is the premise?
    premise_kind: PremiseKind               # What kind of premise?
    
    # Acceptance basis
    acceptance_basis: str                   # Why is this accepted? (e.g., "validated", "axiomatic")
    
    # Scope
    scope: Tuple[str, ...] = ()             # Contextual constraints on applicability
    scope_limitation: Optional[str] = None  # When does this premise NOT apply?
    
    # Provenance
    origin_artifact: Optional[str] = None   # Where did this premise come from?
    validated_at_utc: Optional[float] = None  # If previously validated
    
    @property
    def is_temporary(self) -> bool:
        """Check if this is a temporary assumption."""
        return self.premise_kind == PremiseKind.WORKING_ASSUMPTION
    
    @classmethod
    def create(
        cls,
        premise_content: str,
        premise_kind: PremiseKind,
        acceptance_basis: str = "validated",
        origin_artifact: Optional[str] = None,
        scope: Optional[List[str]] = None,
    ) -> DeductionPremise:
        """Create a new deduction premise."""
        return cls(
            premise_id=f"premise:{uuid.uuid4().hex[:16]}",
            semantic_identity=f"premise:{hash(premise_content)}",
            premise_content=premise_content,
            premise_kind=premise_kind,
            acceptance_basis=acceptance_basis,
            origin_artifact=origin_artifact,
            scope=tuple(scope or []),
        )
    
    def with_scope(self, additional_scopes: List[str]) -> DeductionPremise:
        """Return a copy with additional scope constraints."""
        return dataclass_replace(
            self,
            scope=self.scope + tuple(additional_scopes),
        )


@dataclass(frozen=True)
class PremiseSet:
    """
    A set of accepted premises for deduction.
    
    A premise set defines:
        - Accepted premises
        - Temporary assumptions (for specific deductions)
        - Constraints on reasoning
        - Provenance tracking
    
    Premise Sets remain immutable during proof execution;
    new sets are created when changes are needed.
    """
    
    # Identity
    premise_set_id: str                     # Unique set identifier
    semantic_identity: str                  # Semantic identity for comparison
    
    # Participating premises
    accepted_premises: Tuple[DeductionPremise, ...]  # All accepted premises
    
    # Assumptions (temporary for this deduction)
    assumptions: Tuple[DeductionPremise, ...] = ()  # Working assumptions
    
    # Constraints on reasoning
    constraints: Tuple[str, ...] = ()       # e.g., "no circular proofs", "finite steps"
    
    # Provenance
    created_at_utc: float = field(default_factory=time.time)
    source_descriptor_id: Optional[str] = None  # Which deduction session?
    
    @property
    def all_premises(self) -> Tuple[DeductionPremise, ...]:
        """Return all premises including assumptions."""
        return self.accepted_premises + self.assumptions
    
    @property
    def premise_count(self) -> int:
        """Count of total premises."""
        return len(self.all_premises)
    
    @classmethod
    def create(
        cls,
        accepted_premises: List[DeductionPremise],
        assumptions: Optional[List[DeductionPremise]] = None,
        constraints: Optional[List[str]] = None,
        source_descriptor_id: Optional[str] = None,
    ) -> PremiseSet:
        """Create a new premise set."""
        return cls(
            premise_set_id=f"premise_set:{uuid.uuid4().hex[:16]}",
            semantic_identity=f"premise_set:{hash(tuple(p.premise_content for p in accepted_premises))}",
            accepted_premises=tuple(accepted_premises),
            assumptions=tuple(assumptions or []),
            constraints=tuple(constraints or []),
            source_descriptor_id=source_descriptor_id,
        )
    
    def with_assumptions(self, additional_assumptions: List[DeductionPremise]) -> PremiseSet:
        """Return a copy with additional assumptions."""
        return dataclass_replace(
            self,
            assumptions=self.assumptions + tuple(additional_assumptions),
        )
    
    def without_premise(self, premise_id: str) -> PremiseSet:
        """Return a copy without the specified premise."""
        new_accepted = tuple(p for p in self.accepted_premises if p.premise_id != premise_id)
        return dataclass_replace(
            self,
            accepted_premises=new_accepted,
        )


def dataclass_replace(instance: Any, **kwargs: Any) -> Any:
    """Simple dataclass replace helper for frozen instances."""
    return instance.__class__(**{**instance.__dict__, **kwargs})


__all__ = [
    "PremiseSet",
    "DeductionPremise",
    "PremiseKind",
]