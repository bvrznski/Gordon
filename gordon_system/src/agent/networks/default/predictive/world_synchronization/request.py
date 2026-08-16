# Canonical World Synchronization Request/Result - Phase 4.9.6
# ==============================================================
"""
Request/Result contract models for WorldModelSynchronization subsystem.
No runtime dependencies; pure semantic definitions.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


# =============================================================================
# SYNCHRONIZATION POLICY (CONFIGURABLE BEHAVIOR)
# =============================================================================

@dataclass(frozen=True, slots=True)
class SynchronizationPolicy:
    """
    Immutable policy configuration for world synchronization.
    
    Fields:
        entity_lifecycle_policy:  Entity lifecycle behavior
        relationship_policy:      Relationship handling
        ontology_policy:          Ontology evolution rules
        transaction_policy:       Transaction constraints
        rollback_policy:          Rollback options
        validation_strictness:    Validation tolerance
    
    Rules:
        - Policy must be explicitly provided
        - No default values; all policies must be configured
        - Policy remains immutable during synchronization
    """
    entity_lifecycle_policy: str = "strict"  # strict/lenient
    relationship_policy: str = "validate"   # validate/ignore
    ontology_policy: str = "evolutionary"   # evolutionary/conservative
    transaction_policy: str = "atomic"      # atomic/non-atomic
    rollback_policy: str = "enabled"        # enabled/disabled
    validation_strictness: str = "high"     # high/low


@dataclass(frozen=True, slots=True)
class AcceptanceCriteria:
    """
    Immutable acceptance criteria for synchronization.
    
    Fields:
        min_confidence:      Minimum confidence threshold [0.0, 1.0]
        max_graph_cycles:    Maximum allowed graph cycles
        require_ontology:    Require ontology consistency
        allow_partial:       Allow partial synchronization
    
    Rules:
        - All criteria must be satisfied for success
        - Criteria are applied during validation phase
    """
    min_confidence: float = 0.5
    max_graph_cycles: int = 0
    require_ontology: bool = True
    allow_partial: bool = False


# =============================================================================
# SYNCHRONIZATION REQUEST (INPUT)
# =============================================================================

@dataclass(frozen=True, slots=True)
class WorldModelSynchronizationRequest:
    """
    Canonical immutable synchronization request.
    
    Fields:
        identity:               Unique request identifier
        updated_belief_state:   Updated belief state from revision
        current_world_model:    Current world model to synchronize
        synchronization_policy: Policy configuration for this sync
        semantic_time:          Semantic time reference for the update
        provenance:             Provenance tracking for this request
    
    Rules:
        - Request must be immutable
        - All required fields must be provided
        - No runtime data in request payload
    """
    identity: str  # UUID or similar stable identifier
    updated_belief_state: dict[str, Any]  # Updated BeliefState representation
    current_world_model: dict[str, Any]   # Current WorldModel representation
    synchronization_policy: SynchronizationPolicy
    semantic_time: str | None = None      # External semantic time reference
    provenance: dict[str, Any] | None = None  # Provenance for this request


# =============================================================================
# SYNCHRONIZATION RESULT (OUTPUT)
# =============================================================================

@dataclass(frozen=True, slots=True)
class WorldModelSynchronizationResult:
    """
    Canonical immutable synchronization result.
    
    Fields:
        status:                 Result status (success/failed)
        updated_world_model:    New world model revision
        transaction_summary:    Summary of operations performed
        findings:               Typed findings from validation
        limitations:            Known limitations or constraints
        trace:                  Execution trace for audit
        world_revision_graph:   Revision lineage graph
    
    Rules:
        - Result must be immutable
        - All fields must have values (even if empty)
        - No side-effect data in result payload
    """
    status: str = "SUCCESS"  # SUCCESS, FAILED, PARTIAL_SUCCESS
    updated_world_model: dict[str, Any] = field(default_factory=dict)
    transaction_summary: dict[str, Any] = field(default_factory=dict)
    findings: tuple[dict[str, Any], ...] = field(default_factory=tuple)
    limitations: tuple[str, ...] = field(default_factory=tuple)
    trace: tuple[str, ...] = field(default_factory=tuple)
    world_revision_graph: dict[str, Any] | None = None


# =============================================================================
# TRANSACTION SUMMARY (DETAILED OPERATIONS)
# =============================================================================

@dataclass(frozen=True, slots=True)
class TransactionSummary:
    """
    Immutable transaction operation summary.
    
    Fields:
        operation_count:      Total number of operations
        entity_operations:    Entity lifecycle operations count
        relationship_operations: Relationship operations count
        ontology_operations:  Ontology evolution operations count
        start_time_ref:       Start semantic time reference
        end_time_ref:         End semantic time reference
    
    Rules:
        - Summary remains immutable after creation
        - Counts must be non-negative
    """
    operation_count: int = 0
    entity_operations: int = 0
    relationship_operations: int = 0
    ontology_operations: int = 0
    start_time_ref: str | None = None
    end_time_ref: str | None = None


# =============================================================================
# VALIDATION FINDING (TYPED)
# =============================================================================

@dataclass(frozen=True, slots=True)
class ValidationFinding:
    """
    Typed validation finding.
    
    Fields:
        kind:               Finding category
        severity:           Severity level (info/warning/error)
        description:        Human-readable explanation
        location:           Location in world model
        timestamp_ref:      Semantic time reference
    
    Rules:
        - Findings are typed and actionable
        - No silent findings allowed
    """
    kind: str  # FailureKind or custom finding type
    severity: str = "info"  # info/warning/error
    description: str = ""
    location: str | None = None
    timestamp_ref: str | None = None


# =============================================================================
# WORLD REVISION REFERENCE (EXTERNAL)
# =============================================================================

@dataclass(frozen=True, slots=True)
class WorldRevisionReference:
    """
    Reference to a previous world model revision.
    
    Fields:
        revision_id:       Unique revision identifier
        parent_revision:   Parent revision reference (if any)
        timestamp_ref:     Semantic time of revision
    
    Rules:
        - References remain immutable
        - No ownership transfer via reference
    """
    revision_id: str
    parent_revision: str | None = None  # Revision ID of parent
    timestamp_ref: str | None = None


# =============================================================================
# SYNCHRONIZATION ENGINE (INTERFACE)
# =============================================================================

@dataclass(frozen=True, slots=True)
class SynchronizationEngine:
    """
    Interface definition for world synchronization engine.
    
    This is an abstract type; actual implementations provide the
    concrete behavior. The interface ensures consistent contract
    across all synchronization operations.
    
    Methods:
        validate_request:   Validate incoming request
        compute_plan:       Compute synchronization plan
        execute_transaction: Execute transaction
        create_snapshot:    Create world snapshot
        handle_failure:     Handle failure and rollback
    
    Rules:
        - Engine remains immutable
        - No state mutation during execution
        - All operations return new results
    """
    identity: str = "world_model_synchronization_engine"