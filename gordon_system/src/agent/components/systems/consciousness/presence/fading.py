# Gordon Phase 5.7.5-I: Presence Engine - Fading Mechanism
# ===============================================================================
"""
Fading mechanism for gradual withdrawal of content from presence.
"""

from __future__ import annotations

import time
from dataclasses import dataclass, field
from typing import Tuple, Dict, Optional


@dataclass(frozen=True)
class FadePolicy:
    """
    Immutable fading policy configuration.
    
    Defines how content fades from active to withdrawn state.
    """
    
    weakening_duration_seconds: float = 60.0
    """Duration in weakening state before full fading (1 minute)."""
    
    fade_duration_seconds: float = 30.0
    """Duration in fading state before withdrawal (30 seconds)."""
    
    grace_period_seconds: float = 300.0
    """Grace period after active before fading begins (5 minutes)."""
    
    max_weakening_count: int = 10
    """Maximum consecutive weakening cycles."""
    
    def can_begin_fading(
        self,
        active_from_utc: Optional[float],
        now_utc: Optional[float] = None,
    ) -> Tuple[bool, Optional[str]]:
        """
        Check if fading can begin for content that became active.
        
        Args:
            active_from_utc: When content became active (None = never)
            now_utc: Current time
            
        Returns:
            Tuple of (can_begin, reason_if_not)
        """
        if now_utc is None:
            now_utc = time.time()
        
        if active_from_utc is None:
            return False, "Content has no active timestamp"
        
        # Check grace period
        time_active = now_utc - active_from_utc
        if time_active < self.grace_period_seconds:
            return False, f"Grace period not met ({time_active:.1f}s < {self.grace_period_seconds}s)"
        
        return True, None
    
    def is_weakening_complete(
        self,
        weakening_started_utc: float,
        now_utc: Optional[float] = None,
    ) -> bool:
        """
        Check if weakening phase is complete.
        
        Args:
            weakening_started_utc: When weakening began
            now_utc: Current time
            
        Returns:
            True if weakening should transition to fading
        """
        if now_utc is None:
            now_utc = time.time()
        
        return (now_utc - weakening_started_utc) >= self.weakening_duration_seconds
    
    def is_fading_complete(
        self,
        fading_started_utc: float,
        now_utc: Optional[float] = None,
    ) -> bool:
        """
        Check if fading phase is complete.
        
        Args:
            fading_started_utc: When fading began
            now_utc: Current time
            
        Returns:
            True if fading should transition to withdrawn
        """
        if now_utc is None:
            now_utc = time.time()
        
        return (now_utc - fading_started_utc) >= self.fade_duration_seconds
    
    def get_fade_progress(
        self,
        state: str,
        started_at_utc: float,
        now_utc: Optional[float] = None,
    ) -> float:
        """
        Get fade progress as 0.0-1.0.
        
        Args:
            state: Current fading state (weakening, fading)
            started_at_utc: When current phase began
            now_utc: Current time
            
        Returns:
            Progress from 0.0 to 1.0
        """
        if now_utc is None:
            now_utc = time.time()
        
        duration = self.weakening_duration_seconds if state == "weakening" else self.fade_duration_seconds
        elapsed = max(0, now_utc - started_at_utc)
        
        return min(1.0, elapsed / duration)


