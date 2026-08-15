# Executive Uncertainty Demand Types
# ===================================

"""
Types for assessing uncertainty demand.

Uncertainty demand may be contributed to executive demand without being
a conflict itself.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Tuple


@dataclass(frozen=True)
class ExecutiveUncertaintyDemand:
    """
    Assessment of uncertainty-driven demand for executive control.
    
    Uncertainty demand must remain distinct from conflict severity.
    """
    
    contributor_class: str = "unknown"
    confidence_class: str = "unknown"
    context_incompleteness_class: str = "unknown"
    model_uncertainty_class: str = "unknown"
    prediction_uncertainty_class: str = "unknown"
    authority_ambiguity_class: str = "unknown"
    
    recommendations: Tuple[str, ...] = ()


__all__: Tuple[str, ...] = ("ExecutiveUncertaintyDemand",)