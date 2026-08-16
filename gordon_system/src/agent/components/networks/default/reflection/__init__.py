# Default Network - Reflection Coordination Package
# ================================================

"""
Reflection coordination layer for the Default Network.

This package implements bounded, immutable coordination of internally
generated reflection activities. It provides:

    • Immutable request models (ReflectionRequest, scope, purpose, subject)
    • Episode specialization (ReflectionEpisode reusing InternalEpisode)
    • Planning support (declarative plan steps)
    • Capability contracts (request/result boundaries)
    • Evidence model with contradiction tracking
    • Reflective products (insights, patterns, assumptions, etc.)
    • Outcomes and continuation recommendations
    • Recursion safeguards
    • State tracking with bounded history
    
ARCHITECTURAL PRINCIPLES:
    1. Reflection coordination is distinct from reflection computation
    2. All contracts are deeply immutable
    3. No runtime references in domain models
    4. All bounds are explicit and bounded
    5. State transitions are semantic records, not runtime actions
    
ARCHITECTURAL BOUNDARIES:
    • Does NOT implement reflective algorithms (outsourced to capabilities)
    • Does NOT mutate memory, identity, narrative, or learning systems
    • Does NOT schedule execution or allocate resources
    • Does NOT own runtime progression (ExecutionLoop does that)
"""

from __future__ import annotations

# Main reflection models
from .request import ReflectionRequest, ReflectionRequestId
from .purpose import ReflectionPurpose
from .subject import ReflectionSubject
from .scope import ReflectionScope
from .episode import ReflectionEpisode

# Plan and steps
from .plan import ReflectionPlan, ReflectionStepKind, ReflectionPlanStep

# Enums (re-exports)
from .enums import (
    ReflectiveProductKind,
)

# Evidence
from .evidence import (
    ReflectionEvidence,
    EvidenceCategory,
)

# Products - re-export from products module
from .products import (
    ReflectiveProduct,
    InsightValidationStatus,
    InsightStructure,
    PatternStructure,
    AssumptionStructure,
)

# Outcomes and continuation
from .outcome import (
    ReflectionOutcome,
    ReflectionContinuation,
    ReflectionConfidence,
    ReflectionCompleteness,
    ReflectionCompletenessRecord,
)

# State
from .state.model import ReflectionCoordinationState

# Exceptions
from .exceptions import (
    ReflectionCoordinationError,
    InvalidReflectionRequest,
    InvalidReflectionPurpose,
    InvalidReflectionSubject,
    InvalidReflectionScope,
    ReflectionRecursionLimitExceeded,
    RepeatedReflectionRejected,
    ReflectionInvariantViolation,
    InvalidReflectionPlan,
    InvalidReflectionEvidence,
    InvalidReflectionOutcome,
)

# Configuration
from .configuration import (
    ReflectionCoordinationConfig,
)


__all__ = [
    # Core models
    "ReflectionRequest",
    "ReflectionRequestId",
    "ReflectionPurpose",
    "ReflectionSubject",
    "ReflectionScope",
    "ReflectionEpisode",
    
    # Planning
    "ReflectionPlan",
    "ReflectionStepKind",
    "ReflectionPlanStep",
    
    # Enums
    "ReflectiveProductKind",
    
    # Evidence
    "ReflectionEvidence",
    "EvidenceCategory",
    
    # Products
    "ReflectiveProduct",
    "InsightValidationStatus",
    "InsightStructure",
    "PatternStructure",
    "AssumptionStructure",
    
    # Outcomes and continuation
    "ReflectionOutcome",
    "ReflectionContinuation",
    "ReflectionConfidence",
    "ReflectionCompleteness",
    "ReflectionCompletenessRecord",
    
    # State
    "ReflectionCoordinationState",
    
    # Exceptions
    "ReflectionCoordinationError",
    "InvalidReflectionRequest",
    "InvalidReflectionPurpose",
    "InvalidReflectionSubject",
    "InvalidReflectionScope",
    "ReflectionRecursionLimitExceeded",
    "RepeatedReflectionRejected",
    "ReflectionInvariantViolation",
    "InvalidReflectionPlan",
    "InvalidReflectionEvidence",
    "InvalidReflectionOutcome",
    
    # Configuration
    "ReflectionCoordinationConfig",
]