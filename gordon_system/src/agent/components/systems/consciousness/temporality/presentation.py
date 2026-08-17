# Gordon Phase 5.7.4-I: Temporal Context Engine - Presentation
# ===============================================================================
"""
Presentation module for current Experiential Field reference.
"""

from __future__ import annotations

import time
from dataclasses import dataclass, field
from typing import Tuple, Optional


@dataclass(frozen=True)
class PresentationReference:
    """
    Immutable reference to the current Experiential Field snapshot.
    
    Presentation represents the explicit temporal anchor - the current conscious
    context. It never duplicates the field; it only references it.
    
    Key properties:
        - Reference-only: Never owns or copies EF data
        - Current-generation: Points to the active EF generation
        - Canonical anchor: Serves as the temporal present point
    """
    
    # Required fields first (no defaults)
    field_context_id: str
    """Context ID of the referenced Experiential Field."""
    
    field_generation: int = 0
    """Generation number of the referenced EF snapshot."""
    
    # Fields with defaults after
    presentation_id: str = field(default_factory=lambda: f"pres-{time.time()}")
    """Unique identifier for this presentation reference."""
    
    timestamp_utc: float = field(default_factory=time.time)
    """When this presentation reference was created."""
    
    @classmethod
    def from_field_snapshot(
        cls,
        field_context_id: Optional[str] = None,
        context_id: Optional[str] = None,
        generation: int = 0,
    ) -> "PresentationReference":
        """
        Create a presentation reference from an Experiential Field snapshot.
        
        Args:
            context_id: EF context ID to reference
            generation: EF generation number
            
        Returns:
            New PresentationReference pointing to the field
        """
        # Support both parameter names for backward compatibility
        fcid = field_context_id or context_id
        return cls(
            field_context_id=fcid if fcid else "",
            field_generation=generation,
        )


class PresentationValidator:
    """
    Validator for presentation references.
    
    Ensures that presentation references are valid and properly bound
    to current Experiential Field state.
    """
    
    def __init__(self):
        """Initialize the validator."""
        self._last_validated_field_generation: Optional[int] = None
    
    @property
    def last_validated_generation(self) -> Optional[int]:
        """Get the last validated field generation."""
        return self._last_validated_field_generation
    
    def validate_reference(
        self,
        reference: PresentationReference,
        expected_generation: int,
    ) -> Tuple[bool, Optional[str]]:
        """
        Validate a presentation reference against expected state.
        
        Args:
            reference: The presentation reference to validate
            expected_generation: Expected current EF generation
            
        Returns:
            Tuple of (is_valid, error_message if invalid)
        """
        # Check that the field context ID is not empty
        if not reference.field_context_id:
            return False, "Field context ID is required"
        
        # Check that the generation is non-negative
        if reference.field_generation < 0:
            return False, "Generation cannot be negative"
        
        # The presentation should match or be one behind (for continuity)
        if reference.field_generation > expected_generation:
            return False, (
                f"Presentation generation ({reference.field_generation}) "
                f"exceeds expected ({expected_generation})"
            )
        
        self._last_validated_field_generation = reference.field_generation
        return True, None
    
    def validate_transition(
        self,
        previous: PresentationReference,
        current: PresentationReference,
    ) -> Tuple[bool, Optional[str]]:
        """
        Validate a transition from one presentation to another.
        
        Args:
            previous: Previous presentation reference
            current: New presentation reference
            
        Returns:
            Tuple of (is_valid, error_message if invalid)
        """
        # Check that the new generation is strictly greater
        if current.field_generation <= previous.field_generation:
            return False, (
                f"Presentation transition must increment generation "
                f"(previous: {previous.field_generation}, current: {current.field_generation})"
            )
        
        # Check that generations are consecutive (or at least increasing)
        if current.field_generation != previous.field_generation + 1:
            return False, (
                f"Generation jump from {previous.field_generation} to "
                f"{current.field_generation} exceeds allowed increment"
            )
        
        return True, None


__all__: Tuple[str, ...] = (
    "PresentationReference",
    "PresentationValidator",
)