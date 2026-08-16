# Migration Domain - Governance Subsystem

"""
Migration: Version transition evaluation for Memory.

The migration domain:
    
    - Evaluates transitions between memory versions
    - Assesses semantic identity preservation
    - Provides migration recommendations
    - Never executes migrations
    
Migration Laws:

    MIGRATION-LAW-001: Migration shall evaluate compatibility
    MIGRATION-LAW-002: Migration shall preserve semantic identity
    MIGRATION-LAW-003: Migration shall preserve provenance
    MIGRATION-LAW-004: Migration shall preserve revision history
    MIGRATION-LAW-005: Migration recommendations shall remain explicit
    MIGRATION-LAW-006: Migration shall never execute migrations
    MIGRATION-LAW-007: Migration reports shall remain inspectable
    MIGRATION-LAW-008: Migration evaluation shall remain deterministic

Migration Input:
    
    - Current revision identifier
    - Target revision identifier
    - Migration strategy (if any)
    - Compatibility requirements

Migration Output:
    
    - Migration Certification
    - Compatibility Assessment
    - Migration Recommendations
    
Anti-Patterns Rejected:
    
    - Direct migration execution
    - Hidden compatibility analysis
    - Non-deterministic migration evaluation
"""

from __future__ import annotations

from typing import Dict, List, Tuple, Optional, Any
from dataclasses import dataclass, field
import time


# =============================================================================
# MIGRATION CERTIFICATION
# =============================================================================


@dataclass(frozen=True)
class MigrationCertification:
    """
    Certification of a memory migration.
    
    Fields:
        certification_id:   Unique identifier
        
        from_revision:      Source revision identifier
        to_revision:        Target revision identifier
        
        compatibility_score: 0.0-1.0 compatibility score
        semantic_preserved:  True if semantic identity preserved
        provenance_preserved: True if provenance preserved
        
        issues:             List of migration issues found
        warnings:           List of warnings
        
        timestamp_utc:      When certification was issued
    """
    
    certification_id: str                  # Unique identifier
    
    from_revision: str                     # Source revision identifier
    to_revision: str                       # Target revision identifier
    
    compatibility_score: float = 1.0       # Compatibility score (0.0-1.0)
    
    semantic_preserved: bool = True        # Semantic identity preserved?
    provenance_preserved: bool = True      # Provenance preserved?
    
    issues: Tuple[str, ...] = field(default_factory=tuple)   # Migration issues
    warnings: Tuple[str, ...] = field(default_factory=tuple)  # Warnings
    
    timestamp_utc: float = field(default_factory=time.time)
    
    @property
    def is_migratable(self) -> bool:
        """Check if migration is recommended."""
        return (
            self.compatibility_score >= 0.9 
            and self.semantic_preserved 
            and self.provenance_preserved
        )
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert certification to dictionary representation."""
        return {
            "certification_id": self.certification_id,
            "from_revision": self.from_revision,
            "to_revision": self.to_revision,
            "compatibility_score": self.compatibility_score,
            "semantic_preserved": self.semantic_preserved,
            "provenance_preserved": self.provenance_preserved,
            "issues": list(self.issues),
            "warnings": list(self.warnings),
            "timestamp_utc": self.timestamp_utc,
        }


# =============================================================================
# MIGRATION RECOMMENDATION
# =============================================================================


@dataclass(frozen=True)
class MigrationRecommendation:
    """
    Recommendation for a memory migration.
    
    Fields:
        recommendation_id:  Unique identifier
        
        strategy:           Migration strategy (direct, staged, staged_with_backup)
        
        estimated_duration_seconds: Estimated duration of migration
        risk_level:         Risk level (low/medium/high)
        
        prerequisites:      List of prerequisites that must be met first
        post_migration_actions: Actions to take after migration
        
        timestamp_utc:      When recommendation was created
    """
    
    recommendation_id: str                  # Unique identifier
    
    strategy: str = "direct"               # direct/staged/staged_with_backup
    
    estimated_duration_seconds: float = 0.0
    risk_level: str = "medium"             # low/medium/high
    
    prerequisites: Tuple[str, ...] = field(default_factory=tuple)
    post_migration_actions: Tuple[str, ...] = field(default_factory=tuple)
    
    timestamp_utc: float = field(default_factory=time.time)
    
    @property
    def is_low_risk(self) -> bool:
        """Check if migration is low risk."""
        return self.risk_level == "low"
    
    @property
    def is_ready_for_execution(self) -> bool:
        """Check if all prerequisites are met (simplified)."""
        # In a real implementation, this would check actual state
        return True
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert recommendation to dictionary representation."""
        return {
            "recommendation_id": self.recommendation_id,
            "strategy": self.strategy,
            "estimated_duration_seconds": self.estimated_duration_seconds,
            "risk_level": self.risk_level,
            "prerequisites": list(self.prerequisites),
            "post_migration_actions": list(self.post_migration_actions),
            "timestamp_utc": self.timestamp_utc,
        }


# =============================================================================
# MIGRATION REPORT
# =============================================================================


@dataclass(frozen=True)
class MigrationReport:
    """
    Complete report on migration evaluation.
    
    Fields:
        report_id:          Unique identifier
        
        from_revision:      Source revision identifier
        to_revision:        Target revision identifier
        
        certification:      MigrationCertification
        recommendation:     MigrationRecommendation
        
        timestamp_utc:      When report was generated
    """
    
    report_id: str                          # Unique identifier
    
    from_revision: str                     # Source revision identifier
    to_revision: str                       # Target revision identifier
    
    certification: MigrationCertification
    recommendation: MigrationRecommendation
    
    timestamp_utc: float = field(default_factory=time.time)
    
    @property
    def is_migration_ready(self) -> bool:
        """Check if migration is ready."""
        return self.certification.is_migratable and self.recommendation.is_low_risk
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert report to dictionary representation."""
        return {
            "report_id": self.report_id,
            "from_revision": self.from_revision,
            "to_revision": self.to_revision,
            "certification": self.certification.to_dict(),
            "recommendation": self.recommendation.to_dict(),
            "timestamp_utc": self.timestamp_utc,
        }


# =============================================================================
# EXPORTS
# =============================================================================

__all__ = [
    "MigrationCertification",
    "MigrationRecommendation",
    "MigrationReport",
]