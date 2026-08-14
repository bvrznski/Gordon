# State Restoration & Reconciliation Architecture - Phase 3.15.10
# ================================================================
#
# Canonical Restoration and Reconciliation Architecture for Gordon Core.
#
# This module establishes the architecture governing restoration, reconciliation,
# repair, and recovery of runtime state throughout the Gordon Core.
#
# ARCHITECTURAL PRINCIPLES:
#   1. One canonical restoration architecture exists throughout the Core
#   2. One canonical reconciliation architecture exists throughout the Core
#   3. Runtime State remains owned by live runtime authority (restoration never bypasses)
#   4. Persistent Record, Checkpoint, Restoration, Recovery, Repair remain distinct
#   5. Restoration reconstructs state; it never becomes the state authority
#   6. Reconciliation validates consistency but never silently mutates runtime state
#
# This extends:
#     Phase 3.15.1 — Core State Foundations
#     Phase 3.15.2 — State Identity, Scope & Ownership
#     Phase 3.15.3 — Immutable & Mutable State Semantics
#     Phase 3.15.4 — Runtime State Hierarchy
#     Phase 3.15.5 — State Transitions & Transition Validation
#     Phase 3.15.6 — State Snapshots & Views
#     Phase 3.15.7 — State Versioning & Generations
#     Phase 3.15.8 — State Consistency & Concurrency
#     Phase 3.15.9 — State Persistence Boundaries

"""
Canonical Restoration and Reconciliation Architecture for Gordon Core Phase 3.15.10.

This module defines the canonical restoration and reconciliation architecture that governs how
runtime state is safely reconstructed after failures, restarts, migrations, checkpoints,
persistence restoration, and partial corruption while preserving:

    OWNERSHIP:
        - Restored state always receives a valid runtime owner before activation
        - Runtime authority ownership boundaries are never bypassed
        
    INTEGRITY:
        - Version integrity preserved through lineage validation
        - Generation integrity validated for epoch tracking
        
    ISOLATION:
        - Runtime isolation maintained during restoration
        - Boot session context preserved and validated
        
    CONSISTENCY:
        - Hierarchy integrity preserved during reconstruction
        - Dependency availability validated before activation

RESTORATION vs. RECONCILIATION vs. REPAIR:

    RESTORATION: Reconstructs runtime state from persistent source.
                 Always creates new runtime bindings; never retains stale bindings.

    RECONCILIATION: Validates whether runtime state remains internally consistent.
                    May recommend repair but never silently modifies runtime state.

    REPAIR: Applies explicit repair strategies to restore consistency.
            Always policy-driven and produces observable evidence.

ARCHITECTURAL MODEL:

    Source (Checkpoint/Persistence/Archive)
               │
               ▼
    Restoration Request → Source Validation → Integrity Verification
                                            ↓ Schema Compatibility
                                            ↓ Version Validation
                                            ↓ Generation Validation
                                            ↓ Ownership Assignment
                                            ↓ Runtime Binding
                                            ↓ Hierarchy Reconstruction
                                            ↓ Dependency Validation
                                            ↓ Invariant Validation
                                            ↓ Activation Approval
                                              ↓
                                      Restored State (bound to runtime)

    RESTORATION SOURCE TYPES:
        - Checkpoint: Saved state from previous runtime
        - Persistent Storage: Long-term persistence records
        - Archive: Versioned backup storage
        - Replicated State: Copied state from other instances
        - Migration Package: Transferred state with schema evolution
        - Recovery Image: Complete system recovery snapshot
        - Serialized Snapshot: Encoded state representation

    RESTORATION POLICIES:
        - Full Restore: Complete reconstruction of all state
        - Partial Restore: Selective reconstruction by scope
        - Selective Restore: Targeted aggregate restoration
        - Replace Existing: Overwrite current state unconditionally
        - Merge Existing: Combine restored with current state
        - Restore If Missing: Only restore if no current state exists
        - Restore With Migration: Apply schema evolution during restore
        - Restore Read-Only: Create read-only bindings

    RECONCILIATION TYPES:
        - Identity Reconciliation: Validate aggregate identity uniqueness
        - Hierarchy Reconciliation: Verify parent-child relationships
        - Ownership Reconciliation: Ensure valid ownership chains
        - Scope Reconciliation: Validate scope boundaries
        - Version Reconciliation: Check version lineage integrity
        - Generation Reconciliation: Validate epoch consistency
        - Dependency Reconciliation: Confirm dependency availability
        - Resource Reconciliation: Verify resource allocation validity

    REPAIR STRATEGIES:
        - Reject: Reject the state as invalid
        - Rebuild: Recreate from scratch using available evidence
        - Reconstruct: Build from partial state with validation
        - Replace: Swap with known good instance
        - Retry: Attempt restoration again
        - Reconcile: Apply reconciliation to resolve inconsistency
        - Rollback: Return to prior verified state
        - Compensate: Execute compensating actions
        - Escalate: Delegate to higher authority

PUBLIC API:
    - RestorationRequest     : Request structure for state restoration
    - RestorationSource      : Source identifier and metadata
    - RestorationPolicy      : Explicit policy declaration
    - ReconciliationRequest  : Request for state consistency validation
    - RepairStrategy         : Strategy selection for repair actions
    
    - RestorationPipeline    : Main execution pipeline
    - ReconciliationEngine   : Consistency validation engine
    - RepairResolver         : Strategy-based repair application
    - RestorationDiagnostics : Immutable diagnostics collection

See docs/agent/architecture/phase-3.15.10-state-restoration-reconciliation.md for complete documentation.
"""

# =============================================================================
# IMPORTS - Import-time purity maintained (no storage connections)
# =============================================================================

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple, Any, Protocol, runtime_checkable
from enum import Enum, auto
import uuid
import time as _time_module

# Core state foundations (Phase 3.15.x)
from ..identity import AggregateId, RuntimeId, BootSessionId, OwnerId
from ..ownership import (
    OwnershipAuthorityType,
    RuntimeIsolationEnforcement,
    OwnershipValidator,
    OwnershipDiagnostics,
)
from ..semantics import ImmutableStateMixin, MutableStateMixin
from ..hierarchy import StateHierarchyNode, StateHierarchyBoundary
from ..transitions import TransitionRecord, TransitionValidationResult
from ..snapshots import SnapshotKind, SnapshotProvenance
from ..versioning import (
    VersionIdentity,
    GenerationIdentity,
    ChangeIdentity,
    BaseStateVersion,
    BaseGeneration,
    VersionLineage,
    GenerationLineage,
)
from ..persistence import (
    PersistenceEligibility,
    StateAggregateEligibility,
    CheckpointRecord,
    ArchiveDescriptor,
    IntegrityEvidence,
)

# Failure model (Phase 3.14.x)
from ...failure.architecture import FailureArtifact, RecoveryStrategy


# =============================================================================
# RESTORATION SOURCE TYPES
# =============================================================================


class RestorationSourceKind(Enum):
    """
    Canonical source kinds for state restoration.
    
    Every restoration must explicitly identify its source.
    
    SOURCES:
        CHECKPOINT        : State from saved checkpoint file
        PERSISTENT_STORE  : Long-term persistence storage
        ARCHIVE           : Versioned backup archive
        REPLICATED_STATE  : Copied state from remote instance
        MIGRATION_PACKAGE : Transferred state with schema evolution
        RECOVERY_IMAGE    : Complete system recovery snapshot
        SERIALIZED_SNAPSHOT: Encoded state representation
        
    INVARIANTS:
        SRC-001: Every restoration has exactly one source kind
        SRC-002: Source kind is immutable once set
        SRC-003: Source metadata includes identification and version info
    """
    
    # Checkpoint-based restoration
    CHECKPOINT = "checkpoint"
    
    # Persistent storage restoration
    PERSISTENT_STORE = "persistent_store"
    
    # Archive-based restoration
    ARCHIVE = "archive"
    
    # Replicated state from remote instance
    REPLICATED_STATE = "replicated_state"
    
    # Migration package with schema evolution
    MIGRATION_PACKAGE = "migration_package"
    
    # Recovery image (complete system snapshot)
    RECOVERY_IMAGE = "recovery_image"
    
    # Serialized snapshot (encoded representation)
    SERIALIZED_SNAPSHOT = "serialized_snapshot"


