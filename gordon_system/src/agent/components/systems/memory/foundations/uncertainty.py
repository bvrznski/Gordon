# Memory Uncertainty - Phase 5.1 Canonical Unknown Measure
# =========================================================

"""
Memory Uncertainty: Explicit unknown dimensions for memory artifacts.

Every Memory Artifact possesses:
    - uncertainty (completely independent from confidence)
    - multiple uncertainty dimensions

Confidence and uncertainty remain independent:
    - High confidence can coexist with high uncertainty
    - Low confidence does NOT imply high uncertainty
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Tuple, Optional
from enum import Enum, auto
import time


# =============================================================================
# UNCERTAINTY KINDS - Types of unknowns
# =============================================================================


class UncertaintyKind(Enum):
    """
    Categories of uncertainty dimensions.
    
    | Kind             | Description                                        |
    |------------------|---------------------------------------------------|
    | EPISTEMIC        | Lack of knowledge (can be reduced)                |
    | ALEATORIC        | Inherent randomness (inherent to the system)      |
    | MODEL            | Model limitations                                 |
    | SOURCE           | Source unreliability                              |
    | TEMPORAL         | Temporal instability (changes over time)          |
    | SCOPE            | Scope uncertainty (boundaries unclear)            |
    | IDENTITY         | Identity ambiguity (what exactly is this?)        |
    | CAUSAL           | Causal ambiguity (why did this happen?)           |
    """
    
    EPISTEMIC = "epistemic"         # Lack of knowledge
    ALEATORIC = "aleatoric"         # Inherent randomness
    MODEL = "model"                 # Model limitations
    SOURCE = "source"               # Source unreliability
    TEMPORAL = "temporal"           # Temporal instability
    SCOPE = "scope"                 # Scope uncertainty
    IDENTITY = "identity"           # Identity ambiguity
    CAUSAL = "causal"               # Causal ambiguity


# =============================================================================
# UNCERTAINTY SCOPES - Context of uncertainty
# =============================================================================


class UncertaintyScope(Enum):
    """
    Scopes for uncertainty measurement.
    
    | Scope          | Description                                    |
    |----------------|------------------------------------------------|
    | CONTENT        | Uncertainty about the content itself           |
    | RELATIONSHIP   | Uncertainty in relationships                   |
    | VALIDITY       | Uncertainty about validity                     |
    | TIMESTAMP      | Uncertainty about timing                       |
    | LOCATION       | Uncertainty about spatial context              |
    """
    
    CONTENT = "content"
    RELATIONSHIP = "relationship"
    VALIDITY = "validity"
    TIMESTAMP = "timestamp"
    LOCATION = "location"


# =============================================================================
# MEMORY UNCERTAINTY - Explicit unknown dimensions
# =============================================================================


@dataclass(frozen=True)
class MemoryUncertainty:
    """
    Uncertainty measures for a memory artifact.
    
    Uncertainty is COMPLETELY independent from confidence. An artifact can be:
        - High confidence, low uncertainty: Well-supported fact
        - High confidence, high uncertainty: Strong belief but incomplete picture
        - Low confidence, low uncertainty: Weak signal we're confident about
        - Low confidence, high uncertainty: Doubtful and incomplete
    
    Fields:
        # Dimensional uncertainty (0.0-1.0 each)
        epistemic:      Knowledge gap
        aleatoric:      Randomness
        model:          Model issues
        source:         Source unreliability
        
        # Scope-specific uncertainty
        scope_by_dimension: Dict of scope -> uncertainty value
        
        # Provenance
        provenance:     How was this uncertainty estimated?
    """
    
    # Dimensional uncertainty (0.0-1.0)
    epistemic: float = 0.0          # Knowledge gap
    aleatoric: float = 0.0          # Inherent randomness
    model: float = 0.0              # Model limitations
    source: float = 0.0             # Source unreliability
    
    # Temporal, scope, identity, causal as additional dimensions
    temporal: float = 0.0           # Temporal instability
    scope: float = 0.0              # Scope boundaries unclear
    identity: float = 0.0           # Identity ambiguity
    causal: float = 0.0             # Causal ambiguity
    
    # Provenance
    provenance: Optional[str] = None
    
    def __post_init__(self):
        """Validate all uncertainty values."""
        for field_name in ["epistemic", "aleatoric", "model", "source", "temporal", "scope", "identity", "causal"]:
            value = getattr(self, field_name)
            if not 0.0 <= value <= 1.0:
                raise ValueError(
                    f"{field_name} must be 0.0-1.0, got {value}"
                )
    
    @property
    def total_uncertainty(self) -> float:
        """Calculate an overall uncertainty measure."""
        return sum([
            self.epistemic,
            self.aleatoric,
            self.model,
            self.source,
            self.temporal,
            self.scope,
            self.identity,
            self.causal,
        ]) / 8.0
    
    @property
    def is_low(self) -> bool:
        """Check if uncertainty is low (< 0.3)."""
        return self.total_uncertainty < 0.3
    
    @property
    def is_high(self) -> bool:
        """Check if uncertainty is high (> 0.7)."""
        return self.total_uncertainty > 0.7
    
    @classmethod
    def low(cls) -> "MemoryUncertainty":
        """Create a low uncertainty state."""
        return cls(epistemic=0.1, aleatoric=0.1, model=0.05, source=0.1)
    
    @classmethod
    def moderate(cls) -> "MemoryUncertainty":
        """Create a moderate uncertainty state."""
        return cls(epistemic=0.4, aleatoric=0.3, model=0.2, source=0.2)
    
    @classmethod
    def high(cls) -> "MemoryUncertainty":
        """Create a high uncertainty state."""
        return cls(epistemic=0.8, aleatoric=0.6, model=0.5, source=0.7)
    
    def with_epistemic(self, value: float) -> "MemoryUncertainty":
        """Return copy with epistemic uncertainty set."""
        return dataclass_replace(self, epistemic=value)
    
    def with_aleatoric(self, value: float) -> "MemoryUncertainty":
        """Return copy with aleatoric uncertainty set."""
        return dataclass_replace(self, aleatoric=value)


# =============================================================================
# UTILITY FUNCTIONS
# =============================================================================


def dataclass_replace(instance: MemoryUncertainty, **kwargs) -> MemoryUncertainty:
    """Replace fields in a frozen dataclass."""
    return MemoryUncertainty(
        epistemic=kwargs.get("epistemic", instance.epistemic),
        aleatoric=kwargs.get("aleatoric", instance.aleatoric),
        model=kwargs.get("model", instance.model),
        source=kwargs.get("source", instance.source),
        temporal=kwargs.get("temporal", instance.temporal),
        scope=kwargs.get("scope", instance.scope),
        identity=kwargs.get("identity", instance.identity),
        causal=kwargs.get("causal", instance.causal),
        provenance=kwargs.get("provenance", instance.provenance),
    )


def normalize_uncertainty(value: float) -> float:
    """Normalize a value to 0.0-1.0 range."""
    return max(0.0, min(1.0, float(value)))


# =============================================================================
# EXPORTS
# =============================================================================

__all__ = [
    "MemoryUncertainty",
    "UncertaintyKind",
    "UncertaintyScope",
    "dataclass_replace",
    "normalize_uncertainty",
]