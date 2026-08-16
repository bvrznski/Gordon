# Multi-Domain Reward Engine - MultiDomainRewardState (Phase 4.10.5)
# ==================================================================

"""
MultiDomainRewardState model for Phase 4.10.5.

This module defines the canonical multi-domain reward state that aggregates
all classified domains, relationships, and profiles into a single semantic
representation without scalar collapse.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Tuple, Optional, Dict

from .domain import RewardDomain, DomainType
from .profile import RewardProfile, DomainProfile
from .relationships import DomainRelationshipGraph, DomainRelationship


@dataclass(frozen=True)
class MultiDomainRewardState:
    """
    The canonical multi-domain reward state.
    
    STATE-LAW-001: Exactly one canonical MultiDomainRewardState exists.
    STATE-LAW-002: The state remains immutable.
    STATE-LAW-003: Every RewardProfile is preserved.
    STATE-LAW-004: Domain interaction graphs are preserved.
    STATE-LAW-005: Hierarchies remain explicit.
    STATE-LAW-006: Temporal partitions remain explicit.
    STATE-LAW-007: Confidence remains domain-specific.
    STATE-LAW-008: Uncertainty remains domain-specific.
    
    PROPERTIES:
        • state_id: Unique identifier for this state
        • reward_profile: The complete reward profile with all domains
        • domain_graph: Domain relationship graph showing interactions
        • domain_hierarchy: Hierarchical mappings between domains
        • temporal_context: Temporal partitions (immediate, short-term, etc.)
    
    NOT RESPONSIBLE FOR:
        • Scalar collapse of domain values
        • Motivation generation  
        • Executive decisions
    """
    
    state_id: str = "multi_domain_reward_state"
    """Unique identifier for this state."""
    
    revision: int = 0
    """Revision number for versioning."""
    
    # Core components (all preserved)
    reward_profile: RewardProfile = field(
        default_factory=lambda: RewardProfile.create_empty()
    )
    """The complete reward profile with all classified domains."""
    
    domain_graph: DomainRelationshipGraph = field(
        default_factory=DomainRelationshipGraph.create_empty
    )
    """Domain relationship graph showing interactions between domains."""
    
    domain_hierarchy: Dict[str, Tuple[str, ...]] = field(default_factory=dict)
    """Hierarchical mappings (domain -> child domains)."""
    
    temporal_context: str = "immediate"
    """Temporal context for this state."""
    
    # Semantic summary
    dominant_domains: Tuple[str, ...] = field(default_factory=tuple)
    """Domains with highest confidence scores."""
    
    conflicting_domains: Tuple[str, ...] = field(default_factory=tuple)
    """Domains that may conflict (low confidence/high uncertainty)."""
    
    supported_domains: Tuple[str, ...] = field(default_factory=tuple)
    """Domains that support other domains."""
    
    # Metadata
    provenance: str = "unknown"
    """Source information for traceability."""
    
    findings: Tuple[str, ...] = field(default_factory=tuple)
    """Key findings from state construction."""
    
    limitations: Tuple[str, ...] = field(default_factory=tuple)
    """Known limitations of this state."""
    
    trace: Tuple[str, ...] = field(default_factory=tuple)
    """Construction trace for provenance."""
    
    @property
    def canonical_identity(self) -> str:
        """Return fully qualified canonical identity."""
        return f"{self.state_id}@v{self.revision}"
    
    @property
    def total_domains(self) -> int:
        """Get count of classified domains."""
        return self.reward_profile.total_domains
    
    @property
    def aggregate_confidence(self) -> float:
        """Calculate average confidence across all domains."""
        return self.reward_profile.aggregate_confidence
    
    @property
    def aggregate_uncertainty(self) -> float:
        """Calculate average uncertainty across all domains."""
        return self.reward_profile.aggregate_uncertainty
    
    @property
    def has_domains(self) -> bool:
        """Check if state contains any domain classifications."""
        return self.total_domains > 0
    
    def get_domain_confidence(self, domain_type: DomainType) -> float:
        """
        Get confidence for a specific domain type.
        
        Args:
            domain_type: The domain type to look up
            
        Returns:
            Confidence value (0.0-1.0), or 0.0 if not found
        """
        profile = self.reward_profile.get_domain_profile(domain_type)
        return profile.confidence if profile else 0.0
    
    def get_domain_uncertainty(self, domain_type: DomainType) -> float:
        """
        Get uncertainty for a specific domain type.
        
        Args:
            domain_type: The domain type to look up
            
        Returns:
            Uncertainty value (0.0-1.0), or 1.0 if not found
        """
        profile = self.reward_profile.get_domain_profile(domain_type)
        return profile.uncertainty if profile else 1.0
    
    def find_conflicts(self) -> Tuple[str, ...]:
        """Find domains that may conflict."""
        return tuple(
            dp.domain_type.value
            for dp in self.reward_profile.find_conflicts()
        )
    
    def to_dict(self) -> dict:
        """Convert state to dictionary representation."""
        return {
            "state_id": self.state_id,
            "revision": self.revision,
            "profile": self.reward_profile.to_dict(),
            "domain_graph": self.domain_graph.to_dict(),
            "domain_hierarchy": self.domain_hierarchy,
            "temporal_context": self.temporal_context,
            "dominant_domains": list(self.dominant_domains),
            "conflicting_domains": list(self.conflicting_domains),
            "supported_domains": list(self.supported_domains),
            "total_domains": self.total_domains,
            "aggregate_confidence": self.aggregate_confidence,
            "aggregate_uncertainty": self.aggregate_uncertainty,
            "provenance": self.provenance,
            "findings": list(self.findings),
            "limitations": list(self.limitations),
        }
    
    @classmethod
    def create_empty(cls, state_id: str = "multi_domain_reward_state") -> MultiDomainRewardState:
        """Create an empty multi-domain reward state."""
        return cls(
            state_id=state_id,
        )
    
    @classmethod
    def from_components(
        cls,
        profile: RewardProfile,
        domain_graph: DomainRelationshipGraph,
        state_id: str = "multi_domain_reward_state",
    ) -> MultiDomainRewardState:
        """
        Create a state from profile and graph components.
        
        Args:
            profile: The reward profile with all classified domains
            domain_graph: The domain relationship graph
            state_id: Unique identifier for this state
            
        Returns:
            New MultiDomainRewardState instance
        """
        # Identify dominant domains (highest confidence)
        dominant = tuple(
            dp.domain_type.value
            for dp in sorted(
                profile.domain_profiles,
                key=lambda p: p.confidence,
                reverse=True
            )[:5]  # Top 5
        )
        
        # Find conflicts
        conflicts = tuple(
            dp.domain_type.value
            for dp in profile.find_conflicts()
        )
        
        # Find supported domains (sources of support relationships)
        supports = set()
        for edge in domain_graph.edges:
            if edge.relationship_type.value == "supports":
                supports.add(edge.source_domain)
        supported = tuple(supports)
        
        return cls(
            state_id=state_id,
            revision=0,
            reward_profile=profile,
            domain_graph=domain_graph,
            temporal_context="immediate",
            dominant_domains=dominant,
            conflicting_domains=conflicts,
            supported_domains=supported,
            findings=("STATE_CONSTRUCTED", "VALIDATION_COMPLETED"),
            trace=("DOMAIN_PROFILES_AGGREGATED", "RELATIONSHIPS_ANALYZED", "GRAPH_BUILT"),
        )
    
    @classmethod
    def from_domains(
        cls,
        domains: Tuple[RewardDomain, ...],
        relationships: Tuple[DomainRelationship, ...] = (),
        state_id: str = "multi_domain_reward_state",
    ) -> MultiDomainRewardState:
        """
        Create a state directly from domain instances.
        
        Args:
            domains: Tuple of reward domains
            relationships: Tuple of domain relationships (optional)
            state_id: Unique identifier for this state
            
        Returns:
            New MultiDomainRewardState instance
        """
        profile = RewardProfile.from_domains(domains, f"{state_id}_profile")
        graph = DomainRelationshipGraph.from_edges(relationships)
        
        return cls.from_components(profile, graph, state_id)


__all__ = [
    "MultiDomainRewardState",
]