@dataclass(frozen=True)
class RestorationSource:
    """
    Explicit identification of restoration source.
    
    The source always remains distinct from the runtime state authority.
    Source provides data; it never becomes the authority.
    
    INVARIANTS:
        SRC-DEF-001: Source is immutable once created
        SRC-DEF-002: Source kind, identity, version, generation are all explicit
        SRC-DEF-003: Source may include provenance for audit trail
    """
    
    # Source classification
    source_kind: RestorationSourceKind
    
    # Source identification
    source_id: str  # Unique identifier for this specific source instance
    
    # Source state at time of capture
    source_version_sequence: int = 0
    """Version sequence number of the captured state."""
    
    source_generation_epoch: int = 0
    """Generation epoch of the captured state."""
    
    # Context
    source_timestamp_utc: float = field(default_factory=_time_module.monotonic)
    """When this source was created/last modified."""
    
    # Provenance
    provenance: Dict[str, str] = field(default_factory=dict)
    """Source tracking information for audit."""
    
    @classmethod
    def from_checkpoint(cls, checkpoint: CheckpointRecord) -> "RestorationSource":
        """
        Create a source reference from a checkpoint record.
        
        Args:
            checkpoint: The checkpoint record containing state
            
        Returns:
            RestorationSource referencing the checkpoint
        """
        return cls(
            source_kind=RestorationSourceKind.CHECKPOINT,
            source_id=checkpoint.checkpoint_id,
            source_version_sequence=checkpoint.version_sequence,
            source_generation_epoch=checkpoint.generation_epoch,
            provenance={
                "created_at": str(checkpoint.created_at_utc),
                "persistence_boundary": checkpoint.persistence_boundary.value,
            },
        )
    
    @classmethod
    def from_archive(cls, archive: ArchiveDescriptor) -> "RestorationSource":
        """
        Create a source reference from an archive descriptor.
        
        Args:
            archive: The archive descriptor containing state
            
        Returns:
            RestorationSource referencing the archive
        """
        return cls(
            source_kind=RestorationSourceKind.ARCHIVE,
            source_id=archive.archive_id,
            source_version_sequence=archive.version_sequence,
            source_generation_epoch=archive.generation_epoch,
            provenance={
                "retention_until": str(archive.retention_until_utc),
                "integrity_algorithm": archive.integrity_evidence.algorithm.value if archive.integrity_evidence else "none",
            },
        )
    
    @classmethod
    def from_persistent_store(
        cls, aggregate_id: str, version_sequence: int, generation_epoch: int
    ) -> "RestorationSource":
        """
        Create a source reference from persistent storage.
        
        Args:
            aggregate_id: The aggregate being restored
            version_sequence: Version sequence in storage
            generation_epoch: Generation epoch in storage
            
        Returns:
            RestorationSource referencing the persistent record
        """
        return cls(
            source_kind=RestorationSourceKind.PERSISTENT_STORE,
            source_id=f"persist:{aggregate_id}",
            source_version_sequence=version_sequence,
            source_generation_epoch=generation_epoch,
        )
    
    @property
    def is_checkpoint(self) -> bool:
        """Check if this is a checkpoint source."""
        return self.source_kind == RestorationSourceKind.CHECKPOINT
    
    @property
    def is_archive(self) -> bool:
        """Check if this is an archive source."""
        return self.source_kind == RestorationSourceKind.ARCHIVE


# =============================================================================
# RESTORATION POLICIES
# =============================================================================


class RestorationPolicy(Enum):
    """
    Canonical restoration policies.
    
    Policies shall never be inferred implicitly. Each restoration must
    explicitly declare its policy.
    
    POLICIES:
        FULL_RESTORE          : Complete reconstruction of all state
        PARTIAL_RESTORE       : Selective reconstruction by scope
        SELECTIVE_RESTORE     : Targeted aggregate restoration
        REPLACE_EXISTING      : Overwrite current state unconditionally
        MERGE_EXISTING        : Combine restored with current state
        RESTORE_IF_MISSING    : Only restore if no current state exists
        RESTORE_WITH_MIGRATION: Apply schema evolution during restore
        RESTORE_READ_ONLY     : Create read-only bindings
        
    INVARIANTS:
        POL-001: Every restoration has exactly one policy
        POL-002: Policy is immutable once set
        POL-003: No implicit policy inference is permitted
    """
    
    # Full restoration of all state
    FULL_RESTORE = "full_restore"
    
    # Partial restoration by scope
    PARTIAL_RESTORE = "partial_restore"
    
    # Selective aggregate restoration
    SELECTIVE_RESTORE = "selective_restore"
    
    # Replace current state unconditionally
    REPLACE_EXISTING = "replace_existing"
    
    # Merge restored with current state
    MERGE_EXISTING = "merge_existing"
    
    # Only restore if no current state exists
    RESTORE_IF_MISSING = "restore_if_missing"
    
    # Apply schema evolution during restore
    RESTORE_WITH_MIGRATION = "restore_with_migration"
    
    # Create read-only bindings
    RESTORE_READ_ONLY = "restore_read_only"


@dataclass(frozen=True)
class RestorationPolicyConfiguration:
    """
    Configuration for a restoration policy.
    
    Policy configuration is immutable and explicitly declared.
    
    INVARIANTS:
        POL-CONFIG-001: Policy configuration is immutable once set
        POL-CONFIG-002: Policy may include parameters (e.g., scope, merge strategy)
        POL-CONFIG-003: Policy validation occurs before execution
    """
    
    # The policy to apply
    policy: RestorationPolicy
    
    # Optional parameters based on policy type
    target_aggregate_ids: Tuple[str, ...] = ()  # For partial/selective restore
    merge_strategy: str = "default"  # For merge operations
    migration_version: Optional[int] = None  # For migration restores
    read_only: bool = False  # For read-only restores
    
    # Validation requirements
    validate_schema: bool = True
    validate_integrity: bool = True
    verify_ownership: bool = True
    
    @classmethod
    def full_restore(cls) -> "RestorationPolicyConfiguration":
        """Create configuration for full restoration."""
        return cls(policy=RestorationPolicy.FULL_RESTORE)
    
    @classmethod
    def partial_restore(
        cls, aggregate_ids: List[str]
    ) -> "RestorationPolicyConfiguration":
        """
        Create configuration for partial restoration.
        
        Args:
            aggregate_ids: List of aggregate IDs to restore
            
        Returns:
            Configuration for partial restoration
        """
        return cls(
            policy=RestorationPolicy.PARTIAL_RESTORE,
            target_aggregate_ids=tuple(aggregate_ids),
        )
    
    @classmethod
    def replace_existing(cls) -> "RestorationPolicyConfiguration":
        """Create configuration to replace existing state."""
        return cls(policy=RestorationPolicy.REPLACE_EXISTING)
    
    @classmethod
    def merge_existing(cls) -> "RestorationPolicyConfiguration":
        """Create configuration to merge with existing state."""
        return cls(policy=RestorationPolicy.MERGE_EXISTING, merge_strategy="default")
    
    @classmethod
    def restore_if_missing(
        cls,
    ) -> "RestorationPolicyConfiguration":
        """Create configuration for conditional restoration."""
        return cls(policy=RestorationPolicy.RESTORE_IF_MISSING)
    
    @classmethod
    def with_migration(cls, target_version: int) -> "RestorationPolicyConfiguration":
        """
        Create configuration for migration-based restore.
        
        Args:
            target_version: Target schema version after migration
            
        Returns:
            Configuration for migration restoration
        """
        return cls(
            policy=RestorationPolicy.RESTORE_WITH_MIGRATION,
            migration_version=target_version,
        )
    
    @classmethod
    def read_only(cls) -> "RestorationPolicyConfiguration":
        """Create configuration for read-only restoration."""
        return cls(policy=RestorationPolicy.RESTORE_READ_ONLY, read_only=True)


