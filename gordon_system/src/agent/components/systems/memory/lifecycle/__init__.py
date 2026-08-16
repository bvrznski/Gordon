# Memory Lifecycle - Phase 5.1.4 Canonical Lifecycle System
# ===========================================================
"""
Memory Lifecycle: The state machine governing Memory Artifact existence.

This module implements the lifecycle system as specified in Phase 5.1.4 of the
Gordon Cognitive Architecture.

Architecture Summary:
    ┌────────────────────────────────────────────────────────────────────┐
    │                    MEMORY LIFECYCLE                                │
    ├────────────────────────────────────────────────────────────────────┤
    │                                                                    │
    │   owns                                                             │
    │   └── MemoryArtifact lifecycle state and transitions             │
    │                                                                    │
    │   depends on                                                       │
    │       ├── Foundation (Memory Artifact, Identity, Provenance)     │
    │       ├── Validation (validation rules)                          │
    │       └── Contract system (transition contracts)                 │
    │                                                                    │
    │   provides                                                         │
    │       ├── LifecycleState (CANDIDATE, ACTIVE, RETAINED, etc.)     │
    │       ├── State transitions (validated, recorded, reversible)    │
    │       ├── History tracking (immutable transition records)        │
    │       └── Diagnostics and observability                          │
    │                                                                    │
    └────────────────────────────────────────────────────────────────────┘

Core Principles:
    - Lifecycle owns existence state
    - Lifecycle never owns semantic content
    - Transitions are explicit, validated, and recorded
    - History is immutable and inspectable
    - Failures are recoverable when possible

Lifecycle Laws (LIFECYCLE-LAW-XXX):
    LIFECYCLE-LAW-001: Every Memory Artifact has exactly one Lifecycle
    LIFECYCLE-LAW-002: Lifecycle begins only after successful admission
    LIFECYCLE-LAW-003: Lifecycle preserves artifact identity
    LIFECYCLE-LAW-004: Lifecycle preserves provenance
    LIFECYCLE-LAW-005: Lifecycle preserves revision history
    LIFECYCLE-LAW-006: Lifecycle transitions are explicit
    LIFECYCLE-LAW-007: Lifecycle is independently testable
    LIFECYCLE-LAW-008: Lifecycle behavior is deterministic

Canonical State Transitions:
    CANDIDATE → ACTIVE          (Admission complete)
    ACTIVE → RETAINED           (Retention policy positive)
    RETAINED → ARCHIVED         (Archival decision)
    ACTIVE → SUPERSEDED         (New revision created)
    ACTIVE → FAILED             (Validation failure)
    FAILED → RECOVERING         (Recovery attempt)
    RECOVERING → ACTIVE         (Recovery successful)
    RECOVERING → FAILED         (Recovery failed)

See Also:
    - states.py: State definitions and state machine
    - contracts.py: Transition contracts
    - history.py: Lifecycle history tracking
"""

from __future__ import annotations

# Re-export core components for convenience
from .states import (
    LifecycleState,
    TransitionType,
    TransitionTrigger,
    LifecycleTransitionRecord,
    LifecycleStateMachine,
    LifecycleStatistics,
)

from .contracts import (
    ContractType,
    AdmissionContract,
    ActivationContract,
    RetentionContract,
    ArchivalContract,
    SupersessionContract,
    FailureContract,
    RecoveryContract,
)

__all__ = [
    # States
    "LifecycleState",
    "TransitionType",
    "TransitionTrigger",
    "LifecycleTransitionRecord",
    "LifecycleStateMachine",
    "LifecycleStatistics",
    
    # Contracts
    "ContractType",
    "AdmissionContract",
    "ActivationContract",
    "RetentionContract",
    "ArchivalContract",
    "SupersessionContract",
    "FailureContract",
    "RecoveryContract",
]

# Version information
__version__ = "1.0.0"
__phase__ = "5.1.4"