# World-Model Reasoning Dynamics - Phase 7.44
# =================================

"""
Canonical World Dynamics Management.

World dynamics track state transitions, motion, and causal interactions in the world.
"""

from __future__ import annotations

import time
import uuid
from dataclasses import dataclass, field
from typing import Dict, List, Tuple, Optional, Any
from enum import Enum, auto


class DynamicsKind(Enum):
    """Types of world dynamics."""
    
    MOTION = "motion"                   # Object movement and kinematics
    INTERACTION = "interaction"         # Physical interactions between entities
    CAUSAL_TRANSITION = "causal_transition"  # Cause-effect transitions
    ENVIRONMENT_EVOLUTION = "environment_evolution"  # Environmental changes
    ENTITY_LIFECYCLE = "entity_lifecycle"  # Birth, transformation, death of entities


class DynamicsState(Enum):
    """Dynamics session states."""
    
    EMERGING = "emerging"
    ACTIVE = "active"
    SETTLING = "settling"
    STABLE = "stable"


@dataclass(frozen=True)
class StateTransition:
    """
    A state transition from one world state to another.
    """
    
    transition_id: str                  # Unique identifier
    timestamp_utc: float                # When transition occurred
    
    # From/to states
    from_state_hash: str                # Hash of previous state (for tracking)
    to_state_hash: str                  # Hash of new state
    
    # Transition details
    kind: DynamicsKind = DynamicsKind.MOTION
    triggered_by: Optional[str] = None  # What caused this transition?
    
    @classmethod
    def create(
        cls,
        from_state_hash: str,
        to_state_hash: str,
        timestamp_utc: Optional[float] = None,
        kind: DynamicsKind = DynamicsKind.MOTION,
        triggered_by: Optional[str] = None,
    ) -> StateTransition:
        """Create a new state transition."""
        return cls(
            transition_id=f"transition:{uuid.uuid4().hex[:16]}",
            timestamp_utc=timestamp_utc or time.time(),
            from_state_hash=from_state_hash,
            to_state_hash=to_state_hash,
            kind=kind,
            triggered_by=triggered_by,
        )


@dataclass(frozen=True)
class MotionTrack:
    """
    Track motion of an entity over time.
    """
    
    track_id: str                       # Unique identifier
    entity_id: str                      # Entity being tracked
    
    # Position history (time, position_3d pairs)
    position_history: List[Tuple[float, Tuple[float, float, float]]] = field(default_factory=list)
    
    # Velocity and acceleration
    instantaneous_velocity: Optional[Tuple[float, float, float]] = None
    instantaneous_acceleration: Optional[Tuple[float, float, float]] = None
    
    @classmethod
    def create(cls, entity_id: str) -> MotionTrack:
        """Create a new motion track."""
        return cls(
            track_id=f"motion_track:{uuid.uuid4().hex[:16]}",
            entity_id=entity_id,
        )
    
    def add_position(self, timestamp_utc: float, position_3d: Tuple[float, float, float]) -> MotionTrack:
        """Add a position sample to the history."""
        new_history = self.position_history + [(timestamp_utc, position_3d)]
        return dataclass_replace(self, position_history=new_history)


@dataclass(frozen=True)
class CausalTransition:
    """
    A causal transition from one state to another.
    
    Includes explicit causal structure.
    """
    
    transition_id: str                  # Unique identifier
    timestamp_utc: float                # When transition occurred
    
    # Causal structure
    cause_state_hash: str               # Hash of cause state
    effect_state_hash: str              # Hash of effect state
    
    # Causal mechanism (explicit)
    causal_mechanism: Dict[str, Any]    # Description of how cause led to effect
    confidence: float = 1.0             # Confidence in the causal relationship
    
    @classmethod
    def create(
        cls,
        cause_state_hash: str,
        effect_state_hash: str,
        timestamp_utc: Optional[float] = None,
        causal_mechanism: Optional[Dict[str, Any]] = None,
        confidence: float = 1.0,
    ) -> CausalTransition:
        """Create a new causal transition."""
        return cls(
            transition_id=f"causal_transition:{uuid.uuid4().hex[:16]}",
            timestamp_utc=timestamp_utc or time.time(),
            cause_state_hash=cause_state_hash,
            effect_state_hash=effect_state_hash,
            causal_mechanism=causal_mechanism or {},
            confidence=confidence,
        )