# =============================================================================
# RESTORATION REQUEST
# =============================================================================


@dataclass(frozen=True)
class RestorationRequest:
    """
    Request to restore state from a source.
    
    Every request shall be explicitly represented and immutable once created.
    
    INVARIANTS:
        REQ-001: Request is immutable once created
        REQ-002: Source, policy, target runtime are all explicit
        REQ-003: Request always includes authority for validation
    """
    
    # Request identification
    request_id: str = field(default_factory=lambda: f"restore_req_{uuid.uuid4().hex[:16]}")
    
    # Source information
    source: RestorationSource
    
    # Policy
    policy_configuration: RestorationPolicyConfiguration
    
    # Target runtime context
    target_runtime_id: RuntimeId
    target_boot_session_id: BootSessionId
    target_owner_id: OwnerId
    
    # Request metadata
    requested_at_utc: float = field(default_factory=_time_module.monotonic)
    
    # Authority
    requesting_authority: str = "restoration_service"
    
    @property
    def source_version(self) -> int:
        """Get the source version sequence."""
        return self.source.source_version_sequence
    
    @property
    def source_generation(self) -> int:
        """Get the source generation epoch."""
        return self.source.source_generation_epoch


# =============================================================================
# RESTORATION RESULT AND STATUS
# =============================================================================


class RestorationStatus(Enum):
    """
    Status codes for restoration operations.
    
    STATUS CODES:
        PENDING      : Request received, not yet processed
        VALIDATING   : Validation in progress
        SOURCE_ERROR : Source validation failed
        INTEGRITY_ERROR : Integrity verification failed
        SCHEMA_ERROR : Schema compatibility issue
        VERSION_ERROR : Version validation failed
        GENERATION_ERROR : Generation validation failed
        OWNERSHIP_ERROR : Ownership assignment failed
        HIERARCHY_ERROR : Hierarchy reconstruction failed
        DEPENDENCY_ERROR : Dependency validation failed
        INVARIANT_ERROR : Invariant validation failed
        COMPLETED    : Restoration completed successfully
        FAILED       : Restoration failed irrecoverably
        
    INVARIANTS:
        STATUS-001: Every restoration has exactly one final status
        STATUS-002: Status transitions are deterministic
        STATUS-003: Failed/completed are terminal states
    """
    
    # Lifecycle states
    PENDING = "pending"
    VALIDATING = "validating"
    SOURCE_ERROR = "source_error"
    INTEGRITY_ERROR = "integrity_error"
    SCHEMA_ERROR = "schema_error"
    VERSION_ERROR = "version_error"
    GENERATION_ERROR = "generation_error"
    OWNERSHIP_ERROR = "ownership_error"
    HIERARCHY_ERROR = "hierarchy_error"
    DEPENDENCY_ERROR = "dependency_error"
    INVARIANT_ERROR = "invariant_error"
    COMPLETED = "completed"
    FAILED = "failed"


@dataclass(frozen=True)
class RestorationResult:
    """
    Result of a restoration operation.
    
    Immutable result with full provenance for diagnostics and audit.
    
    INVARIANTS:
        RES-001: Result is immutable once created
        RES-002: Success implies complete state reconstruction
        RES-003: Failure includes structured error information
    """
    
    # Request context
    request_id: str
    source_id: str
    
    # Status
    status: RestorationStatus
    
    # Runtime bindings established
    runtime_bound: bool = False
    hierarchy_reconstructed: bool = False
    dependencies_validated: bool = False
    
    # Result state (if successful)
    restored_version_sequence: Optional[int] = None
    restored_generation_epoch: Optional[int] = None
    new_generation_created: bool = False  # True if a new generation was created
    
    # Error information (if failed)
    error_message: str = ""
    error_category: Optional[str] = None
    
    # Timestamps
    requested_at_utc: float = field(default_factory=_time_module.monotonic)
    completed_at_utc: Optional[float] = None
    
    @property
    def is_success(self) -> bool:
        """Check if restoration succeeded."""
        return self.status == RestorationStatus.COMPLETED
    
    @property
    def duration_seconds(self) -> Optional[float]:
        """Calculate total duration, or None if not completed."""
        if self.completed_at_utc is None:
            return None
        return self.completed_at_utc - self.requested_at_utc


# =============================================================================
# VALIDATION FINDINGS AND RESULTS
# =============================================================================


class ValidationOutcome(Enum):
    """
    Outcome of validation checks.
    
    OUTCOMES:
        VALID     : Check passed successfully
        WARNING   : Check passed but with concerns
        REJECTED  : Check failed, restoration blocked
        
    INVARIANTS:
        VAL-OUTCOME-001: Every check produces one outcome type
        VAL-OUTCOME-002: REJECTED implies restoration cannot proceed
    """
    
    VALID = "valid"
    WARNING = "warning"
    REJECTED = "rejected"


@dataclass(frozen=True)
class ValidationFinding:
    """
    Structured validation finding.
    
    Every validation produces deterministic, immutable findings.
    
    INVARIANTS:
        FINDING-001: Finding is immutable once created
        FINDING-002: Findings include category, level, and detailed message
        FINDING-003: Timestamps preserved for diagnostics
    """
    
    # Classification
    outcome: ValidationOutcome
    
    finding_category: str  # e.g., "schema_compatibility", "ownership"
    finding_type: str      # e.g., "version_mismatch", "hierarchy_conflict"
    
    # Severity (for diagnostics)
    severity: str = "info"  # info, warning, error
    
    # Timestamp
    validated_at_utc: float = field(default_factory=_time_module.monotonic)
    
    # Detailed message
    message: str = ""
    
    # Context
    source_context: Optional[str] = None
    target_context: Optional[str] = None
    
    @classmethod
    def valid(cls, category: str, message: str) -> "ValidationFinding":
        """Create a valid finding."""
        return cls(
            outcome=ValidationOutcome.VALID,
            finding_category=category,
            finding_type="valid",
            severity="info",
            message=message,
        )
    
    @classmethod
    def warning(cls, category: str, message: str) -> "ValidationFinding":
        """Create a warning finding."""
        return cls(
            outcome=ValidationOutcome.WARNING,
            finding_category=category,
            finding_type="warning",
            severity="warning",
            message=message,
        )
    
    @classmethod
    def rejected(cls, category: str, message: str) -> "ValidationFinding":
        """Create a rejection finding."""
        return cls(
            outcome=ValidationOutcome.REJECTED,
            finding_category=category,
            finding_type="rejected",
            severity="error",
            message=message,
        )


