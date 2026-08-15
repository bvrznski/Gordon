# Projection Validation Model
# ===========================

"""
Validation for context projections.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Tuple


@dataclass(frozen=True, slots=True)
class ProjectionValidator:
    """
    Validator for context projections.
    
    Validates projection structure without runtime behavior.
    """
    
    minimum_confidence: float = 0.3
    
    @classmethod
    def create(cls, minimum_confidence: float = 0.3) -> ProjectionValidator:
        """Create a new validator."""
        return cls(minimum_confidence=minimum_confidence)
    
    def validate_projection(
        self,
        projection_id: str,
        source_revision: int,
        captured_at_utc,
        confidence: float,
    ) -> Tuple[bool, str | None]:
        """
        Validate a context projection.
        
        Returns:
            Tuple of (is_valid, error_message_or_none)
        """
        checks = []
        
        # Check projection_id is not empty
        if not projection_id:
            checks.append((False, "projection_id must not be empty"))
        else:
            checks.append((True, None))
        
        # Check source_revision is non-negative
        if source_revision < 0:
            checks.append((False, "source_revision must be non-negative"))
        else:
            checks.append((True, None))
        
        # Validate confidence score
        if not (0.0 <= confidence <= 1.0):
            checks.append((False, f"confidence {confidence} out of range [0.0, 1.0]"))
        elif confidence < self.minimum_confidence:
            checks.append((True, None))  # Below threshold but structurally valid
        else:
            checks.append((True, None))
        
        for passed, msg in checks:
            if not passed:
                return (False, msg)
        
        return (True, None)