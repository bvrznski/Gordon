# Salience Sensory Observation
# ===========================
#
# Canonical implementation of sensory observations (Phase 4.8.3).
#

"""
Sensory observation for the Salience Network.

SENSORY OBSERVATION:
    Represents raw semantic information from sensory inputs without interpretation.
    
CONTENT LAWS:
    SALIENCE-OBSERVATION-LAW-001: Observations represent raw semantic information
    SALIENCE-OBSERVATION-LAW-002: Observations never interpret themselves
    SALIENCE-OBSERVATION-LAW-003: Observations remain immutable
    SALIENCE-OBSERVATION-LAW-004: Every observation possesses explicit ownership
    SALIENCE-OBSERVATION-LAW-005: Observations preserve origin

SEMANTIC HIERARCHY:
    BaseSalienceContent → BaseObservation → SensoryObservation
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import FrozenSet, Tuple

from gordon_system.src.agent.networks.salience.content.observations.base import BaseObservation


@dataclass(frozen=True)
class SensoryObservation(BaseObservation):
    """
    Observation of raw sensory information from external or internal sources.
    
    SENSORY TYPES:
        - visual: Sight-based input
        - auditory: Sound-based input
        - tactile: Touch-based input
        - olfactory: Smell-based input
        - gustatory: Taste-based input
        - proprioceptive: Body position awareness
        - interoceptive: Internal state awareness
    
    SEMANTIC HIERARCHY:
        BaseObservation → SensoryObservation
        
    EXAMPLES:
        - "Visual observation of moving object at position (100, 200)"
        - "Auditory observation of voice pattern with frequency 440Hz"
        - "Proprioceptive observation of arm at 90 degree angle"
    """
    
    sensory_type: str = field(default="visual")
    """Type of sensory input (visual, auditory, tactile, olfactory, gustatory)."""
    
    sensory_channel: str = field(default="")
    """Specific sensory channel identifier."""
    
    intensity: float = field(default=1.0)
    """Intensity level of the sensory signal (0.0 to 1.0)."""
    
    duration_ms: int = field(default=0)
    """Duration of the sensory observation in milliseconds."""
    
    @property
    def is_sensory(self) -> bool:
        """Indicates whether this is a sensory observation."""
        return True
    
    @property
    def canonical_type(self) -> str:
        """Return the canonical type identifier for this sensory observation."""
        return f"salience.sensory.{self.sensory_type}"
    
    def validate_sensory_compliance(self) -> bool:
        """
        Validate that this sensory observation satisfies Salience Network laws.
        
        Returns:
            True if compliance is valid, False otherwise.
        """
        return (
            super().validate_observation_compliance() and
            self._validate_sensory_type()
        )
    
    def _validate_sensory_type(self) -> bool:
        """Validate that sensory type is explicit and recognized."""
        recognized_types = {
            "visual", "auditory", "tactile", "olfactory", 
            "gustatory", "proprioceptive", "interoceptive"
        }
        return self.sensory_type in recognized_types