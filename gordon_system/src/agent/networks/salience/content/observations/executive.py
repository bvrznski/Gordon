# Salience Executive Observation
# =============================
#
# Canonical implementation of executive observations (Phase 4.8.3).
#

"""
Executive observation for the Salience Network.

EXECUTIVE OBSERVATION:
    Represents raw semantic information about executive processes without interpretation.
    
SEMANTIC HIERARCHY:
    BaseSalienceContent → BaseObservation → ExecutiveObservation
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import FrozenSet, Tuple

from gordon_system.src.agent.networks.salience.content.observations.base import BaseObservation


@dataclass(frozen=True)
class ExecutiveObservation(BaseObservation):
    """
    Observation of raw executive-related information without interpretation.
    
    EXECUTIVE TYPES:
        - control: Executive control signals
        - switching: Task switching events
        - inhibition: Inhibitory control signals
        - monitoring: Performance monitoring signals
    
    SEMANTIC HIERARCHY:
        BaseObservation → ExecutiveObservation
    """
    
    executive_type: str = field(default="control")
    """Type of executive process (control, switching, inhibition, monitoring)."""
    
    executive_state: str = field(default="active")
    """Current state of the executive process."""
    
    @property
    def is_executive(self) -> bool:
        """Indicates whether this is an executive observation."""
        return True
    
    @property
    def canonical_type(self) -> str:
        """Return the canonical type identifier for this executive observation."""
        return f"salience.executive.{self.executive_type}"
    
    def validate_executive_compliance(self) -> bool:
        """
        Validate that this executive observation satisfies Salience Network laws.
        
        Returns:
            True if compliance is valid, False otherwise.
        """
        return (
            super().validate_observation_compliance() and
            self._validate_executive_type()
        )
    
    def _validate_executive_type(self) -> bool:
        """Validate that executive type is explicit and recognized."""
        recognized_types = {"control", "switching", "inhibition", "monitoring"}
        return self.executive_type in recognized_types