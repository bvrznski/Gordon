# Uncertainty Analysis - Phase 7.7
# =================================

"""
Canonical uncertainty analysis contracts.

Uncertainty is decomposed into epistemic and aleatoric components.
"""

from __future__ import annotations

import time
import uuid
from dataclasses import dataclass, field
from typing import Dict, List, Tuple, Optional, Any


@dataclass(frozen=True)
class EpistemicUncertainty:
    """
    Epistemic ( reducible ) uncertainty due to incomplete knowledge.
    
    This uncertainty can be reduced by gathering more information or evidence.
    """
    
    # Identity
    uncertainty_id: str                     # Unique identifier
    
    # Source identification
    source_type: str = "model_unknown"      # What type of ignorance?
    source_description: str = ""            # Human-readable description
    
    # Magnitude
    magnitude: float = 0.5                  # How much epistemic uncertainty?
    
    # Reducibility
    reducible: bool = True                  # Can this be reduced with more data?
    estimated_reductions: int = 1           # How many info-gathering steps needed?
    
    # Evidence for reduction
    reduction_evidence: Tuple[str, ...] = ()  # What would help reduce it?


@dataclass(frozen=True)
class AleatoricUncertainty:
    """
    Aleatoric ( irreducible ) uncertainty due to inherent randomness.
    
    This uncertainty cannot be reduced by gathering more information.
    It's noise in the system itself.
    """
    
    # Identity
    uncertainty_id: str                     # Unique identifier
    
    # Source identification
    source_type: str = "inherent_noise"     # What type of randomness?
    source_description: str = ""            # Human-readable description
    
    # Magnitude
    magnitude: float = 0.3                  # How much aleatoric uncertainty?
    
    # Irreducibility
    irreducible: bool = True                # Cannot be reduced by more data


@dataclass(frozen=True)
class UncertaintyComponent:
    """
    A single component of overall uncertainty.
    
    Represents one source or aspect of uncertainty in a system.
    """
    
    # Identity
    component_id: str                       # Unique identifier
    
    # Type
    uncertainty_type: str = "epistemic"     # "epistemic" or "aleatoric"
    
    # Magnitude estimates
    lower_bound: float = 0.0                # Minimum possible magnitude
    upper_bound: float = 1.0                # Maximum possible magnitude
    most_likely_value: float = 0.5          # Best estimate
    
    # Source info
    source_variable: str = ""               # Which variable is this about?
    source_description: str = ""            # What causes it?
    
    @property
    def range(self) -> float:
        """Calculate uncertainty range."""
        return self.upper_bound - self.lower_bound


@dataclass(frozen=True)
class UncertaintyAnalysis:
    """
    Complete analysis of uncertainty sources in a probabilistic estimate.
    
    Decomposes total uncertainty into identifiable components.
    """
    
    # Identity
    analysis_id: str                        # Unique identifier
    
    # Variables analyzed
    analyzed_variables: Tuple[str, ...] = ()
    
    # Components (decomposed)
    components: Tuple["UncertaintyComponent", ...] = ()
    
    # Aggregated estimates
    total_uncertainty: float = 0.5          # Overall uncertainty level
    dominant_sources: Tuple[str, ...] = ()  # Top uncertainty sources
    
    # Diagnostics
    epistemic_total: float = 0.0            # Total epistemic component
    aleatoric_total: float = 0.0            # Total aleatoric component
    is_well_understood: bool = False        # Is most epistemic uncertainty resolved?
    
    # Metadata
    analyzed_at_utc: float = field(default_factory=time.time)
    
    @property
    def has_epistemic(self) -> bool:
        """Check if epistemic uncertainty exists."""
        return self.epistemic_total > 0
    
    @classmethod
    def create_empty(cls) -> UncertaintyAnalysis:
        """Create an analysis with no components."""
        return cls(
            analysis_id=f"uncertainty_analysis:{uuid.uuid4().hex[:16]}",
        )


def dataclass_replace(instance: Any, **kwargs: Any) -> Any:
    """Simple dataclass replace helper for frozen instances."""
    return instance.__class__(**{**instance.__dict__, **kwargs})


__all__ = [
    "UncertaintyAnalysis",
    "EpistemicUncertainty",
    "AleatoricUncertainty",
    "UncertaintyComponent",
]