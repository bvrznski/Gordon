# Gordon Cognitive Architecture - Phase 4.5.2 Action Tree

"""
Action Selection Subsystem - Tree Structure Documentation

This module documents the hierarchical organization of Action artifacts.

ACTION TREE
===========

ActionArtifact (base concept)
    ↓
Action (semantic operation description)
    ├── Identity: ActionIdentity - unique identifier across revisions
    │   ├── ActionReference - reference to an Action
    │   │   ├── CanonicalActionReference - current authoritative version
    │   │   ├── ExternalActionReference - reference from external system
    │   │   └── WeakActionReference - non-owning cache reference
    │   └── ActionRevisionReference - lightweight revision reference
    ├── Revision: ActionRevision - semantic update record
    │   ├── ActionContinuation - continues identity with new revision
    │   ├── ActionReplacement - replaces previous revision (traceable)
    │   └── ActionSupersession - supersedes previous revision (stronger)
    ├── Subject: what the action serves
    ├── Target: what the action operates on
    ├── Purpose: why the action exists
    ├── Kind: semantic category of operation (ActionKind enum)
    ├── Modality: state change behavior (ActionModality enum)
    └── Lifecycle: semantic position in existence (ActionLifecycleState enum)

    ↓
ActionLineage - immutable history graph for one identity
    ├── ActionHistory - append-only log of all changes
    ├── ActionDelta - record of changes between revisions
    ├── ActionTransition - state transition event
    ├── Continuation chain - valid revision sequence
    └── Replacement/Supersession relationships

    ↓
Versioning Dimensions (separate concerns)
    ├── IdentityVersion - canonical semantic version number
    ├── SemanticRevision - major/minor/patch for semantic changes
    ├── SchemaVersion - data structure format version
    ├── SerializationVersion - wire format version
    └── MigrationVersion - migration compatibility tracking

VALIDATION
==========

ValidationResult - validation operation result
    ├── is_valid: whether validation passed
    ├── errors: list of error messages
    └── warnings: list of warning messages

ARCHITECTURAL INVARIANTS
========================

1. ActionIdentity is immutable and never regenerated
2. Revision history is acyclic and append-only  
3. References never embed runtime handles or objects
4. Deterministic reconstruction from serialized form
5. Migration preserves conceptual identity
6. Equivalence is context-dependent and explicit

ARCHITECTURAL LAWS (ACTION-ID-LAW-XXX)
=======================================

ACTION-ID-LAW-001: Every Action owns exactly one ActionIdentity.
ACTION-ID-LAW-002: ActionIdentity survives semantic revisions.
ACTION-ID-LAW-003: Revisions never overwrite history.
ACTION-ID-LAW-004: ExecutionAttempt never becomes ActionIdentity.
ACTION-ID-LAW-005: Identity continuity is explicit.
ACTION-ID-LAW-006: Identity relationships are immutable.
ACTION-ID-LAW-007: Replay never creates new identities.
ACTION-ID-LAW-008: Migration never changes conceptual identity.
ACTION-ID-LAW-009: Replacement never mutates previous identity.
ACTION-ID-LAW-010: History is append-only.

FILES
=====

identities.py   - Core identity types (ActionIdentity, IdentityVersion, etc.)
lineage.py      - Lineage graph types (ActionLineage, ActionHistory, transitions)
versions.py     - Versioning dimensions (VersionMatrix, relationships)
validation/     - Validation module (ValidationResult)

PACKAGE IMPORT SAFETY
=====================

No runtime initialization during import.
No filesystem access during import.
No network access during import.
No random identity generation during import.

All construction is deterministic given identical semantic inputs.
"""

__all__ = []