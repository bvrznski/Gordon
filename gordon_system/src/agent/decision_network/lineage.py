# Gordon Cognitive Architecture - Phase 4.5.2
# ===========================================
"""
Action Lineage Model

This module implements the immutable lineage graph for Action identities,
tracking revision history, transitions, replacements, and supersessions.

ARCHITECTURE
============

ActionLineage (immutable history graph)
    ├── ActionHistory (append-only log of all changes)
    ├── ActionDelta (change record between revisions)
    ├── ActionTransition (state transition event)
    ├── ActionContinuation (continues identity with revision)
    ├── ActionReplacement (replaces previous revision with traceability)
    └── ActionSupersession (supersedes with stronger relationship)

IDENTITY TRANSITION RULES
=========================

Continuation:  Same identity, valid revision → ActionContinuation
Replacement:   New identity replaces old → ActionReplacement  
Supersession:  New identity supersedes old → ActionSupersession

All transitions are immutable and append-only.
History is acyclic.

ARCHITECTURAL INVARIANTS
========================

ACTION-LINEAGE-INV-001: Lineage graph is acyclic.
ACTION-LINEAGE-INV-002: History is append-only.
ACTION-LINEAGE-INV-003: All transitions are immutable.
ACTION-LINEAGE-INV-004: Replacement preserves traceability.
ACTION-LINEAGE-INV-005: Supersession is explicit and stronger than replacement.
"""

from dataclasses import dataclass, field
from typing import List, Optional
from enum import Enum


# =============================================================================
# TRANSITION KINDS - Types of lineage transitions
# =============================================================================

class TransitionKind(Enum):
    """
    Kinds of identity transitions in lineage.
    
    Runtime-neutral: Yes
    Executable: No
    """
    
    CONTINUATION = "continuation"
    """Identity continues with valid revision."""
    
    REPLACEMENT = "replacement"
    """New identity replaces old (with traceability)."""
    
    SUPERSESION = "supersession"
    """New identity supersedes old (stronger relationship)."""
    
    TERMINATION = "termination"
    """Action permanently invalidated."""
    
    REVERSION = "reversion"
    """Revert to a previous valid revision."""
    
    UNKNOWN = "unknown"


# =============================================================================
# ACTION DELTA - Change record between revisions
# =============================================================================

