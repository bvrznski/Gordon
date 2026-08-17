# Gordon Phase 5.7.4-I: Temporal Context Engine - Integrity
# ===============================================================================
"""
Integrity enforcer for temporal context validation.
"""

from __future__ import annotations

import time
from dataclasses import dataclass, field
from typing import Tuple, Optional


@dataclass
class TemporalIntegrityEnforcer:
    """
    Enforcer of integrity constraints for the Temporal Context Engine.
    
    Validates all temporal state changes before publication to ensure that:
        - Boundaries are respected (retention history, protention expectations)
        - Generations are strictly monotonic
        - Snapshots are valid and consistent
        - Transitions preserve continuity
    """
    
    max_retention_history: int = 10
    """Maximum retention history entries."""
    
    max_protention_expectations: int = 5
    """Maximum protentional expectations."""
    
    max_continuity_window_size: int = 20
    """Maximum total size of continuity window."""
    
    def validate_snapshot(
        self,
        generation: int,
        previous_generation: Optional[int],
        retention_count: int,
        protention_count: int,
        continuity_window_size: int,
    ) -> Tuple[bool, Optional[str]]:
        """
        Validate a temporal snapshot before publication.
        
        Args:
            generation: Snapshot generation number
            previous_generation: Previous generation (for lineage)
            retention_count: Number of retention references
            protention_count: Number of protentional expectations
            continuity_window_size: Total window size
            
        Returns:
            Tuple of (is_valid, error_message if invalid)
        """
        # Check generation is non-negative and advances properly
        if generation < 0:
            return False, "Generation cannot be negative"
        
        if previous_generation is not None and generation != previous_generation + 1:
            return False, (
                f"Snapshot generation ({generation}) must be exactly one more than "
                f"previous generation ({previous_generation})"
            )
        
        # Check bounds
        if retention_count > self.max_retention_history:
            return False, (
                f"Retention count ({retention_count}) exceeds maximum "
                f"({self.max_retention_history})"
            )
        
        if protention_count > self.max_protention_expectations:
            return False, (
                f"Protention count ({protention_count}) exceeds maximum "
                f"({self.max_protention_expectations})"
            )
        
        # Check continuity window size
        if continuity_window_size > self.max_continuity_window_size:
            return False, (
                f"Continuity window size ({continuity_window_size}) exceeds maximum "
                f"({self.max_continuity_window_size})"
            )
        
        return True, None
    
    def validate_transition(
        self,
        previous_generation: int,
        new_generation: int,
        is_rollback: bool = False,
    ) -> Tuple[bool, Optional[str]]:
        """
        Validate a transition before commit.
        
        Args:
            previous_generation: Generation before the transition
            new_generation: Generation after the transition
            is_rollback: Whether this is a rollback
            
        Returns:
            Tuple of (is_valid, error_message if invalid)
        """
        # Check non-negative generations
        if previous_generation < 0 or new_generation < 0:
            return False, "Generation cannot be negative"
        
        # Check monotonic advancement
        if not is_rollback and new_generation != previous_generation + 1:
            return False, (
                f"Transition must advance by exactly 1 generation "
                f"(from {previous_generation} to {new_generation})"
            )
        
        # For rollback, check that we're going back
        if is_rollback and new_generation > previous_generation:
            return False, "Rollback transition cannot increase generation"
        
        return True, None
    
    def validate_continuity(
        self,
        retention_refs: Tuple[str, ...],
        presentation_ref: Optional[str],
        protention_refs: Tuple[str, ...],
    ) -> Tuple[bool, Optional[str]]:
        """
        Validate the integrity of a continuity window's temporal elements.
        
        Args:
            retention_refs: References to previous generations
            presentation_ref: Reference to current EF context
            protention_refs: Protentional expectations
            
        Returns:
            Tuple of (is_valid, error_message if invalid)
        """
        # Presentation reference must be present for active windows
        if not presentation_ref:
            return False, "Presentation reference is required"
        
        # Check retention count bound
        if len(retention_refs) > self.max_retention_history:
            return False, f"Retention history exceeds maximum ({self.max_retention_history})"
        
        # Check protention count bound
        if len(protention_refs) > self.max_protention_expectations:
            return False, (
                f"Protention expectations exceed maximum ({self.max_protention_expectations})"
            )
        
        return True, None
    
    def verify_integrity(
        self,
        retention_count: int,
        protention_count: int,
        window_size: int,
    ) -> Tuple[bool, Optional[str]]:
        """
        Verify overall temporal integrity.
        
        Args:
            retention_count: Number of active retention references
            protention_count: Number of protentional expectations
            window_size: Current continuity window size
            
        Returns:
            Tuple of (is_valid, error_message if invalid)
        """
        issues = []
        
        if retention_count > self.max_retention_history:
            issues.append(f"retention overflow ({retention_count}/{self.max_retention_history})")
        
        if protention_count > self.max_protention_expectations:
            issues.append(
                f"protention overflow ({protention_count}/{self.max_protention_expectations})"
            )
        
        if window_size > self.max_continuity_window_size:
            issues.append(f"window size overflow ({window_size}/{self.max_continuity_window_size})")
        
        if issues:
            return False, "; ".join(issues)
        
        return True, None


__all__: Tuple[str, ...] = (
    "TemporalIntegrityEnforcer",
)