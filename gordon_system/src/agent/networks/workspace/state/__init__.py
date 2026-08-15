# Workspace State Module
# ======================

"""
Canonical WorkspaceState semantic model.

This module defines the complete semantic architecture for Workspace State in Phase 4.6.8.
All types are immutable, deterministic, and runtime-neutral.

EXPORTS
-------

Core Types:
    - WorkspaceStateIdentity: Unique identifier for a workspace state
    - WorkspaceStateRevision: Revision number for workspace states
    - WorkspaceStateReference: Reference to a workspace state
    - WorkspaceStateSnapshot: Bounded snapshot of workspace state

State Model:
    - WorkspaceState: Complete semantic representation of workspace state
    - WorkspaceStateDelta: Immutable record of state changes
    - StateDeltaOperation: Single atomic operation in a delta
    - DeltaApplicationResult: Result of applying a delta

Transition:
    - TransitionIdentity: Unique identifier for a transition
    - TransitionEvidence: Evidence supporting a transition
    - WorkspaceStateTransition: Complete record of state transition
    - TransitionChain: Chain of consecutive transitions

Continuity:
    - ContinuationContext: Context for semantic continuation
    - ContinuationHistoryEntry: Record of continuity event
    - WorkspaceContinuity: Semantic model of workspace continuity
    - ContinuityViolation: Record of continuity violation

History:
    - HistoryRecord: Single record in the history log
    - InvalidationRecord: Record of invalidation event
    - WorkspaceHistory: Append-only history of all events

Lineage:
    - LineageNode: Node in the semantic lineage graph
    - LineagePath: Path through the lineage graph
    - WorkspaceLineage: Complete lineage record for a state

Persistence:
    - PersistenceEligibility: Record of persistence eligibility
    - PersistenceScope: Scope of persistence for a state
    - PersistenceAuthority: Authority for persistence operations
    - PersistenceRecord: Record of a persistence operation

Restoration:
    - RestorationCandidate: Candidate for restoration from storage
    - RestorationRequest: Request to restore a workspace state
    - RestorationValidation: Validation of a restoration attempt
    - RestorationOutcome: Result of a restoration operation

Consistency:
    - SemanticConsistency: Semantic consistency record
    - RevisionConsistency: Revision chain consistency record
    - LineageConsistency: Lineage chain consistency record
    - DependencyConsistency: Dependency chain consistency record
    - ProvenanceConsistency: Provenance chain consistency record
    - OwnershipConsistency: Ownership boundary consistency record
    - AuthorityConsistency: Authority boundary consistency record
    - ConsistencyResult: Complete consistency result

Certification:
    - CertificationIdentity: Unique identifier for certification
    - CertificationEvidence: Evidence supporting certification
    - ValidationResult: Result of a validation check
    - WorkspaceCertification: Complete certification of workspace state
    - CertifiedWorkspaceState: Final, certified workspace state artifact

ARCHITECTURAL LAWS
------------------
1. Workspace State is immutable.
2. State revisions are append-only (strictly monotonic).
3. Transitions preserve provenance.
4. Snapshots preserve lineage.
5. History is append-only.
6. No runtime state enters semantic Workspace State.
7. Workspace State never owns runtime resources.
8. Persistence remains external.
9. Certification never mutates Workspace State.

ARCHITECTURAL INVARIANTS
------------------------
1. Every State has one Identity.
2. Every Revision belongs to one State.
3. Every Delta belongs to one Revision chain.
4. Every Transition references previous and next State.
5. Every Snapshot references one State Revision.
6. Every Certified State references one Certification.
7. Lineage is acyclic.
8. History is append-only.

PHASE 4.6.8 COMPLETE
====================
"""

from __future__ import annotations

# Identity types
from .identity import (
    WorkspaceStateIdentity,
    WorkspaceStateRevision,
    WorkspaceStateReference,
)

# Model types
from .model import (
    WorkspaceCandidateReference,
    WorkspaceStateSnapshot,
    WorkspaceState,
)

# Delta types
from .delta import (
    WorkspaceStateDeltaIdentity,
    StateDeltaOperation,
    WorkspaceStateDelta,
    DeltaApplicationResult,
)

# Transition types
from .transition import (
    TransitionIdentity,
    TransitionEvidence,
    WorkspaceStateTransition,
    TransitionChain,
)

# Continuity types
from .continuity import (
    ContinuationContext,
    ContinuationHistoryEntry,
    WorkspaceContinuity,
    ContinuityViolation,
)

# History types
from .history import (
    HistoryRecord,
    InvalidationRecord,
    WorkspaceHistory,
)

# Lineage types
from .lineage import (
    LineageNode,
    LineagePath,
    WorkspaceLineage,
)

# Persistence types
from .persistence import (
    PersistenceEligibility,
    PersistenceScope,
    PersistenceAuthority,
    PersistenceRecord,
)

# Restoration types
from .restoration import (
    RestorationCandidate,
    RestorationRequest,
    RestorationValidation,
    RestorationOutcome,
)

# Consistency types
from .consistency import (
    SemanticConsistency,
    RevisionConsistency,
    LineageConsistency,
    DependencyConsistency,
    ProvenanceConsistency,
    OwnershipConsistency,
    AuthorityConsistency,
    ConsistencyResult,
)

# Certification types
from .certification import (
    CertificationIdentity,
    CertificationEvidence,
    ValidationResult,
    WorkspaceCertification,
    CertifiedWorkspaceState,
)

__all__: tuple[str, ...] = (
    # Identity types
    "WorkspaceStateIdentity",
    "WorkspaceStateRevision",
    "WorkspaceStateReference",
    # Model types
    "WorkspaceCandidateReference",
    "WorkspaceStateSnapshot",
    "WorkspaceState",
    # Delta types
    "WorkspaceStateDeltaIdentity",
    "StateDeltaOperation",
    "WorkspaceStateDelta",
    "DeltaApplicationResult",
    # Transition types
    "TransitionIdentity",
    "TransitionEvidence",
    "WorkspaceStateTransition",
    "TransitionChain",
    # Continuity types
    "ContinuationContext",
    "ContinuationHistoryEntry",
    "WorkspaceContinuity",
    "ContinuityViolation",
    # History types
    "HistoryRecord",
    "InvalidationRecord",
    "WorkspaceHistory",
    # Lineage types
    "LineageNode",
    "LineagePath",
    "WorkspaceLineage",
    # Persistence types
    "PersistenceEligibility",
    "PersistenceScope",
    "PersistenceAuthority",
    "PersistenceRecord",
    # Restoration types
    "RestorationCandidate",
    "RestorationRequest",
    "RestorationValidation",
    "RestorationOutcome",
    # Consistency types
    "SemanticConsistency",
    "RevisionConsistency",
    "LineageConsistency",
    "DependencyConsistency",
    "ProvenanceConsistency",
    "OwnershipConsistency",
    "AuthorityConsistency",
    "ConsistencyResult",
    # Certification types
    "CertificationIdentity",
    "CertificationEvidence",
    "ValidationResult",
    "WorkspaceCertification",
    "CertifiedWorkspaceState",
)