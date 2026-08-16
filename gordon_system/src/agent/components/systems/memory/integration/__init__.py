# Memory Integration System - Phase 5.1.7

"""
Memory Integration: System communication layer for the Gordon Cognitive Architecture.

This module provides the integration layer that enables Memory to communicate
with other subsystems through explicit contracts. Memory never exposes its
implementation directly; all communication goes through well-defined contracts.

Architecture:
    
    External Subsystems
            ↓
    Integration Contracts
            ↓
    Memory System
    
Contract Types:
    - perception: Observation and signal exchange
    - workspace: Active context and working memory
    - knowledge: Semantic information exchange
    - learning: Behavior improvement proposals
    - identity: Autobiographical continuity
    - coordination: Synchronization and ordering
    - reasoning: Evidence and hypothesis support
    - world_model: Environmental modeling

Guarantees:
    - Projection-only communication (never implementation)
    - Deterministic behavior
    - Versioned contracts with compatibility checks
    - Full observability and diagnostics
"""

from __future__ import annotations

from .contract import (
    IntegrationContractType,
    CompatibilityState,
    VersionInfo,
    MemoryIntegrationContract,
    ContractManager,
)

from .request import (
    RequestType,
    ScopeType,
    RequestScope,
    RequestAuthorization,
    MemoryIntegrationRequest,
    RequestReply,
    create_request,
)

from .response import (
    ProjectionType,
    ResponseOutcome,
    ProvenanceRecord,
    ResponseLimitation,
    MemoryIntegrationResponse,
    create_response,
    ProjectionBuilder,
)

from .compatibility import (
    VersionConstraint,
    CompatibilityResult,
    CompatibilityDefinition,
    CompatibilityManager,
    parse_version,
    compare_versions,
)

from .health import (
    HealthState,
    LatencyMetrics,
    ErrorMetrics,
    IntegrationHealthStatus,
    IntegrationHealthChecker,
)

from .statistics import (
    StatisticType,
    RequestStatistics,
    ResponseStatistics,
    LatencyStatistics,
    ThroughputStatistics,
    IntegrationStatistics,
    IntegrationStatisticsCollector,
)

from .diagnostics import (
    DiagnosticSeverity,
    DiagnosticCategory,
    DiagnosticEntry,
    SessionDiagnostic,
    IntegrationDiagnostics,
    DiagnosticsCollector,
)

from .routing import (
    RouteType,
    RouteMatch,
    RoutingTableEntry,
    Router,
    RoutingDecision,
)

from .session import (
    SessionState,
    SessionMetadata,
    SessionHistory,
    SessionRecord,
    SessionManager,
)

from .validation import (
    ValidationResult,
    ValidationError,
    ValidationOutcome,
    Validator,
    RequestValidator,
    ResponseValidator,
    ValidationPipeline,
)


# Expose all integration protocol modules
from .perception import create_perception_contract, PerceptionProtocol
from .workspace import create_workspace_contract, WorkspaceProtocol
from .knowledge import create_knowledge_contract, KnowledgeProtocol
from .learning import create_learning_contract, LearningProtocol
from .identity import create_identity_contract, IdentityProtocol
from .coordination import create_coordination_contract, CoordinationProtocol
from .reasoning import create_reasoning_contract, ReasoningProtocol
from .world_model import create_world_model_contract, WorldModelProtocol


__all__ = [
    # Contract types
    "IntegrationContractType",
    "CompatibilityState",
    "VersionInfo",
    "MemoryIntegrationContract",
    "ContractManager",
    
    # Request/Response types
    "RequestType",
    "ScopeType",
    "RequestScope",
    "RequestAuthorization",
    "MemoryIntegrationRequest",
    "RequestReply",
    "create_request",
    
    "ProjectionType",
    "ResponseOutcome",
    "ProvenanceRecord",
    "ResponseLimitation",
    "MemoryIntegrationResponse",
    "create_response",
    "ProjectionBuilder",
    
    # Compatibility
    "VersionConstraint",
    "CompatibilityResult",
    "CompatibilityDefinition",
    "CompatibilityManager",
    "parse_version",
    "compare_versions",
    
    # Health
    "HealthState",
    "LatencyMetrics",
    "ErrorMetrics",
    "IntegrationHealthStatus",
    "IntegrationHealthChecker",
    
    # Statistics
    "StatisticType",
    "RequestStatistics",
    "ResponseStatistics",
    "LatencyStatistics",
    "ThroughputStatistics",
    "IntegrationStatistics",
    "IntegrationStatisticsCollector",
    
    # Diagnostics
    "DiagnosticSeverity",
    "DiagnosticCategory",
    "DiagnosticEntry",
    "SessionDiagnostic",
    "IntegrationDiagnostics",
    "DiagnosticsCollector",
    
    # Routing
    "RouteType",
    "RouteMatch",
    "RoutingTableEntry",
    "Router",
    "RoutingDecision",
    
    # Session
    "SessionState",
    "SessionMetadata",
    "SessionHistory",
    "SessionRecord",
    "SessionManager",
    
    # Validation
    "ValidationResult",
    "ValidationError",
    "ValidationOutcome",
    "Validator",
    "RequestValidator",
    "ResponseValidator",
    "ValidationPipeline",
    
    # Protocols (for each integration type)
    "create_perception_contract",
    "PerceptionProtocol",
    "create_workspace_contract",
    "WorkspaceProtocol",
    "create_knowledge_contract",
    "KnowledgeProtocol",
    "create_learning_contract",
    "LearningProtocol",
    "create_identity_contract",
    "IdentityProtocol",
    "create_coordination_contract",
    "CoordinationProtocol",
    "create_reasoning_contract",
    "ReasoningProtocol",
    "create_world_model_contract",
    "WorldModelProtocol",
]