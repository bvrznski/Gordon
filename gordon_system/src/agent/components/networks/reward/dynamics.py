# Reward Network - Reward Dynamics
# ================================

"""
Reward dynamics model for tracking reward evaluation changes over time.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Tuple, Optional


@dataclass(frozen=True)
class RewardDynamics:
    """
    Track evolution of reward estimates over time.
    
    DYNAMICS TRACKS:
        • current: Current estimate value
        • historical: Past values
        • trend: Directional change (increasing/decreasing/stable)
        • volatility: Variability across evaluations
        
    NOT RESPONSIBLE FOR:
        • Learning policies from dynamics
        • Making decisions based on trends
        • Modifying estimates
    """
    
    dynamics_id: str = "default"
    """Unique identifier for this dynamics record."""
    
    current_value: float = 0.0
    """Current reward value."""
    
    historical_values: Tuple[float, ...] = field(default_factory=tuple)
    """Historical values for comparison."""
    
    trend: str = "stable"  # increasing/decreasing/stable
    """Directional change in reward value."""
    
    volatility: float = 0.0
    """Variability measure (0.0 to 1.0)."""
    
    @property
    def has_history(self) -> bool:
        """Check if historical data exists."""
        return len(self.historical_values) > 0
    
    @property
    def average_historical(self) -> float:
        """Compute average of historical values."""
        if not self.historical_values:
            return self.current_value
        return sum(self.historical_values) / len(self.historical_values)