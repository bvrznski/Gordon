# Memory Policies Package - Phase 5.1.5 Canonical Implementation
# ================================================================
"""
Memory Policies: Decision-making layer for memory management.

Policies evaluate proposals and produce recommendations.
They never execute actions; execution belongs elsewhere.

Package Structure:
    policies/
        admission/      : Candidate admission decisions
        activation/     : Artifact activation decisions  
        retention/      : Long-term preservation decisions
        archival/       : Archival storage decisions
        supersession/   : Revision replacement decisions
        compression/    : Representation simplification decisions
        reconstruction/ : Missing data recovery decisions
        recovery/       : Failure recovery decisions
        aggregation/    : Multi-policy decision merging
        conflict/       : Policy disagreement detection

Canonical Policies:
    - AdmissionPolicy
    - ActivationPolicy
    - RetentionPolicy
    - ArchivalPolicy
    - SupersessionPolicy
    - CompressionPolicy
    - ReconstructionPolicy
    - RecoveryPolicy

Core Contracts:
    - MemoryDecision: Decision output from policy evaluation
    - PolicyEvidence: Evidence referenced in decisions
    - MemoryPolicy: Abstract base class for all policies

Statistics & Monitoring:
    - PolicyStatistics: Metrics about policy behavior
    - PolicyDiagnostics: Runtime diagnostics
    - PolicyHealthMonitor: Health monitoring

Aggregation & Conflict:
    - AggregatedDecision: Merged decision from multiple policies
    - PolicyConflict: Detected conflict between policies
"""

from __future__ import annotations

# Core contracts
from .decision import (
    DecisionKind,
    DecisionStatus,
    MemoryDecision,
    MemoryDecisionBuilder,
)

from .evidence import (
    EvidenceKind,
    PolicyEvidence,
    PolicyEvidenceBuilder,
    EvidenceCollection,
)

from .policy import (
    PolicyKind,
    PolicyMetrics,
    PolicyDiagnostics,
    MemoryPolicy,
)

# Statistics & monitoring
from .statistics import (
    PolicyStatistics,
    PolicyStatisticsAggregator,
)

from .health import (
    PolicyHealthStatus,
    PolicyHealth,
    PolicyHealthMonitor,
)

# Aggregation and conflict
from .aggregation import (
    AggregatedDecision,
    PolicyAggregator,
)

from .conflict import (
    ConflictKind,
    PolicyConflict,
    ConflictDetector,
    ConflictResolutionReport,
)

# Canonical policies
from .admission.policy import (
    AdmissionPolicy,
    create_admission_policy,
)

from .activation.policy import (
    ActivationPolicy,
    create_activation_policy,
)

from .retention.policy import (
    RetentionPolicy,
    create_retention_policy,
)

from .archival.policy import (
    ArchivalPolicy,
    create_archival_policy,
)

from .supersession.policy import (
    SupersessionPolicy,
    create_supersession_policy,
)

from .compression.policy import (
    CompressionPolicy,
    create_compression_policy,
)

from .reconstruction.policy import (
    ReconstructionPolicy,
    create_reconstruction_policy,
)

from .recovery.policy import (
    RecoveryPolicy,
    create_recovery_policy,
)

from .forgetting.policy import (
    ForgettingPolicy,
    create_forgetting_policy,
)

__all__ = [
    # Core contracts
    "DecisionKind",
    "DecisionStatus",
    "MemoryDecision",
    "MemoryDecisionBuilder",
    "EvidenceKind",
    "PolicyEvidence",
    "PolicyEvidenceBuilder",
    "EvidenceCollection",
    "PolicyKind",
    "PolicyMetrics",
    "PolicyDiagnostics",
    "MemoryPolicy",
    
    # Statistics & monitoring
    "PolicyStatistics",
    "PolicyStatisticsAggregator",
    "PolicyHealthStatus",
    "PolicyHealth",
    "PolicyHealthMonitor",
    
    # Aggregation & conflict
    "AggregatedDecision",
    "PolicyAggregator",
    "ConflictKind",
    "PolicyConflict",
    "ConflictDetector",
    "ConflictResolutionReport",
    
    # Canonical policies
    "AdmissionPolicy",
    "create_admission_policy",
    "ActivationPolicy",
    "create_activation_policy",
    "RetentionPolicy",
    "create_retention_policy",
    "ArchivalPolicy",
    "create_archival_policy",
    "SupersessionPolicy",
    "create_supersession_policy",
    "CompressionPolicy",
    "create_compression_policy",
    "ReconstructionPolicy",
    "create_reconstruction_policy",
    "RecoveryPolicy",
    "create_recovery_policy",
    "ForgettingPolicy",
    "create_forgetting_policy",
]

__version__ = "5.1.5"