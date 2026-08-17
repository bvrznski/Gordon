# Possibility Space - Phase 7.15 Part 2
# =======================================

"""
Canonical Possibility Space.

Possibility Spaces organize candidate hypotheses, candidate mechanisms,
candidate outcomes, constraints, and unknowns.
"""

from __future__ import annotations

import time
import uuid
from dataclasses import dataclass, field
from typing import Dict, List, Tuple, Optional, Any
from enum import Enum, auto


class PossibilityKind(Enum):
    """Kinds of possibilities in possibility space."""
    
    HYPOTHESIS = "hypothesis"               # Candidate explanation
    MECHANISM = "mechanism"                 # Causal mechanism
    OUTCOME = "outcome"                     # Potential result
    CONDITION = "condition"                 # Condition for possibility
    CONSTRAINT = "constraint"               # Boundary condition


@dataclass(frozen=True)
class PossibilityIdentity:
    """
    Immutable identity for a possibility.
    
    Allows tracking possibilities across sessions.
    """
    
    semantic_identity: str                    # Stable identity across runs
    kind: PossibilityKind                     # What kind of possibility?
    
    @classmethod
    def create(cls, semantic_identity: str, kind: PossibilityKind) -> PossibilityIdentity:
        """Create a new possibility identity."""
        return cls(semantic_identity=semantic_identity, kind=kind)


@dataclass(frozen=True)
class Constraint:
    """
    A constraint on possibility space.
    
    Constraints define boundaries for what is considered possible.
    """
    
    # Identity
    constraint_id: str                        # Unique identifier
    
    # Content
    constraint_statement: str                 # What is constrained?
    constraint_type: str                      # e.g., "hard", "soft", "probabilistic"
    
    # Strength
    strength: float = 1.0                     # 0.0 (weak) to 1.0 (hard)
    
    @classmethod
    def create(cls, constraint_statement: str, constraint_type: str = "hard") -> Constraint:
        """Create a new constraint."""
        return cls(
            constraint_id=f"constraint:{uuid.uuid4().hex[:16]}",
            constraint_statement=constraint_statement,
            constraint_type=constraint_type,
        )


@dataclass(frozen=True)
class PossibilitySpaceIdentity:
    """
    Immutable identity for a possibility space.
    
    Allows replay and verification of exploration results.
    """
    
    semantic_identity: str                    # Stable identity across runs
    timestamp_utc: float = field(default_factory=time.time)
    
    @classmethod
    def create(cls, semantic_identity: str) -> PossibilitySpaceIdentity:
        """Create a new possibility space identity."""
        return cls(semantic_identity=semantic_identity)


@dataclass(frozen=True)
class PossibilitySpace:
    """
    Possibility space for hypothetical reasoning.
    
    A possibility space contains:
        - Candidate hypotheses
        - Candidate mechanisms
        - Candidate outcomes
        - Constraints on possibilities
        - Unknown regions requiring exploration
    
    Possibility Spaces remain explicit and inspectable at all times.
    """
    
    # Identity
    possibility_space_id: str                 # Unique identifier
    semantic_identity: str                    # Semantic identity (stable across runs)
    
    # Contents
    participating_hypotheses: Tuple[PossibilityIdentity, ...]  # Candidate hypotheses
    candidate_mechanisms: Tuple[PossibilityIdentity, ...]      # Candidate mechanisms
    candidate_outcomes: Tuple[PossibilityIdentity, ...]        # Potential outcomes
    
    # Constraints
    constraints: Tuple[Constraint, ...]       # Hard and soft constraints
    
    # Unknowns
    unknown_regions: Tuple[str, ...] = ()     # Areas requiring exploration
    
    # Metadata
    created_at_utc: float = field(default_factory=time.time)
    updated_at_utc: float = field(default_factory=time.time)
    
    @property
    def total_candidates(self) -> int:
        """Return total number of candidate possibilities."""
        return len(self.participating_hypotheses) + len(self.candidate_mechanisms) + len(self.candidate_outcomes)
    
    @classmethod
    def create(
        cls,
        semantic_identity: str,
        hypotheses: Optional[List[PossibilityIdentity]] = None,
        mechanisms: Optional[List[PossibilityIdentity]] = None,
        outcomes: Optional[List[PossibilityIdentity]] = None,
        constraints: Optional[List[Constraint]] = None,
        unknown_regions: Optional[List[str]] = None,
    ) -> PossibilitySpace:
        """Create a new possibility space."""
        return cls(
            possibility_space_id=f"possibility_space:{uuid.uuid4().hex[:16]}",
            semantic_identity=semantic_identity,
            participating_hypotheses=tuple(hypotheses or []),
            candidate_mechanisms=tuple(mechanisms or []),
            candidate_outcomes=tuple(outcomes or []),
            constraints=tuple(constraints or []),
            unknown_regions=tuple(unknown_regions or []),
        )
    
    def with_hypothesis(self, hypothesis: PossibilityIdentity) -> "PossibilitySpace":
        """Return a copy with the hypothesis added."""
        new_hypotheses = self.participating_hypotheses + (hypothesis,)
        return dataclass_replace(
            self,
            participating_hypotheses=new_hypotheses,
            updated_at_utc=time.time(),
        )
    
    def without_hypothesis(self, hypothesis: PossibilityIdentity) -> "PossibilitySpace":
        """Return a copy with the hypothesis removed."""
        new_hypotheses = tuple(h for h in self.participating_hypotheses if h != hypothesis)
        return dataclass_replace(
            self,
            participating_hypotheses=new_hypotheses,
            updated_at_utc=time.time(),
        )


@dataclass(frozen=True)
class PossibilitySpaceConstruction:
    """
    Record of possibility space construction.
    
    Tracks the process of building a possibility space from observations
    through to final candidate set.
    """
    
    # Identity
    construction_id: str                      # Unique identifier
    
    # Input
    exploration_strategy: str                 # How was space explored?
    observations: Tuple[str, ...] = ()        # Observations that triggered construction
    
    # Resulting space
    resulting_space: PossibilitySpace         # The constructed possibility space
    
    # Diagnostics
    diagnostics: Dict[str, Any] = field(default_factory=dict)  # Construction metrics
    
    # Metadata
    created_at_utc: float = field(default_factory=time.time)
    
    @classmethod
    def create(
        cls,
        exploration_strategy: str,
        resulting_space: PossibilitySpace,
        observations: Optional[List[str]] = None,
        diagnostics: Optional[Dict[str, Any]] = None,
    ) -> PossibilitySpaceConstruction:
        """Create a new construction record."""
        return cls(
            construction_id=f"construction:{uuid.uuid4().hex[:16]}",
            exploration_strategy=exploration_strategy,
            observations=tuple(observations or []),
            resulting_space=resulting_space,
            diagnostics=diagnostics or {},
        )


def dataclass_replace(instance: Any, **kwargs: Any) -> Any:
    """Simple dataclass replace helper for frozen instances."""
    return instance.__class__(**{**instance.__dict__, **kwargs})


__all__ = [
    "PossibilityKind",
    "PossibilityIdentity",
    "Constraint",
    "PossibilitySpaceIdentity",
    "PossibilitySpace",
    "PossibilitySpaceConstruction",
]