# Salience Network State Package
# ==============================
#
# Canonical implementation of immutable State components (Phase 4.8.4).
#

"""
Salience Network State Model.

This package defines the canonical immutable State architecture of the Salience
Network as established in Phase 4.8.4.

ARCHITECTURAL PRINCIPLES:
    - Immutability: All public State objects are deeply frozen dataclasses
    - Representational: State describes, never computes or executes
    - External Authority: Subsystem ownership is preserved through references
    - Deterministic: Serialization and validation are reproducible

PUBLIC API:
    SalienceNetworkState      Aggregate State representing complete snapshot
    SalienceSnapshotKind      Snapshot semantic kind (CURRENT, CANDIDATE, etc.)
    SalienceLevel             Salience significance levels
    SalienceActivationStatus  Activation status categories
    SalienceReadiness         Readiness for downstream consumption
    SaliencePersistenceKind   Persistence classification
    SalienceDecayKind         Decay classification
    SalienceCompetitionStatus Competition resolution status
    
    Validation functions:
        validate_salience_state    Full State validation
        validate_identity          Identity format validation
        validate_revision          Revision range validation
        
    Exceptions:
        SalienceStateValidationError  Raised for construction failures

COMPONENT MODULES:
    enums.py      Semantic enum definitions
    subject.py    Subject reference representation
    assessment.py Multi-dimensional salience assessment
    activation.py Activation status and basis
    readiness.py  Downstream consumption readiness
    evidence.py   Evidence composition references
    uncertainty.py Semantic uncertainty representation
    context.py    External context projections
    persistence.py Expected semantic continuity
    decay.py      Expected semantic loss classification
    competition.py Multiple candidate relationships
    integrity.py  Validation findings and result model
    aggregate.py  Canonical SalienceNetworkState definition
    validation.py Validation framework
"""

from __future__ import annotations

# Expose enums for public use
from .enums import (
    SalienceSnapshotKind,
    SalienceLevel,
    SalienceActivationStatus,
    SalienceReadiness,
    SaliencePersistenceKind,
    SalienceDecayKind,
    SalienceCompetitionStatus,
    ValidationSeverity,
)

# Expose subject reference
from .subject import SalienceSubjectReference

# Expose assessment components
from .assessment import (
    SignificanceDescriptor,
    RelevanceDescriptor,
    NoveltyDescriptor,
    UrgencyDescriptor,
    UncertaintyDescriptor,
    ConflictDescriptor,
    PredictionErrorDescriptor,
    MotivationalSalienceDescriptor,
    ContextualSalienceDescriptor,
    ConfidenceDescriptor,
    SalienceAssessmentState,
)

# Expose activation, readiness, evidence, uncertainty, context
from .activation import SalienceActivationState
from .readiness import SalienceReadinessState
from .evidence import SalienceEvidence, SalienceEvidenceState
from .uncertainty import SalienceUncertaintyState
from .context import SalienceContextEntry, SalienceContextState

# Expose persistence and decay
from .persistence import SaliencePersistenceState
from .decay import SalienceDecayState

# Expose competition
from .competition import SalienceCandidateReference, SalienceCompetitionState

# Expose integrity findings
from .integrity import SalienceStateFinding, SalienceStateValidationResult

# Expose aggregate State (canonical root)
from .aggregate import (
    SalienceStateProvenance,
    SalienceStateLineage,
    SalienceNetworkState,
)

# Expose validation functions and exception
from .validation import (
    validate_salience_state,
    validate_identity,
    validate_revision,
    validate_enum,
    SalienceStateValidationError,
)

__all__ = [
    # Enums
    "SalienceSnapshotKind",
    "SalienceLevel",
    "SalienceActivationStatus",
    "SalienceReadiness",
    "SaliencePersistenceKind",
    "SalienceDecayKind",
    "SalienceCompetitionStatus",
    "ValidationSeverity",
    # Subject reference
    "SalienceSubjectReference",
    # Assessment components
    "SignificanceDescriptor",
    "RelevanceDescriptor",
    "NoveltyDescriptor",
    "UrgencyDescriptor",
    "UncertaintyDescriptor",
    "ConflictDescriptor",
    "PredictionErrorDescriptor",
    "MotivationalSalienceDescriptor",
    "ContextualSalienceDescriptor",
    "ConfidenceDescriptor",
    "SalienceAssessmentState",
    # State components
    "SalienceActivationState",
    "SalienceReadinessState",
    "SalienceEvidence",
    "SalienceEvidenceState",
    "SalienceUncertaintyState",
    "SalienceContextEntry",
    "SalienceContextState",
    "SaliencePersistenceState",
    "SalienceDecayState",
    "SalienceCandidateReference",
    "SalienceCompetitionState",
    # Integrity
    "SalienceStateFinding",
    "SalienceStateValidationResult",
    # Aggregate State (canonical root)
    "SalienceStateProvenance",
    "SalienceStateLineage",
    "SalienceNetworkState",
    # Validation
    "validate_salience_state",
    "validate_identity",
    "validate_revision",
    "validate_enum",
    "SalienceStateValidationError",
]

__version__ = "1.0.0"
"""Salience State Model version."""