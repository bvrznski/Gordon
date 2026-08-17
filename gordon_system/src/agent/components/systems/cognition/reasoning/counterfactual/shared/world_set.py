# World Set - Phase 7.6
# =====================

"""
World Set contracts for counterfactual reasoning.

A World Set defines:
    - Reference world (the actual world state)
    - Alternative worlds (hypothetical variations)
    - Branching structure (how alternatives diverge from reference)
    - Intervention history
"""

from __future__ import annotations

import time
import uuid
from dataclasses import dataclass, field
from typing import Dict, List, Tuple, Optional, Any
from enum import Enum, auto


@dataclass(frozen=True)
class WorldSet:
    """
    A set of worlds for counterfactual reasoning.
    
    Contains:
        - One immutable Reference World (the actual world state)
        - Multiple Alternative Worlds (hypothetical variations)
        - Branching structure showing how alternatives diverge
        - Provenance tracking all interventions and divergences
    """
    
    # Identity
    world_set_id: str                         # Unique World Set identifier
    
    # Reference world (the immutable baseline)
    reference_world: "ReferenceWorld"         # Immutable reference world state
    
    # Alternative worlds
    alternative_worlds: Tuple["AlternativeWorld", ...] = ()  # Generated alternatives
    
    # Branching structure
    branching_structure: Optional[BranchingStructure] = None
    
    # Provenance
    created_at_utc: float = field(default_factory=time.time)
    provenance: str = "unknown"               # Source of the World Set
    
    @property
    def alternative_count(self) -> int:
        """Number of alternative worlds in this set."""
        return len(self.alternative_worlds)
    
    @classmethod
    def create(
        cls,
        reference_world: "ReferenceWorld",
        provenance: str = "unknown",
    ) -> WorldSet:
        """Create a new World Set with the given reference world."""
        return cls(
            world_set_id=f"worldset:{uuid.uuid4().hex[:16]}",
            reference_world=reference_world,
            alternative_worlds=(),
            branching_structure=None,
            provenance=provenance,
        )
    
    def add_alternative(self, alternative: "AlternativeWorld") -> WorldSet:
        """Return a copy with the given alternative world added."""
        return dataclass_replace(
            self,
            alternative_worlds=self.alternative_worlds + (alternative,),
        )


@dataclass(frozen=True)
class ReferenceWorld:
    """
    The immutable reference world state.
    
    Every counterfactual reasoning session starts from exactly one Reference World.
    The Reference World remains completely unchanged during reasoning - only
    hypothetical alternatives are constructed and compared.
    """
    
    # Identity
    world_id: str                             # Unique world identifier
    
    # World snapshot (the observed state)
    world_snapshot: "WorldSnapshot"           # Snapshot of world at this point
    
    # Causal state (how mechanisms operate in this world)
    causal_state: Optional["CausalState"] = None  # How causality works here
    
    # Temporal position
    temporal_position: Optional[TemporalPosition] = None  # When is this?
    
    # Provenance
    created_at_utc: float = field(default_factory=time.time)
    source_descriptor_id: Optional[str] = None   # Where did this world come from?
    
    @property
    def is_immutable(self) -> bool:
        """Reference worlds are always immutable - a fundamental invariant."""
        return True
    
    @classmethod
    def create(
        cls,
        snapshot: "WorldSnapshot",
        source_descriptor_id: Optional[str] = None,
    ) -> ReferenceWorld:
        """Create a new Reference World from a snapshot."""
        return cls(
            world_id=f"reference_world:{uuid.uuid4().hex[:16]}",
            world_snapshot=snapshot,
            causal_state=None,
            temporal_position=None,
            source_descriptor_id=source_descriptor_id,
        )


@dataclass(frozen=True)
class AlternativeWorld:
    """
    A hypothetical alternative world constructed from interventions on the reference.
    
    Each Alternative World:
        - Has exactly one parent (either Reference or another Alternative)
        - Contains the applied intervention explicitly
        - Shows resulting state after causal propagation
        - Maintains complete provenance traceability
    """
    
    # Identity
    world_id: str                             # Unique alternative world identifier
    
    # Parent relationship
    originating_reference: "ReferenceWorld"   # Direct parent (reference or branch)
    applied_intervention: Optional["CounterfactualIntervention"] = None  # What was changed?
    
    # Resulting state after intervention + propagation
    resulting_state: "WorldSnapshot"          # World state after interventions
    
    # Causal divergence from reference
    divergence_trace: Tuple["WorldDivergence", ...] = ()  # Where did we diverge?
    
    # Provenance
    created_at_utc: float = field(default_factory=time.time)
    branch_depth: int = 1                     # How many interventions from reference?
    
    @property
    def is_direct_alternative(self) -> bool:
        """True if this world branched directly from the reference."""
        return self.branch_depth == 1
    
    @classmethod
    def create(
        cls,
        originating_reference: "ReferenceWorld",
        resulting_state: "WorldSnapshot",
        applied_intervention: Optional["CounterfactualIntervention"] = None,
        branch_depth: int = 1,
    ) -> AlternativeWorld:
        """Create a new Alternative World."""
        return cls(
            world_id=f"alt_world:{uuid.uuid4().hex[:16]}",
            originating_reference=originating_reference,
            applied_intervention=applied_intervention,
            resulting_state=resulting_state,
            divergence_trace=(),
            branch_depth=branch_depth,
        )
    
    def with_divergence(self, divergence: "WorldDivergence") -> AlternativeWorld:
        """Return a copy with the given divergence added to trace."""
        return dataclass_replace(
            self,
            divergence_trace=self.divergence_trace + (divergence,),
        )


