# Gordon Workspace Network Audit Subsystem
# =========================================

"""
Phase: 4.7.22
Canonical subsystem: Workspace Network Audit (WNAudit)
Architectural layer: Network Layer - Observer Tier

This package implements the Workspace Network Audit subsystem which provides
runtime integrity, consistency, diagnostics and certification for the entire
Workspace Network.

The audit system acts as Gordon's internal workspace inspector:
- It never modifies the Workspace directly
- It only observes, validates and reports
- It transforms Workspace state into trustworthy diagnostics

VERSION: 0.1.0-alpha
"""

__version__ = "0.1.0-alpha"
__author__ = "Gordon Cognitive Agent Team"
__status__ = "alpha"

# =============================================================================
# PHASE COMPLETION FLAGS
# =============================================================================

PHASE_4_7_22_COMPLETE = False  # Workspace Network Audit - Phase 4.7.22

# =============================================================================
# IMPORTS - Core Components
# =============================================================================

from . import constants, enums, exceptions, models, config

from .subsystem import WorkspaceAuditSubsystem
from .engine import AuditEngine
from .pipeline import AuditPipeline
from .scheduler import AuditScheduler

# =============================================================================
# VALIDATORS
# =============================================================================

from .graph_validator import GraphTopologyValidator
from .node_validator import NodeValidator
from .edge_validator import EdgeValidator
from .activation_validator import ActivationValidator
from .salience_validator import SalienceValidator
from .synchronization_validator import SynchronizationValidator
from .provenance_validator import ProvenanceValidator
from .lifecycle_validator import LifecycleValidator
from .duplicate_detector import DuplicateDetector
from .orphan_detector import OrphanDetector
from .stale_detector import StaleRepresentationDetector
from .invariant_validator import InvariantValidator

# =============================================================================
# DIAGNOSTICS AND REPORTING
# =============================================================================

from .diagnostics import AuditDiagnostics, DiagnosticsBuilder
from .metrics import AuditMetrics, MetricsCollector
from .health import AuditHealth, HealthAggregator
from .report_builder import ReportBuilder

# =============================================================================
# CORE INTEGRITY
# =============================================================================

from .integrity import workspace_network_audit_integrity_check

# =============================================================================
# EXPORTS
# =============================================================================

__all__: tuple[str, ...] = (
    # Core components
    "WorkspaceAuditSubsystem",
    "AuditEngine",
    "AuditPipeline",
    "AuditScheduler",
    
    # Validators
    "GraphTopologyValidator",
    "NodeValidator",
    "EdgeValidator",
    "ActivationValidator",
    "SalienceValidator",
    "SynchronizationValidator",
    "ProvenanceValidator",
    "LifecycleValidator",
    "DuplicateDetector",
    "OrphanDetector",
    "StaleRepresentationDetector",
    "InvariantValidator",
    
    # Diagnostics and reporting
    "AuditDiagnostics",
    "DiagnosticsBuilder",
    "AuditMetrics",
    "MetricsCollector",
    "AuditHealth",
    "HealthAggregator",
    "ReportBuilder",
    
    # Core integrity
    "workspace_network_audit_integrity_check",
    
    # Constants, enums, exceptions, models, config
    "constants", "enums", "exceptions", "models", "config",
)