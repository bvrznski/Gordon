# Core Data Governance Models
# ===========================

"""
Immutable model definitions for information governance.

All models are frozen dataclasses or enums representing:
* Classification levels and evidence
* Ownership records
* Lifecycle states and transitions
* Metadata schemas and versions
* Provenance graphs and lineages
* Privacy policies and decisions
* Retention schedules and policies
* Archive records and evidence
* Disposal records and evidence
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any, Set, FrozenSet
from enum import Enum
import time


# =============================================================================
# Classification Model
# =============================================================================

class ClassificationLevel(Enum):
    """
    Information classification levels.
    
    Levels ordered from least to most restrictive:
    - PUBLIC: Openly accessible
    - INTERNAL: Internal use only
    - RESTRICTED: Limited distribution
    - CONFIDENTIAL: Sensitive internal information
    - SECRET: High sensitivity, restricted access
    - SYSTEM: System-critical, no external exposure
    """
    
    PUBLIC = "public"
    INTERNAL = "internal"
    RESTRICTED = "restricted"
    CONFIDENTIAL = "confidential"
    SECRET = "secret"
    SYSTEM = "system"
    
    @classmethod
    def from_value(cls, value: str) -> "ClassificationLevel":
        """Convert string to classification level."""
        for level in cls:
            if level.value == value:
                return level
        raise ValueError(f"Invalid classification level: {value}")
    
    @property
    def access_level(self) -> int:
        """Return numeric access level (higher = more restrictive)."""
        levels = {
            ClassificationLevel.PUBLIC: 1,
            ClassificationLevel.INTERNAL: 2,
            ClassificationLevel.RESTRICTED: 3,
            ClassificationLevel.CONFIDENTIAL: 4,
            ClassificationLevel.SECRET: 5,
            ClassificationLevel.SYSTEM: 6,
        }
        return levels[self]


@dataclass(frozen=True)
class ClassificationEvidence:
    """
    Evidence supporting a classification decision.
    
    Args:
        classifier_id: Entity that made the classification
        criteria: Classification rules applied
        factors: Supporting factors for the decision
        timestamp: When classification was assigned
        confidence: Confidence level (0.0-1.0)
    """
    
    classifier_id: str
    criteria: str
    factors: Dict[str, Any] = field(default_factory=dict)
    timestamp: float = field(default_factory=time.time)
    confidence: float = 1.0
    
    @property
    def is_expired(self) -> bool:
        """Check if evidence is expired (older than 24 hours)."""
        return time.time() - self.timestamp > 86400


@dataclass(frozen=True)
class ClassificationDecision:
    """
    A classification decision for information.
    
    Args:
        information_id: ID of the classified information
        level: Assigned classification level
        evidence: Supporting evidence
        assigned_by: Entity ID that made the assignment
        timestamp: When classification was assigned
    """
    
    information_id: str
    level: ClassificationLevel
    evidence: ClassificationEvidence
    assigned_by: str = "system"
    timestamp: float = field(default_factory=time.time)
    
    @property
    def is_valid(self) -> bool:
        """Check if the classification decision is still valid."""
        return not self.evidence.is_expired


# =============================================================================
# Ownership Model
# =============================================================================

class OwnerType(Enum):
    """
    Types of information owners.
    
    - KERNEL: The core runtime kernel
    - RUNTIME: Runtime state manager
    - SERVICE: A registered service
    - SUBSYSTEM: A subsystem component
    - COMPONENT: An agent component
    - MEMORY: Memory system
    - OPERATOR: Human operator
    - USER: End user
    - PLUGIN: A plugin module
    - PROVIDER: An external provider
    - TOOL: A tool or utility
    """
    
    KERNEL = "kernel"
    RUNTIME = "runtime"
    SERVICE = "service"
    SUBSYSTEM = "subsystem"
    COMPONENT = "component"
    MEMORY = "memory"
    OPERATOR = "operator"
    USER = "user"
    PLUGIN = "plugin"
    PROVIDER = "provider"
    TOOL = "tool"


@dataclass(frozen=True)
class OwnerIdentity:
    """
    Identity of an information owner.
    
    Args:
        type: Type of owner
        id: Unique identifier for the owner
        name: Human-readable name (optional)
    """
    
    type: OwnerType
    id: str
    name: Optional[str] = None
    
    def __str__(self) -> str:
        return f"{self.type.value}:{self.id}"


@dataclass(frozen=True)
class OwnershipRecord:
    """
    Record of information ownership.
    
    Args:
        information_id: ID of the owned information
        owner: Owner identity
        assigned_at: When ownership was assigned
        transfer_reason: Reason for ownership (optional)
        revocable: Whether ownership can be revoked
    """
    
    information_id: str
    owner: OwnerIdentity
    assigned_at: float = field(default_factory=time.time)
    transfer_reason: Optional[str] = None
    revocable: bool = True
    
    def is_owner(self, owner_id: str) -> bool:
        """Check if given ID matches current owner."""
        return self.owner.id == owner_id


# =============================================================================
# Lifecycle Model
# =============================================================================

class LifecycleState(Enum):
    """
    Information lifecycle states.
    
    States follow the canonical lifecycle:
    CREATED → REGISTERED → ACTIVE → SHARED → ARCHIVED → EXPIRED → DELETED
    
    Transitions are explicit and auditable.
    """
    
    # Information lifecycle (data governance)
    CREATED = "created"
    REGISTERED = "registered"
    ACTIVE = "active"
    SHARED = "shared"
    ARCHIVED = "archived"
    EXPIRED = "expired"
    DELETED = "deleted"
    
    # Runtime lifecycle (entity states - for records like services, components)
    INITIALIZING = "initializing"  # Entity is initializing
    READY = "ready"                # Entity is ready but not running
    STARTING = "starting"          # Entity is starting up
    RUNNING = "running"            # Entity is actively running
    STOPPING = "stopping"          # Entity is stopping down
    STOPPED = "stopped"            # Entity has stopped
    FAILED = "failed"              # Entity failed


@dataclass(frozen=True)
class LifecycleTransition:
    """
    A valid lifecycle state transition.
    
    Args:
        information_id: ID of the information
        from_state: Source state
        to_state: Target state
        conditions: Preconditions that must be met
        effects: Side effects of the transition
    """
    
    information_id: str
    from_state: LifecycleState
    to_state: LifecycleState
    conditions: List[str] = field(default_factory=list)
    effects: List[str] = field(default_factory=list)


# =============================================================================
# Runtime Lifecycle (Entity States)
# =============================================================================


@dataclass(frozen=True)
class LifecycleEvent:
    """
    Record of a lifecycle state transition.
    
    Args:
        information_id: ID of the information
        from_state: Previous lifecycle state
        to_state: New lifecycle state
        timestamp: When transition occurred
        performed_by: Entity that performed the transition
        reason: Reason for the transition (optional)
    """
    
    information_id: str
    from_state: LifecycleState
    to_state: LifecycleState
    timestamp: float = field(default_factory=time.time)
    performed_by: str = "system"
    reason: Optional[str] = None


class RuntimeLifecycleCoordinator:
    """
    Coordinator for runtime entity lifecycle transitions.
    
    PHASE 3.7.21 REMEDIATION:
    - Validates transitions but doesn't own record state
    - Each record maintains its own lifecycle_state field
    
    Valid transitions:
        CREATED → INITIALIZING, FAILED
        INITIALIZING → READY, FAILED
        READY → STARTING, STOPPED, FAILED
        STARTING → RUNNING, STOPPING, FAILED
        RUNNING → STOPPING, FAILED
        STOPPING → STOPPED, FAILED
        STOPPED → STARTING, FAILED
    """
    
    TRANSITIONS: Dict[str, List[str]] = {
        LifecycleState.CREATED.value: [LifecycleState.INITIALIZING.value, LifecycleState.FAILED.value],
        LifecycleState.INITIALIZING.value: [LifecycleState.READY.value, LifecycleState.FAILED.value],
        LifecycleState.READY.value: [LifecycleState.STARTING.value, LifecycleState.STOPPED.value, LifecycleState.FAILED.value],
        LifecycleState.STARTING.value: [LifecycleState.RUNNING.value, LifecycleState.STOPPING.value, LifecycleState.FAILED.value],
        LifecycleState.RUNNING.value: [LifecycleState.STOPPING.value, LifecycleState.FAILED.value],
        LifecycleState.STOPPING.value: [LifecycleState.STOPPED.value, LifecycleState.FAILED.value],
        LifecycleState.STOPPED.value: [LifecycleState.STARTING.value, LifecycleState.FAILED.value],
        LifecycleState.FAILED.value: [],
    }
    
    @staticmethod
    def can_transition(from_state: str, to_state: str) -> bool:
        """Check if a transition is valid."""
        allowed = RuntimeLifecycleCoordinator.TRANSITIONS.get(from_state, [])
        return to_state in allowed
    
    @staticmethod
    def validate_transition(from_state: str, to_state: str) -> None:
        """Validate and raise if invalid."""
        if not RuntimeLifecycleCoordinator.can_transition(from_state, to_state):
            raise ValueError(f"Invalid transition from {from_state} to {to_state}")


# =============================================================================
# Metadata Model
# =============================================================================

@dataclass(frozen=True)
class MetadataSchema:
    """
    Schema definition for metadata validation.
    
    Args:
        schema_id: Unique schema identifier
        version: Schema version
        fields: Dictionary of field definitions
        required_fields: List of required field names
        validators: Optional validation functions
    """
    
    schema_id: str
    version: int = 1
    fields: Dict[str, type] = field(default_factory=dict)
    required_fields: List[str] = field(default_factory=list)
    validators: List[Any] = field(default_factory=list)
    
    def is_valid(self, metadata: Dict[str, Any]) -> bool:
        """Check if metadata conforms to schema."""
        for field_name in self.required_fields:
            if field_name not in metadata:
                return False
        
        for field_name, expected_type in self.fields.items():
            if field_name in metadata:
                value = metadata[field_name]
                if not isinstance(value, expected_type):
                    return False
        
        return True


@dataclass(frozen=True)
class MetadataVersion:
    """
    Version of a metadata record.
    
    Args:
        version_number: Version number
        metadata: Metadata content at this version
        timestamp: When this version was created
        author: Entity that created this version
    """
    
    version_number: int
    metadata: Dict[str, Any]
    timestamp: float = field(default_factory=time.time)
    author: str = "system"
    
    @property
    def is_current(self) -> bool:
        """Check if this is the current (highest) version."""
        return True


@dataclass(frozen=True)
class MetadataSnapshot:
    """
    Snapshot of metadata at a point in time.
    
    Args:
        information_id: ID of the information
        version: Version number
        metadata: Metadata values
        timestamp: When snapshot was taken
        author: Entity that took the snapshot
    """
    
    information_id: str
    version: int
    metadata: Dict[str, Any]
    timestamp: float = field(default_factory=time.time)
    author: str = "system"


@dataclass(frozen=True)
class MetadataRecord:
    """
    Complete metadata record for information.
    
    Args:
        information_id: ID of the information
        schema: Metadata schema used
        version: Current version number
        values: Current metadata values
        history: Version history
    """
    
    information_id: str
    schema: MetadataSchema
    version: int = 1
    values: Dict[str, Any] = field(default_factory=dict)
    history: List[MetadataVersion] = field(default_factory=list)
    
    def add_version(self, new_values: Dict[str, Any], author: str) -> "MetadataRecord":
        """Create a new version of the metadata."""
        new_history = self.history.copy()
        new_history.append(MetadataVersion(
            version_number=self.version + 1,
            metadata=dict(new_values),
            author=author
        ))
        
        return MetadataRecord(
            information_id=self.information_id,
            schema=self.schema,
            version=self.version + 1,
            values=dict(new_values),
            history=new_history
        )


# =============================================================================
# Provenance Model
# =============================================================================

@dataclass(frozen=True)
class ProvenanceNode:
    """
    Node in the provenance graph.
    
    Args:
        entity_id: Unique identifier for the entity
        entity_type: Type of entity (information, artifact, etc.)
        timestamp: When this node was created
        owner: Owner identity
    """
    
    entity_id: str
    entity_type: str
    timestamp: float = field(default_factory=time.time)
    owner: Optional[str] = None


@dataclass(frozen=True)
class ProvenanceEdge:
    """
    Edge in the provenance graph (transformation relationship).
    
    Args:
        source_id: Source node ID
        target_id: Target node ID
        transformation: Type of transformation applied
        timestamp: When transformation occurred
    """
    
    source_id: str
    target_id: str
    transformation: str
    timestamp: float = field(default_factory=time.time)


@dataclass(frozen=True)
class ProvenanceRecord:
    """
    Complete provenance record for information.
    
    Args:
        information_id: ID of the information
        nodes: Provenance graph nodes
        edges: Provenance graph edges
        root_entity: Original source entity ID
        timestamp: When provenance was recorded
    """
    
    information_id: str
    nodes: List[ProvenanceNode]
    edges: List[ProvenanceEdge]
    root_entity: Optional[str] = None
    timestamp: float = field(default_factory=time.time)


@dataclass(frozen=True)
class LineageReport:
    """
    Report on information lineage.
    
    Args:
        information_id: ID of the information
        ancestors: List of ancestor information IDs (in order from most recent)
        descendants: List of descendant information IDs
        transformations: List of transformations applied
        total_depth: Total depth in provenance graph
    """
    
    information_id: str
    ancestors: List[str]
    descendants: List[str]
    transformations: List[str]
    total_depth: int = 0


@dataclass(frozen=True)
class ProvenanceSnapshot:
    """
    Immutable snapshot of provenance state.
    
    Args:
        timestamp: When snapshot was taken
        nodes: All provenance nodes at this point
        edges: All provenance edges at this point
        graph_version: Version number of the graph
    """
    
    timestamp: float = field(default_factory=time.time)
    nodes: List[ProvenanceNode] = field(default_factory=list)
    edges: List[ProvenanceEdge] = field(default_factory=list)
    graph_version: int = 1


# =============================================================================
# Privacy Model
# =============================================================================

class PrivacyLevel(Enum):
    """
    Privacy protection levels.
    
    - OPEN: No privacy restrictions
    - CONFIDENTIAL: Requires explicit access approval
    - RESTRICTED: Limited access with audit trail
    - PRIVATE: High privacy, requires consent
    - PERSONAL_DATA: Subject to data protection regulations
    """
    
    OPEN = "open"
    CONFIDENTIAL = "confidential"
    RESTRICTED = "restricted"
    PRIVATE = "private"
    PERSONAL_DATA = "personal_data"


@dataclass(frozen=True)
class PersonalDataIndicator:
    """
    Indicator of personal data content.
    
    Args:
        detected: Whether personal data was detected
        types: Types of personal data detected (names, emails, IDs, etc.)
        confidence: Detection confidence level
        timestamp: When detection occurred
    """
    
    detected: bool
    types: List[str] = field(default_factory=list)
    confidence: float = 0.0
    timestamp: float = field(default_factory=time.time)


@dataclass(frozen=True)
class PrivacyPolicy:
    """
    Privacy policy configuration.
    
    Args:
        policy_id: Unique policy identifier
        version: Policy version number
        applicable_levels: Classification levels this applies to
        requirements: Required privacy controls
        audit_required: Whether all access must be audited
    """
    
    policy_id: str
    version: int = 1
    applicable_levels: List[ClassificationLevel] = field(default_factory=list)
    requirements: List[str] = field(default_factory=list)
    audit_required: bool = False
    
    def __hash__(self) -> int:
        return hash(self.policy_id)


@dataclass(frozen=True)
class PrivacyDecision:
    """
    A privacy policy decision.
    
    Args:
        information_id: ID of the information
        policy: Applied privacy policy
        decision: Approved or rejected
        timestamp: When decision was made
        reviewer: Entity that made the review
        conditions: Conditions of approval (if approved)
    """
    
    information_id: str
    policy: PrivacyPolicy
    decision: bool  # True = approved, False = rejected
    timestamp: float = field(default_factory=time.time)
    reviewer: str = "system"
    conditions: List[str] = field(default_factory=list)


# =============================================================================
# Retention Model
# =============================================================================

@dataclass(frozen=True)
class RetentionPolicy:
    """
    Retention policy configuration.
    
    Args:
        policy_id: Unique policy identifier
        retention_days: Number of days to retain
        review_interval_days: Interval for review cycles
        extendable: Whether retention can be extended
        auto_archive_after_days: Days before auto-archival (optional)
        minimum_retention_days: Minimum retention period (optional)
    """
    
    policy_id: str
    retention_days: int = 365
    review_interval_days: int = 90
    extendable: bool = True
    auto_archive_after_days: Optional[int] = None
    minimum_retention_days: Optional[int] = None
    
    def __hash__(self) -> int:
        return hash(self.policy_id)
    
    @property
    def review_cycle_length(self) -> float:
        """Return review cycle length in seconds."""
        return self.review_interval_days * 86400


@dataclass(frozen=True)
class RetentionSchedule:
    """
    Schedule for a specific information's retention.
    
    Args:
        information_id: ID of the information
        policy: Applied retention policy
        created_at: When information was created
        expires_at: When information will expire
        next_review_at: When next review is scheduled
        extensions: List of extension records
    """
    
    information_id: str
    policy: RetentionPolicy
    created_at: float = field(default_factory=time.time)
    expires_at: Optional[float] = None
    next_review_at: Optional[float] = None
    extensions: List["RetentionExtension"] = field(default_factory=list)
    
    def __post_init__(self) -> None:
        if self.expires_at is None:
            object.__setattr__(self, 'expires_at', 
                             self.created_at + (self.policy.retention_days * 86400))
        
        if self.next_review_at is None:
            object.__setattr__(self, 'next_review_at',
                             self.created_at + self.policy.review_cycle_length)


@dataclass(frozen=True)
class ExpirationStatus(Enum):
    """
    Status of information expiration.
    
    - ACTIVE: Information is within retention period
    - EXPIRING_SOON: Information will expire soon (within 7 days)
    - EXPIRED: Information has expired
    - EXTENDED: Retention has been extended
    - PERMANENT: No expiration (permanent retention)
    """
    
    ACTIVE = "active"
    EXPIRING_SOON = "expiring_soon"
    EXPIRED = "expired"
    EXTENDED = "extended"
    PERMANENT = "permanent"


@dataclass(frozen=True)
class RetentionExtension:
    """
    Record of a retention extension.
    
    Args:
        original_expires_at: Original expiration time
        extended_expires_at: New expiration time
        requested_by: Entity that requested the extension
        approved_by: Entity that approved the extension
        reason: Reason for extension
        timestamp: When extension was granted
    """
    
    original_expires_at: float
    extended_expires_at: float
    requested_by: str = "system"
    approved_by: str = "system"
    reason: str = ""
    timestamp: float = field(default_factory=time.time)


# =============================================================================
# Archive Model
# =============================================================================

@dataclass(frozen=True)
class ArchiveRequest:
    """
    Request to archive information.
    
    Args:
        information_id: ID of the information to archive
        reason: Reason for archival
        priority: Priority level (high, medium, low)
        include_provenance: Whether to preserve provenance in archive
        timestamp: When request was made
    """
    
    information_id: str
    reason: str
    priority: int = 1
    include_provenance: bool = True
    timestamp: float = field(default_factory=time.time)
    
    @property
    def is_high_priority(self) -> bool:
        """Check if this is high priority."""
        return self.priority <= 1


@dataclass(frozen=True)
class ArchiveDecision(Enum):
    """
    Decision on archive request.
    
    - APPROVED: Request approved
    - REJECTED: Request rejected
    - DEFERRED: Defer decision (need more information)
    """
    
    APPROVED = "approved"
    REJECTED = "rejected"
    DEFERRED = "deferred"


@dataclass(frozen=True)
class ArchiveRecord:
    """
    Record of archived information.
    
    Args:
        archive_id: Unique archive identifier
        information_id: Original information ID
        archive_time: When information was archived
        archive_location: Storage location path
        provenance_preserved: Whether provenance is preserved
        checksum: Integrity checksum of archived data
    """
    
    archive_id: str
    information_id: str
    archive_time: float = field(default_factory=time.time)
    archive_location: str = "/archive/default"
    provenance_preserved: bool = True
    checksum: Optional[str] = None
    
    def is_valid(self) -> bool:
        """Check if the archive record is valid."""
        return bool(self.checksum or self.archive_id)


@dataclass(frozen=True)
class ArchiveEvidence:
    """
    Evidence supporting an archival operation.
    
    Args:
        information_id: ID of the archived information
        archive_record: Archive record created
        decision: Archive decision made
        timestamp: When evidence was recorded
        operator: Entity that performed the operation
    """
    
    information_id: str
    archive_record: ArchiveRecord
    decision: ArchiveDecision
    timestamp: float = field(default_factory=time.time)
    operator: str = "system"


# =============================================================================
# Disposal Model
# =============================================================================

@dataclass(frozen=True)
class DisposalRequest:
    """
    Request to dispose (delete) information.
    
    Args:
        information_id: ID of the information to dispose
        reason: Reason for disposal
        method: Deletion method (soft, hard, secure)
        timestamp: When request was made
    """
    
    information_id: str
    reason: str
    method: "DisposalMethod" = field(default_factory=lambda: DisposalMethod.SOFT)
    timestamp: float = field(default_factory=time.time)


class DisposalMethod(Enum):
    """
    Methods of disposal/deletion.
    
    - SOFT: Mark as deleted (recoverable)
    - HARD: Overwrite data markers
    - SECURE: Cryptographic erasure or physical destruction
    """
    
    SOFT = "soft"
    HARD = "hard"
    SECURE = "secure"


@dataclass(frozen=True)
class DisposalRecord:
    """
    Record of information disposal.
    
    Args:
        disposal_id: Unique disposal identifier
        information_id: ID of the disposed information
        disposal_time: When disposal occurred
        method: Method used
        verified: Whether destruction was verified
        evidence_location: Location of disposal evidence
    """
    
    disposal_id: str
    information_id: str
    disposal_time: float = field(default_factory=time.time)
    method: DisposalMethod = field(default_factory=lambda: DisposalMethod.SOFT)
    verified: bool = False
    evidence_location: Optional[str] = None
    
    @property
    def is_complete(self) -> bool:
        """Check if disposal is complete (verified)."""
        return self.verified


@dataclass(frozen=True)
class DisposalEvidence:
    """
    Evidence supporting a disposal operation.
    
    Args:
        information_id: ID of the disposed information
        disposal_record: Disposal record created
        timestamp: When evidence was recorded
        operator: Entity that performed the operation
        verification_result: Result of verification (if any)
    """
    
    information_id: str
    disposal_record: DisposalRecord
    timestamp: float = field(default_factory=time.time)
    operator: str = "system"
    verification_result: Optional[str] = None


# =============================================================================
# Information Record - Master model combining all aspects
# =============================================================================

@dataclass(frozen=True)
class InformationRecord:
    """
    Complete record of governed information.
    
    Args:
        information_id: Unique identifier for the information
        content_hash: Hash of the information content (integrity)
        owner: Owner identity
        classification: Classification level
        lifecycle_state: Current lifecycle state
        created_at: When information was created
        metadata: Metadata record
        provenance_id: ID of the associated provenance record
        retention_schedule: Applied retention schedule
        privacy_policy: Applied privacy policy (optional)
    """
    
    information_id: str
    content_hash: str
    owner: OwnerIdentity
    classification: ClassificationLevel
    lifecycle_state: LifecycleState
    created_at: float = field(default_factory=time.time)
    metadata: Optional[MetadataRecord] = None
    provenance_id: Optional[str] = None
    retention_schedule: Optional[RetentionSchedule] = None
    privacy_policy: Optional[PrivacyPolicy] = None
    
    @property
    def is_active(self) -> bool:
        """Check if information is in active lifecycle state."""
        return self.lifecycle_state == LifecycleState.ACTIVE
    
    @property
    def is_expired(self) -> bool:
        """Check if information has expired."""
        if self.retention_schedule is None:
            return False
        return time.time() > (self.created_at + 
                             (self.retention_schedule.policy.retention_days * 86400))
    
    @property
    def is_destroyed(self) -> bool:
        """Check if information has been destroyed."""
        return self.lifecycle_state == LifecycleState.DELETED


__all__ = [
    # Classification
    "ClassificationLevel",
    "ClassificationEvidence",
    "ClassificationDecision",
    
    # Ownership
    "OwnerType",
    "OwnerIdentity",
    "OwnershipRecord",
    
    # Lifecycle
    "LifecycleState",
    "LifecycleEvent",
    "LifecycleTransition",
    
    # Metadata
    "MetadataSchema",
    "MetadataVersion",
    "MetadataSnapshot",
    "MetadataRecord",
    
    # Provenance
    "ProvenanceRecord",
    "ProvenanceNode",
    "ProvenanceEdge",
    "LineageReport",
    "ProvenanceSnapshot",
    
    # Privacy
    "PrivacyLevel",
    "PersonalDataIndicator",
    "PrivacyPolicy",
    "PrivacyDecision",
    
    # Retention
    "RetentionPolicy",
    "RetentionSchedule",
    "ExpirationStatus",
    "RetentionExtension",
    
    # Archive
    "ArchiveRequest",
    "ArchiveDecision",
    "ArchiveRecord",
    "ArchiveEvidence",
    
    # Disposal
    "DisposalRequest",
    "DisposalMethod",
    "DisposalRecord",
    "DisposalEvidence",
    
    # Master model
    "InformationRecord",
]