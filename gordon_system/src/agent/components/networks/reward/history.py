# Reward Network - Temporal Reward History Module (Phase 4.10.4)
# ===============================================================

"""
Temporal reward history module for maintaining immutable records of reward
evaluations and their temporal evolution over time.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Tuple, Optional


@dataclass(frozen=True)
class RewardHistoryEntry:
    """
    Immutable record of a single reward evaluation at a point in time.
    
    History entries preserve the complete semantic context of each evaluation,
    enabling analysis of temporal patterns without modifying any system state.
    
    PROPERTIES:
        • entry_id: Unique identifier for this history entry
        • timestamp: When this evaluation occurred (semantic, not wall-clock)
        • landscape_id: Reference to the RewardLandscape evaluated
        • estimate_refs: References to all reward estimates in that landscape
        
    NOT RESPONSIBLE FOR:
        • Modifying historical records
        • Learning from history
        • Making decisions based on history
    """
    
    # Identity and reference (no defaults first)
    entry_id: str
    """Unique identifier for this history entry."""
    
    timestamp: str
    """Semantic time when this evaluation occurred."""
    
    landscape_id: str
    """Reference to the RewardLandscape that was evaluated."""
    
    revision: int = 0
    """Revision number for versioning."""
    
    sequence_number: int = 0
    """Position in observation sequence (for temporal ordering)."""
    
    estimate_refs: Tuple[str, ...] = field(default_factory=tuple)
    """References to all reward estimates in that landscape."""
    
    # Summary values (always preserved for analysis)
    total_magnitude: float = 0.0
    """Sum of all estimate magnitudes at evaluation time."""
    
    positive_count: int = 0
    negative_count: int = 0
    neutral_count: int = 0
    
    # Semantic context
    provenance: Optional[str] = None
    """Provenance reference for this history entry."""
    
    trace: Tuple[str, ...] = field(default_factory=tuple)
    """Evaluation trace for provenance."""
    
    @property
    def canonical_identity(self) -> str:
        """Return fully qualified canonical identity."""
        return f"{self.entry_id}@v{self.revision}"
    
    @property
    def estimate_count(self) -> int:
        """Get count of estimates in this history entry."""
        return len(self.estimate_refs)
    
    @classmethod
    def create_entry(
        cls,
        entry_id: str,
        timestamp: str,
        landscape_id: str,
        total_magnitude: float = 0.0,
        positive_count: int = 0,
        negative_count: int = 0,
        neutral_count: int = 0,
        sequence_number: int = 0,
    ) -> RewardHistoryEntry:
        """Create a new history entry."""
        return cls(
            entry_id=entry_id,
            timestamp=timestamp,
            landscape_id=landscape_id,
            total_magnitude=total_magnitude,
            positive_count=positive_count,
            negative_count=negative_count,
            neutral_count=neutral_count,
            sequence_number=sequence_number,
        )


@dataclass(frozen=True)
class RewardHistory:
    """
    Immutable record of reward evaluation history over time.
    
    History maintains a complete, append-only log of all reward evaluations,
    enabling temporal analysis without modifying any previous state.
    
    PROPERTIES:
        • history_id: Unique identifier for this history
        • entries: Sequence of historical evaluation records
        • first_evaluation: First recorded evaluation
        • last_evaluation: Most recent evaluation
        • observation_count: Total number of observations
        
    NOT RESPONSIBLE FOR:
        • Modifying historical records (they are immutable)
        • Learning from historical patterns
        • Making decisions based on history
    """
    
    # Identity and reference (no defaults first)
    history_id: str
    """Unique identifier for this reward history."""
    
    # History storage (always preserved)
    entries: Tuple[RewardHistoryEntry, ...] = field(default_factory=tuple)
    """Sequence of historical evaluation records."""
    
    # Semantic context (with defaults last)
    provenance: Optional[str] = None
    """Provenance reference for this history collection."""
    
    revision: int = 0
    """Revision number for versioning."""
    
    findings: Tuple[str, ...] = field(default_factory=tuple)
    """Key findings from history analysis."""
    
    trace: Tuple[str, ...] = field(default_factory=tuple)
    """History analysis trace for provenance."""
    
    @property
    def canonical_identity(self) -> str:
        """Return fully qualified canonical identity."""
        return f"{self.history_id}@v{self.revision}"
    
    @property
    def observation_count(self) -> int:
        """Get count of historical observations."""
        return len(self.entries)
    
    @property
    def has_observations(self) -> bool:
        """Check if history contains any observations."""
        return len(self.entries) > 0
    
    @property
    def first_evaluation(self) -> Optional[RewardHistoryEntry]:
        """Get the first evaluation in history (by sequence number)."""
        if not self.entries:
            return None
        
        # Sort by sequence number to get first
        sorted_entries = sorted(self.entries, key=lambda e: e.sequence_number)
        return sorted_entries[0]
    
    @property
    def last_evaluation(self) -> Optional[RewardHistoryEntry]:
        """Get the most recent evaluation in history."""
        if not self.entries:
            return None
        
        # Sort by sequence number to get last
        sorted_entries = sorted(self.entries, key=lambda e: e.sequence_number)
        return sorted_entries[-1]
    
    @property
    def estimate_history(self) -> Tuple[Tuple[str, float], ...]:
        """
        Get history of total magnitudes as (timestamp, value) pairs.
        
        Returns a tuple of (sequence_timestamp, magnitude) tuples for analysis.
        """
        if not self.entries:
            return tuple()
        
        return tuple(
            (e.timestamp, e.total_magnitude)
            for e in sorted(self.entries, key=lambda x: x.sequence_number)
        )
    
    @classmethod
    def create_empty(cls, history_id: str) -> RewardHistory:
        """Create an empty reward history."""
        return cls(
            history_id=history_id,
            entries=tuple(),
        )
    
    @classmethod
    def from_entries(
        cls,
        history_id: str,
        entries: Tuple[RewardHistoryEntry, ...],
    ) -> RewardHistory:
        """
        Create a reward history from individual entries.
        
        Entries are sorted by sequence number to ensure proper temporal ordering.
        """
        if not entries:
            return cls.create_empty(history_id)
        
        # Sort by sequence number for deterministic temporal order
        sorted_entries = tuple(
            sorted(entries, key=lambda e: e.sequence_number)
        )
        
        # Extract estimate history for analysis findings
        estimate_history = tuple(
            (e.timestamp, e.total_magnitude)
            for e in sorted_entries
        )
        
        return cls(
            history_id=history_id,
            entries=sorted_entries,
            findings=("history_created", f"count_{len(sorted_entries)}"),
        )


@dataclass(frozen=True)
class HistoryAnalyzer:
    """
    Deterministic reward history analyzer.
    
    Analyzes reward history to extract temporal patterns without modifying
    any historical records or making decisions based on the analysis.
    
    ANALYSIS METHOD:
        1. Extract and sort entries by sequence number
        2. Compute aggregate statistics across observations
        3. Identify patterns in temporal evolution
        
    NOT RESPONSIBLE FOR:
        • Modifying history (always immutable)
        • Learning from historical patterns
        • Making decisions based on analysis
    """
    
    @classmethod
    def analyze_history(cls, history: RewardHistory) -> Tuple[str, ...]:
        """
        Analyze a reward history and return findings as trace entries.
        
        Args:
            history: The RewardHistory to analyze
            
        Returns:
            Tuple of finding strings describing the analysis results
        """
        if not history.has_observations:
            return ("no_observations",)
        
        # Get estimate history for analysis
        estimate_history = history.estimate_history
        
        if len(estimate_history) < 2:
            return ("single_observation",)
        
        findings: list[str] = []
        
        # Extract magnitudes for trend analysis
        magnitudes = tuple(m for _, m in estimate_history)
        
        # Compute basic statistics
        mean_magnitude = sum(magnitudes) / len(magnitudes)
        variance = sum((m - mean_magnitude) ** 2 for m in magnitudes) / (len(magnitudes) - 1)
        
        findings.append(f"mean_magnitude_{mean_magnitude:.3f}")
        findings.append(f"variance_{variance:.3f}")
        
        # Analyze trend direction
        if len(estimate_history) >= 2:
            first_mag = magnitudes[0]
            last_mag = magnitudes[-1]
            
            if last_mag > first_mag * 1.1:
                findings.append("trend_increasing")
            elif last_mag < first_mag * 0.9:
                findings.append("trend_decreasing")
            else:
                findings.append("trend_stable")
        
        # Analyze stability
        std_dev = variance ** 0.5
        if std_dev <= mean_magnitude * 0.1 and mean_magnitude > 0:
            findings.append("high_stability")
        elif std_dev <= mean_magnitude * 0.3:
            findings.append("moderate_stability")
        else:
            findings.append("low_stability")
        
        findings.append(f"analysis_complete_{len(estimate_history)}_observations")
        
        return tuple(findings)
    
    @classmethod
    def get_temporal_span(cls, history: RewardHistory) -> Tuple[int, int]:
        """
        Get the temporal span of observations in the history.
        
        Returns:
            Tuple of (first_sequence_number, last_sequence_number)
        """
        if not history.has_observations:
            return (0, 0)
        
        sequence_numbers = [e.sequence_number for e in history.entries]
        return (min(sequence_numbers), max(sequence_numbers))