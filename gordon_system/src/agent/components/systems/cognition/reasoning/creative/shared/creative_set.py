# Creative Set Contract - Phase 7.33
# ==================================

"""
Canonical Creative Set.

A creative set defines the knowledge, constraints, and domains available for
creative reasoning during a session.
"""

from __future__ import annotations

import time
import uuid
from dataclasses import dataclass, field
from typing import Dict, List, Tuple, Optional, Any
from enum import Enum, auto


@dataclass(frozen=True)
class CreativeSet:
    """
    Defines the creative space for a reasoning session.
    
    A creative set includes:
        - Available knowledge domains
        - Exploration scope boundaries
        - Creative constraints (novelty thresholds, etc.)
        - Provenance tracking
    
    Creative sets remain immutable during reasoning to ensure deterministic
    creative outcomes.
    """
    
    # Identity
    set_id: str                             # Unique set identifier
    semantic_identity: str                  # Semantic identity
    
    # Participating domains (where knowledge comes from)
    participating_domains: List[str] = field(default_factory=list)
    
    # Exploration scope
    exploration_scope: str = "general"      # e.g., "architecture", "design", "strategy"
    
    # Creative constraints
    novelty_minimum: float = 0.3            # Minimum novelty required (0-1)
    usefulness_minimum: float = 0.3         # Minimum usefulness required (0-1)
    feasibility_minimum: float = 0.2        # Minimum feasibility threshold (0-1)
    
    # Constraints on exploration
    max_alternatives: int = 10              # Maximum alternatives to explore
    max_syntheses: int = 5                  # Maximum concept syntheses per session
    
    # Metadata
    created_at_utc: float = field(default_factory=time.time)
    
    @property
    def domain_count(self) -> int:
        """Return number of participating domains."""
        return len(self.participating_domains)
    
    @property
    def is_constrained(self) -> bool:
        """Check if creative set has meaningful constraints."""
        return (
            self.novelty_minimum > 0.0 or
            self.usefulness_minimum > 0.0 or
            self.feasibility_minimum > 0.0 or
            self.max_alternatives < float('inf') or
            self.max_syntheses < float('inf')
        )
    
    @classmethod
    def create(
        cls,
        semantic_identity: str,
        participating_domains: Optional[List[str]] = None,
        exploration_scope: str = "general",
        novelty_minimum: float = 0.3,
        usefulness_minimum: float = 0.3,
        feasibility_minimum: float = 0.2,
        max_alternatives: int = 10,
        max_syntheses: int = 5,
    ) -> CreativeSet:
        """Create a new creative set."""
        return cls(
            set_id=f"creative_set:{uuid.uuid4().hex[:16]}",
            semantic_identity=semantic_identity,
            participating_domains=participating_domains or [],
            exploration_scope=exploration_scope,
            novelty_minimum=novelty_minimum,
            usefulness_minimum=usefulness_minimum,
            feasibility_minimum=feasibility_minimum,
            max_alternatives=max_alternatives,
            max_syntheses=max_syntheses,
            created_at_utc=time.time(),
        )
    
    def with_novelty_threshold(self, threshold: float) -> CreativeSet:
        """Return a copy with updated novelty minimum."""
        return dataclass_replace(
            self,
            novelty_minimum=max(0.0, min(1.0, threshold)),
        )
    
    def with_usefulness_threshold(self, threshold: float) -> CreativeSet:
        """Return a copy with updated usefulness minimum."""
        return dataclass_replace(
            self,
            usefulness_minimum=max(0.0, min(1.0, threshold)),
        )
    
    def with_domain(self, domain: str) -> CreativeSet:
        """Return a copy with an additional domain."""
        new_domains = list(self.participating_domains)
        if domain not in new_domains:
            new_domains.append(domain)
        return dataclass_replace(
            self,
            participating_domains=new_domains,
        )
    
    def without_domain(self, domain: str) -> CreativeSet:
        """Return a copy with a domain removed."""
        new_domains = [d for d in self.participating_domains if d != domain]
        return dataclass_replace(
            self,
            participating_domains=new_domains,
        )


def dataclass_replace(instance: Any, **kwargs: Any) -> Any:
    """Simple dataclass replace helper for frozen instances."""
    # For Python 3.12+, use dataclasses.replace
    # This is a simple implementation for compatibility
    return instance.__class__(**{**instance.__dict__, **kwargs})


__all__ = [
    "CreativeSet",
]