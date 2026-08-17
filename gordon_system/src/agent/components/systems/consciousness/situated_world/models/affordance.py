# Gordon Phase 5.7.7: Situated World - Affordance Model
# ======================================================

"""
Canonical affordance model for Situated World.

Affordances describe what actions are *possible* in the current world state.
They never grant action authority and are non-authoritative.
"""

from __future__ import annotations

import uuid

from dataclasses import dataclass, field, replace


def _generate_uuid() -> str:
    """Generate a UUID-like identifier."""
    return uuid.uuid4().hex[:8]


@dataclass(frozen=True)
class AffordancePrecondition:
    """
    Precondition for an affordance to be available.
    
    Examples:
        - Entity must have attribute X
        - World must satisfy constraint Y  
        - Agent must have relation Z with entity E
    """
    
    precondition_id: str
    """Unique identifier for this precondition."""
    
    kind: str = "attribute"
    """Precondition kind (attribute, constraint, relation)."""
    
    reference: str | None = None
    """Reference to the required element."""
    
    value: object = None
    """Required value if applicable."""
    
    @classmethod
    def attribute(
        cls,
        entity_id: str,
        attr_name: str,
        attr_value: object = None,
    ) -> "AffordancePrecondition":
        """Create an attribute precondition."""
        return cls(
            precondition_id=f"prec-{entity_id[:8]}-attr",
            kind="attribute",
            reference=entity_id,
            value={attr_name: attr_value},
        )
    
    @classmethod
    def constraint(cls, constraint_id: str) -> "AffordancePrecondition":
        """Create a constraint precondition."""
        return cls(
            precondition_id=f"prec-{constraint_id[:8]}-cstr",
            kind="constraint",
            reference=constraint_id,
        )
    
    @classmethod
    def relation(
        cls,
        source_id: str,
        target_id: str,
        relation_kind: str = "related_to",
    ) -> "AffordancePrecondition":
        """Create a relation precondition."""
        return cls(
            precondition_id=f"prec-{source_id[:8]}-rel",
            kind="relation",
            reference=f"{source_id}->{target_id}",
            value={"kind": relation_kind},
        )


@dataclass(frozen=True)
class Affordance:
    """
    Canonical immutable affordance model.
    
    Rules:
        - Describes possibility, not permission
        - Requires preconditions that must be satisfied
        - Context-dependent (only valid for specific environment)
        - Never authorizes actions (non-authoritative)
    """
    
    affordance_id: str = field(default_factory=lambda: f"aff-{_generate_uuid()}")
    """Unique identifier for this affordance."""
    
    possible_action: str
    """Description of the possible action."""
    
    required_preconditions: tuple[AffordancePrecondition, ...] = field(
        default_factory=tuple,
    )
    """Preconditions that must be satisfied."""
    
    expected_effects: tuple[str, ...] = field(default_factory=tuple)
    """Expected outcome references if action is performed."""
    
    context_ref: str | None = None
    """Environment/context where this affordance applies."""
    
    confidence: float = 1.0
    """Confidence in the affordance [0.0, 1.0]."""
    
    @classmethod
    def create(
        cls,
        possible_action: str,
        context_ref: str | None = None,
        required_preconditions: tuple[AffordancePrecondition, ...] | None = None,
        expected_effects: tuple[str, ...] | None = None,
        confidence: float = 1.0,
    ) -> "Affordance":
        """
        Create an Affordance.
        
        Rules:
            - Possible action must be specified
            - Preconditions describe required conditions
            - Effects describe expected outcomes
            - Confidence indicates certainty [0.0, 1.0]
        """
        if not possible_action:
            raise ValueError("possible_action must be non-empty")
        
        return cls(
            affordance_id=f"aff-{_generate_uuid()}",
            possible_action=possible_action,
            required_preconditions=required_preconditions or (),
            expected_effects=expected_effects or (),
            context_ref=context_ref,
            confidence=min(1.0, max(0.0, float(confidence))),
        )
    
    def with_confidence(self, confidence: float) -> "Affordance":
        """Return new affordance with updated confidence."""
        return replace(
            self,
            confidence=min(1.0, max(0.0, float(confidence))),
        )
    
    def has_precondition(self, precondition_id: str) -> bool:
        """Check if this affordance requires a specific precondition."""
        return any(p.precondition_id == precondition_id for p in self.required_preconditions)