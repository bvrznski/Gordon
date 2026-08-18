# Normative Reasoning Module
# ===========================

"""
Normative Reasoning subsystem for the Gordon Cognitive Architecture.

This module provides normative and moral reasoning capabilities including:
    - Value analysis and evaluation
    - Principle application and management
    - Obligation tracking
    - Permission analysis
    - Prohibition enforcement
    - Conflict resolution
    - Validation of normative judgments
    - Governance oversight
    - Observability and traceability

Normative Reasoning determines which actions are:
    - Permitted
    - Forbidden
    - Obligatory
    - Recommended
    - Discouraged

It serves as Gordon's behavioral constraint engine before commitment.
"""

from __future__ import annotations

# Core contracts (imported from shared module)
from .shared import (
    NormativeSession,
    NormativeDescriptor,
    NormativeSet,
    NormativePipeline,
    NormativeJudgment,
    NormativeTrace,
)

# Values module
from .values import ValueAssessment

# Principles module
from .principles import PrincipleApplication

# Obligations module
from .obligations import ObligationState

# Permissions module
from .permissions import PermissionState

# Prohibitions module
from .prohibitions import ProhibitionState

# Conflicts module
from .conflicts import ConflictResolution

# Validation module
from .validation import ValidationCheck

# Governance module
from .governance import GovernanceEvaluation

# Observability module
from .observability import NormativeTrace


__all__ = [
    # Core contracts
    "NormativeSession",
    "NormativeDescriptor",
    "NormativeSet",
    "NormativePipeline",
    "NormativeJudgment",
    "NormativeTrace",
    # Values
    "ValueAssessment",
    # Principles
    "PrincipleApplication",
    # Obligations
    "ObligationState",
    # Permissions
    "PermissionState",
    # Prohibitions
    "ProhibitionState",
    # Conflicts
    "ConflictResolution",
    # Validation
    "ValidationCheck",
    # Governance
    "GovernanceEvaluation",
]