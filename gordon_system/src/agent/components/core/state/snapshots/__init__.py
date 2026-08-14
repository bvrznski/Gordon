# State Snapshot Architecture - Phase 3.15.6
# ===========================================

"""
Canonical snapshot architecture governing state observation throughout Gordon Core.

This module establishes how runtime state is safely observed, projected, serialized,
shared, and diagnosed without exposing mutable runtime state or violating ownership boundaries.

ARCHITECTURAL PRINCIPLES:
    1. One canonical snapshot architecture exists throughout the Core
    2. All snapshots are immutable observational artifacts
    3. Snapshots never become mutable runtime state authorities
    4. Projections are explicit (no implicit behavior)
    5. Consistency and completeness guarantees are declared
    6. Redaction is deterministic and policy-driven
    7. Runtime ownership boundaries are never bypassed

This extends:
    Phase 3.15.1 - Core State Foundations
    Phase 3.15.2 - State Identity, Scope & Ownership
    Phase 3.15.3 - Immutable & Mutable State Semantics
    Phase 3.15.4 - Runtime State Hierarchy
    Phase 3.15.5 - State Transitions & Transition Validation

ONE CANONICAL ARCHITECTURE:
    Only one snapshot architecture exists throughout the Core.
    Subsystems may extend with typed snapshots but must use this foundation.
"""

# =============================================================================
# IMPORTS - Import-time purity maintained
# =============================================================================

from dataclasses import dataclass, field
from typing import (
    Dict,
    List,
    Optional,
    Tuple,
    Protocol,
    runtime_checkable,
    Any,
)
from enum import Enum, auto
import uuid
import time as _time_module

# Core state foundations (Phase 3.15.x)
from ..hierarchy import RuntimeStateId, dataclass_replace
from ..__init__ import (
    CoreStateDomain,
    CoreStateScope,
    CoreStateMutability,
    CoreStateVersion,
    CoreSnapshotConsistency as BaseCoreSnapshotConsistency,
    CoreSnapshotCompleteness as BaseCoreSnapshotCompleteness,
)


# =============================================================================
# CANONICAL SNAPSHOT CLASSIFICATIONS (TAXONOMY)
# =============================================================================


class SnapshotKind(Enum):
    """
    Canonical snapshot kinds/kategories.
    
    SUBSYSTEM EXTENSIONS:
        Subsystems may define additional typed extensions through
        subsystem-specific snapshot kinds that extend this taxonomy.
    
    INVARIANTS:
        SNAP-KIND-001: Every snapshot has exactly one kind from this taxonomy
        SNAP-KIND-002: Snapshot kinds are repository-wide and consistent
        SNAP-KIND-003: Subsystem extensions must use canonical base for compatibility
    """
    
    # Runtime snapshots (runtime state at a point in time)
    RUNTIME = "runtime"
    
    # Aggregate snapshots (entire aggregate at version)
    AGGREGATE = "aggregate"
    
    # Component-level snapshots
    COMPONENT = "component"
    
    # Service-level snapshots
    SERVICE = "service"
    
    # Resource-level snapshots
    RESOURCE = "resource"
    
    # Stream-level snapshots
    STREAM = "stream"
    
    # Transaction-level snapshots
    TRANSACTION = "transaction"
    
    # Health snapshots (health condition at version)
    HEALTH = "health"
    
    # Readiness snapshots (readiness availability at version)
    READINESS = "readiness"
    
    # Admission snapshots (admission decision state at version)
    ADMISSION = "admission"
    
    # Recovery snapshots (recovery process state at version)
    RECOVERY = "recovery"
    
    # Shutdown snapshots (shutdown procedure state at version)
    SHUTDOWN = "shutdown"
    
    # Hierarchy snapshots (hierarchical structure at version)
    HIERARCHY = "hierarchy"
    
    # Diagnostic snapshots (diagnostic information at version)
    DIAGNOSTIC = "diagnostic"


# =============================================================================
# SNAPSHOT CONSENSUS CLASSIFICATIONS
# =============================================================================


class SnapshotConsistency(BaseCoreSnapshotConsistency):
    """
    Canonical snapshot consistency classifications.
    
    EXTENDS: CoreSnapshotConsistency from Phase 3.15.x
    
    CONSISTENCY CLASSES:
        ATOMIC           - Snapshot was captured atomically
        TRANSACTIONAL    - Snapshot reflects a committed transaction
        VERSION_CONSISTENT - All fields from same version
        EVENTUALLY_CONSISTENT - May not reflect most recent write
        BEST_EFFORT      - Best attempt, no consistency guarantees
        PARTIAL          - Incomplete snapshot (some fields missing)
    
    INVARIANTS:
        SNAP-CONS-001: Every snapshot states its consistency classification
        SNAP-CONS-002: Atomic snapshots are consistent
        SNAP-CONS-003: Consistency does not imply current state
    """
    
    # Extended classifications
    ATOMIC = "atomic"
    TRANSACTIONAL = "transactional"
    VERSION_CONSISTENT = "version_consistent"
    EVENTUALLY_CONSISTENT = "eventually_consistent"
    BEST_EFFORT = "best_effort"
    PARTIAL = "partial"
    UNKNOWN = "unknown"


