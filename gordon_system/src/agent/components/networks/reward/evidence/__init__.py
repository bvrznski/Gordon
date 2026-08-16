# Reward Network - Evidence Package
# ===================================

"""
Canonical Reward Evidence Engine (Phase 4.10.2).

The Reward Evidence Engine extracts, normalizes, attributes, and structures
semantic evidence from outcomes. It produces the canonical RewardEvidenceState
that downstream reward estimation engines consume.

CRITICAL DISTINCTION:
    - Evidence belongs to Phase 4.10.2 (this module)
    - Reward estimation belongs to Phase 4.10.3
    
This module asks: "What semantic evidence exists?"
Next module will ask: "Given this evidence, what is the reward value?"

EVIDENCE LAWS:
    EVIDENCE-LAW-001: Exactly one canonical RewardEvidenceEngine exists
    EVIDENCE-LAW-002: Exactly one canonical RewardEvidenceState exists
    EVIDENCE-LAW-003: Every RewardEvidence references at least one Outcome
    EVIDENCE-LAW-004: RewardEvidence preserves semantic identity
    EVIDENCE-LAW-005: RewardEvidence preserves provenance
    EVIDENCE-LAW-006: RewardEvidence preserves revision history
    EVIDENCE-LAW-007: RewardEvidence preserves contextual semantics
    EVIDENCE-LAW-008: RewardEvidence is immutable
    EVIDENCE-LAW-009: Evidence processing remains deterministic
    EVIDENCE-LAW-010: RewardEvidence shall never contain reward values
"""

from __future__ import annotations

# Core evidence model
from .evidence import (
    RewardEvidence,
    EvidenceType,
    EvidenceKind,
)

# Attribution models
from .attribution import (
    EvidenceAttribution,
    EvidenceSourceSubsystem,
    EvidenceProvenance,
)

# Graph models
from .graph import (
    RewardEvidenceGraph,
    EvidenceEdge,
    EvidenceRelationship,
)

# State model
from .state import (
    RewardEvidenceState,
)

# Engine
from .engine import (
    RewardEvidenceEngine,
)

# Requests/Results
from .request import (
    RewardEvidenceRequest,
)

from .result import (
    RewardEvidenceResult,
)

# Validation
from .validation import (
    EvidenceValidation,
    ValidationErrorType,
)

# Confidence and uncertainty
from .confidence import EvidenceConfidence

from .uncertainty import EvidenceUncertainty

# Normalization and fusion
from .normalization import EvidenceNormalizer

from .fusion import EvidenceFusion

# Serialization
from .serialization import serialize_evidence, deserialize_evidence

__all__ = [
    # Core evidence model
    "RewardEvidence",
    "EvidenceType",
    "EvidenceKind",
    # Attribution models
    "EvidenceAttribution",
    "EvidenceSourceSubsystem",
    "EvidenceProvenance",
    # Graph models
    "RewardEvidenceGraph",
    "EvidenceEdge",
    "EvidenceRelationship",
    # State model
    "RewardEvidenceState",
    # Engine
    "RewardEvidenceEngine",
    # Requests/Results
    "RewardEvidenceRequest",
    "RewardEvidenceResult",
    # Validation
    "EvidenceValidation",
    "ValidationErrorType",
    # Confidence and uncertainty
    "EvidenceConfidence",
    "EvidenceUncertainty",
    # Normalization and fusion
    "EvidenceNormalizer",
    "EvidenceFusion",
    # Serialization
    "serialize_evidence",
    "deserialize_evidence",
]
