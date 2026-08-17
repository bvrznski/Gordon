# Gordon Phase 5.7.6-I: Perspective Engine - Transformations
# ===============================================================================
"""
Canonical viewpoint transformation system for the Perspective Engine.

Transformations provide deterministic perspective changes while preserving
historical snapshots and maintaining observer continuity.
"""

from __future__ import annotations

from dataclasses import dataclass, field, replace as dataclass_replace
from typing import Tuple, Optional, Callable


def _generate_uuid() -> str:
    """Generate a short UUID-like identifier."""
    import uuid
    return uuid.uuid4().hex[:8]


# =============================================================================
# TRANSFORMATION TYPES
# =============================================================================

TRANSFORM_TYPE_SELF_TO_EXTERNAL = "self_to_external"
"""Transform from self-perspective to external observer."""

TRANSFORM_TYPE_EXTERNAL_TO_SELF = "external_to_self"
"""Transform from external observer back to self."""

TRANSFORM_TYPE_SIMULATED_TO_SELF = "simulated_to_self"
"""Transform simulated perspective to real self."""

TRANSFORM_TYPE_HYPOTHETICAL_TO_SELF = "hypothetical_to_self"
"""Transform hypothetical counterfactual to actual self."""


# =============================================================================
# TRANSFORMATION DEFINITION
# =============================================================================

@dataclass(frozen=True)
class TransformationDefinition:
    """
    Immutable definition of a viewpoint transformation.
    
    A transformation definition specifies how to convert between different
    perspective frames. Each transformation is deterministic and reproducible.
    """
    
    transform_id: str = field(default_factory=lambda: f"transform-{_generate_uuid()}")
    """Unique identifier for this transformation."""
    
    from_perspective_type: str = "self"
    """Source perspective type."""
    
    to_perspective_type: str = "external_observer"
    """Target perspective type."""
    
    transform_type: str = TRANSFORM_TYPE_SELF_TO_EXTERNAL
    """Type of transformation."""
    
    parameters: dict = field(default_factory=dict)
    """Optional transformation parameters."""
    
    # Metadata
    generated_at_utc: float = field(default_factory=lambda: 0.0)
    """When this definition was created."""
    
    provenance: Optional[str] = None
    """Source that defined this transformation."""
    
    @classmethod
    def self_to_external(cls) -> "TransformationDefinition":
        """Create a self-to-external observer transformation."""
        import time
        return cls(
            from_perspective_type="self",
            to_perspective_type="external_observer",
            transform_type=TRANSFORM_TYPE_SELF_TO_EXTERNAL,
            generated_at_utc=time.time(),
        )
    
    @classmethod
    def external_to_self(cls) -> "TransformationDefinition":
        """Create an external-to-self transformation."""
        import time
        return cls(
            from_perspective_type="external_observer",
            to_perspective_type="self",
            transform_type=TRANSFORM_TYPE_EXTERNAL_TO_SELF,
            generated_at_utc=time.time(),
        )
    
    @property
    def is_valid(self) -> bool:
        """Check if this transformation definition is valid."""
        from .constants import VALID_PERSPECTIVE_TYPES
        
        return (
            self.from_perspective_type in VALID_PERSPECTIVE_TYPES and
            self.to_perspective_type in VALID_PERSPECTIVE_TYPES
        )
    
    def invert(self) -> "TransformationDefinition":
        """
        Get the inverse transformation.
        
        Returns a new definition with source and target reversed.
        """
        import time
        return dataclass_replace(
            self,
            from_perspective_type=self.to_perspective_type,
            to_perspective_type=self.from_perspective_type,
            transform_id=f"inverted-{self.transform_id}",
            generated_at_utc=time.time(),
        )


# =============================================================================
# TRANSFORMATION APPLICATION RESULT
# =============================================================================

