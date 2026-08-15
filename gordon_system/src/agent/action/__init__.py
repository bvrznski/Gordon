# Gordon Cognitive Architecture - Phase 4.5.13
# ===========================================
#
# Legacy Action Selection Network Compatibility Shim
#
# This package is deprecated as of Phase 4.5.13.
# The canonical package has been renamed to `decision_network`.
#
# This module re-exports all symbols from the new canonical location
# for backward compatibility during migration.
#
# MIGRATION:
#   Old: from gordon_system.src.agent.action import ...
#   New: from gordon_system.src.agent.decision_network import ...

"""
Legacy Action Selection Network Compatibility Shim

This package was renamed to Decision Network in Phase 4.5.13.
All functionality has been migrated to:
    gordon_system.src.agent.decision_network

The canonical Decision Network subsystem owns:
    - Action Selection process (internal naming preserved)
    - Candidate generation semantics
    - Evaluation and Arbitration
    - Final Action Selection stage
    - Selected Action production
    - State management
    - Coordination contracts
    - Serialization and validation

Action Selection terminology remains valid for internal processes:
    ActionSelectionRequest, ActionSelectionOutcome, 
    ActionSelectionFrontier, SelectedAction, etc.

See Phase 4.5.13 documentation for full renaming rationale.
"""

# Re-export all canonical symbols from new location
from gordon_system.src.agent.decision_network import (
    IdentityKind,
    IdentityVersion,
    ActionIdentity,
    ActionReference,
    CanonicalActionReference,
    ExternalActionReference,
    WeakActionReference,
    ActionRevisionReference,
    ActionRevisionMetadata,
    TransitionKind,
    ActionDelta,
    ActionTransition,
    ActionContinuation,
    ActionReplacement,
    ActionSupersession,
    ActionHistory,
    ActionLineage,
    VersionMatrix,
    VersionRelationship,
    VersionEquivalence,
    VersionProjection,
    ValidationResult,
)

__all__ = [
    # Identity types
    "IdentityKind",
    "IdentityVersion",
    "ActionIdentity",
    "ActionReference",
    "CanonicalActionReference",
    "ExternalActionReference",
    "WeakActionReference",
    "ActionRevisionReference",
    "ActionRevisionMetadata",
    # Lineage types
    "TransitionKind",
    "ActionDelta",
    "ActionTransition",
    "ActionContinuation",
    "ActionReplacement",
    "ActionSupersession",
    "ActionHistory",
    "ActionLineage",
    # Version types
    "VersionMatrix",
    "VersionRelationship",
    "VersionEquivalence",
    "VersionProjection",
    # Validation types
    "ValidationResult",
]

__deprecated__ = True
__canonical_module__ = "gordon_system.src.agent.decision_network"