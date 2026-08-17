# World Models - Phase 6.7
# ========================

"""
World Models: External environment representations.

World Models represent Gordon's understanding of external reality including:
- Physical world properties and behaviors
- Operating system structures and capabilities
- Hardware constraints and characteristics
- Network topology and availability
- Workspace state and resources
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Tuple, Optional, Any
import time
import uuid


# =============================================================================
# WORLD MODEL - Canonical world representation
# =============================================================================


@dataclass(frozen=True)
class WorldModel:
    """
    Canonical representation of a world model in Gordon's knowledge system.
    
    World Models describe external reality while preserving assumptions and
    their limits.
    
    Fields:
        model_identity:         Unique identifier for this world model
        semantic_identity:      Stable semantic identity across revisions
        scope:                  Domain coverage description
        environment_state:      Current state of the environment
        assumptions:            Explicit assumptions about the environment
        constraints:            Known limitations and boundaries
        provenance:             Origin tracking with timestamps and sources
    """
    
    # Identity fields (required)
    model_identity: str                 # Unique ID for this instance
    
    semantic_identity: str              # Stable identifier across revisions
    
    # Scope definition
    scope: Dict[str, Any] = field(default_factory=dict)  # Domain coverage
    
    # Environment representation
    environment_state: Dict[str, Any] = field(default_factory=dict)  # Current state
    
    # Assumptions (required)
    assumptions: Tuple[str, ...] = field(default_factory=tuple)  # Explicit assumptions
    
    # Constraints (optional but recommended)
    constraints: Tuple[str, ...] = field(default_factory=tuple)  # Known limitations
    
    # Provenance tracking
    provenance: Dict[str, Any] = field(default_factory=dict)
    
    @property
    def is_valid(self) -> bool:
        """Check if model has minimal required data."""
        return (
            len(self.model_identity) > 0 and
            len(self.assumptions) >= 1
        )
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert world model to dictionary for serialization."""
        return {
            "model_identity": self.model_identity,
            "semantic_identity": self.semantic_identity,
            "scope": dict(self.scope),
            "environment_state": dict(self.environment_state),
            "assumptions": list(self.assumptions),
            "constraints": list(self.constraints),
            "provenance": dict(self.provenance),
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "WorldModel":
        """Create world model from dictionary."""
        return cls(
            model_identity=data.get("model_identity", str(uuid.uuid4())),
            semantic_identity=data.get("semantic_identity", ""),
            scope=dict(data.get("scope", {})),
            environment_state=dict(data.get("environment_state", {})),
            assumptions=tuple(data.get("assumptions", [])),
            constraints=tuple(data.get("constraints", [])),
            provenance=dict(data.get("provenance", {})),
        )
    
    @classmethod
    def create(
        cls,
        semantic_identity: str,
        scope: Optional[Dict[str, Any]] = None,
        environment_state: Optional[Dict[str, Any]] = None,
        assumptions: Optional[List[str]] = None,
        constraints: Optional[List[str]] = None,
    ) -> "WorldModel":
        """
        Create a new world model.
        
        Args:
            semantic_identity: Stable identifier across revisions
            scope: Domain coverage description (optional)
            environment_state: Current state representation (optional)
            assumptions: Explicit assumptions about the environment (required)
            constraints: Known limitations (optional)
            
        Returns:
            A new world model
        """
        return cls(
            model_identity=f"world_model:{uuid.uuid4().hex[:16]}",
            semantic_identity=semantic_identity,
            scope=dict(scope or {}),
            environment_state=dict(environment_state or {}),
            assumptions=tuple(assumptions or []),
            constraints=tuple(constraints or []),
            provenance={
                "created_at_utc": time.time(),
                "builder_version": "1.0",
            },
        )


# =============================================================================
# ENVIRONMENT STATE - Environment representation
# =============================================================================


@dataclass(frozen=True)
class EnvironmentState:
    """
    Representation of environment state at a point in time.
    
    Fields:
        timestamp:              When the state was captured (UTC timestamp)
        entities:               Known entities and their properties
        relations:              Relationships between entities
        dynamics:               Dynamic properties (rates, velocities, etc.)
    """
    
    timestamp: float                    # UTC timestamp when captured
    
    entities: Dict[str, Dict[str, Any]] = field(default_factory=dict)  # Entity states
    
    relations: Dict[Tuple[str, str], str] = field(default_factory=dict)  # Entity relations
    
    dynamics: Dict[str, Any] = field(default_factory=dict)  # Dynamic properties


__all__ = [
    "WorldModel",
    "EnvironmentState",
]