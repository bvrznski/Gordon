# Salience Environmental Observation
# ==================================
#
# Canonical implementation of environmental observations (Phase 4.8.3).
#

"""
Environmental observation for the Salience Network.

ENVIRONMENTAL OBSERVATION:
    Represents raw semantic information about the external environment without interpretation.
    
SEMANTIC HIERARCHY:
    BaseSalienceContent → BaseObservation → EnvironmentalObservation
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import FrozenSet, Tuple

from gordon_system.src.agent.networks.salience.content.observations.base import BaseObservation


@dataclass(frozen=True)
class EnvironmentalObservation(BaseObservation):
    """
    Observation of raw environmental information without interpretation.
    
    ENVIRONMENTAL TYPES:
        - spatial: Physical space and position
        - temporal: Time-based phenomena
        - physical: Physical properties and states
        - chemical: Chemical composition and reactions
        - biological: Living system observations
        - social: Social interaction observations
    
    SEMANTIC HIERARCHY:
        BaseObservation → EnvironmentalObservation
    """
    
    environmental_type: str = field(default="spatial")
    """Type of environmental observation (spatial, temporal, physical, chemical, etc.)."""
    
    location: Tuple[float, float, float] = field(default=(0.0, 0.0, 0.0))
    """3D spatial coordinates of the observation."""
    
    timestamp_offset_ms: int = field(default=0)
    """Time offset from reference point in milliseconds."""
    
    @property
    def is_environmental(self) -> bool:
        """Indicates whether this is an environmental observation."""
        return True
    
    @property
    def canonical_type(self) -> str:
        """Return the canonical type identifier for this environmental observation."""
        return f"salience.environmental.{self.environmental_type}"
    
    def validate_environmental_compliance(self) -> bool:
        """
        Validate that this environmental observation satisfies Salience Network laws.
        
        Returns:
            True if compliance is valid, False otherwise.
        """
        return (
            super().validate_observation_compliance() and
            self._validate_environmental_type()
        )
    
    def _validate_environmental_type(self) -> bool:
        """Validate that environmental type is explicit and recognized."""
        recognized_types = {
            "spatial", "temporal", "physical", "chemical", 
            "biological", "social"
        }
        return self.environmental_type in recognized_types