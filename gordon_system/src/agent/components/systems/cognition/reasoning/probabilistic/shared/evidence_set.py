# Probability Evidence Set - Phase 7.7
# =====================================

"""
Canonical Probability Evidence Set Contract.

Evidence Sets define available evidence for probabilistic reasoning with:
- Source reliability estimates
- Confidence estimates
- Dependencies between evidence sources
"""

from __future__ import annotations

import time
import uuid
from dataclasses import dataclass, field
from typing import Dict, List, Tuple, Optional, Any
from enum import Enum


class EvidenceQuality(Enum):
    """Evidence quality levels."""
    
    INVALID = "invalid"           # Cannot be used
    WEAK = "weak"                 # Low confidence, may be noisy
    MODERATE = "moderate"         # Reasonable confidence
    STRONG = "strong"             # High confidence, reliable
    CONCLUSIVE = "conclusive"     # Near-certain, very reliable


class DependencyType(Enum):
    """Types of dependencies between evidence sources."""
    
    INDEPENDENT = "independent"       # No relationship
    CONDITIONAL = "conditional"       # One depends on another
    CORRELATED = "correlated"         # Related but not directly dependent
    MUTUALLY_EXCLUSIVE = "mutually_exclusive"  # Cannot both be true


@dataclass(frozen=True)
class EvidenceSource:
    """
    A single evidence source with reliability and confidence estimates.
    
    Each source includes:
        - Source identity and type
        - Reliability estimate (how often is it correct?)
        - Confidence in the specific evidence
        - Quality rating
    """
    
    # Identity
    source_id: str                      # Unique identifier for this source
    
    # Source information
    source_type: str                    # e.g., "sensor", "memory", "prediction"
    source_name: Optional[str] = None   # Human-readable name
    
    # Reliability estimates
    reliability_estimate: float = 0.5   # 0.0 to 1.0, estimated accuracy
    
    # Quality metrics
    quality_rating: EvidenceQuality = EvidenceQuality.MODERATE
    confidence_estimate: float = 0.5    # Confidence in this specific evidence
    
    # Metadata
    timestamp_utc: float = field(default_factory=time.time)
    
    @property
    def is_reliable(self) -> bool:
        """Check if source meets minimum reliability threshold."""
        return self.reliability_estimate >= 0.7


@dataclass(frozen=True)
class SourceWeight:
    """
    Weight assigned to an evidence source for fusion calculations.
    
    Weights determine how much influence a source has during fusion.
    """
    
    # Source reference
    source_id: str              # Reference to EvidenceSource.source_id
    
    # Weight parameters
    base_weight: float = 1.0    # Base weight before adjustments
    reliability_multiplier: float = 1.0  # Multiplier based on reliability
    
    @property
    def effective_weight(self) -> float:
        """Calculate effective weight after applying multipliers."""
        return self.base_weight * self.reliability_multiplier


@dataclass(frozen=True)
class DependencyGraph:
    """
    Graph representing dependencies between evidence sources.
    
    Dependencies affect how evidence is combined during fusion.
    """
    
    # Structure
    edges: Dict[str, List[str]] = field(default_factory=dict)  # source_id -> dependent_source_ids
    
    # Configuration
    default_dependency_type: DependencyType = DependencyType.INDEPENDENT
    max_chain_length: int = 10
    
    def add_edge(self, from_id: str, to_id: str) -> DependencyGraph:
        """Add a dependency edge."""
        new_edges = dict(self.edges)
        if from_id not in new_edges:
            new_edges[from_id] = []
        new_edges[from_id].append(to_id)
        return dataclass_replace(self, edges=new_edges)
    
    def get_dependents(self, source_id: str) -> List[str]:
        """Get sources that depend on this one."""
        return self.edges.get(source_id, [])
    
    def is_independent(self, id1: str, id2: str) -> bool:
        """Check if two sources are independent (no path between them)."""
        # For now, simple check - can be expanded for full graph traversal
        deps1 = set(self.get_dependents(id1))
        deps2 = set(self.get_dependents(id2))
        return id1 not in deps2 and id2 not in deps1


@dataclass(frozen=True)
class ProbabilityEvidenceSet:
    """
    Set of evidence sources with weights and dependency information.
    
    Evidence Sets define the input to probabilistic reasoning.
    They remain immutable during inference.
    """
    
    # Identity
    evidence_set_id: str                    # Unique identifier
    
    # Evidence collection
    participating_evidence: Tuple[EvidenceSource, ...] = ()
    
    # Weights
    source_weights: Dict[str, SourceWeight] = field(default_factory=dict)
    
    # Dependencies
    dependencies: DependencyGraph = field(default_factory=DependencyGraph)
    
    # Metadata
    created_at_utc: float = field(default_factory=time.time)
    
    @property
    def total_weight(self) -> float:
        """Calculate sum of all effective weights."""
        return sum(
            w.effective_weight for w in self.source_weights.values()
        )
    
    @property
    def reliable_sources(self) -> Tuple[EvidenceSource, ...]:
        """Get sources that meet reliability threshold."""
        return tuple(e for e in self.participating_evidence if e.is_reliable)
    
    @classmethod
    def create(
        cls,
        participating_evidence: List[EvidenceSource],
        source_weights: Optional[Dict[str, SourceWeight]] = None,
        dependencies: Optional[DependencyGraph] = None,
    ) -> ProbabilityEvidenceSet:
        """Create a new evidence set."""
        weights = source_weights or {}
        
        # Auto-generate weights for unweighted sources
        for evidence in participating_evidence:
            if evidence.source_id not in weights:
                weights[evidence.source_id] = SourceWeight(
                    source_id=evidence.source_id,
                    base_weight=1.0,
                    reliability_multiplier=evidence.reliability_estimate,
                )
        
        return cls(
            evidence_set_id=f"evidence_set:{uuid.uuid4().hex[:16]}",
            participating_evidence=tuple(participating_evidence),
            source_weights=weights,
            dependencies=dependencies or DependencyGraph(),
            created_at_utc=time.time(),
        )
    
    def with_evidence(self, new_evidence: EvidenceSource) -> ProbabilityEvidenceSet:
        """Return a copy with added evidence."""
        new_evidence_list = list(self.participating_evidence)
        new_evidence_list.append(new_evidence)
        
        # Add default weight if not present
        new_weights = dict(self.source_weights)
        if new_evidence.source_id not in new_weights:
            new_weights[new_evidence.source_id] = SourceWeight(
                source_id=new_evidence.source_id,
                base_weight=1.0,
                reliability_multiplier=new_evidence.reliability_estimate,
            )
        
        return dataclass_replace(
            self,
            participating_evidence=tuple(new_evidence_list),
            source_weights=new_weights,
        )


def dataclass_replace(instance: Any, **kwargs: Any) -> Any:
    """Simple dataclass replace helper for frozen instances."""
    return instance.__class__(**{**instance.__dict__, **kwargs})


__all__ = [
    "ProbabilityEvidenceSet",
    "EvidenceSource", 
    "SourceWeight",
    "DependencyGraph",
    "EvidenceQuality",
    "DependencyType",
]