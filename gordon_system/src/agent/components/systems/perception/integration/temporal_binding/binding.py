# Temporal Binding - Phase 5.2.3
# =============================

"""
Core temporal binding logic.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Tuple, Optional, Any
import time
import uuid


@dataclass(frozen=True)
class TemporalBinding:
    """
    A temporal binding of artifacts into a coherent structure.
    
    Fields:
        binding_identity: Unique identifier
        bound_artifacts: Which artifacts are bound together?
        binding_window: Time window containing the binding
        temporal_relations: Relations between artifacts (before, after, simultaneous)
        ordering_constraints: Known ordering constraints
        missing_intervals: Gaps in observation
        temporal_residuals: Timing differences that couldn't be explained
    """
    
    binding_identity: str
    
    bound_artifacts: Tuple[str, ...]
    
    binding_window: Dict[str, float] = field(default_factory=dict)  # start, end, tolerance
    temporal_relations: Tuple[Dict[str, Any], ...] = field(default_factory=tuple)
    ordering_constraints: Tuple[str, ...] = field(default_factory=tuple)
    
    missing_intervals: Tuple[Dict[str, Any], ...] = field(default_factory=tuple)
    temporal_residuals: Tuple[str, ...] = field(default_factory=tuple)
    
    confidence: float = 1.0
    uncertainty: float = 0.0
    
    alternatives: Tuple[str, ...] = field(default_factory=tuple)
    
    provenance: Dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class BindingWindow:
    """
    A temporal window for binding artifacts.
    
    Fields:
        window_identity: Unique identifier
        start: Start time (UTC epoch seconds)
        end: End time (UTC epoch seconds)
        tolerance: Maximum acceptable timing difference (seconds)
        source_latency_allowances: Per-modality latency allowances
        event_density_constraints: Minimum/maximum events per interval
    """
    
    window_identity: str
    
    start: float  # UTC epoch
    end: float    # UTC epoch
    tolerance: float = 1.0  # seconds
    
    source_latency_allowances: Dict[str, float] = field(default_factory=dict)  # modality -> max_delay_seconds
    event_density_constraints: Dict[str, Any] = field(default_factory=dict)
    
    window_policy: str = "fixed"  # fixed, adaptive, event_defined, etc.
    
    provenance: Dict[str, Any] = field(default_factory=dict)
    
    @property
    def duration(self) -> float:
        """Duration of the binding window in seconds."""
        return self.end - self.start
    
    def contains_time(self, t: float) -> bool:
        """Check if a time is within this window (with tolerance)."""
        return self.start - self.tolerance <= t <= self.end + self.tolerance
    
    def overlaps_with(self, other_start: float, other_end: float) -> bool:
        """Check if this window overlaps with another time range."""
        return not (other_end < self.start or other_start > self.end)