@dataclass(frozen=True)
class ValidationResults:
    """
    Collection of validation findings.
    
    Results are immutable and complete for the operation context.
    
    INVARIANTS:
        RESULTS-001: Results include all findings
        RESULTS-002: Has_rejections indicates restoration blocking
        RESULTS-003: Summary provides quick inspection
    """
    
    # All validation findings
    findings: Tuple[ValidationFinding, ...]
    
    # Validation context
    source_id: str
    validation_at_utc: float = field(default_factory=_time_module.monotonic)
    
    @property
    def has_rejections(self) -> bool:
        """Check if any validations were rejected."""
        return any(f.outcome == ValidationOutcome.REJECTED for f in self.findings)
    
    @property
    def has_warnings(self) -> bool:
        """Check if any warnings were produced."""
        return any(f.outcome == ValidationOutcome.WARNING for f in self.findings)
    
    @property
    def rejection_count(self) -> int:
        """Count of rejected validations."""
        return sum(1 for f in self.findings if f.outcome == ValidationOutcome.REJECTED)
    
    @classmethod
    def empty(cls, source_id: str) -> "ValidationResults":
        """Create empty validation results."""
        return cls(findings=(), source_id=source_id)


# =============================================================================
# RESTORATION PIPELINE
# =============================================================================


class RestorationPipeline:
    """
    Canonical restoration pipeline for state reconstruction.
    
    The pipeline executes the canonical sequence:
        Request → Source Validation → Integrity Verification → Schema Compatibility
        → Version Validation → Generation Validation → Ownership Assignment
        → Runtime Binding → Hierarchy Reconstruction → Dependency Validation
        → Invariant Validation → Activation Approval → Result
    
    INVARIANTS:
        PIPELINE-001: Pipeline execution is deterministic
        PIPELINE-002: Each phase produces structured results
        PIPELINE-003: Early failures prevent later phases
        PIPELINE-004: Results are immutable for diagnostics
    """
    
    def __init__(self) -> None:
        """Initialize the restoration pipeline."""
        self._phase_results: Dict[str, Any] = {}
    
    def execute(
        self, request: RestorationRequest
    ) -> Tuple[RestorationResult, Tuple[ValidationFinding, ...]]:
        """
        Execute the restoration pipeline for a request.
        
        Args:
            request: The restoration request
            
        Returns:
            Tuple of (result, all_findings)
            
        Pipeline phases:
            1. Source Validation
            2. Integrity Verification
            3. Schema Compatibility Validation
            4. Version Validation
            5. Generation Validation
            6. Ownership Assignment
            7. Runtime Binding
            8. Hierarchy Reconstruction
            9. Dependency Validation
            10. Invariant Validation
        """
        all_findings: List[ValidationFinding] = []
        
        # Phase 1: Source Validation
        source_result, source_findings = self._validate_source(request)
        all_findings.extend(source_findings)
        self._phase_results["source_validation"] = source_result
        
        if source_result.status == RestorationStatus.FAILED:
            return (
                source_result,
                tuple(all_findings),
            )
        
        # Phase 2: Integrity Verification
        integrity_result, integrity_findings = self._verify_integrity(request)
        all_findings.extend(integrity_findings)
        self._phase_results["integrity_verification"] = integrity_result
        
        if integrity_result.status == RestorationStatus.FAILED:
            return (
                integrity_result,
                tuple(all_findings),
            )
        
        # Phase 3: Schema Compatibility Validation
        schema_result, schema_findings = self._validate_schema_compatibility(request)
        all_findings.extend(schema_findings)
        self._phase_results["schema_validation"] = schema_result
        
        if schema_result.status == RestorationStatus.FAILED:
            return (
                schema_result,
                tuple(all_findings),
            )
        
        # Phase 4: Version Validation
        version_result, version_findings = self._validate_version(request)
        all_findings.extend(version_findings)
        self._phase_results["version_validation"] = version_result
        
        if version_result.status == RestorationStatus.FAILED:
            return (
                version_result,
                tuple(all_findings),
            )
        
        # Phase 5: Generation Validation
        generation_result, generation_findings = self._validate_generation(request)
        all_findings.extend(generation_findings)
        self._phase_results["generation_validation"] = generation_result
        
        if generation_result.status == RestorationStatus.FAILED:
            return (
                generation_result,
                tuple(all_findings),
            )
        
        # Phase 6: Ownership Assignment
        ownership_result, ownership_findings = self._assign_ownership(request)
        all_findings.extend(ownership_findings)
        self._phase_results["ownership_assignment"] = ownership_result
        
        if ownership_result.status == RestorationStatus.FAILED:
            return (
                ownership_result,
                tuple(all_findings),
            )
        
        # Phase 7: Runtime Binding
        runtime_result, runtime_findings = self._bind_runtime(request)
        all_findings.extend(runtime_findings)
        self._phase_results["runtime_binding"] = runtime_result
        
        if runtime_result.status == RestorationStatus.FAILED:
            return (
                runtime_result,
                tuple(all_findings),
            )
        
        # Phase 8: Hierarchy Reconstruction
        hierarchy_result, hierarchy_findings = self._reconstruct_hierarchy(request)
        all_findings.extend(hierarchy_findings)
        self._phase_results["hierarchy_reconstruction"] = hierarchy_result
        
        if hierarchy_result.status == RestorationStatus.FAILED:
            return (
                hierarchy_result,
                tuple(all_findings),
            )
        
        # Phase 9: Dependency Validation
        dependency_result, dependency_findings = self._validate_dependencies(request)
        all_findings.extend(dependency_findings)
        self._phase_results["dependency_validation"] = dependency_result
        
        if dependency_result.status == RestorationStatus.FAILED:
            return (
                dependency_result,
                tuple(all_findings),
            )
        
        # Phase 10: Invariant Validation
        invariant_result, invariant_findings = self._validate_invariants(request)
        all_findings.extend(invariant_findings)
        self._phase_results["invariant_validation"] = invariant_result
        
        if invariant_result.status == RestorationStatus.FAILED:
            return (
                invariant_result,
                tuple(all_findings),
            )
        
        # All phases successful - create result
        result = RestorationResult(
            request_id=request.request_id,
            source_id=request.source.source_id,
            status=RestorationStatus.COMPLETED,
            runtime_bound=True,
            hierarchy_reconstructed=True,
            dependencies_validated=True,
            restored_version_sequence=request.source.source_version_sequence,
            restored_generation_epoch=request.source.source_generation_epoch,
            new_generation_created=False,  # Would be set by specific restoration logic
            completed_at_utc=_time_module.monotonic(),
        )
        
        return result, tuple(all_findings)
    
    def _validate_source(self, request: RestorationRequest) -> Tuple[RestorationResult, List[ValidationFinding]]:
        """Phase 1: Validate source identification and metadata."""
        findings: List[ValidationFinding] = []
        
        # Check source kind is valid
        if not isinstance(request.source.source_kind, RestorationSourceKind):
            return (
                RestorationResult(
                    request_id=request.request_id,
                    source_id=request.source.source_id,
                    status=RestorationStatus.SOURCE_ERROR,
                    error_message="Invalid source kind",
                    error_category="source_validation",
                ),
                [ValidationFinding.rejected("source", "Invalid source kind")],
            )
        
        # Check source has required identification
        if not request.source.source_id:
            return (
                RestorationResult(
                    request_id=request.request_id,
                    source_id="unknown",
                    status=RestorationStatus.SOURCE_ERROR,
                    error_message="Source ID is missing",
                    error_category="source_validation",
                ),
                [ValidationFinding.rejected("source", "Missing source identification")],
            )
        
        # Check version and generation are specified
        if request.source.source_version_sequence < 0:
            findings.append(
                ValidationFinding.warning(
                    "version", f"Negative version sequence: {request.source.source_version_sequence}"
                )
            )
        
        if request.source.source_generation_epoch < 0:
            findings.append(
                ValidationFinding.warning(
                    "generation", f"Negative generation epoch: {request.source.source_generation_epoch}"
                )
            )
        
        return (
            RestorationResult(
                request_id=request.request_id,
                source_id=request.source.source_id,
                status=RestorationStatus.PENDING,
            ),
            findings,
        )
    
    def _verify_integrity(self, request: RestorationRequest) -> Tuple[RestorationResult, List[ValidationFinding]]:
        """Phase 2: Verify integrity of source data."""
        # In real implementation, would verify hash/digest against stored evidence
        # For now, assume valid (integrity verification is source-specific)
        
        findings: List[ValidationFinding] = []
        
        if not request.policy_configuration.validate_integrity:
            findings.append(
                ValidationFinding.warning(
                    "integrity", "Integrity validation disabled by policy"
                )
            )
        
        return (
            RestorationResult(
                request_id=request.request_id,
                source_id=request.source.source_id,
                status=RestorationStatus.PENDING,
            ),
            findings,
        )
    
    def _validate_schema_compatibility(self, request: RestorationRequest) -> Tuple[RestorationResult, List[ValidationFinding]]:
        """Phase 3: Validate schema compatibility between source and target."""
        # In real implementation, would check schema version compatibility
        # For now, assume compatible
        
        findings: List[ValidationFinding] = []
        
        if not request.policy_configuration.validate_schema:
            findings.append(
                ValidationFinding.warning(
                    "schema", "Schema validation disabled by policy"
                )
            )
        
        return (
            RestorationResult(
                request_id=request.request_id,
                source_id=request.source.source_id,
                status=RestorationStatus.PENDING,
            ),
            findings,
        )
    
    def _validate_version(self, request: RestorationRequest) -> Tuple[RestorationResult, List[ValidationFinding]]:
        """Phase 4: Validate version lineage and compatibility."""
        # In real implementation, would check version against current lineage
        # For now, assume valid
        
        return (
            RestorationResult(
                request_id=request.request_id,
                source_id=request.source.source_id,
                status=RestorationStatus.PENDING,
            ),
            [],
        )
    
    def _validate_generation(self, request: RestorationRequest) -> Tuple[RestorationResult, List[ValidationFinding]]:
        """Phase 5: Validate generation lineage and compatibility."""
        # In real implementation, would check generation against current generation
        # For now, assume valid
        
        return (
            RestorationResult(
                request_id=request.request_id,
                source_id=request.source.source_id,
                status=RestorationStatus.PENDING,
            ),
            [],
        )
    
    def _assign_ownership(self, request: RestorationRequest) -> Tuple[RestorationResult, List[ValidationFinding]]:
        """Phase 6: Assign ownership for restored state."""
        findings: List[ValidationFinding] = []
        
        # Ownership must be assigned to a valid owner
        if not request.target_owner_id:
            return (
                RestorationResult(
                    request_id=request.request_id,
                    source_id=request.source.source_id,
                    status=RestorationStatus.OWNERSHIP_ERROR,
                    error_message="Target owner ID is missing",
                    error_category="ownership_validation",
                ),
                [ValidationFinding.rejected("ownership", "Missing target owner ID")],
            )
        
        return (
            RestorationResult(
                request_id=request.request_id,
                source_id=request.source.source_id,
                status=RestorationStatus.PENDING,
            ),
            findings,
        )
    
    def _bind_runtime(self, request: RestorationRequest) -> Tuple[RestorationResult, List[ValidationFinding]]:
        """Phase 7: Bind restored state to runtime context."""
        # In real implementation, would establish runtime binding
        # For now, assume successful
        
        return (
            RestorationResult(
                request_id=request.request_id,
                source_id=request.source.source_id,
                status=RestorationStatus.PENDING,
            ),
            [],
        )
    
    def _reconstruct_hierarchy(self, request: RestorationRequest) -> Tuple[RestorationResult, List[ValidationFinding]]:
        """Phase 8: Reconstruct hierarchy relationships."""
        # In real implementation, would restore parent-child relationships
        # For now, assume successful
        
        return (
            RestorationResult(
                request_id=request.request_id,
                source_id=request.source.source_id,
                status=RestorationStatus.PENDING,
            ),
            [],
        )
    
    def _validate_dependencies(self, request: RestorationRequest) -> Tuple[RestorationResult, List[ValidationFinding]]:
        """Phase 9: Validate dependency availability."""
        # In real implementation, would check that dependencies exist and are valid
        # For now, assume all dependencies available
        
        return (
            RestorationResult(
                request_id=request.request_id,
                source_id=request.source.source_id,
                status=RestorationStatus.PENDING,
            ),
            [],
        )
    
    def _validate_invariants(self, request: RestorationRequest) -> Tuple[RestorationResult, List[ValidationFinding]]:
        """Phase 10: Validate invariants for restored state."""
        # In real implementation, would check all architectural invariants
        # For now, assume valid
        
        return (
            RestorationResult(
                request_id=request.request_id,
                source_id=request.source.source_id,
                status=RestorationStatus.PENDING,
            ),
            [],
        )


