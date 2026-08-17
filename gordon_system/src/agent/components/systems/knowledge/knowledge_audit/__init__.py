# Knowledge Audit - Phase 6.10
# ============================
"""
Knowledge Audit: Continuous evaluation of knowledge quality, health, validity,
consistency and usefulness.

Knowledge Audit answers:
    "Can Gordon trust what it knows?"

This subsystem never changes knowledge directly.
It produces findings and recommendations.

Only Learning Memory and the owning subsystem may authorize knowledge changes.
"""

from __future__ import annotations

from .enums import (
    AuditDimension,
    FindingType,
    RecommendationType,
    AuditStatus,
    EvidenceQuality,
    ConfidenceCalibration,
    DependencyStatus,
)

from .constants import (
    DEFAULT_CONFIDENCE_THRESHOLD,
    DEFAULT_UNCERTAINTY_THRESHOLD,
    DEFAULT_COVERAGE_THRESHOLD,
    MIN_EVIDENCE_COUNT,
    MAX_CONTRADICTION_RATIO,
    FRESHNESS_RECENT_THRESHOLD,
    FRESHNESS_WARNING_THRESHOLD,
    FRESHNESS_OBSOLETE_THRESHOLD,
)

# Exceptions
from .exceptions import (
    KnowledgeAuditError,
    InvalidAuditRequest,
    AuditRequestTimeout,
    AuditEngineError,
    EngineConfigurationError,
    ArtifactNotFoundError,
    DependencyNotFoundError,
    ReportSerializationError,
    ReportDeserializationError,
    AuditSessionError,
    SessionAlreadyActive,
    SessionNotActive,
    IntegrityCheckError,
)

# Core models
from .interfaces import (
    KnowledgeAuditRequest,
    KnowledgeAuditSession,
    KnowledgeAuditTarget,
    KnowledgeAuditFinding,
    KnowledgeAuditRecommendation,
    KnowledgeAuditReport,
    KnowledgeHealth,
    KnowledgeConsistencyAssessment,
    KnowledgeCoverageAssessment,
    KnowledgeFreshnessAssessment,
    KnowledgeConfidenceAssessment,
    KnowledgeCoverage,
    KnowledgeDependencyGraph,
    KnowledgeEvidenceSummary,
)

from .interfaces import (
    KnowledgeAuditEngine,
    KnowledgeAuditSessionHandler,
    AuditReportGenerator,
    KnowledgeArtifactProvider,
)

# Import pipeline components
from .pipeline import KnowledgeAuditPipeline, PipelineContext

# Import sessions
from .sessions import ActiveSession, KnowledgeAuditSessionFactory


__all__ = [
    # Core models
    "KnowledgeAuditRequest",
    "KnowledgeAuditSession",
    "KnowledgeAuditTarget",
    "KnowledgeAuditFinding",
    "KnowledgeAuditRecommendation",
    "KnowledgeAuditReport",
    
    # Enums
    "AuditDimension",
    "FindingType",
    "RecommendationType",
    "AuditStatus",
    "EvidenceQuality",
    "ConfidenceCalibration",
    "DependencyStatus",
    
    # Constants
    "DEFAULT_CONFIDENCE_THRESHOLD",
    "DEFAULT_UNCERTAINTY_THRESHOLD",
    "DEFAULT_COVERAGE_THRESHOLD",
    "MIN_EVIDENCE_COUNT",
    "MAX_CONTRADICTION_RATIO",
    "FRESHNESS_RECENT_THRESHOLD",
    "FRESHNESS_WARNING_THRESHOLD",
    "FRESHNESS_OBSOLETE_THRESHOLD",
    
    # Exceptions
    "KnowledgeAuditError",
    "InvalidAuditRequest",
    "AuditRequestTimeout",
    "AuditEngineError",
    "EngineConfigurationError",
    "ArtifactNotFoundError",
    "DependencyNotFoundError",
    "ReportSerializationError",
    "ReportDeserializationError",
    "AuditSessionError",
    "SessionAlreadyActive",
    "SessionNotActive",
    "IntegrityCheckError",
    
    # Interfaces and base classes
    "KnowledgeAuditEngine",
    "KnowledgeAuditSessionHandler",
    "AuditReportGenerator",
    "KnowledgeArtifactProvider",
    
    # Health metrics
    "KnowledgeHealth",
    "KnowledgeConsistencyAssessment",
    "KnowledgeCoverageAssessment",
    "KnowledgeFreshnessAssessment",
    "KnowledgeConfidenceAssessment",
    "KnowledgeCoverage",
    "KnowledgeDependencyGraph",
    "KnowledgeEvidenceSummary",
    
    # Pipeline components
    "KnowledgeAuditPipeline",
    "PipelineContext",
    
    # Session management
    "ActiveSession",
    "KnowledgeAuditSessionFactory",
]