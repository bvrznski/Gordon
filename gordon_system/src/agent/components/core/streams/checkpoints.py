# Stream Checkpointing Infrastructure - Phase 3.11.6
# ====================================================

"""
Canonical Checkpoint Architecture for Gordon's Semantic Streams.

This module implements:
    - Checkpoint identity and validation
    - Immutable checkpoint descriptors
    - Consistency levels and scopes
    - Cursor checkpoints
    - Integrity verification
    - Serialization with versioning

Architecture Overview:

Checkpoint Axis (Continuation of Stream Continuity):
    Stream → Generation → Record → Commit → [Checkpoint] → Replay Cursor
    
Checkpoint Purpose:
    - Validate committed stream boundaries
    - Enable crash recovery via cursor restoration
    - Provide replay entry points
    - Preserve consumer progress safely

Ownership Model:
    Core owns: Checkpoint infrastructure, descriptor validation,
               serialization, integrity, persistence interfaces
    Consumers own: Cursor checkpoints for their subscriptions
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple, Any, Protocol, runtime_checkable
from enum import Enum, auto
import time
import uuid
import hashlib

# Import from core streams modules
from .__init__ import (
    StreamId,
    StreamGenerationId,
    StreamRecordId,
    StreamCommitId,
    CursorPosition,
)


# =============================================================================
# CHECKPOINT IDENTITY TYPES - Typed, Immutable, Deterministic
# =============================================================================


class CheckpointIdType(Enum):
    """Categories of checkpoint identity."""
    CHECKPOINT = "checkpoint"           # Main checkpoint record
    SCHEMA = "schema"                   # Schema version identifier
    VERSION = "version"                 # Version within schema
    GENERATION = "generation"           # Generation reference
    SET_ID = "set_id"                   # Checkpoint set membership
    REQUEST = "request"                 # Request that triggered checkpoint
    COMMIT = "commit"                   # Commit reference


@dataclass(frozen=True)
class CheckpointId:
    """
    Immutable identifier for a checkpoint.
    
    Format: checkpoint:{timestamp_ns}:{nonce}
    """
    
    value: str
    
    @classmethod
    def generate(cls) -> "CheckpointId":
        """Generate a new unique checkpoint ID."""
        ts = time.monotonic_ns()
        nonce = uuid.uuid4().hex[:8]
        return cls(value=f"checkpoint:{ts}:{nonce}")
    
    def __str__(self) -> str:
        return self.value
    
    def __hash__(self) -> int:
        return hash(self.value)


@dataclass(frozen=True)
class CheckpointSetId:
    """
    Identifier for a set of related checkpoints.
    
    Used when multiple streams must be checkpointed together.
    """
    
    value: str
    
    @classmethod
    def generate(cls) -> "CheckpointSetId":
        """Generate a new checkpoint set ID."""
        ts = time.monotonic_ns()
        nonce = uuid.uuid4().hex[:8]
        return cls(value=f"cpset:{ts}:{nonce}")
    
    def __hash__(self) -> int:
        return hash(self.value)


@dataclass(frozen=True)
class CheckpointVersion:
    """
    Version of a checkpoint schema/contract.
    
    Used to track compatibility between checkpoint producers and consumers.
    """
    
    major: int
    minor: int
    patch: int
    
    @classmethod
    def from_string(cls, s: str) -> "CheckpointVersion":
        """Parse version string (e.g., '1.2.3')."""
        parts = s.split(".")
        return cls(
            major=int(parts[0]) if len(parts) > 0 else 0,
            minor=int(parts[1]) if len(parts) > 1 else 0,
            patch=int(parts[2]) if len(parts) > 2 else 0
        )
    
    def __str__(self) -> str:
        return f"{self.major}.{self.minor}.{self.patch}"


# =============================================================================
# CHECKPOINT SCOPE - What's Included in a Checkpoint
# =============================================================================


class CheckpointScope(Enum):
    """
    Scope of what a checkpoint includes.
    
    Defines exactly what metadata is captured and preserved.
    """
    
    STREAM_POSITION_ONLY = "stream_position_only"           # Just committed position
    STREAM_AND_LIFECYCLE = "stream_and_lifecycle"          # Position + lifecycle state
    STREAM_AND_SELECTED_CURSORS = "stream_and_selected_cursors"  # Selected cursors
    STREAM_AND_ALL_ELIGIBLE_CURSORS = "stream_and_all_eligible_cursors"  # All cursors
    STREAM_GENERATION_FINAL = "stream_generation_final"     # Final generation state
    CONTINUITY_SAFE = "continuity_safe"                    # Safe for crash recovery
    OPERATOR_DIAGNOSTIC = "operator_diagnostic"            # Full diagnostic info
    OWNER_DEFINED = "owner_defined"                         # Owner-specified scope


# =============================================================================
# CHECKPOINT CONSISTENCY LEVEL - Validation Guarantees
# =============================================================================


class CheckpointConsistency(Enum):
    """
    Consistency guarantees provided by a checkpoint.
    
    Defines what state invariants are maintained at the boundary.
    """
    
    POSITION_CONSISTENT = "position_consistent"              # Position is valid
    GENERATION_CONSISTENT = "generation_consistent"         # Generation state is valid
    CURSOR_CONSISTENT = "cursor_consistent"                 # Cursor references are valid
    LIFECYCLE_CONSISTENT = "lifecycle_consistent"           # Lifecycle state consistent
    CONTINUITY_CONSISTENT = "continuity_consistent"         # Continuity-safe snapshot
    FINAL_GENERATION_CONSISTENT = "final_generation_consistent"  # Generation closed


# =============================================================================
# CHECKPOINT STATUS - State of a Checkpoint
# =============================================================================


class CheckpointStatus(Enum):
    """Lifecycle status of a checkpoint."""
    
    PROPOSED = "proposed"               # Created but not yet committed
    VALIDATED = "validated"             # Validation passed
    SERIALIZED = "serialized"           # Serialization complete
    PERSISTED = "persisted"             # Durable storage confirmed
    COMMITTED = "committed"             # Canonical commit complete
    EXPIRED = "expired"                 # No longer valid (retention exceeded)
    CORRUPTED = "corrupted"             # Integrity check failed


# =============================================================================
# CHECKPOINT CREATION MODE - How Checkpoint Was Created
# =============================================================================


class CheckpointCreationMode(Enum):
    """Mode of checkpoint creation."""
    
    ONLINE = "online"                   # Stream active during capture
    QUIESCENT = "quiescent"             # Stream paused temporarily
    DRAINED = "drained"                 # All in-flight work completed
    GENERATION_FINAL = "generation_final"  # After generation closure
    RECOVERY_PREPARATION = "recovery_preparation"  # Before restart
    CONTINUITY_PREPARATION = "continuity_preparation"  # For continuity


# =============================================================================
# CHECKPOINT REQUEST - Request for Checkpoint Creation
# =============================================================================


@dataclass(frozen=True)
class CheckpointRequest:
    """
    Immutable request to create a checkpoint.
    
    Contains all parameters needed to create and validate a checkpoint.
    Does NOT contain live objects, locks, or runtime state.
    """
    
    # Identity
    request_id: str                     # Unique request ID
    
    # Stream reference (stable identifiers)
    stream_id: str                      # Which stream?
    runtime_instance_id: str            # Which instance (for scoped ownership)
    
    # Expected state for validation
    expected_generation_id: Optional[str] = None  # Expected current generation
    expected_last_sequence: Optional[int] = None  # Expected last committed sequence
    
    # Requested scope and consistency
    checkpoint_scope: CheckpointScope = CheckpointScope.STREAM_POSITION_ONLY
    consistency_level: CheckpointConsistency = CheckpointConsistency.POSITION_CONSISTENT
    
    # What to include
    include_subscription_cursors: bool = False  # Include subscriber cursors?
    selected_cursor_ids: Tuple[str, ...] = field(default_factory=tuple)  # Specific cursors
    selected_consumer_group_ids: Tuple[str, ...] = field(default_factory=tuple)  # Consumer groups
    
    # Request metadata
    requested_by: Optional[str] = None          # Who requested?
    reason: str = "auto"                        # Reason for checkpoint
    deadline_utc: Optional[float] = None        # Deadline for creation
    
    # Correlation (for traceability)
    correlation_id: Optional[str] = None
    causation_id: Optional[str] = None
    
    # Authorization reference (not credentials)
    authorization_context_reference: Optional[str] = None
    
    # Provenance
    provenance: Dict[str, str] = field(default_factory=dict)
    
    @classmethod
    def for_position_only(cls, stream_id: str, runtime_instance_id: str) -> "CheckpointRequest":
        """Create a minimal checkpoint request for position only."""
        return cls(
            request_id=f"req-{time.monotonic_ns()}-{uuid.uuid4().hex[:8]}",
            stream_id=stream_id,
            runtime_instance_id=runtime_instance_id,
            checkpoint_scope=CheckpointScope.STREAM_POSITION_ONLY,
            consistency_level=CheckpointConsistency.POSITION_CONSISTENT,
        )
    
    @classmethod
    def for_continuity_safe(cls, stream_id: str, runtime_instance_id: str) -> "CheckpointRequest":
        """Create a continuity-safe checkpoint request."""
        return cls(
            request_id=f"req-{time.monotonic_ns()}-{uuid.uuid4().hex[:8]}",
            stream_id=stream_id,
            runtime_instance_id=runtime_instance_id,
            checkpoint_scope=CheckpointScope.CONTINUITY_SAFE,
            consistency_level=CheckpointConsistency.CONTINUITY_CONSISTENT,
        )
    
    def is_expired(self, at_utc: Optional[float] = None) -> bool:
        """Check if this request has expired."""
        if self.deadline_utc is None:
            return False
        at = at_utc or time.time()
        return at > self.deadline_utc


# =============================================================================
# CHECKPOINT DESCRIPTOR - Immutable Checkpoint Record
# =============================================================================


@dataclass(frozen=True)
class CheckpointDescriptor:
    """
    Immutable descriptor of a validated checkpoint.
    
    This is the canonical record that gets persisted and referenced by
    recovery systems. It contains ONLY bounded metadata - no live objects.
    
    A checkpoint becomes "committed" when validation, serialization,
    and persistence all succeed according to policy.
    """
    
    # Identity (canonical)
    checkpoint_id: str                  # Unique ID for this checkpoint
    schema_id: str                      # Schema version identifier
    version: CheckpointVersion          # Version of this descriptor format
    
    # Scope and consistency
    scope: CheckpointScope              # What's included?
    consistency_level: CheckpointConsistency  # What guarantees are valid?
    
    # Stream reference (stable identifiers)
    stream_id: str                      # Which stream?
    runtime_instance_id: str            # Which instance?
    generation_id: str                  # Current generation at checkpoint
    
    # Boundary position
    last_included_sequence: int         # Last committed sequence included
    last_included_commit_id: Optional[str] = None  # Commit reference (optional)
    
    # Lifecycle state at boundary
    lifecycle_state: str                # Current lifecycle state
    last_lifecycle_transition_id: Optional[str] = None  # Last transition
    
    # Configuration context (versioned references, not objects)
    ownership_version: int = 1          # Ownership configuration version
    configuration_generation: int = 1   # Configuration generation
    ordering_policy_id: str = "default" # Ordering policy reference
    ordering_policy_version: int = 1    # Policy version
    record_contract_version: int = 1    # Record contract version
    stream_contract_version: int = 1    # Stream contract version
    
    # Cursor references (stable IDs only, NOT live objects)
    cursor_checkpoint_references: Tuple[str, ...] = field(default_factory=tuple)  # Cursor checkpoint IDs
    consumer_group_positions: Tuple[Tuple[str, str], ...] = field(default_factory=tuple)  # (group_id, position_ref)
    
    # Retention boundary at time of checkpoint
    retention_boundary_earliest_sequence: Optional[int] = None
    
    # Timestamps
    created_at_utc: float               # When checkpoint was created
    persisted_at_utc: Optional[float] = None  # When persisted (if applicable)
    
    # Request reference
    created_by: Optional[str] = None    # Who/what created it?
    reason: str = "auto"                # Reason for creation
    correlation_id: Optional[str] = None
    causation_id: Optional[str] = None
    provenance: Dict[str, str] = field(default_factory=dict)
    
    # Integrity verification
    integrity_algorithm: str = "sha256"
    integrity_digest: Optional[str] = None  # Hash of canonical representation
    
    # Persistence reference (stable reference to durable storage)
    persistence_reference: Optional[str] = None  # e.g., "s3://bucket/checkpoint-id"
    
    # Continuity reference (for crash recovery)
    continuity_reference: Optional[str] = None  # Reference for continuity system
    
    # Status and metadata
    status: CheckpointStatus = CheckpointStatus.PROPOSED
    warnings: Tuple[str, ...] = field(default_factory=tuple)  # Non-fatal issues
    
    # Durability level (what persistence guarantees are provided?)
    durability_level: str = "ephemeral"  # ephemeral, process_local, host_local, durable_local, replicated
    
    @classmethod
    def create(
        cls,
        stream_id: str,
        runtime_instance_id: str,
        generation_id: str,
        last_included_sequence: int,
        lifecycle_state: str = "active",
    ) -> "CheckpointDescriptor":
        """
        Create a new checkpoint descriptor.
        
        This is the primary factory method. Additional configuration can be
        added via the with_* methods below.
        """
        return cls(
            checkpoint_id=CheckpointId.generate().value,
            schema_id="gordon.checkpoint.v1",
            version=CheckpointVersion(1, 0, 0),
            scope=CheckpointScope.STREAM_POSITION_ONLY,
            consistency_level=CheckpointConsistency.POSITION_CONSISTENT,
            stream_id=stream_id,
            runtime_instance_id=runtime_instance_id,
            generation_id=generation_id,
            last_included_sequence=last_included_sequence,
            lifecycle_state=lifecycle_state,
            created_at_utc=time.time(),
        )
    
    def with_scope(self, scope: CheckpointScope) -> "CheckpointDescriptor":
        """Return new descriptor with updated scope."""
        return dataclass_replace(self, scope=scope)
    
    def with_consistency(self, consistency: CheckpointConsistency) -> "CheckpointDescriptor":
        """Return new descriptor with updated consistency level."""
        return dataclass_replace(self, consistency_level=consistency)
    
    def with_cursors(self, cursor_checkpoint_ids: Tuple[str, ...]) -> "CheckpointDescriptor":
        """Return new descriptor with cursor checkpoint references."""
        return dataclass_replace(
            self,
            cursor_checkpoint_references=cursor_checkpoint_ids
        )
    
    def with_consumer_groups(
        self,
        group_positions: Tuple[Tuple[str, str], ...]
    ) -> "CheckpointDescriptor":
        """Return new descriptor with consumer group positions."""
        return dataclass_replace(self, consumer_group_positions=group_positions)
    
    def with_retention_boundary(self, earliest_sequence: int) -> "CheckpointDescriptor":
        """Return new descriptor with retention boundary information."""
        return dataclass_replace(
            self,
            retention_boundary_earliest_sequence=earliest_sequence
        )
    
    def with_persistence(self, reference: str, durability_level: str = "durable_local") -> "CheckpointDescriptor":
        """Return new descriptor with persistence reference."""
        return dataclass_replace(
            self,
            persistence_reference=reference,
            durability_level=durability_level,
            persisted_at_utc=time.time(),
        )
    
    def with_continuity(self, reference: str) -> "CheckpointDescriptor":
        """Return new descriptor with continuity reference."""
        return dataclass_replace(
            self,
            continuity_reference=reference
        )
    
    def mark_committed(self) -> "CheckpointDescriptor":
        """Mark checkpoint as committed."""
        if self.status == CheckpointStatus.COMMITTED:
            return self
        return dataclass_replace(self, status=CheckpointStatus.COMMITTED)
    
    def add_warning(self, warning: str) -> "CheckpointDescriptor":
        """Add a warning to the descriptor."""
        return dataclass_replace(
            self,
            warnings=self.warnings + (warning,)
        )
    
    def with_integrity_digest(self, digest: str) -> "CheckpointDescriptor":
        """Return new descriptor with integrity digest set."""
        return dataclass_replace(self, integrity_digest=digest)
    
    def is_expired(self, retention_seconds: int = 86400, at_utc: Optional[float] = None) -> bool:
        """
        Check if checkpoint has exceeded retention period.
        
        Args:
            retention_seconds: How long checkpoints are retained (default 24h)
            at_utc: Current time for comparison
        
        Returns:
            True if checkpoint is expired
        """
        at = at_utc or time.time()
        return (at - self.created_at_utc) > retention_seconds
    
    def verify_integrity(self, canonical_serialization: bytes) -> bool:
        """
        Verify integrity of this checkpoint descriptor.
        
        Args:
            canonical_serialization: The serialized representation
        
        Returns:
            True if integrity check passes
        """
        if self.integrity_digest is None:
            return False  # No digest to verify against
        
        hash_obj = hashlib.sha256(canonical_serialization)
        computed = hash_obj.hexdigest()
        return computed == self.integrity_digest


def dataclass_replace(obj: Any, **kwargs) -> Any:
    """Simple dataclass replace implementation for frozen dataclasses."""
    if hasattr(obj, "__dataclass_fields__"):
        field_dict = {f.name: getattr(obj, f.name) for f in obj.__dataclass_fields__.values()}
        field_dict.update(kwargs)
        return type(obj)(**field_dict)
    raise TypeError("Not a dataclass")


# =============================================================================
# CHECKPOINT VALIDATION - Validation Results
# =============================================================================


@dataclass(frozen=True)
class CheckpointValidationResult:
    """Result of checkpoint validation."""
    
    is_valid: bool
    errors: Tuple[str, ...] = field(default_factory=tuple)
    warnings: Tuple[str, ...] = field(default_factory=tuple)
    
    @classmethod
    def valid(cls) -> "CheckpointValidationResult":
        return cls(is_valid=True)
    
    @classmethod
    def invalid(cls, *errors: str) -> "CheckpointValidationResult":
        return cls(is_valid=False, errors=errors)
    
    @classmethod
    def with_warnings(
        cls,
        warnings: Tuple[str, ...]
    ) -> "CheckpointValidationResult":
        return cls(is_valid=True, warnings=warnings)


# =============================================================================
# CURSOR CHECKPOINT - Checkpoint for a Single Cursor
# =============================================================================


@dataclass(frozen=True)
class CursorCheckpoint:
    """
    Immutable checkpoint representing a recovery point for a cursor.
    
    Used to preserve subscriber progress for crash recovery.
    This is the low-level building block that higher-level checkpoints reference.
    """
    
    # Identity
    checkpoint_id: str                  # Unique ID
    
    # References (stable identifiers)
    stream_id: str                      # Which stream?
    subscription_id: Optional[str] = None  # Subscription reference
    subscriber_id: Optional[str] = None    # Subscriber reference
    
    # Cursor position
    cursor_position: CursorPosition     # Position at checkpoint time
    
    # Metadata
    created_at_utc: float = field(default_factory=time.time)
    version: int = 1                    # Version for updates
    
    # Provenance (for audit trail)
    created_by: Optional[str] = None
    reason: str = "auto"                # Reason for checkpoint creation
    
    # Integrity verification
    integrity_digest: Optional[str] = None
    
    @classmethod
    def create(
        cls,
        stream_id: str,
        cursor_position: CursorPosition,
        subscription_id: Optional[str] = None,
        subscriber_id: Optional[str] = None,
    ) -> "CursorCheckpoint":
        """Create a new cursor checkpoint."""
        return cls(
            checkpoint_id=f"cursor-cp-{time.monotonic_ns()}-{uuid.uuid4().hex[:8]}",
            stream_id=stream_id,
            subscription_id=subscription_id,
            subscriber_id=subscriber_id,
            cursor_position=cursor_position,
            created_at_utc=time.time(),
        )
    
    def with_subscription(self, subscription_id: str) -> "CursorCheckpoint":
        """Return new checkpoint with subscription reference."""
        return dataclass_replace(
            self,
            subscription_id=subscription_id
        )
    
    def advance_cursor(self, position: CursorPosition) -> "CursorCheckpoint":
        """Create a new checkpoint at an advanced cursor position."""
        return dataclass_replace(
            self,
            cursor_position=position,
            created_at_utc=time.time(),
            version=self.version + 1
        )


# =============================================================================
# CHECKPOINT SET - Coordinated Set of Checkpoints
# =============================================================================


@dataclass(frozen=True)
class CheckpointSet:
    """
    A set of checkpoints created together.
    
    Used when multiple streams must be checkpointed with coordination.
    Members may be independent or have cross-stream consistency requirements.
    """
    
    # Identity
    set_id: str                         # Set identifier
    
    # Member checkpoints (stable references only)
    member_checkpoint_ids: Tuple[str, ...]  # Checkpoint IDs
    
    # Creation metadata
    created_at_utc: float               # When set was created
    consistency_policy: str = "independent"  # How members relate
    
    # Status
    status: str = "complete"            # complete, partial, failed
    
    # Optional cross-reference info
    correlation_id: Optional[str] = None
    causation_id: Optional[str] = None
    
    @classmethod
    def create_independent(
        cls,
        checkpoint_ids: Tuple[str, ...]
    ) -> "CheckpointSet":
        """Create a set with independent checkpoints."""
        return cls(
            set_id=f"set-{time.monotonic_ns()}-{uuid.uuid4().hex[:8]}",
            member_checkpoint_ids=checkpoint_ids,
            created_at_utc=time.time(),
            consistency_policy="independent"
        )
    
    def is_complete(self) -> bool:
        """Check if all member checkpoints are committed."""
        return self.status == "complete"


# =============================================================================
# CHECKPOINT PERSISTENCE - Persistence Interface
# =============================================================================


@runtime_checkable
class CheckpointPersistence(Protocol):
    """
    Protocol for checkpoint persistence backends.
    
    Persistence backends must support:
        - Saving checkpoint descriptors
        - Loading checkpoint descriptors by ID
        - Listing checkpoints for a stream
        - Deleting expired checkpoints
    
    NOTE: This is only the persistence interface. Checkpoint semantics
          (validation, integrity, etc.) are owned by this module.
    """
    
    async def initialize(self) -> None:
        """Initialize the persistence backend."""
        ...
    
    async def shutdown(self) -> None:
        """Shutdown the persistence backend cleanly."""
        ...
    
    async def save_checkpoint(
        self,
        checkpoint: CheckpointDescriptor,
        canonical_serialization: bytes,
    ) -> bool:
        """
        Save a checkpoint descriptor and its serialization.
        
        Args:
            checkpoint: The checkpoint descriptor
            canonical_serialization: The serialized form for integrity
        
        Returns:
            True if saved successfully
        """
        ...
    
    async def load_checkpoint(
        self,
        checkpoint_id: str,
    ) -> Optional[CheckpointDescriptor]:
        """
        Load a checkpoint by ID.
        
        Args:
            checkpoint_id: ID of checkpoint to load
        
        Returns:
            Checkpoint descriptor, or None if not found
        """
        ...
    
    async def delete_checkpoint(
        self,
        checkpoint_id: str,
    ) -> bool:
        """
        Delete a checkpoint.
        
        Args:
            checkpoint_id: ID of checkpoint to delete
        
        Returns:
            True if deleted, False if not found
        """
        ...
    
    async def list_checkpoints_for_stream(
        self,
        stream_id: str,
        limit: int = 100,
        before_utc: Optional[float] = None,
    ) -> Tuple[CheckpointDescriptor, ...]:
        """
        List checkpoints for a stream.
        
        Args:
            stream_id: Stream to query
            limit: Maximum number of checkpoints
            before_utc: Only include checkpoints created before this time
        
        Returns:
            Tuple of checkpoint descriptors (newest first)
        """
        ...
    
    async def cleanup_expired(
        self,
        current_time_utc: Optional[float] = None,
        retention_seconds: int = 86400,
    ) -> Dict[str, Any]:
        """
        Remove expired checkpoints.
        
        Args:
            current_time_utc: Current time for expiry calculations
            retention_seconds: How long to retain checkpoints
        
        Returns:
            Statistics about cleanup operations
        """
        ...


# =============================================================================
# CHECKPOINT INTEGRITY - Integrity Verification
# =============================================================================


def compute_checkpoint_integrity_digest(
    checkpoint: CheckpointDescriptor,
) -> Optional[str]:
    """
    Compute the integrity digest of a checkpoint descriptor.
    
    The digest is computed over the canonical serialization of:
        - checkpoint_id (stable)
        - schema_id
        - version (major.minor.patch)
        - scope
        - consistency_level
        - stream_id
        - runtime_instance_id
        - generation_id
        - last_included_sequence
        - lifecycle_state
        - ownership_version
        - configuration_generation
    
    Args:
        checkpoint: The checkpoint to hash
        
    Returns:
        Hex digest of the canonical serialization, or None if not computable
    """
    try:
        # Build canonical string representation
        parts = [
            checkpoint.checkpoint_id,
            checkpoint.schema_id,
            str(checkpoint.version),
            checkpoint.scope.value,
            checkpoint.consistency_level.value,
            checkpoint.stream_id,
            checkpoint.runtime_instance_id,
            checkpoint.generation_id,
            str(checkpoint.last_included_sequence),
            checkpoint.lifecycle_state,
            str(checkpoint.ownership_version),
            str(checkpoint.configuration_generation),
        ]
        
        # Hash the concatenated parts
        hash_obj = hashlib.sha256()
        for part in parts:
            hash_obj.update(part.encode("utf-8"))
        
        return hash_obj.hexdigest()
    except Exception:
        return None


# =============================================================================
# CHECKPOINT SERIALIZATION - Safe, Versioned Serialization
# =============================================================================


class SerializationError(Exception):
    """Checkpoint serialization error."""
    pass


def serialize_checkpoint(checkpoint: CheckpointDescriptor) -> bytes:
    """
    Serialize a checkpoint descriptor to canonical form.
    
    Uses JSON with deterministic key ordering for reproducibility.
    
    Args:
        checkpoint: The checkpoint to serialize
        
    Returns:
        Bytes of serialized data
    
    Raises:
        SerializationError: If serialization fails
    """
    import json
    
    try:
        # Convert dataclass to dict with canonical field order
        def convert_field(value):
            if hasattr(value, 'value'):
                return value.value  # Enum values
            elif isinstance(value, tuple):
                return [convert_field(item) for item in value]
            elif hasattr(value, '__dataclass_fields__'):
                # Recursively handle nested dataclasses
                result = {}
                for field_name in sorted(value.__dataclass_fields__.keys()):
                    v = getattr(value, field_name)
                    if v is not None:
                        result[field_name] = convert_field(v)
                return result
            else:
                return value
        
        data = {
            "checkpoint_id": checkpoint.checkpoint_id,
            "schema_id": checkpoint.schema_id,
            "version": str(checkpoint.version),
            "scope": checkpoint.scope.value,
            "consistency_level": checkpoint.consistency_level.value,
            "stream_id": checkpoint.stream_id,
            "runtime_instance_id": checkpoint.runtime_instance_id,
            "generation_id": checkpoint.generation_id,
            "last_included_sequence": checkpoint.last_included_sequence,
            "lifecycle_state": checkpoint.lifecycle_state,
            "ownership_version": checkpoint.ownership_version,
            "configuration_generation": checkpoint.configuration_generation,
        }
        
        # Add optional fields if present
        if checkpoint.cursor_checkpoint_references:
            data["cursor_checkpoint_references"] = list(checkpoint.cursor_checkpoint_references)
        if checkpoint.persistence_reference:
            data["persistence_reference"] = checkpoint.persistence_reference
        if checkpoint.integrity_digest:
            data["integrity_digest"] = checkpoint.integrity_digest
        
        # Serialize with deterministic ordering
        return json.dumps(data, sort_keys=True, separators=(',', ':')).encode("utf-8")
    
    except Exception as e:
        raise SerializationError(f"Failed to serialize checkpoint: {e}")


def deserialize_checkpoint(data: bytes) -> CheckpointDescriptor:
    """
    Deserialize checkpoint data back into a descriptor.
    
    Args:
        data: Serialized checkpoint data
        
    Returns:
        Checkpoint descriptor
    
    Raises:
        SerializationError: If deserialization fails
        ValueError: If version is unsupported
    """
    import json
    
    try:
        raw = json.loads(data.decode("utf-8"))
        
        # Validate schema and version
        schema_id = raw.get("schema_id", "")
        if not schema_id.startswith("gordon.checkpoint.v"):
            raise ValueError(f"Unsupported checkpoint schema: {schema_id}")
        
        version_str = raw.get("version", "1.0.0")
        try:
            major = int(version_str.split(".")[0])
            if major != 1:
                raise ValueError(f"Unsupported checkpoint version: {major}")
        except (ValueError, IndexError):
            pass
        
        # Parse fields
        return CheckpointDescriptor(
            checkpoint_id=raw["checkpoint_id"],
            schema_id=schema_id,
            version=CheckpointVersion.from_string(version_str),
            scope=CheckpointScope(raw.get("scope", "stream_position_only")),
            consistency_level=CheckpointConsistency(raw.get("consistency_level", "position_consistent")),
            stream_id=raw["stream_id"],
            runtime_instance_id=raw["runtime_instance_id"],
            generation_id=raw["generation_id"],
            last_included_sequence=int(raw["last_included_sequence"]),
            lifecycle_state=raw.get("lifecycle_state", "active"),
            ownership_version=int(raw.get("ownership_version", 1)),
            configuration_generation=int(raw.get("configuration_generation", 1)),
            cursor_checkpoint_references=tuple(raw.get("cursor_checkpoint_references", [])),
            persistence_reference=raw.get("persistence_reference"),
            integrity_digest=raw.get("integrity_digest"),
            created_at_utc=time.time(),  # Can't restore from serialized form
        )
    
    except json.JSONDecodeError as e:
        raise SerializationError(f"Invalid JSON: {e}")
    except KeyError as e:
        raise SerializationError(f"Missing required field: {e}")


# =============================================================================
# EXPORTS
# =============================================================================

__all__ = [
    # Identity types
    "CheckpointIdType",
    "CheckpointId",
    "CheckpointSetId",
    "CheckpointVersion",
    
    # Scope and consistency
    "CheckpointScope",
    "CheckpointConsistency",
    
    # Status and modes
    "CheckpointStatus",
    "CheckpointCreationMode",
    
    # Request and descriptor
    "CheckpointRequest",
    "CheckpointDescriptor",
    "dataclass_replace",
    
    # Validation
    "CheckpointValidationResult",
    
    # Cursor checkpoints
    "CursorCheckpoint",
    
    # Checkpoint sets
    "CheckpointSet",
    
    # Persistence protocol
    "CheckpointPersistence",
    
    # Integrity and serialization
    "compute_checkpoint_integrity_digest",
    "serialize_checkpoint",
    "deserialize_checkpoint",
    "SerializationError",
]