# Analogical Reasoning - Phase 7.4
# ===============================

"""
Canonical Analogical Reasoning System.

Analogical Reasoning is Gordon's knowledge transfer engine.
It transfers relational structure between domains without relying on surface similarity.
"""

from __future__ import annotations

import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from .shared.descriptor import (
    AnalogyDescriptor,
    AnalogySessionIdentity,
    AnalogyMode,
    AnalogyLifecycle,
)

from .shared.case_collection import (
    SourceCase,
    CaseCollection,
)

from .shared.retrieval_pipeline import (
    AnalogyRetrieval,
    FeatureExtraction,
)

from .shared.structural_alignment import (
    StructuralMapping,
    AlignmentEvaluation,
)

from .shared.transfer_pipeline import (
    KnowledgeTransfer,
    TransferPipeline,
)

from .shared.schema_extraction import (
    RelationalSchema,
    SchemaExtraction,
)

from .shared.validation import (
    TransferValidation,
    ValidationFindings,
)

from .shared.refinement import (
    AnalogyRefinement,
    RefinementHistory,
)

from .shared.failure import (
    AnalogyFailure,
    FAILURE_KINDS,
)

from .shared.governance import (
    AnalogyGovernance,
    GovernanceFindings,
)

from .shared.health import (
    AnalogyHealth,
    HealthMetrics,
)

from .shared.diagnostics import (
    AnalogyTrace,
)

__all__ = [
    # Shared contracts
    "AnalogyDescriptor",
    "AnalogySessionIdentity",
    "AnalogyMode",
    "AnalogyLifecycle",
    # Case collection
    "SourceCase",
    "CaseCollection",
    # Retrieval
    "AnalogyRetrieval",
    "FeatureExtraction",
    # Structural alignment
    "StructuralMapping",
    "AlignmentEvaluation",
    # Transfer pipeline
    "KnowledgeTransfer",
    "TransferPipeline",
    # Schema extraction
    "RelationalSchema",
    "SchemaExtraction",
    # Validation
    "TransferValidation",
    "ValidationFindings",
    # Refinement
    "AnalogyRefinement",
    "RefinementHistory",
    # Failure
    "AnalogyFailure",
    "FAILURE_KINDS",
    # Governance
    "AnalogyGovernance",
    "GovernanceFindings",
    # Health
    "AnalogyHealth",
    "HealthMetrics",
    # Diagnostics
    "AnalogyTrace",
]

__version__ = "7.4.0"