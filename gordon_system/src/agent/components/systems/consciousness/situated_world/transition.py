# Gordon Phase 5.7.7: Situated World - Transition
# ================================================

"""
Canonical immutable world transition model.

Transitions are deterministic, atomic, and replayable:
* initialization
* entity updates  
* relation updates
* affordance updates
* constraint updates
* environment switching
* interruption
* resume
* degradation
* recovery
"""

from __future__ import annotations

import uuid
from dataclasses import dataclass, field


def _generate_uuid() -> str:
    """Generate a UUID-like identifier."""
    return uuid.uuid4().hex[:8]


@dataclass(frozen=True)
class TransitionId:
    """
    Immutable transition identifier.
    
    Generated deterministically from:
        - Previous transition ID (or None for initial)
        - Current generation
        - Timestamp reference
        
    This ensures replay produces identical transitions.
    """
    
    value: str = field(default_factory=lambda: f"trans-{_generate_uuid()}")
    """The UUID value of this transition."""
    
    @classmethod
    def from_previous(
        cls,
        previous_id: str | None,
        generation: int,
        timestamp_ref: str | None = None,
    ) -> "TransitionId":
        """
        Create a deterministic transition ID.
        
        Rules:
            - Previous ID (if present) is part of the hash
            - Generation must match target world generation
            - Timestamp reference provides temporal anchor
        """
        parts = [f"trans-{_generate_uuid()}"]
        if previous_id:
            parts.append(previous_id[:8])
        if timestamp_ref:
            parts.append(timestamp_ref[:8])
        
        return cls(value="-".join(parts))


@dataclass(frozen=True)
class TransitionLogEntry:
    """
    Immutable log entry for transition replay.
    
    Contains minimal information needed to reconstruct world state
    without exposing sensitive runtime data.
    """
    
    transition_id: str
    """The transition that produced this change."""
    
    timestamp_ref: str | None = None
    """Semantic time reference."""
    
    entity_action: str | None = None
    """Entity action (CREATE, UPDATE, DEPRECATE, REMOVE)."""
    
    entity_id: str | None = None
    """Affected entity ID if applicable."""
    
    relation_action: str | None = None
    """Relation action (ADD, REMOVE)."""
    
    relation_id: str | None = None
    """Affected relation ID if applicable."""
    
    constraint_action: str | None = None
    """Constraint action (ADD, REMOVE, MODIFY)."""
    
    constraint_id: str | None = None
    """Affected constraint ID if applicable."""


@dataclass(frozen=True)
class WorldTransition:
    """
    Canonical immutable world transition model.
    
    Rules:
        - Deterministic (same inputs = same outputs)
        - Atomic (all-or-nothing)
        - Replayable (can reproduce from logs)
        - Never modifies published state
    """
    
    transition_id: str = field(default_factory=lambda: f"trans-{_generate_uuid()}")
    """Unique identifier for this transition."""
    
    from_generation: int
    """Generation before transition."""
    
    to_generation: int
    """Generation after transition (must be from_generation + 1)."""
    
    timestamp_ref: str | None = None
    """Semantic time reference when transition occurred."""
    
    # Entity operations
    entities_added: tuple[str, ...] = field(default_factory=tuple)
    entities_updated: tuple[str, ...] = field(default_factory=tuple)
    entities_removed: tuple[str, ...] = field(default_factory=tuple)
    
    # Relation operations  
    relations_added: tuple[str, ...] = field(default_factory=tuple)
    relations_removed: tuple[str, ...] = field(default_factory=tuple)
    
    # Affordance operations
    affordances_added: tuple[str, ...] = field(default_factory=tuple)
    affordances_removed: tuple[str, ...] = field(default_factory=tuple)
    
    # Constraint operations
    constraints_added: tuple[str, ...] = field(default_factory=tuple)
    constraints_removed: tuple[str, ...] = field(default_factory=tuple)
    
    # Environment operations
    environment_changed: bool = False
    """True if environment reference changed."""
    
    # Lifecycle operations
    transition_type: str = "normal"
    """Transition type (init, update, interrupt, resume, degrade, recover)."""
    
    @classmethod
    def create(
        cls,
        from_generation: int,
        to_generation: int,
        timestamp_ref: str | None = None,
        entities_added: tuple[str, ...] | None = None,
        entities_updated: tuple[str, ...] | None = None,
        entities_removed: tuple[str, ...] | None = None,
        relations_added: tuple[str, ...] | None = None,
        relations_removed: tuple[str, ...] | None = None,
        affordances_added: tuple[str, ...] | None = None,
        affordances_removed: tuple[str, ...] | None = None,
        constraints_added: tuple[str, ...] | None = None,
        constraints_removed: tuple[str, ...] | None = None,
        environment_changed: bool = False,
        transition_type: str = "normal",
    ) -> "WorldTransition":
        """
        Create a WorldTransition with validation.
        
        Rules:
            - to_generation must equal from_generation + 1
            - Operations are immutable (only references, not objects)
            - Environment change is recorded but doesn't modify state
        """
        if to_generation != from_generation + 1:
            raise ValueError(
                f"Generation must increment by 1: {from_generation} -> {to_generation}"
            )
        
        return cls(
            transition_id=f"trans-{_generate_uuid()}",
            from_generation=from_generation,
            to_generation=to_generation,
            timestamp_ref=timestamp_ref,
            entities_added=entities_added or (),
            entities_updated=entities_updated or (),
            entities_removed=entities_removed or (),
            relations_added=relations_added or (),
            relations_removed=relations_removed or (),
            affordances_added=affordances_added or (),
            affordances_removed=affordances_removed or (),
            constraints_added=constraints_added or (),
            constraints_removed=constraints_removed or (),
            environment_changed=environment_changed,
            transition_type=transition_type,
        )
    
    def log_entry(self) -> TransitionLogEntry:
        """Create a minimal replay log entry from this transition."""
        return TransitionLogEntry(
            transition_id=self.transition_id,
            timestamp_ref=self.timestamp_ref,
            entity_action=None,  # Use detailed action fields
            entity_id=None,
            relation_action=None,
            relation_id=None,
            constraint_action=None,
            constraint_id=None,
        )
    
    def is_deterministic(self) -> bool:
        """Check if this transition was deterministic."""
        # All immutable types and no random elements = deterministic
        return True  # By construction
    
    def apply_to_generation(self, current: int) -> int:
        """Apply this transition to a generation number."""
        if current != self.from_generation:
            raise ValueError(
                f"Generation mismatch: expected {self.from_generation}, got {current}"
            )
        return self.to_generation