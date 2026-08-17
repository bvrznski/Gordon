# Knowledge Belief System - Uncertainty Module - Phase 6.6
# ===========================================================

"""
Uncertainty module for belief uncertainty management.

This module handles epistemic uncertainty metrics and their propagation,
distinguishing between low confidence and unresolved questions.
"""

from __future__ import annotations

import uuid
import time


class UncertaintyEngine:
    """
    Manages uncertainty metrics for beliefs.
    
    Tracks sources of uncertainty, unresolved questions, and provides
    uncertainty measures that remain independent from confidence values.
    """
    
    def __init__(self):
        """Initialize the uncertainty engine."""
        self._uncertainties: dict = {}  # belief_id -> {measure, sources, questions}
    
    @property
    def belief_count(self) -> int:
        """Get count of tracked beliefs with uncertainty metrics."""
        return len(self._uncertainties)
    
    def get_uncertainty(self, belief_id: str) -> float | None:
        """Get the current uncertainty measure for a belief."""
        if belief_id not in self._uncertainties:
            return None
        return self._uncertainties[belief_id].get("measure", 0.5)
    
    def set_uncertainty(
        self,
        belief_id: str,
        measure: float,
        sources: list[str] = None,
    ) -> dict:
        """
        Set uncertainty for a belief.
        
        Args:
            belief_id: ID of the belief
            measure: Uncertainty value (0.0-1.0)
            sources: Optional list of uncertainty sources
            
        Returns:
            Update record dictionary
        """
        measure = max(0.0, min(1.0, float(measure)))
        
        if belief_id not in self._uncertainties:
            self._uncertainties[belief_id] = {
                "measure": measure,
                "sources": set(),
                "questions": [],
                "history": [],
            }
        
        record = {
            "belief_id": belief_id,
            "previous_uncertainty": self._uncertainties[belief_id]["measure"],
            "new_uncertainty": measure,
            "timestamp_utc": time.time(),
            "source_count": len(sources or []),
        }
        
        self._uncertainties[belief_id]["history"].append(record)
        self._uncertainties[belief_id]["measure"] = measure
        if sources:
            self._uncertainties[belief_id]["sources"].update(sources)
        
        return record
    
    def add_uncertainty_source(
        self,
        belief_id: str,
        source_description: str,
    ) -> dict:
        """
        Add a new uncertainty source to a belief.
        
        Args:
            belief_id: ID of the belief
            source_description: Description of the new uncertainty source
            
        Returns:
            Update record dictionary
        """
        if belief_id not in self._uncertainties:
            self._uncertainties[belief_id] = {
                "measure": 0.5,
                "sources": set(),
                "questions": [],
                "history": [],
            }
        
        measure = self._uncertainties[belief_id]["measure"]
        new_measure = min(1.0, measure * 1.1)  # Increase uncertainty
        
        record = {
            "belief_id": belief_id,
            "previous_uncertainty": measure,
            "new_uncertainty": new_measure,
            "source_added": source_description,
            "timestamp_utc": time.time(),
        }
        
        self._uncertainties[belief_id]["sources"].add(source_description)
        self._uncertainties[belief_id]["measure"] = new_measure
        self._uncertainties[belief_id]["history"].append(record)
        
        return record
    
    def resolve_uncertainty_source(
        self,
        belief_id: str,
        resolved_source: str,
    ) -> dict:
        """
        Mark an uncertainty source as resolved.
        
        Args:
            belief_id: ID of the belief
            resolved_source: The uncertainty source to mark as resolved
            
        Returns:
            Update record dictionary
        """
        if belief_id not in self._uncertainties:
            return {"error": "Belief not found", "belief_id": belief_id}
        
        sources = self._uncertainties[belief_id]["sources"]
        
        if resolved_source not in sources:
            return {"error": "Source not found", "source": resolved_source}
        
        new_sources = sources - {resolved_source}
        measure = self._uncertainties[belief_id]["measure"]
        
        # Decrease uncertainty when source is resolved
        new_measure = max(0.0, measure * 0.9)
        
        record = {
            "belief_id": belief_id,
            "previous_uncertainty": measure,
            "new_uncertainty": new_measure,
            "source_resolved": resolved_source,
            "remaining_sources": len(new_sources),
            "timestamp_utc": time.time(),
        }
        
        self._uncertainties[belief_id]["sources"] = new_sources
        self._uncertainties[belief_id]["measure"] = new_measure
        self._uncertainties[belief_id]["history"].append(record)
        
        return record
    
    def get_all_uncertainties(self) -> dict:
        """Get current uncertainty for all tracked beliefs."""
        return {
            bid: data.get("measure", 0.5)
            for bid, data in self._uncertainties.items()
        }
    
    def clear_belief(self, belief_id: str):
        """Clear all uncertainty tracking for a belief."""
        if belief_id in self._uncertainties:
            del self._uncertainties[belief_id]


