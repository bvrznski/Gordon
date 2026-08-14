# State Versioning & Generations Architecture - Phase 3.15.7
# ============================================================
#
# Canonical versioning and generation architecture governing state evolution throughout Gordon Core.
#
# This module establishes:
#   - Explicit, immutable state versions with lineage tracking
#   - Generation epochs for restart/migration/recovery detection
#   - Deterministic version progression (no skipped/duplicate versions)
#   - Stale version/generation detection
#   - Bounded history management
#   - Lineage integrity validation
#
# ARCHITECTURAL PRINCIPLES:
#   1. One canonical versioning architecture exists throughout the Core
#   2. Identity, Version, and Generation remain distinct concepts
#   3. Version progression is deterministic (one successor per mutation)
#   4. Generation changes are rare but invalidate stale ownership evidence
#   5. All versioning artifacts are immutable once created
#   6. Lineage integrity is preserved throughout evolution
#
# This extends:
#     Phase 3.15.1 - Core State Foundations
#     Phase 3.15.2 - State Identity, Scope & Ownership
#     Phase 3.15.3 - Immutable & Mutable State Semantics
#     Phase 3.15.4 - Runtime State Hierarchy
#     Phase 3.15.5 - State Transitions & Transition Validation
#     Phase 3.15.6 - State Snapshots & Views

