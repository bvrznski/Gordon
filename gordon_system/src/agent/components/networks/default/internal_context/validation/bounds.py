# Bounds Validation Model
# ======================

"""
Validation for context bounds and capacity constraints.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Tuple


@dataclass(frozen=True, slots=True)
class BoundValidator:
    """
    Validator for context bounds and capacity constraints.
    
    Validates that contexts don't exceed their defined limits.
    """
    
    maximum_total_items: int = 500
    """Maximum total items across all projections."""
    
    maximum_conflicts: int = 50
    """Maximum conflict records."""
    
    @classmethod
    def create(cls, maximum_total_items: int = 500, maximum_conflicts: int = 50) -> BoundValidator:
        """Create a new validator with specified bounds."""
        return cls(
            maximum_total_items=maximum_total_items,
            maximum_conflicts=maximum_conflicts,
        )
    
    def check_overflow(
        self,
        current_count: int,
        projection_kind: str,
    ) -> Tuple[bool, str | None]:
        """
        Check if adding items to a projection would exceed bounds.
        
        Returns:
            Tuple of (is_within_bounds, overflow_message_or_none)
        """
        # Get limit for this projection kind
        limits = {
            "objectives": 50,
            "commitments": 50,
            "memory": 200,
            "identity": 100,
            "narrative": 50,
            "prediction": 100,
            "workspace": 30,
            "working_memory": 50,
            "execution": 20,
            "attention": 50,
            "affect": 20,
            "concerns": 100,
            "resources": 20,
        }
        
        limit = limits.get(projection_kind, self.maximum_total_items // 13)
        
        if current_count >= limit:
            return (
                False,
                f"{projection_kind} projection has {current_count} items (limit: {limit})"
            )
        
        return (True, None)
    
    def check_capacity(
        self,
        total_item_count: int,
        conflict_count: int,
    ) -> Tuple[bool, str | None]:
        """
        Check overall context capacity constraints.
        
        Returns:
            Tuple of (is_within_bounds, overflow_message_or_none)
        """
        if total_item_count > self.maximum_total_items:
            return (
                False,
                f"Total items {total_item_count} exceeds maximum {self.maximum_total_items}"
            )
        
        if conflict_count > self.maximum_conflicts:
            return (
                False,
                f"Conflict count {conflict_count} exceeds maximum {self.maximum_conflicts}"
            )
        
        return (True, None)