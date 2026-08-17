# Gordon Phase 5.7.4-I: Temporal Context Engine - Continuity Window
# ===============================================================================
"""
Continuity window module for bounded temporal context organization.
"""

from __future__ import annotations

import time
from dataclasses import dataclass, field
from typing import Tuple, Dict, Optional

from gordon.agent.components.systems.consciousnessretention import RetentionRecord, RetentionRegistry
from gordon.agent.components.systems.consciousnesspresentation import PresentationReference, PresentationValidator
from gordon.agent.components.systems.consciousnessprotention import ProtentionExpectation, ProtentionSet


@dataclass(frozen=True)
class ContinuityWindow:
    """
    Immutable bounded continuity window for a single conscious context.
    
    A continuity window defines the temporal scope of a conscious context,
    including its history (retention), present (presentation), and immediate
    future (protention).
    
    Key properties:
        - Bounded: Limited by MAX_CONTINUITY_WINDOW_SIZE generations
        - Deterministic: Same inputs produce identical outputs
        - Provenance-preserving: Maintains lineage tracking
    """
    
    window_id: str = field(default_factory=lambda: f"cw-{time.time()}")
    """Unique identifier for this continuity window."""
    
    # Temporal components
    retention_references: Tuple[str, ...] = field(default_factory=tuple)
    """References to previous generation contexts (retention)."""
    
    presentation_reference: Optional[str] = None
    """Reference to current Experiential Field context (presentation)."""
    
    protention_expectations: Tuple[str, ...] = field(default_factory=tuple)
    """Expectations about immediate forthcoming context (protention)."""
    
    # Versioning
    start_generation: int = 0
    """Generation when this window was created."""
    
    current_generation: int = 0
    """Current generation within the window."""
    
    # Status and timing
    state: str = "active"
    """Window state (active, paused, closed, degraded)."""
    
    created_at_utc: float = field(default_factory=time.time)
    """When this window was created."""
    
    last_updated_utc: float = field(default_factory=time.time)
    """Last update timestamp."""
    
    # Integrity
    provenance: Optional[str] = None
    """Provenance chain for continuity tracking."""
    
    trust_summary: str = "medium"
    """Summary trust level of all temporal references."""
    
    @classmethod
    def initial(
        cls,
        field_context_id: str,
        start_generation: int = 0,
    ) -> "ContinuityWindow":
        """
        Create an initial continuity window.
        
        Args:
            field_context_id: Current EF context ID
            start_generation: Starting generation number
            
        Returns:
            New ContinuityWindow with empty retention, single presentation
        """
        return cls(
            presentation_reference=field_context_id,
            start_generation=start_generation,
            current_generation=start_generation,
        )
    
    def next_generation(
        self,
        new_presentation_ref: str,
        new_retention_refs: Tuple[str, ...] = tuple(),
        new_protentions: Tuple[str, ...] = tuple(),
    ) -> "ContinuityWindow":
        """
        Create a new generation continuity window.
        
        Args:
            new_presentation_ref: New EF context reference
            new_retention_refs: Additional retention references
            new_protentions: Protentional expectations for next context
            
        Returns:
            New ContinuityWindow with incremented generation
        """
        # Combine existing and new retention references
        all_retentions = self.retention_references + new_retention_refs
        
        return ContinuityWindow(
            window_id=self.window_id,  # Same ID for continuity
            retention_references=all_retentions[-10:],  # Bounded to 10
            presentation_reference=new_presentation_ref,
            protention_expectations=new_protentions[:5],  # Bounded to 5
            start_generation=self.start_generation,
            current_generation=self.current_generation + 1,
            state="active",
            last_updated_utc=time.time(),
        )
    
    def pause(self) -> "ContinuityWindow":
        """Return a paused version of this window."""
        return dataclass_replace(
            self, state="paused", last_updated_utc=time.time()
        )
    
    def resume(self) -> "ContinuityWindow":
        """Return a resumed (active) version of this window."""
        return dataclass_replace(
            self, state="active", last_updated_utc=time.time()
        )
    
    def close(self) -> "ContinuityWindow":
        """Return a closed version of this window."""
        return dataclass_replace(
            self, state="closed", last_updated_utc=time.time()
        )
    
    @property
    def history_size(self) -> int:
        """Get the current size of the retention history."""
        return len(self.retention_references)
    
    @property
    def is_empty(self) -> bool:
        """Check if this window has no content."""
        return (
            self.presentation_reference is None
            and len(self.protention_expectations) == 0
        )
    
    @property
    def is_valid(self) -> bool:
        """Check if this window's state indicates validity."""
        return self.state in ("active", "paused")


def dataclass_replace(instance, **kwargs):
    """Helper to create a new dataclass instance with modified fields."""
    import dataclasses
    return type(instance)(
        **{**dataclasses.asdict(instance), **kwargs}
    )