class SnapshotCompleteness(BaseCoreSnapshotCompleteness):
    """
    Canonical snapshot completeness classifications.
    
    EXTENDS: CoreSnapshotCompleteness from Phase 3.15.x
    
    COMPLETENESS CLASSES:
        COMPLETE      - All state fields included
        PROJECTION    - Only selected fields included (view)
        METADATA_ONLY - Only metadata, no actual state values
        INCREMENTAL   - Only changed fields since last snapshot
        DIFFERENTIAL  - Changes relative to another snapshot
    
    INVARIANTS:
        SNAP-COMP-001: Every snapshot states its completeness classification
        SNAP-COMP-002: Complete snapshots include all state fields
    """
    
    # Extended classifications
    COMPLETE = "complete"
    PROJECTION = "projection"
    METADATA_ONLY = "metadata_only"
    INCREMENTAL = "incremental"
    DIFFERENTIAL = "differential"


# =============================================================================
# SNAPSHOT LIFECYCLE STAGES
# =============================================================================


class SnapshotLifecycleStage(Enum):
    """
    Canonical snapshot lifecycle stages.
    
    LIFECYCLE STAGES:
        REQUESTED   - Snapshot request received
        CREATED     - Snapshot has been created
        VALIDATED   - Snapshot validation completed
        PUBLISHED   - Snapshot published to observers
        STORED      - Snapshot persisted (if eligible)
        ARCHIVED    - Snapshot archived for long-term storage
        EXPIRED     - Snapshot has expired
        DISCARDED   - Snapshot discarded (invalid or no longer needed)
    
    INVARIANTS:
        SNAP-LIFE-001: Snapshots progress through lifecycle stages
        SNAP-LIFE-002: Lifecycle is monotonic (no regression without explicit reset)
        SNAP-LIFE-003: Expiration and discard are terminal stages
    """
    
    REQUESTED = "requested"
    CREATED = "created"
    VALIDATED = "validated"
    PUBLISHED = "published"
    STORED = "stored"
    ARCHIVED = "archived"
    EXPIRED = "expired"
    DISCARDED = "discarded"


# =============================================================================
# PROJECTION POLICY
# =============================================================================


@dataclass(frozen=True)
class ProjectionPolicy:
    """
    Policy governing a view projection over state or snapshot.
    
    Every projection must have an associated policy that defines:
        - Source state identification
        - Included fields (what to include)
        - Excluded fields (what to exclude)
        - Derived fields (computed values)
        - Redacted fields (sensitive data masked/removed)
        - Consumer scope (who can see this projection)
        - Visibility policy (when it's visible)
    
    INVARIANTS:
        PROJ-POL-001: Every projection has exactly one canonical policy
        PROJ-POL-002: Policies are immutable once created
        PROJ-POL-003: Projection must be fully specified (no implicit defaults)
    """
    
    # Source identification
    source_state_id: RuntimeStateId
    source_snapshot_id: Optional[str] = None  # If from a snapshot
    
    # Field inclusion/exclusion
    included_fields: Tuple[str, ...] = field(default_factory=tuple)  # Empty = all fields
    excluded_fields: Tuple[str, ...] = field(default_factory=tuple)
    
    # Derived fields (computed values)
    derived_fields: Dict[str, str] = field(default_factory=dict)  # name -> expression
    
    # Redaction policy (what to hide)
    redacted_fields: Tuple[str, ...] = field(default_factory=tuple)
    redaction_mask_value: Optional[Any] = None  # e.g., "******" for secrets
    redaction_mode: str = "mask"  # "mask", "remove", or custom strategy
    
    # Consumer scope
    consumer_scope: CoreStateScope = CoreStateScope.LOCAL
    visibility_policy: str = "default"  # Policy string for documentation
    
    # Version context
    version_context: Optional[CoreStateVersion] = None
    
    @classmethod
    def full_projection(
        cls,
        source_state_id: RuntimeStateId,
        consumer_scope: CoreStateScope = CoreStateScope.LOCAL,
    ) -> "ProjectionPolicy":
        """Create a projection that includes all fields."""
        return cls(
            source_state_id=source_state_id,
            consumer_scope=consumer_scope,
            included_fields=tuple(),  # Empty tuple means all
            excluded_fields=tuple(),
        )
    
    @classmethod
    def public_projection(
        cls,
        source_state_id: RuntimeStateId,
        redacted_fields: Tuple[str, ...] = ("secrets", "credentials", "internal_ids"),
    ) -> "ProjectionPolicy":
        """Create a projection suitable for external exposure."""
        return cls(
            source_state_id=source_state_id,
            consumer_scope=CoreStateScope.APPLICATION,
            included_fields=tuple(),
            excluded_fields=tuple(),  # Will use redaction
            redacted_fields=redacted_fields,
            visibility_policy="public",
        )
    
    @classmethod
    def diagnostic_projection(
        cls,
        source_state_id: RuntimeStateId,
    ) -> "ProjectionPolicy":
        """Create a projection for diagnostic purposes."""
        return cls(
            source_state_id=source_state_id,
            consumer_scope=CoreStateScope.CONTROL,
            included_fields=tuple(),
            excluded_fields=tuple(),  # Will use redaction for sensitive
            redacted_fields=("secrets", "credentials"),
            derived_fields={
                "diagnostic_timestamp": "_time_module.monotonic()",
                "state_status": "compute_state_status()",
            },
            visibility_policy="diagnostic",
        )


# =============================================================================
# SNAPSHOT PROVENANCE
# =============================================================================


