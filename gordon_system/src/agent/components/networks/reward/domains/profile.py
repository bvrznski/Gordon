# Multi-Domain Reward Engine - Profile System (Phase 4.10.5)
# ============================================================

"""
RewardProfile and DomainProfile models for Phase 4.10.5.

This module defines the canonical reward profile system that aggregates classified
domains into a comprehensive semantic representation.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Tuple, Optional, Dict

from .domain import RewardDomain, DomainType


@dataclass(frozen=True)
class DomainProfile:
    """
    Profile of a single reward domain classification.
    
    PROFILE-LAW-001: Exactly one RewardProfile exists for every evaluation request.
    PROFILE-LAW-002: RewardProfiles remain immutable.
    PROFILE-LAW-003: RewardProfiles preserve every classified domain.
    PROFILE-LAW-004: RewardProfiles preserve domain confidence.
    PROFILE-LAW-005: RewardProfiles preserve domain uncertainty.
    
    PROPERTIES:
        • domain_type: The semantic category of the domain
        • confidence: Overall confidence in this domain's classification
        • uncertainty: Overall uncertainty in this domain's classification
        • supporting_estimates: List of estimate IDs that support this domain
    
    NOT RESPONSIBLE FOR:
        • Modifying reward estimates
        • Generating motivation
    """
    
    domain_type: DomainType
    """The semantic category of the domain."""
    
    confidence: float = 1.0
    """Overall confidence in classification (0.0-1.0)."""
    
    uncertainty: float = 0.0
    """Overall uncertainty in classification (0.0-1.0)."""
    
    supporting_estimates: Tuple[str, ...] = field(default_factory=tuple)
    """List of estimate IDs supporting this domain."""
    
    @property
    def canonical_identity(self) -> str:
        """Return fully qualified canonical identity."""
        return f"profile_{self.domain_type.value}"
    
    def to_dict(self) -> dict:
        """Convert profile to dictionary representation."""
        return {
            "domain_type": self.domain_type.value,
            "confidence": self.confidence,
            "uncertainty": self.uncertainty,
            "supporting_estimates": list(self.supporting_estimates),
        }
    
    @classmethod
    def from_domain(cls, domain: RewardDomain) -> DomainProfile:
        """Create a profile from a domain."""
        return cls(
            domain_type=domain.domain_type,
            confidence=domain.confidence,
            uncertainty=domain.uncertainty,
            supporting_estimates=domain.supporting_estimates,
        )


@dataclass(frozen=True)
class RewardProfile:
    """
    A complete reward profile aggregating all classified domains.
    
    PROFILE-LAW-006: RewardProfiles preserve hierarchy.
    PROFILE-LAW-007: RewardProfiles preserve provenance.
    PROFILE-LAW-008: RewardProfiles shall never collapse domains into one scalar.
    
    PROPERTIES:
        • domain_profiles: Tuple of all DomainProfile instances
        • total_domains: Total count of classified domains
        • aggregate_confidence: Average confidence across all domains
        • aggregate_uncertainty: Average uncertainty across all domains
    
    NOT RESPONSIBLE FOR:
        • Modifying reward estimates
        • Generating motivation
        • Making decisions
    """
    
    profile_id: str = "reward_profile"
    """Unique identifier for this profile."""
    
    revision: int = 0
    """Revision number for versioning."""
    
    domain_profiles: Tuple[DomainProfile, ...] = field(default_factory=tuple)
    """Tuple of all domain profiles."""
    
    provenance: str = "unknown"
    """Source information for traceability."""
    
    findings: Tuple[str, ...] = field(default_factory=tuple)
    """Key findings from profile construction."""
    
    trace: Tuple[str, ...] = field(default_factory=tuple)
    """Construction trace for provenance."""
    
    limitations: Tuple[str, ...] = field(default_factory=tuple)
    """Known limitations of this profile."""
    
    @property
    def canonical_identity(self) -> str:
        """Return fully qualified canonical identity."""
        return f"{self.profile_id}@v{self.revision}"
    
    @property
    def total_domains(self) -> int:
        """Get count of classified domains."""
        return len(self.domain_profiles)
    
    @property
    def domain_types(self) -> Tuple[DomainType, ...]:
        """Get all domain types in this profile."""
        return tuple(dp.domain_type for dp in self.domain_profiles)
    
    @property
    def aggregate_confidence(self) -> float:
        """Calculate average confidence across domains."""
        if not self.domain_profiles:
            return 0.0
        total = sum(dp.confidence for dp in self.domain_profiles)
        return total / len(self.domain_profiles)
    
    @property
    def aggregate_uncertainty(self) -> float:
        """Calculate average uncertainty across domains."""
        if not self.domain_profiles:
            return 1.0
        total = sum(dp.uncertainty for dp in self.domain_profiles)
        return total / len(self.domain_profiles)
    
    @property
    def has_domains(self) -> bool:
        """Check if profile contains any domain classifications."""
        return self.total_domains > 0
    
    def get_domain_profile(self, domain_type: DomainType) -> Optional[DomainProfile]:
        """
        Get the domain profile for a specific domain type.
        
        Args:
            domain_type: The domain type to look up
            
        Returns:
            DomainProfile if found, None otherwise
        """
        for dp in self.domain_profiles:
            if dp.domain_type == domain_type:
                return dp
        return None
    
    def find_conflicts(self) -> Tuple[DomainProfile, ...]:
        """Find domains that may conflict (low confidence/high uncertainty)."""
        return tuple(
            dp for dp in self.domain_profiles
            if dp.confidence < 0.5 or dp.uncertainty > 0.5
        )
    
    def to_dict(self) -> dict:
        """Convert profile to dictionary representation."""
        return {
            "profile_id": self.profile_id,
            "revision": self.revision,
            "domain_count": self.total_domains,
            "aggregate_confidence": self.aggregate_confidence,
            "aggregate_uncertainty": self.aggregate_uncertainty,
            "domain_profiles": [dp.to_dict() for dp in self.domain_profiles],
            "provenance": self.provenance,
            "findings": list(self.findings),
            "limitations": list(self.limitations),
        }
    
    @classmethod
    def create_empty(cls, profile_id: str = "reward_profile") -> RewardProfile:
        """Create an empty reward profile."""
        return cls(
            profile_id=profile_id,
        )
    
    @classmethod
    def from_domain_profiles(
        cls,
        domain_profiles: Tuple[DomainProfile, ...],
        profile_id: str = "reward_profile",
    ) -> RewardProfile:
        """
        Create a profile from domain profiles.
        
        Args:
            domain_profiles: Tuple of domain profiles to include
            profile_id: Unique identifier for this profile
            
        Returns:
            New RewardProfile instance
        """
        return cls(
            profile_id=profile_id,
            revision=0,
            domain_profiles=domain_profiles,
            findings=("PROFILE_CREATED",),
            trace=("DOMAIN_PROFILES_AGGREGATED", "VALIDATION_COMPLETED"),
        )
    
    @classmethod
    def from_domains(
        cls,
        domains: Tuple[RewardDomain, ...],
        profile_id: str = "reward_profile",
    ) -> RewardProfile:
        """
        Create a profile from domain instances.
        
        Args:
            domains: Tuple of reward domains to include
            profile_id: Unique identifier for this profile
            
        Returns:
            New RewardProfile instance
        """
        profiles = tuple(DomainProfile.from_domain(d) for d in domains)
        return cls.from_domain_profiles(profiles, profile_id)


__all__ = [
    "DomainProfile",
    "RewardProfile",
]