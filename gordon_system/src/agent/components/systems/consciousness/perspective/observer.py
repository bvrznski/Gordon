# Gordon Phase 5.7.6-I: Perspective Engine - Observer
# ===============================================================================
"""
Canonical observer representation for the Perspective Engine.

The observer is the active computational entity that organizes perception,
anchors intentionality, and maintains conscious accessibility from a first-
person reference frame.
"""

from __future__ import annotations

from dataclasses import dataclass, field, replace as dataclass_replace
from typing import Tuple, Optional


def _generate_uuid() -> str:
    """Generate a short UUID-like identifier."""
    import uuid
    return uuid.uuid4().hex[:8]


# =============================================================================
# OBSERVER STATE
# =============================================================================

@dataclass(frozen=True)
class ObserverState:
    """
    Immutable observer state data.
    
    Observer state captures the current configuration and mode of the
    observer, determining how it organizes conscious contents.
    """
    
    state_id: str = field(default_factory=lambda: f"state-{_generate_uuid()}")
    """Unique identifier for this state."""
    
    active: bool = True
    """Whether the observer is currently active."""
    
    mode: str = "default"
    """Observer mode (default, external, simulated, hypothetical)."""
    
    # Attention properties
    attention_focused: Optional[str] = None
    """Currently focused attention target (if any)."""
    
    attention_width: float = 1.0
    """Attention span/width factor."""
    
    # Processing capacity
    max_active_items: int = 100
    """Maximum concurrent conscious items."""
    
    current_item_count: int = 0
    """Current number of active items."""
    
    @classmethod
    def default(cls) -> "ObserverState":
        """Return the default observer state."""
        return cls()
    
    @classmethod
    def external_observer(cls) -> "ObserverState":
        """Return an external observer state."""
        return cls(mode="external", attention_focused=None)
    
    @property
    def is_full(self) -> bool:
        """Check if observer capacity is reached."""
        return self.current_item_count >= self.max_active_items
    
    def with_focus(self, target: str) -> "ObserverState":
        """Return a copy with focused attention on target."""
        return dataclass_replace(self, attention_focused=target)
    
    def with_capacity_update(self, new_count: int) -> "ObserverState":
        """Return a copy with updated item count."""
        return dataclass_replace(
            self,
            current_item_count=new_count,
            active=new_count < self.max_active_items
        )


# =============================================================================
# OBSERVER REFERENCE
# =============================================================================

@dataclass(frozen=True)
class ObserverReference:
    """
    Immutable reference to an observer instance.
    
    This provides a stable identity for the observer without exposing
    internal state. External systems can use this reference to track
    observer changes across context generations.
    """
    
    observer_id: str = field(default_factory=lambda: f"observer-{_generate_uuid()}")
    """Unique identifier for this observer instance."""
    
    state_ref: Optional[str] = None
    """Reference to current observer state (if tracked)."""
    
    active_frame_ref: Optional[str] = None
    """Reference to current reference frame (if tracked)."""
    
    generation: int = 0
    """Current context generation when this reference was created."""
    
    timestamp_utc: float = field(default_factory=lambda: 0.0)
    """When this reference was created."""
    
    @classmethod
    def initial(cls) -> "ObserverReference":
        """Return an initial observer reference."""
        import time
        return cls(
            observer_id="observer-001",
            generation=0,
            timestamp_utc=time.time(),
        )
    
    def next_generation(self, new_state_ref: Optional[str] = None) -> "ObserverReference":
        """Return a copy for the next context generation."""
        import time
        return dataclass_replace(
            self,
            generation=self.generation + 1,
            state_ref=new_state_ref,
            timestamp_utc=time.time(),
        )


# =============================================================================
# OBSERVER (Main Class)
# =============================================================================