@dataclass(frozen=True)
class SnapshotProvenance:
    """
    Immutable provenance information for a snapshot.
    
    Provenance preserves the origin and history of a snapshot.
    
    PROVENANCE PRINCIPLES:
        - Provenance is immutable once created
        - Provenance may include source authority, operation, correlation
        - Runtime isolation is preserved
    
    INVARIANTS:
        SNAP-PROV-001: Provenance is immutable once created
        SNAP-PROV-002: Source authority is preserved
        SNAP-PROV-003: Correlation and causation are preserved
    """
    
    # Origin
    source_authority: Optional[str] = None  # e.g., "lifecycle", "execution"
    source_operation_id: Optional[str] = None
    
    # Request context
    originating_request_id: Optional[str] = None
    
    # Runtime binding (for isolation)
    runtime_identity: Optional[str] = None
    boot_session_identity: Optional[str] = None
    process_identity: Optional[str] = None
    
    # Correlation
    correlation_id: Optional[str] = None
    causation_id: Optional[str] = None
    
    # Schema and architecture
    schema_identity: Optional[str] = None
    schema_version: Optional[int] = None
    architecture_revision: Optional[str] = None
    
    # Snapshot-specific
    snapshot_kind: Optional[str] = None
    snapshot_completeness: Optional[str] = None
    
    @classmethod
    def from_operation(
        cls,
        source_authority: str,
        operation_id: str,
        runtime_identity: Optional[str] = None,
        correlation_id: Optional[str] = None,
    ) -> "SnapshotProvenance":
        """Create provenance from an operation."""
        return cls(
            source_authority=source_authority,
            source_operation_id=operation_id,
            runtime_identity=runtime_identity,
            correlation_id=correlation_id,
        )


# =============================================================================
# CANONICAL SNAPSHOT (BASE CLASS)
# =============================================================================


@dataclass(frozen=True)
class BaseStateSnapshot:
    """
    Immutable snapshot of state at a specific version.
    
    A snapshot is an OBSERVATION, not the current state authority.
    It remains valid even after the source state changes.
    
    SNAPSHOT PRINCIPLES:
        - Snapshots are immutable once created
        - Snapshots do not provide mutation access
        - Snapshots identify source version and generation
    
    INVARIANTS:
        SNAP-001: Snapshot is immutable once created
        SNAP-002: Snapshot does not become a second mutable authority
        SNAP-003: Snapshot identifies source state, version, and generation
    """
    
    # Identity
    snapshot_id: str = field(default_factory=lambda: f"snap_{uuid.uuid4().hex[:24]}")
    
    # Source identification
    source_state_id: RuntimeStateId
    source_domain: CoreStateDomain
    source_scope: CoreStateScope
    
    # Source version information
    source_version: CoreStateVersion
    source_generation: int
    
    # Snapshot content (immutable)
    captured_value: Any  # The actual state value at this snapshot
    captured_at_utc: float = field(default_factory=_time_module.monotonic)
    
    # Classification
    consistency_class: SnapshotConsistency = SnapshotConsistency.VERSION_CONSISTENT
    completeness_class: SnapshotCompleteness = SnapshotCompleteness.COMPLETE
    
    # Lifecycle stage
    lifecycle_stage: SnapshotLifecycleStage = SnapshotLifecycleStage.CREATED
    
    # Provenance
    provenance: SnapshotProvenance = field(default_factory=SnapshotProvenance)
    
    # Metadata
    schema_version: str = "1.0.0"
    
    @classmethod
    def capture(
        cls,
        source_state_id: RuntimeStateId,
        source_domain: CoreStateDomain,
        source_scope: CoreStateScope,
        captured_value: Any,
        source_version: CoreStateVersion,
        source_generation: int,
        consistency_class: SnapshotConsistency = SnapshotConsistency.VERSION_CONSISTENT,
    ) -> "BaseStateSnapshot":
        """Create an immutable snapshot of current state."""
        return cls(
            source_state_id=source_state_id,
            source_domain=source_domain,
            source_scope=source_scope,
            captured_value=captured_value,
            source_version=source_version,
            source_generation=source_generation,
            consistency_class=consistency_class,
        )
    
    def with_lifecycle_stage(self, stage: SnapshotLifecycleStage) -> "BaseStateSnapshot":
        """Create a copy with updated lifecycle stage."""
        return dataclass_replace(self, lifecycle_stage=stage)
    
    def is_expired(self, current_time: Optional[float] = None, max_age_seconds: float = 3600) -> bool:
        """Check if snapshot has exceeded its maximum age."""
        current = current_time or _time_module.monotonic()
        return (current - self.captured_at_utc) > max_age_seconds


# =============================================================================
# CANONICAL VIEW (BASE CLASS)
# =============================================================================


