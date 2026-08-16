# Oriented Network Coherence Models - Phase 4.7.10
# ==================================================

"""
Coherence evaluation models for semantic quality assessment.

SEMANTIC ROLE:
    - Describes semantic compatibility between orientation elements
    - Never resolves inconsistencies
    - Never repairs structures

OWNERSHIP CONTRACT:
    - Owns: coherence semantics, relationships, context
    - Never owns: resolution, repair, runtime synchronization

COHERENCE LAWS:
    ORIENTED-COHERENCE-LAW-001 through 006: Coherence semantics and constraints
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, Tuple
from enum import Enum

from gordon_system.src.agent.components.networks.oriented.evaluation.base.models import (
    BaseCoherenceModel,
    EvaluationAuthority,
)


# =============================================================================
# COHERENCE LEVELS (Part 1)
# =============================================================================

class CoherenceLevel(Enum):
    """
    Canonical coherence levels for orientation assessment.
    
    SEMANTIC ROLE:
        - Describes semantic compatibility
        - Never prescribes resolution
        
    COHERENCE LAWS:
        ORIENTED-COHERENCE-LAW-001: Coherence represents semantic compatibility
        ORIENTED-COHERENCE-LAW-002 through 006: Constraints on coherence behavior
    """
    
    HIGH = "high"
    """Strong semantic compatibility between orientation elements"""
    
    MODERATE = "moderate"
    """Acceptable semantic compatibility with some minor issues"""
    
    LOW = "low"
    """Weak semantic compatibility requiring attention"""
    
    BROKEN = "broken"
    """Severe semantic incompatibility present"""
    
    UNKNOWN = "unknown"
    """Insufficient information to determine coherence"""


# =============================================================================
# COHERENCE MODELS (Part 1)
# =============================================================================

@dataclass(frozen=True)
class OrientationCoherence(BaseCoherenceModel):
    """
    Base coherence evaluation for orientation elements.
    
    SEMANTIC ROLE:
        - Describes semantic compatibility between orientation components
        - Never resolves incompatibilities
        - Never repairs structures
        
    OWNERSHIP CONTRACT:
        - Owns: coherence semantics, relationships, context
        - Never owns: resolution, repair, runtime synchronization
        
    COHERENCE LAWS:
        ORIENTED-COHERENCE-LAW-001 through 006: Coherence semantics and constraints
    """
    
    orientation_identity: str = ""
    """Identity of the oriented network element being evaluated"""
    
    coherence_level: CoherenceLevel = CoherenceLevel.UNKNOWN
    
    semantic_compatibility_score: float = 0.0
    """Numerical score representing semantic compatibility (0.0 to 1.0)"""
    
    compatibility_factors: Tuple[str, ...] = field(default_factory=tuple)
    """Factors contributing to coherence assessment"""
    
    @classmethod
    def create(
        cls,
        identity: str,
        orientation_identity: str,
        coherence_level: CoherenceLevel = CoherenceLevel.UNKNOWN,
        semantic_compatibility_score: float = 0.0,
        compatibility_factors: Tuple[str, ...] = tuple(),
    ) -> OrientationCoherence:
        """Create a new orientation coherence evaluation."""
        return cls(
            identity=identity,
            orientation_identity=orientation_identity,
            coherence_level=coherence_level,
            semantic_compatibility_score=semantic_compatibility_score,
            compatibility_factors=compatibility_factors,
        )
    
    def to_dict(self) -> Dict[str, Any]:
        """Serialize coherence evaluation to dictionary."""
        return {
            "identity": self.identity,
            "revision": self.revision,
            "version": self.version,
            "authority": self.authority.value,
            "owner": self.owner,
            "orientation_identity": self.orientation_identity,
            "coherence_level": self.coherence_level.value,
            "semantic_compatibility_score": self.semantic_compatibility_score,
            "compatibility_factors": list(self.compatibility_factors),
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> OrientationCoherence:
        """Create coherence evaluation from dictionary."""
        return cls(
            identity=data.get("identity", ""),
            revision=data.get("revision", 1),
            version=data.get("version", 1),
            authority=EvaluationAuthority(data.get("authority", "oriented_network")),
            owner=data.get("owner", "oriented_network"),
            orientation_identity=data.get("orientation_identity", ""),
            coherence_level=CoherenceLevel(
                data.get("coherence_level", CoherenceLevel.UNKNOWN.value)
            ),
            semantic_compatibility_score=float(
                data.get("semantic_compatibility_score", 0.0)
            ),
            compatibility_factors=tuple(data.get("compatibility_factors", [])),
        )
    
    def validate(self) -> Tuple[bool, Tuple[str, ...]]:
        """Validate coherence evaluation."""
        errors = []
        
        # Validate identity
        if not self.identity:
            errors.append("Identity must be non-empty")
        
        # Validate orientation_identity
        if not self.orientation_identity:
            errors.append("Orientation identity must be non-empty")
        
        # Validate score range
        if not (0.0 <= self.semantic_compatibility_score <= 1.0):
            errors.append(
                f"Semantic compatibility score must be between 0.0 and 1.0, "
                f"got {self.semantic_compatibility_score}"
            )
        
        return len(errors) == 0, tuple(errors)


@dataclass(frozen=True)
class HighCoherence(OrientationCoherence):
    """
    High semantic coherence evaluation.
    
    SEMANTIC ROLE:
        - Represents strong semantic compatibility
        - Indicates well-aligned orientation elements
        
    COHERENCE LAWS:
        ORIENTED-COHERENCE-LAW-001: Coherence represents semantic compatibility
        ORIENTED-COHERENCE-LAW-002 through 006: Constraints on coherence behavior
    """
    
    coherence_level: CoherenceLevel = field(default=CoherenceLevel.HIGH, init=False)
    semantic_compatibility_score: float = field(default=0.85, init=False)


@dataclass(frozen=True)
class ModerateCoherence(OrientationCoherence):
    """
    Moderate semantic coherence evaluation.
    
    SEMANTIC ROLE:
        - Represents acceptable semantic compatibility
        - May have minor alignment issues
        
    COHERENCE LAWS:
        ORIENTED-COHERENCE-LAW-001: Coherence represents semantic compatibility
        ORIENTED-COHERENCE-LAW-002 through 006: Constraints on coherence behavior
    """
    
    coherence_level: CoherenceLevel = field(default=CoherenceLevel.MODERATE, init=False)
    semantic_compatibility_score: float = field(default=0.5, init=False)


@dataclass(frozen=True)
class LowCoherence(OrientationCoherence):
    """
    Low semantic coherence evaluation.
    
    SEMANTIC ROLE:
        - Represents weak semantic compatibility
        - Indicates alignment issues requiring attention
        
    COHERENCE LAWS:
        ORIENTED-COHERENCE-LAW-001: Coherence represents semantic compatibility
        ORIENTED-COHERENCE-LAW-002 through 006: Constraints on coherence behavior
    """
    
    coherence_level: CoherenceLevel = field(default=CoherenceLevel.LOW, init=False)
    semantic_compatibility_score: float = field(default=0.3, init=False)


@dataclass(frozen=True)
class BrokenCoherence(OrientationCoherence):
    """
    Broken semantic coherence evaluation.
    
    SEMANTIC ROLE:
        - Represents severe semantic incompatibility
        - Indicates significant misalignment
        
    COHERENCE LAWS:
        ORIENTED-COHERENCE-LAW-001: Coherence represents semantic compatibility
        ORIENTED-COHERENCE-LAW-002 through 006: Constraints on coherence behavior
    """
    
    coherence_level: CoherenceLevel = field(default=CoherenceLevel.BROKEN, init=False)
    semantic_compatibility_score: float = field(default=0.0, init=False)


@dataclass(frozen=True)
class UnknownCoherence(OrientationCoherence):
    """
    Unknown semantic coherence evaluation.
    
    SEMANTIC ROLE:
        - Represents insufficient information for assessment
        - May indicate missing data or undefined state
        
    COHERENCE LAWS:
        ORIENTED-COHERENCE-LAW-001: Coherence represents semantic compatibility
        ORIENTED-COHERENCE-LAW-002 through 006: Constraints on coherence behavior
    """
    
    coherence_level: CoherenceLevel = field(default=CoherenceLevel.UNKNOWN, init=False)
    semantic_compatibility_score: float = field(default=0.0, init=False)


__all__ = [
    "CoherenceLevel",
    "OrientationCoherence",
    "HighCoherence",
    "ModerateCoherence",
    "LowCoherence",
    "BrokenCoherence",
    "UnknownCoherence",
]