# Agentic Reward Network - Phase 4.10.1
# ========================================

"""
Canonical Agentic Reward Network (Phase 4.10.1).

The Reward Network evaluates cognitive and behavioral outcomes by estimating:

    * expected benefit
    * realized benefit  
    * expected cost
    * realized cost
    * goal progress
    * drive satisfaction
    * resource expenditure
    * outcome quality

It transforms cognitive outcomes into reward representations.

CRITICAL DISTINCTION:
    - Truth belongs to Predictive Processing
    - Importance belongs to Salience  
    - Decision belongs to Executive Control
    - Reward belongs to Outcome Evaluation

This is a PURE semantic evaluation layer.
No learning. No decision making. No action selection.

The Reward Network produces immutable reward estimates that downstream systems
(Prediction, Planning, Executive Control) consume for their own computations.
"""

from __future__ import annotations

# Core models
from .outcome import (
    Outcome,
    OutcomeCategory,
    OutcomeSourceSubsystem,
)

from .reward import (
    RewardEstimate,
    RewardSource,
)

from .benefit import BenefitEstimate

from .cost import CostEstimate

from .confidence import ConfidenceEstimate

from .uncertainty import UncertaintyEstimate

from .valence import Valence

# Landscape
from .landscape import (
    RewardLandscape,
    MultiTimescaleReward,
    HierarchicalReward,
)

# Baseline and dynamics (Phase 4.10.1-4)
try:
    from .baseline import RewardBaseline
except ImportError:
    # Phase 4.10.4 style baseline (AdaptiveRewardBaseline is the main one now)
    class RewardBaseline: pass

from .baseline import (
    AdaptiveRewardBaseline,
    BaselineDomain,
)

from .dynamics import (
    RewardDynamics,
)

# State
from .state import (
    RewardState,  # Phase 4.10.1-3 basic state
    TemporalRewardState,  # Phase 4.10.4 temporal aggregation state
)

# Engine (Phase 4.10.3 - Evaluation; Phase 4.10.4 - Dynamics)
from .engine import (
    RewardEvaluationEngine,  # Phase 4.10.3 evaluation engine
    RewardDynamicsEngine,  # Phase 4.10.4 dynamics engine
)

# Requests/Results
from .request import RewardEvaluationRequest

from .result import RewardEvaluationResult

# Validation (Phase 4.10.3 + 4.10.4)
# Import validation - handle missing classes gracefully
try:
    from .validation import (
        RewardValidation,
        ValidationErrorType,
    )
except ImportError:
    pass

try:
    from .validation import ValidationTrace
except ImportError:
    pass

try:
    from .validation import ValidationResult
except ImportError:
    pass

try:
    from .validation import RewardDynamicsValidator
except ImportError:
    pass

# Evidence Engine (Phase 4.10.2)
from .evidence import (
    RewardEvidence,
    RewardEvidenceRequest,
    RewardEvidenceResult,
    RewardEvidenceState,
    RewardEvidenceGraph,
    EvidenceConfidence,
    EvidenceUncertainty,
    EvidenceNormalizer,
    EvidenceFusion,
    RewardEvidenceEngine,
)

# Phase 4.10.4 Temporal Analysis Components
from .trajectory import (
    RewardTrajectory,  # Individual trajectory model
    TrajectoryKind,  # Type alias for trajectory types
    RewardTrajectoryCollection,  # Aggregated trajectory collection
)

from .trend import (
    RewardTrend,  # Trend analysis model
    TrendDirection,  # Type alias for trend directions
    TrendVelocity,  # Type alias for velocity measures
    TrendCollection,  # Aggregated trend collection
    TrendAnalyzer,  # Deterministic trend analyzer
)

from .stability import (
    RewardStability,  # Stability analysis model
    StabilityCollection,  # Aggregated stability collection
    StabilityAnalyzer,  # Deterministic stability analyzer
)

from .volatility import (
    RewardVolatility,  # Volatility analysis model
    VolatilityCollection,  # Aggregated volatility collection
    VolatilityAnalyzer,  # Deterministic volatility analyzer
)

from .drift import (
    RewardDrift,  # Drift analysis model
    DriftCollection,  # Aggregated drift collection
    DriftAnalyzer,  # Deterministic drift analyzer
)

from .homeostasis import (
    RewardHomeostasis,  # Homeostasis state model
    HomeostasisCollection,  # Aggregated homeostasis collection
    HomeostasisAnalyzer,  # Deterministic homeostasis analyzer
)

from .history import (
    RewardHistoryEntry,  # Single history entry
    RewardHistory,  # Complete reward history
    HistoryAnalyzer,  # Deterministic history analyzer
)

from .serialization import (
    SerializationError,
    DeserializationError,
    serialize_trajectory,
    serialize_baseline,
    serialize_trend,
    serialize_stability,
    serialize_volatility,
    serialize_drift,
    serialize_homeostasis,
    serialize_history_entry,
    serialize_history,
    serialize_temporal_state,
    json_serialize_trajectory,
    json_serialize_baseline,
    json_serialize_temporal_state,
)

