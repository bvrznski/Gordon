# Canonical Belief Revision Package - Phase 4.9.5
# ================================================
"""
BeliefRevision subsystem for Gordon Cognitive Architecture.

This package implements the belief revision engine that:

* Takes current beliefs and precision landscape as input
* Identifies revision candidates from prediction errors
* Validates consistency and resolves contradictions
* Produces an updated BeliefState

Architecture:
    Prediction Error Landscape  Precision Landscape
                |                     |
                v                     v
        Revision Candidates  <-- Engine -->  Updated Belief State
                                        / \
                                       /   \
                                Revision Graph  World Model Synchronization (next phase)

Phase Position:
    Precision Estimation -> Belief Revision [CURRENT] -> World Model Synchronization

No runtime dependencies; pure semantic definitions.
"""
from __future__ import annotations

# Enums
from .enums import (
    # Revision Kind
    CREATE, UPDATE, MERGE, SPLIT, WEAKEN, STRENGTHEN, REMOVE, DEFER, REJECT, UNKNOWN,
    # Contradiction Kind
    LOGICAL_CONTRADICTION, SEMANTIC_CONTRADICTION, TEMPORAL_CONTRADICTION,
    HIERARCHICAL_CONTRADICTION, CAUSAL_CONTRADICTION, SCHEMA_CONTRADICTION,
    # Dependency Relationship
    SUPPORTS, DEPENDS_ON, CONTRADICTS, REFINES, GENERALIZES, SPECIALIZES, EXPLAINS,
    # Conflict Resolution Strategy
    RETAIN_BOTH, REPLACE, MERGE_CONFLICTING, DEFER_RESOLUTION, REJECT_CONTRADICTION,
    MARK_UNRESOLVED,
    # Hierarchy Level
    SENSORY, CONTEXTUAL, CONCEPTUAL, ABSTRACT,
    # Status
    PENDING, VALIDATED, EVALUATED, CONTRADICTION_ANALYZED, CONSISTENCY_VALIDATED,
    PROPAGATION_COMPLETED, REVISION_GRAPH_CREATED, BELIEF_STATE_CREATED, COMPLETED, FAILED,
    # Trace Event
    REQUEST_VALIDATED, BELIEF_STATE_VALIDATED, PRECISION_VALIDATED, CANDIDATES_GENERATED,
    EVIDENCE_EVALUATED, CONTRADICTIONS_ANALYZED, CONSISTENCY_CHECKED, BELIEFS_UPDATED,
    REVISION_GRAPH_CREATED, STATE_VALIDATED,
    # Failure Kind
    INVALID_BELIEF, INVALID_PRECISION, INVALID_POLICY, UNSUPPORTED_SCHEMA,
    DEPENDENCY_CYCLE, CONTRADICTION_UNRESOLVED, UNKNOWN_FAILURE
)

# Core Models
from .models import (
    SemanticIdentity, BeliefIdentity, Revision, Provenance, Belief, BeliefState,
    PrecisionLandscapeReference, ContextProjection, WorldModelProjection, SemanticTime,
    FailureRecord, SerializationEnvelope, CANONICAL_SCHEMA_PREFIX, DEFAULT_SCHEMA_VERSION
)

# Request/Result
from .request import (
    BeliefRevisionRequest, BeliefRevisionResult, BeliefRevisionEngine
)

# Validation
from .validation import ValidationResult, BeliefRevisionValidator

# Policy
from .policy import RevisionPolicy, AcceptanceCriteria, PolicyEnforcer, create_policy

# Consistency
from .consistency import ConsistencyCheckResult, ConsistencyRule, ConsistencyValidator

# Contradiction
from .contradiction import (
    Contradiction, ContradictionAnalysisResult, ContradictionAnalyzer,
    ContradictionResolver, resolve_contradiction
)

# Dependency Graph
from .dependency_graph import (
    DependencyEdge, DependencyGraph, DependencyGraphBuilder, DependencyAnalyzer
)

# Serialization
from .serialization import SerializationResult, BeliefRevisionSerializer, serialize_belief_state

# Package Metadata
__version__: str = "1.0.0"
__spec_version__: str = "4.9.5"

__all__: tuple[str, ...] = (
    # Enums - Revision Kind
    "CREATE", "UPDATE", "MERGE", "SPLIT", "WEAKEN", "STRENGTHEN", "REMOVE",
    "DEFER", "REJECT", "UNKNOWN",
    # Enums - Contradiction Kind
    "LOGICAL_CONTRADICTION", "SEMANTIC_CONTRADICTION", "TEMPORAL_CONTRADICTION",
    "HIERARCHICAL_CONTRADICTION", "CAUSAL_CONTRADICTION", "SCHEMA_CONTRIDICTION",
    # Enums - Dependency Relationship
    "SUPPORTS", "DEPENDS_ON", "CONTRADICTS", "REFINES", "GENERALIZES",
    "SPECIALIZES", "EXPLAINS",
    # Enums - Conflict Resolution Strategy
    "RETAIN_BOTH", "REPLACE", "MERGE_CONFLICTING", "DEFER_RESOLUTION",
    "REJECT_CONTRADICTION", "MARK_UNRESOLVED",
    # Enums - Hierarchy Level
    "SENSORY", "CONTEXTUAL", "CONCEPTUAL", "ABSTRACT",
    # Enums - Status
    "PENDING", "VALIDATED", "EVALUATED", "CONTRADICTION_ANALYZED",
    "CONSISTENCY_VALIDATED", "PROPAGATION_COMPLETED", "REVISION_GRAPH_CREATED",
    "BELIEF_STATE_CREATED", "COMPLETED", "FAILED",
    # Enums - Trace Event
    "REQUEST_VALIDATED", "BELIEF_STATE_VALIDATED", "PRECISION_VALIDATED",
    "CANDIDATES_GENERATED", "EVIDENCE_EVALUATED", "CONTRADICTIONS_ANALYZED",
    "CONSISTENCY_CHECKED", "BELIEFS_UPDATED", "REVISION_GRAPH_CREATED", "STATE_VALIDATED",
    # Enums - Failure Kind
    "INVALID_BELIEF", "INVALID_PRECISION", "INVALID_POLICY", "UNSUPPORTED_SCHEMA",
    "DEPENDENCY_CYCLE", "CONTRADICTION_UNRESOLVED", "UNKNOWN_FAILURE",
    # Models
    "SemanticIdentity", "BeliefIdentity", "Revision", "Provenance", "Belief",
    "BeliefState", "PrecisionLandscapeReference", "ContextProjection",
    "WorldModelProjection", "SemanticTime", "FailureRecord", "SerializationEnvelope",
    "CANONICAL_SCHEMA_PREFIX", "DEFAULT_SCHEMA_VERSION",
    # Request/Result
    "BeliefRevisionRequest", "BeliefRevisionResult", "BeliefRevisionEngine",
    # Validation
    "ValidationResult", "BeliefRevisionValidator",
    # Policy
    "RevisionPolicy", "AcceptanceCriteria", "PolicyEnforcer", "create_policy",
    # Consistency
    "ConsistencyCheckResult", "ConsistencyRule", "ConsistencyValidator",
    # Contradiction
    "Contradiction", "ContradictionAnalysisResult", "ContradictionAnalyzer",
    "ContradictionResolver", "resolve_contradiction",
    # Dependency Graph
    "DependencyEdge", "DependencyGraph", "DependencyGraphBuilder", "DependencyAnalyzer",
    # Serialization
    "SerializationResult", "BeliefRevisionSerializer", "serialize_belief_state"
)