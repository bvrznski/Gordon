# Workspace State Transition Module
# ==================================

"""
Canonical WorkspaceStateTransition and related types.

WorkspaceStateTransition represents a complete semantic record of state change,
including previous state, next state, applied deltas, and transition evidence.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Tuple


TransitionIdentity = str
"""
Unique identifier for a WorkspaceStateTransition instance.

Characteristics:
- Globally unique across all time
- Never changes once assigned
- External or deterministically derived (never internally generated)
"""


@dataclass(frozen=True)
class TransitionEvidence:
    """
    Evidence supporting a state transition.
    
    Captures the semantic justification and context for why a transition
    occurred, without embedding runtime state.
    """
    
    # Justification
    justifications: Tuple[str, ...] = field(default_factory=tuple)
    """Semantic justifications for this transition."""
    
    # Assumptions
    assumptions: Tuple[str, ...] = field(default_factory=tuple)
    """Assumptions held during the transition."""
    
    # Dependencies
    dependencies_met: Tuple[str, ...] = field(default_factory=tuple)
    """Dependencies that were satisfied before the transition."""
    
    dependencies_failed: Tuple[str, ...] = field(default_factory=tuple)
    """Dependencies that failed (if any)."""
    
    # Validation
    pre_transition_valid: bool = True
    """Whether the previous state was valid."""
    
    post_transition_valid: bool = True
    """Whether the resulting state is valid."""
    
    delta_applied_successfully: bool = True
    """Whether the delta was successfully applied."""


@dataclass(frozen=True)
class WorkspaceStateTransition:
    """
    Complete semantic record of a workspace state transition.
    
    Transition semantics:
    - Deterministic: same inputs produce identical transitions
    - Immutable: once recorded, cannot be modified
    - Complete: captures all aspects of the transition
    - Provenance-preserving: maintains traceability through lineage
    
    A transition represents exactly one revision change in the workspace state.
    Each transition produces exactly one new state from exactly one previous state.
    
    ARCHITECTURAL INVARIANT: Every transition references exactly one previous state
    and exactly one next state.
    """
    
    # Identity and Revisioning
    transition_id: TransitionIdentity = "transition_initial"
    """Unique identifier for this transition instance."""
    
    revision: int = 0
    """Revision number that this transition produces."""
    
    schema_version: str = "1.0.0"
    """Schema version for compatibility tracking."""
    
    # State references
    previous_state_id: str = ""
    """ID of the state before this transition."""
    
    next_state_id: str = ""
    """ID of the state after this transition."""
    
    # Delta reference (the delta that caused this transition)
    applied_delta_id: str = ""
    """ID of the delta that was applied to produce this transition."""
    
    # Transition evidence and metadata
    evidence: TransitionEvidence = field(default_factory=TransitionEvidence)
    """Evidence supporting this transition."""
    
    justification: str = ""
    """High-level description of why this transition occurred."""
    
    # Timing (semantic only, not runtime state)
    produced_at_utc: float = 0.0
    """When transition was recorded (seconds since epoch)."""
    
    produced_by: str = "workspace_transition"
    """Who/what recorded this transition."""
    
    # Validation
    validity_class: str = "valid"
    """Classification of transition validity."""
    
    determinism_class: str = "deterministic"
    """Classification of determinism."""
    
    @classmethod
    def create_initial(cls) -> WorkspaceStateTransition:
        """
        Create an initial (empty) transition.
        
        This represents the transition that produces the initial state from nothing.
        """
        return cls(
            transition_id="transition_initial",
            revision=0,
            previous_state_id="",
            next_state_id="workspace_state_initial",
            validity_class="valid",
            determinism_class="deterministic",
        )
    
    @property
    def is_forward(self) -> bool:
        """Check if this is a forward transition (produces new state)."""
        return self.next_state_id != ""
    
    @property
    def is_backward(self) -> bool:
        """Check if this could be part of a restoration."""
        # Backward transitions would reference future states for rollback
        # This is a semantic capability, not runtime execution
        return False


@dataclass(frozen=True)
class TransitionChain:
    """
    A chain of consecutive state transitions.
    
    Used to represent the complete history from one state to another via
    intermediate steps. Each transition in the chain must be valid and
    properly connected.
    """
    
    start_state_id: str = ""
    """ID of the starting state."""
    
    end_state_id: str = ""
    """ID of the ending state."""
    
    transitions: Tuple[WorkspaceStateTransition, ...] = field(default_factory=tuple)
    """Ordered sequence of transitions in this chain."""
    
    @property
    def length(self) -> int:
        """Return the number of transitions in this chain."""
        return len(self.transitions)
    
    @property
    def is_empty(self) -> bool:
        """Check if this chain has no transitions."""
        return self.length == 0
    
    def verify_chain_integrity(self) -> bool:
        """
        Verify that all transitions are properly connected.
        
        Returns True if the chain is valid (each transition's next_state_id
        matches the following transition's previous_state_id).
        """
        if len(self.transitions) <= 1:
            return True
        
        for i in range(len(self.transitions) - 1):
            current = self.transitions[i]
            next_transition = self.transitions[i + 1]
            
            if current.next_state_id != next_transition.previous_state_id:
                return False
        
        return True


# =============================================================================
# EXPORTS
# =============================================================================

__all__: tuple[str, ...] = (
    "TransitionIdentity",
    "TransitionEvidence",
    "WorkspaceStateTransition",
    "TransitionChain",
)