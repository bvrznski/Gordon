# Knowledge Representation Compatibility - Phase 6.2
# =================================================

"""
Compatibility tracking between representations.

This module tracks version compatibility relationships:
    * FULL        - Fully interchangeable
    * BACKWARD    - Newer works with older consumers
    * FORWARD     - Older works with newer consumers
    * PARTIAL     - Some operations work, others don't
    * MIGRATION_REQUIRED - Requires explicit migration process
    * INCOMPATIBLE  - Cannot interact without breaking
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Tuple, Optional, Any
from enum import Enum, auto
import time
import uuid


# =============================================================================
# COMPATIBILITY KINDS - Version interaction types
# =============================================================================


class RepresentationCompatibilityKind(Enum):
    """
    Kinds of compatibility between representations.
    
    Defines how two revisions may interact:
        FULLY_COMPATIBLE      -> Can be used interchangeably
        BACKWARD_COMPATIBLE   -> Newer works with older consumers
        FORWARD_COMPATIBLE    -> Older works with newer consumers
        PARTIALLY_COMPATIBLE  -> Some operations work, others don't
        MIGRATION_REQUIRED    -> Requires explicit migration process
        INCOMPATIBLE          -> Cannot interact without breaking
    """
    
    FULLY_COMPATIBLE = "fully_compatible"
    BACKWARD_COMPATIBLE = "backward_compatible"
    FORWARD_COMPATIBLE = "forward_compatible"
    PARTIALLY_COMPATIBLE = "partially_compatible"
    MIGRATION_REQUIRED = "migration_required"
    INCOMPATIBLE = "incompatible"


# =============================================================================
# REPRESENTATION COMPATIBILITY - Version compatibility record
# =============================================================================


@dataclass(frozen=True)
class RepresentationCompatibility:
    """
    Compatibility record between two representations.
    
    Tracks how compatible two representations are, including migration
    requirements and information loss during conversion.
    
    Fields:
        compatibility_identity: Unique identifier for this compatibility record
        source_representation:  ID of the source representation
        target_representation:  ID of the target representation
        compatibility_kind:     Type of compatibility relationship
        migration_requirements: Requirements for migration (if any)
        information_loss:       Description of any information lost in conversion
        provenance_identity:    Provenance tracking info
    """
    
    # Identity (required)
    compatibility_identity: str            # Unique compatibility ID
    
    source_representation: str             # Source representation ID
    target_representation: str             # Target representation ID
    
    # Compatibility kind
    compatibility_kind: RepresentationCompatibilityKind
    
    # Migration info (optional, with defaults)
    migration_requirements: Dict[str, Any] = field(default_factory=dict)
    
    information_loss: Optional[str] = None  # Description of any loss
    
    provenance_identity: str = field(default_factory=lambda: f"compat:{uuid.uuid4().hex[:16]}")
    created_at_utc: float = field(default_factory=time.time)
    
    @property
    def is_compatible(self) -> bool:
        """Check if representations are compatible."""
        return self.compatibility_kind in (
            RepresentationCompatibilityKind.FULLY_COMPATIBLE,
            RepresentationCompatibilityKind.BACKWARD_COMPATIBLE,
            RepresentationCompatibilityKind.FORWARD_COMPATIBLE,
            RepresentationCompatibilityKind.PARTIALLY_COMPATIBLE,
        )
    
    @property
    def requires_migration(self) -> bool:
        """Check if migration is required."""
        return self.compatibility_kind == RepresentationCompatibilityKind.MIGRATION_REQUIRED
    
    @property
    def is_incompatible(self) -> bool:
        """Check if representations are incompatible."""
        return self.compatibility_kind == RepresentationCompatibilityKind.INCOMPATIBLE
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert compatibility record to dictionary for serialization."""
        return {
            "compatibility_identity": self.compatibility_identity,
            "source_representation": self.source_representation,
            "target_representation": self.target_representation,
            "compatibility_kind": self.compatibility_kind.value if hasattr(
                self.compatibility_kind, 'value'
            ) else str(self.compatibility_kind),
            "migration_requirements": self.migration_requirements,
            "information_loss": self.information_loss,
            "provenance_identity": self.provenance_identity,
            "created_at_utc": self.created_at_utc,
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "RepresentationCompatibility":
        """Create compatibility record from dictionary."""
        return cls(
            compatibility_identity=data.get("compatibility_identity", str(uuid.uuid4())),
            source_representation=data.get("source_representation", ""),
            target_representation=data.get("target_representation", ""),
            compatibility_kind=RepresentationCompatibilityKind(
                data.get("compatibility_kind", "incompatible")
            ),
            migration_requirements=data.get("migration_requirements", {}),
            information_loss=data.get("information_loss"),
            provenance_identity=data.get("provenance_identity", f"compat:{uuid.uuid4().hex[:16]}"),
            created_at_utc=float(data.get("created_at_utc", time.time())),
        )
    
    @classmethod
    def create_compatible(
        cls,
        source_id: str,
        target_id: str,
    ) -> "RepresentationCompatibility":
        """Create a fully compatible relationship."""
        return cls(
            compatibility_identity=f"compat:{uuid.uuid4().hex[:16]}",
            source_representation=source_id,
            target_representation=target_id,
            compatibility_kind=RepresentationCompatibilityKind.FULLY_COMPATIBLE,
        )
    
    @classmethod
    def create_backward_compatible(
        cls,
        source_id: str,
        target_id: str,
    ) -> "RepresentationCompatibility":
        """Create a backward compatible relationship (newer works with older)."""
        return cls(
            compatibility_identity=f"compat:{uuid.uuid4().hex[:16]}",
            source_representation=source_id,
            target_representation=target_id,
            compatibility_kind=RepresentationCompatibilityKind.BACKWARD_COMPATIBLE,
        )
    
    @classmethod
    def create_incompatible(
        cls,
        source_id: str,
        target_id: str,
        reason: Optional[str] = None,
    ) -> "RepresentationCompatibility":
        """Create an incompatible relationship."""
        return cls(
            compatibility_identity=f"compat:{uuid.uuid4().hex[:16]}",
            source_representation=source_id,
            target_representation=target_id,
            compatibility_kind=RepresentationCompatibilityKind.INCOMPATIBLE,
            information_loss=reason,
        )


__all__ = [
    # Compatibility kinds
    "RepresentationCompatibilityKind",
    
    # Compatibility records
    "RepresentationCompatibility",
]