@dataclass(frozen=True)
class WorldDynamics:
    """
    World dynamics analysis result.
    
    A WorldDynamics contains:
        - Dynamics identity
        - Dynamic model (state transitions, motion, interactions)
        - Causal transitions
        - Confidence estimates
        - Provenance tracking
    """
    
    # Identity
    dynamics_id: str                    # Unique dynamics identifier
    
    # Model
    dynamic_model: Dict[str, Any]       # Complete dynamic model representation
    
    # History of transitions
    transition_history: List[StateTransition]
    
    # Causal analysis
    causal_transitions: List[CausalTransition]
    
    # Motion tracking (if applicable)
    motion_tracks: List[MotionTrack] = field(default_factory=list)
    
    # Metadata
    dynamics_state: DynamicsState = DynamicsState.STABLE
    world_revision: int = 1
    
    # Confidence and provenance
    confidence: float = 1.0
    provenance: Optional[str] = None
    
    @classmethod
    def create(
        cls,
        provenance: Optional[str] = None,
        world_revision: int = 1,
    ) -> WorldDynamics:
        """Create a new world dynamics analysis."""
        return cls(
            dynamics_id=f"dynamics:{uuid.uuid4().hex[:16]}",
            dynamic_model={},
            transition_history=[],
            causal_transitions=[],
            confidence=1.0,
            provenance=provenance,
            world_revision=world_revision,
        )
    
    def add_transition(self, transition: StateTransition) -> WorldDynamics:
        """Add a state transition to history."""
        new_history = self.transition_history + [transition]
        return dataclass_replace(
            self,
            transition_history=new_history,
            confidence=self.confidence * 0.95,
        )
    
    def add_causal_transition(self, causal: CausalTransition) -> WorldDynamics:
        """Add a causal transition."""
        new_causal = self.causal_transitions + [causal]
        return dataclass_replace(
            self,
            causal_transitions=new_causal,
        )


@dataclass(frozen=True)
class WorldDynamicsManagement:
    """
    World dynamics management contract.
    
    A world dynamics management result contains:
        - Dynamics identity
        - Dynamics model (complete representation)
        - Transition history
        - Confidence estimates
        - Provenance tracking
    """
    
    # Identity
    management_id: str                  # Unique management identifier
    
    # Model
    dynamics_model: Dict[str, Any]      # Complete dynamics model
    
    # History and analysis
    transition_history: List[StateTransition]
    causal_transitions: List[CausalTransition]
    
    # Metadata
    confidence: float = 1.0
    provenance: Optional[str] = None
    world_revision: int = 1
    
    @classmethod
    def create(
        cls,
        provenance: Optional[str] = None,
        world_revision: int = 1,
    ) -> WorldDynamicsManagement:
        """Create a new world dynamics management."""
        return cls(
            management_id=f"dynamics_management:{uuid.uuid4().hex[:16]}",
            dynamics_model={},
            transition_history=[],
            causal_transitions=[],
            confidence=1.0,
            provenance=provenance,
            world_revision=world_revision,
        )
    
    def with_dynamics_model(self, model: Dict[str, Any]) -> WorldDynamicsManagement:
        """Update management result with full dynamics model."""
        return dataclass_replace(
            self,
            dynamics_model=model,
        )


# Helper function for dataclass replacement
def dataclass_replace(instance: Any, **kwargs: Any) -> Any:
    """Simple dataclass replace helper for frozen instances."""
    return instance.__class__(**{**instance.__dict__, **kwargs})


__all__ = [
    "DynamicsKind",
    "DynamicsState",
    "StateTransition",
    "MotionTrack",
    "CausalTransition",
    "WorldDynamics",
    "WorldDynamicsManagement",
]