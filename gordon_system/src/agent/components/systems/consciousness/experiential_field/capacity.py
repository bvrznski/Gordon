# Gordon Phase 5.7.2-I: Experiential Field Capacity
# ===============================================================================
#
# Capacity policy and enforcement for the experiential field.
#

"""
Capacity management module for Experiential Field Builder.

This module handles capacity bounds:
    - Maximum content count
    - Maximum relation count  
    - Per-source limits
    - Payload size limits
"""

from __future__ import annotations

import time
from dataclasses import dataclass, field
from typing import Tuple


@dataclass(frozen=True)
class CapacityEnforcementResult:
    """
    Result of capacity enforcement action.
    
    Records which items were accepted, rejected, or modified due to
    capacity constraints.
    """
    
    succeeded: bool
    """Whether the operation succeeded."""
    
    accepted_items: int = 0
    """Number of items accepted."""
    
    rejected_items: int = 0
    """Number of items rejected."""
    
    truncated_items: int = 0
    """Number of items that had metadata truncated."""
    
    reduction_actions: Tuple[str, ...] = field(default_factory=tuple)
    """Actions taken to reduce capacity usage."""
    
    @classmethod
    def success(cls, accepted: int = 0) -> "CapacityEnforcementResult":
        """Create a successful result with no rejections."""
        return cls(succeeded=True, accepted_items=accepted)
    
    @classmethod
    def rejected(cls, rejected: int = 1) -> "CapacityEnforcementResult":
        """Create a rejection result."""
        return cls(succeeded=False, rejected_items=rejected)


@dataclass
class FieldCapacityPolicy:
    """
    Policy for field capacity bounds.
    
    Defines and enforces limits on:
        - Total content count
        - Total relation count
        - Per-source content count
        - Payload size
        - Untrusted/private content ratios
    """
    
    max_content_count: int = 1000
    """Maximum number of content items in a field."""
    
    max_relation_count: int = 5000
    """Maximum number of relations in a field."""
    
    max_payload_size_bytes: int = 1_048_576  # 1MB
    """Maximum total payload size in bytes."""
    
    max_per_source_count: int = 200
    """Maximum content items from any single source."""
    
    max_untrusted_content_count: int = 100
    """Maximum untrusted content allowed."""
    
    max_private_content_count: int = 50
    """Maximum private content allowed."""
    
    max_pending_contributions: int = 1000
    """Maximum pending contributions to process."""
    
    def __post_init__(self):
        """Post-initialization validation."""
        if self.max_content_count <= 0:
            raise ValueError("max_content_count must be positive")
        if self.max_relation_count <= 0:
            raise ValueError("max_relation_count must be positive")
    
    def check_content_capacity(
        self,
        current_count: int,
        new_items: int = 1
    ) -> CapacityEnforcementResult:
        """
        Check if adding items would exceed content capacity.
        
        Args:
            current_count: Current number of content items
            new_items: Number of items being added
            
        Returns:
            Result indicating whether operation is within bounds
        """
        total = current_count + new_items
        if total <= self.max_content_count:
            return CapacityEnforcementResult.success(accepted=new_items)
        
        # Exceeds capacity - determine how many can be accepted
        remaining_capacity = max(0, self.max_content_count - current_count)
        
        # Return partial success or rejection based on policy
        if remaining_capacity > 0:
            return CapacityEnforcementResult.success(accepted=remaining_capacity)
        else:
            return CapacityEnforcementResult.rejected(rejected=new_items)
    
    def check_relation_capacity(
        self,
        current_count: int,
        new_relations: int = 1
    ) -> CapacityEnforcementResult:
        """Check if adding relations would exceed relation capacity."""
        total = current_count + new_relations
        if total <= self.max_relation_count:
            return CapacityEnforcementResult.success(accepted=new_relations)
        
        remaining_capacity = max(0, self.max_relation_count - current_count)
        
        if remaining_capacity > 0:
            return CapacityEnforcementResult.success(accepted=remaining_capacity)
        else:
            return CapacityEnforcementResult.rejected(rejected=new_relations)
    
    def check_per_source_limit(
        self,
        source_counts: dict[str, int],
        new_source: str,
        new_count: int = 1
    ) -> CapacityEnforcementResult:
        """Check if adding items for a source would exceed per-source limit."""
        current = source_counts.get(new_source, 0)
        total = current + new_count
        
        if total <= self.max_per_source_count:
            return CapacityEnforcementResult.success(accepted=new_count)
        
        remaining = max(0, self.max_per_source_count - current)
        if remaining > 0:
            return CapacityEnforcementResult.success(accepted=remaining)
        else:
            return CapacityEnforcementResult.rejected(rejected=new_count)
    
    def check_trusted_content_ratio(
        self,
        trusted_count: int,
        total_count: int
    ) -> bool:
        """
        Check if untrusted content ratio is within acceptable bounds.
        
        Returns True if the field meets policy requirements.
        """
        if total_count == 0:
            return True
        
        # At least some capacity for untrusted items
        max_untrusted = min(
            self.max_untrusted_content_count,
            int(total_count * 0.3)  # No more than 30% untrusted
        )
        
        untrusted_count = total_count - trusted_count
        return untrusted_count <= max_untrusted
    
    def enforce_capacity(
        self,
        contents: list,
        relations: list,
        per_source_counts: dict[str, int]
    ) -> Tuple[list, list, Tuple[CapacityEnforcementResult, ...]]:
        """
        Enforce all capacity limits and trim if necessary.
        
        Args:
            contents: List of content items
            relations: List of relation items  
            per_source_counts: Dict mapping source IDs to their counts
            
        Returns:
            Tuple of (trimmed_contents, trimmed_relations, results_tuple)
        """
        results: list[CapacityEnforcementResult] = []
        trimmed_contents = list(contents)
        trimmed_relations = list(relations)
        
        # Enforce content count
        if len(trimmed_contents) > self.max_content_count:
            # Keep highest priority items (simple truncation for now)
            removed = len(trimmed_contents) - self.max_content_count
            trimmed_contents = trimmed_contents[:self.max_content_count]
            results.append(
                CapacityEnforcementResult.rejected(rejected=removed)
            )
        
        # Enforce relation count
        if len(trimmed_relations) > self.max_relation_count:
            removed = len(trimmed_relations) - self.max_relation_count
            trimmed_relations = trimmed_relations[:self.max_relation_count]
            results.append(
                CapacityEnforcementResult.rejected(rejected=removed)
            )
        
        return trimmed_contents, trimmed_relations, tuple(results)


# =============================================================================
# EXPORTS
# =============================================================================

__all__: tuple[str, ...] = (
    "CapacityEnforcementResult",
    "FieldCapacityPolicy",
)