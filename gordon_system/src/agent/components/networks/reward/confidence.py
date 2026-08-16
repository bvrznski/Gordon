# Reward Network - Confidence Estimator
# ======================================

"""
Confidence estimator for reward evaluation.

Reward confidence estimates how reliable a reward estimate is. It remains
independent from reward magnitude, precision, and prediction confidence.

CONFIDENCE LAWS:
    CONFIDENCE-LAW-001: Reward confidence remains independent from reward magnitude.
    CONFIDENCE-LAW-002: Reward confidence remains independent from precision.
    CONFIDENCE-LAW-003: Reward confidence remains independent from prediction confidence.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Tuple, Optional


@dataclass(frozen=True)
class ConfidenceEstimate:
    """
    Estimate of reward reliability and certainty.
    
    Confidence represents how reliably the reward estimate was computed,
    based on evidence quality, estimator confidence, and estimation context.
    
    CONFIDENCE INVARIANTS:
        • Confidence is independent from reward magnitude
        • Confidence is independent from precision estimates
        • Confidence is independent from prediction confidence
        
    HIGH REWARD with LOW confidence:
        - Strong benefit estimate but weak evidence
        - Potential overestimation risk
        
    LOW REWARD with HIGH confidence:  
        - Weak benefit/cost but strong evidence
        - Reliable negative assessment
    """
    
    value: float  # 0.0 to 1.0
    """Confidence level in the reward estimate."""
    
    basis: str = "default"
    """Basis for this confidence (e.g., 'sufficient_evidence', 'limited_data')."""
    
    evidence_quality: float = 1.0
    """Quality of underlying evidence supporting the estimate."""
    
    estimator_confidence: float = 1.0
    """Confidence in the estimation method itself."""
    
    context_stability: float = 1.0
    """Stability of context during estimation."""
    
    evidence: Tuple[str, ...] = field(default_factory=tuple)
    """Evidence supporting this confidence assignment."""
    
    provenance: Optional[str] = None
    """Provenance reference for this estimation method."""
    
    @property
    def is_high(self) -> bool:
        """Check if confidence is high (>= 0.7)."""
        return self.value >= 0.7
    
    @property
    def is_medium(self) -> bool:
        """Check if confidence is medium (0.4 to 0.7)."""
        return 0.4 <= self.value < 0.7
    
    @property
    def is_low(self) -> bool:
        """Check if confidence is low (< 0.4)."""
        return self.value < 0.4
    
    @classmethod
    def high(cls, value: float = 1.0) -> ConfidenceEstimate:
        """Create a high confidence estimate."""
        return cls(value=value, basis="sufficient_evidence", evidence_quality=0.9)
    
    @classmethod
    def medium(cls, value: float = 0.5) -> ConfidenceEstimate:
        """Create a medium confidence estimate."""
        return cls(value=value, basis="moderate_evidence", evidence_quality=0.6)
    
    @classmethod
    def low(cls, value: float = 0.2) -> ConfidenceEstimate:
        """Create a low confidence estimate."""
        return cls(value=value, basis="limited_data", evidence_quality=0.3)