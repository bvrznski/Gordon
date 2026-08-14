# Gordon Core: Evolution Architecture (Phase 3.33)
#
# The canonical Evolution, Upgrade, Migration, and Architectural Evolution
# Architecture for the Gordon Core.
#
# This module provides one unified system governing:
# - Evolution: Architectural change while preserving identity
# - Upgrade: Replacement of architecture with new version
# - Migration: Movement of architecture between contexts
# - Compatibility: Preservation of continuity across changes
# - Deprecation: Controlled retirement of artifacts
# - Technical Debt: Management of architectural obligations

"""
Gordon Core Evolution Architecture (Phase 3.33)

This module provides the canonical Evolution, Upgrade, Migration, and
Architectural Evolution Architecture for the Gordon Core.

Evolution Philosophy:
- Evolution changes architecture while preserving identity
- Upgrade replaces architecture with newer version
- Migration moves architecture between contexts
- Compatibility preserves continuity across changes
- Deprecation ensures controlled retirement

Key Principles:
- One canonical evolution architecture throughout repository
- All evolution is explicit, governed, and auditable
- No silent or accidental evolution
- Evidence preserved for all evolutionary events
"""

from gordon_system.src.agent.architecture.evolution.foundations import (
    EvolutionType,
    EvolutionPhase,
    EvolutionStatus,
    EvolutionGovernance,
)

from gordon_system.src.agent.architecture.evolution.model import (
    EvolutionModel,
    EvolutionArtifact,
    EvolutionRelationship,
    EvolutionPath,
)

from gordon_system.src.agent.architecture.evolution.compatibility import (
    CompatibilityMode,
    CompatibilityLevel,
    CompatibilityValidator,
)

from gordon_system.src.agent.architecture.evolution.deprecation import (
    DeprecationPolicy,
    DeprecationTimeline,
    DeprecationNotice,
)

from gordon_system.src.agent.architecture.evolution.migration import (
    MigrationStrategy,
    MigrationPlan,
    MigrationTask,
)

from gordon_system.src.agent.architecture.evolution.upgrade import (
    UpgradeType,
    UpgradePolicy,
    UpgradeExecution,
)

from gordon_system.src.agent.architecture.evolution.drift import (
    DriftDetection,
    DriftReport,
    DriftRemediation,
)

from gordon_system.src.agent.architecture.evolution.debt import (
    DebtClassification,
    DebtPriority,
    DebtMetrics,
)

from gordon_system.src.agent.architecture.evolution.metrics import (
    EvolutionMetrics,
    RepositoryEvolutionScore,
)

__all__ = [
    # Foundations
    "EvolutionType",
    "EvolutionPhase",
    "EvolutionStatus",
    "EvolutionGovernance",
    # Model
    "EvolutionModel",
    "EvolutionArtifact",
    "EvolutionRelationship",
    "EvolutionPath",
    # Compatibility
    "CompatibilityMode",
    "CompatibilityLevel",
    "CompatibilityValidator",
    # Deprecation
    "DeprecationPolicy",
    "DeprecationTimeline",
    "DeprecationNotice",
    # Migration
    "MigrationStrategy",
    "MigrationPlan",
    "MigrationTask",
    # Upgrade
    "UpgradeType",
    "UpgradePolicy",
    "UpgradeExecution",
    # Drift Detection
    "DriftDetection",
    "DriftReport",
    "DriftRemediation",
    # Technical Debt
    "DebtClassification",
    "DebtPriority",
    "DebtMetrics",
    # Metrics
    "EvolutionMetrics",
    "RepositoryEvolutionScore",
]