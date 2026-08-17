# Knowledge Compatibility - Phase 6.1
# ===================================

"""
Knowledge Compatibility: Revision interaction and migration support in Gordon's knowledge system.

Compatibility determines how two revisions may interact:
    FULLY_COMPATIBLE      -> Can be used interchangeably
    BACKWARD_COMPATIBLE   -> Newer works with older consumers  
    FORWARD_COMPATIBLE    -> Older works with newer consumers
    PARTIALLY_COMPATIBLE  -> Some operations work, others don't
    MIGRATION_REQUIRED    -> Requires explicit migration process
    INCOMPATIBLE          -> Cannot interact without breaking

Compatibility never changes artifacts - it's purely a relationship assessment.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Tuple, Optional, Any
from enum import Enum, auto
import time
import uuid


# =============================================================================
# COMPATIBILITY KINDS - Revision interaction types
# =============================================================================


class CompatibilityKind(Enum):
    """
    Kinds of compatibility between revisions.
    
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
# COMPATIBILITY RECORD - Revision compatibility assessment
# =============================================================================


@dataclass(frozen=True)
class CompatibilityRecord:
    """
    Assessment of compatibility between two revisions.
    
    Records the evaluation result for how two revision states may interact.
    
    Fields:
        compatibility_identity:  Unique identifier for this record
        source_revision:         First revision (reference point)
        target_revision:         Second revision (to compare against)
        compatibility_kind:      Type of compatibility determined
        migration_requirements:  What's needed to make compatible
        limitations:             Constraints when interacting
        timestamp_utc:           When assessment was made
    """
    
    # Identity and metadata (required)
    compatibility_identity: str           # Unique record ID
    
    source_revision: str                  # First revision identity
    target_revision: str                  # Second revision identity
    
    compatibility_kind: CompatibilityKind = CompatibilityKind.INCOMPATIBLE
    
    migration_requirements: Tuple[str, ...] = field(default_factory=tuple)  # Steps needed
    limitations: Tuple[str, ...] = field(default_factory=tuple)            # Constraints
    
    timestamp_utc: float = field(default_factory=time.time)
    
    @property
    def is_valid(self) -> bool:
        """Check if record has valid data."""
        return (
            len(self.compatibility_identity) > 0 and
            len(self.source_revision) > 0 and
            len(self.target_revision) > 0
        )
    
    @property
    def is_compatible(self) -> bool:
        """Check if revisions are compatible for interaction."""
        return self.compatibility_kind in (
            CompatibilityKind.FULLY_COMPATIBLE,
            CompatibilityKind.BACKWARD_COMPATIBLE,
            CompatibilityKind.FORWARD_COMPATIBLE,
        )
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert record to dictionary for serialization."""
        return {
            "compatibility_identity": self.compatibility_identity,
            "source_revision": self.source_revision,
            "target_revision": self.target_revision,
            "compatibility_kind": self.compatibility_kind.value,
            "migration_requirements": list(self.migration_requirements),
            "limitations": list(self.limitations),
            "timestamp_utc": self.timestamp_utc,
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "CompatibilityRecord":
        """Create record from dictionary."""
        return cls(
            compatibility_identity=data.get("compatibility_identity", str(uuid.uuid4())),
            source_revision=data.get("source_revision", ""),
            target_revision=data.get("target_revision", ""),
            compatibility_kind=CompatibilityKind(data.get("compatibility_kind", "incompatible")),
            migration_requirements=tuple(data.get("migration_requirements", [])),
            limitations=tuple(data.get("limitations", [])),
            timestamp_utc=float(data.get("timestamp_utc", time.time())),
        )


# =============================================================================
# COMPATIBILITY ENGINE - Compatibility assessment
# =============================================================================


class CompatibilityEngine:
    """
    Engine for assessing revision compatibility.
    
    Evaluates how two revisions interact, determines migration requirements,
    and provides compatibility information for safe interaction.
    """
    
    def __init__(
        self,
        default_kind: CompatibilityKind = CompatibilityKind.INCOMPATIBLE,
    ):
        """
        Initialize the compatibility engine.
        
        Args:
            default_kind: Default compatibility when undetermined
        """
        self._default_kind = default_kind
    
    def compare_revisions(
        self,
        source_revision_id: str,
        target_revision_id: str,
        source_data: Dict[str, Any],
        target_data: Dict[str, Any],
    ) -> CompatibilityRecord:
        """
        Compare two revisions for compatibility.
        
        Args:
            source_revision_id: First revision identifier
            target_revision_id: Second revision identifier
            source_data: Data from first revision
            target_data: Data from second revision
            
        Returns:
            CompatibilityRecord with assessment result
        """
        # Get semantic identity to compare (must be same artifact)
        source_identity = source_data.get("semantic_identity", "")
        target_identity = target_data.get("semantic_identity", "")
        
        if source_identity != target_identity:
            return CompatibilityRecord(
                compatibility_identity=f"compat:{uuid.uuid4().hex[:16]}",
                source_revision=source_revision_id,
                target_revision=target_revision_id,
                compatibility_kind=CompatibilityKind.INCOMPATIBLE,
                limitations=("Different semantic identities",),
                timestamp_utc=time.time(),
            )
        
        # Compare revision numbers
        source_rev = source_data.get("semantic_revision", 1)
        target_rev = target_data.get("semantic_revision", 1)
        
        if source_rev == target_rev:
            return CompatibilityRecord(
                compatibility_identity=f"compat:{uuid.uuid4().hex[:16]}",
                source_revision=source_revision_id,
                target_revision=target_revision_id,
                compatibility_kind=CompatibilityKind.FULLY_COMPATIBLE,
                timestamp_utc=time.time(),
            )
        
        # Determine compatibility based on revision relationship
        if abs(target_rev - source_rev) == 1:
            # Adjacent revisions are typically backward compatible
            return CompatibilityRecord(
                compatibility_identity=f"compat:{uuid.uuid4().hex[:16]}",
                source_revision=source_revision_id,
                target_revision=target_revision_id,
                compatibility_kind=CompatibilityKind.BACKWARD_COMPATIBLE,
                timestamp_utc=time.time(),
            )
        
        # Non-adjacent revisions may require migration
        return CompatibilityRecord(
            compatibility_identity=f"compat:{uuid.uuid4().hex[:16]}",
            source_revision=source_revision_id,
            target_revision=target_revision_id,
            compatibility_kind=CompatibilityKind.MIGRATION_REQUIRED,
            migration_requirements=(
                "Apply intermediate revisions in order",
                "Verify schema compatibility",
                "Update dependent references",
            ),
            timestamp_utc=time.time(),
        )
    
    def check_migration_needed(
        self,
        record: CompatibilityRecord,
    ) -> bool:
        """
        Check if a migration is required for compatible interaction.
        
        Args:
            record: Compatibility assessment
            
        Returns:
            True if migration is required
        """
        return record.compatibility_kind in (
            CompatibilityKind.MIGRATION_REQUIRED,
            CompatibilityKind.INCOMPATIBLE,
        )
    
    def get_migration_steps(
        self,
        record: CompatibilityRecord,
    ) -> List[str]:
        """
        Get the steps needed for migration.
        
        Args:
            record: Compatibility assessment
            
        Returns:
            List of migration step descriptions
        """
        if record.migration_requirements:
            return list(record.migration_requirements)
        
        # Default migration steps
        return [
            "Review revision differences",
            "Update schema structures",
            "Migrate data fields",
            "Verify compatibility constraints",
        ]


# =============================================================================
# MIGRATION RECORD - Migration operation tracking
# =============================================================================


@dataclass(frozen=True)
class MigrationRecord:
    """
    Record of a migration operation between revisions.
    
    Tracks the transformation applied during migration for auditability.
    
    Fields:
        migration_identity:     Unique identifier for this migration
        source_revision:        Source revision (before migration)
        target_revision:        Target revision (after migration)
        migration_steps:        Steps performed during migration
        information_loss:       Any data that could not be migrated
        compatibility_result:   Result after migration
        timestamp_utc:          When migration occurred
    """
    
    # Identity and metadata (required)
    migration_identity: str               # Unique migration ID
    
    source_revision: str                  # Source revision identity
    target_revision: str                  # Target revision identity
    
    migration_steps: Tuple[str, ...] = field(default_factory=tuple)  # Steps performed
    information_loss: Tuple[str, ...] = field(default_factory=tuple)  # Lost data
    
    compatibility_result: Dict[str, Any] = field(default_factory=dict)  # Result status
    
    timestamp_utc: float = field(default_factory=time.time)
    
    @property
    def is_valid(self) -> bool:
        """Check if migration record has valid data."""
        return (
            len(self.migration_identity) > 0 and
            len(self.source_revision) > 0 and
            len(self.target_revision) > 0
        )
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert record to dictionary for serialization."""
        return {
            "migration_identity": self.migration_identity,
            "source_revision": self.source_revision,
            "target_revision": self.target_revision,
            "migration_steps": list(self.migration_steps),
            "information_loss": list(self.information_loss),
            "compatibility_result": dict(self.compatibility_result),
            "timestamp_utc": self.timestamp_utc,
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "MigrationRecord":
        """Create record from dictionary."""
        return cls(
            migration_identity=data.get("migration_identity", str(uuid.uuid4())),
            source_revision=data.get("source_revision", ""),
            target_revision=data.get("target_revision", ""),
            migration_steps=tuple(data.get("migration_steps", [])),
            information_loss=tuple(data.get("information_loss", [])),
            compatibility_result=dict(data.get("compatibility_result", {})),
            timestamp_utc=float(data.get("timestamp_utc", time.time())),
        )


__all__ = [
    # Compatibility kinds
    "CompatibilityKind",
    # Record types
    "CompatibilityRecord",
    "MigrationRecord",
    # Engine
    "CompatibilityEngine",
]