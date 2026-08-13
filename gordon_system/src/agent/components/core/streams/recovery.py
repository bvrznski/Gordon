# Stream Recovery & Continuity Infrastructure - Phase 3.11.7
# ============================================================

"""
Canonical Fault-Tolerance Architecture for Gordon's Semantic Stream Subsystem.

This module implements the complete recovery and continuity architecture:

Architecture Overview:
    
    Failure Axis (Stream Failures):
        Publication Failure → Delivery Failure → Subscriber Failure → 
        Publisher Failure → Cursor Corruption → Checkpoint Corruption → 
        Replay Failure → Integrity Failure → Storage Failure → 
        Authorization Failure → Capacity Exhaustion → Timeout → Cancellation
    
    Recovery Axis:
        Detection → Planning → Checkpoint Restoration → Replay-assisted Recovery →
        Validation → Resumption
    
    Continuity Axis:
        Continuity Coordinator manages recovery orchestration without owning history

Key Principles:
    - Failures remain immutable (dataclass)
    - Recovery is deterministic (no randomness in planning)
    - Checkpoints are validated before restoration
    - Replay never recreates committed history
    - Ownership and lifecycle constraints are preserved
    - Degraded operation is bounded
    - Retries are bounded and observable

Failure Categories:
    PUBLICATION_FAILURE     - Failed to publish record to stream
    DELIVERY_FAILURE        - Failed to deliver record to subscriber
    SUBSCRIBER_FAILURE      - Subscriber encountered error
    PUBLISHER_FAILURE       - Publisher encountered error
    CURSOR_CORRUPTION       - Cursor state corrupted
    CHECKPOINT_CORRUPTION   - Checkpoint integrity failure
    REPLAY_FAILURE          - Replay operation failed
    INTEGRITY_FAILURE       - Record or artifact integrity check failed
    STORAGE_FAILURE         - Storage layer failure
    AUTHORIZATION_FAILURE   - Authorization rejected
    CAPACITY_EXHAUSTION     - Stream capacity exceeded
    TIMEOUT                 - Operation timed out
    CANCELLATION            - Operation was cancelled
    LIFECYCLE_CONFLICT      - Recovery conflicts with lifecycle state
    VERSION_MISMATCH        - Version incompatibility detected

Recovery Decisions:
    RESUME          - Resume from checkpoint without replay
    REPLAY          - Replay from checkpoint to restore cursor position
    RESTORE         - Restore from validated checkpoint
    RESTART         - Restart generation from scratch
    DEGRADE         - Enter degraded operation mode
    ABORT           - Terminate recovery attempt
    ESCALATE        - Escalate to higher authority for decision
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple, Any, Set
from enum import Enum, auto
import time
import uuid


# =============================================================================
# FAILURE CATEGORIES (Canonical)
# =============================================================================

class StreamFailureCategory(Enum):
    """
    Canonical failure categories for stream operations.
    
    Each category defines:
        - Severity baseline
        - Retry eligibility
        - Recovery approach
        - Audit logging requirement
    
    Categories form a hierarchy from transient to terminal.
    """
    
    # Publication failures (producer side)
    PUBLICATION_FAILURE = "publication_failure"
    """Failed to publish record to stream."""
    
    DELIVERY_FAILURE = "delivery_failure"
    """Failed to deliver record to subscriber."""
    
    SUBSCRIBER_FAILURE = "subscriber_failure"
    """Subscriber encountered error during processing."""
    
    PUBLISHER_FAILURE = "publisher_failure"
    """Publisher encountered error."""
    
    # Cursor and checkpoint failures
    CURSOR_CORRUPTION = "cursor_corruption"
    """Cursor state corrupted or invalid."""
    
    CHECKPOINT_CORRUPTION = "checkpoint_corruption"
    """Checkpoint integrity check failed."""
    
    REPLAY_FAILURE = "replay_failure"
    """Replay operation encountered error."""
    
    # Integrity failures
    INTEGRITY_FAILURE = "integrity_failure"
    """Record or artifact integrity check failed."""
    
    ARTIFACT_UNAVAILABLE = "artifact_unavailable"
    """Artifact reference cannot be resolved."""
    
    # Storage failures
    STORAGE_FAILURE = "storage_failure"
    """Storage layer failure."""
    
    CHECKPOINT_STORAGE_FAILURE = "checkpoint_storage_failure"
    """Checkpoint persistence operation failed."""
    
    REPLAY_STORAGE_FAILURE = "replay_storage_failure"
    """Replay storage access failed."""
    
    # Authorization failures
    AUTHORIZATION_FAILURE = "authorization_failure"
    """Authorization check rejected operation."""
    
    UNAUTHORIZED_RESTORE = "unauthorized_restore"
    """Attempt to restore unauthorized checkpoint."""
    
    # Capacity and resource failures
    CAPACITY_EXHAUSTION = "capacity_exhaustion"
    """Stream capacity exceeded."""
    
    BUDGET_EXHAUSTED = "budget_exhausted"
    """Retry budget exhausted."""
    
    TIMEOUT = "timeout"
    """Operation timed out."""
    
    CANCELLATION = "cancellation"
    """Operation was cancelled (graceful)."""
    
    # Lifecycle failures
    LIFECYCLE_CONFLICT = "lifecycle_conflict"
    """Recovery conflicts with current lifecycle state."""
    
    VERSION_MISMATCH = "version_mismatch"
    """Version incompatibility detected."""
    
    # Infrastructure failures
    INFRASTRUCTURE_FAILURE = "infrastructure_failure"
    """Infrastructure layer failure (network, disk, etc)."""
    
    UNKNOWN = "unknown"
    """Unknown or unclassified failure."""


# =============================================================================
# FAILURE SEVERITY (Impact Level)
# =============================================================================

class FailureSeverity(Enum):
    """
    Severity level for stream failures.
    
    Severity is independent from category. A TRANSIENT failure can be CRITICAL
    if it affects safety-critical systems.
    
    Levels:
        DEBUG: Detailed diagnostic info (no action needed)
        INFO: Informational event
        NOTICE: Notable event, may need attention
        WARNING: May need attention, recovery possible
        ERROR: System impact, recovery attempted
        CRITICAL: Major system impact, immediate escalation
        FATAL: Terminal condition
    """
    
    DEBUG = "debug"
    """Debug-level diagnostic info."""
    
    INFO = "info"
    """Informational event, no action needed."""
    
    NOTICE = "notice"
    """Notable event that may need attention."""
    
    WARNING = "warning"
    """Potential problem, recovery may be possible."""
    
    ERROR = "error"
    """System impact occurred, recovery attempted."""
    
    CRITICAL = "critical"
    """Major system impact requiring immediate escalation."""
    
    FATAL = "fatal"
    """Terminal condition, no recovery possible."""


# =============================================================================
# FAILURE DESCRIPTOR (Immutable Failure Artifact)
# =============================================================================

@dataclass(frozen=True)
class StreamFailureDescriptor:
    """
    Immutable descriptor for a stream failure.
    
    A failure descriptor preserves all context about a failure without
    implying mutability. It is the canonical artifact passed between
    recovery components.
    
    Design principles:
        - Immutable (frozen dataclass) for thread safety
        - Deterministic serialization for logging/diagnostics
        - Explicit unknown state when evidence insufficient
        - Stable identity via generated failure_id
    """
    
    # ------------------------------------------------------------------
    # Identification
    # ------------------------------------------------------------------
    
    failure_id: str  # Unique identifier
    
    stream_id: Optional[str] = None  # Which stream?
    generation_id: Optional[int] = None  # Which generation?
    
    # ------------------------------------------------------------------
    # Classification
    # ------------------------------------------------------------------
    
    category: StreamFailureCategory = StreamFailureCategory.UNKNOWN
    """The failure category."""
    
    severity: FailureSeverity = FailureSeverity.WARNING
    """Impact level of the failure."""
    
    kind: Optional[str] = None  # Transient/Recoverable/Fatal/etc.
    
    # ------------------------------------------------------------------
    # Context Information
    # ------------------------------------------------------------------
    
    timestamp_utc: float = field(default_factory=time.time)
    """When the failure occurred."""
    
    detected_at: float = field(default_factory=time.time)
    """When failure was detected (may differ from occurrence time)."""
    
    message: str = ""
    """Human-readable description."""
    
    # ------------------------------------------------------------------
    # Operation Context
    # ------------------------------------------------------------------
    
    operation_type: Optional[str] = None  # publish, deliver, replay, etc.
    operation_id: Optional[str] = None  # Which specific operation?
    
    record_sequence: Optional[int] = None  # Record position if applicable
    
    cursor_position: Optional[int] = None  # Cursor position at failure
    checkpoint_id: Optional[str] = None  # Checkpoint involved (if any)
    
    # ------------------------------------------------------------------
    # Causation Chain
    # ------------------------------------------------------------------
    
    correlation_id: Optional[str] = None  # User/request correlation
    causation_id: Optional[str] = None  # Root cause failure ID
    
    parent_failure_id: Optional[str] = None  # If this is a child failure
    
    # ------------------------------------------------------------------
    # Recovery Classification
    # ------------------------------------------------------------------
    
    retryable: bool = False
    """Can the operation be retried?"""
    
    recoverable: bool = True
    """Can recovery restore from this failure?"""
    
    terminal: bool = False
    """Is this a terminal failure requiring shutdown?"""
    
    escalate_required: bool = False
    """Requires human/operator escalation."""
    
    # ------------------------------------------------------------------
    # State at Time of Failure
    # ------------------------------------------------------------------
    
    affected_entity_ids: List[str] = field(default_factory=list)
    """Entities affected by this failure."""
    
    affected_capability_ids: List[str] = field(default_factory=list)
    """Capabilities affected by this failure."""
    
    integrity_impact: str = "unknown"  # none, degraded, corrupted
    security_impact: str = "none"      # none, suspected, confirmed
    
    # ------------------------------------------------------------------
    # Provenance and Metadata
    # ------------------------------------------------------------------
    
    source_component: Optional[str] = None
    """Component where failure originated."""
    
    detected_by: Optional[str] = None  # Detection mechanism/service
    
    provenance: Dict[str, str] = field(default_factory=dict)
    """Source tracking metadata."""
    
    metadata: Dict[str, Any] = field(default_factory=dict)
    """Additional context data."""
    
    # ------------------------------------------------------------------
    # Properties for Quick Inspection
    # ------------------------------------------------------------------
    
    @property
    def is_transient(self) -> bool:
        """Check if this failure may be transient (temporary)."""
        return self.kind in ("transient", "timeout") or self.retryable
    
    @property
    def needs_escalation(self) -> bool:
        """Check if this failure requires escalation."""
        return (
            self.severity in (FailureSeverity.CRITICAL, FailureSeverity.FATAL)
            or self.terminal
            or self.escalate_required
        )
    
    @property
    def is_integrity_impact(self) -> bool:
        """Check if integrity may be affected."""
        return self.integrity_impact != "none"
    
    # ------------------------------------------------------------------
    # Serialization
    # ------------------------------------------------------------------
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert to JSON-serializable dictionary.
        
        This is deterministic - same inputs always produce same output.
        """
        return {
            "failure_id": self.failure_id,
            "stream_id": self.stream_id,
            "generation_id": self.generation_id,
            "category": self.category.value if hasattr(self.category, 'value') else str(self.category),
            "severity": self.severity.value if hasattr(self.severity, 'value') else str(self.severity),
            "kind": self.kind,
            "timestamp_utc": self.timestamp_utc,
            "detected_at": self.detected_at,
            "message": self.message,
            "operation_type": self.operation_type,
            "operation_id": self.operation_id,
            "record_sequence": self.record_sequence,
            "cursor_position": self.cursor_position,
            "checkpoint_id": self.checkpoint_id,
            "correlation_id": self.correlation_id,
            "causation_id": self.causation_id,
            "parent_failure_id": self.parent_failure_id,
            "retryable": self.retryable,
            "recoverable": self.recoverable,
            "terminal": self.terminal,
            "escalate_required": self.escalate_required,
            "affected_entity_ids": list(self.affected_entity_ids),
            "affected_capability_ids": list(self.affected_capability_ids),
            "integrity_impact": self.integrity_impact,
            "security_impact": self.security_impact,
            "source_component": self.source_component,
            "detected_by": self.detected_by,
            "provenance": dict(self.provenance),
            "metadata": self._serialize_metadata(self.metadata),
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "StreamFailureDescriptor":
        """Create StreamFailureDescriptor from serialized dictionary."""
        # Parse enums with defaults
        category = cls._parse_enum(data.get("category"), StreamFailureCategory, StreamFailureCategory.UNKNOWN)
        severity = cls._parse_enum(data.get("severity"), FailureSeverity, FailureSeverity.WARNING)
        
        return cls(
            failure_id=data["failure_id"],
            stream_id=data.get("stream_id"),
            generation_id=data.get("generation_id"),
            category=category,
            severity=severity,
            kind=data.get("kind"),
            timestamp_utc=data.get("timestamp_utc", time.time()),
            detected_at=data.get("detected_at", time.time()),
            message=data.get("message", ""),
            operation_type=data.get("operation_type"),
            operation_id=data.get("operation_id"),
            record_sequence=data.get("record_sequence"),
            cursor_position=data.get("cursor_position"),
            checkpoint_id=data.get("checkpoint_id"),
            correlation_id=data.get("correlation_id"),
            causation_id=data.get("causation_id"),
            parent_failure_id=data.get("parent_failure_id"),
            retryable=data.get("retryable", False),
            recoverable=data.get("recoverable", True),
            terminal=data.get("terminal", False),
            escalate_required=data.get("escalate_required", False),
            affected_entity_ids=data.get("affected_entity_ids", []),
            affected_capability_ids=data.get("affected_capability_ids", []),
            integrity_impact=data.get("integrity_impact", "unknown"),
            security_impact=data.get("security_impact", "none"),
            source_component=data.get("source_component"),
            detected_by=data.get("detected_by"),
            provenance=data.get("provenance", {}),
            metadata=cls._deserialize_metadata(data.get("metadata", {})),
        )
    
    @staticmethod
    def _parse_enum(value: Any, enum_type: type, default: Any) -> Any:
        """Parse an enum value with a safe default."""
        if isinstance(value, enum_type):
            return value
        if isinstance(value, str):
            try:
                return enum_type(value)
            except ValueError:
                pass
        return default
    
    @staticmethod
    def _serialize_metadata(metadata: Dict[str, Any]) -> Dict[str, Any]:
        """Serialize metadata for storage/transmission."""
        result = {}
        for k, v in metadata.items():
            if isinstance(v, Enum):
                result[k] = v.value if hasattr(v, 'value') else str(v)
            elif isinstance(v, (list, dict)):
                result[k] = v  # Let JSON handle these
            else:
                result[k] = v
        return result
    
    @staticmethod
    def _deserialize_metadata(data: Dict[str, Any]) -> Dict[str, Any]:
        """Deserialize metadata from storage/transmission."""
        return dict(data)
    
    @classmethod
    def generate_id(cls) -> str:
        """Generate a unique failure ID."""
        ts = time.monotonic_ns()
        nonce = uuid.uuid4().hex[:8]
        return f"failure:{ts}:{nonce}"


# =============================================================================
# FAILURE TYPE ALIASES (For Backward Compatibility)
# =============================================================================

# Re-export StreamFailureDescriptor for convenience
StreamFailure = StreamFailureDescriptor