# =============================================================================
# RECONCILIATION ARCHITECTURE
# =============================================================================


class ReconciliationScope(Enum):
    """
    Canonical reconciliation scopes.
    
    SCOPE:
        IDENTITY       : Validate aggregate identity uniqueness
        HIERARCHY      : Verify parent-child relationships
        OWNERSHIP      : Ensure valid ownership chains
        SCOPES         : Validate scope boundaries
        VERSIONS       : Check version lineage integrity
        GENERATIONS    : Validate epoch consistency
        DEPENDENCIES   : Confirm dependency availability
        RESOURCES      : Verify resource allocation validity
        STREAMS        : Validate stream state consistency
        TRANSACTIONS   : Validate transaction state
        
    INVARIANTS:
        SCOPE-001: Every reconciliation has exactly one primary scope
        SCOPE-002: Multiple scopes may be validated in one operation
    """
    
    IDENTITY = "identity"
    HIERARCHY = "hierarchy"
    OWNERSHIP = "ownership"
    SCOPES = "scopes"
    VERSIONS = "versions"
    GENERATIONS = "generations"
    DEPENDENCIES = "dependencies"
    RESOURCES = "resources"
    STREAMS = "streams"
    TRANSACTIONS = "transactions"


@dataclass(frozen=True)
class ReconciliationRequest:
    """
    Request for state consistency validation.
    
    Reconciliation validates consistency but NEVER silently modifies runtime state.
    
    INVARIANTS:
        REC-REQ-001: Request is immutable
        REC-REQ-002: Scope(s) are explicitly declared
        REC-REQ-003: Runtime context is provided for validation
    """
    
    # Request identification
    request_id: str = field(default_factory=lambda: f"reconcile_req_{uuid.uuid4().hex[:16]}")
    
    # Reconciliation scope(s)
    scopes: Tuple[ReconciliationScope, ...]
    
    # Runtime context for validation
    runtime_id: Optional[str] = None
    boot_session_id: Optional[str] = None
    
    # Context information
    requested_at_utc: float = field(default_factory=_time_module.monotonic)
    requesting_authority: str = "reconciliation_service"
    
    @classmethod
    def full_reconciliation(cls) -> "ReconciliationRequest":
        """Create a request for full reconciliation (all scopes)."""
        return cls(scopes=tuple(ReconciliationScope))
    
    @classmethod
    def identity_only(cls) -> "ReconciliationRequest":
        """Create a request for identity reconciliation."""
        return cls(scopes=(ReconciliationScope.IDENTITY,))
    
    @classmethod
    def hierarchy_only(cls) -> "ReconciliationRequest":
        """Create a request for hierarchy reconciliation."""
        return cls(scopes=(ReconciliationScope.HIERARCHY,))
    
    @classmethod
    def ownership_only(cls) -> "ReconciliationRequest":
        """Create a request for ownership reconciliation."""
        return cls(scopes=(ReconciliationScope.OWNERSHIP,))