@dataclass
class Observer:
    """
    Canonical observer for perspective organization.
    
    The observer is the active computational entity that organizes conscious
    content. It establishes the reference frame, maintains attention focus,
    and coordinates access to conscious contents.
    
    Observer properties:
        - Immutable publications: State is never exposed directly
        - Active engagement: Organizes perception and intentionality
        - Continuity anchor: Maintains self-reference across transitions
        - Attention coordinator: Manages focused consciousness
    
    NOT responsible for:
        - Content evaluation or interpretation
        - Memory storage or retrieval
        - Planning or execution
        - Identity construction
    """
    
    # Core identity
    _observer_id: str = field(default_factory=lambda: f"observer-{_generate_uuid()}")
    """Internal observer instance ID."""
    
    _state: ObserverState = field(default_factory=ObserverState.default)
    """Current observer state."""
    
    # References (external tracking)
    _active_frame_ref: Optional[str] = None
    """Reference to current reference frame."""
    
    _current_generation: int = 0
    """Current context generation."""
    
    def __post_init__(self) -> None:
        """Initialize internal state after construction."""
        pass
    
    @property
    def observer_id(self) -> str:
        """Get the observer instance ID."""
        return self._observer_id
    
    @property
    def state(self) -> ObserverState:
        """Get a copy of the current observer state (immutable)."""
        return self._state
    
    @property
    def active_frame_reference(self) -> Optional[str]:
        """Get reference to current reference frame."""
        return self._active_frame_ref
    
    @property
    def current_generation(self) -> int:
        """Get current context generation."""
        return self._current_generation
    
    # ==========================================================================
    # STATE MANAGEMENT - Deterministic transitions only
    # ==========================================================================
    
    def switch_mode(self, new_mode: str) -> Tuple[bool, Optional[str]]:
        """
        Switch observer to a different mode.
        
        Args:
            new_mode: New observer mode (default, external, simulated, hypothetical)
            
        Returns:
            Tuple of (success, error_message if failed)
        """
        valid_modes = ("default", "external", "simulated", "hypothetical")
        if new_mode not in valid_modes:
            return False, f"Invalid mode: {new_mode}"
        
        self._state = dataclass_replace(self._state, mode=new_mode)
        return True, None
    
    def set_attention_focus(self, target: str) -> Tuple[bool, Optional[str]]:
        """
        Set attention focus to a specific target.
        
        Args:
            target: Target ID to focus on
            
        Returns:
            Tuple of (success, error_message if failed)
        """
        self._state = dataclass_replace(
            self._state,
            attention_focused=target
        )
        return True, None
    
    def clear_attention_focus(self) -> None:
        """Clear current attention focus."""
        self._state = dataclass_replace(
            self._state,
            attention_focused=None
        )
    
    def update_item_count(self, new_count: int) -> Tuple[bool, Optional[str]]:
        """
        Update the number of active conscious items.
        
        Args:
            new_count: New item count
            
        Returns:
            Tuple of (success, error_message if failed)
        """
        if new_count < 0:
            return False, "Item count cannot be negative"
        if new_count > self._state.max_active_items:
            return False, f"Item count exceeds capacity ({self._state.max_active_items})"
        
        self._state = dataclass_replace(
            self._state,
            current_item_count=new_count,
            active=new_count < self._state.max_active_items
        )
        return True, None
    
    def advance_generation(self) -> int:
        """
        Advance to next context generation.
        
        Returns:
            New generation number
        """
        self._current_generation += 1
        return self._current_generation
    
    # ==========================================================================
    # SNAPSHOTS - Immutable publications
    # ==========================================================================
    
    def get_reference(self) -> ObserverReference:
        """
        Get an immutable reference to current observer state.
        
        Returns:
            ObserverReference with bounded information
        """
        import time
        return ObserverReference(
            observer_id=self._observer_id,
            state_ref=None,  # State not exposed directly
            active_frame_ref=self._active_frame_ref,
            generation=self._current_generation,
            timestamp_utc=time.time(),
        )


# =============================================================================
# EXPORTS
# =============================================================================

__all__: Tuple[str, ...] = (
    "ObserverState",
    "ObserverReference",
    "Observer",
)