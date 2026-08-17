# Knowledge Belief System - Confidence Module - Phase 6.6
# =========================================================

"""
Confidence module for belief confidence management.

This module handles epistemic confidence metrics and propagation through the
belief dependency graph.
"""

from __future__ import annotations

import uuid
import time


class ConfidenceEngine:
    """
    Manages confidence metrics for beliefs.
    
    Tracks, updates, and propagates confidence values while maintaining history
    and provenance for traceability.
    """
    
    def __init__(self):
        """Initialize the confidence engine."""
        self._confidences: dict = {}  # belief_id -> {measure, history}
    
    @property
    def belief_count(self) -> int:
        """Get count of tracked beliefs with confidence metrics."""
        return len(self._confidences)
    
    def get_confidence(self, belief_id: str) -> float | None:
        """Get the current confidence measure for a belief."""
        if belief_id not in self._confidences:
            return None
        return self._confidences[belief_id].get("measure", 0.5)
    
    def set_confidence(
        self,
        belief_id: str,
        measure: float,
        source_id: str = None,
    ) -> dict:
        """
        Set confidence for a belief.
        
        Args:
            belief_id: ID of the belief
            measure: Confidence value (0.0-1.0)
            source_id: Optional ID of what set this confidence
            
        Returns:
            Update record dictionary
        """
        measure = max(0.0, min(1.0, float(measure)))
        
        if belief_id not in self._confidences:
            self._confidences[belief_id] = {
                "measure": measure,
                "history": [],
                "sources": set(),
            }
        
        record = {
            "belief_id": belief_id,
            "previous_confidence": self._confidences[belief_id]["measure"],
            "new_confidence": measure,
            "timestamp_utc": time.time(),
            "source": source_id,
        }
        
        self._confidences[belief_id]["history"].append(record)
        self._confidences[belief_id]["measure"] = measure
        if source_id:
            self._confidences[belief_id]["sources"].add(source_id)
        
        return record
    
    def update_confidence(
        self,
        belief_id: str,
        delta: float,
        source_id: str = None,
    ) -> dict:
        """
        Update confidence by a delta amount.
        
        Args:
            belief_id: ID of the belief
            delta: Amount to change confidence (can be negative)
            source_id: Optional ID of what triggered this update
            
        Returns:
            Update record dictionary
        """
        current = self.get_confidence(belief_id) or 0.5
        new_value = max(0.0, min(1.0, current + delta))
        
        return self.set_confidence(belief_id, new_value, source_id)
    
    def get_history(self, belief_id: str, limit: int = None) -> list:
        """
        Get confidence history for a belief.
        
        Args:
            belief_id: ID of the belief
            limit: Maximum number of history items to return
            
        Returns:
            List of confidence change records
        """
        if belief_id not in self._confidences:
            return []
        
        history = list(self._confidences[belief_id]["history"])
        if limit is not None:
            history = history[-limit:]
        return history
    
    def get_all_confidences(self) -> dict:
        """Get current confidence for all tracked beliefs."""
        return {
            bid: data.get("measure", 0.5)
            for bid, data in self._confidences.items()
        }


class ConfidencePropagator:
    """
    Propagates confidence values through belief dependency graphs.
    
    Implements strategies like averaging, weighted propagation, and
    boundary-based updates.
    """
    
    def __init__(self):
        """Initialize the propagator."""
        self._propagation_count = 0
    
    @property
    def total_propagations(self) -> int:
        """Get total number of propagation operations."""
        return self._propagation_count
    
    def propagate_average(
        self,
        source_confidences: list[float],
    ) -> float:
        """
        Propagate confidence using averaging strategy.
        
        Args:
            source_confidences: Confidence values from source beliefs
            
        Returns:
            Averaged confidence value
        """
        if not source_confidences:
            return 0.5
        
        result = sum(source_confidences) / len(source_confidences)
        self._propagation_count += 1
        return result
    
    def propagate_weighted(
        self,
        source_confidences: list[float],
        weights: list[float] = None,
    ) -> float:
        """
        Propagate confidence using weighted averaging.
        
        Args:
            source_confidences: Confidence values from source beliefs
            weights: Optional weights for each source (must match length)
            
        Returns:
            Weighted average confidence value
        """
        if not source_confidences:
            return 0.5
        
        if weights is None or len(weights) != len(source_confidences):
            # Default to equal weights
            weights = [1.0] * len(source_confidences)
        
        total_weight = sum(weights)
        weighted_sum = sum(c * w for c, w in zip(source_confidences, weights))
        
        result = weighted_sum / total_weight if total_weight > 0 else 0.5
        self._propagation_count += 1
        return result
    
    def propagate_min(
        self,
        source_confidences: list[float],
        base_confidence: float = None,
    ) -> float:
        """
        Propagate confidence using minimum strategy.
        
        Conservative approach - the propagated confidence is the minimum
        of all sources, ensuring we don't overstate confidence.
        
        Args:
            source_confidences: Confidence values from source beliefs
            base_confidence: Optional baseline confidence
            
        Returns:
            Minimum (conservative) confidence value
        """
        if not source_confidences:
            return base_confidence or 0.5
        
        result = min(source_confidences)
        self._propagation_count += 1
        return result
    
    def propagate_max(
        self,
        source_confidences: list[float],
        base_confidence: float = None,
    ) -> float:
        """
        Propagate confidence using maximum strategy.
        
        Optimistic approach - the propagated confidence is the maximum
        of all sources.
        
        Args:
            source_confidences: Confidence values from source beliefs
            base_confidence: Optional baseline confidence
            
        Returns:
            Maximum (optimistic) confidence value
        """
        if not source_confidences:
            return base_confidence or 0.5
        
        result = max(source_confidences)
        self._propagation_count += 1
        return result
    
    def propagate_with_decay(
        self,
        source_confidences: list[float],
        decay_factor: float = 0.9,
    ) -> float:
        """
        Propagate confidence with decay based on distance.
        
        Reduces propagated confidence as it moves through the dependency graph,
        reflecting potential information loss or degradation.
        
        Args:
            source_confidences: Confidence values from source beliefs
            decay_factor: Factor to multiply by (less than 1.0)
            
        Returns:
            Decay-adjusted confidence value
        """
        if not source_confidences:
            return 0.5
        
        average = sum(source_confidences) / len(source_confidences)
        result = max(0.0, min(1.0, average * decay_factor))
        self._propagation_count += 1
        return result


