# Legal Reasoning Shared Components - Phase 7.47
# ================================================

"""
Canonical shared components for Legal Reasoning.

Legal Reasoning determines:
    - "What does the applicable legal framework require?"
    - "Which actions satisfy legal obligations while preserving rights and regulatory compliance?"

Legal Reasoning transforms legal sources into explicit interpretations,
obligations, permissions and compliance assessments.
"""

from __future__ import annotations

from .descriptor import (
    LegalSessionDescriptor,
    LegalReasoningKind,
    LegalLifecycleState,
)

from .legal_set import LegalSet
from .pipeline import LegalPipeline

from .jurisdictions import Jurisdiction, JurisdictionManager
from .legal_sources import LegalSource, LegalSourceManager
from .statutes import Statute, StatuteManager
from .regulations import Regulation, RegulationManager
from .precedents import Precedent, PrecedentAnalysis
from .obligations import Obligation, ObligationAnalysis
from .rights import Right, RightsAnalysis
from .compliance import ComplianceStatus, ComplianceAnalysis
from .evolution import LegalEvolution
from .validation import LegalValidation, ValidationResult
from .failure import LegalFailure, FailureKind
from .governance import LegalGovernance, GovernanceFinding
from .health import LegalHealth, HealthMetric
from .diagnostics import DiagnosticRecord, DiagnosticsEngine

__all__ = [
    # Descriptors and lifecycle
    "LegalSessionDescriptor",
    "LegalReasoningKind",
    "LegalLifecycleState",
    
    # Core models
    "LegalSet",
    "LegalPipeline",
    
    # Jurisdiction management
    "Jurisdiction",
    "JurisdictionManager",
    
    # Legal source management  
    "LegalSource",
    "LegalSourceManager",
    
    # Statutes
    "Statute",
    "StatuteManager",
    
    # Regulations
    "Regulation",
    "RegulationManager",
    
    # Precedents
    "Precedent",
    "PrecedentAnalysis",
    
    # Obligations
    "Obligation",
    "ObligationAnalysis",
    
    # Rights
    "Right",
    "RightsAnalysis",
    
    # Compliance
    "ComplianceStatus",
    "ComplianceAnalysis",
    
    # Evolution and history
    "LegalEvolution",
    
    # Validation
    "LegalValidation",
    "ValidationResult",
    
    # Failure handling
    "LegalFailure",
    "FailureKind",
    
    # Governance
    "LegalGovernance",
    "GovernanceFinding",
    
    # Health metrics
    "LegalHealth",
    "HealthMetric",
    
    # Diagnostics
    "DiagnosticRecord",
    "DiagnosticsEngine",
]