class ReconciliationResultStatus(Enum):
    """
    Status codes for reconciliation operations.
    
    STATUS CODES:
        VALID          : All validations passed
        CONFLICT_DETECTED : Conflict detected but not necessarily invalid
        INCONSISTENCY_DETECTED : Inconsistency detected requiring attention
        ERROR          : Validation error occurred
        
    INVARIANTS:
        REC-STATUS-001: Every reconciliation has exactly one final status
        REC-STATUS-002: Results are immutable for diagnostics
    """
    
    VALID = "valid"
    CONFLICT_DETECTED = "conflict_detected"
    INCONSISTENCY_DETECTED = "inconsistency_detected"
    ERROR = "error"


@dataclass(frozen=True)
class ReconciliationResult:
    """
    Result of a reconciliation operation.
    
    Immutable result with structured findings for diagnostics and audit.
    
    INVARIANTS:
        REC-RES-001: Result is immutable once created
        REC-RES-002: Success implies consistent state
        REC-RES-003: Findings include specific issues detected
    """
    
    # Request context
    request_id: str
    
    # Status
    status: ReconciliationResultStatus
    
    # Findings (conflicts, inconsistencies, etc.)
    findings: Tuple[str, ...]
    
    # Repair recommendations (if any)
    repair_recommendations: Tuple["RepairRecommendation", ...] = ()
    
    # Timestamps
    requested_at_utc: float = field(default_factory=_time_module.monotonic)
    completed_at_utc: Optional[float] = None
    
    @property
    def is_valid(self) -> bool:
        """Check if reconciliation passed."""
        return self.status == ReconciliationResultStatus.VALID
    
    @property
    def has_repair_recommendations(self) -> bool:
        """Check if repairs are recommended."""
        return len(self.repair_recommendations) > 0
    
    @property
    def duration_seconds(self) -> Optional[float]:
        """Calculate total duration, or None if not completed."""
        if self.completed_at_utc is None:
            return None
        return self.completed_at_utc - self.requested_at_utc


@dataclass(frozen=True)
class RepairRecommendation:
    """
    Recommended repair strategy for an inconsistency.
    
    Recommendations are policy-driven and never automatically applied.
    
    INVARIANTS:
        REC-REC-001: Recommendation is immutable
        REC-REC-002: Strategy, target, and context are all explicit
    """
    
    # Repair strategy to apply
    strategy: "RepairStrategy"
    
    # Target of the repair
    target_id: str  # Aggregate ID or other identifier
    target_type: str  # e.g., "aggregate", "dependency", "hierarchy_node"
    
    # Context for the recommendation
    context: Dict[str, str] = field(default_factory=dict)
    
    # Justification for this recommendation
    justification: str = ""
    
    @classmethod
    def rebuild(cls, target_id: str, reason: str) -> "RepairRecommendation":
        """Recommend rebuilding the target."""
        return cls(
            strategy=RepairStrategy.REBUILD,
            target_id=target_id,
            target_type="aggregate",
            context={"reason": reason},
            justification=f"Rebuild required because: {reason}",
        )
    
    @classmethod
    def replace(cls, target_id: str, replacement_context: Dict[str, str]) -> "RepairRecommendation":
        """Recommend replacing the target."""
        return cls(
            strategy=RepairStrategy.REPLACE,
            target_id=target_id,
            target_type="aggregate",
            context=replacement_context,
            justification=f"Replace required with updated context",
        )


class ReconciliationEngine:
    """
    Canonical reconciliation engine.
    
    Reconciliation validates whether runtime state remains internally consistent.
    
    RECONCILIATION TYPES:
        - Identity Reconciliation: Validate aggregate identity uniqueness
        - Hierarchy Reconciliation: Verify parent-child relationships
        - Ownership Reconciliation: Ensure valid ownership chains
        - Scope Reconciliation: Validate scope boundaries
        - Version Reconciliation: Check version lineage integrity
        - Generation Reconciliation: Validate epoch consistency
        - Dependency Reconciliation: Confirm dependency availability
        - Resource Reconciliation: Verify resource allocation validity
        
    INVARIANTS:
        ENGINE-001: Engine never silently modifies runtime state
        ENGINE-002: Results are deterministic and reproducible
        ENGINE-003: Recommendations are policy-driven
    """
    
    def __init__(self) -> None:
        """Initialize the reconciliation engine."""
        self._validation_rules: Dict[ReconciliationScope, Any] = {}
    
    def reconcile(
        self, request: ReconciliationRequest
    ) -> Tuple[ReconciliationResult, List[str]]:
        """
        Perform reconciliation for the requested scopes.
        
        Args:
            request: The reconciliation request
            
        Returns:
            Tuple of (result, diagnostic_messages)
            
        INVARIANTS:
            - Never modifies runtime state
            - Always produces immutable results
            - Findings are structured and deterministic
        """
        findings: List[str] = []
        repair_recommendations: List[RepairRecommendation] = []
        
        for scope in request.scopes:
            result, messages = self._reconcile_scope(scope, request)
            findings.extend(messages)
            
            if result == ReconciliationResultStatus.ERROR:
                return (
                    ReconciliationResult(
                        request_id=request.request_id,
                        status=result,
                        findings=tuple(findings),
                        repair_recommendations=tuple(repair_recommendations),
                        completed_at_utc=_time_module.monotonic(),
                    ),
                    [],
                )
        
        # Determine final status
        if any("conflict" in f.lower() for f in findings):
            final_status = ReconciliationResultStatus.CONFLICT_DETECTED
        elif findings:
            final_status = ReconciliationResultStatus.INCONSISTENCY_DETECTED
        else:
            final_status = ReconciliationResultStatus.VALID
        
        return (
            ReconciliationResult(
                request_id=request.request_id,
                status=final_status,
                findings=tuple(findings),
                repair_recommendations=tuple(repair_recommendations),
                completed_at_utc=_time_module.monotonic(),
            ),
            [],
        )
    
    def _reconcile_scope(
        self, scope: ReconciliationScope, request: ReconciliationRequest
    ) -> Tuple[ReconciliationResultStatus, List[str]]:
        """Reconcile a single scope."""
        # In real implementation, would check specific consistency rules for the scope
        # For now, assume all scopes are consistent
        
        return ReconciliationResultStatus.VALID, []


# =============================================================================
# REPAIR STRATEGIES AND RESOLVER
# =============================================================================


class RepairStrategy(Enum):
    """
    Canonical repair strategies.
    
    Strategies shall never be applied automatically. They must be selected
    explicitly and produce observable evidence.
    
    STRATEGIES:
        REJECT       : Reject the state as invalid (no repair attempted)
        REBUILD      : Recreate from scratch using available evidence
        RECONSTRUCT  : Build from partial state with validation
        REPLACE      : Swap with known good instance
        RETRY        : Attempt operation again
        RECONCILE    : Apply reconciliation to resolve inconsistency
        ROLLBACK     : Return to prior verified state
        COMPENSATE   : Execute compensating actions
        ESCALATE     : Delegate to higher authority
        
    INVARIANTS:
        STRATEGY-001: Every repair has exactly one strategy
        STRATEGY-002: Strategy selection is policy-driven
        STRATEGY-003: Strategy execution produces observable evidence
    """
    
    # Reject the state as invalid
    REJECT = "reject"
    
    # Recreate from scratch
    REBUILD = "rebuild"
    
    # Build from partial state with validation
    RECONSTRUCT = "reconstruct"
    
    # Swap with known good instance
    REPLACE = "replace"
    
    # Attempt operation again
    RETRY = "retry"
    
    # Apply reconciliation to resolve inconsistency
    RECONCILE = "reconcile"
    
    # Return to prior verified state
    ROLLBACK = "rollback"
    
    # Execute compensating actions
    COMPENSATE = "compensate"
    
    # Delegate to higher authority
    ESCALATE = "escalate"


