# Multi-Domain Reward Engine - Domain Model (Phase 4.10.5)
# ===========================================================

"""
RewardDomain model for Phase 4.10.5.

This module defines the canonical RewardDomain data structure that represents
a classified reward domain with its supporting evidence, confidence, and provenance.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Tuple, Optional


class DomainType(Enum):
    """
    Canonical reward domain types.
    
    Each domain type represents a distinct semantic category of reward that may
    be simultaneously present in an evaluation. Domains remain independent and
    never collapse into a single scalar value.
    
    DOMAIN-LAW-001: Every RewardDomain references one or more Reward Estimates.
    DOMAIN-LAW-002: Reward domains preserve semantic identity.
    DOMAIN-LAW-003: Reward domains preserve provenance.
    """
    
    # Core reward domains (canonical taxonomy)
    INTRINSIC = "intrinsic"
    """Intrinsic reward: problem solving, understanding, mastery, internal coherence."""
    
    EXTRINSIC = "extrinsic"
    """Extrinsic reward: task completion, resource acquisition, objective achievement."""
    
    SOCIAL = "social"
    """Social reward: cooperation, trust, communication, approval, shared goals."""
    
    EPISTEMIC = "epistemic"
    """Epistemic reward: knowledge acquisition, uncertainty reduction, model improvement."""
    
    COMPETENCE = "competence"
    """Competence reward: skill improvement, execution quality, efficiency, robustness."""
    
    AUTONOMY = "autonomy"
    """Autonomy reward: independent problem solving, self-directed behavior."""
    
    CURIOSITY = "curiosity"
    """Curiosity reward: exploration, novel discovery, interesting observations."""
    
    MISSION = "mission"
    """Mission reward: long-term objective alignment, architectural integrity."""
    
    NORMATIVE = "normative"
    """Normative reward: consistency with internal principles, policies, ethical frameworks."""
    
    # Extended domains (extensible taxonomy)
    SAFETY = "safety"
    """Safety reward: risk avoidance, harm prevention, system preservation."""
    
    RESOURCE = "resource"
    """Resource reward: resource acquisition, efficiency optimization."""
    
    IDENTITY = "identity"
    """Identity reward: self-concept consistency, role fulfillment."""
    
    # Unknown domain for unclassified rewards
    UNKNOWN = "unknown"


@dataclass(frozen=True)
class RewardDomain:
    """
    A classified reward domain with its supporting evidence and metadata.
    
    PROPERTIES:
        • domain_type: The semantic category of this reward
        • supporting_estimates: References to supporting Reward Estimates
        • confidence: Confidence in the classification (0.0-1.0)
        • uncertainty: Uncertainty in the classification (0.0-1.0)  
        • provenance: Source information for traceability
        • revision: Version number for immutability
    
    DOMAIN-LAW-004: Reward domains preserve supporting Reward Estimates.
    DOMAIN-LAW-005: Reward domains preserve revision lineage.
    DOMAIN-LAW-006: Reward domains remain immutable.
    DOMAIN-LAW-007: Domain classification remains deterministic.
    DOMAIN-LAW-008: Reward domains shall never modify Reward Estimates.
    
    NOT RESPONSIBLE FOR:
        • Modifying reward estimates
        • Generating motivation
        • Making decisions
    """
    
    domain_type: DomainType
    """The semantic category of this reward."""
    
    # Supporting evidence (references to RewardEstimates)
    supporting_estimates: Tuple[str, ...] = field(default_factory=tuple)
    """Reference IDs for supporting reward estimates."""
    
    confidence: float = 1.0
    """Confidence in the classification (0.0-1.0)."""
    
    uncertainty: float = 0.0
    """Uncertainty in the classification (0.0-1.0)."""
    
    # Provenance and traceability
    provenance: str = "unknown"
    """Source information for traceability."""
    
    revision: int = 0
    """Version number for immutability tracking."""
    
    @property
    def canonical_identity(self) -> str:
        """Return fully qualified canonical identity."""
        return f"{self.domain_type.value}@v{self.revision}"
    
    @property
    def is_valid(self) -> bool:
        """Check if domain configuration is valid."""
        return (
            0.0 <= self.confidence <= 1.0
            and 0.0 <= self.uncertainty <= 1.0
            and self.confidence + self.uncertainty <= 1.1  # Allow small floating point error
        )
    
    def update_confidence(self, new_confidence: float) -> RewardDomain:
        """Return a copy with updated confidence."""
        if not (0.0 <= new_confidence <= 1.0):
            raise ValueError(f"Confidence must be in [0.0, 1.0], got {new_confidence}")
        
        return RewardDomain(
            domain_type=self.domain_type,
            supporting_estimates=self.supporting_estimates,
            confidence=new_confidence,
            uncertainty=max(0.0, 1.0 - new_confidence),
            provenance=f"{self.provenance}_updated",
            revision=self.revision + 1,
        )
    
    def add_supporting_estimate(self, estimate_id: str) -> RewardDomain:
        """Return a copy with an additional supporting estimate reference."""
        return RewardDomain(
            domain_type=self.domain_type,
            supporting_estimates=self.supporting_estimates + (estimate_id,),
            confidence=self.confidence,
            uncertainty=self.uncertainty,
            provenance=f"{self.provenance}_extended",
            revision=self.revision + 1,
        )
    
    # Factory methods for common domains
    @classmethod
    def create_intrinsic(
        cls,
        estimate_refs: Tuple[str, ...] = (),
        confidence: float = 1.0,
    ) -> RewardDomain:
        """Create an intrinsic reward domain."""
        return cls(
            domain_type=DomainType.INTRINSIC,
            supporting_estimates=estimate_refs,
            confidence=confidence,
            provenance="intrinsic_classifier",
        )
    
    @classmethod
    def create_extrinsic(
        cls,
        estimate_refs: Tuple[str, ...] = (),
        confidence: float = 1.0,
    ) -> RewardDomain:
        """Create an extrinsic reward domain."""
        return cls(
            domain_type=DomainType.EXTRINSIC,
            supporting_estimates=estimate_refs,
            confidence=confidence,
            provenance="extrinsic_classifier",
        )
    
    @classmethod
    def create_social(
        cls,
        estimate_refs: Tuple[str, ...] = (),
        confidence: float = 1.0,
    ) -> RewardDomain:
        """Create a social reward domain."""
        return cls(
            domain_type=DomainType.SOCIAL,
            supporting_estimates=estimate_refs,
            confidence=confidence,
            provenance="social_classifier",
        )
    
    @classmethod
    def create_epistemic(
        cls,
        estimate_refs: Tuple[str, ...] = (),
        confidence: float = 1.0,
    ) -> RewardDomain:
        """Create an epistemic reward domain."""
        return cls(
            domain_type=DomainType.EPISTEMIC,
            supporting_estimates=estimate_refs,
            confidence=confidence,
            provenance="epistemic_classifier",
        )
    
    @classmethod
    def create_competence(
        cls,
        estimate_refs: Tuple[str, ...] = (),
        confidence: float = 1.0,
    ) -> RewardDomain:
        """Create a competence reward domain."""
        return cls(
            domain_type=DomainType.COMPETENCE,
            supporting_estimates=estimate_refs,
            confidence=confidence,
            provenance="competence_classifier",
        )
    
    @classmethod
    def create_autonomy(
        cls,
        estimate_refs: Tuple[str, ...] = (),
        confidence: float = 1.0,
    ) -> RewardDomain:
        """Create an autonomy reward domain."""
        return cls(
            domain_type=DomainType.AUTONOMY,
            supporting_estimates=estimate_refs,
            confidence=confidence,
            provenance="autonomy_classifier",
        )
    
    @classmethod
    def create_curiosity(
        cls,
        estimate_refs: Tuple[str, ...] = (),
        confidence: float = 1.0,
    ) -> RewardDomain:
        """Create a curiosity reward domain."""
        return cls(
            domain_type=DomainType.CURIOSITY,
            supporting_estimates=estimate_refs,
            confidence=confidence,
            provenance="curiosity_classifier",
        )
    
    @classmethod
    def create_mission(
        cls,
        estimate_refs: Tuple[str, ...] = (),
        confidence: float = 1.0,
    ) -> RewardDomain:
        """Create a mission reward domain."""
        return cls(
            domain_type=DomainType.MISSION,
            supporting_estimates=estimate_refs,
            confidence=confidence,
            provenance="mission_classifier",
        )
    
    @classmethod
    def create_normative(
        cls,
        estimate_refs: Tuple[str, ...] = (),
        confidence: float = 1.0,
    ) -> RewardDomain:
        """Create a normative reward domain."""
        return cls(
            domain_type=DomainType.NORMATIVE,
            supporting_estimates=estimate_refs,
            confidence=confidence,
            provenance="normative_classifier",
        )
    
    @classmethod
    def create_unknown(
        cls,
        estimate_refs: Tuple[str, ...] = (),
        confidence: float = 0.5,
    ) -> RewardDomain:
        """Create an unknown reward domain (for unclassified rewards)."""
        return cls(
            domain_type=DomainType.UNKNOWN,
            supporting_estimates=estimate_refs,
            confidence=confidence,
            provenance="unknown_classifier",
        )
    
    def to_dict(self) -> dict:
        """Convert domain to dictionary representation."""
        return {
            "domain_id": self.canonical_identity,
            "domain_type": self.domain_type.value,
            "supporting_estimates": list(self.supporting_estimates),
            "confidence": self.confidence,
            "uncertainty": self.uncertainty,
            "provenance": self.provenance,
            "revision": self.revision,
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> RewardDomain:
        """Create domain from dictionary representation."""
        domain_type = DomainType(data.get("domain_type", "unknown"))
        
        return cls(
            domain_type=domain_type,
            supporting_estimates=tuple(data.get("supporting_estimates", ())),
            confidence=float(data.get("confidence", 1.0)),
            uncertainty=float(data.get("uncertainty", 0.0)),
            provenance=data.get("provenance", "unknown"),
            revision=int(data.get("revision", 0)),
        )


__all__ = [
    "RewardDomain",
    "DomainType",
]