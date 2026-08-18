# Experimental Reasoning - Control Conditions
# ============================================

"""
Canonical Control contracts.

Controls define experimental baselines for comparison.
"""

from __future__ import annotations

import time
import uuid
from dataclasses import dataclass, field
from typing import Dict, List, Tuple, Optional, Any
from enum import Enum, auto


class ControlType(Enum):
    """Types of control conditions in experiments."""
    
    BASELINE = "baseline"                       # No intervention (control condition)
    POSITIVE_CONTROL = "positive_control"       # Expected to produce known effect
    NEGATIVE_CONTROL = "negative_control"       # Expected to produce no effect
    SHAM_CONTROL = "sham_control"               # Placebo/no-treatment control
    ENVIRONMENTAL_CONTROL = "environmental_control"  # Control for environmental factors


@dataclass(frozen=True)
class BaselineDefinition:
    """
    Definition of a baseline condition for comparison.
    
    Includes:
        - Reference values and their uncertainty
        - Comparison criteria
    """
    
    # Identity
    baseline_id: str                            # Unique identifier
    
    # Baseline characteristics
    reference_value: float = 0.0                # Expected value under control
    reference_uncertainty: float = 0.1          # Uncertainty in reference
    
    # Statistical properties
    distribution_type: str = "normal"           # e.g., "normal", "uniform", "poisson"
    degrees_of_freedom: int = 30                # For t-distribution etc.
    
    # Acceptance criteria for comparison
    equivalence_margin: float = 0.1             # Margin for equivalence testing
    min_effect_size: float = 0.05               # Minimum detectable effect
    
    @classmethod
    def create(
        cls,
        reference_value: float = 0.0,
        reference_uncertainty: float = 0.1,
        distribution_type: str = "normal",
    ) -> BaselineDefinition:
        """Create a new baseline definition."""
        return cls(
            baseline_id=f"baseline:{uuid.uuid4().hex[:8]}",
            reference_value=reference_value,
            reference_uncertainty=reference_uncertainty,
            distribution_type=distribution_type,
        )


@dataclass(frozen=True)
class ControlCondition:
    """
    A control condition in an experiment.
    
    Includes:
        - Type of control
        - Maintained conditions (what stays constant)
        - Comparison strategy
    
    Controls remain explicit and independently inspectable.
    """
    
    # Identity
    control_id: str                             # Unique identifier
    semantic_identity: str                      # Stable identity across runs
    
    # Control type
    control_type: ControlType = ControlType.BASELINE
    
    # Maintained conditions (what stays constant)
    maintained_conditions: Tuple[str, ...] = ()  # e.g., "temperature", "pressure"
    
    # Comparison strategy
    comparison_strategy: str = "difference"     # How to compare with experimental condition
    alpha_level: float = 0.05                   # Significance threshold
    
    # Provenance
    created_at_utc: float = field(default_factory=time.time)
    source_descriptor_id: Optional[str] = None   # If this is a refinement
    origin_context: str = "unknown"              # Where did control condition originate?
    
    @classmethod
    def create(
        cls,
        control_type: ControlType = ControlType.BASELINE,
        maintained_conditions: Optional[Tuple[str, ...]] = None,
        comparison_strategy: str = "difference",
        origin_context: str = "unknown",
    ) -> ControlCondition:
        """Create a new control condition."""
        return cls(
            control_id=f"control:{uuid.uuid4().hex[:16]}",
            semantic_identity=f"{control_type.value}:{origin_context}",
            control_type=control_type,
            maintained_conditions=maintained_conditions or (),
            comparison_strategy=comparison_strategy,
            origin_context=origin_context,
        )


@dataclass(frozen=True)
class ControlManagement:
    """
    Management of control conditions for an experiment.
    
    Evaluates:
        - Baseline condition validity
        - Comparison validity (are controls comparable?)
        - Confounding variables
        - Environment stability
        - Replication strategy
    
    Management remains explicit and inspectable.
    """
    
    # Identity
    management_id: str                          # Unique identifier
    experiment_identity: str                    # Which experiment?
    
    # Participating controls
    participating_controls: Tuple[ControlCondition, ...]
    
    # Baseline definition
    baseline_definition: Optional[BaselineDefinition] = None
    
    # Comparison policy
    comparison_policy: str = "pairwise"         # How to compare conditions
    correction_for_multiple_comparisons: bool = True  # Apply statistical correction?
    
    # Confounding analysis
    identified_confounders: Tuple[str, ...] = ()   # Variables that might affect results
    confounder_mitigations: Dict[str, str] = field(default_factory=dict)  # mitigation strategy
    
    # Provenance
    created_at_utc: float = field(default_factory=time.time)
    origin_context: str = "unknown"
    
    @property
    def control_count(self) -> int:
        """Get the number of control conditions."""
        return len(self.participating_controls)
    
    @classmethod
    def create(
        cls,
        experiment_identity: str,
        controls: List[ControlCondition],
        origin_context: str = "unknown",
    ) -> ControlManagement:
        """Create new control management."""
        return cls(
            management_id=f"control_management:{uuid.uuid4().hex[:16]}",
            experiment_identity=experiment_identity,
            participating_controls=tuple(controls),
            origin_context=origin_context,
        )
    
    @property
    def is_valid(self) -> bool:
        """Check if control setup is valid (has at least one baseline)."""
        return any(c.control_type == ControlType.BASELINE for c in self.participating_controls)


__all__ = [
    "ControlType",
    "BaselineDefinition",
    "ControlCondition",
    "ControlManagement",
]