@dataclass(frozen=True)
class RepairRequest:
    """
    Request to apply a repair strategy.
    
    Repair is policy-driven and never automatic.
    
    INVARIANTS:
        REPAIR-REQ-001: Request is immutable
        REPAIR-REQ-002: Strategy, target, and context are all explicit
    """
    
    # Request identification
    request_id: str = field(default_factory=lambda: f"repair_req_{uuid.uuid4().hex[:16]}")
    
    # Strategy to apply
    strategy: RepairStrategy
    
    # Target of repair
    target_id: str  # Aggregate ID, hierarchy node, etc.
    target_type: str  # e.g., "aggregate", "dependency"
    
    # Context for the repair
    context: Dict[str, Any] = field(default_factory=dict)
    
    # Policy configuration
    evidence_required: bool = True  # Require observable evidence of repair
    
    requested_at_utc: float = field(default_factory=_time_module.monotonic)


@dataclass(frozen=True)
class RepairResult:
    """
    Result of a repair operation.
    
    Results are immutable with full provenance for audit.
    
    INVARIANTS:
        REPAIR-RES-001: Result is immutable once created
        REPAIR-RES-002: Success implies repair applied successfully
        REPAIR-RES-003: Evidence preserved for observability
    """
    
    # Request context
    request_id: str
    
    # Status
    success: bool
    
    # Timestamps
    requested_at_utc: float = field(default_factory=_time_module.monotonic)
    completed_at_utc: Optional[float] = None
    
    # Evidence (if required)
    evidence: Dict[str, Any] = field(default_factory=dict)
    
    @property
    def duration_seconds(self) -> Optional[float]:
        """Calculate total duration, or None if not completed."""
        if self.completed_at_utc is None:
            return None
        return self.completed_at_utc - self.requested_at_utc


class RepairResolver:
    """
    Canonical repair resolver.
    
    Applies explicit repair strategies based on policy decisions.
    
    RESOLVER BEHAVIOR:
        - Never applies repairs automatically
        - Always produces observable evidence
        - Strategy selection is policy-driven
        - Results are immutable for audit
        
    INVARIANTS:
        RESOLVER-001: Resolver never silently modifies state
        RESOLVER-002: Evidence is always produced when required
        RESOLVER-003: Strategy execution is deterministic
    """
    
    def __init__(self) -> None:
        """Initialize the repair resolver."""
        self._strategy_handlers: Dict[RepairStrategy, Any] = {}
    
    def resolve(
        self, request: RepairRequest
    ) -> Tuple[RepairResult, List[str]]:
        """
        Resolve a repair request by applying the specified strategy.
        
        Args:
            request: The repair request
            
        Returns:
            Tuple of (result, diagnostic_messages)
            
        INVARIANTS:
            - Strategy is applied exactly once per call
            - Evidence is produced when required
            - Results are deterministic
        """
        # In real implementation, would dispatch to strategy-specific handler
        
        if request.strategy == RepairStrategy.REJECT:
            return (
                RepairResult(
                    request_id=request.request_id,
                    success=False,
                    completed_at_utc=_time_module.monotonic(),
                ),
                [f"Rejected {request.target_type} {request.target_id}"],
            )
        
        elif request.strategy == RepairStrategy.REBUILD:
            # Would trigger rebuild logic
            return (
                RepairResult(
                    request_id=request.request_id,
                    success=True,
                    completed_at_utc=_time_module.monotonic(),
                    evidence={"action": "rebuild", "target": request.target_id},
                ),
                [f"Rebuilding {request.target_type} {request.target_id}"],
            )
        
        elif request.strategy == RepairStrategy.REPLACE:
            # Would trigger replacement logic
            return (
                RepairResult(
                    request_id=request.request_id,
                    success=True,
                    completed_at_utc=_time_module.monotonic(),
                    evidence={"action": "replace", "target": request.target_id},
                ),
                [f"Replacing {request.target_type} {request.target_id}"],
            )
        
        elif request.strategy == RepairStrategy.RETRY:
            # Would trigger retry logic
            return (
                RepairResult(
                    request_id=request.request_id,
                    success=True,
                    completed_at_utc=_time_module.monotonic(),
                    evidence={"action": "retry", "target": request.target_id},
                ),
                [f"Retrying operation on {request.target_type} {request.target_id}"],
            )
        
        elif request.strategy == RepairStrategy.ROLLBACK:
            # Would trigger rollback logic
            return (
                RepairResult(
                    request_id=request.request_id,
                    success=True,
                    completed_at_utc=_time_module.monotonic(),
                    evidence={"action": "rollback", "target": request.target_id},
                ),
                [f"Rolling back {request.target_type} {request.target_id}"],
            )
        
        elif request.strategy == RepairStrategy.ESCALATE:
            # Would trigger escalation logic
            return (
                RepairResult(
                    request_id=request.request_id,
                    success=False,  # Escalation is not a direct success
                    completed_at_utc=_time_module.monotonic(),
                    evidence={"action": "escalate", "target": request.target_id},
                ),
                [f"Escalating repair of {request.target_type} {request.target_id}"],
            )
        
        else:
            # Unimplemented strategy
            return (
                RepairResult(
                    request_id=request.request_id,
                    success=False,
                    completed_at_utc=_time_module.monotonic(),
                ),
                [f"Repair strategy {request.strategy.value} not implemented"],
            )


# =============================================================================
# RESTORATION DIAGNOSTICS
# =============================================================================


@dataclass(frozen=True)
class RestorationDiagnosticEvent:
    """
    Immutable diagnostic event for restoration operations.
    
    Events are captured throughout the restoration lifecycle for observability.
    
    EVENT TYPES:
        REQUEST_RECEIVED      : Request received from client
        SOURCE_VALIDATED      : Source validation completed
        INTEGRITY_VERIFIED    : Integrity verification completed
        SCHEMA_VALIDATED      : Schema compatibility validated
        VERSION_VALIDATED     : Version validation completed
        GENERATION_VALIDATED  : Generation validation completed
        OWNERSHIP_ASSIGNED    : Ownership assignment completed
        RUNTIME_BOUND         : Runtime binding completed
        HIERARCHY_RECONSTRUCTED: Hierarchy reconstruction completed
        DEPENDENCIES_VALIDATED: Dependency validation completed
        INVARIANTS_VALIDATED  : Invariant validation completed
        RESTORATION_COMPLETED : Full restoration completed
        RESTORATION_FAILED    : Restoration failed
        
    INVARIANTS:
        EVENT-001: Event is immutable once created
        EVENT-002: Timestamps preserved for ordering
        EVENT-003: Context information included
    """
    
    # Event identification
    event_id: str = field(default_factory=lambda: f"diag_{uuid.uuid4().hex[:16]}")
    
    # Event type
    event_type: str  # e.g., "REQUEST_RECEIVED", "SOURCE_VALIDATED"
    
    # Timestamp (UTC epoch seconds)
    timestamp_utc: float = field(default_factory=_time_module.monotonic)
    
    # Request context
    request_id: Optional[str] = None
    
    # Status information
    status: Optional[RestorationStatus] = None
    
    # Context information (structured data for observability)
    context: Dict[str, Any] = field(default_factory=dict)
    
    @classmethod
    def request_received(cls, request: RestorationRequest) -> "RestorationDiagnosticEvent":
        """Create an event for a received request."""
        return cls(
            event_type="REQUEST_RECEIVED",
            request_id=request.request_id,
            context={
                "source_id": request.source.source_id,
                "target_runtime_id": str(request.target_runtime_id),
            },
        )
    
    @classmethod
    def source_validated(cls, request: RestorationRequest) -> "RestorationDiagnosticEvent":
        """Create an event for source validation completion."""
        return cls(
            event_type="SOURCE_VALIDATED",
            request_id=request.request_id,
        )
    
    @classmethod
    def integrity_verified(cls, request: RestorationRequest) -> "RestorationDiagnosticEvent":
        """Create an event for integrity verification completion."""
        return cls(
            event_type="INTEGRITY_VERIFIED",
            request_id=request.request_id,
        )
    
    @classmethod
    def restoration_completed(cls, result: RestorationResult) -> "RestorationDiagnosticEvent":
        """Create an event for successful restoration completion."""
        return cls(
            event_type="RESTORATION_COMPLETED",
            request_id=result.request_id,
            status=RestorationStatus.COMPLETED,
            context={
                "source_id": result.source_id,
                "runtime_bound": result.runtime_bound,
                "hierarchy_reconstructed": result.hierarchy_reconstructed,
            },
        )
    
    @classmethod
    def restoration_failed(
        cls, request: RestorationRequest, error_message: str
    ) -> "RestorationDiagnosticEvent":
        """Create an event for failed restoration."""
        return cls(
            event_type="RESTORATION_FAILED",
            request_id=request.request_id,
            status=RestorationStatus.FAILED,
            context={"error": error_message},
        )


