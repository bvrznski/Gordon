# Gordon Phase 5.7.4-I: Temporal Context Engine - Protention
# ===============================================================================
"""
Protention module for bounded immediate expectation tracking.
"""

from __future__ import annotations

import time
from dataclasses import dataclass, field
from typing import Tuple, Dict, Optional


@dataclass(frozen=True)
class ProtentionExpectation:
    """
    Immutable record of an immediate protentional expectation.
    
    Protention represents bounded expectations about the immediately forthcoming
    context. It is distinct from prediction, planning, or reasoning.
    
    Key properties:
        - Immediate: Only expects what is about to happen next
        - Bounded: Limited by MAX_PROTENTION_EXPECTATIONS
        - Distinct: Not prediction/planning (those belong to Cognition)
    """
    
    protention_id: str = field(default_factory=lambda: f"prot-{time.time()}")
    """Unique identifier for this protentional expectation."""
    
    expected_content_reference: Optional[str] = None
    """Reference to expected content that will enter the context."""
    
    expected_generation_offset: int = 1
    """Expected generation offset (typically +1 for next immediate)."""
    
    timestamp_utc: float = field(default_factory=time.time)
    """When this expectation was registered."""
    
    ttl_seconds: float = 60.0
    """Time-to-live for this expectation (default 1 minute)."""
    
    @property
    def is_expired(self) -> bool:
        """Check if this expectation has exceeded its TTL."""
        return time.time() - self.timestamp_utc > self.ttl_seconds
    
    @classmethod
    def next_context(
        cls,
        expected_content_reference: str,
    ) -> "ProtentionExpectation":
        """
        Create an expectation for the immediate next context.
        
        Args:
            expected_content_reference: Reference to content expected in next EF
            
        Returns:
            New ProtentionExpectation for next context
        """
        return cls(
            expected_content_reference=expected_content_reference,
            expected_generation_offset=1,
            ttl_seconds=60.0,
        )
    
    @classmethod
    def continuation_of(
        cls,
        current_context_id: str,
    ) -> "ProtentionExpectation":
        """
        Create an expectation for context continuation.
        
        This represents the expectation that the next context will be a
        natural continuation of the current one (no interruption).
        
        Args:
            current_context_id: Current EF context ID
            
        Returns:
            New ProtentionExpectation for continuation
        """
        return cls(
            expected_content_reference=f"continuation-{current_context_id}",
            expected_generation_offset=1,
        )


class ProtentionSet:
    """
    Immutable bounded set of protentional expectations.
    
    Maintains a collection of immediate expectations, enforcing bounds
    and ensuring that only valid expectations are tracked.
    """
    
    def __init__(self, max_expectations: int = 5):
        """
        Initialize the protention set.
        
        Args:
            max_expectations: Maximum number of expectations to maintain
        """
        self._max_expectations: int = max_expectations
        
        self._expectations: Dict[str, ProtentionExpectation] = {}
    
    @property
    def expectation_count(self) -> int:
        """Get the current count of expectations."""
        return len(self._expectations)
    
    @property
    def is_at_capacity(self) -> bool:
        """Check if at maximum capacity."""
        return self.expectation_count >= self._max_expectations
    
    def register(
        self,
        expectation: ProtentionExpectation,
    ) -> Tuple[bool, Optional[str]]:
        """
        Register an expectation.
        
        Enforces bounded size by removing oldest expired expectations if needed.
        
        Args:
            expectation: The protentional expectation to register
            
        Returns:
            Tuple of (success, error_message if failed)
        """
        # Remove expired expectations first
        self._clean_expired()
        
        # Check capacity
        if len(self._expectations) >= self._max_expectations:
            return False, "Protention set is at maximum capacity"
        
        # Register the new expectation
        self._expectations[expectation.protention_id] = expectation
        
        return True, None
    
    def unregister(self, protention_id: str) -> Tuple[bool, Optional[str]]:
        """
        Unregister an expectation by its ID.
        
        Args:
            protention_id: ID of the expectation to remove
            
        Returns:
            Tuple of (success, error_message if failed)
        """
        if protention_id not in self._expectations:
            return False, f"Protention expectation {protention_id} not found"
        
        del self._expectations[protention_id]
        return True, None
    
    def get(self, protention_id: str) -> Optional[ProtentionExpectation]:
        """Get an expectation by its ID."""
        return self._expectations.get(protention_id)
    
    def get_all(self) -> Tuple[ProtentionExpectation, ...]:
        """Get all registered expectations as an immutable tuple."""
        return tuple(sorted(
            self._expectations.values(),
            key=lambda e: e.timestamp_utc
        ))
    
    def find_by_content_reference(
        self,
        content_reference: str,
    ) -> Optional[ProtentionExpectation]:
        """
        Find an expectation by its expected content reference.
        
        Args:
            content_reference: Content reference to match
            
        Returns:
            Matching expectation if found
        """
        for expectation in self._expectations.values():
            if expectation.expected_content_reference == content_reference:
                return expectation
        return None
    
    def _clean_expired(self) -> int:
        """Remove expired expectations. Returns count removed."""
        expired_ids = [
            pid
            for pid, exp in self._expectations.items()
            if exp.is_expired
        ]
        
        for pid in expired_ids:
            del self._expectations[pid]
        
        return len(expired_ids)
    
    def clear(self) -> None:
        """Clear all expectations."""
        self._expectations.clear()


@dataclass(frozen=True)
class ProtentionBoundaries:
    """
    Bounded constraints for protention configuration.
    
    Defines limits and timeouts for protentional expectations.
    """
    
    max_expectations: int = 5
    """Maximum number of simultaneous expectations."""
    
    default_ttl_seconds: float = 60.0
    """Default TTL for new expectations (1 minute)."""
    
    @classmethod
    def default(cls) -> "ProtentionBoundaries":
        """Get the default protention boundaries."""
        return cls()
    
    @classmethod
    def strict(cls) -> "ProtentionBoundaries":
        """Get strict boundaries (minimal, short TTL)."""
        return cls(max_expectations=2)
    
    @classmethod
    def generous(cls) -> "ProtentionBoundaries":
        """Get generous boundaries (maximal, longer TTL)."""
        return cls(max_expectations=10)


__all__: Tuple[str, ...] = (
    "ProtentionExpectation",
    "ProtentionSet",
    "ProtentionBoundaries",
)