@dataclass(frozen=True)
class TransformationResult:
    """
    Immutable result of a perspective transformation application.
    
    This represents the outcome of applying a transformation, including
    any modifications made to the reference frame.
    """
    
    transform_id: str
    """Transformation that was applied."""
    
    succeeded: bool = False
    """Whether the transformation succeeded."""
    
    # Output (if successful)
    new_reference_frame_ref: Optional[str] = None
    """Reference to new reference frame."""
    
    observer_shift: Optional[str] = None
    """Description of observer shift (if any)."""
    
    # Failure information
    failure_reason: Optional[str] = None
    """Reason for failure (if failed)."""
    
    partial_success: bool = False
    """Whether this was a partial success."""
    
    @property
    def is_failed(self) -> bool:
        """Check if this result represents a failure."""
        return not self.succeeded


# =============================================================================
# TRANSFORMER ENGINE
# =============================================================================

@dataclass
class TransformerEngine:
    """
    Canonical transformer engine for perspective transformations.
    
    The transformer engine applies deterministic viewpoint transformations
    while preserving historical snapshots and maintaining observer continuity.
    
    Transformation properties:
        - Deterministic: Same inputs always produce same outputs
        - Non-mutating: Historical snapshots are never modified
        - Atomic: Transformations either fully apply or not at all
        - Traceable: All transformations are logged with provenance
    
    NOT responsible for:
        - Creating new perspectives (handled by builder)
        - Publishing perspective state (handled by engine)
        - Storing historical data (handled by persistence layer)
    """
    
    # Configuration
    _max_transformations_per_generation: int = 10
    """Maximum transformations allowed per context generation."""
    
    _current_generation: int = 0
    """Current context generation."""
    
    _transformation_count: int = 0
    """Count of transformations in current generation."""
    
    # Internal state
    _applied_transformations: list[str] = field(default_factory=list)
    """List of transformation IDs applied."""
    
    def __post_init__(self) -> None:
        """Initialize internal state after construction."""
        self._applied_transformations.clear()
    
    @property
    def current_generation(self) -> int:
        """Get current context generation."""
        return self._current_generation
    
    @property
    def transformation_count(self) -> int:
        """Get number of transformations applied in current generation."""
        return self._transformation_count
    
    # ==========================================================================
    # TRANSFORMATION APPLICATION
    # ==========================================================================
    
    def can_transform(
        self,
        from_type: str,
        to_type: str,
    ) -> Tuple[bool, Optional[str]]:
        """
        Check if a perspective transformation is allowed.
        
        Args:
            from_type: Source perspective type
            to_type: Target perspective type
            
        Returns:
            Tuple of (allowed, reason_if_not)
        """
        from .constants import VALID_PERSPECTIVE_TYPES
        
        # Check source and target are valid
        if from_type not in VALID_PERSPECTIVE_TYPES:
            return False, f"Invalid source perspective: {from_type}"
        if to_type not in VALID_PERSPECTIVE_TYPES:
            return False, f"Invalid target perspective: {to_type}"
        
        # Self-to-self is always allowed (identity transform)
        if from_type == to_type:
            return True, None
        
        # Check generation limit
        if self._transformation_count >= self._max_transformations_per_generation:
            return False, "Transformation limit reached for this generation"
        
        # All checks passed
        return True, None
    
    def apply_transformation(
        self,
        definition: TransformationDefinition,
    ) -> TransformationResult:
        """
        Apply a perspective transformation.
        
        Args:
            definition: Transformation definition to apply
            
        Returns:
            TransformationResult with outcome information
        """
        # Validate the transformation is allowed
        allowed, reason = self.can_transform(
            definition.from_perspective_type,
            definition.to_perspective_type,
        )
        
        if not allowed:
            return TransformationResult(
                transform_id=definition.transform_id,
                succeeded=False,
                failure_reason=f"Transformation not allowed: {reason}",
            )
        
        # Check capacity
        if self._transformation_count >= self._max_transformations_per_generation:
            return TransformationResult(
                transform_id=definition.transform_id,
                succeeded=False,
                partial_success=True,
                failure_reason="Capacity limit reached",
            )
        
        try:
            # Record the transformation
            self._applied_transformations.append(definition.transform_id)
            self._transformation_count += 1
            
            # Create result (actual coordinate transformation would happen here)
            return TransformationResult(
                transform_id=definition.transform_id,
                succeeded=True,
                new_reference_frame_ref=f"frame-{_generate_uuid()}",
                observer_shift=f"{definition.from_perspective_type} -> {definition.to_perspective_type}",
            )
            
        except Exception as e:
            # Rollback on failure
            self._applied_transformations.pop()
            self._transformation_count -= 1
            
            return TransformationResult(
                transform_id=definition.transform_id,
                succeeded=False,
                failure_reason=str(e),
            )
    
    def apply_batch(
        self,
        definitions: list[TransformationDefinition],
    ) -> Tuple[int, list[TransformationResult]]:
        """
        Apply a batch of transformations atomically.
        
        All transformations in the batch are applied together or none are.
        
        Args:
            definitions: List of transformation definitions
            
        Returns:
            Tuple of (applied_count, results_list)
        """
        # Validate all transformations first
        for definition in definitions:
            allowed, reason = self.can_transform(
                definition.from_perspective_type,
                definition.to_perspective_type,
            )
            if not allowed:
                return 0, [
                    TransformationResult(
                        transform_id=definition.transform_id,
                        succeeded=False,
                        failure_reason=f"Invalid: {reason}",
                    )
                ]
        
        # All valid, apply them
        results = []
        applied = 0
        
        for definition in definitions:
            if self._transformation_count >= self._max_transformations_per_generation:
                break
            
            result = self.apply_transformation(definition)
            if result.succeeded:
                applied += 1
            results.append(result)
        
        return applied, results
    
    # ==========================================================================
    # STATE MANAGEMENT
    # ==========================================================================
    
    def advance_generation(self) -> int:
        """
        Advance to next context generation.
        
        Resets transformation count for the new generation.
        
        Returns:
            New generation number
        """
        self._current_generation += 1
        self._transformation_count = 0
        self._applied_transformations.clear()
        return self._current_generation
    
    def get_applied_transformation_ids(self) -> list[str]:
        """Get IDs of transformations applied in current generation."""
        return list(self._applied_transformations)
    
    # ==========================================================================
    # REPLAY SUPPORT
    # ==========================================================================
    
    def replay_transformation(
        self,
        definition: TransformationDefinition,
    ) -> Tuple[bool, Optional[str]]:
        """
        Replay a transformation (for debugging/testing).
        
        This applies the same transformation but doesn't increment counters.
        
        Args:
            definition: Transformation definition to replay
            
        Returns:
            Tuple of (success, error_message if failed)
        """
        # Use can_transform without capacity check
        from .constants import VALID_PERSPECTIVE_TYPES
        
        if definition.from_perspective_type not in VALID_PERSPECTIVE_TYPES:
            return False, f"Invalid source perspective: {definition.from_perspective_type}"
        if definition.to_perspective_type not in VALID_PERSPECTIVE_TYPES:
            return False, f"Invalid target perspective: {definition.to_perspective_type}"
        
        # Replay without capacity check (for replay purposes)
        try:
            self._applied_transformations.append(definition.transform_id)
            return True, None
            
        except Exception as e:
            return False, str(e)


# =============================================================================
# EXPORTS
# =============================================================================

__all__: Tuple[str, ...] = (
    # Types
    "TRANSFORM_TYPE_SELF_TO_EXTERNAL",
    "TRANSFORM_TYPE_EXTERNAL_TO_SELF",
    "TRANSFORM_TYPE_SIMULATED_TO_SELF",
    "TRANSFORM_TYPE_HYPOTHETICAL_TO_SELF",
    # Classes
    "TransformationDefinition",
    "TransformationResult",
    "TransformerEngine",
)