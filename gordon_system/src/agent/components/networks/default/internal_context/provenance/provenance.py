# Internal Context Provenance Models
# ===================================

"""
Provenance models for internal context.

Provenance tracks the origin and transformation history of context items
without copying full source payloads.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Tuple, Optional
from datetime import datetime


@dataclass(frozen=True, slots=True)
class ProjectionSource:
    """
    Source information for a projection without ownership transfer.
    
    PROPERTIES:
        • source_id: Unique identifier of the source system
        • source_type: Type/category of source (e.g., "memory", "identity")
        • source_revision: Revision number at time of capture
    """
    
    source_id: str
    """Unique identifier of the source system."""
    
    source_type: str = "unknown"
    """Type/category of source."""
    
    source_revision: int = 1
    """Revision number at time of capture."""


@dataclass(frozen=True, slots=True)
class ProjectionProvenance:
    """
    Provenance record for a single projection.
    
    PROPERTIES:
        • projection_id: Unique identifier for this projection instance
        • source: Source system information
        • captured_at_utc: When the projection was captured
        • transformation_count: Number of transformations applied
        • normalized_values: Whether values were normalized
    """
    
    projection_id: str
    """Unique identifier for this projection."""
    
    source: ProjectionSource
    """Source system information."""
    
    captured_at_utc: datetime
    """When the projection was captured."""
    
    transformation_count: int = 0
    """Number of transformations applied during assembly."""
    
    normalized_values: bool = True
    """Whether values were normalized during assembly."""
    
    @classmethod
    def from_projection(
        cls,
        projection_id: str,
        source: ProjectionSource,
        captured_at_utc: datetime,
    ) -> ProjectionProvenance:
        """Create provenance from a projection."""
        return cls(
            projection_id=projection_id,
            source=source,
            captured_at_utc=captured_at_utc,
        )


@dataclass(frozen=True, slots=True)
class InternalContextProvenance:
    """
    Complete provenance for an internal context.
    
    Bounded record of how the context was assembled, including source
    projection references and assembly metadata. Does NOT contain full
    source payloads - only references.
    
    PROPERTIES:
        • request_id: ID of the context request that triggered assembly
        • captured_at_utc: When assembly completed
        • assembler_version: Version of assembler used
        • configuration_hash: Hash of configuration for reproducibility
        • total_source_projections: Number of source projections included
        • source_projection_ids: Tuple of source projection IDs (bounded)
    """
    
    request_id: str
    """ID of the context request that triggered assembly."""
    
    captured_at_utc: datetime
    """When assembly completed."""
    
    assembler_version: str = "1.0.0"
    """Version of assembler used."""
    
    configuration_hash: Optional[str] = None
    """Hash of configuration for reproducibility tracking."""
    
    total_source_projections: int = 0
    """Total number of source projections included in this context."""
    
    source_projection_ids: Tuple[str, ...] = field(default_factory=tuple)
    """Tuple of source projection IDs (bounded to prevent unbounded growth)."""
    
    # Transformation records (bounded)
    transformation_records: Tuple[Tuple[str, str], ...] = field(default_factory=tuple)
    """Records of transformations applied during assembly."""
    
    @classmethod
    def create(
        cls,
        request_id: str,
        captured_at_utc: datetime,
        source_projection_ids: Tuple[str, ...] = (),
        transformation_records: Tuple[Tuple[str, str], ...] = (),
    ) -> InternalContextProvenance:
        """Create a provenance record."""
        return cls(
            request_id=request_id,
            captured_at_utc=captured_at_utc,
            total_source_projections=len(source_projection_ids),
            source_projection_ids=source_projection_ids[:50],  # Bounded
            transformation_records=transformation_records[:20],  # Bounded
        )
    
    def get_oldest_source(self) -> Optional[str]:
        """Get the oldest source projection ID (first in tuple)."""
        if self.source_projection_ids:
            return self.source_projection_ids[0]
        return None