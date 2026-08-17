# Gordon Phase 5.7.5-I: Presence Engine - Integrity Enforcement
# ===============================================================================
"""
Integrity enforcement for the Presence Engine.
"""

from __future__ import annotations

import time
from dataclasses import dataclass, field
from typing import Tuple, Dict, Optional


@dataclass(frozen=True)
class IntegrityCheckResult:
    """
    Immutable result of an integrity check.
    
    Indicates whether a state or operation passed integrity validation.
    """
    
    timestamp_utc: float = field(default_factory=time.time)
    """When the check was performed."""
    
    is_valid: bool = True
    """Overall integrity status."""
    
    errors: Tuple[str, ...] = field(default_factory=tuple)
    """Any integrity errors found."""
    
    warnings: Tuple[str, ...] = field(default_factory=tuple)
    """Any integrity warnings found."""
    
    @classmethod
    def valid(cls) -> "IntegrityCheckResult":
        """Create a valid result."""
        return cls()
    
    @classmethod
    def invalid(
        cls,
        *errors: str,
        **kwargs,
    ) -> "IntegrityCheckResult":
        """Create an invalid result with errors."""
        return cls(is_valid=False, errors=tuple(errors), **kwargs)
    
    @property
    def has_errors(self) -> bool:
        """Check if there are any errors."""
        return not self.is_valid or len(self.errors) > 0
    
    @property
    def has_warnings(self) -> bool:
        """Check if there are any warnings."""
        return len(self.warnings) > 0


@dataclass
class IntegrityEnforcer:
    """
    Canonical integrity enforcer for Presence Engine.
    
    Responsibilities:
        - Validate state consistency
        - Verify transition validity
        - Check snapshot integrity
        
    NOT responsible for:
        - Making policy decisions
        - Executing transitions
    """
    
    def validate_transition(
        self,
        from_state: str,
        to_state: str,
    ) -> IntegrityCheckResult:
        """
        Validate if a state transition is allowed.
        
        Args:
            from_state: Current state
            to_state: Target state
            
        Returns:
            Check result indicating validity
        """
        valid_transitions = {
            "candidate": ("admitted",),
            "admitted": ("active", "withdrawn"),
            "active": ("weakening", "suspended", "withdrawn"),
            "weakening": ("fading",),
            "fading": ("withdrawn", "active"),  # Can resume from fading
            "suspended": ("active", "withdrawn"),
            "withdrawn": (),  # No outgoing transitions (terminal)
        }
        
        allowed = valid_transitions.get(from_state, ())
        
        if to_state not in allowed:
            return IntegrityCheckResult.invalid(
                f"Invalid transition: {from_state} → {to_state}"
            )
        
        return IntegrityCheckResult.valid()
    
    def validate_snapshot_integrity(
        self,
        active_count: int,
        fading_count: int,
        total_items: int,
        max_capacity: int = 100,
    ) -> IntegrityCheckResult:
        """
        Validate snapshot integrity.
        
        Args:
            active_count: Number of active items
            fading_count: Number of fading items
            total_items: Total tracked items
            max_capacity: Maximum capacity
            
        Returns:
            Check result indicating validity
        """
        errors = []
        
        # Capacity check
        if active_count > max_capacity:
            errors.append(f"Active count ({active_count}) exceeds capacity ({max_capacity})")
        
        if fading_count > total_items:
            errors.append("Fading count exceeds total items")
        
        if total_items < 0:
            errors.append("Total items cannot be negative")
        
        if errors:
            return IntegrityCheckResult.invalid(*errors)
        
        return IntegrityCheckResult.valid()
    
    def validate_state_consistency(
        self,
        state: str,
        item_id: str,
    ) -> IntegrityCheckResult:
        """
        Validate that a state is valid for the presence system.
        
        Args:
            state: State to validate
            item_id: ID of the item (for context)
            
        Returns:
            Check result indicating validity
        """
        valid_states = (
            "candidate", "admitted", "active", "weakening",
            "fading", "suspended", "withdrawn"
        )
        
        if state not in valid_states:
            return IntegrityCheckResult.invalid(
                f"Invalid state '{state}' for item {item_id}"
            )
        
        return IntegrityCheckResult.valid()