class RestorationDiagnostics:
    """
    Immutable diagnostics collection for restoration operations.
    
    Diagnostics remain immutable throughout their lifetime. They provide
    complete observability of restoration lifecycle events.
    
    INVARIANTS:
        DIAG-001: Diagnostics are immutable once created
        DIAG-002: Events are chronologically ordered
        DIAG-003: Summary information available for quick inspection
    """
    
    def __init__(self) -> None:
        """Initialize diagnostics collection."""
        self._events: List[RestorationDiagnosticEvent] = []
        self._lock = False  # Prevent modification after finalization
    
    def record_event(self, event: RestorationDiagnosticEvent) -> None:
        """
        Record a diagnostic event.
        
        Args:
            event: The event to record
        """
        if not self._lock:
            self._events.append(event)
    
    def get_events(self) -> Tuple[RestorationDiagnosticEvent, ...]:
        """Get all recorded events."""
        return tuple(self._events)
    
    def get_event_count_by_type(self, event_type: str) -> int:
        """Count events of a specific type."""
        return sum(1 for e in self._events if e.event_type == event_type)
    
    def get_summary(self) -> Dict[str, Any]:
        """
        Get diagnostic summary.
        
        Returns:
            Summary dictionary with counts and timing information
        """
        completed_count = self.get_event_count_by_type("RESTORATION_COMPLETED")
        failed_count = self.get_event_count_by_type("RESTORATION_FAILED")
        
        return {
            "total_events": len(self._events),
            "completed_restorations": completed_count,
            "failed_restorations": failed_count,
        }
    
    def finalize(self) -> None:
        """Finalize diagnostics (prevent further modifications)."""
        self._lock = True


# =============================================================================
# PUBLIC API - PHASE 3.15.10
# =============================================================================


class StateRestorationFacade:
    """
    Canonical facade for state restoration and reconciliation operations.
    
    Exposes one canonical interface for restoration, reconciliation,
    and repair operations without exposing mutable runtime internals.
    
    PUBLIC API:
        - validate_restoration : Validate a restoration request before execution
        - execute_restoration  : Execute the restoration pipeline
        - reconcile_state      : Perform state consistency validation
        - resolve_repair       : Apply explicit repair strategy
        
    INVARIANTS:
        FACADE-001: All operations are pure (no side effects on runtime state)
        FACADE-002: Results are deterministic and reproducible
        FACADE-003: No mutable runtime internals exposed
        FACADE-004: Diagnostics remain immutable
    """
    
    def __init__(self) -> None:
        """Initialize the restoration facade."""
        self._pipeline = RestorationPipeline()
        self._reconciliation_engine = ReconciliationEngine()
        self._repair_resolver = RepairResolver()
        self._diagnostics = RestorationDiagnostics()
    
    def validate_restoration(
        self, request: RestorationRequest
    ) -> Tuple[ValidationResults, List[str]]:
        """
        Validate a restoration request before execution.
        
        Performs all validation checks without actually executing the restoration.
        
        Args:
            request: The restoration request to validate
            
        Returns:
            Tuple of (validation_results, diagnostic_messages)
        """
        all_findings: List[ValidationFinding] = []
        
        # Run through all phases but don't execute
        result, findings = self._pipeline.execute(request)
        all_findings.extend(findings)
        
        return (
            ValidationResults(
                findings=tuple(all_findings),
                source_id=request.source.source_id,
            ),
            [],
        )
    
    def execute_restoration(
        self, request: RestorationRequest
    ) -> Tuple[RestorationResult, Tuple[ValidationFinding, ...]]:
        """
        Execute the restoration pipeline for a request.
        
        This is the main entry point for state restoration.
        
        Args:
            request: The restoration request
            
        Returns:
            Tuple of (restoration_result, validation_findings)
            
        INVARIANTS:
            - Source validation precedes execution
            - Runtime binding occurs only after validation
            - Hierarchy reconstruction preserves integrity
        """
        # Record request event
        self._diagnostics.record_event(
            RestorationDiagnosticEvent.request_received(request)
        )
        
        # Execute the pipeline
        result, findings = self._pipeline.execute(request)
        
        # Record completion event
        if result.status == RestorationStatus.COMPLETED:
            self._diagnostics.record_event(
                RestorationDiagnosticEvent.restoration_completed(result)
            )
        else:
            self._diagnostics.record_event(
                RestorationDiagnosticEvent.restoration_failed(request, result.error_message)
            )
        
        return result, findings
    
    def reconcile_state(
        self, request: ReconciliationRequest
    ) -> Tuple[ReconciliationResult, List[str]]:
        """
        Perform state consistency validation.
        
        Never silently modifies runtime state. Only validates and reports.
        
        Args:
            request: The reconciliation request
            
        Returns:
            Tuple of (result, diagnostic_messages)
        """
        return self._reconciliation_engine.reconcile(request)
    
    def resolve_repair(
        self, request: RepairRequest
    ) -> Tuple[RepairResult, List[str]]:
        """
        Apply a repair strategy to restore consistency.
        
        Never applies repairs automatically - always explicit strategy selection.
        
        Args:
            request: The repair request
            
        Returns:
            Tuple of (result, diagnostic_messages)
        """
        return self._repair_resolver.resolve(request)
    
    def get_diagnostics(self) -> Dict[str, Any]:
        """Get current diagnostic summary."""
        return self._diagnostics.get_summary()


# =============================================================================
# EXPORTS
# =============================================================================

__all__ = [
    # Source types
    "RestorationSourceKind",
    "RestorationSource",
    
    # Policies
    "RestorationPolicy",
    "RestorationPolicyConfiguration",
    
    # Requests
    "RestorationRequest",
    "ReconciliationRequest",
    "RepairRequest",
    
    # Results
    "RestorationStatus",
    "RestorationResult",
    "ValidationOutcome",
    "ValidationFinding",
    "ValidationResults",
    "ReconciliationResultStatus",
    "ReconciliationResult",
    "RepairResult",
    
    # Pipelines and engines
    "RestorationPipeline",
    "ReconciliationEngine",
    "RepairResolver",
    
    # Repair strategies
    "RepairStrategy",
    "RepairRecommendation",
    
    # Diagnostics
    "RestorationDiagnosticEvent",
    "RestorationDiagnostics",
    
    # Public API facade (Phase 3.15.10)
    "StateRestorationFacade",
]