# Causal Mechanism Set - Phase 7.5
# =================================

"""
Canonical Causal Mechanism Set.

Mechanisms describe how changes propagate through systems.
"""

from __future__ import annotations

import time
import uuid
from dataclasses import dataclass, field
from typing import Dict, List, Tuple, Optional, Any, Callable
from enum import Enum, auto


class MechanismKind(Enum):
    """Kinds of causal mechanisms."""
    
    RESOURCE_ALLOCATION = "resource_allocation"         # CPU, memory, bandwidth allocation
    SIGNAL_PROPAGATION = "signal_propagation"           # Signal transmission through systems
    MEMORY_CORRUPTION = "memory_corruption"             # Memory state corruption
    NETWORK_CONGESTION = "network_congestion"           # Network congestion effects
    FEEDBACK_LOOP = "feedback_loop"                     # Feedback-driven dynamics
    STATE_TRANSITION = "state_transition"               # State change mechanisms
    SCHEDULER_DELAY = "scheduler_delay"                 # Scheduler-induced delays
    TIMEOUT_MECHANISM = "timeout_mechanism"             # Timeout-based failure
    QUEUE_PROCESSING = "queue_processing"               # Queue-based processing
    CONCURRENCY_CONFLICT = "concurrency_conflict"       # Concurrency issues


@dataclass(frozen=True)
class CausalMechanism:
    """
    A causal mechanism describes how changes propagate.
    
    Mechanisms remain explicit and inspectable. They do not execute;
    they only describe the rules of propagation.
    """
    
    # Identity
    mechanism_id: str                       # Unique mechanism identifier
    semantic_identity: str                  # Semantic identity (stable across runs)
    
    # Mechanism specification
    name: str                               # Human-readable name
    kind: MechanismKind                     # What type of mechanism?
    
    # Participating entities
    input_entities: Tuple[str, ...]         # Entities that feed into this mechanism
    output_entities: Tuple[str, ...]        # Entities produced by this mechanism
    
    # Causal relations
    causal_relations: Tuple[str, ...]       # Explicit causal relations defined
    
    # Activation conditions
    activation_conditions: Tuple[str, ...] = ()  # Conditions required for activation
    
    # Behavior specification (as documentation strings)
    behavior_description: str = ""      # How does this mechanism work?
    
    # Provenance
    created_at_utc: float = field(default_factory=time.time)
    source_system: str = "unknown"          # Where did this mechanism come from?
    
    @property
    def is_active(self) -> bool:
        """Check if mechanism can be activated."""
        return len(self.activation_conditions) == 0
    
    def can_propagate_to(self, target_entity: str) -> bool:
        """Check if this mechanism can propagate to a target entity."""
        return target_entity in self.output_entities


@dataclass(frozen=True)
class MechanismSet:
    """
    A set of explicit causal mechanisms for reasoning.
    
    Mechanism Sets remain immutable during analysis. They define
    the universe of possible causal relationships.
    """
    
    # Identity
    mechanism_set_id: str                   # Unique mechanism set identifier
    semantic_identity: str                  # Semantic identity (stable across runs)
    
    # Participating mechanisms
    participating_mechanisms: Tuple[CausalMechanism, ...]  # All mechanisms in the set
    
    # Known causal assumptions
    assumptions: Tuple[str, ...] = ()       # Explicit causal assumptions
    
    # Domain constraints
    domain_constraints: Tuple[str, ...] = ()  # Domain-specific constraints
    
    # Provenance
    created_at_utc: float = field(default_factory=time.time)
    source_descriptor_id: Optional[str] = None   # From which causal session?
    
    @property
    def mechanism_count(self) -> int:
        """Number of mechanisms in the set."""
        return len(self.participating_mechanisms)
    
    def get_mechanism_by_id(self, mechanism_id: str) -> Optional[CausalMechanism]:
        """Get a mechanism by its identifier."""
        for m in self.participating_mechanisms:
            if m.mechanism_id == mechanism_id:
                return m
        return None
    
    def find_mechanisms_by_entity(self, entity: str) -> Tuple[CausalMechanism, ...]:
        """Find all mechanisms that involve a particular entity."""
        result = []
        for m in self.participating_mechanisms:
            if (entity in m.input_entities or 
                entity in m.output_entities):
                result.append(m)
        return tuple(result)
    
    def find_mechanisms_by_kind(self, kind: MechanismKind) -> Tuple[CausalMechanism, ...]:
        """Find all mechanisms of a particular kind."""
        return tuple(m for m in self.participating_mechanisms if m.kind == kind)


def make_mechanism_set(
    name: str,
    mechanisms: List[CausalMechanism],
    assumptions: Tuple[str, ...] = (),
    domain_constraints: Tuple[str, ...] = (),
) -> MechanismSet:
    """Create a new mechanism set."""
    return MechanismSet(
        mechanism_set_id=f"mechanism_set:{uuid.uuid4().hex[:16]}",
        semantic_identity=name,
        participating_mechanisms=tuple(mechanisms),
        assumptions=assumptions,
        domain_constraints=domain_constraints,
        created_at_utc=time.time(),
    )


__all__ = [
    "CausalMechanism",
    "MechanismKind",
    "MechanismSet",
]