# Experimental Reasoning - Information Gain
# =========================================

"""
Canonical Information Gain contracts.

Information gain estimates quantify the expected knowledge acquisition from experiments.
"""

from __future__ import annotations

import time
import uuid
from dataclasses import dataclass, field
from typing import Dict, List, Tuple, Optional, Any
from enum import Enum, auto


@dataclass(frozen=True)
class InformationGainEstimate:
    """
    Estimate of information gain from an experiment.
    
    Includes:
        - Expected uncertainty reduction
        - Hypothesis discrimination power
        - Expected evidence value
        - Scientific utility
        - Experimental efficiency
    
    Estimation remains explicit and inspectable.
    """
    
    # Identity
    estimate_id: str                            # Unique identifier
    experiment_identity: str                    # Which experiment?
    
    # Information gain components
    expected_uncertainty_reduction: float = 0.0  # Expected reduction in entropy
    hypothesis_discrimination_power: float = 0.0  # Ability to distinguish hypotheses
    
    # Evidence value
    expected_evidence_value: float = 0.0        # Value of expected evidence
    evidential_strength: str = "weak"            # "weak", "moderate", "strong"
    
    # Scientific utility
    scientific_utility: float = 0.0              # Overall scientific value (0-1)
    knowledge_impact: str = "low"                # Impact on existing knowledge
    
    # Estimation method details
    estimation_method: str = "analytical"        # How was this estimated?
    confidence_in_estimate: float = 0.5          # Confidence in the estimate itself
    
    # Provenance
    created_at_utc: float = field(default_factory=time.time)
    origin_context: str = "unknown"
    
    @property
    def overall_information_gain(self) -> float:
        """Calculate overall information gain (weighted combination)."""
        weights = {
            "uncertainty_reduction": 0.3,
            "discrimination_power": 0.25,
            "evidence_value": 0.25,
            "scientific_utility": 0.2,
        }
        return (
            self.expected_uncertainty_reduction * weights["uncertainty_reduction"] +
            self.hypothesis_discrimination_power * weights["discrimination_power"] +
            self.expected_evidence_value * weights["evidence_value"] +
            self.scientific_utility * weights["scientific_utility"]
        )
    
    @property
    def is_high_quality(self) -> bool:
        """Check if this is a high-quality information estimate."""
        return (
            self.confidence_in_estimate >= 0.7 and
            self.expected_uncertainty_reduction > 0.1 and
            self.hypothesis_discrimination_power > 0.1
        )
    
    @classmethod
    def create(
        cls,
        experiment_identity: str,
        origin_context: str = "unknown",
    ) -> InformationGainEstimate:
        """Create a new information gain estimate."""
        return cls(
            estimate_id=f"info_gain:{uuid.uuid4().hex[:16]}",
            experiment_identity=experiment_identity,
            origin_context=origin_context,
        )


class EstimationMethod(Enum):
    """Methods for estimating information gain."""
    
    ANALYTICAL = "analytical"                   # Analytical calculation (closed-form)
    MONTE_CARLO = "monte_carlo"                # Monte Carlo simulation
    BAYESIAN_ANALYSIS = "bayesian_analysis"     # Bayesian model comparison
    ENTROPY_ESTIMATION = "entropy_estimation"   # Direct entropy estimation
    EMPIRICAL = "empirical"                     # Based on prior empirical data


@dataclass(frozen=True)
class InformationGainCalculation:
    """
    Detailed calculation of information gain for an experiment.
    
    Includes the full mathematical derivation and assumptions.
    """
    
    # Identity
    calc_id: str                                # Unique identifier
    
    # Calculation details
    input_entropy: float = 0.0                  # Entropy before experiment
    output_entropy: float = 0.0                 # Expected entropy after experiment
    information_gain: float = 0.0               # Calculated gain (H(in) - H(out))
    
    # Hypothesis comparison
    hypothesis_posteriors_before: Dict[str, float] = field(default_factory=dict)
    hypothesis_posteriors_after: Dict[str, float] = field(default_factory=dict)
    kl_divergence: float = 0.0                  # KL divergence between posteriors
    
    # Assumptions made
    assumptions: Tuple[str, ...] = ()           # Key assumptions in calculation
    
    @classmethod
    def create(
        cls,
        input_entropy: float = 0.0,
        output_entropy: float = 0.0,
    ) -> InformationGainCalculation:
        """Create a new information gain calculation."""
        return cls(
            calc_id=f"info_calc:{uuid.uuid4().hex[:16]}",
            input_entropy=input_entropy,
            output_entropy=output_entropy,
            information_gain=max(0.0, input_entropy - output_entropy),
        )
    
    @property
    def mutual_information(self) -> float:
        """Calculate mutual information between experiment and outcome."""
        # I(X;Y) = H(Y) - H(Y|X)
        return self.information_gain


__all__ = [
    "InformationGainEstimate",
    "EstimationMethod",
    "InformationGainCalculation",
]