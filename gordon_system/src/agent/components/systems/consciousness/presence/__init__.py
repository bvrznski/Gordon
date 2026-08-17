# Gordon Phase 5.7.5-I: Presence Engine Package
# ===============================================================================
"""
Canonical Presence Engine for conscious accessibility.

This package implements:
    - Presence Engine (canonical): Main engine class for presence management
    - Constants: State constants, policy constants
    - State model: PresenceItem and PresenceStateSnapshot classes
    - Admission: Deterministic admission authority with policy checks
    - Persistence: Bounded lifetime tracking for content
    - Fading: Gradual withdrawal mechanism (weakening → fading → withdrawn)
    - Transitions: Immutable transition records for replayability
    - Snapshots: Immutable publications of presence state
    - Diagnostics: Metrics collection and health monitoring
    - Integrity: State consistency validation

Integration:
    - Experiential Field → proposes candidates
    - Intentional Context → targets content
    - Temporal Context → provides timing

Responsibilities (YES):
    - Admit candidate content according to policy
    - Track lifecycle state transitions
    - Manage fading progress
    - Publish immutable snapshots
    - Collect metrics and health data

NOT responsible for (NO):
    - Content evaluation or reasoning
    - Attention computation
    - Salience computation
    - Memory storage/retrieval
    - Planning or execution
"""

from .constants import (
    PRESENCE_STATE_CANDIDATE,
    PRESENCE_STATE_ADMITTED,
    PRESENCE_STATE_ACTIVE,
    PRESENCE_STATE_WEAKENING,
    PRESENCE_STATE_FADING,
    PRESENCE_STATE_SUSPENDED,
    PRESENCE_STATE_WITHDRAWN,
    VALID_PRESENCE_STATES,
    ADMISSION_POLICY_SOURCE_VALIDATION,
    ADMISSION_POLICY_FRESHNESS_CHECK,
    ADMISSION_POLICY_CAPACITY_LIMIT,
    VALID_ADMISSION_POLICIES,
)

from gordon.agent.components.systems.consciousnessstate import (
    PresenceItem,
    PresenceStateSnapshot,
)

from .exceptions import (
    PresenceError,
    InvalidAdmission,
    InvalidWithdrawal,
    TransitionConflict,
    PublicationFailure,
    SnapshotCorruption,
    InvalidStateTransition,
    CapacityExceeded,
)

from gordon.agent.components.systems.consciousnessadmission import (
    AdmissionAuthority,
    AdmissionPolicy,
)

from gordon.agent.components.systems.consciousnesspersistence import (
    PersistenceManager,
    PersistencePolicy,
)

from gordon.agent.components.systems.consciousnessfading import (
    FadingManager,
    FadePolicy,
)

from gordon.agent.components.systems.consciousnesstransition import (
    PresenceTransition,
    TransitionBatch,
)

from gordon.agent.components.systems.consciousnesssnapshot import (
    PresenceSnapshot,
)

from gordon.agent.components.systems.consciousnessdiagnostics import (
    Diagnostics,
    PresenceMetrics,
    HealthStatus,
)

from gordon.agent.components.systems.consciousnessintegrity import (
    IntegrityEnforcer,
    IntegrityCheckResult,
)

from gordon.agent.components.systems.consciousnessengine import (
    PresenceEngine,
)


__all__ = (
    # Constants
    "PRESENCE_STATE_CANDIDATE",
    "PRESENCE_STATE_ADMITTED",
    "PRESENCE_STATE_ACTIVE",
    "PRESENCE_STATE_WEAKENING",
    "PRESENCE_STATE_FADING",
    "PRESENCE_STATE_SUSPENDED",
    "PRESENCE_STATE_WITHDRAWN",
    "VALID_PRESENCE_STATES",
    "ADMISSION_POLICY_SOURCE_VALIDATION",
    "ADMISSION_POLICY_FRESHNESS_CHECK",
    "ADMISSION_POLICY_CAPACITY_LIMIT",
    "VALID_ADMISSION_POLICIES",
    
    # State
    "PresenceItem",
    "PresenceStateSnapshot",
    
    # Exceptions
    "PresenceError",
    "InvalidAdmission",
    "InvalidWithdrawal",
    "TransitionConflict",
    "PublicationFailure",
    "SnapshotCorruption",
    "InvalidStateTransition",
    "CapacityExceeded",
    
    # Core components
    "AdmissionAuthority",
    "AdmissionPolicy",
    "PersistenceManager",
    "PersistencePolicy",
    "FadingManager",
    "FadePolicy",
    "PresenceTransition",
    "TransitionBatch",
    "PresenceSnapshot",
    
    # Diagnostics & Integrity
    "Diagnostics",
    "PresenceMetrics",
    "HealthStatus",
    "IntegrityEnforcer",
    "IntegrityCheckResult",
    
    # Main engine (canonical)
    "PresenceEngine",
)