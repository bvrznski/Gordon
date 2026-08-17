# Analogical Reasoning Shared Contracts - Phase 7.4
# ================================================

"""
Shared contracts for analogical reasoning.

This module contains all canonical contract types that are used throughout
the analogical reasoning system.
"""

from .descriptor import (
    AnalogyDescriptor,
    AnalogySessionIdentity,
    AnalogyMode,
    AnalogyLifecycle,
)

from .case_collection import (
    SourceCase,
    CaseCollection,
)

from .retrieval_pipeline import (
    AnalogyRetrieval,
    FeatureExtraction,
)

from .structural_alignment import (
    StructuralMapping,
    AlignmentEvaluation,
)

from .transfer_pipeline import (
    KnowledgeTransfer,
    TransferPipeline,
)

from .schema_extraction import (
    RelationalSchema,
    SchemaExtraction,
)

from .validation import (
    TransferValidation,
    ValidationFindings,
)

from .refinement import (
    AnalogyRefinement,
    RefinementHistory,
)

from .failure import (
    AnalogyFailure,
    FAILURE_KINDS,
)

from .governance import (
    AnalogyGovernance,
    GovernanceFindings,
)

from .health import (
    AnalogyHealth,
    HealthMetrics,
)

from .diagnostics import (
    AnalogyTrace,
)

__all__ = [
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