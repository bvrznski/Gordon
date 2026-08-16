# Reward Network - Uncertainty Estimator
# =======================================

"""
Uncertainty estimator for reward evaluation.

Reward uncertainty represents unknown information about reward estimation.
It is independent from confidence (which measures reliability).

UNCERTAINTY LAWS:
    UNCERTAINTY-LAW-001: Reward uncertainty remains explicitly represented.
    UNCERTAINTY-LAW-002: Reward uncertainty remains independent from confidence.
    UNCERTAINTY-LAW-003: Unknown uncertainty remains distinguishable from low uncertainty.
    UNCERTAINTY-LAW-004: Reward uncertainty shall never be computed as:
        1 - confidence
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Tuple, Optional


@dataclass(frozen=True)
class UncertaintyEstimate:
    """
    Estimate of reward unknown information.
    
    Uncertainty represents gaps in available information for reward estimation,
    distinct from confidence which measures reliability of existing estimates.
    
    UNCERTAINTY KINDS:
        • high: Significant information gaps in estimation
        • medium: Moderate uncertainty about some factors  
        • low: Reasonable certainty about most factors
        • unknown: Cannot determine uncertainty from available data
        
    UNCERTAINTY INVARIANTS:
        • Uncertainty is independent from confidence
        • Unknown uncertainty is distinguishable from low uncertainty
        • Uncertainty is never computed as 1 - confidence
    """
    
    kind: str = "unknown"
    """Uncertainty level (high, medium, low, unknown)."""
    
    information_gaps: Tuple[str, ...] = field(default_factory=tuple)
    """Descriptions of missing information."""
    
    evidence: Tuple[str, ...] = field(default_factory=tuple)
    """Evidence supporting this uncertainty assessment."""
    
    provenance: Optional[str] = None
    """Provenance reference for this estimation method."""
    
    @property
    def is_high(self) -> bool:
        """Check if uncertainty is high."""
        return self.kind == "high"
    
    @property
    def is_medium(self) -> bool:
        """Check if uncertainty is medium."""
        return self.kind == "medium"
    
    @property
    def is_low(self) -> bool:
        """Check if uncertainty is low."""
        return self.kind == "low"
    
    @property
    def is_unknown(self) -> bool:
        """Check if uncertainty is unknown."""
        return self.kind == "unknown"