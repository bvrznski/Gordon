# Knowledge Belief System - Suspension Module - Phase 6.6
# =========================================================

"""
Suspension module for belief suspension handling.

This module handles suspending beliefs without rejecting them, preserving
history for potential reactivation when more evidence becomes available.
"""

from __future__ import annotations

import uuid
import time


class BeliefSuspensionManager:
    """
    Manages suspended beliefs and their expected resolution paths.
    
    Allows beliefs to be temporarily set aside while maintaining full
    history for potential re-evaluation later.
    """
    
    def __init__(self):
        """Initialize the suspension manager."""
        self._suspensions: dict = {}  # belief_id -> suspension record
    
    @property
    def suspended_belief_count(self) -> int:
        """Get count of currently suspended beliefs."""
        return len(self._suspensions)
    
    def suspend_belief(
        self,
        belief_id: str,
        reason: str,
        expected_resolution: str = None,
    ) -> dict:
        """
        Suspend a belief without rejecting it.
        
        Args:
            belief_id: ID of the belief to suspend
            reason: Reason for suspension (e.g., insufficient evidence)
            expected_resolution: When/why the suspension might end
            
        Returns:
            Suspension record dictionary
        """
        suspension_id = f"suspension:{uuid.uuid4().hex[:16]}"
        
        record = {
            "suspension_identity": suspension_id,
            "belief_id": belief_id,
            "reason": reason,
            "expected_resolution": expected_resolution,
            "suspended_at_utc": time.time(),
            "is_active": True,
        }
        
        self._suspensions[belief_id] = record
        return record
    
    def get_suspension(self, belief_id: str) -> dict | None:
        """Get suspension record for a belief."""
        return self._suspensions.get(belief_id)
    
    def get_all_suspensions(self) -> list:
        """Get all active suspensions."""
        return [
            {"belief_id": bid, **data}
            for bid, data in self._suspensions.items()
            if data.get("is_active", True)
        ]
    
    def extend_suspension(
        self,
        belief_id: str,
        new_expected_resolution: str,
    ) -> dict | None:
        """
        Extend the expected resolution time for a suspended belief.
        
        Args:
            belief_id: ID of the suspended belief
            new_expected_resolution: New expected resolution information
            
        Returns:
            Updated suspension record or None if not found
        """
        if belief_id not in self._suspensions:
            return None
        
        self._suspensions[belief_id]["expected_resolution"] = new_expected_resolution
        self._suspensions[belief_id]["extension_count"] = (
            self._suspensions[belief_id].get("extension_count", 0) + 1
        )
        
        return self._suspensions[belief_id]
    
    def resolve_suspension(
        self,
        belief_id: str,
        resolution_action: str,  # "reactivate", "reject", "accept"
    ) -> dict | None:
        """
        Resolve a suspension.
        
        Args:
            belief_id: ID of the suspended belief
            resolution_action: Action to take (reactivate, reject, accept)
            
        Returns:
            Resolution record or None if not found
        """
        if belief_id not in self._suspensions:
            return None
        
        record = self._suspensions[belief_id]
        record["is_active"] = False
        record["resolved_at_utc"] = time.time()
        record["resolution_action"] = resolution_action
        
        return record
    
    def clear_suspension(self, belief_id: str) -> bool:
        """Clear the suspension for a belief (for reset purposes)."""
        if belief_id in self._suspensions:
            del self._suspensions[belief_id]
            return True
        return False


class SuspensionReasonAnalyzer:
    """
    Analyzes reasons for belief suspensions.
    
    Categorizes and tracks common reasons why beliefs are suspended,
    helping identify patterns in evidence quality or gaps.
    """
    
    def __init__(self):
        """Initialize the analyzer."""
        self._reason_counts: dict = {}  # reason_category -> count
        self._all_reasons: list = []
    
    @property
    def total_suspensions_analyzed(self) -> int:
        """Get total number of suspension reasons analyzed."""
        return len(self._all_reasons)
    
    def categorize_reason(self, reason: str) -> str:
        """
        Categorize a suspension reason.
        
        Args:
            reason: The reason text
            
        Returns:
            Category string
        """
        reason_lower = reason.lower()
        
        if "insufficient" in reason_lower or "missing" in reason_lower:
            return "insufficient_evidence"
        elif "contradict" in reason_lower or "conflict" in reason_lower:
            return "contradictory_evidence"
        elif "unclear" in reason_lower or "ambiguous" in reason_lower:
            return "ambiguous_content"
        else:
            return "other"
    
    def record_suspension(self, reason: str):
        """
        Record a suspension reason for analysis.
        
        Args:
            reason: The reason for suspension
        """
        category = self.categorize_reason(reason)
        
        self._reason_counts[category] = self._reason_counts.get(category, 0) + 1
        self._all_reasons.append({
            "reason": reason,
            "category": category,
            "timestamp_utc": time.time(),
        })
    
    def get_category_stats(self) -> dict:
        """Get statistics by suspension reason category."""
        total = sum(self._reason_counts.values())
        
        return {
            "total_suspensions": total,
            "by_category": {
                cat: count
                for cat, count in self._reason_counts.items()
            },
            "percentages": {
                cat: (count / total * 100) if total > 0 else 0.0
                for cat, count in self._reason_counts.items()
            },
        }


class SuspensionHistory:
    """
    Maintains complete history of suspensions for a belief.
    
    Tracks when suspensions occurred and how they were resolved,
    enabling analysis of epistemic state over time.
    """
    
    def __init__(self, belief_id: str):
        """Initialize the history tracker."""
        self._belief_id = belief_id
        self._events: list = []
    
    @property
    def event_count(self) -> int:
        """Get count of recorded events."""
        return len(self._events)
    
    def add_suspension(
        self,
        suspension_id: str,
        reason: str,
        timestamp_utc: float = None,
    ):
        """
        Record a suspension event.
        
        Args:
            suspension_id: ID of the suspension
            reason: Reason for suspension
            timestamp_utc: Event timestamp (default: now)
        """
        self._events.append({
            "event_type": "suspension",
            "suspension_id": suspension_id,
            "reason": reason,
            "timestamp_utc": timestamp_utc or time.time(),
        })
    
    def add_resolution(
        self,
        resolution_action: str,
        timestamp_utc: float = None,
    ):
        """
        Record a resolution event.
        
        Args:
            resolution_action: How the suspension was resolved
            timestamp_utc: Event timestamp (default: now)
        """
        self._events.append({
            "event_type": "resolution",
            "resolution_action": resolution_action,
            "timestamp_utc": timestamp_utc or time.time(),
        })
    
    def get_all_events(self) -> list:
        """Get all events in chronological order."""
        return list(self._events)
    
    def to_dict(self) -> dict:
        """Convert history to dictionary."""
        return {
            "belief_id": self._belief_id,
            "event_count": len(self._events),
            "events": self._events,
        }


__all__ = [
    "BeliefSuspensionManager",
    "SuspensionReasonAnalyzer",
    "SuspensionHistory",
]