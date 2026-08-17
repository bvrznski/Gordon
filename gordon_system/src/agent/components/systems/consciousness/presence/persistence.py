# Gordon Phase 5.7.5-I: Presence Engine - Persistence Manager
# ===============================================================================
"""
Bounded persistence manager for the Presence Engine.

The persistence manager handles bounded content lifetime and expiration.
It does NOT handle semantic meaning, only temporal boundaries.
"""

from __future__ import annotations

import time
from dataclasses import dataclass, field
from typing import Tuple, Dict, Optional


@dataclass(frozen=True)
class PersistencePolicy:
    """
    Immutable persistence policy configuration.
    
    Defines how long content remains in presence before expiration.
    """
    
    default_lifetime_seconds: float = 3600.0
    """Default content lifetime (1 hour)."""
    
    max_lifetime_seconds: float = 86400.0
    """Maximum allowed lifetime (24 hours)."""
    
    min_lifetime_seconds: float = 60.0
    """Minimum required lifetime (1 minute)."""
    
    grace_period_seconds: float = 300.0
    """Grace period before fading begins (5 minutes)."""
    
    reuse_expired: bool = True
    """Whether expired content can be re-admitted."""
    
    def is_valid_lifetime(self, seconds: float) -> Tuple[bool, Optional[str]]:
        """
        Check if a lifetime value is valid.
        
        Args:
            seconds: Proposed lifetime in seconds
            
        Returns:
            Tuple of (valid, reason_if_invalid)
        """
        if seconds < self.min_lifetime_seconds:
            return False, f"Lifetime too short: {seconds}s < {self.min_lifetime_seconds}s"
        
        if seconds > self.max_lifetime_seconds:
            return False, f"Lifetime too long: {seconds}s > {self.max_lifetime_seconds}s"
        
        return True, None
    
    def get_expiration_time(
        self,
        created_at_utc: float,
        lifetime_seconds: Optional[float] = None,
    ) -> float:
        """
        Calculate when content should expire.
        
        Args:
            created_at_utc: When the content was created
            lifetime_seconds: Override lifetime (uses default if None)
            
        Returns:
            UTC timestamp when content expires
        """
        if lifetime_seconds is None:
            lifetime_seconds = self.default_lifetime_seconds
        
        return created_at_utc + lifetime_seconds
    
    def has_expired(
        self,
        created_at_utc: float,
        now_utc: Optional[float] = None,
        lifetime_seconds: Optional[float] = None,
    ) -> bool:
        """
        Check if content has expired.
        
        Args:
            created_at_utc: When the content was created
            now_utc: Current time (uses current time if not provided)
            lifetime_seconds: Override lifetime
            
        Returns:
            True if expired, False otherwise
        """
        if now_utc is None:
            now_utc = time.time()
        
        expiration_time = self.get_expiration_time(
            created_at_utc=created_at_utc,
            lifetime_seconds=lifetime_seconds,
        )
        
        return now_utc > expiration_time
    
    def get_remaining_seconds(
        self,
        created_at_utc: float,
        now_utc: Optional[float] = None,
        lifetime_seconds: Optional[float] = None,
    ) -> float:
        """
        Get remaining lifetime for content.
        
        Args:
            created_at_utc: When the content was created
            now_utc: Current time (uses current time if not provided)
            lifetime_seconds: Override lifetime
            
        Returns:
            Seconds until expiration (may be negative if expired)
        """
        if now_utc is None:
            now_utc = time.time()
        
        expiration_time = self.get_expiration_time(
            created_at_utc=created_at_utc,
            lifetime_seconds=lifetime_seconds,
        )
        
        return expiration_time - now_utc


@dataclass
class PersistenceManager:
    """
    Canonical persistence manager for Presence Engine.
    
    Responsibilities:
        - Track content creation timestamps
        - Calculate expiration times
        - Determine if content has expired
        - Enforce bounded lifetime policies
        
    NOT responsible for:
        - Content evaluation or reasoning
        - Admission decisions (only provides timing data)
        - Withdrawal execution
    """
    
    _policy: PersistencePolicy = field(default_factory=PersistencePolicy)
    """Persistence policy configuration."""
    
    # Track content lifecycles by ID
    _content_info: Dict[str, float] = field(default_factory=dict)
    """Maps content_id -> creation_timestamp."""
    
    def __post_init__(self) -> None:
        """Initialize empty content info dict."""
        self._content_info.clear()
    
    @property
    def policy(self) -> PersistencePolicy:
        """Get the current persistence policy."""
        return self._policy
    
    def register_content(
        self,
        content_id: str,
        now_utc: Optional[float] = None,
    ) -> Tuple[bool, Optional[str]]:
        """
        Register new content for persistence tracking.
        
        Args:
            content_id: ID of the content to track
            now_utc: Current time (uses current time if not provided)
            
        Returns:
            Tuple of (success, reason_if_failed)
        """
        if now_utc is None:
            now_utc = time.time()
        
        # Check if already tracked
        if content_id in self._content_info:
            return False, "Content already registered"
        
        self._content_info[content_id] = now_utc
        return True, None
    
    def unregister_content(self, content_id: str) -> bool:
        """
        Remove content from tracking.
        
        Args:
            content_id: ID of the content to remove
            
        Returns:
            True if removed (or was not tracked), False otherwise
        """
        if content_id in self._content_info:
            del self._content_info[content_id]
            return True
        
        # If not tracked, that's also fine
        return True
    
    def is_content_expired(
        self,
        content_id: str,
        now_utc: Optional[float] = None,
        lifetime_seconds: Optional[float] = None,
    ) -> bool:
        """
        Check if registered content has expired.
        
        Args:
            content_id: ID of the content to check
            now_utc: Current time (uses current time if not provided)
            lifetime_seconds: Override lifetime
            
        Returns:
            True if expired, False otherwise
        """
        if now_utc is None:
            now_utc = time.time()
        
        created_at = self._content_info.get(content_id)
        if created_at is None:
            return True  # Not tracked = can't verify = treat as expired
        
        return self._policy.has_expired(
            created_at_utc=created_at,
            now_utc=now_utc,
            lifetime_seconds=lifetime_seconds,
        )
    
    def get_remaining_lifetime(
        self,
        content_id: str,
        now_utc: Optional[float] = None,
        lifetime_seconds: Optional[float] = None,
    ) -> float:
        """
        Get remaining lifetime for registered content.
        
        Args:
            content_id: ID of the content to check
            now_utc: Current time (uses current time if not provided)
            lifetime_seconds: Override lifetime
            
        Returns:
            Seconds until expiration (negative if already expired)
        """
        if now_utc is None:
            now_utc = time.time()
        
        created_at = self._content_info.get(content_id)
        if created_at is None:
            return 0.0
        
        return self._policy.get_remaining_seconds(
            created_at_utc=created_at,
            now_utc=now_utc,
            lifetime_seconds=lifetime_seconds,
        )
    
    def clear_tracking(self) -> int:
        """Clear all content tracking and return count."""
        count = len(self._content_info)
        self._content_info.clear()
        return count
    
    def get_tracked_count(self) -> int:
        """Get number of currently tracked items."""
        return len(self._content_info)