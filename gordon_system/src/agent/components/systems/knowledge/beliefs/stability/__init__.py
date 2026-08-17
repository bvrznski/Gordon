# Knowledge Belief System - Stability Module - Phase 6.6
# =======================================================

"""
Stability module for belief stability tracking.

This module tracks how stable beliefs are over time, measuring resistance
to revision based on history and supporting evidence.
"""

from __future__ import annotations

import uuid
import time


class BeliefStabilityManager:
    """
    Manages stability metrics for beliefs.
    
    Tracks accumulated stability over time and provides measures of
    belief resilience to revision.
    """
    
    def __init__(self):
        """Initialize the stability manager."""
        self._stabilities: dict = {}  # belief_id -> {measure, history}
    
    @property
    def tracked_belief_count(self) -> int:
        """Get count of beliefs with stability metrics."""
        return len(self._stabilities)
    
    def get_stability(self, belief_id: str) -> float | None:
        """Get the current stability measure for a belief."""
        if belief_id not in self._stabilities:
            return None
        return self._stabilities[belief_id].get("measure", 0.0)
    
    def initialize_stability(
        self,
        belief_id: str,
        initial_measure: float = 0.0,
    ) -> dict:
        """
        Initialize stability tracking for a new belief.
        
        Args:
            belief_id: ID of the belief
            initial_measure: Starting stability measure
            
        Returns:
            Initialization record dictionary
        """
        self._stabilities[belief_id] = {
            "measure": max(0.0, min(1.0, float(initial_measure))),
            "history": [],
            "supporting_evidence_ids": set(),
            "confirmation_count": 0,
        }
        
        return {"belief_id": belief_id, "initialized": True}
    
    def accumulate_stability(
        self,
        belief_id: str,
        additional_measure: float,
        evidence_id: str = None,
    ) -> dict:
        """
        Accumulate stability for a belief.
        
        Args:
            belief_id: ID of the belief
            additional_measure: Amount to add to stability (0.0-1.0)
            evidence_id: Optional ID of supporting evidence
            
        Returns:
            Update record dictionary
        """
        if belief_id not in self._stabilities:
            self.initialize_stability(belief_id)
        
        current = self._stabilities[belief_id]["measure"]
        new_measure = min(1.0, current + additional_measure)
        
        record = {
            "belief_id": belief_id,
            "previous_stability": current,
            "new_stability": new_measure,
            "added_measure": additional_measure,
            "timestamp_utc": time.time(),
        }
        
        self._stabilities[belief_id]["measure"] = new_measure
        self._stabilities[belief_id]["history"].append(record)
        if evidence_id:
            self._stabilities[belief_id]["supporting_evidence_ids"].add(evidence_id)
        
        return record
    
    def confirm_belief(
        self,
        belief_id: str,
        confidence_boost: float = 0.1,
        stability_boost: float = 0.05,
    ) -> dict:
        """
        Record a confirmation of a belief.
        
        Args:
            belief_id: ID of the belief
            confidence_boost: How much to boost confidence (default: 0.1)
            stability_boost: How much to boost stability (default: 0.05)
            
        Returns:
            Confirmation record dictionary
        """
        if belief_id not in self._stabilities:
            self.initialize_stability(belief_id)
        
        current_measure = self._stabilities[belief_id]["measure"]
        new_measure = min(1.0, current_measure + stability_boost)
        
        record = {
            "belief_id": belief_id,
            "previous_stability": current_measure,
            "new_stability": new_measure,
            "confidence_boost": confidence_boost,
            "stability_boost": stability_boost,
            "timestamp_utc": time.time(),
        }
        
        self._stabilities[belief_id]["measure"] = new_measure
        self._stabilities[belief_id]["history"].append(record)
        self._stabilities[belief_id]["confirmation_count"] += 1
        
        return record
    
    def get_history(self, belief_id: str) -> list:
        """
        Get stability history for a belief.
        
        Args:
            belief_id: ID of the belief
            
        Returns:
            List of stability update records
        """
        if belief_id not in self._stabilities:
            return []
        return list(self._stabilities[belief_id]["history"])