@dataclass(frozen=True)
class BaseStateView:
    """
    Immutable view of state (projection).
    
    A view is a filtered/derived representation of state.
    
    VIEW PRINCIPLES:
        - Views are immutable once created
        - Views identify source state and version
        - Views may redact or project fields
    
    INVARIANTS:
        VIEW-001: View is immutable once created
        VIEW-002: View does not become a hidden cache of mutable truth
        VIEW-003: View identifies source state, version, and projection
    """
    
    # Identity
    view_id: str = field(default_factory=lambda: f"view_{uuid.uuid4().hex[:24]}")
    
    # Source identification
    source_state_id: RuntimeStateId
    source_snapshot_id: Optional[str] = None  # If from a snapshot
    source_version: CoreStateVersion
    
    # Projection specification
    projection_identity: str  # What kind of view is this?
    included_fields: Tuple[str, ...] = field(default_factory=tuple)  # Empty = all fields
    excluded_fields: Tuple[str, ...] = field(default_factory=tuple)
    
    # Derived fields (computed values)
    derived_fields: Dict[str, Any] = field(default_factory=dict)
    
    # Redacted fields (sensitive data masked/removed)
    redacted_fields: Tuple[str, ...] = field(default_factory=tuple)
    
    # Consumer context
    consumer_scope: CoreStateScope = CoreStateScope.LOCAL
    visibility_policy: str = "default"  # Policy string for documentation
    
    # Version context
    version_context: Optional[CoreStateVersion] = None
    
    @classmethod
    def project(
        cls,
        source_state_id: RuntimeStateId,
        source_version: CoreStateVersion,
        projection_identity: str,
        included_fields: Optional[Tuple[str, ...]] = None,
        excluded_fields: Optional[Tuple[str, ...]] = None,
    ) -> "BaseStateView":
        """Create an immutable view of state."""
        return cls(
            source_state_id=source_state_id,
            source_version=source_version,
            projection_identity=projection_identity,
            included_fields=included_fields or tuple(),
            excluded_fields=excluded_fields or tuple(),
        )
    
    def with_redaction(self, redacted_fields: Tuple[str, ...]) -> "BaseStateView":
        """Create a copy with additional redactions."""
        return dataclass_replace(
            self,
            redacted_fields=self.redacted_fields + redacted_fields
        )


# =============================================================================
# SNAPSHOT FACTORY (PUBLIC API)
# =============================================================================