class ContinuityWindowManager:
    """
    Manager for continuity windows.
    
    Coordinates multiple windows and ensures proper lifecycle management,
    including transitions, state changes, and cleanup.
    """
    
    def __init__(self):
        """Initialize the manager."""
        self._windows: Dict[str, ContinuityWindow] = {}
        self._active_window_id: Optional[str] = None
    
    @property
    def active_window(self) -> Optional[ContinuityWindow]:
        """Get the currently active continuity window."""
        if self._active_window_id is None:
            return None
        return self._windows.get(self._active_window_id)
    
    @property
    def window_count(self) -> int:
        """Get the total number of managed windows."""
        return len(self._windows)
    
    def create_window(
        self,
        field_context_id: str,
        start_generation: int = 0,
    ) -> Tuple[bool, Optional[str], Optional[ContinuityWindow]]:
        """
        Create a new continuity window.
        
        Args:
            field_context_id: Current EF context ID
            start_generation: Starting generation number
            
        Returns:
            Tuple of (success, error_message, window if successful)
        """
        new_window = ContinuityWindow.initial(
            field_context_id=field_context_id,
            start_generation=start_generation,
        )
        
        self._windows[new_window.window_id] = new_window
        self._active_window_id = new_window.window_id
        
        return True, None, new_window
    
    def get_window(self, window_id: str) -> Optional[ContinuityWindow]:
        """Get a window by its ID."""
        return self._windows.get(window_id)
    
    def set_active(self, window_id: str) -> Tuple[bool, Optional[str]]:
        """
        Set a window as the active window.
        
        Args:
            window_id: Window to activate
            
        Returns:
            Tuple of (success, error_message if failed)
        """
        if window_id not in self._windows:
            return False, f"Window {window_id} not found"
        
        self._active_window_id = window_id
        return True, None
    
    def advance_generation(
        self,
        new_presentation_ref: str,
        new_retention_refs: Tuple[str, ...] = tuple(),
        new_protentions: Tuple[str, ...] = tuple(),
    ) -> Tuple[bool, Optional[str], Optional[ContinuityWindow]]:
        """
        Advance the active window to a new generation.
        
        Args:
            new_presentation_ref: New EF context reference
            new_retention_refs: Additional retention references
            new_protentions: Protentional expectations
            
        Returns:
            Tuple of (success, error_message, new_window if successful)
        """
        current = self.active_window
        if current is None:
            return False, "No active window to advance", None
        
        # Check state - cannot advance if closed or degraded
        if current.state == "closed":
            return False, "Cannot advance closed window", None
        if current.state == "degraded":
            return False, "Cannot advance degraded window", None
        
        new_window = current.next_generation(
            new_presentation_ref=new_presentation_ref,
            new_retention_refs=new_retention_refs,
            new_protentions=new_protentions,
        )
        
        self._windows[new_window.window_id] = new_window
        self._active_window_id = new_window.window_id
        
        return True, None, new_window
    
    def pause_active(self) -> Tuple[bool, Optional[str]]:
        """Pause the active window."""
        current = self.active_window
        if current is None:
            return False, "No active window to pause"
        
        paused = current.pause()
        self._windows[paused.window_id] = paused
        return True, None
    
    def resume_active(self) -> Tuple[bool, Optional[str]]:
        """Resume the active window."""
        current = self.active_window
        if current is None:
            return False, "No active window to resume"
        
        resumed = current.resume()
        self._windows[resumed.window_id] = resumed
        return True, None
    
    def close_active(self) -> Tuple[bool, Optional[str]]:
        """Close the active window."""
        current = self.active_window
        if current is None:
            return False, "No active window to close"
        
        closed = current.close()
        self._windows[closed.window_id] = closed
        return True, None


@dataclass
class ContinuityWindowBuilder:
    """
    Builder for constructing continuity windows incrementally.
    
    Provides a fluent interface for building windows with proper validation.
    """
    
    window_id: Optional[str] = None
    """Optional window ID (generated if not provided)."""
    
    retention_references: Tuple[str, ...] = tuple()
    """Retention references."""
    
    presentation_reference: Optional[str] = None
    """Presentation reference."""
    
    protention_expectations: Tuple[str, ...] = tuple()
    """Protentional expectations."""
    
    start_generation: int = 0
    """Starting generation number."""
    
    current_generation: int = 0
    """Current generation number."""
    
    state: str = "active"
    """Window state."""
    
    def set_presentation(self, ref: str) -> "ContinuityWindowBuilder":
        """Set the presentation reference."""
        self.presentation_reference = ref
        return self
    
    def add_retention(self, ref: str) -> "ContinuityWindowBuilder":
        """Add a retention reference."""
        self.retention_references += (ref,)
        return self
    
    def add_protention(self, expectation: ProtentionExpectation) -> "ContinuityWindowBuilder":
        """Add a protentional expectation."""
        # Extract the expectation ID or content reference
        if expectation.expected_content_reference:
            self.protention_expectations += (
                expectation.expected_content_reference,
            )
        return self
    
    def set_generation(self, generation: int) -> "ContinuityWindowBuilder":
        """Set the current generation number."""
        self.current_generation = generation
        return self
    
    def build(self) -> ContinuityWindow:
        """
        Build and validate the continuity window.
        
        Returns:
            New ContinuityWindow
            
        Raises:
            ValueError: If required fields are missing or validation fails
        """
        if self.presentation_reference is None:
            raise ValueError("Presentation reference is required")
        
        return ContinuityWindow(
            window_id=self.window_id or f"cw-{time.time()}",
            retention_references=self.retention_references,
            presentation_reference=self.presentation_reference,
            protention_expectations=self.protention_expectations,
            start_generation=self.start_generation,
            current_generation=self.current_generation,
            state=self.state,
        )


__all__: Tuple[str, ...] = (
    "ContinuityWindow",
    "ContinuityWindowManager",
    "ContinuityWindowBuilder",
)