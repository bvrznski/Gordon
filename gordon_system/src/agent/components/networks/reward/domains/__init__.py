# Multi-Domain Reward Engine (Phase 4.10.5)
# ===========================================

"""
Multi-Domain Reward Engine - Phase 4.10.5.

This subsystem decomposes reward estimates into independent semantic domains
without creating motivation or making decisions. It answers:

    "What kind of reward is this?"

NOT:
    "What should Gordon pursue?"

ARCHITECTURAL ROLE:
    Reward Landscape → Domain Classification → Multi-Domain Reward State
    
    This is a PURE semantic evaluation layer. No learning. No volition.

REWARD TAXONOMY:
    - Intrinsic: problem solving, understanding, mastery
    - Extrinsic: task completion, resource acquisition, objective achievement  
    - Social: cooperation, trust, communication, approval
    - Epistemic: knowledge acquisition, uncertainty reduction
    - Competence: skill improvement, execution quality
    - Autonomy: independent problem solving, self-directed behavior
    - Curiosity: exploration, novel discovery
    - Mission: long-term objective alignment
    - Normative: consistency with internal principles

PROPERTIES:
    • deterministic: Same inputs produce same outputs
    • immutable: No state modifications during evaluation
    • traceable: Full provenance preserved

NOT RESPONSIBLE FOR:
    • Reward estimation (handled by Phase 4.10.3/4)
    • Motivation generation
    • Executive arbitration
    • Planning
    • Policy learning
"""

from __future__ import annotations

# Core models
from .domain import (
    RewardDomain,
    DomainType,
)

# Taxonomy
from .taxonomy import (
    RewardTaxonomy,
    DomainClassificationRules,
)

# Classifiers (one per domain)
from .classifiers.base import (
    BaseRewardClassifier,
    ClassifierResult,
)

# Individual domain classifiers
try:
    from .classifiers.intrinsic import IntrinsicRewardClassifier
except ImportError:
    pass

try:
    from .classifiers.extrinsic import ExtrinsicRewardClassifier
except ImportError:
    pass

try:
    from .classifiers.social import SocialRewardClassifier
except ImportError:
    pass

try:
    from .classifiers.epistemic import EpistemicRewardClassifier
except ImportError:
    pass

try:
    from .classifiers.competence import CompetenceRewardClassifier
except ImportError:
    pass

try:
    from .classifiers.autonomy import AutonomyRewardClassifier
except ImportError:
    pass

try:
    from .classifiers.curiosity import CuriosityRewardClassifier
except ImportError:
    pass

try:
    from .classifiers.mission import MissionRewardClassifier
except ImportError:
    pass

try:
    from .classifiers.normative import NormativeRewardClassifier
except ImportError:
    pass

# Profile and state
from .profile import (
    RewardProfile,
    DomainProfile,
)

from .state import (
    MultiDomainRewardState,
)

# Relationships (includes DomainRelationshipGraph)
from .relationships import (
    DomainRelationshipType,
    DomainRelationship,
    DomainRelationshipGraph,
)

# Engine (orchestrator)
from .engine import (
    RewardDomainEngine,
)

# Validation
try:
    from .validation import (
        DomainValidationResult,
        DomainValidationErrorType,
        DomainValidator,
    )
except ImportError:
    pass

# Serialization
try:
    from .serialization import (
        serialize_profile,
        serialize_state,
        deserialize_profile,
        deserialize_state,
    )
except ImportError:
    pass

__all__ = [
    # Core models
    "RewardDomain",
    "DomainType",
    # Taxonomy
    "RewardTaxonomy",
    "DomainClassificationRules",
    # Classifiers
    "BaseRewardClassifier",
    "ClassifierResult",
    # Profiles and state
    "RewardProfile",
    "DomainProfile",
    "MultiDomainRewardState",
    # Relationships (includes DomainRelationshipGraph)
    "DomainRelationshipType",
    "DomainRelationship",
    "DomainRelationshipGraph",
    # Engine
    "RewardDomainEngine",
    # Validation
    "DomainValidationResult",
    "DomainValidationErrorType",
    "DomainValidator",
    # Serialization
    "serialize_profile",
    "serialize_state",
    "deserialize_profile",
    "deserialize_state",
]