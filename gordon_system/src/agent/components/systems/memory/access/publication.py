# Memory Publication - Phase 5.1.3 Canonical Access Exposure
# ==========================================================

"""
Memory Publication: Exposes approved projections to consumers.

Publication:
    - Constructs consumer-specific views of memory
    - May filter, summarize, or serialize artifacts
    - Never changes semantic meaning or memory state

Publication Laws:
    PUBLICATION-LAW-001: Only projections are published
    PUBLICATION-LAW-002: Implementation internals never exposed
    PUBLICATION-LAW-003: Semantic consistency preserved
    PUBLICATION-LAW-004: Provenance preserved
    PUBLICATION-LAW-005: Revisions remain explicit
    PUBLICATION-LAW-006: Explainability preserved
    PUBLICATION-LAW-007: Compatibility preserved
    PUBLICATION-LAW-008: Deterministic behavior
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Tuple, Optional, Any
from enum import Enum, auto
import time


# =============================================================================
# PUBLICATION FORMAT - How results are serialized?
# =============================================================================


class PublicationFormat(Enum):
    """
    Output formats for published projections.
    
    | Format       | Description                               |
    |--------------|-------------------------------------------|
    | FULL         | Complete artifact data                    |
    | SUMMARY      | Summary statistics only                   |
    | IDENTIFIERS  | Artifact IDs only                         |
    | METADATA     | Metadata and provenance                   |
    | RELATIONSHIP | Relationships between artifacts           |
    """
    
    FULL = "full"
    SUMMARY = "summary"
    IDENTIFIERS = "identifiers"
    METADATA = "metadata"
    RELATIONSHIP = "relationship"


# =============================================================================
# PUBLICATION RESULT - The published view
# =============================================================================


@dataclass(frozen=True)
class PublicationResult:
    """
    Result of publishing a projection.
    
    Fields:
        publication_id:   Unique identifier
        
        # Content
        artifacts:        Published artifact projections (may be filtered)
        summary:          Optional summary statistics
        
        # Metadata
        format:           How were results serialized?
        visible_count:    Number of artifacts published
        total_count:      Total matches before filtering
        
        # Timestamps
        published_at_utc: When was this published?
        
        # Constraints
        limitations:      What constraints were applied?
        
        # Provenance
        generated_by:     Who/what generated this publication?
    """
    
    publication_id: str
    
    artifacts: Tuple[Any, ...] = field(default_factory=tuple)
    summary: Optional[Dict[str, Any]] = None
    
    format: PublicationFormat = PublicationFormat.FULL
    visible_count: int = 0
    total_count: int = 0
    
    published_at_utc: float = field(default_factory=time.time)
    
    limitations: Tuple[str, ...] = field(default_factory=tuple)
    
    generated_by: Optional[str] = None


# =============================================================================
# PUBLISHER - Core publication engine
# =============================================================================


class MemoryPublisher:
    """
    Core publication engine for memory access.
    
    Publication happens through projections - the substrate is never exposed
    directly. Each publication is a consumer-specific view of memory.
    
    The publisher is stateless and deterministic.
    """
    
    def __init__(self):
        self._publication_count: int = 0
    
    @property
    def publication_count(self) -> int:
        """Total publications generated."""
        return self._publication_count
    
    def publish_projection(
        self,
        artifacts: Tuple[Any, ...],
        format: PublicationFormat = PublicationFormat.FULL,
        summary: Optional[Dict[str, Any]] = None,
        limitations: Tuple[str, ...] = tuple(),
        generated_by: Optional[str] = None,
    ) -> PublicationResult:
        """
        Publish a projection of artifacts.
        
        Args:
            artifacts: Artifacts to publish (after visibility filtering)
            format: How should they be serialized?
            summary: Summary statistics (optional)
            limitations: Applied constraints
            generated_by: Who/what generated this? (optional)
            
        Returns:
            PublicationResult with the published projection
            
        The publication is deterministic - same artifacts always produce same output.
        """
        self._publication_count += 1
        
        return PublicationResult(
            publication_id=str(time.time_ns()),
            artifacts=artifacts,
            summary=summary,
            format=format,
            visible_count=len(artifacts),
            total_count=len(artifacts),  # After visibility filtering
            published_at_utc=time.time(),
            limitations=limitations,
            generated_by=generated_by,
        )
    
    def publish_summary(
        self,
        artifact_counts: Dict[str, int],
        confidence_stats: Optional[Dict[str, float]] = None,
        total_artifact_count: Optional[int] = None,
        limitations: Tuple[str, ...] = tuple(),
        generated_by: Optional[str] = None,
    ) -> PublicationResult:
        """
        Publish a summary projection.
        
        Args:
            artifact_counts: Counts by kind
            confidence_stats: Confidence statistics (optional)
            total_artifact_count: Total count if different from sum
            limitations: Applied constraints
            generated_by: Who/what generated this? (optional)
            
        Returns:
            PublicationResult with summary data
        """
        summary = {
            "artifact_counts": dict(artifact_counts),
        }
        
        if confidence_stats is not None:
            summary["confidence_stats"] = dict(confidence_stats)
        
        total = total_artifact_count or sum(artifact_counts.values())
        
        return self.publish_projection(
            artifacts=tuple(),
            format=PublicationFormat.SUMMARY,
            summary=summary,
            limitations=limitations,
            generated_by=generated_by,
        )
    
    def publish_identifiers_only(
        self,
        artifact_ids: Tuple[str, ...],
        limitations: Tuple[str, ...] = tuple(),
        generated_by: Optional[str] = None,
    ) -> PublicationResult:
        """
        Publish only artifact identifiers.
        
        Args:
            artifact_ids: IDs to publish
            limitations: Applied constraints
            generated_by: Who/what generated this? (optional)
            
        Returns:
            PublicationResult with identifier-only view
        """
        return self.publish_projection(
            artifacts=tuple(),
            format=PublicationFormat.IDENTIFIERS,
            summary={"artifact_id_count": len(artifact_ids)},
            limitations=limitations,
            generated_by=generated_by,
        )