class ConfidenceHistory:
    """
    Maintains complete confidence history for a belief.
    
    Tracks all confidence values over time with revision numbers,
    enabling reconstruction of how confidence evolved.
    """
    
    def __init__(self, belief_id: str):
        """Initialize the history tracker."""
        self._belief_id = belief_id
        self._measurements: list[tuple[int, float]] = []  # (revision, measure)
        self._sources: dict = {}  # revision -> source info
    
    @property
    def measurement_count(self) -> int:
        """Get count of confidence measurements."""
        return len(self._measurements)
    
    def add_measurement(
        self,
        revision: int,
        measure: float,
        source: str = None,
    ):
        """
        Add a confidence measurement.
        
        Args:
            revision: Revision number
            measure: Confidence value (0.0-1.0)
            source: Optional source identifier
        """
        measure = max(0.0, min(1.0, float(measure)))
        self._measurements.append((revision, measure))
        if source:
            self._sources[revision] = source
    
    def get_latest_measurement(self) -> tuple[int, float] | None:
        """Get the most recent measurement."""
        if not self._measurements:
            return None
        return self._measurements[-1]
    
    def get_all_measurements(self) -> list[tuple[int, float]]:
        """Get all measurements in order."""
        return list(self._measurements)
    
    def get_source_at_revision(self, revision: int) -> str | None:
        """Get source for a specific revision."""
        return self._sources.get(revision)
    
    def to_dict(self) -> dict:
        """Convert history to dictionary."""
        return {
            "belief_id": self._belief_id,
            "measurement_count": len(self._measurements),
            "measurements": [
                {"revision": r, "confidence": m}
                for r, m in self._measurements
            ],
        }


class ConfidenceValidator:
    """
    Validates confidence values and updates.
    
    Ensures confidence measures stay within valid ranges and that
    updates follow proper patterns.
    """
    
    def __init__(self):
        """Initialize the validator."""
        self._violations: list = []
    
    @property
    def violation_count(self) -> int:
        """Get count of recorded violations."""
        return len(self._violations)
    
    def validate_measure(self, measure: float) -> tuple[bool, str | None]:
        """
        Validate a confidence measure.
        
        Args:
            measure: The measure to validate
            
        Returns:
            Tuple of (is_valid, error_message if invalid)
        """
        if not isinstance(measure, (int, float)):
            return False, f"Confidence must be numeric, got {type(measure)}"
        
        if measure < 0.0 or measure > 1.0:
            return False, f"Confidence out of range: {measure} (must be 0.0-1.0)"
        
        return True, None
    
    def validate_update(
        self,
        previous: float,
        current: float,
        delta: float = None,
    ) -> tuple[bool, str | None]:
        """
        Validate a confidence update.
        
        Args:
            previous: Previous confidence value
            current: New confidence value
            delta: Optional delta between them
            
        Returns:
            Tuple of (is_valid, error_message if invalid)
        """
        valid, msg = self.validate_measure(previous)
        if not valid:
            return False, f"Previous confidence: {msg}"
        
        valid, msg = self.validate_measure(current)
        if not valid:
            return False, f"New confidence: {msg}"
        
        # Check delta consistency
        if delta is not None:
            expected_delta = current - previous
            if abs(expected_delta - delta) > 0.01:
                return False, f"Delta mismatch: reported {delta}, actual {expected_delta:.4f}"
        
        return True, None
    
    def record_violation(self, violation: str):
        """Record a validation violation."""
        self._violations.append({
            "violation": violation,
            "timestamp_utc": time.time(),
        })
    
    def clear_violations(self):
        """Clear all violations."""
        self._violations.clear()


__all__ = [
    "ConfidenceEngine",
    "ConfidencePropagator",
    "ConfidenceHistory",
    "ConfidenceValidator",
]