class StabilityTracker:
    """
    Tracks long-term stability trends for beliefs.
    
    Records historical measurements over time to enable trend analysis
    and stability assessment across revision cycles.
    """
    
    def __init__(self, belief_id: str):
        """Initialize the tracker."""
        self._belief_id = belief_id
        self._measurements: list[tuple[int, float]] = []  # (revision, measure)
    
    @property
    def measurement_count(self) -> int:
        """Get count of recorded measurements."""
        return len(self._measurements)
    
    def add_measurement(
        self,
        revision: int,
        stability_measure: float,
    ):
        """
        Add a stability measurement at a specific revision.
        
        Args:
            revision: Revision number
            stability_measure: Stability value (0.0-1.0)
        """
        measure = max(0.0, min(1.0, float(stability_measure)))
        self._measurements.append((revision, measure))
    
    def get_latest_measurement(self) -> tuple[int, float] | None:
        """Get the most recent measurement."""
        if not self._measurements:
            return None
        return self._measurements[-1]
    
    def calculate_stability_trend(self) -> str:
        """
        Calculate stability trend from measurements.
        
        Returns: "increasing", "stable", or "decreasing"
        """
        if len(self._measurements) < 2:
            return "stable"
        
        first_half = self._measurements[:len(self._measurements)//2]
        second_half = self._measurements[len(self._measurements)//2:]
        
        first_avg = sum(m[1] for m in first_half) / len(first_half)
        second_avg = sum(m[1] for m in second_half) / len(second_half)
        
        diff = second_avg - first_avg
        
        if diff > 0.05:
            return "increasing"
        elif diff < -0.05:
            return "decreasing"
        else:
            return "stable"
    
    def to_dict(self) -> dict:
        """Convert tracker data to dictionary."""
        trend = self.calculate_stability_trend()
        
        return {
            "belief_id": self._belief_id,
            "measurement_count": len(self._measurements),
            "latest_measure": (
                self._measurements[-1][1] if self._measurements else 0.0
            ),
            "trend": trend,
        }


class StabilityHistory:
    """
    Maintains complete stability history for a belief.
    
    Tracks all stability measurements over the lifetime of a belief,
    enabling analysis of how stability has accumulated over time.
    """
    
    def __init__(self, belief_id: str):
        """Initialize the history tracker."""
        self._belief_id = belief_id
        self._entries: list = []
    
    @property
    def entry_count(self) -> int:
        """Get count of recorded entries."""
        return len(self._entries)
    
    def add_entry(
        self,
        revision: int,
        stability_measure: float,
        supporting_evidence_ids: list[str] = None,
        timestamp_utc: float = None,
    ):
        """
        Add a stability history entry.
        
        Args:
            revision: Revision number
            stability_measure: Stability value (0.0-1.0)
            supporting_evidence_ids: Evidence IDs at this point
            timestamp_utc: Entry timestamp (default: now)
        """
        measure = max(0.0, min(1.0, float(stability_measure)))
        
        entry = {
            "revision": revision,
            "stability_measure": measure,
            "supporting_evidence_ids": supporting_evidence_ids or [],
            "timestamp_utc": timestamp_utc or time.time(),
        }
        
        self._entries.append(entry)
    
    def get_all_entries(self) -> list:
        """Get all history entries in order."""
        return list(self._entries)
    
    def to_dict(self) -> dict:
        """Convert history to dictionary."""
        return {
            "belief_id": self._belief_id,
            "entry_count": len(self._entries),
            "latest_stability": (
                self._entries[-1]["stability_measure"] if self._entries else 0.0
            ),
            "entries": self._entries,
        }


__all__ = [
    "BeliefStabilityManager",
    "StabilityTracker",
    "StabilityHistory",
]