# Phase 4.10.5 Multi-Domain Reward Engine
from .domains import (
    # Core models
    RewardDomain,
    DomainType,
    # Taxonomy
    RewardTaxonomy,
    DomainClassificationRules,
    # Classifiers
    BaseRewardClassifier,
    ClassifierResult,
    IntrinsicRewardClassifier,
    ExtrinsicRewardClassifier,
    SocialRewardClassifier,
    EpistemicRewardClassifier,
    CompetenceRewardClassifier,
    AutonomyRewardClassifier,
    CuriosityRewardClassifier,
    MissionRewardClassifier,
    NormativeRewardClassifier,
    # Profile and state
    RewardProfile,
    DomainProfile,
    MultiDomainRewardState,
    # Relationships
    DomainRelationshipType,
    DomainRelationship,
    DomainRelationshipGraph,
    # Engine
    RewardDomainEngine,
    # Validation
    DomainValidationResult,
    DomainValidationErrorType,
    DomainValidator,
)

__all__ = [
    # Core models (Phase 4.10.1)
    "Outcome",
    "OutcomeCategory", 
    "OutcomeSourceSubsystem",
    "RewardEstimate",
    "RewardSource",
    "BenefitEstimate",
    "CostEstimate",
    "ConfidenceEstimate",
    "UncertaintyEstimate",
    "Valence",
    # Landscape (Phase 4.10.1)
    "RewardLandscape",
    "MultiTimescaleReward", 
    "HierarchicalReward",
    # Baseline models
    "RewardBaseline",  # Phase 4.10.1 reference baseline
    "AdaptiveRewardBaseline",  # Phase 4.10.4 adaptive baseline
    "BaselineDomain",  # Phase 4.10.4 domain definitions
    # Dynamics (Phase 4.10.1)
    "RewardDynamics",
    # State models
    "RewardState",  # Phase 4.10.1-3 basic state
    "TemporalRewardState",  # Phase 4.10.4 temporal aggregation state
    # Engine components
    "RewardEvaluationEngine",  # Phase 4.10.3 evaluation engine
    "RewardDynamicsEngine",  # Phase 4.10.4 dynamics engine
    # Requests/Results
    "RewardEvaluationRequest",
    "RewardEvaluationResult",
    # Validation (Phase 4.10.1-4)
    "RewardValidation",
    "ValidationErrorType",
    "ValidationTrace",
    "ValidationResult",
    "RewardDynamicsValidator",
    # Evidence Engine (Phase 4.10.2)
    "RewardEvidence",
    "RewardEvidenceRequest",
    "RewardEvidenceResult",
    "RewardEvidenceState",
    "RewardEvidenceGraph",
    "EvidenceConfidence",
    "EvidenceUncertainty",
    "EvidenceNormalizer",
    "EvidenceFusion",
    "RewardEvidenceEngine",
    # Phase 4.10.4 Temporal Analysis Components
    "RewardTrajectory",  # Trajectory model
    "TrajectoryKind",
    "RewardTrajectoryCollection",
    "RewardTrend",  # Trend analysis
    "TrendDirection",
    "TrendVelocity",
    "TrendCollection",
    "TrendAnalyzer",
    "RewardStability",  # Stability analysis
    "StabilityCollection",
    "StabilityAnalyzer",
    "RewardVolatility",  # Volatility analysis
    "VolatilityCollection",
    "VolatilityAnalyzer",
    "RewardDrift",  # Drift analysis
    "DriftCollection",
    "DriftAnalyzer",
    "RewardHomeostasis",  # Homeostasis state
    "HomeostasisCollection",
    "HomeostasisAnalyzer",
    "RewardHistoryEntry",  # History entry
    "RewardHistory",  # Complete history
    "HistoryAnalyzer",
    # Serialization (Phase 4.10.4)
    "SerializationError",
    "DeserializationError",
    "serialize_trajectory",
    "serialize_baseline",
    "serialize_trend",
    "serialize_stability",
    "serialize_volatility",
    "serialize_drift",
    "serialize_homeostasis",
    "serialize_history_entry",
    "serialize_history",
    "serialize_temporal_state",
    "json_serialize_trajectory",
    "json_serialize_baseline",
    "json_serialize_temporal_state",
    # Phase 4.10.5 Multi-Domain Reward Engine
    "RewardDomain",
    "DomainType",
    "RewardTaxonomy",
    "DomainClassificationRules",
    "BaseRewardClassifier",
    "ClassifierResult",
    "IntrinsicRewardClassifier",
    "ExtrinsicRewardClassifier",
    "SocialRewardClassifier",
    "EpistemicRewardClassifier",
    "CompetenceRewardClassifier",
    "AutonomyRewardClassifier",
    "CuriosityRewardClassifier",
    "MissionRewardClassifier",
    "NormativeRewardClassifier",
    "RewardProfile",
    "DomainProfile",
    "MultiDomainRewardState",
    "DomainRelationshipType",
    "DomainRelationship",
    "DomainRelationshipGraph",
    "RewardDomainEngine",
    "DomainValidationResult",
    "DomainValidationErrorType",
    "DomainValidator",
]
