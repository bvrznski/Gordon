# Gordon Cognitive Architecture - Phase 4.5.1
# ===========================================

"""
Action Selection Subsystem - Action Semantics

This module defines the canonical semantic architecture for representing possible
operations in the Gordon autonomous cognitive agent.

CANONICAL DEFINITION
====================

An Action is an immutable semantic description of a bounded operation that may be
performed by an authorized capability against an explicit subject or target in
order to produce intended effects under declared preconditions, constraints,
authority, and operational context.

Action is NOT:
    - The operation occurring (that's execution)
    - A runtime process (runtime state belongs elsewhere)
    - An effect (effects are outcomes of execution)
    - An outcome (outcomes interpret effects against goals)
    - A tool invocation (tool invocations realize Actions)
    - A mutable instruction object (Actions are immutable descriptions)

ARCHITECTURE
============

SemanticObject (base concept)
    ↓
ActionArtifact (semantic root for all Action-related types)
    ├── Action (the primary artifact - describes possible operation)
    │   ├── Identity: unique identifier across revisions
    │   ├── Revision: version tracking with history preservation
    │   ├── Subject: what the action serves
    │   ├── Target: what the action operates on
    │   ├── Purpose: why the action exists
    │   ├── Kind: semantic category of operation
    │   ├── Modality: state change behavior
    │   ├── Context: bounded environment
    │   └── Lifecycle: semantic position in existence
    │
    ├── ActionReference (reference to a specific Action revision)
    ├── ActionRevision (semantic update record for one identity)
    ├── ActionContext (bounded semantic environment)
    ├── ActionScope (explicit bounds on the action)
    └── ... other semantic artifacts

ARCHITECTURAL LAWS
==================

ACTION-SEM-LAW-001: An Action is an immutable semantic representation of a possible
                    bounded operation. It never performs, schedules, dispatches,
                    or supervises its own execution.

ACTION-SEM-LAW-002: Action Identity is distinct from Execution Attempt Identity.

ACTION-SEM-LAW-003: Action Revision never overwrites prior revisions.

ACTION-SEM-LAW-004: Action is distinct from Decision, Plan, Selection, Execution,
                    Effect, and Outcome.

ACTION-SEM-LAW-005: Every Action has explicit bounded scope.

ACTION-SEM-LAW-006: Every Action has explicit ownership and authority requirements.

ACTION-SEM-LAW-007: Every Action preserves target identity and revision where applicable.

ACTION-SEM-LAW-008: Preconditions and Postconditions are semantic propositions
                    and do not evaluate themselves.

ACTION-SEM-LAW-009: Intended Effects are distinct from observed Effects.

ACTION-SEM-LAW-010: Side Effects are distinct from primary Effects and Risks.

ACTION-SEM-LAW-011: Action requirements do not allocate resources or invoke capabilities.

ACTION-SEM-LAW-012: Policy and Security constraints remain externally authoritative.

ACTION-SEM-LAW-013: Reversibility, rollback, compensation, idempotency, and
                    retryability remain distinct.

ACTION-SEM-LAW-014: Action semantics contain no runtime handles or executable callbacks.

ACTION-SEM-LAW-015: Action lifecycle excludes Execution runtime states.

ACTION-SEM-LAW-016: Action semantic artifacts are deeply immutable.

ACTION-SEM-LAW-017: Equivalent semantic inputs produce equivalent Action representations.

ACTION-SEM-LAW-018: Action semantic collections are explicitly bounded.

ACTION-SEM-LAW-019: Action semantic time is externally supplied.

ACTION-SEM-LAW-020: Package import performs no runtime work.

OWNERSHIP
=========

Action Selection Subsystem owns:
    - Canonical Action semantics
    - Action Identity model
    - Action Revision model
    - Action taxonomy (purpose, kind, modality, etc.)
    - Action Context and Scope models
    - Preconditions and Postconditions models
    - Effects and Side Effects models
    - Requirements and Constraints models
    - Dependencies and Assumptions models
    - Evidence and Justification models
    - Risk and Reversibility semantics
    - Lifecycle semantics (before execution)
    - Validation logic for semantic contracts

Action Selection Subsystem does NOT own:
    - Goal definition
    - Strategy formulation
    - Plan construction
    - Executive Decision making
    - Action candidate generation
    - Action selection algorithm
    - Runtime execution
    - Effector invocation
    - Tool implementation
    - Policy or Security rules

IMPORT SAFETY
=============

This package is designed to be import-safe:
    - No filesystem access during import
    - No network access during import
    - No model loading during import
    - No runtime initialization during import
    - No random identity generation during import
    - No wall-clock acquisition during import

All construction is deterministic given identical semantic inputs.
"""

__all__ = [
    # Identity types (identities.py)
    "IdentityKind",
    "IdentityVersion",
    "ActionIdentity",
    "ActionReference",
    "CanonicalActionReference",
    "ExternalActionReference",
    "WeakActionReference",
    "ActionRevisionReference",
    "ActionRevisionMetadata",
    
    # Lineage types (lineage.py)
    "TransitionKind",
    "ActionDelta",
    "ActionTransition",
    "ActionContinuation",
    "ActionReplacement",
    "ActionSupersession",
    "ActionHistory",
    "ActionLineage",
    
    # Version types (versions.py)
    "VersionMatrix",
    "VersionRelationship",
    "VersionEquivalence",
    "VersionProjection",
    
    # Validation types (validation/__init__.py)
    "ValidationResult",
]

# Exports for Phase 4.5.2 - Action Identity Architecture
# =======================================================

# Import all public symbols from submodules
from .identities import (
    IdentityKind,
    IdentityVersion,
    ActionIdentity,
    ActionReference,
    CanonicalActionReference,
    ExternalActionReference,
    WeakActionReference,
    ActionRevisionReference,
    ActionRevisionMetadata,
)

from .lineage import (
    TransitionKind,
    ActionDelta,
    ActionTransition,
    ActionContinuation,
    ActionReplacement,
    ActionSupersession,
    ActionHistory,
    ActionLineage,
)

from .versions import (
    VersionMatrix,
    VersionRelationship,
    VersionEquivalence,
    VersionProjection,
)

from .validation import ValidationResult