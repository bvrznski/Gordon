# Experimental Reasoning - Measurements
# ======================================

"""
Canonical Measurement contracts.

Measurements define observable evidence and how it will be collected.
"""

from __future__ import annotations

import time
import uuid
from dataclasses import dataclass, field
from typing import Dict, List, Tuple, Optional, Any
from enum import Enum, auto


@dataclass(frozen=True)
class ObservedVariable:
    """
    A variable that will be observed in an experiment.
    
    Includes:
        - Variable identity and type
        - Measurement precision and uncertainty
        - Acceptance criteria
    """
    
    # Identity
    variable_id: str                            # Unique identifier
    variable_name: str                          # Human-readable name
    
    # Variable characteristics
    variable_type: str = "continuous"           # e.g., "continuous", "categorical", "boolean"
    unit: Optional[str] = None                  # Physical/unit (e.g., "seconds", "meters")
    
    # Measurement specifications
    expected_range: Tuple[float, float] = (0.0, 1.0)  # Expected value range
    precision: float = 0.01                     # Desired measurement precision
    
    # Uncertainty
    uncertainty_estimate: float = 0.0           # Estimated measurement uncertainty
    confidence_level: float = 0.95              # Confidence level for estimates
    
    # Acceptance criteria
    acceptance_lower: Optional[float] = None   # Lower bound for acceptance
    acceptance_upper: Optional[float] = None   # Upper bound for acceptance
    
    @classmethod
    def create(
        cls,
        variable_name: str,
        variable_type: str = "continuous",
        unit: Optional[str] = None,
        precision: float = 0.01,
        uncertainty_estimate: float = 0.0,
    ) -> ObservedVariable:
        """Create a new observed variable."""
        return cls(
            variable_id=f"variable:{uuid.uuid4().hex[:8]}",
            variable_name=variable_name,
            variable_type=variable_type,
            unit=unit,
            precision=precision,
            uncertainty_estimate=uncertainty_estimate,
        )


class SamplingStrategy(Enum):
    """Strategies for sampling measurements."""
    
    FIXED_INTERVAL = "fixed_interval"           # Sample at fixed time intervals
    EVENT_TRIGGERED = "event_triggered"         # Sample when specific events occur
    ADAPTIVE = "adaptive"                       # Adapt sampling based on observations
    ONE_TIME = "one_time"                       # Single measurement
    CONTINUOUS = "continuous"                   # Continuous monitoring


@dataclass(frozen=True)
class UncertaintyEstimate:
    """
    Estimate of measurement uncertainty.
    
    Includes both statistical and systematic components.
    """
    
    # Statistical uncertainty
    statistical_uncertainty: float = 0.0        # Random noise, sampling error
    
    # Systematic uncertainty
    systematic_uncertainty: float = 0.0         # Bias, calibration error
    
    # Correlation matrix (if applicable)
    correlation_matrix: Dict[Tuple[str, str], float] = field(default_factory=dict)
    
    @property
    def total_uncertainty(self) -> float:
        """Calculate total uncertainty from components."""
        return (
            self.statistical_uncertainty ** 2 +
            self.systematic_uncertainty ** 2
        ) ** 0.5
    
    @classmethod
    def create(
        cls,
        statistical: float = 0.0,
        systematic: float = 0.0,
    ) -> UncertaintyEstimate:
        """Create a new uncertainty estimate."""
        return cls(
            statistical_uncertainty=statistical,
            systematic_uncertainty=systematic,
        )


@dataclass(frozen=True)
class MeasurementPlan:
    """
    A plan for measuring variables in an experiment.
    
    Includes:
        - Variables to be observed
        - Sampling strategy and frequency
        - Expected precision and uncertainty
        - Instrument requirements
    
    Measurement plans remain explicit and independently inspectable.
    """
    
    # Identity
    measurement_id: str                         # Unique identifier
    semantic_identity: str                      # Stable identity across runs
    
    # Variables to observe
    observed_variables: Tuple[ObservedVariable, ...]
    
    # Sampling strategy
    sampling_strategy: SamplingStrategy = SamplingStrategy.FIXED_INTERVAL
    sampling_frequency: float = 1.0             # Samples per second (for fixed interval)
    
    # Expected precision
    expected_precision: Dict[str, float] = field(default_factory=dict)  # variable_id -> precision
    
    # Uncertainty estimates
    uncertainty_estimates: Dict[str, UncertaintyEstimate] = field(default_factory=dict)
    
    # Instrument requirements
    required_instruments: Tuple[str, ...] = ()  # e.g., "sensor_a", "camera_b"
    
    # Provenance
    created_at_utc: float = field(default_factory=time.time)
    source_descriptor_id: Optional[str] = None   # If this is a refinement
    origin_context: str = "unknown"              # Where did measurement plan originate?
    
    @property
    def variable_count(self) -> int:
        """Get the number of observed variables."""
        return len(self.observed_variables)
    
    @classmethod
    def create(
        cls,
        semantic_identity: str,
        observed_variables: List[ObservedVariable],
        sampling_strategy: SamplingStrategy = SamplingStrategy.FIXED_INTERVAL,
        origin_context: str = "unknown",
    ) -> MeasurementPlan:
        """Create a new measurement plan."""
        return cls(
            measurement_id=f"measurement_plan:{uuid.uuid4().hex[:16]}",
            semantic_identity=semantic_identity,
            observed_variables=tuple(observed_variables),
            sampling_strategy=sampling_strategy,
            origin_context=origin_context,
        )


@dataclass(frozen=True)
class MeasurementPlanning:
    """
    The process of planning measurements for an experiment.
    
    Evaluates:
        - Observable variables
        - Measurement precision
        - Sampling frequency
        - Expected uncertainty
        - Instrument selection
    
    Planning remains explicit and inspectable.
    """
    
    # Identity
    planning_id: str                            # Unique identifier
    experiment_identity: str                    # Which experiment is this for?
    
    # Planning results
    selected_variables: Tuple[str, ...]         # Variables to measure
    selected_strategy: SamplingStrategy         # Selected sampling strategy
    
    # Uncertainty analysis
    estimated_uncertainty: float = 0.0          # Overall uncertainty estimate
    confidence_level: float = 0.95              # Confidence level for estimates
    
    # Instrument assignment
    instrument_assignments: Dict[str, str] = field(default_factory=dict)  # variable_id -> instrument
    
    # Justification
    justification: str = ""                     # Why this measurement plan?
    
    # Provenance
    created_at_utc: float = field(default_factory=time.time)
    origin_context: str = "unknown"
    
    @classmethod
    def create(
        cls,
        experiment_identity: str,
        origin_context: str = "unknown",
    ) -> MeasurementPlanning:
        """Create a new measurement planning."""
        return cls(
            planning_id=f"measurement_planning:{uuid.uuid4().hex[:16]}",
            experiment_identity=experiment_identity,
            origin_context=origin_context,
        )
    
    @property
    def is_complete(self) -> bool:
        """Check if all variables have been assigned instruments."""
        return len(self.instrument_assignments) == len(self.selected_variables)


__all__ = [
    "ObservedVariable",
    "SamplingStrategy",
    "UncertaintyEstimate",
    "MeasurementPlan",
    "MeasurementPlanning",
]