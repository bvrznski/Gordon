# Gordon Phase 5.7.6-I: Perspective Engine - Validator
# ===============================================================================
"""
Canonical validation system for the Perspective Engine.

Validator ensures perspective state is well-formed, consistent, and ready
for publication while maintaining all architectural boundaries.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Tuple, Optional


@dataclass
class PerspectiveValidator:
    """
    Canonical validator for perspective state.
    
    Validates all perspective components before they are published to ensure
    consistency and adherence to architectural contracts. Validator operates
    independently of state management to enable deterministic validation.
    """
    
    # Validation rules
    require_active_observer: bool = True
    """Whether observer must be active."""
    
    require_valid_reference_frame: bool = True
    """Whether reference frame must be valid."""
    
    max_concurrent_perspective_types: int = 10
    """Maximum number of perspective types to track."""
    
    # State tracking
    _validation_count: int = 0
    _invalid_count: int = 0
    
    def __post_init__(self) -> None:
        """Initialize after construction."""
        self._validation_count = 0
        self._invalid_count = 0
    
    @property
    def validation_count(self) -> int:
        """Get total validations performed."""
        return self._validation_count
    
    @property
    def invalid_count(self) -> int:
        """Get total invalid validations."""
        return self._invalid_count
    
    @property
    def accuracy(self) -> float:
        """Get current validation accuracy rate."""
        if self._validation_count == 0:
            return 1.0
        return (self._validation_count - self._invalid_count) / self._validation_count
    
    # ==========================================================================
    # VALIDATION METHODS
    # ==========================================================================
    
    def validate_observer(
        self,
        observer_id: str,
        state_active: bool = True,
    ) -> Tuple[bool, Optional[str]]:
        """
        Validate an observer reference.
        
        Args:
            observer_id: Observer ID to validate
            state_active: Whether observer should be active
            
        Returns:
            Tuple of (valid, error_message if invalid)
        """
        self._validation_count += 1
        
        # Check observer has identifier
        if not observer_id or len(observer_id) < 3:
            self._invalid_count += 1
            return False, "Observer ID must be non-empty and at least 3 characters"
        
        # Check observer state (if required)
        if self.require_active_observer and not state_active:
            self._invalid_count += 1
            return False, "Observer must be active"
        
        # All checks passed
        return True, None
    
    def validate_reference_frame(
        self,
        frame_ref: str,
        origin_valid: bool = True,
        orientation_valid: bool = True,
    ) -> Tuple[bool, Optional[str]]:
        """
        Validate a reference frame reference.
        
        Args:
            frame_ref: Frame reference to validate
            origin_valid: Whether frame origin is valid
            orientation_valid: Whether frame orientation is valid
            
        Returns:
            Tuple of (valid, error_message if invalid)
        """
        self._validation_count += 1
        
        # Check frame has reference
        if not frame_ref or len(frame_ref) < 3:
            self._invalid_count += 1
            return False, "Frame reference must be non-empty and at least 3 characters"
        
        # Check origin validity (if required)
        if self.require_valid_reference_frame and not origin_valid:
            self._invalid_count += 1
            return False, "Reference frame origin is invalid"
        
        # Check orientation validity (if required)
        if orientation_valid is False:
            self._invalid_count += 1
            return False, "Reference frame orientation is invalid"
        
        # All checks passed
        return True, None
    
    def validate_perspective_type(
        self,
        perspective_type: str,
    ) -> Tuple[bool, Optional[str]]:
        """
        Validate a perspective type.
        
        Args:
            perspective_type: Perspective type to validate
            
        Returns:
            Tuple of (valid, error_message if invalid)
        """
        from .constants import VALID_PERSPECTIVE_TYPES
        
        self._validation_count += 1
        
        if perspective_type not in VALID_PERSPECTIVE_TYPES:
            self._invalid_count += 1
            return False, f"Invalid perspective type: {perspective_type}"
        
        # All checks passed
        return True, None
    
    def validate_self_reference(
        self,
        self_ref_kind: str,
        context_generation: int = 0,
    ) -> Tuple[bool, Optional[str]]:
        """
        Validate a self-reference.
        
        Args:
            self_ref_kind: Kind of self-reference
            context_generation: Current context generation
            
        Returns:
            Tuple of (valid, error_message if invalid)
        """
        from .constants import VALID_SELF_REFERENCE_KINDS
        
        self._validation_count += 1
        
        # Check kind is valid
        if self_ref_kind not in VALID_SELF_REFERENCE_KINDS:
            self._invalid_count += 1
            return False, f"Invalid self-reference kind: {self_ref_kind}"
        
        # Check context generation (if required)
        if context_generation < 0:
            self._invalid_count += 1
            return False, "Context generation cannot be negative"
        
        # All checks passed
        return True, None
    
    def validate_transition(
        self,
        from_type: str,
        to_type: str,
        generation: int = 0,
    ) -> Tuple[bool, Optional[str]]:
        """
        Validate a perspective transition.
        
        Args:
            from_type: Source perspective type
            to_type: Target perspective type
            generation: Context generation
            
        Returns:
            Tuple of (valid, error_message if invalid)
        """
        self._validation_count += 1
        
        # Validate source type
        valid_from, reason = self.validate_perspective_type(from_type)
        if not valid_from:
            self._invalid_count += 1
            return False, f"Source perspective invalid: {reason}"
        
        # Validate target type
        valid_to, reason = self.validate_perspective_type(to_type)
        if not valid_to:
            self._invalid_count += 1
            return False, f"Target perspective invalid: {reason}"
        
        # Check generation
        if generation < 0:
            self._invalid_count += 1
            return False, "Context generation cannot be negative"
        
        # All checks passed
        return True, None
    
    def validate_snapshot(
        self,
        snapshot_id: str,
        generation: int = 0,
        perspective_type: str = "",
    ) -> Tuple[bool, Optional[str]]:
        """
        Validate a perspective snapshot.
        
        Args:
            snapshot_id: Snapshot identifier
            generation: Context generation
            perspective_type: Active perspective type
            
        Returns:
            Tuple of (valid, error_message if invalid)
        """
        self._validation_count += 1
        
        # Check snapshot has identifier
        if not snapshot_id or len(snapshot_id) < 3:
            self._invalid_count += 1
            return False, "Snapshot ID must be non-empty and at least 3 characters"
        
        # Validate perspective type
        valid_persp, reason = self.validate_perspective_type(perspective_type)
        if not valid_persp:
            self._invalid_count += 1
            return False, f"Perspective type invalid: {reason}"
        
        # Check generation
        if generation < 0:
            self._invalid_count += 1
            return False, "Generation cannot be negative"
        
        # All checks passed
        return True, None
    
    def validate_full(
        self,
        observer_id: str,
        frame_ref: str,
        perspective_type: str,
        self_ref_kind: str,
        generation: int = 0,
    ) -> Tuple[bool, Optional[str]]:
        """
        Perform full perspective validation.
        
        This validates all components together to ensure consistency.
        
        Args:
            observer_id: Observer identifier
            frame_ref: Reference frame reference
            perspective_type: Active perspective type
            self_ref_kind: Self-reference kind
            generation: Context generation
            
        Returns:
            Tuple of (valid, error_message if invalid)
        """
        # Validate each component
        checks = [
            self.validate_observer(observer_id),
            self.validate_reference_frame(frame_ref),
            self.validate_perspective_type(perspective_type),
            self.validate_self_reference(self_ref_kind, generation),
            (generation >= 0, "Generation cannot be negative" if generation < 0 else None),
        ]
        
        for valid, reason in checks:
            if not valid:
                return False, reason
        
        # All checks passed
        return True, None
    
    @classmethod
    def default(cls) -> "PerspectiveValidator":
        """Return a validator with default settings."""
        return cls()
    
    @classmethod
    def strict(cls) -> "PerspectiveValidator":
        """Return a strict validator for production use."""
        return cls(
            require_active_observer=True,
            require_valid_reference_frame=True,
            max_concurrent_perspective_types=5,
        )


# =============================================================================
# EXPORTS
# =============================================================================

__all__: Tuple[str, ...] = (
    "PerspectiveValidator",
)