# Perception Audit - Phase 5.2.6
# ================================

"""
Perception Audit: Evaluates the quality, consistency, completeness,
and reliability of perceptual processing.

Perception Audit is a cognitive subsystem that continuously monitors and 
assesses the health, accuracy, and trustworthiness of perception results.
It does NOT perform perception itself; rather, it audits perception.

Core Principles:
    - Audit never modifies perception
    - Audit never performs reasoning about the external world
    - Audit never interprets semantic meaning
    - Audit never decides on actions
    - Audit measures quality of what perception produces
"""

from __future__ import annotations

# Core exports from models (immutable data structures)
from .models import (
    PerceptionSnapshot,
    ModalityAssessment,
    QualityAssessment,
    ConsistencyAssessment,
    CompletenessAssessment,
    ConfidenceAssessment,
    AuditFinding,
    PerceptionAuditReport,
    PerceptionAuditHealth,
    AuditStatistics,
)

# Constants
from .constants import (
    AuditSeverity,
    FindingType,
    ModalityQualityDimension,
    AuditStatus,
    ConfidencePolicy,
    UncertaintyPolicy,
)

# Core exports from engine (runtime components)
from .engine.engine import (
    PerceptionAuditEngine,
    PerceptionAuditRequest,
    AuditPipelineStage,
)
from .engine.integrity import (
    perception_audit_integrity_check,
    verify_perception_audit_integrity,
)

__all__ = [
    # Models
    "PerceptionSnapshot",
    "ModalityAssessment",
    "QualityAssessment",
    "ConsistencyAssessment",
    "CompletenessAssessment",
    "ConfidenceAssessment",
    "AuditFinding",
    "PerceptionAuditReport",
    "PerceptionAuditHealth",
    "AuditStatistics",
    # Constants
    "AuditSeverity",
    "FindingType",
    "ModalityQualityDimension",
    "AuditStatus",
    "ConfidencePolicy",
    "UncertaintyPolicy",
    # Engine
    "PerceptionAuditEngine",
    "PerceptionAuditRequest",
    "AuditPipelineStage",
    # Integrity
    "perception_audit_integrity_check",
    "verify_perception_audit_integrity",
]