@dataclass(frozen=True)
class WorldBranch:
    """
    A branch in the world tree - connects parent to child via intervention.
    
    Branches preserve ancestry and are never implicitly merged.
    """
    
    # Identity
    branch_id: str                            # Unique branch identifier
    
    # Parent relationship
    parent_world: "ReferenceWorld"            # Parent (reference or alternative)
    
    # Intervention that creates this branch
    applied_intervention: "CounterfactualIntervention"
    
    # Child world after intervention + propagation
    resulting_world: "AlternativeWorld"
    
    # Provenance
    created_at_utc: float = field(default_factory=time.time)
    
    @classmethod
    def create(
        cls,
        parent_world: "ReferenceWorld",
        intervention: "CounterfactualIntervention",
        resulting_world: "AlternativeWorld",
    ) -> WorldBranch:
        """Create a new world branch."""
        return cls(
            branch_id=f"branch:{uuid.uuid4().hex[:16]}",
            parent_world=parent_world,
            applied_intervention=intervention,
            resulting_world=resulting_world,
        )


@dataclass(frozen=True)
class WorldSnapshot:
    """
    A snapshot of the world state at a particular point in time.
    
    Snapshots are immutable and serve as the basis for counterfactual comparisons.
    """
    
    # Identity
    snapshot_id: str                          # Unique snapshot identifier
    
    # State content (what we know about the world)
    state_variables: Dict[str, Any] = field(default_factory=dict)  # Key-value state
    
    # World properties
    time_utc: float = field(default_factory=time.time)
    
    # Causal state (how mechanisms work in this snapshot)
    causal_properties: Dict[str, Any] = field(default_factory=dict)
    
    @classmethod
    def create(cls, snapshot_id: Optional[str] = None) -> WorldSnapshot:
        """Create a new world snapshot."""
        return cls(
            snapshot_id=snapshot_id or f"snapshot:{uuid.uuid4().hex[:16]}",
            state_variables={},
            causal_properties={},
        )
    
    def with_variable(self, key: str, value: Any) -> WorldSnapshot:
        """Return a copy with the given variable set."""
        new_vars = dict(self.state_variables)
        new_vars[key] = value
        return dataclass_replace(self, state_variables=new_vars)


@dataclass(frozen=True)
class CausalState:
    """
    The causal mechanisms operating in this world.
    
    Defines how interventions propagate through the world.
    """
    
    # Identity
    causal_state_id: str                      # Unique causal state identifier
    
    # Mechanisms (causal rules, dependencies, etc.)
    mechanisms: Tuple[str, ...] = ()          # Causal mechanism descriptions
    
    # Dependencies (what affects what)
    dependencies: Dict[str, List[str]] = field(default_factory=dict)  # var -> [depends_on...]
    
    @classmethod
    def create(cls) -> CausalState:
        """Create a new causal state."""
        return cls(
            causal_state_id=f"causal_state:{uuid.uuid4().hex[:16]}",
        )
    
    def with_mechanism(self, mechanism: str) -> CausalState:
        """Return a copy with the given mechanism added."""
        return dataclass_replace(
            self,
            mechanisms=self.mechanisms + (mechanism,),
        )


@dataclass(frozen=True)
class TemporalPosition:
    """
    The temporal position of a world state.
    
    Allows reasoning about when interventions would have occurred relative to
    the reference timeline.
    """
    
    # Identity
    temporal_id: str                          # Unique temporal identifier
    
    # Position in time
    timestamp_utc: float = field(default_factory=time.time)
    
    # Temporal scope of this world's validity
    valid_from: Optional[float] = None        #Earliest valid time (if applicable)
    valid_until: Optional[float] = None       #Latest valid time (if applicable)
    
    @classmethod
    def create(cls, timestamp_utc: Optional[float] = None) -> TemporalPosition:
        """Create a new temporal position."""
        return cls(
            temporal_id=f"temporal:{uuid.uuid4().hex[:16]}",
            timestamp_utc=timestamp_utc or time.time(),
        )


def dataclass_replace(instance: Any, **kwargs: Any) -> Any:
    """Simple dataclass replace helper for frozen instances."""
    return instance.__class__(**{**instance.__dict__, **kwargs})


__all__ = [
    "WorldSet",
    "ReferenceWorld",
    "AlternativeWorld",
    "WorldBranch",
    "WorldSnapshot",
    "CausalState",
    "TemporalPosition",
]