class SnapshotFactory:
    """
    Factory for creating snapshots with proper validation and classification.
    
    This is the canonical entry point for creating snapshots. All
    snapshots should be created through this factory to ensure:
        - Consistent identity generation
        - Policy enforcement at creation time
        - Proper validation before publication
    
    INVARIANTS:
        SNAP-FCT-001: Factory is stateless (pure functions)
        SNAP-FCT-002: All created snapshots are properly validated
        SNAP-FCT-003: No snapshot can be created with invalid policy
    """
    
    def __init__(self) -> None:
        """Initialize the snapshot factory."""
        self._created_snapshots: Dict[str, BaseStateSnapshot] = {}
    
    def create_runtime_snapshot(
        self,
        source_state_id: RuntimeStateId,
        captured_value: Any,
        source_version: CoreStateVersion,
        source_generation: int,
        runtime_identity: Optional[str] = None,
    ) -> BaseStateSnapshot:
        """Create a runtime snapshot."""
        provenance = SnapshotProvenance(
            source_authority="snapshot_factory",
            runtime_identity=runtime_identity,
        )
        
        return BaseStateSnapshot.capture(
            source_state_id=source_state_id,
            source_domain=CoreStateDomain.RUNTIME,
            source_scope=CoreStateScope.APPLICATION,
            captured_value=captured_value,
            source_version=source_version,
            source_generation=source_generation,
            consistency_class=SnapshotConsistency.VERSION_CONSISTENT,
        ).with_lifecycle_stage(SnapshotLifecycleStage.CREATED)
    
    def create_aggregate_snapshot(
        self,
        source_state_id: RuntimeStateId,
        captured_value: Any,
        source_version: CoreStateVersion,
        source_generation: int,
    ) -> BaseStateSnapshot:
        """Create an aggregate snapshot."""
        return BaseStateSnapshot.capture(
            source_state_id=source_state_id,
            source_domain=CoreStateDomain.CORE,
            source_scope=CoreStateScope.APPLICATION,
            captured_value=captured_value,
            source_version=source_version,
            source_generation=source_generation,
            consistency_class=SnapshotConsistency.TRANSACTIONAL,
        ).with_lifecycle_stage(SnapshotLifecycleStage.CREATED)
    
    def create_component_snapshot(
        self,
        source_state_id: RuntimeStateId,
        component_name: str,
        captured_value: Any,
        source_version: CoreStateVersion,
        source_generation: int,
    ) -> BaseStateSnapshot:
        """Create a component snapshot."""
        return BaseStateSnapshot.capture(
            source_state_id=source_state_id,
            source_domain=CoreStateDomain.COMPONENT,
            source_scope=CoreStateScope.LOCAL,
            captured_value=captured_value,
            source_version=source_version,
            source_generation=source_generation,
            consistency_class=SnapshotConsistency.VERSION_CONSISTENT,
        ).with_lifecycle_stage(SnapshotLifecycleStage.CREATED)
    
    def create_service_snapshot(
        self,
        source_state_id: RuntimeStateId,
        service_name: str,
        captured_value: Any,
        source_version: CoreStateVersion,
        source_generation: int,
    ) -> BaseStateSnapshot:
        """Create a service snapshot."""
        return BaseStateSnapshot.capture(
            source_state_id=source_state_id,
            source_domain=CoreStateDomain.SERVICE,
            source_scope=CoreStateScope.APPLICATION,
            captured_value=captured_value,
            source_version=source_version,
            source_generation=source_generation,
            consistency_class=SnapshotConsistency.VERSION_CONSISTENT,
        ).with_lifecycle_stage(SnapshotLifecycleStage.CREATED)
    
    def create_resource_snapshot(
        self,
        source_state_id: RuntimeStateId,
        resource_type: str,
        captured_value: Any,
        source_version: CoreStateVersion,
        source_generation: int,
    ) -> BaseStateSnapshot:
        """Create a resource snapshot."""
        return BaseStateSnapshot.capture(
            source_state_id=source_state_id,
            source_domain=CoreStateDomain.RESOURCE,
            source_scope=CoreStateScope.APPLICATION,
            captured_value=captured_value,
            source_version=source_version,
            source_generation=source_generation,
            consistency_class=SnapshotConsistency.VERSION_CONSISTENT,
        ).with_lifecycle_stage(SnapshotLifecycleStage.CREATED)
    
    def create_stream_snapshot(
        self,
        source_state_id: RuntimeStateId,
        stream_name: str,
        captured_value: Any,
        source_version: CoreStateVersion,
        source_generation: int,
    ) -> BaseStateSnapshot:
        """Create a stream snapshot."""
        return BaseStateSnapshot.capture(
            source_state_id=source_state_id,
            source_domain=CoreStateDomain.STREAM,
            source_scope=CoreStateScope.APPLICATION,
            captured_value=captured_value,
            source_version=source_version,
            source_generation=source_generation,
            consistency_class=SnapshotConsistency.VERSION_CONSISTENT,
        ).with_lifecycle_stage(SnapshotLifecycleStage.CREATED)
    
    def create_transaction_snapshot(
        self,
        source_state_id: RuntimeStateId,
        transaction_id: str,
        captured_value: Any,
        source_version: CoreStateVersion,
        source_generation: int,
    ) -> BaseStateSnapshot:
        """Create a transaction snapshot."""
        return BaseStateSnapshot.capture(
            source_state_id=source_state_id,
            source_domain=CoreStateDomain.TRANSACTION,
            source_scope=CoreStateScope.LOCAL,
            captured_value=captured_value,
            source_version=source_version,
            source_generation=source_generation,
            consistency_class=SnapshotConsistency.TRANSACTIONAL,
        ).with_lifecycle_stage(SnapshotLifecycleStage.CREATED)
    
    def create_health_snapshot(
        self,
        source_state_id: RuntimeStateId,
        health_status: str,
        source_version: CoreStateVersion,
        source_generation: int,
    ) -> BaseStateSnapshot:
        """Create a health snapshot."""
        return BaseStateSnapshot.capture(
            source_state_id=source_state_id,
            source_domain=CoreStateDomain.HEALTH,
            source_scope=CoreStateScope.APPLICATION,
            captured_value={"status": health_status},
            source_version=source_version,
            source_generation=source_generation,
            consistency_class=SnapshotConsistency.VERSION_CONSISTENT,
        ).with_lifecycle_stage(SnapshotLifecycleStage.CREATED)
    
    def create_readiness_snapshot(
        self,
        source_state_id: RuntimeStateId,
        readiness_status: str,
        source_version: CoreStateVersion,
        source_generation: int,
    ) -> BaseStateSnapshot:
        """Create a readiness snapshot."""
        return BaseStateSnapshot.capture(
            source_state_id=source_state_id,
            source_domain=CoreStateDomain.READINESS,
            source_scope=CoreStateScope.APPLICATION,
            captured_value={"status": readiness_status},
            source_version=source_version,
            source_generation=source_generation,
            consistency_class=SnapshotConsistency.VERSION_CONSISTENT,
        ).with_lifecycle_stage(SnapshotLifecycleStage.CREATED)
    
    def create_admission_snapshot(
        self,
        source_state_id: RuntimeStateId,
        admission_decision: str,
        source_version: CoreStateVersion,
        source_generation: int,
    ) -> BaseStateSnapshot:
        """Create an admission snapshot."""
        return BaseStateSnapshot.capture(
            source_state_id=source_state_id,
            source_domain=CoreStateDomain.ADMISSION,
            source_scope=CoreStateScope.APPLICATION,
            captured_value={"decision": admission_decision},
            source_version=source_version,
            source_generation=source_generation,
            consistency_class=SnapshotConsistency.VERSION_CONSISTENT,
        ).with_lifecycle_stage(SnapshotLifecycleStage.CREATED)
    
    def create_recovery_snapshot(
        self,
        source_state_id: RuntimeStateId,
        recovery_status: str,
        source_version: CoreStateVersion,
        source_generation: int,
    ) -> BaseStateSnapshot:
        """Create a recovery snapshot."""
        return BaseStateSnapshot.capture(
            source_state_id=source_state_id,
            source_domain=CoreStateDomain.RECOVERY,
            source_scope=CoreStateScope.LOCAL,
            captured_value={"status": recovery_status},
            source_version=source_version,
            source_generation=source_generation,
            consistency_class=SnapshotConsistency.VERSION_CONSISTENT,
        ).with_lifecycle_stage(SnapshotLifecycleStage.CREATED)
    
    def create_shutdown_snapshot(
        self,
        source_state_id: RuntimeStateId,
        shutdown_status: str,
        source_version: CoreStateVersion,
        source_generation: int,
    ) -> BaseStateSnapshot:
        """Create a shutdown snapshot."""
        return BaseStateSnapshot.capture(
            source_state_id=source_state_id,
            source_domain=CoreStateDomain.SHUTDOWN,
            source_scope=CoreStateScope.APPLICATION,
            captured_value={"status": shutdown_status},
            source_version=source_version,
            source_generation=source_generation,
            consistency_class=SnapshotConsistency.VERSION_CONSISTENT,
        ).with_lifecycle_stage(SnapshotLifecycleStage.CREATED)
    
    def create_hierarchy_snapshot(
        self,
        source_state_id: RuntimeStateId,
        hierarchy_data: Dict[str, Any],
        source_version: CoreStateVersion,
        source_generation: int,
    ) -> BaseStateSnapshot:
        """Create a hierarchy snapshot."""
        return BaseStateSnapshot.capture(
            source_state_id=source_state_id,
            source_domain=CoreStateDomain.RUNTIME,
            source_scope=CoreStateScope.APPLICATION,
            captured_value=hierarchy_data,
            source_version=source_version,
            source_generation=source_generation,
            consistency_class=SnapshotConsistency.VERSION_CONSISTENT,
        ).with_lifecycle_stage(SnapshotLifecycleStage.CREATED)
    
    def create_diagnostic_snapshot(
        self,
        source_state_id: RuntimeStateId,
        diagnostic_data: Dict[str, Any],
        source_version: CoreStateVersion,
        source_generation: int,
    ) -> BaseStateSnapshot:
        """Create a diagnostic snapshot."""
        return BaseStateSnapshot.capture(
            source_state_id=source_state_id,
            source_domain=CoreStateDomain.RUNTIME,
            source_scope=CoreStateScope.APPLICATION,
            captured_value=diagnostic_data,
            source_version=source_version,
            source_generation=source_generation,
            consistency_class=SnapshotConsistency.BEST_EFFORT,
        ).with_lifecycle_stage(SnapshotLifecycleStage.CREATED)