@dataclass(frozen=True)
class ActionDelta:
    """
    Record of changes between two revisions of an Action.
    
    A delta captures the semantic difference from one revision to another,
    enabling replay and migration without full revision reconstruction.
    
    Runtime-neutral: Yes
    Executable: No
    """
    
    # Revision references
    from_revision_id: str = field(default="")
    """Source revision identifier."""
    
    to_revision_id: str = field(default="")
    """Target revision identifier."""
    
    # Change description (human-readable)
    description: str = field(default="")
    """Description of the changes made."""
    
    # Change categories
    changed_fields: List[str] = field(default_factory=list)
    """List of fields that changed."""
    
    added_fields: List[str] = field(default_factory=list)
    """Fields added in new revision."""
    
    removed_fields: List[str] = field(default_factory=list)
    """Fields removed in new revision."""
    
    # Semantic change indicator
    is_semantic_change: bool = False
    """True if the change affects semantic meaning."""
    
    @property
    def delta_id(self) -> str:
        """Return unique delta identifier."""
        return f"{self.from_revision_id}→{self.to_revision_id}"
    
    @classmethod
    def between(
        cls,
        from_rev: str,
        to_rev: str,
        description: str = "",
    ) -> "ActionDelta":
        """
        Create a delta record between two revisions.
        
        Args:
            from_rev: Source revision ID
            to_rev: Target revision ID
            description: Description of changes
            
        Returns:
            ActionDelta instance
        """
        return cls(
            from_revision_id=from_rev,
            to_revision_id=to_rev,
            description=description,
        )
    
    def to_dict(self) -> dict:
        """Serialize to dictionary."""
        return {
            "from_revision_id": self.from_revision_id,
            "to_revision_id": self.to_revision_id,
            "description": self.description,
            "changed_fields": list(self.changed_fields),
            "added_fields": list(self.added_fields),
            "removed_fields": list(self.removed_fields),
            "is_semantic_change": self.is_semantic_change,
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> "ActionDelta":
        """Deserialize from dictionary."""
        return cls(
            from_revision_id=data.get("from_revision_id", ""),
            to_revision_id=data.get("to_revision_id", ""),
            description=data.get("description", ""),
            changed_fields=list(data.get("changed_fields", [])),
            added_fields=list(data.get("added_fields", [])),
            removed_fields=list(data.get("removed_fields", [])),
            is_semantic_change=bool(data.get("is_semantic_change", False)),
        )


# =============================================================================
# ACTION TRANSITION - State transition event
# =============================================================================

@dataclass(frozen=True)
class ActionTransition:
    """
    Record of a state transition in the lineage graph.
    
    A transition records when an Action identity moves from one state to another,
    including the kind of transition, timestamp, and any relevant metadata.
    
    Runtime-neutral: Yes
    Executable: No
    """
    
    # Transition identification
    transition_id: str = field(default="")
    """Unique identifier for this transition."""
    
    # Source and target states
    from_state: str = field(default="draft")
    """Source state (e.g., 'draft', 'active', 'superseded')."""
    
    to_state: str = field(default="active")
    """Target state after transition."""
    
    # Timing
    transition_time_semantic: float = field(default=0.0)
    """Semantic time of the transition."""
    
    # Transition kind
    kind: TransitionKind = field(default=TransitionKind.CONTINUATION)
    """Type of transition."""
    
    # Metadata
    reason: Optional[str] = None
    """Reason for the transition."""
    
    authority: Optional[str] = None
    """Entity or process that authorized the transition."""
    
    evidence: List[str] = field(default_factory=list)
    """Evidence supporting this transition."""
    
    @property
    def is_valid_continuation(self) -> bool:
        """Check if this transition represents valid continuation."""
        return self.kind in (
            TransitionKind.CONTINUATION,
            TransitionKind.REVERSION,
        )
    
    def to_dict(self) -> dict:
        """Serialize to dictionary."""
        return {
            "transition_id": self.transition_id,
            "from_state": self.from_state,
            "to_state": self.to_state,
            "transition_time_semantic": self.transition_time_semantic,
            "kind": self.kind.value,
            "reason": self.reason,
            "authority": self.authority,
            "evidence": list(self.evidence),
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> "ActionTransition":
        """Deserialize from dictionary."""
        return cls(
            transition_id=data.get("transition_id", ""),
            from_state=data.get("from_state", "draft"),
            to_state=data.get("to_state", "active"),
            transition_time_semantic=float(data.get("transition_time_semantic", 0.0)),
            kind=TransitionKind(data.get("kind", TransitionKind.CONTINUATION.value)),
            reason=data.get("reason"),
            authority=data.get("authority"),
            evidence=list(data.get("evidence", [])),
        )


# =============================================================================
# ACTION CONTINUATION - Continues identity with revision
# =============================================================================

@dataclass(frozen=True)
class ActionContinuation:
    """
    Record that an action identity continues with a valid revision.
    
    A continuation indicates the semantic continuity of an Action through
    a valid revision. It preserves all prior history while adding new content.
    
    Invariant: Continuation never changes the base identity, only version.
    
    Runtime-neutral: Yes
    Executable: No
    """
    
    # Identity being continued
    action_identity_id: str = field(default="")
    """The ActionIdentity that continues."""
    
    # Revision information
    previous_revision_id: Optional[str] = None
    """Previous revision (None for initial)."""
    
    new_revision_id: str = field(default="")
    """New revision being added."""
    
    # Timestamps
    continuation_time_semantic: float = field(default=0.0)
    """Semantic time of continuation."""
    
    # Continuation metadata
    is_valid: bool = True
    """Whether this continuation is valid (not invalidated)."""
    
    reason: Optional[str] = None
    """Reason for the revision."""
    
    @property
    def continuation_id(self) -> str:
        """Return unique continuation identifier."""
        if self.previous_revision_id:
            return f"{self.action_identity_id}:cont:{self.new_revision_id}"
        return f"{self.action_identity_id}:init"
    
    def to_dict(self) -> dict:
        """Serialize to dictionary."""
        return {
            "action_identity_id": self.action_identity_id,
            "previous_revision_id": self.previous_revision_id,
            "new_revision_id": self.new_revision_id,
            "continuation_time_semantic": self.continuation_time_semantic,
            "is_valid": self.is_valid,
            "reason": self.reason,
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> "ActionContinuation":
        """Deserialize from dictionary."""
        return cls(
            action_identity_id=data.get("action_identity_id", ""),
            previous_revision_id=data.get("previous_revision_id"),
            new_revision_id=data.get("new_revision_id", ""),
            continuation_time_semantic=float(data.get("continuation_time_semantic", 0.0)),
            is_valid=bool(data.get("is_valid", True)),
            reason=data.get("reason"),
        )


# =============================================================================
# ACTION REPLACEMENT - Replaces previous revision with traceability
# =============================================================================

@dataclass(frozen=True)
class ActionReplacement:
    """
    Record that an action replaces a previous revision.
    
    Replacement creates a new identity while maintaining traceability to the
    replaced identity. The old identity remains in history but is marked as
    replaced by this new one.
    
    Invariant: Replacement never mutates the original identity.
    
    Runtime-neutral: Yes
    Executable: No
    """
    
    # Old (replaced) identity
    previous_identity_id: str = field(default="")
    """The ActionIdentity being replaced."""
    
    # New (replacement) identity
    new_identity_id: str = field(default="")
    """The new ActionIdentity that replaces the old."""
    
    # Timestamps
    replacement_time_semantic: float = field(default=0.0)
    """Semantic time of replacement."""
    
    # Replacement metadata
    reason: Optional[str] = None
    """Reason for replacement (e.g., 'semantic_break', 'bug_fix')."""
    
    authority: Optional[str] = None
    """Entity that authorized the replacement."""
    
    traceability_evidence: List[str] = field(default_factory=list)
    """Evidence linking old to new identity."""
    
    @property
    def replacement_id(self) -> str:
        """Return unique replacement identifier."""
        return f"replace:{self.previous_identity_id}→{self.new_identity_id}"
    
    @classmethod
    def create(
        cls,
        previous_id: str,
        new_id: str,
        reason: Optional[str] = None,
        authority: Optional[str] = None,
    ) -> "ActionReplacement":
        """
        Create a replacement record.
        
        Args:
            previous_id: The identity being replaced
            new_id: The new identity that replaces it
            reason: Reason for replacement
            authority: Entity authorizing the replacement
            
        Returns:
            ActionReplacement instance
        """
        return cls(
            previous_identity_id=previous_id,
            new_identity_id=new_id,
            reason=reason,
            authority=authority,
        )
    
    def to_dict(self) -> dict:
        """Serialize to dictionary."""
        return {
            "previous_identity_id": self.previous_identity_id,
            "new_identity_id": self.new_identity_id,
            "replacement_time_semantic": self.replacement_time_semantic,
            "reason": self.reason,
            "authority": self.authority,
            "traceability_evidence": list(self.traceability_evidence),
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> "ActionReplacement":
        """Deserialize from dictionary."""
        return cls(
            previous_identity_id=data.get("previous_identity_id", ""),
            new_identity_id=data.get("new_identity_id", ""),
            replacement_time_semantic=float(data.get("replacement_time_semantic", 0.0)),
            reason=data.get("reason"),
            authority=data.get("authority"),
            traceability_evidence=list(data.get("traceability_evidence", [])),
        )


# =============================================================================
# ACTION SUPERSESSION - Supersedes with stronger relationship
# =============================================================================

@dataclass(frozen=True)
class ActionSupersession:
    """
    Record that an action supersedes a previous revision.
    
    Supersession is stronger than replacement. It indicates the new action
    completely subsumes the old, typically due to semantic evolution or
    major version changes.
    
    Invariant: Supersession invalidates all prior versions for selection purposes.
    
    Runtime-neutral: Yes
    Executable: No
    """
    
    # Old (superseded) identity
    superseded_identity_id: str = field(default="")
    """The ActionIdentity being superseded."""
    
    # New (superseding) identity
    superseding_identity_id: str = field(default="")
    """The new ActionIdentity that supersedes the old."""
    
    # Timestamps
    supersession_time_semantic: float = field(default=0.0)
    """Semantic time of supersession."""
    
    # Supersession metadata
    reason: Optional[str] = None
    """Reason for supersession (e.g., 'major_revision', 'semantic_update')."""
    
    authority: Optional[str] = None
    """Entity that authorized the supersession."""
    
    # Relationship details
    is_deprecated: bool = True
    """Whether the superseded identity is deprecated."""
    
    has_backward_compatibility: bool = False
    """Whether the new action maintains backward compatibility."""
    
    @property
    def supersession_id(self) -> str:
        """Return unique supersession identifier."""
        return f"super:{self.superseded_identity_id}→{self.superseding_identity_id}"
    
    @classmethod
    def create(
        cls,
        superseded_id: str,
        superseding_id: str,
        reason: Optional[str] = None,
        authority: Optional[str] = None,
    ) -> "ActionSupersession":
        """
        Create a supersession record.
        
        Args:
            superseded_id: The identity being superseded
            superseding_id: The new identity that supersedes it
            reason: Reason for supersession
            authority: Entity authorizing the supersession
            
        Returns:
            ActionSupersession instance
        """
        return cls(
            superseded_identity_id=superseded_id,
            superseding_identity_id=superseding_id,
            reason=reason,
            authority=authority,
        )
    
    def to_dict(self) -> dict:
        """Serialize to dictionary."""
        return {
            "superseded_identity_id": self.superseded_identity_id,
            "superseding_identity_id": self.superseding_identity_id,
            "supersession_time_semantic": self.supersession_time_semantic,
            "reason": self.reason,
            "authority": self.authority,
            "is_deprecated": self.is_deprecated,
            "has_backward_compatibility": self.has_backward_compatibility,
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> "ActionSupersession":
        """Deserialize from dictionary."""
        return cls(
            superseded_identity_id=data.get("superseded_identity_id", ""),
            superseding_identity_id=data.get("superseding_identity_id", ""),
            supersession_time_semantic=float(data.get("supersession_time_semantic", 0.0)),
            reason=data.get("reason"),
            authority=data.get("authority"),
            is_deprecated=bool(data.get("is_deprecated", True)),
            has_backward_compatibility=bool(data.get("has_backward_compatibility", False)),
        )


# =============================================================================
# ACTION HISTORY - Append-only log of all changes
# =============================================================================

@dataclass(frozen=True)
class ActionHistory:
    """
    Append-only history log for an Action's lineage.
    
    History contains all transitions, continuations, replacements, and
    supersessions in temporal order. It is immutable and append-only.
    
    Runtime-neutral: Yes
    Executable: No
    """
    
    # Identity this history belongs to
    action_identity_id: str = field(default="")
    """The ActionIdentity this history tracks."""
    
    # Log entries (oldest first)
    entries: List[ActionTransition] = field(default_factory=list)
    """Ordered list of state transitions."""
    
    # Continuation records
    continuations: List[ActionContinuation] = field(default_factory=list)
    """Records of identity continuations with revisions."""
    
    # Replacement records (where this identity is replaced or does replacing)
    replacements: List[ActionReplacement] = field(default_factory=list)
    """Replacement records involving this identity."""
    
    # Supersession records
    supersessions: List[ActionSupersession] = field(default_factory=list)
    """Supersession records involving this identity."""
    
    @property
    def history_id(self) -> str:
        """Return unique history identifier."""
        return f"history:{self.action_identity_id}"
    
    @property
    def is_empty(self) -> bool:
        """Check if history has no entries."""
        return (
            len(self.entries) == 0
            and len(self.continuations) == 0
            and len(self.replacements) == 0
            and len(self.supersessions) == 0
        )
    
    @property
    def current_state(self) -> str:
        """Get the current state from the last transition."""
        if self.entries:
            return self.entries[-1].to_state
        return "draft"
    
    def add_transition(self, transition: ActionTransition) -> "ActionHistory":
        """
        Add a transition to history (returns new immutable instance).
        
        Args:
            transition: The transition to add
            
        Returns:
            New ActionHistory with the transition added
        """
        return ActionHistory(
            action_identity_id=self.action_identity_id,
            entries=[*self.entries, transition],
            continuations=list(self.continuations),
            replacements=list(self.replacements),
            supersessions=list(self.supersessions),
        )
    
    def add_continuation(self, continuation: ActionContinuation) -> "ActionHistory":
        """
        Add a continuation to history (returns new immutable instance).
        
        Args:
            continuation: The continuation to add
            
        Returns:
            New ActionHistory with the continuation added
        """
        return ActionHistory(
            action_identity_id=self.action_identity_id,
            entries=list(self.entries),
            continuations=[*self.continuations, continuation],
            replacements=list(self.replacements),
            supersessions=list(self.supersessions),
        )
    
    def add_replacement(self, replacement: ActionReplacement) -> "ActionHistory":
        """
        Add a replacement to history (returns new immutable instance).
        
        Args:
            replacement: The replacement to add
            
        Returns:
            New ActionHistory with the replacement added
        """
        return ActionHistory(
            action_identity_id=self.action_identity_id,
            entries=list(self.entries),
            continuations=list(self.continuations),
            replacements=[*self.replacements, replacement],
            supersessions=list(self.supersessions),
        )
    
    def add_supersession(self, supersession: ActionSupersession) -> "ActionHistory":
        """
        Add a supersession to history (returns new immutable instance).
        
        Args:
            supersession: The supersession to add
            
        Returns:
            New ActionHistory with the supersession added
        """
        return ActionHistory(
            action_identity_id=self.action_identity_id,
            entries=list(self.entries),
            continuations=list(self.continuations),
            replacements=list(self.replacements),
            supersessions=[*self.supersessions, supersession],
        )
    
    def to_dict(self) -> dict:
        """Serialize to dictionary."""
        return {
            "action_identity_id": self.action_identity_id,
            "entries": [e.to_dict() for e in self.entries],
            "continuations": [c.to_dict() for c in self.continuations],
            "replacements": [r.to_dict() for r in self.replacements],
            "supersessions": [s.to_dict() for s in self.supersessions],
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> "ActionHistory":
        """Deserialize from dictionary."""
        return cls(
            action_identity_id=data.get("action_identity_id", ""),
            entries=[ActionTransition.from_dict(e) for e in data.get("entries", [])],
            continuations=[
                ActionContinuation.from_dict(c)
                for c in data.get("continuations", [])
            ],
            replacements=[
                ActionReplacement.from_dict(r)
                for r in data.get("replacements", [])
            ],
            supersessions=[
                ActionSupersession.from_dict(s)
                for s in data.get("supersessions", [])
            ],
        )


# =============================================================================
# ACTION LINEAGE - Immutable history graph
# =============================================================================

@dataclass(frozen=True)
class ActionLineage:
    """
    Complete immutable lineage graph for an Action.
    
    The lineage graph contains all historical information about an Action,
    including its identity, revisions, transitions, replacements, and
    supersessions. It is acyclic and append-only.
    
    Runtime-neutral: Yes
    Executable: No
    """
    
    # Canonical identity at the root
    action_identity_id: str = field(default="")
    """The canonical ActionIdentity for this lineage."""
    
    # Root revision
    root_revision_id: Optional[str] = None
    """First revision in this lineage (if any)."""
    
    # History log
    history: ActionHistory = field(default_factory=ActionHistory)
    """Complete history of all changes."""
    
    # Current state
    current_state: str = field(default="draft")
    """Current state of the action."""
    
    @property
    def lineage_id(self) -> str:
        """Return unique lineage identifier."""
        return f"lineage:{self.action_identity_id}"
    
    def is_acyclic(self) -> bool:
        """
        Verify that the lineage graph is acyclic.
        
        Returns:
            True if the lineage has no cycles
        """
        visited = set()
        current = self.root_revision_id
        
        while current:
            if current in visited:
                return False  # Cycle detected
            visited.add(current)
            
            # Find transitions from this revision
            transitions_from_current = [
                t for t in self.history.entries
                if t.from_state == current or t.to_state == current
            ]
            
            if len(transitions_from_current) > 1:
                # Multiple outgoing edges - potential cycle (simplified check)
                return False
            
            if not transitions_from_current:
                break  # End of chain
            
            current = transitions_from_current[0].to_state
        
        return True
    
    def add_continuation(self, continuation: ActionContinuation) -> "ActionLineage":
        """
        Add a continuation to the lineage.
        
        Args:
            continuation: The continuation to add
            
        Returns:
            New ActionLineage with the continuation added
        """
        return ActionLineage(
            action_identity_id=self.action_identity_id,
            root_revision_id=self.root_revision_id,
            history=self.history.add_continuation(continuation),
            current_state=continuation.new_revision_id,
        )
    
    def to_dict(self) -> dict:
        """Serialize to dictionary."""
        return {
            "action_identity_id": self.action_identity_id,
            "root_revision_id": self.root_revision_id,
            "current_state": self.current_state,
            "history": self.history.to_dict(),
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> "ActionLineage":
        """Deserialize from dictionary."""
        return cls(
            action_identity_id=data.get("action_identity_id", ""),
            root_revision_id=data.get("root_revision_id"),
            current_state=data.get("current_state", "draft"),
            history=ActionHistory.from_dict(data.get("history", {})),
        )


__all__ = [
    # Transition kinds
    "TransitionKind",
    
    # Core types
    "ActionDelta",
    "ActionTransition",
    "ActionContinuation",
    "ActionReplacement",
    "ActionSupersession",
    "ActionHistory",
    "ActionLineage",
]