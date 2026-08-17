"""Discovery Service - Phase 6.9 Part 2 Section 12.

This module implements the canonical contract for knowledge discovery
in Knowledge Services.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Tuple, Optional, Any
from enum import Enum, auto
import time
import uuid


# =============================================================================
# DISCOVERY METHOD - Phase 6.9 Part 2 Section 13
# =============================================================================


class DiscoveryMethod(Enum):
    """
    Methods for knowledge discovery.
    
    Per DISCOVERY-LAW-001: Discovery shall produce Candidates only.
    
    Types:
        GRAPH_ANALYSIS    -> Analyze graph structure for gaps
        SEMANTIC_GAP      -> Identify semantic inconsistencies
        MISSING_RELATION  -> Find missing relations between known artifacts
        ANOMALY_DETECTION -> Detect anomalies that suggest missing knowledge
        INCONSISTENCY     -> Identify conflicting or incomplete information
    """
    
    GRAPH_ANALYSIS = "graph_analysis"
    SEMANTIC_GAP = "semantic_gap"
    MISSING_RELATION = "missing_relation"
    ANOMALY_DETECTION = "anomaly_detection"
    INCONSISTENCY = "inconsistency"


# =============================================================================
# DISCOVERY CANDIDATE - Phase 6.9 Part 2 Section 12
# =============================================================================


@dataclass(frozen=True)
class DiscoveryCandidate:
    """
    Candidate for discovered knowledge.
    
    Per DISCOVERY-LAW-001: Discovery shall produce Candidates only.
    
    Fields:
        candidate_identity: Unique identifier for this candidate
        candidate_kind: Kind of artifact that might be missing
        supporting_evidence: Evidence suggesting this candidate exists
        confidence: Confidence in the candidate's existence (0.0 - 1.0)
        
    Invariants:
        * Discovery produces candidates only, not canonical artifacts
        * Supporting evidence is preserved (DISCOVERY-LAW-002)
        * Uncertainty is recorded (DISCOVERY-LAW-003)
    """
    
    candidate_identity: str  # Unique identifier
    
    candidate_kind: str  # "concept", "relation", "assertion", "belief"
    supporting_evidence: Tuple[str, ...]
    confidence: float = 0.5
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert candidate to dictionary."""
        return {
            "candidate_identity": self.candidate_identity,
            "candidate_kind": self.candidate_kind,
            "supporting_evidence": list(self.supporting_evidence),
            "confidence": self.confidence,
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> DiscoveryCandidate:
        """Create candidate from dictionary."""
        return cls(
            candidate_identity=data.get("candidate_identity", str(uuid.uuid4())),
            candidate_kind=data.get("candidate_kind", "concept"),
            supporting_evidence=tuple(data.get("supporting_evidence", [])),
            confidence=float(data.get("confidence", 0.5)),
        )


# =============================================================================
# DISCOVERY PIPELINE - Phase 6.9 Part 2 Section 13
# =============================================================================


@dataclass(frozen=True)
class DiscoveryPipeline:
    """
    Pipeline for knowledge discovery operations.
    
    Per DISCOVERY-LAW-005: Discovery provenance shall remain complete.
    
    Fields:
        pipeline_identity: Unique identifier for this pipeline
        discovery_method: Method used for discovery
        
    Invariants:
        * Methods are explicit (implied)
        * Provenance is preserved
    """
    
    pipeline_identity: str  # Unique identifier
    
    discovery_method: DiscoveryMethod
    
    diagnostics: Dict[str, Any] = field(default_factory=dict)
    
    def __post_init__(self) -> None:
        """Validate pipeline after creation."""
        if not self.pipeline_identity:
            raise ValueError("pipeline_identity cannot be empty")
    
    @classmethod
    def create_initial(
        cls,
        method: DiscoveryMethod,
    ) -> "DiscoveryPipeline":
        """
        Create initial discovery pipeline.
        
        Args:
            method: Method to use for discovery
            
        Returns:
            New DiscoveryPipeline ready for execution
        """
        return cls(
            pipeline_identity=f"discovery-pipeline:{uuid.uuid4().hex[:16]}",
            discovery_method=method,
        )
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert pipeline to dictionary."""
        return {
            "pipeline_identity": self.pipeline_identity,
            "discovery_method": self.discovery_method.value,
            "diagnostics": dict(self.diagnostics),
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "DiscoveryPipeline":
        """Create pipeline from dictionary."""
        return cls(
            pipeline_identity=data.get("pipeline_identity", str(uuid.uuid4())),
            discovery_method=DiscoveryMethod(data.get("discovery_method", "graph_analysis")),
            diagnostics=dict(data.get("diagnostics", {})),
        )


# =============================================================================
# KNOWLEDGE DISCOVERY - Phase 6.9 Part 2 Section 10
# =============================================================================


@dataclass(frozen=True)
class KnowledgeDiscovery:
    """
    Knowledge discovery operation result.
    
    Per DISCOVERY-LAW-001: Discovery shall produce Candidates only.
    Per DISCOVERY-LAW-007: Discovery shall remain independently inspectable.
    
    Fields:
        discovery_identity: Unique identifier for this discovery
        discovery_method: Method used to discover candidates
        discovered_candidates: Candidates found by discovery
        
    Invariants:
        * Only produces candidates, not canonical artifacts (DISCOVERY-LAW-001)
        * Supporting evidence is preserved (DISCOVERY-LAW-002)
        * Uncertainty is recorded (DISCOVERY-LAW-003)
    """
    
    discovery_identity: str  # Unique identifier
    
    discovery_method: DiscoveryMethod
    
    discovered_candidates: Tuple[DiscoveryCandidate, ...]
    
    # Confidence in overall discovery (0.0 - 1.0)
    confidence: float = 0.0
    
    # Uncertainty measures
    uncertainty: Dict[str, Any] = field(default_factory=dict)
    
    # Provenance
    provenance: Tuple[Dict[str, Any], ...] = field(default_factory=tuple)
    
    def __post_init__(self) -> None:
        """Validate discovery result after creation."""
        if not self.discovery_identity:
            raise ValueError("discovery_identity cannot be empty")
    
    @property
    def candidate_count(self) -> int:
        """Number of candidates discovered."""
        return len(self.discovered_candidates)
    
    @classmethod
    def create_initial(
        cls,
        discovery_method: DiscoveryMethod,
    ) -> "KnowledgeDiscovery":
        """
        Create initial knowledge discovery.
        
        Args:
            discovery_method: Method to use for discovery
            
        Returns:
            New KnowledgeDiscovery with empty candidates
        """
        return cls(
            discovery_identity=f"discovery:{uuid.uuid4().hex[:16]}",
            discovery_method=discovery_method,
            discovered_candidates=tuple(),
            provenance=(
                {
                    "provenance_identity": f"provenance:{uuid.uuid4().hex[:16]}",
                    "originating_request": "Knowledge discovery initialization",
                    "originating_system": "knowledge-services-system",
                    "timestamp_utc": time.time(),
                },
            ),
        )
    
    def add_candidate(
        self,
        candidate: DiscoveryCandidate,
    ) -> "KnowledgeDiscovery":
        """Add a discovered candidate and return new result."""
        # Recalculate confidence
        all_confidences = [c.confidence for c in self.discovered_candidates] + [candidate.confidence]
        avg_confidence = sum(all_confidences) / len(all_confidences)
        
        return KnowledgeDiscovery(
            discovery_identity=self.discovery_identity,
            discovery_method=self.discovery_method,
            discovered_candidates=tuple(list(self.discovered_candidates) + [candidate]),
            confidence=avg_confidence,
            uncertainty=dict(self.uncertainty),
            provenance=tuple(list(self.provenance) + [
                {
                    "provenance_identity": f"provenance:{uuid.uuid4().hex[:16]}",
                    "originating_request": f"Added discovery candidate: {candidate.candidate_identity}",
                    "originating_system": "knowledge-services-system",
                    "timestamp_utc": time.time(),
                },
            ]),
        )
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert discovery result to dictionary."""
        return {
            "discovery_identity": self.discovery_identity,
            "discovery_method": self.discovery_method.value,
            "discovered_candidates": [c.to_dict() for c in self.discovered_candidates],
            "confidence": self.confidence,
            "uncertainty": dict(self.uncertainty),
            "provenance": list(self.provenance),
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "KnowledgeDiscovery":
        """Create discovery result from dictionary."""
        candidates = []
        for c_data in data.get("discovered_candidates", []):
            if isinstance(c_data, dict):
                candidates.append(DiscoveryCandidate.from_dict(c_data))
        
        provenance = []
        for p_data in data.get("provenance", []):
            if isinstance(p_data, dict):
                provenance.append(p_data)
        
        return cls(
            discovery_identity=data.get("discovery_identity", str(uuid.uuid4())),
            discovery_method=DiscoveryMethod(data.get("discovery_method", "graph_analysis")),
            discovered_candidates=tuple(candidates),
            confidence=float(data.get("confidence", 0.0)),
            uncertainty=dict(data.get("uncertainty", {})),
            provenance=tuple(provenance),
        )


# =============================================================================
# EXPORTS
# =============================================================================


__all__ = [
    # Discovery methods (Part 2 Section 13)
    "DiscoveryMethod",
    # Discovery candidates
    "DiscoveryCandidate",
    # Discovery pipeline
    "DiscoveryPipeline",
    # Knowledge discovery
    "KnowledgeDiscovery",
]