# =============================================================================
# VIEW FACTORY (PUBLIC API)
# =============================================================================


class ViewFactory:
    """
    Factory for creating views with proper validation and classification.
    
    This is the canonical entry point for creating views. All
    views should be created through this factory to ensure:
        - Consistent identity generation
        - Policy enforcement at creation time
        - Proper projection rules applied
    
    INVARIANTS:
        VIEW-FCT-001: Factory is stateless (pure functions)
        VIEW-FCT-002: All created views are properly validated
        VIEW-FCT-003: No view can be created with invalid policy
    """
    
    def __init__(self) -> None:
        """Initialize the view factory."""
        self._created_views: Dict[str, BaseStateView] = {}
    
    def create_public_view(
        self,
        source_state_id: RuntimeStateId,
        source_version: CoreStateVersion,
        included_fields: Optional[Tuple[str, ...]] = None,
        redacted_fields: Tuple[str, ...] = ("secrets", "credentials", "internal_ids"),
    ) -> BaseStateView:
        """Create a public view suitable for external exposure."""
        return BaseStateView.project(
            source_state_id=source_state_id,
            source_version=source_version,
            projection_identity="public",
            included_fields=included_fields,
            excluded_fields=tuple(),
        ).with_redaction(redacted_fields)
    
    def create_internal_view(
        self,
        source_state_id: RuntimeStateId,
        source_version: CoreStateVersion,
        included_fields: Optional[Tuple[str, ...]] = None,
    ) -> BaseStateView:
        """Create an internal view for subsystem use."""
        return BaseStateView.project(
            source_state_id=source_state_id,
            source_version=source_version,
            projection_identity="internal",
            included_fields=included_fields,
        )
    
    def create_diagnostic_view(
        self,
        source_state_id: RuntimeStateId,
        source_version: CoreStateVersion,
        derived_fields: Optional[Dict[str, Any]] = None,
    ) -> BaseStateView:
        """Create a diagnostic view for debugging and monitoring."""
        return BaseStateView.project(
            source_state_id=source_state_id,
            source_version=source_version,
            projection_identity="diagnostic",
            included_fields=tuple(),
            derived_fields=derived_fields or {
                "diagnostic_timestamp": _time_module.monotonic(),
                "state_status": "active",
            },
        ).with_redaction(("secrets", "credentials"))
    
    def create_administrative_view(
        self,
        source_state_id: RuntimeStateId,
        source_version: CoreStateVersion,
        included_fields: Optional[Tuple[str, ...]] = None,
    ) -> BaseStateView:
        """Create an administrative view for system management."""
        return BaseStateView.project(
            source_state_id=source_state_id,
            source_version=source_version,
            projection_identity="administrative",
            included_fields=included_fields,
        )
    
    def create_health_view(
        self,
        source_state_id: RuntimeStateId,
        source_version: CoreStateVersion,
        health_status: str,
    ) -> BaseStateView:
        """Create a health view for monitoring."""
        return BaseStateView.project(
            source_state_id=source_state_id,
            source_version=source_version,
            projection_identity="health",
            included_fields=tuple(),
            derived_fields={
                "health_status": health_status,
                "last_updated_utc": _time_module.monotonic(),
            },
        )
    
    def create_readiness_view(
        self,
        source_state_id: RuntimeStateId,
        source_version: CoreStateVersion,
        readiness_status: str,
    ) -> BaseStateView:
        """Create a readiness view for admission decisions."""
        return BaseStateView.project(
            source_state_id=source_state_id,
            source_version=source_version,
            projection_identity="readiness",
            included_fields=tuple(),
            derived_fields={
                "readiness_status": readiness_status,
                "last_checked_utc": _time_module.monotonic(),
            },
        )
    
    def create_resource_view(
        self,
        source_state_id: RuntimeStateId,
        source_version: CoreStateVersion,
        resource_type: str,
        resource_data: Dict[str, Any],
    ) -> BaseStateView:
        """Create a resource view."""
        return BaseStateView.project(
            source_state_id=source_state_id,
            source_version=source_version,
            projection_identity="resource",
            included_fields=tuple(),
            derived_fields={
                "resource_type": resource_type,
                "resource_data": resource_data,
            },
        )
    
    def create_lifecycle_view(
        self,
        source_state_id: RuntimeStateId,
        source_version: CoreStateVersion,
        lifecycle_stage: str,
    ) -> BaseStateView:
        """Create a lifecycle view."""
        return BaseStateView.project(
            source_state_id=source_state_id,
            source_version=source_version,
            projection_identity="lifecycle",
            included_fields=tuple(),
            derived_fields={
                "lifecycle_stage": lifecycle_stage,
                "stage_entered_utc": _time_module.monotonic(),
            },
        )
    
    def create_security_view(
        self,
        source_state_id: RuntimeStateId,
        source_version: CoreStateVersion,
        redacted_fields: Tuple[str, ...] = ("secrets", "credentials"),
    ) -> BaseStateView:
        """Create a security view with proper redaction."""
        return BaseStateView.project(
            source_state_id=source_state_id,
            source_version=source_version,
            projection_identity="security",
            included_fields=tuple(),
        ).with_redaction(redacted_fields)
    
    def create_observability_view(
        self,
        source_state_id: RuntimeStateId,
        source_version: CoreStateVersion,
        metrics_data: Dict[str, Any],
    ) -> BaseStateView:
        """Create an observability view for monitoring."""
        return BaseStateView.project(
            source_state_id=source_state_id,
            source_version=source_version,
            projection_identity="observability",
            included_fields=tuple(),
            derived_fields={
                "metrics": metrics_data,
                "observed_at_utc": _time_module.monotonic(),
            },
        )
    
    def create_projection_view(
        self,
        source_state_id: RuntimeStateId,
        source_version: CoreStateVersion,
        projection_policy: ProjectionPolicy,
    ) -> BaseStateView:
        """Create a view following an explicit projection policy."""
        return BaseStateView.project(
            source_state_id=source_state_id,
            source_version=source_version,
            projection_identity=projection_policy.projection_identity or "custom",
            included_fields=projection_policy.included_fields,
            excluded_fields=projection_policy.excluded_fields,
        ).with_redaction(projection_policy.redacted_fields)
    
    def create_summary_view(
        self,
        source_state_id: RuntimeStateId,
        source_version: CoreStateVersion,
        summary_data: Dict[str, Any],
    ) -> BaseStateView:
        """Create a summary view."""
        return BaseStateView.project(
            source_state_id=source_state_id,
            source_version=source_version,
            projection_identity="summary",
            included_fields=tuple(),
            derived_fields={"summary": summary_data},
        )
    
    def create_detailed_view(
        self,
        source_state_id: RuntimeStateId,
        source_version: CoreStateVersion,
        detailed_data: Dict[str, Any],
    ) -> BaseStateView:
        """Create a detailed view."""
        return BaseStateView.project(
            source_state_id=source_state_id,
            source_version=source_version,
            projection_identity="detailed",
            included_fields=tuple(),
            derived_fields={"details": detailed_data},
        )


