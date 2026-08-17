# Domain Set - Phase 7.12
# =======================

"""
Canonical Domain Set Contract.

Domain Sets define source and target domains for analogical reasoning.
"""

from __future__ import annotations

import time
import uuid
from dataclasses import dataclass, field
from typing import Dict, List, Tuple, Optional, Any


@dataclass(frozen=True)
class ReasoningDomain:
    """
    A domain in which reasoning occurs.
    
    Domains may originate from:
        - Knowledge stores
        - Memory systems  
        - Simulations
        - Perception systems
        - External models
    
    Domains remain explicit; they are never inferred or fabricated.
    """
    
    # Identity
    domain_id: str                              # Unique identifier
    semantic_identity: str                      # Stable identity across runs
    
    # Participating elements
    participating_entities: Tuple[str, ...] = ()  # What entities exist?
    participating_relations: Tuple[str, ...] = () # What relations hold?
    
    # Abstraction level (0=concrete, 1=abstract)
    abstraction_level: float = 0.5
    
    # Origin
    originating_system: str = "unknown"         # Where did this domain come from?
    origin_context: str = "unknown"             # Context of creation
    
    # Metadata
    created_at_utc: float = field(default_factory=time.time)
    
    # Provenance
    provenance: Dict[str, Any] = field(default_factory=dict)
    
    @property
    def entity_count(self) -> int:
        """Number of participating entities."""
        return len(self.participating_entities)
    
    @property
    def relation_count(self) -> int:
        """Number of participating relations."""
        return len(self.participating_relations)


@dataclass(frozen=True)
class DomainSet:
    """
    A set of domains for analogical reasoning.
    
    Domain Sets define:
        - Source domain (where knowledge comes from)
        - Target domain (where knowledge goes to)
        - Participating domains (all involved in the analogy)
        - Mapping assumptions (what we assume about correspondences)
        - Domain boundaries (what's included/excluded)
    
    Domain Sets remain immutable during reasoning.
    """
    
    # Identity
    domain_set_id: str                          # Unique identifier
    
    # Source and target domains
    source_domain: ReasoningDomain              # Where does knowledge come from?
    target_domain: ReasoningDomain              # Where does knowledge go to?
    
    # All participating domains (source, target, any intermediate)
    participating_domains: Tuple[ReasoningDomain, ...] = ()
    
    # Mapping assumptions
    mapping_assumptions: Tuple[str, ...] = ()   # What do we assume about mappings?
    
    # Domain boundaries
    domain_boundaries: Tuple[str, ...] = ()     # Which domains are included?
    
    # Quality constraints
    min_correspondence_confidence: float = 0.5  # Minimum confidence for valid mapping
    
    # Metadata
    created_at_utc: float = field(default_factory=time.time)
    
    # Provenance
    provenance: Dict[str, Any] = field(default_factory=dict)
    
    @property
    def domain_count(self) -> int:
        """Number of participating domains."""
        return 1 + len(self.participating_domains)
    
    @classmethod
    def create(
        cls,
        source_domain: ReasoningDomain,
        target_domain: ReasoningDomain,
        participating_domains: Optional[List[ReasoningDomain]] = None,
        mapping_assumptions: Optional[List[str]] = None,
        domain_boundaries: Optional[List[str]] = None,
        min_correspondence_confidence: float = 0.5,
    ) -> DomainSet:
        """Create a new domain set."""
        return cls(
            domain_set_id=f"domain_set:{uuid.uuid4().hex[:16]}",
            source_domain=source_domain,
            target_domain=target_domain,
            participating_domains=tuple(participating_domains or []),
            mapping_assumptions=tuple(mapping_assumptions or []),
            domain_boundaries=tuple(domain_boundaries or []),
            min_correspondence_confidence=min_correspondence_confidence,
        )
    
    def add_participant(self, domain: ReasoningDomain) -> DomainSet:
        """Return a new domain set with the participant added."""
        return dataclass_replace(
            self,
            participating_domains=self.participating_domains + (domain,),
        )


def dataclass_replace(instance: Any, **kwargs: Any) -> Any:
    """Simple dataclass replace helper for frozen instances."""
    return instance.__class__(**{**instance.__dict__, **kwargs})


__all__ = [
    "ReasoningDomain",
    "DomainSet",
]