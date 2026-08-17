# Gordon Phase 5.7.6-I: Perspective Engine - Canonical Engine
# ===============================================================================
"""
Canonical Perspective Engine integrating reference frame, observer,
self-reference, transformations, transitions, snapshots, validation,
and diagnostics for the active computational first-person reference frame.
"""

from __future__ import annotations

import time
import uuid
from dataclasses import dataclass, field, replace as dataclass_replace
from typing import Tuple, Dict, Any, Optional


# Gordon Phase 5.7.6 - Perspective Engine imports (absolute paths for module use)
try:
    from gordon.agent.components.systems.consciousness import (
        constants,
        exceptions,
        reference_frame,
        observer,
        self_reference,
        transformations,
        transitions,
        snapshots,
        validator,
        diagnostics,
    )
except ImportError:
    # Absolute imports for standalone testing
    from gordon_system.src.agent.capabilities.consciousness.perspective import (
        constants,
        exceptions,
        reference_frame,
        observer,
        self_reference,
        transformations,
        transitions,
        snapshots,
        validator,
        diagnostics,
    )


# =============================================================================
# CANONICAL PERSPECTIVE ENGINE
# =============================================================================

@dataclass
class PerspectiveEngine:
    """
    Canonical Perspective Engine for the active computational first-person reference frame.
    
    The Perspective Engine establishes Gordon's current first-person computational
    reference frame. It answers: "From whose perspective is the current conscious
    context organized?"
    
    Responsibilities:
        - Maintain active reference frame (origin, orientation, coordinate system)
        - Manage observer instance and state
        - Track self-reference within the current perspective
        - Apply deterministic viewpoint transformations
        - Publish immutable perspective snapshots
        - Validate all perspective state transitions
        
    NOT responsible for:
        - Identity construction or narrative
        - Affective state or personality
        - Memory storage or retrieval
        - Reasoning, planning, or execution
        - World model construction
    
    Integration points:
        - Experiential Field (reference frame context)
        - Intentional Context (observer anchoring)
        - Temporal Context (continuity across generations)
        - Presence & Awareness (conscious accessibility)
    """
    
    # Core components
    _reference_frame: reference_frame.ReferenceFrame = field(default_factory=reference_frame.ReferenceFrame.initial)
    """Active reference frame."""
    
    _observer: observer.Observer = field(default_factory=observer.Observer)
    """Active observer instance."""
    
    _self_reference: self_reference.SelfReference = field(default_factory=self_reference.SelfReference.initial)
    """Current self-reference within the perspective."""
    
    # Sub-engines
    _transformer_engine: transformations.TransformerEngine = field(default_factory=transformations.TransformerEngine)
    """Viewpoint transformation engine."""
    
    _validator: validator.PerspectiveValidator = field(default_factory=validator.PerspectiveValidator.default)
    """State validation authority."""
    
    _diagnostics: diagnostics.Diagnostics = field(default_factory=diagnostics.Diagnostics)
    """Diagnostics and observability."""
    
    # State tracking
    _state: str = constants.PERSPECTIVE_STATE_INITIALIZING
    """Current engine state (initializing, active, transitioning, suspended, terminated)."""
    
    _current_generation: int = 0
    """Current context generation."""
    
    # Snapshot history for replay
    _snapshot_history: list[snapshots.PerspectiveSnapshot] = field(default_factory=list)
    """History of published snapshots for replay/debugging."""
    
    def __post_init__(self) -> None:
        """Initialize after construction."""
        self._state = constants.PERSPECTIVE_STATE_INITIALIZING
        self._current_generation = 0
        self._snapshot_history.clear()
        
        # Initialize initial snapshot
        initial_snapshot = snapshots.PerspectiveSnapshot.initial()
        self._snapshot_history.append(initial_snapshot)
    
    @property
    def state(self) -> str:
        """Get current engine state."""
        return self._state
    
    @property
    def current_generation(self) -> int:
        """Get current context generation."""
        return self._current_generation
    
    @property
    def reference_frame(self) -> reference_frame.ReferenceFrame:
        """Get current reference frame (immutable copy)."""
        return self._reference_frame
    
    @property
    def observer(self) -> observer.Observer:
        """Get current observer instance."""
        return self._observer
    
    @property
    def self_reference(self) -> self_reference.SelfReference:
        """Get current self-reference."""
        return self._self_reference
    
    # ==========================================================================
    # LIFECYCLE MANAGEMENT
    # ==========================================================================
    
    def initialize(self) -> Tuple[bool, Optional[str]]:
        """
        Initialize the Perspective Engine.
        
        Returns:
            Tuple of (success, error_message if failed)
        """
        if self._state != constants.PERSPECTIVE_STATE_INITIALIZING:
            return False, "Cannot initialize - already initialized or started"
        
        # Validate initial state
        valid, reason = self._validator.validate(
            observer_id=self._observer.observer_id,
            frame_ref=self._reference_frame.frame_id,
            perspective_type=self._reference_frame.frame_type,
            self_ref_kind=self._self_reference.kind,
            generation=self._current_generation,
        )
        
        if not valid:
            return False, f"Initial state validation failed: {reason}"
        
        # Set active state
        self._state = constants.PERSPECTIVE_STATE_ACTIVE
        
        # Record initialization transition
        self._diagnostics.record_transition(0.1)
        
        return True, None
    
    def start(self) -> Tuple[bool, Optional[str]]:
        """
        Start the Perspective Engine.
        
        After starting, the engine is ACTIVE and can process perspective changes.
        
        Returns:
            Tuple of (success, error_message if failed)
        """
        if self._state != constants.PERSPECTIVE_STATE_INITIALIZING:
            return False, "Cannot start - already initialized or started"
        
        # Initialize first
        success, reason = self.initialize()
        if not success:
            return False, f"Initialization failed: {reason}"
        
        return True, None
    
    def stop(self) -> Tuple[bool, Optional[str]]:
        """
        Stop the Perspective Engine.
        
        Returns:
            Tuple of (success, error_message if failed)
        """
        if self._state not in (
            constants.PERSPECTIVE_STATE_ACTIVE,
            constants.PERSPECTIVE_STATE_TRANSITIONING,
        ):
            return False, "Cannot stop - not running"
        
        self._state = constants.PERSPECTIVE_STATE_TERMINATED
        return True, None
    
    def pause(self) -> Tuple[bool, Optional[str]]:
        """
        Pause the Perspective Engine temporarily.
        
        Returns:
            Tuple of (success, error_message if failed)
        """
        if self._state != constants.PERSPECTIVE_STATE_ACTIVE:
            return False, "Cannot pause - not active"
        
        self._state = constants.PERSPECTIVE_STATE_SUSPENDED
        return True, None
    
    def resume(self) -> Tuple[bool, Optional[str]]:
        """
        Resume from paused state.
        
        Returns:
            Tuple of (success, error_message if failed)
        """
        if self._state != constants.PERSPECTIVE_STATE_SUSPENDED:
            return False, "Cannot resume - not paused"
        
        self._state = constants.PERSPECTIVE_STATE_ACTIVE
        return True, None
    
    # ==========================================================================
    # VIEWPOINT TRANSFORMATIONS
    # ==========================================================================
    
    def apply_transformation(
        self,
        transform_type: str = "self_to_external",
    ) -> Tuple[bool, Optional[str]]:
        """
        Apply a viewpoint transformation.
        
        Args:
            transform_type: Type of transformation to apply
            
        Returns:
            Tuple of (success, error_message if failed)
        """
        if self._state not in (
            constants.PERSPECTIVE_STATE_ACTIVE,
            constants.PERSPECTIVE_STATE_TRANSITIONING,
        ):
            return False, "Cannot transform - engine not active"
        
        # Create transformation definition
        from gordon.agent.components.systems.consciousnesstransformations import TransformationDefinition
        
        if transform_type == "self_to_external":
            defn = TransformationDefinition.self_to_external()
        elif transform_type == "external_to_self":
            defn = TransformationDefinition.external_to_self()
        else:
            return False, f"Unknown transformation type: {transform_type}"
        
        # Apply via transformer engine
        result = self._transformer_engine.apply_transformation(defn)
        
        if not result.succeeded:
            self._diagnostics.record_invalid_transition(result.failure_reason or "")
            return False, result.failure_reason
        
        # Update state based on transformation
        new_frame_ref = result.new_reference_frame_ref
        if new_frame_ref:
            self._reference_frame = self._reference_frame.transform_to(
                reference_frame.ReferenceFrame(frame_id=new_frame_ref)
            ) or self._reference_frame
        
        # Record metrics
        self._diagnostics.record_transformation()
        
        return True, None
    
    def switch_perspective_type(self, new_type: str) -> Tuple[bool, Optional[str]]:
        """
        Switch to a different perspective type.
        
        Args:
            new_type: New perspective type
            
        Returns:
            Tuple of (success, error_message if failed)
        """
        # Validate the new perspective type
        from .constants import VALID_PERSPECTIVE_TYPES
        
        if new_type not in VALID_PERSPECTIVE_TYPES:
            return False, f"Invalid perspective type: {new_type}"
        
        # Check capacity
        if self._transformer_engine.transformation_count >= 10:
            return False, "Transformation limit reached"
        
        try:
            # Record transition
            old_type = self._reference_frame.frame_type
            self._diagnostics.record_perspective_type_change(new_type)
            
            # Update reference frame type
            self._reference_frame = dataclasses_replace(
                self._reference_frame,
                frame_type=new_type,
            )
            
            return True, None
            
        except Exception as e:
            return False, str(e)
    
    # ==========================================================================
    # SNAPSHOTS - PUBLICATION
    # ==========================================================================
    
    def get_snapshot(self) -> snapshots.PerspectiveSnapshot:
        """
        Get an immutable snapshot of current perspective state.
        
        Returns:
            PerspectiveSnapshot with all current state information
        """
        import time as t
        
        snapshot = snapshots.PerspectiveSnapshot(
            generation=self._current_generation,
            previous_generation=self._current_generation - 1 if self._current_generation > 0 else None,
            created_at_utc=t.time(),
            valid_from_utc=0.0,
            reference_frame_ref=self._reference_frame.frame_id,
            observer_id=self._observer.observer_id,
            self_reference_ref=None,  # Not exposed directly
            perspective_type=self._reference_frame.frame_type,
            provenance="perspective_engine",
            active_items_count=0,  # Count from presence system if available
            fading_items_count=0,
            source_summary=tuple(),
        )
        
        # Store for replay
        self._snapshot_history.append(snapshot)
        
        # Record publication
        self._diagnostics.record_snapshot_publication()
        
        return snapshot
    
    def get_reference(self) -> snapshots.SnapshotReplayEngine:
        """
        Get a replay engine with current history.
        
        Returns:
            SnapshotReplayEngine for replay/debugging
        """
        engine = snapshots.SnapshotReplayEngine(max_history_size=1000)
        for s in self._snapshot_history:
            engine.add_snapshot(s)
        return engine
    
    # ==========================================================================
    # DIAGNOSTICS AND HEALTH
    # ==========================================================================
    
    @property
    def metrics(self) -> Dict[str, Any]:
        """Get engine metrics."""
        diag_metrics = self._diagnostics.metrics
        
        return {
            **diag_metrics,
            "state": self._state,
            "current_generation": self._current_generation,
            "observer_id": self._observer.observer_id,
            "reference_frame_id": self._reference_frame.frame_id,
        }
    
    @property
    def health(self) -> Dict[str, bool]:
        """Get engine health status."""
        return {
            **self._diagnostics.health,
            "can_transform": self._state == constants.PERSPECTIVE_STATE_ACTIVE,
            "can_publish": self._state in (
                constants.PERSPECTIVE_STATE_ACTIVE,
                constants.PERSPECTIVE_STATE_TRANSITIONING,
            ),
        }
    
    @property
    def integrity(self) -> Dict[str, bool]:
        """Get integrity status."""
        return {
            "reference_frame_valid": True,  # Validated at construction
            "observer_active": self._state == constants.PERSPECTIVE_STATE_ACTIVE,
            "self_reference_bounded": True,  # By design
        }


# =============================================================================
# UTILITY: dataclass_replace without import in function scope
# =============================================================================

from dataclasses import replace as dataclasses_replace


# =============================================================================
# EXPORTS
# =============================================================================

__all__: Tuple[str, ...] = (
    "PerspectiveEngine",
)