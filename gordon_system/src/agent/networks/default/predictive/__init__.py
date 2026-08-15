# Default Network - Predictive Integration Package
# ================================================

"""
Predictive Integration coordination layer for the Default Network.

This package implements bounded, immutable coordination of internally generated
predictive cognition. It provides:

    • Immutable request models (PredictiveIntegrationRequest, scope, purpose, subject)
    • Episode specialization (PredictiveIntegrationEpisode reusing InternalEpisode)
    • Planning support (declarative plan steps)
    • Capability contracts (request/result boundaries)
    • Prediction structures with uncertainty and confidence
    • Expectation models and expectation-violation detection
    • Prediction-error representation and attribution
    • Revision proposals and monitoring proposals
    • Outcomes and continuation recommendations
    • Recurrence safeguards
    • State tracking with bounded history

ARCHITECTURAL PRINCIPLES:
    1. Predictive Integration is distinct from predictive computation
    2. All contracts are deeply immutable
    3. No runtime references in domain models
    4. All bounds are explicit and bounded
    5. State transitions are semantic records, not runtime actions

ARCHITECTURAL BOUNDARIES:
    • Does NOT implement prediction algorithms (outsourced to capabilities)
    • Does NOT mutate Memory, Identity, Narrative, or Executive state
    • Does NOT schedule execution or allocate resources
    • Does NOT own runtime progression (ExecutionLoop does that)
    • Does NOT directly invoke World Models or predictive models

PREDICTIVE INTEGRATION RESPONSIBILITIES:
    • Coordinating prediction projections and expectations
    • Integrating prediction errors and expectation violations
    • Comparing competing predictions and hypotheses
    • Assessing model applicability and limitations
    • Generating revision proposals and monitoring proposals
    • Composing predictive products and outcomes

PREDICTIVE INTEGRATION DOES NOT:
    • Run world models or forecasting algorithms
    • Acquire observations directly
    • Create MonitoringThreads
    • Schedule observations
    • Commit plans or select actions
    • Update Memory, Narrative, Identity, or Executive state
"""

from __future__ import annotations

# Main request models
from .request import (
    PredictiveIntegrationRequest,
    PredictiveIntegrationRequestId,
)
from .purpose import PredictiveIntegrationPurpose
from .subject import PredictiveSubject
from .scope import PredictiveIntegrationScope

# Episode and plan
from .episode import PredictiveIntegrationEpisode
from .plan import PredictiveIntegrationPlan, PredictiveCoordinationStepKind

# Prediction structures
from .prediction import (
    Prediction,
    PredictionKind,
    PredictionHorizon,
    PredictionAssumption,
)
from .hypothesis import PredictiveHypothesis

# Expectation structures
from .expectation import Expectation, ExpectedState, ExpectedEvent, ExpectedOutcome

# Assessment structures
from .probability import PredictionProbability
from .confidence import PredictionConfidence
from .uncertainty import PredictionUncertainty
from .applicability import PredictiveModelApplicabilityAssessment
from .limitation import PredictiveModelLimitation

# Error structures
from .error.prediction_error import PredictionError
from .error.expectation_violation import ExpectationViolation
from .error.surprise import PredictiveSurpriseAssessment
from .error.attribution import PredictionErrorAttribution
from .error.calibration import PredictionCalibrationAssessment

# Comparison and conflict
from .comparison import PredictionComparison
from .consistency import PredictiveConsistencyAssessment
from .conflict import PredictiveConflict
from .gap import PredictiveGap

# Revision proposals
from .revision.proposal import PredictionRevisionProposal
from .observation_request_proposal import ObservationRequestProposal
from .monitoring_proposal import PredictiveMonitoringProposal

# Products and outcomes
from .product import PredictiveIntegrationProduct, PredictiveProductKind
from .outcome import (
    PredictiveIntegrationOutcome,
    PredictiveIntegrationContinuation,
    PredictiveIntegrationConfidence,
    PredictiveIntegrationCompleteness,
)
from .state.model import PredictiveIntegrationState

# Configuration
from .configuration import PredictiveIntegrationConfig

# Exceptions
from .exceptions import (
    PredictiveCoordinationError,
    InvalidPredictiveRequest,
    InvalidPredictivePurpose,
    InvalidPredictiveSubject,
    InvalidPredictiveScope,
    PredictiveRecursionLimitExceeded,
    RepeatedPredictiveRequestRejected,
    PredictiveInvariantViolation,
    InvalidPredictionReference,
    InvalidObservationReference,
)

# Contracts (imported separately to avoid circular dependencies)
from . import contracts

__all__ = [
    # Core request models
    "PredictiveIntegrationRequest",
    "PredictiveIntegrationRequestId",
    "PredictiveIntegrationPurpose",
    "PredictiveSubject",
    "PredictiveIntegrationScope",
    
    # Episode and plan
    "PredictiveIntegrationEpisode",
    "PredictiveIntegrationPlan",
    "PredictiveCoordinationStepKind",
    
    # Prediction structures
    "Prediction",
    "PredictionKind",
    "PredictionHorizon",
    "PredictionAssumption",
    "PredictiveHypothesis",
    
    # Expectation structures
    "Expectation",
    "ExpectedState",
    "ExpectedEvent",
    "ExpectedOutcome",
    
    # Assessment structures
    "PredictionProbability",
    "PredictionConfidence",
    "PredictionUncertainty",
    "PredictiveModelApplicabilityAssessment",
    "PredictiveModelLimitation",
    
    # Error structures
    "PredictionError",
    "ExpectationViolation",
    "PredictiveSurpriseAssessment",
    "PredictionErrorAttribution",
    "PredictionCalibrationAssessment",
    
    # Comparison and conflict
    "PredictionComparison",
    "PredictiveConsistencyAssessment",
    "PredictiveConflict",
    "PredictiveGap",
    
    # Revision proposals
    "PredictionRevisionProposal",
    "ObservationRequestProposal",
    "PredictiveMonitoringProposal",
    
    # Products and outcomes
    "PredictiveIntegrationProduct",
    "PredictiveProductKind",
    "PredictiveIntegrationOutcome",
    "PredictiveIntegrationContinuation",
    "PredictiveIntegrationConfidence",
    "PredictiveIntegrationCompleteness",
    
    # State and configuration
    "PredictiveIntegrationState",
    "PredictiveIntegrationConfig",
    
    # Exceptions
    "PredictiveCoordinationError",
    "InvalidPredictiveRequest",
    "InvalidPredictivePurpose",
    "InvalidPredictiveSubject",
    "InvalidPredictiveScope",
    "PredictiveRecursionLimitExceeded",
    "RepeatedPredictiveRequestRejected",
    "PredictiveInvariantViolation",
    "InvalidPredictionReference",
    "InvalidObservationReference",
]

# Import contracts module last to avoid circular dependencies
__all__.append("contracts")