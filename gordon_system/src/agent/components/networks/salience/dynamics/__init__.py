# Salience Network Dynamic Updates Package
# =========================================
#
# Canonical implementation of adaptive salience dynamics (Phase 4.8.7).
#
"""
Adaptive Salience Dynamics.

This package defines the temporal evolution layer of the Salience Network,
implementing accumulation, decay, habituation, sensitization, fatigue,
recovery, context adaptation, persistence, and stability evolution.

ARCHITECTURAL PRINCIPLES:
    - Immutability: All public objects are deeply frozen dataclasses
    - Semantic time only: No datetime.now() or system clock access
    - Deterministic: Equivalent inputs always produce equivalent outputs
    - Side-effect free: Pure updates with immutable results

PUBLIC API:
    DynamicUpdateRequest  Request for temporal evolution
    DynamicUpdateResult   Result of temporal evolution
    DynamicPolicy         Policy configuration for dynamics
    
    AdaptiveState         Current adaptive descriptors per Candidate
    TemporalTrace         Structural trace of applied operations
    
    validate_request      Validate an update request
    apply_dynamics        Apply temporal evolution to Candidates

COMPONENT MODULES:
    _request.py       Update request model
    _result.py        Update result model
    _policy.py        Policy configuration
    accumulation.py   Accumulation evolution
    decay.py          Decay evolution  
    habituation.py    Habituation evolution
    sensitization.py  Sensitization evolution
    fatigue.py        Fatigue evolution
    recovery.py       Recovery evolution
    context.py        Context adaptation
    persistence.py    Persistence evolution
    stability.py      Stability evolution
    trace.py          Temporal trace model
    validation.py     Validation functions

PHASE 4.8.7 INVARIANTS:
    DYNAMICS-INV-001: Exactly one canonical DynamicUpdateRequest class exists
    DYNAMICS-INV-002: Request is immutable (frozen dataclass)
    DYNAMICS-INV-003: Semantic time delta is supplied externally
    DYNAMICS-INV-004: No wall-clock access occurs
    DYNAMICS-INV-005: No runtime scheduling occurs
    DYNAMICS-INV-006: Equivalent inputs produce equivalent outputs
"""

from __future__ import annotations

# Expose request and result
from ._request import DynamicUpdateRequest, DynamicDeltaKind
from ._result import DynamicUpdateResult, DynamicFindingKind, DynamicStatus

# Expose policy
from ._policy import (
    AccumulationPolicy,
    DecayPolicy,
    DecayCurve,
    HabituationPolicy,
    SensitizationPolicy,
    FatiguePolicy,
    RecoveryPolicy,
    ContextAdaptationPolicy,
    PersistencePolicy,
    StabilityPolicy,
    DynamicPolicy,
)

# Expose adaptive state models
from ._state import (
    AccumulationState,
    DecayState,
    HabituationState,
    SensitizationState,
    FatigueState,
    RecoveryState,
    PersistenceState,
    StabilityState,
    AdaptiveCandidateState,
    CandidateAdaptiveDeltas,
)

# Expose trace model
from ._trace import TemporalTrace, TraceCode

# Expose validation
from ._validation import validate_request, validate_candidates

__all__ = [
    # Request and result
    "DynamicUpdateRequest",
    "DynamicDeltaKind",
    "DynamicUpdateResult",
    "DynamicFindingKind",
    "DynamicStatus",
    # Policy
    "AccumulationPolicy",
    "DecayPolicy",
    "DecayCurve",
    "HabituationPolicy",
    "SensitizationPolicy",
    "FatiguePolicy",
    "RecoveryPolicy",
    "ContextAdaptationPolicy",
    "PersistencePolicy",
    "StabilityPolicy",
    "DynamicPolicy",
    # Adaptive state
    "AccumulationState",
    "DecayState",
    "HabituationState",
    "SensitizationState",
    "FatigueState",
    "RecoveryState",
    "PersistenceState",
    "StabilityState",
    "AdaptiveCandidateState",
    "CandidateAdaptiveDeltas",
    # Trace
    "TemporalTrace",
    "TraceCode",
    # Validation
    "validate_request",
    "validate_candidates",
]

__version__ = "1.0.0"
"""Dynamic Updates package version."""