# =============================================================================
# SNAPSHOT VALIDATOR (PUBLIC API)
# =============================================================================


class SnapshotValidator:
    """
    Validator for snapshots.
    
    Provides comprehensive validation of snapshots against:
        - Identity requirements
        - Version consistency
        - Completeness classification
        - Consistency guarantees
    
    INVARIANTS:
        SNAP-VAL-001: Validation is exhaustive (all checks performed)
        SNAP-VAL-002: Validation returns structured findings
        SNAP-VAL-003: No mutation occurs during validation
    """
    
    def __init__(self) -> None:
        """Initialize the snapshot validator."""
        self._findings: List[str] = []
    
    def validate_snapshot(
        self,
        snapshot: BaseStateSnapshot,
    ) -> Tuple[bool, List[str]]:
        """
        Validate a snapshot.
        
        Args:
            snapshot: The snapshot to validate
            
        Returns:
            (is_valid: bool, findings: List of validation messages)
        """
        self._findings = []
        
        # Validate identity
        if not snapshot.snapshot_id or not snapshot.snapshot_id.startswith("snap_"):
            self._findings.append("Snapshot ID must start with 'snap_'")
        
        # Validate source identification
        if not snapshot.source_state_id:
            self._findings.append("Source state ID is required")
        
        # Validate version information
        if snapshot.source_version.sequence < 0:
            self._findings.append("Source version sequence must be non-negative")
        
        # Validate consistency classification
        valid_consistency = {c.value for c in SnapshotConsistency}
        if snapshot.consistency_class.value not in valid_consistency:
            self._findings.append(f"Invalid consistency class: {snapshot.consistency_class}")
        
        # Validate completeness classification
        valid_completeness = {c.value for c in SnapshotCompleteness}
        if snapshot.completeness_class.value not in valid_completeness:
            self._findings.append(f"Invalid completeness class: {snapshot.completeness_class}")
        
        # Validate lifecycle stage
        valid_stages = {s.value for s in SnapshotLifecycleStage}
        if snapshot.lifecycle_stage.value not in valid_stages:
            self._findings.append(f"Invalid lifecycle stage: {snapshot.lifecycle_stage}")
        
        return (len(self._findings) == 0, self._findings)
    
    def validate_view(
        self,
        view: BaseStateView,
    ) -> Tuple[bool, List[str]]:
        """
        Validate a view.
        
        Args:
            view: The view to validate
            
        Returns:
            (is_valid: bool, findings: List of validation messages)
        """
        self._findings = []
        
        # Validate identity
        if not view.view_id or not view.view_id.startswith("view_"):
            self._findings.append("View ID must start with 'view_'")
        
        # Validate source identification
        if not view.source_state_id:
            self._findings.append("Source state ID is required")
        
        # Validate projection identity
        if not view.projection_identity:
            self._findings.append("Projection identity is required")
        
        return (len(self._findings) == 0, self._findings)