class UncertaintyPropagator:
    """
    Propagates uncertainty values through belief dependency graphs.
    
    Ensures that missing evidence increases rather than decreases
    uncertainty, and propagates independently from confidence.
    """
    
    def __init__(self):
        """Initialize the propagator."""
        self._propagation_count = 0
    
    @property
    def total_propagations(self) -> int:
        """Get total number of propagation operations."""
        return self._propagation_count
    
    def propagate_accumulate(
        self,
        source_uncertainties: list[float],
        base_uncertainty: float = None,
    ) -> float:
        """
        Propagate uncertainty using accumulation strategy.
        
        Missing evidence increases uncertainty rather than implying rejection.
        
        Args:
            source_uncertainties: Uncertainty values from source beliefs
            base_uncertainty: Optional baseline uncertainty
            
        Returns:
            Accumulated uncertainty value
        """
        if not source_uncertainties:
            return base_uncertainty or 0.5
        
        # Sum uncertainties (representing increased uncertainty)
        result = sum(source_uncertainties) / len(source_uncertainties)
        
        self._propagation_count += 1
        return min(1.0, result)
    
    def propagate_max(
        self,
        source_uncertainties: list[float],
        base_uncertainty: float = None,
    ) -> float:
        """
        Propagate uncertainty using maximum strategy.
        
        Conservative approach - use the highest uncertainty value.
        
        Args:
            source_uncertainties: Uncertainty values from source beliefs
            base_uncertainty: Optional baseline uncertainty
            
        Returns:
            Maximum (conservative) uncertainty value
        """
        if not source_uncertainties:
            return base_uncertainty or 0.5
        
        result = max(source_uncertainties)
        self._propagation_count += 1
        return result
    
    def propagate_with_evidence_penalty(
        self,
        source_uncertainties: list[float],
        evidence_ratio: float,  # Ratio of evidence to total (0.0-1.0)
    ) -> float:
        """
        Propagate uncertainty with penalty based on evidence ratio.
        
        Args:
            source_uncertainties: Uncertainty values from source beliefs
            evidence_ratio: Ratio of supporting evidence (0.0 = no evidence, 1.0 = all evidence)
            
        Returns:
            Evidence-adjusted uncertainty value
        """
        if not source_uncertainties:
            return 0.5
        
        avg_source = sum(source_uncertainties) / len(source_uncertainties)
        
        # Less evidence = higher uncertainty
        penalty = (1.0 - evidence_ratio) * 0.3  # Up to 0.3 additional uncertainty
        
        result = min(1.0, avg_source + penalty)
        self._propagation_count += 1
        return result


class UncertaintyHistory:
    """
    Maintains complete uncertainty history for a belief.
    
    Tracks all sources and measurements over time.
    """
    
    def __init__(self, belief_id: str):
        """Initialize the history tracker."""
        self._belief_id = belief_id
        self._measurements: list[tuple[int, float]] = []  # (revision, measure)
        self._sources_at_revision: dict = {}  # revision -> sources set
    
    @property
    def measurement_count(self) -> int:
        """Get count of uncertainty measurements."""
        return len(self._measurements)
    
    def add_measurement(
        self,
        revision: int,
        measure: float,
        sources: list[str] = None,
    ):
        """
        Add an uncertainty measurement.
        
        Args:
            revision: Revision number
            measure: Uncertainty value (0.0-1.0)
            sources: Optional list of sources at this revision
        """
        measure = max(0.0, min(1.0, float(measure)))
        self._measurements.append((revision, measure))
        if sources:
            self._sources_at_revision[revision] = set(sources)
    
    def get_latest_measurement(self) -> tuple[int, float] | None:
        """Get the most recent measurement."""
        if not self._measurements:
            return None
        return self._measurements[-1]
    
    def get_sources_at_revision(self, revision: int) -> set | None:
        """Get sources for a specific revision."""
        return self._sources_at_revision.get(revision)
    
    def to_dict(self) -> dict:
        """Convert history to dictionary."""
        return {
            "belief_id": self._belief_id,
            "measurement_count": len(self._measurements),
            "measurements": [
                {"revision": r, "uncertainty": m}
                for r, m in self._measurements
            ],
        }


class UncertaintyValidator:
    """
    Validates uncertainty values and updates.
    
    Ensures uncertainty measures stay within valid ranges and that
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
        Validate an uncertainty measure.
        
        Args:
            measure: The measure to validate
            
        Returns:
            Tuple of (is_valid, error_message if invalid)
        """
        if not isinstance(measure, (int, float)):
            return False, f"Uncertainty must be numeric, got {type(measure)}"
        
        if measure < 0.0 or measure > 1.0:
            return False, f"Uncertainty out of range: {measure} (must be 0.0-1.0)"
        
        return True, None
    
    def validate_independence(
        self,
        confidence: float,
        uncertainty: float,
    ) -> tuple[bool, str | None]:
        """
        Validate that confidence and uncertainty are properly independent.
        
        Args:
            confidence: Confidence value (0.0-1.0)
            uncertainty: Uncertainty value (0.0-1.0)
            
        Returns:
            Tuple of (is_valid, error_message if invalid)
        """
        valid, msg = self.validate_measure(confidence)
        if not valid:
            return False, f"Confidence: {msg}"
        
        valid, msg = self.validate_measure(uncertainty)
        if not valid:
            return False, f"Uncertainty: {msg}"
        
        # Confidence and uncertainty should be independent metrics
        # They don't need to sum to 1.0
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
    "UncertaintyEngine",
    "UncertaintyPropagator",
    "UncertaintyHistory",
    "UncertaintyValidator",
]