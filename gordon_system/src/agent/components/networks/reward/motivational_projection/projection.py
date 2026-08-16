# Motivational Projection Network - Drive Projection Model (Phase 4.10.6)
# ==========================================================================
#
# The DriveProjection model represents the projection from a reward domain
# onto a motivational drive. It never creates or modifies drives.
# It only describes potential influence.

"""
DriveProjection model for Phase 4.10.6.

This module defines the canonical DriveProjection data structure that represents
a projected motivational influence from reward domains onto motivational drives.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Tuple, Optional


class ProjectionType(Enum):
    """
    Canonical projection types for drive projections.

    PROJECTION-LAW-001: Every DriveProjection references one or more Reward Domains.
    PROJECTION-LAW-002: DriveProjections preserve semantic identity.
    PROJECTION-LAW-003: DriveProjections preserve provenance.
    PROJECTION-LAW-004: DriveProjections remain immutable.
    """
    
    # Direction types
    ENHANCE = "enhance"
    """Enhance or strengthen the target drive."""
    
    REDUCE = "reduce"
    """Reduce or weaken the target drive."""
    
    MODULATE = "modulate"
    """Modulate the target drive (context-dependent effect)."""
    
    # Strength levels for magnitude
    WEAK = "weak"
    MEDIUM = "medium"
    STRONG = "strong"
    

@dataclass(frozen=True)
class DriveProjection:
    """
    A projected motivational influence from reward domains onto a drive.

    PROJECTION-LAW-005: DriveProjections preserve revision lineage.
    PROJECTION-LAW-006: DriveProjections shall never modify Reward Domains.
    PROJECTION-LAW-007: DriveProjections remain immutable once created.
    
    OWNERSHIP PRINCIPLE:
        The Motivation System owns actual drives. This projection only describes
        potential influence without ownership or modification rights.
        
    NOT RESPONSIBLE FOR:
        • Creating or modifying drives
        • Activating/deactivating motivational state
        • Making executive decisions
        • Updating reinforcement learning models
    """
    
    # Identity and provenance
    projection_id: str
    """Unique identifier for this projection."""
    
    target_drive: str
    """The target drive being projected onto."""
    
    # Reward domain sources (one projection can have multiple sources)
    supporting_reward_domains: Tuple[str, ...]
    """Reward domain IDs supporting this projection."""
    
    # Projection characteristics
    projection_type: ProjectionType = ProjectionType.MODULATE
    """Type of projection (enhance/reduce/modulate)."""
    
    magnitude: float = 0.5
    """Magnitude of the projection effect (0.0-1.0)."""
    
    confidence: float = 1.0
    """Confidence in this projection (0.0-1.0)."""
    
    uncertainty: float = 0.0
    """Uncertainty in this projection (0.0-1.0)."""
    
    # Context
    provenance: str = "unknown"
    """Source information for traceability."""
    
    revision: int = 0
    """Version number for immutability tracking."""
    
    temporal_context: str = "immediate"
    """Timescale context (immediate/short-term/medium-term/long-term/persistent)."""
    
    # Hierarchy level
    hierarchy_level: str = "action"
    """Hierarchy level (action/task/goal/strategy/mission)."""
    
    @property
    def canonical_identity(self) -> str:
        """Return fully qualified canonical identity."""
        return f"{self.projection_id}@v{self.revision}"
    
    @property
    def effective_magnitude(self) -> float:
        """Calculate effective magnitude adjusted for confidence."""
        return self.magnitude * self.confidence
    
    @property
    def is_valid(self) -> bool:
        """Check if projection configuration is valid."""
        return (
            0.0 <= self.magnitude <= 1.0
            and 0.0 <= self.confidence <= 1.0
            and 0.0 <= self.uncertainty <= 1.0
            and self.confidence + self.uncertainty <= 1.1  # Allow small floating point error
        )
    
    def enhance(self) -> DriveProjection:
        """Return a copy with projection type set to ENHANCE."""
        return DriveProjection(
            projection_id=self.projection_id,
            target_drive=self.target_drive,
            supporting_reward_domains=self.supporting_reward_domains,
            projection_type=ProjectionType.ENHANCE,
            magnitude=self.magnitude,
            confidence=self.confidence,
            uncertainty=self.uncertainty,
            provenance=f"{self.provenance}_enhanced",
            revision=self.revision + 1,
            temporal_context=self.temporal_context,
            hierarchy_level=self.hierarchy_level,
        )
    
    def reduce(self) -> DriveProjection:
        """Return a copy with projection type set to REDUCE."""
        return DriveProjection(
            projection_id=self.projection_id,
            target_drive=self.target_drive,
            supporting_reward_domains=self.supporting_reward_domains,
            projection_type=ProjectionType.REDUCE,
            magnitude=self.magnitude,
            confidence=self.confidence,
            uncertainty=self.uncertainty,
            provenance=f"{self.provenance}_reduced",
            revision=self.revision + 1,
            temporal_context=self.temporal_context,
            hierarchy_level=self.hierarchy_level,
        )
    
    def to_dict(self) -> dict:
        """Convert projection to dictionary representation."""
        return {
            "projection_id": self.projection_id,
            "target_drive": self.target_drive,
            "supporting_reward_domains": list(self.supporting_reward_domains),
            "projection_type": self.projection_type.value,
            "magnitude": self.magnitude,
            "confidence": self.confidence,
            "uncertainty": self.uncertainty,
            "provenance": self.provenance,
            "revision": self.revision,
            "temporal_context": self.temporal_context,
            "hierarchy_level": self.hierarchy_level,
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> DriveProjection:
        """Create projection from dictionary representation."""
        proj_type = ProjectionType(data.get("projection_type", "modulate"))
        
        return cls(
            projection_id=data.get("projection_id", "unknown_projection"),
            target_drive=data.get("target_drive", "unknown_drive"),
            supporting_reward_domains=tuple(data.get("supporting_reward_domains", ())),
            projection_type=proj_type,
            magnitude=float(data.get("magnitude", 0.5)),
            confidence=float(data.get("confidence", 1.0)),
            uncertainty=float(data.get("uncertainty", 0.0)),
            provenance=data.get("provenance", "unknown"),
            revision=int(data.get("revision", 0)),
            temporal_context=data.get("temporal_context", "immediate"),
            hierarchy_level=data.get("hierarchy_level", "action"),
        )
    
    @classmethod
    def create(
        cls,
        projection_id: str,
        target_drive: str,
        reward_domain_ids: Tuple[str, ...],
        projection_type: ProjectionType = ProjectionType.MODULATE,
        magnitude: float = 0.5,
        confidence: float = 1.0,
        provenance: str = "unknown",
    ) -> DriveProjection:
        """Create a new drive projection with specified parameters."""
        return cls(
            projection_id=projection_id,
            target_drive=target_drive,
            supporting_reward_domains=reward_domain_ids,
            projection_type=projection_type,
            magnitude=magnitude,
            confidence=confidence,
            uncertainty=max(0.0, 1.0 - confidence),
            provenance=provenance,
        )


__all__ = [
    "DriveProjection",
    "ProjectionType",
]