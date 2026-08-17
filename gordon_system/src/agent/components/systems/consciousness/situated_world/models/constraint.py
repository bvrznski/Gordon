# Gordon Phase 5.7.7: Situated World - Constraint Model
# =======================================================

"""
Canonical constraint model for Situated World.

Constraints represent environmental limitations on the current world.
They are NOT policy decisions, but rather descriptions of what is currently possible.
"""

from __future__ import annotations

import uuid

from dataclasses import dataclass, field, replace


def _generate_uuid() -> str:
    """Generate a UUID-like identifier."""
    return uuid.uuid4().hex[:8]


@dataclass(frozen=True)
class ConstraintCategory:
    """
    Immutable constraint category classification.
    
    Categories:
        - environmental: Physical/biological limitations
        - policy: References to external policies (not enforcement)
        - security: Authorization-related (not enforcement)
    """
    
    category_id: str
    """Unique identifier for this constraint category."""
    
    description: str = ""
    """Human-readable description of the constraint category."""
    
    scope: tuple[str, ...] = field(default_factory=tuple)
    """Entities/contexts this category applies to."""
    
    @classmethod
    def environmental(cls, description: str = "") -> "ConstraintCategory":
        """Create an environmental constraint category."""
        return cls(
            category_id="env",
            description=description or "Environmental constraints",
            scope=("all_entities",),
        )
    
    @classmethod  
    def policy(cls, description: str = "") -> "ConstraintCategory":
        """Create a policy constraint category."""
        return cls(
            category_id="policy",
            description=description or "Policy references",
            scope=("authorized_entities",),
        )
    
    @classmethod
    def security(cls, description: str = "") -> "ConstraintCategory":
        """Create a security constraint category."""
        return cls(
            category_id="security",
            description=description or "Security constraints",
            scope=("access_controlled",),
        )


@dataclass(frozen=True)
class Constraint:
    """
    Canonical immutable constraint model.
    
    Rules:
        - Kind must be from valid categories (environmental, policy, security)
        - Description explains what is constrained
        - Scope identifies affected entities/contexts
        - Never represents enforcement (only description)
    """
    
    constraint_id: str = field(default_factory=lambda: f"c-{_generate_uuid()}")
    """Unique identifier for this constraint."""
    
    kind: str = "environmental"
    """Constraint category (environmental, policy, security)."""
    
    description: str
    """Human-readable description of the constraint."""
    
    scope: tuple[str, ...] = field(default_factory=tuple)
    """Entities/contexts this constraint applies to."""
    
    trust_level: str = "medium"
    """Trust level for this constraint (untrusted, medium, high)."""
    
    @classmethod
    def create(
        cls,
        kind: str,
        description: str,
        scope: tuple[str, ...] | None = None,
        trust_level: str = "medium",
    ) -> "Constraint":
        """
        Create a Constraint.
        
        Rules:
            - Kind must be from valid categories
            - Description explains what is constrained  
            - Scope identifies affected entities/contexts
            - Trust level indicates confidence in constraint validity
        """
        if kind not in ("environmental", "policy", "security"):
            raise ValueError(f"Invalid constraint kind: {kind}")
        
        return cls(
            constraint_id=f"c-{_generate_uuid()}",
            kind=kind,
            description=description,
            scope=scope or (),
            trust_level=trust_level,
        )
    
    def update_trust(self, trust_level: str) -> "Constraint":
        """Return new constraint with updated trust level."""
        return replace(self, trust_level=trust_level)
    
    def in_scope_of(self, entity_id: str) -> bool:
        """Check if this constraint applies to a specific entity."""
        if not self.scope:
            return True  # No scope = global constraint
        return entity_id in self.scope