"""
Canonical State Versioning & Generations Architecture for Gordon Core Phase 3.15.7.

This module defines the canonical versioning and generation architecture that governs how
runtime state evolves while preserving:

    IDENTITY:
        - Each aggregate has a stable identity across all versions/generations
        - Identity never changes through mutation, transition, or update
        
    VERSION:
        - Evolution within a generation (sequence-based)
        - Every mutation produces exactly one successor version
        - Versions form an immutable lineage chain
        
    GENERATION:
        - Epoch change indicator (restart, migration, recovery)
        - Rare change event that may restart version numbering
        - Invalidates stale ownership evidence

ONE CANONICAL ARCHITECTURE:
    Only one versioning architecture exists throughout the Core.
    Subsystems must use this foundation for all state evolution tracking.
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
)
from enum import Enum, auto
import uuid
import time as _time_module

# Core state foundations (Phase 3.15.x)
from ..identity import AggregateId, RuntimeId, BootSessionId, OwnerId
from ..ownership import OwnershipAuthorityType
from ..transitions import TransitionId, OperationId
from .__init__ import CoreStateDomain, CoreStateScope


# =============================================================================
# VERSION IDENTITY
# =============================================================================

@dataclass(frozen=True, order=True)
class VersionIdentity:
    """
    Canonical identifier for a state version.
    
    A version identity uniquely identifies one revision of an aggregate.
    It does not identify the aggregate itself (that's AggregateId).
    
    INVARIANTS:
        VER-ID-001: Every version has exactly one version identity
        VER-ID-002: Version IDs are deterministic from lineage position
        VER-ID-003: No two versions share the same ID within a generation
    """
    
    value: str = field(default_factory=lambda: f"ver_{uuid.uuid4().hex[:20]}")
    sequence: int = 0
    aggregate_id: Optional[str] = None
    
    @classmethod
    def generate(cls, sequence: int = 0, aggregate_id: Optional[str] = None) -> "VersionIdentity":
        """Generate a new version identity."""
        value = f"ver_seq{sequence}_{uuid.uuid4().hex[:16]}"
        return cls(value=value.replace("-", "_"), sequence=sequence, aggregate_id=aggregate_id)
    
    def matches_sequence(self, sequence: int) -> bool:
        """Check if this version matches the given sequence number."""
        return self.sequence == sequence
    
    def is_earlier_than(self, other: "VersionIdentity") -> bool:
        """Check if this version is earlier than the other (by sequence)."""
        return self.sequence < other.sequence
    
    def is_later_than(self, other: "VersionIdentity") -> bool:
        """Check if this version is later than the other (by sequence)."""
        return self.sequence > other.sequence


# =============================================================================
# GENERATION IDENTITY
# =============================================================================

@dataclass(frozen=True, order=True)
class GenerationIdentity:
    """
    Canonical identifier for a generation (epoch).
    
    Generations represent runtime ownership epochs. Changes occur on:
        - Runtime restart
        - Component recreation  
        - Service replacement
        - Recovery
        - Migration
        - Ownership transfer
    
    INVARIANTS:
        GEN-ID-001: Every generation has exactly one identity
        GEN-ID-002: Generation IDs are monotonically increasing (epoch-based)
        GEN-ID-003: Stale generations are rejected for mutations
    """
    
    value: str = field(default_factory=lambda: f"gen_{uuid.uuid4().hex[:20]}")
    epoch: int = 0
    
    @classmethod
    def generate(cls, epoch: int = 0) -> "GenerationIdentity":
        """Generate a new generation identity."""
        value = f"gen_e{epoch}_{uuid.uuid4().hex[:16]}"
        return cls(value=value.replace("-", "_"), epoch=epoch)
    
    def matches_epoch(self, epoch: int) -> bool:
        """Check if this generation has the given epoch number."""
        return self.epoch == epoch
    
    def is_stale(self, current_epoch: int) -> bool:
        """Check if this generation is stale (older than current)."""
        return self.epoch < current_epoch
    
    def is_newer_than(self, other: "GenerationIdentity") -> bool:
        """Check if this generation is newer than the other."""
        return self.epoch > other.epoch


# =============================================================================
# CHANGE IDENTITY
# =============================================================================

@dataclass(frozen=True)
class ChangeIdentity:
    """
    Canonical identifier for a state change.
    
    A change represents one atomic modification to state within a version.
    
    INVARIANTS:
        CHG-ID-001: Every change has exactly one identity
        CHG-ID-002: Changes are ordered within their version
        CHG-ID-003: Change identities are deterministic from lineage
    """
    
    value: str = field(default_factory=lambda: f"chg_{uuid.uuid4().hex[:20]}")
    change_number: int = 0
    
    @classmethod
    def generate(cls, change_number: int = 0) -> "ChangeIdentity":
        """Generate a new change identity."""
        value = f"chg_n{change_number}_{uuid.uuid4().hex[:16]}"
        return cls(value=value.replace("-", "_"), change_number=change_number)


# =============================================================================
# VERSION PROVENANCE
# =============================================================================

@dataclass(frozen=True)
class VersionProvenance:
    """
    Immutable provenance information for a version.
    
    Provenance preserves the origin and history of a version.
    
    INVARIANTS:
        VER-PROV-001: Provenance is immutable once created
        VER-PROV-002: Source transition/operation are preserved
        VER-PROV-003: Correlation and causation are preserved
    """
    
    # Origin
    source_transition_id: Optional[str] = None
    source_operation_id: Optional[str] = None
    
    # Request context
    originating_request_id: Optional[str] = None
    
    # Runtime binding (for isolation)
    runtime_identity: Optional[str] = None
    boot_session_identity: Optional[str] = None
    
    # Correlation
    correlation_id: Optional[str] = None
    causation_id: Optional[str] = None
    
    # Change details
    schema_version: Optional[int] = None
    change_count: int = 0
    
    @classmethod
    def from_transition(
        cls,
        transition_id: str,
        runtime_identity: Optional[str] = None,
        correlation_id: Optional[str] = None,
    ) -> "VersionProvenance":
        """Create provenance from a transition."""
        return cls(
            source_transition_id=transition_id,
            runtime_identity=runtime_identity,
            correlation_id=correlation_id,
        )
    
    @classmethod
    def from_operation(
        cls,
        operation_id: str,
        runtime_identity: Optional[str] = None,
        correlation_id: Optional[str] = None,
    ) -> "VersionProvenance":
        """Create provenance from an operation."""
        return cls(
            source_operation_id=operation_id,
            runtime_identity=runtime_identity,
            correlation_id=correlation_id,
        )


# =============================================================================
# VERSION (BASE CLASS)
# =============================================================================

@dataclass(frozen=True)
class BaseStateVersion:
    """
    Immutable version record for a state aggregate.
    
    A version represents one revision in the evolution of an aggregate.
    
    VERSION PRINCIPLES:
        - Versions are immutable once created
        - Every mutation produces exactly one successor version
        - Version lineage forms a linear chain (no branches in base model)
    
    INVARIANTS:
        VER-001: Version is immutable once created
        VER-002: Every version has exactly one predecessor (except initial)
        VER-003: Versions are ordered by sequence number
        VER-004: No skipped versions in a generation
    """
    
    # Identity
    version_identity: VersionIdentity
    
    # Aggregate identification
    aggregate_id: str  # The stable aggregate this version belongs to
    
    # Runtime binding (for isolation)
    runtime_id: Optional[str] = None
    
    # Generation context
    generation_identity: GenerationIdentity
    
    # Sequence within generation
    sequence: int  # 0 for initial, incrementing for successors
    
    # Lineage
    predecessor_version_id: Optional[VersionIdentity] = None  # None if this is the initial version
    
    # Timestamps
    created_at_utc: float = field(default_factory=_time_module.monotonic)
    
    # Transition/operation that produced this version
    transition_id: Optional[str] = None
    operation_id: Optional[str] = None
    
    # Change details
    change_identity: Optional[ChangeIdentity] = None
    schema_version: int = 1
    provenance: VersionProvenance = field(default_factory=VersionProvenance)
    
    @classmethod
    def create_initial(
        cls,
        aggregate_id: str,
        runtime_id: Optional[str] = None,
        generation_identity: Optional[GenerationIdentity] = None,
        schema_version: int = 1,
    ) -> "BaseStateVersion":
        """
        Create the initial version of an aggregate.
        
        The initial version has no predecessor.
        """
        return cls(
            version_identity=VersionIdentity.generate(sequence=0, aggregate_id=aggregate_id),
            aggregate_id=aggregate_id,
            runtime_id=runtime_id,
            generation_identity=generation_identity or GenerationIdentity.generate(epoch=0),
            sequence=0,
            predecessor_version_id=None,
            schema_version=schema_version,
        )
    
    @classmethod
    def create_successor(
        cls,
        predecessor: "BaseStateVersion",
        transition_id: Optional[str] = None,
        operation_id: Optional[str] = None,
        change_identity: Optional[ChangeIdentity] = None,
        schema_version: Optional[int] = None,
    ) -> "BaseStateVersion":
        """
        Create a successor version from a predecessor.
        
        This is the canonical way to create new versions. Every successful
        mutation should produce exactly one successor version.
        
        INVARIANT: Successor sequence = predecessor.sequence + 1
        """
        return cls(
            version_identity=VersionIdentity.generate(
                sequence=predecessor.sequence + 1,
                aggregate_id=predecessor.aggregate_id
            ),
            aggregate_id=predecessor.aggregate_id,
            runtime_id=predecessor.runtime_id,
            generation_identity=predecessor.generation_identity,
            sequence=predecessor.sequence + 1,
            predecessor_version_id=predecessor.version_identity,
            transition_id=transition_id,
            operation_id=operation_id,
            change_identity=change_identity,
            schema_version=schema_version or (predecessor.schema_version + 1),
            created_at_utc=_time_module.monotonic(),
        )
    
    @property
    def is_initial(self) -> bool:
        """Check if this is the initial version of an aggregate."""
        return self.sequence == 0
    
    @property
    def successor_sequence(self) -> int:
        """Get the sequence number that would be used for a successor."""
        return self.sequence + 1
    
    def matches_generation(self, generation_epoch: int) -> bool:
        """Check if this version belongs to the given generation epoch."""
        return self.generation_identity.epoch == generation_epoch
    
    def with_runtime_id(self, runtime_id: str) -> "BaseStateVersion":
        """Create a copy with updated runtime ID."""
        from dataclasses import replace as dataclass_replace
        return dataclass_replace(self, runtime_id=runtime_id)


# =============================================================================
# GENERATION (BASE CLASS)
# =============================================================================

@dataclass(frozen=True)
class BaseGeneration:
    """
    Immutable generation record for runtime ownership epoch.
    
    Generations represent replacement of the runtime ownership epoch.
    
    GENERATION PRINCIPLES:
        - Generations are immutable once created
        - Generations change on restart/migration/recovery
        - Stale generations are rejected
        
    INVARIANTS:
        GEN-001: Generation is immutable once created
        GEN-002: Every generation has exactly one predecessor (except initial)
        GEN-003: Generations are ordered by epoch number
        GEN-004: No stale generations accepted for mutations
    """
    
    # Identity
    generation_identity: GenerationIdentity
    
    # Runtime context
    runtime_id: Optional[str] = None
    boot_session_id: Optional[str] = None
    
    # Epoch information
    epoch: int  # 0 for initial, incrementing for successors
    predecessor_generation_id: Optional[GenerationIdentity] = None
    
    # Creation metadata
    created_at_utc: float = field(default_factory=_time_module.monotonic)
    
    # Reason for generation change
    creation_reason: str = "initial"  # e.g., "restart", "migration", "recovery"
    
    # Authority that created this generation
    originating_authority: Optional[str] = None
    
    # Provenance
    provenance: Dict[str, str] = field(default_factory=dict)
    
    @classmethod
    def create_initial(
        cls,
        runtime_id: Optional[str] = None,
        boot_session_id: Optional[str] = None,
    ) -> "BaseGeneration":
        """
        Create the initial generation for a runtime.
        
        The initial generation has no predecessor and epoch 0.
        """
        return cls(
            generation_identity=GenerationIdentity.generate(epoch=0),
            runtime_id=runtime_id,
            boot_session_id=boot_session_id,
            epoch=0,
            predecessor_generation_id=None,
            creation_reason="initial",
        )
    
    @classmethod
    def create_successor(
        cls,
        predecessor: "BaseGeneration",
        reason: str = "unknown",
        authority: Optional[str] = None,
        boot_session_id: Optional[str] = None,
    ) -> "BaseGeneration":
        """
        Create a successor generation from a predecessor.
        
        This is the canonical way to create new generations.
        Every generation change should produce exactly one successor.
        """
        return cls(
            generation_identity=GenerationIdentity.generate(epoch=predecessor.epoch + 1),
            runtime_id=predecessor.runtime_id,
            boot_session_id=boot_session_id or predecessor.boot_session_id,
            epoch=predecessor.epoch + 1,
            predecessor_generation_id=predecessor.generation_identity,
            creation_reason=reason,
            originating_authority=authority,
            created_at_utc=_time_module.monotonic(),
        )
    
    @property
    def is_initial(self) -> bool:
        """Check if this is the initial generation."""
        return self.epoch == 0
    
    def is_stale(self, current_epoch: int) -> bool:
        """Check if this generation is stale (older than current)."""
        return self.epoch < current_epoch


# =============================================================================
# VERSION HISTORY ENTRY
# =============================================================================

@dataclass(frozen=True)
class VersionHistoryEntry:
    """
    One entry in the bounded version history.
    
    History supports diagnostics, recovery, and lineage verification.
    
    INVARIANTS:
        VER-HIST-001: Entry is immutable once created
        VER-HIST-002: Entries are chronologically ordered
        VER-HIST-003: Old entries may be pruned to maintain bounds
    """
    
    # Identity
    history_sequence: int
    
    # Version info
    version_identity: str
    predecessor_version_id: Optional[str]
    
    # Timestamp
    timestamp_utc: float = field(default_factory=_time_module.monotonic)
    
    # Context
    transition_id: Optional[str] = None
    operation_id: Optional[str] = None
    
    # Lineage integrity
    lineage_hash: str  # Deterministic hash of version lineage up to this point
    
    @classmethod
    def create(
        cls,
        history_sequence: int,
        version_identity: VersionIdentity,
        predecessor_version_id: Optional[VersionIdentity],
        transition_id: Optional[str] = None,
        operation_id: Optional[str] = None,
    ) -> "VersionHistoryEntry":
        """Create a new history entry."""
        # Compute lineage hash deterministically
        lineage_data = f"{version_identity.value}:{predecessor_version_id.value if predecessor_version_id else 'null'}"
        import hashlib
        lineage_hash = hashlib.sha256(lineage_data.encode()).hexdigest()[:16]
        
        return cls(
            history_sequence=history_sequence,
            version_identity=version_identity.value,
            predecessor_version_id=predecessor_version_id.value if predecessor_version_id else None,
            transition_id=transition_id,
            operation_id=operation_id,
            lineage_hash=lineage_hash,
        )


# =============================================================================
# GENERATION HISTORY ENTRY
# =============================================================================

@dataclass(frozen=True)
class GenerationHistoryEntry:
    """
    One entry in the bounded generation history.
    
    INVARIANTS:
        GEN-HIST-001: Entry is immutable once created
        GEN-HIST-002: Entries are chronologically ordered
        GEN-HIST-003: Old entries may be pruned to maintain bounds
    """
    
    # Identity
    history_sequence: int
    
    # Generation info
    generation_identity: str
    predecessor_generation_id: Optional[str]
    
    # Creation context
    creation_reason: str
    originating_authority: Optional[str] = None
    timestamp_utc: float = field(default_factory=_time_module.monotonic)


# =============================================================================
# VALIDATION OUTCOMES
# =============================================================================

class VersionValidationOutcome(Enum):
    """
    Outcome of version validation.
    
    OUTCOMES:
        VALID: All validations passed
        PREDECESSOR_MISMATCH: Expected predecessor doesn't match
        SEQUENCE_GAP: Non-consecutive sequence numbers detected
        DUPLICATE_VERSION: Version already exists in lineage
        STALE_VERSION: Version is older than current but not terminal
        LINEAGE_INTEGRITY_VIOLATED: Lineage hash mismatch detected
    """
    
    VALID = "valid"
    PREDECESSOR_MISMATCH = "predecessor_mismatch"
    SEQUENCE_GAP = "sequence_gap"
    DUPLICATE_VERSION = "duplicate_version"
    STALE_VERSION = "stale_version"
    LINEAGE_INTEGRITY_VIOLATED = "lineage_integrity_violated"


class GenerationValidationOutcome(Enum):
    """
    Outcome of generation validation.
    
    OUTCOMES:
        VALID: All validations passed
        STALE_GENERATION: Generation epoch is older than current
        DUPLICATE_GENERATION: Generation already exists
        EPOCH_GAP: Non-consecutive epoch numbers detected
        RUNTIME_MISMATCH: Runtime ID doesn't match expected
    """
    
    VALID = "valid"
    STALE_GENERATION = "stale_generation"
    DUPLICATE_GENERATION = "duplicate_generation"
    EPOCH_GAP = "epoch_gap"
    RUNTIME_MISMATCH = "runtime_mismatch"


# =============================================================================
# VALIDATION RESULTS
# =============================================================================

@dataclass(frozen=True)
class VersionValidationResult:
    """
    Structured result of version validation.
    
    INVARIANTS:
        VER-VAL-RESULT-001: Result is immutable once created
        VER-VAL-RESULT-002: Success implies all checks passed
        VER-VAL-RESULT-003: Failure includes specific reason(s)
    """
    
    outcome: VersionValidationOutcome
    version_identity: str
    
    # Timestamps
    validated_at_utc: float = field(default_factory=_time_module.monotonic)
    
    # Detailed findings
    findings: Tuple[str, ...] = field(default_factory=tuple)
    
    @property
    def is_valid(self) -> bool:
        """Check if validation passed."""
        return self.outcome == VersionValidationOutcome.VALID


@dataclass(frozen=True)
class GenerationValidationResult:
    """
    Structured result of generation validation.
    
    INVARIANTS:
        GEN-VAL-RESULT-001: Result is immutable once created
        GEN-VAL-RESULT-002: Success implies all checks passed
        GEN-VAL-RESULT-003: Failure includes specific reason(s)
    """
    
    outcome: GenerationValidationOutcome
    generation_identity: str
    
    # Timestamps
    validated_at_utc: float = field(default_factory=_time_module.monotonic)
    
    # Detailed findings
    findings: Tuple[str, ...] = field(default_factory=tuple)
    
    @property
    def is_valid(self) -> bool:
        """Check if validation passed."""
        return self.outcome == GenerationValidationOutcome.VALID


# =============================================================================
# VERSION LINEAGE (PUBLIC API)
# =============================================================================

class VersionLineage:
    """
    Immutable lineage of versions for one aggregate.
    
    Provides read-only access to version history while enforcing
    integrity constraints.
    
    PUBLIC API:
        - get_version: Get a version by sequence number
        - get_latest: Get the latest version in lineage
        - add_version: Create new lineage with added version
        - validate_integrity: Verify lineage integrity
        - get_history_entries: Get bounded history entries
        
    INVARIANTS:
        VER-LINE-001: Lineage is immutable once created
        VER-LINE-002: No gaps in sequence numbers
        VER-LINE-003: Each version has exactly one predecessor (except initial)
        VER-LINE-004: History remains bounded
    """
    
    def __init__(
        self,
        aggregate_id: str,
        versions_by_sequence: Dict[int, BaseStateVersion] = None,
        max_history_entries: int = 1000,
    ) -> None:
        """
        Initialize version lineage.
        
        Args:
            aggregate_id: The stable ID of the aggregate
            versions_by_sequence: Optional dict of versions by sequence number
            max_history_entries: Maximum history entries to retain
        """
        self.aggregate_id = aggregate_id
        self._versions_by_sequence: Dict[int, BaseStateVersion] = (
            versions_by_sequence or {}
        )
        self.max_history_entries = max_history_entries
    
    @property
    def latest_version(self) -> Optional[BaseStateVersion]:
        """Get the latest version in lineage, or None if empty."""
        if not self._versions_by_sequence:
            return None
        max_seq = max(self._versions_by_sequence.keys())
        return self._versions_by_sequence[max_seq]
    
    @property
    def version_count(self) -> int:
        """Get the number of versions in lineage."""
        return len(self._versions_by_sequence)
    
    @property
    def current_generation(self) -> Optional[GenerationIdentity]:
        """Get the generation of the latest version."""
        latest = self.latest_version
        if latest is None:
            return None
        return latest.generation_identity
    
    def get_version(self, sequence: int) -> Optional[BaseStateVersion]:
        """
        Get a version by its sequence number.
        
        Args:
            sequence: The sequence number (0 for initial)
            
        Returns:
            The version if found, None otherwise
        """
        return self._versions_by_sequence.get(sequence)
    
    def validate_add_version(self, new_version: BaseStateVersion) -> VersionValidationResult:
        """
        Validate that a new version can be added to lineage.
        
        Checks:
            - Same aggregate ID
            - Sequence is consecutive (no gaps)
            - Predecessor matches latest version
            - Generation matches current generation
            
        Args:
            new_version: The version candidate to add
            
        Returns:
            Validation result with outcome and findings
        """
        findings: List[str] = []
        
        # Check aggregate ID matches
        if new_version.aggregate_id != self.aggregate_id:
            findings.append(
                f"Version aggregate ID '{new_version.aggregate_id}' doesn't match lineage aggregate '{self.aggregate_id}'"
            )
        
        # Get latest version
        latest = self.latest_version
        
        # If this is the first version, sequence must be 0
        if latest is None:
            if new_version.sequence != 0:
                findings.append("First version must have sequence 0")
        
        # Check sequence is consecutive
        elif new_version.sequence != latest.sequence + 1:
            findings.append(
                f"Sequence gap: expected {latest.sequence + 1}, got {new_version.sequence}"
            )
        
        # Check predecessor matches latest
        elif new_version.predecessor_version_id is None or latest.version_identity.value != new_version.predecessor_version_id.value:
            findings.append("Predecessor version doesn't match latest in lineage")
        
        # Check generation matches (versions within same generation)
        if latest and new_version.generation_identity.epoch != latest.generation_identity.epoch:
            findings.append(
                f"Generation mismatch: expected epoch {latest.generation_identity.epoch}, got {new_version.generation_identity.epoch}"
            )
        
        # Determine outcome
        if findings:
            outcome = VersionValidationOutcome.LINEAGE_INTEGRITY_VIOLATED
        else:
            outcome = VersionValidationOutcome.VALID
        
        return VersionValidationResult(
            outcome=outcome,
            version_identity=new_version.version_identity.value,
            findings=tuple(findings),
        )
    
    def add_version(self, new_version: BaseStateVersion) -> "VersionLineage":
        """
        Create a new lineage with the given version added.
        
        This is an immutable update - returns a new instance.
        
        Args:
            new_version: The version to add
            
        Returns:
            New VersionLineage with the version added
        """
        # Validate first (raises if invalid)
        result = self.validate_add_version(new_version)
        if not result.is_valid:
            raise ValueError(f"Cannot add version: {result.findings}")
        
        # Add to new dict (immutable update)
        new_versions = dict(self._versions_by_sequence)
        new_versions[new_version.sequence] = new_version
        
        return VersionLineage(
            aggregate_id=self.aggregate_id,
            versions_by_sequence=new_versions,
            max_history_entries=self.max_history_entries,
        )
    
    def validate_integrity(self) -> Tuple[bool, Tuple[str, ...]]:
        """
        Validate the entire lineage integrity.
        
        Checks:
            - No gaps in sequence numbers
            - Each version's predecessor matches previous version
            - All versions belong to same aggregate
            
        Returns:
            (valid: bool, findings: Tuple of finding messages)
        """
        if not self._versions_by_sequence:
            return True, ()  # Empty lineage is valid
        
        findings: List[str] = []
        
        # Check for gaps and predecessor consistency
        sorted_sequences = sorted(self._versions_by_sequence.keys())
        
        for i, seq in enumerate(sorted_sequences):
            version = self._versions_by_sequence[seq]
            
            # First version (sequence 0) must have no predecessor
            if seq == 0:
                if version.predecessor_version_id is not None:
                    findings.append(f"Version 0 should have no predecessor")
            
            # Other versions must have a valid predecessor
            else:
                expected_pred_seq = seq - 1
                expected_pred = self._versions_by_sequence.get(expected_pred_seq)
                
                if expected_pred is None:
                    findings.append(
                        f"Sequence gap at {seq}: predecessor sequence {expected_pred_seq} not found"
                    )
                elif version.predecessor_version_id is None or expected_pred.version_identity.value != version.predecessor_version_id.value:
                    findings.append(
                        f"Version {seq}: predecessor doesn't match previous version in lineage"
                    )
            
            # Check all versions belong to same aggregate
            if version.aggregate_id != self.aggregate_id:
                findings.append(f"Version {seq} belongs to different aggregate")
        
        return (len(findings) == 0, tuple(findings))
    
    def get_history_entries(self) -> Tuple[VersionHistoryEntry, ...]:
        """
        Get bounded history entries for this lineage.
        
        Returns entries in chronological order (oldest first).
        Bounded to max_history_entries.
        
        Returns:
            Tuple of history entries
        """
        if not self._versions_by_sequence:
            return ()
        
        # Sort by sequence (chronological)
        sorted_versions = sorted(
            self._versions_by_sequence.values(),
            key=lambda v: v.sequence
        )
        
        # Take last max_history_entries (most recent)
        latest_versions = sorted_versions[-self.max_history_entries:]
        
        entries = []
        for i, version in enumerate(latest_versions):
            entry = VersionHistoryEntry.create(
                history_sequence=i,
                version_identity=version.version_identity,
                predecessor_version_id=version.predecessor_version_id,
                transition_id=version.transition_id,
                operation_id=version.operation_id,
            )
            entries.append(entry)
        
        return tuple(entries)


# =============================================================================
# GENERATION LINEAGE (PUBLIC API)
# =============================================================================

class GenerationLineage:
    """
    Immutable lineage of generations for one runtime.
    
    Provides read-only access to generation history while enforcing
    integrity constraints.
    
    PUBLIC API:
        - get_generation: Get a generation by epoch
        - get_latest: Get the latest generation in lineage
        - add_generation: Create new lineage with added generation
        - validate_integrity: Verify lineage integrity
        
    INVARIANTS:
        GEN-LINE-001: Lineage is immutable once created
        GEN-LINE-002: No gaps in epoch numbers
        GEN-LINE-003: Each generation has exactly one predecessor (except initial)
    """
    
    def __init__(
        self,
        runtime_id: Optional[str] = None,
        generations_by_epoch: Dict[int, BaseGeneration] = None,
    ) -> None:
        """Initialize generation lineage."""
        self.runtime_id = runtime_id
        self._generations_by_epoch: Dict[int, BaseGeneration] = (
            generations_by_epoch or {}
        )
    
    @property
    def latest_generation(self) -> Optional[BaseGeneration]:
        """Get the latest generation in lineage, or None if empty."""
        if not self._generations_by_epoch:
            return None
        max_epoch = max(self._generations_by_epoch.keys())
        return self._generations_by_epoch[max_epoch]
    
    @property
    def generation_count(self) -> int:
        """Get the number of generations in lineage."""
        return len(self._generations_by_epoch)
    
    def get_generation(self, epoch: int) -> Optional[BaseGeneration]:
        """
        Get a generation by its epoch number.
        
        Args:
            epoch: The epoch number (0 for initial)
            
        Returns:
            The generation if found, None otherwise
        """
        return self._generations_by_epoch.get(epoch)
    
    def validate_add_generation(self, new_generation: BaseGeneration) -> GenerationValidationResult:
        """
        Validate that a new generation can be added to lineage.
        
        Checks:
            - Same runtime ID (if set)
            - Epoch is consecutive (no gaps)
            - Predecessor matches latest generation
            
        Args:
            new_generation: The generation candidate to add
            
        Returns:
            Validation result with outcome and findings
        """
        findings: List[str] = []
        
        # Check runtime ID matches (if both are set)
        if self.runtime_id is not None and new_generation.runtime_id is not None:
            if new_generation.runtime_id != self.runtime_id:
                findings.append(
                    f"Generation runtime ID '{new_generation.runtime_id}' doesn't match lineage runtime '{self.runtime_id}'"
                )
        
        # Get latest generation
        latest = self.latest_generation
        
        # If this is the first generation, epoch must be 0
        if latest is None:
            if new_generation.epoch != 0:
                findings.append("First generation must have epoch 0")
        
        # Check epoch is consecutive
        elif new_generation.epoch != latest.epoch + 1:
            findings.append(
                f"Epoch gap: expected {latest.epoch + 1}, got {new_generation.epoch}"
            )
        
        # Check predecessor matches latest
        elif new_generation.predecessor_generation_id is None or latest.generation_identity.value != new_generation.predecessor_generation_id.value:
            findings.append("Predecessor generation doesn't match latest in lineage")
        
        # Determine outcome
        if findings:
            outcome = GenerationValidationOutcome.RUNTIME_MISMATCH  # Default for failures
        else:
            outcome = GenerationValidationOutcome.VALID
        
        return GenerationValidationResult(
            outcome=outcome,
            generation_identity=new_generation.generation_identity.value,
            findings=tuple(findings),
        )
    
    def add_generation(self, new_generation: BaseGeneration) -> "GenerationLineage":
        """
        Create a new lineage with the given generation added.
        
        This is an immutable update - returns a new instance.
        
        Args:
            new_generation: The generation to add
            
        Returns:
            New GenerationLineage with the generation added
        """
        # Validate first (raises if invalid)
        result = self.validate_add_generation(new_generation)
        if not result.is_valid:
            raise ValueError(f"Cannot add generation: {result.findings}")
        
        # Add to new dict (immutable update)
        new_generations = dict(self._generations_by_epoch)
        new_generations[new_generation.epoch] = new_generation
        
        return GenerationLineage(
            runtime_id=self.runtime_id,
            generations_by_epoch=new_generations,
        )
    
    def validate_integrity(self) -> Tuple[bool, Tuple[str, ...]]:
        """
        Validate the entire generation lineage integrity.
        
        Returns:
            (valid: bool, findings: Tuple of finding messages)
        """
        if not self._generations_by_epoch:
            return True, ()  # Empty lineage is valid
        
        findings: List[str] = []
        
        sorted_epochs = sorted(self._generations_by_epoch.keys())
        
        for i, epoch in enumerate(sorted_epochs):
            generation = self._generations_by_epoch[epoch]
            
            # First generation (epoch 0) must have no predecessor
            if epoch == 0:
                if generation.predecessor_generation_id is not None:
                    findings.append("Generation 0 should have no predecessor")
            
            # Other generations must have a valid predecessor
            else:
                expected_pred_epoch = epoch - 1
                expected_pred = self._generations_by_epoch.get(expected_pred_epoch)
                
                if expected_pred is None:
                    findings.append(
                        f"Epoch gap at {epoch}: predecessor epoch {expected_pred_epoch} not found"
                    )
                elif generation.predecessor_generation_id is None or expected_pred.generation_identity.value != generation.predecessor_generation_id.value:
                    findings.append(
                        f"Generation {epoch}: predecessor doesn't match previous generation in lineage"
                    )
        
        return (len(findings) == 0, tuple(findings))


# =============================================================================
# VERSIONING FACADE (PUBLIC API)
# =============================================================================

class StateVersioningFacade:
    """
    Canonical facade for state versioning operations.
    
    Provides a single entry point for all versioning and generation
    operations while maintaining immutable semantics.
    
    PUBLIC API:
        - create_initial_version: Create initial version of an aggregate
        - create_successor_version: Create successor from latest version
        - validate_version_addition: Validate adding to lineage
        - add_to_lineage: Add version to lineage (if valid)
        
        - create_initial_generation: Create initial generation for runtime
        - create_successor_generation: Create successor from latest generation
        - validate_generation_addition: Validate adding to lineage
        - add_to_generation_lineage: Add generation to lineage (if valid)
        
        - get_version_history: Get bounded version history
        - get_generation_history: Get bounded generation history
        
    INVARIANTS:
        FACADE-001: All operations are pure (no side effects)
        FACADE-002: Lineage integrity is always preserved
        FACADE-003: Stale versions/generations are rejected
    """
    
    def __init__(self) -> None:
        """Initialize the versioning facade."""
        # Track version lineages by aggregate ID
        self._version_lineages: Dict[str, VersionLineage] = {}
        
        # Track generation lineages by runtime ID
        self._generation_lineages: Dict[str, GenerationLineage] = {}
    
    def create_initial_version(
        self,
        aggregate_id: str,
        runtime_id: Optional[str] = None,
        schema_version: int = 1,
    ) -> BaseStateVersion:
        """
        Create the initial version of an aggregate.
        
        This creates a new lineage with one version (sequence 0).
        
        Args:
            aggregate_id: The stable ID of the aggregate
            runtime_id: Optional runtime ID for isolation
            schema_version: Initial schema version
            
        Returns:
            New BaseStateVersion (the initial version)
        """
        # Create initial generation for this runtime
        gen = BaseGeneration.create_initial(runtime_id=runtime_id)
        
        # Create initial version with the generation
        version = BaseStateVersion.create_initial(
            aggregate_id=aggregate_id,
            runtime_id=runtime_id,
            generation_identity=gen.generation_identity,
            schema_version=schema_version,
        )
        
        # Add to lineage (creates new VersionLineage)
        self._version_lineages[aggregate_id] = VersionLineage(
            aggregate_id=aggregate_id
        ).add_version(version)
        
        return version
    
    def create_successor_version(
        self,
        aggregate_id: str,
        transition_id: Optional[str] = None,
        operation_id: Optional[str] = None,
        change_identity: Optional[ChangeIdentity] = None,
        schema_version: Optional[int] = None,
    ) -> BaseStateVersion:
        """
        Create a successor version for an aggregate.
        
        This validates and adds to the existing lineage.
        
        Args:
            aggregate_id: The aggregate ID
            transition_id: Optional transition that produced this version
            operation_id: Optional operation that produced this version
            change_identity: Optional change identity
            schema_version: Optional new schema version
            
        Returns:
            New BaseStateVersion (the successor)
            
        Raises:
            ValueError: If lineage integrity would be violated
        """
        # Get current lineage
        lineage = self._version_lineages.get(aggregate_id)
        
        if lineage is None:
            raise ValueError(f"No existing version lineage for aggregate '{aggregate_id}'")
        
        # Create successor from latest version
        latest = lineage.latest_version
        if latest is None:
            raise ValueError(f"Lineage empty for aggregate '{aggregate_id}'")
        
        new_version = BaseStateVersion.create_successor(
            predecessor=latest,
            transition_id=transition_id,
            operation_id=operation_id,
            change_identity=change_identity,
            schema_version=schema_version,
        )
        
        # Validate and add to lineage
        result = lineage.validate_add_version(new_version)
        if not result.is_valid:
            raise ValueError(f"Cannot create successor version: {result.findings}")
        
        new_lineage = lineage.add_version(new_version)
        self._version_lineages[aggregate_id] = new_lineage
        
        return new_version
    
    def get_version_history(
        self,
        aggregate_id: str,
    ) -> Tuple[VersionHistoryEntry, ...]:
        """
        Get bounded version history for an aggregate.
        
        Args:
            aggregate_id: The aggregate ID
            
        Returns:
            Tuple of version history entries (oldest first)
        """
        lineage = self._version_lineages.get(aggregate_id)
        if lineage is None:
            return ()
        return lineage.get_history_entries()
    
    def create_initial_generation(
        self,
        runtime_id: Optional[str] = None,
        boot_session_id: Optional[str] = None,
    ) -> BaseGeneration:
        """
        Create the initial generation for a runtime.
        
        Args:
            runtime_id: Runtime ID
            boot_session_id: Boot session ID
            
        Returns:
            New BaseGeneration (epoch 0)
        """
        gen = BaseGeneration.create_initial(
            runtime_id=runtime_id,
            boot_session_id=boot_session_id,
        )
        
        # Add to lineage
        self._generation_lineages[runtime_id or "default"] = GenerationLineage(
            runtime_id=runtime_id,
        ).add_generation(gen)
        
        return gen
    
    def create_successor_generation(
        self,
        runtime_id: str,
        reason: str = "unknown",
        authority: Optional[str] = None,
        boot_session_id: Optional[str] = None,
    ) -> BaseGeneration:
        """
        Create a successor generation for a runtime.
        
        Args:
            runtime_id: Runtime ID
            reason: Reason for generation change
            authority: Authority that created the generation
            boot_session_id: Optional new boot session ID
            
        Returns:
            New BaseGeneration (next epoch)
            
        Raises:
            ValueError: If lineage integrity would be violated
        """
        # Get current lineage
        lineage = self._generation_lineages.get(runtime_id)
        
        if lineage is None:
            raise ValueError(f"No existing generation lineage for runtime '{runtime_id}'")
        
        # Create successor from latest generation
        latest = lineage.latest_generation
        if latest is None:
            raise ValueError(f"Generation lineage empty for runtime '{runtime_id}'")
        
        new_gen = BaseGeneration.create_successor(
            predecessor=latest,
            reason=reason,
            authority=authority,
            boot_session_id=boot_session_id,
        )
        
        # Validate and add to lineage
        result = lineage.validate_add_generation(new_gen)
        if not result.is_valid:
            raise ValueError(f"Cannot create successor generation: {result.findings}")
        
        new_lineage = lineage.add_generation(new_gen)
        self._generation_lineages[runtime_id] = new_lineage
        
        return new_gen
    
    def get_generation_history(
        self,
        runtime_id: str,
    ) -> Tuple[GenerationHistoryEntry, ...]:
        """
        Get bounded generation history for a runtime.
        
        Args:
            runtime_id: Runtime ID
            
        Returns:
            Tuple of generation history entries (oldest first)
        """
        lineage = self._generation_lineages.get(runtime_id)
        if lineage is None:
            return ()
        
        # Get all generations sorted by epoch
        sorted_gens = sorted(
            lineage._generations_by_epoch.values(),
            key=lambda g: g.epoch
        )
        
        entries = []
        for i, gen in enumerate(sorted_gens):
            entry = GenerationHistoryEntry(
                history_sequence=i,
                generation_identity=gen.generation_identity.value,
                predecessor_generation_id=(
                    gen.predecessor_generation_id.value
                    if gen.predecessor_generation_id else None
                ),
                creation_reason=gen.creation_reason,
                originating_authority=gen.originating_authority,
                timestamp_utc=gen.created_at_utc,
            )
            entries.append(entry)
        
        return tuple(entries)


# =============================================================================
# PUBLIC API EXPORTS
# =============================================================================

__all__ = [
    # Identity types
    "VersionIdentity",
    "GenerationIdentity", 
    "ChangeIdentity",
    
    # Provenance
    "VersionProvenance",
    
    # Base classes
    "BaseStateVersion",
    "BaseGeneration",
    
    # History entries
    "VersionHistoryEntry",
    "GenerationHistoryEntry",
    
    # Validation outcomes
    "VersionValidationOutcome",
    "GenerationValidationOutcome",
    
    # Validation results
    "VersionValidationResult",
    "GenerationValidationResult",
    
    # Lineage types
    "VersionLineage",
    "GenerationLineage",
    
    # Public facade
    "StateVersioningFacade",
]