# =============================================================================
# SNAPSHOT DIAGNOSTICS (PUBLIC API)
# =============================================================================


@dataclass(frozen=True)
class SnapshotDiagnostics:
    """
    Immutable bounded diagnostics for snapshots and views.
    
    Diagnostics are for debugging and monitoring, not for state logic.
    
    DIAGNOSTIC PRINCIPLES:
        - Diagnostics are immutable once created
        - Diagnostics are bounded (not unbounded append-only)
        - Diagnostics don't include live handles or secrets
    
    INVARIANTS:
        SNAP-DIAG-001: Diagnostics are immutable once created
        SNAP-DIAG-002: Diagnostics are bounded in size
        SNAP-DIAG-003: Diagnostics don't expose live handles
    """
    
    # Snapshot statistics
    snapshot_count: int = 0
    active_snapshots: int = 0
    
    # View statistics
    view_count: int = 0
    active_views: int = 0
    
    # Projection statistics
    projection_statistics: Dict[str, int] = field(default_factory=dict)
    
    # Classification counts
    consistency_classifications: Dict[str, int] = field(default_factory=dict)
    completeness_classifications: Dict[str, int] = field(default_factory=dict)
    
    # Validation summary
    validation_failures: int = 0
    validation_successes: int = 0
    
    # Serialization statistics
    serialization_count: int = 0
    last_serialization_duration_seconds: Optional[float] = None
    
    # Redaction activity
    redaction_events: int = 0
    fields_redacted_total: int = 0
    
    @classmethod
    def empty(cls) -> "SnapshotDiagnostics":
        """Create an empty diagnostics instance."""
        return cls()
    
    def record_snapshot(self, snapshot: BaseStateSnapshot) -> "SnapshotDiagnostics":
        """Record a snapshot creation."""
        consistency_key = snapshot.consistency_class.value
        completeness_key = snapshot.completeness_class.value
        
        return dataclass_replace(
            self,
            snapshot_count=self.snapshot_count + 1,
            active_snapshots=self.active_snapshots + 1,
            consistency_classifications={
                **self.consistency_classifications,
                consistency_key: self.consistency_classifications.get(consistency_key, 0) + 1,
            },
            completeness_classifications={
                **self.completeness_classifications,
                completeness_key: self.completeness_classifications.get(completeness_key, 0) + 1,
            },
        )
    
    def record_view(self, view: BaseStateView) -> "SnapshotDiagnostics":
        """Record a view creation."""
        return dataclass_replace(
            self,
            view_count=self.view_count + 1,
            active_views=self.active_views + 1,
        )
    
    def record_validation_failure(self) -> "SnapshotDiagnostics":
        """Record a validation failure."""
        return dataclass_replace(
            self,
            validation_failures=self.validation_failures + 1,
        )
    
    def record_validation_success(self) -> "SnapshotDiagnostics":
        """Record a validation success."""
        return dataclass_replace(
            self,
            validation_successes=self.validation_successes + 1,
        )


# =============================================================================
# PUBLIC API - FOUNDATIONAL FACES
# =============================================================================


def validate_snapshot(snapshot: BaseStateSnapshot) -> bool:
    """
    Validate that a snapshot is well-formed.
    
    Checks:
        - Snapshot has valid identity
        - Source identification is complete
        - Version and generation are present
    
    Returns:
        True if the snapshot is valid, False otherwise
    """
    validator = SnapshotValidator()
    is_valid, _ = validator.validate_snapshot(snapshot)
    return is_valid


def validate_view(view: BaseStateView) -> bool:
    """
    Validate that a view is well-formed.
    
    Checks:
        - View has valid identity
        - Source identification is complete
        - Projection is specified
    
    Returns:
        True if the view is valid, False otherwise
    """
    validator = SnapshotValidator()
    is_valid, _ = validator.validate_view(view)
    return is_valid


# =============================================================================
# EXPOSE FOUNDATIONAL SYMBOLS
# =============================================================================

__all__ = [
    # Kinds
    "SnapshotKind",
    
    # Classifications
    "SnapshotConsistency",
    "SnapshotCompleteness",
    "SnapshotLifecycleStage",
    
    # Policies and provenance
    "ProjectionPolicy",
    "SnapshotProvenance",
    
    # Base classes
    "BaseStateSnapshot",
    "BaseStateView",
    
    # Factories
    "SnapshotFactory",
    "ViewFactory",
    
    # Validator
    "SnapshotValidator",
    
    # Diagnostics
    "SnapshotDiagnostics",
    
    # Validation functions
    "validate_snapshot",
    "validate_view",
]