@dataclass
class FadingManager:
    """
    Canonical fading manager for Presence Engine.
    
    Responsibilities:
        - Track when content began fading transitions
        - Determine if fading should advance between states
        - Enforce bounded fading durations
        
    NOT responsible for:
        - Initiating fade transitions (only managing state progress)
        - Content evaluation or reasoning
    """
    
    _policy: FadePolicy = field(default_factory=FadePolicy)
    """Fading policy configuration."""
    
    # Track fading progress by item_id
    _weakening_start_times: Dict[str, float] = field(default_factory=dict)
    """Maps item_id -> weakening_started_utc."""
    
    _fading_start_times: Dict[str, float] = field(default_factory=dict)
    """Maps item_id -> fading_started_utc."""
    
    def __post_init__(self) -> None:
        """Initialize empty tracking dicts."""
        self._weakening_start_times.clear()
        self._fading_start_times.clear()
    
    @property
    def policy(self) -> FadePolicy:
        """Get the current fading policy."""
        return self._policy
    
    def begin_weakening(
        self,
        item_id: str,
        now_utc: Optional[float] = None,
    ) -> Tuple[bool, Optional[str]]:
        """
        Mark an item as entering weakening state.
        
        Args:
            item_id: ID of the item
            now_utc: Current time
            
        Returns:
            Tuple of (success, reason_if_failed)
        """
        if now_utc is None:
            now_utc = time.time()
        
        # Check if already in fading states
        if item_id in self._weakening_start_times:
            return False, "Item already weakening"
        
        if item_id in self._fading_start_times:
            return False, "Item already fading"
        
        self._weakening_start_times[item_id] = now_utc
        
        # Clear any previous fading time (if resuming)
        self._fading_start_times.pop(item_id, None)
        
        return True, None
    
    def begin_fading(
        self,
        item_id: str,
        now_utc: Optional[float] = None,
    ) -> Tuple[bool, Optional[str]]:
        """
        Mark an item as entering fading state.
        
        Args:
            item_id: ID of the item
            now_utc: Current time
            
        Returns:
            Tuple of (success, reason_if_failed)
        """
        if now_utc is None:
            now_utc = time.time()
        
        # Check if already fading
        if item_id in self._fading_start_times:
            return False, "Item already fading"
        
        # Verify weakening completed
        if item_id in self._weakening_start_times:
            weakening_time = self._weakening_start_times[item_id]
            if not self._policy.is_weakening_complete(weakening_time, now_utc):
                return False, "Weakening phase not complete"
        
        self._fading_start_times[item_id] = now_utc
        
        # Clear weakening time (transitioned to fading)
        self._weakening_start_times.pop(item_id, None)
        
        return True, None
    
    def is_weakening_complete(
        self,
        item_id: str,
        now_utc: Optional[float] = None,
    ) -> bool:
        """
        Check if weakening phase should complete.
        
        Args:
            item_id: ID of the item
            now_utc: Current time
            
        Returns:
            True if transition to fading is appropriate
        """
        start_time = self._weakening_start_times.get(item_id)
        if start_time is None:
            return False
        
        if now_utc is None:
            now_utc = time.time()
        
        return self._policy.is_weakening_complete(start_time, now_utc)
    
    def is_fading_complete(
        self,
        item_id: str,
        now_utc: Optional[float] = None,
    ) -> bool:
        """
        Check if fading phase should complete.
        
        Args:
            item_id: ID of the item
            now_utc: Current time
            
        Returns:
            True if transition to withdrawn is appropriate
        """
        start_time = self._fading_start_times.get(item_id)
        if start_time is None:
            return False
        
        if now_utc is None:
            now_utc = time.time()
        
        return self._policy.is_fading_complete(start_time, now_utc)
    
    def get_weakening_progress(
        self,
        item_id: str,
        now_utc: Optional[float] = None,
    ) -> float:
        """Get weakening progress (0.0-1.0)."""
        start_time = self._weakening_start_times.get(item_id)
        if start_time is None:
            return 0.0
        
        return self._policy.get_fade_progress("weakening", start_time, now_utc)
    
    def get_fading_progress(
        self,
        item_id: str,
        now_utc: Optional[float] = None,
    ) -> float:
        """Get fading progress (0.0-1.0)."""
        start_time = self._fading_start_times.get(item_id)
        if start_time is None:
            return 0.0
        
        return self._policy.get_fade_progress("fading", start_time, now_utc)
    
    def clear_item(self, item_id: str) -> bool:
        """
        Clear fading tracking for an item.
        
        Args:
            item_id: ID of the item
            
        Returns:
            True if cleared (or not found), False otherwise
        """
        removed_weakening = item_id in self._weakening_start_times
        removed_fading = item_id in self._fading_start_times
        
        self._weakening_start_times.pop(item_id, None)
        self._fading_start_times.pop(item_id, None)
        
        return removed_weakening or removed_fading
    
    def clear_all(self) -> int:
        """Clear all fading tracking and return count."""
        count = len(self._weakening_start_times) + len(self._fading_start_times)
        self._weakening_start_times.clear()
        self._fading_start_times.clear()
        return count