# Memory Streams - Phase 3.11.11 Canonical Semantic Stream Architecture
# ====================================================================

"""
Memory Semantic Streams: Canonical semantic transport for committed memory operations.

Architecture:
    Perception Streams → Consciousness Streams → Cognition Streams → 
    Memory System (owns memory) → Memory Streams (canonical transport) → Networks (consumers)

Ownership Model:
    | Entity           | Owns                                    | Does NOT Own              |
    |------------------|-----------------------------------------|---------------------------|
    | Memory System    | Persistent representation, state        | Stream transport          |
    | Memory Streams   | Publication, ordering, replay, checkpoints | Runtime memory state    |

Stream Types Implemented:
    - Encoding Stream      : Memory encoding operations
    - Storage Stream       : Memory storage operations  
    - Retrieval Stream     : Memory retrieval operations
    - Recall Stream        : Memory recall operations
    - Working Memory Stream: Working memory operations
    - Episodic Stream      : Episodic memory operations
    - Semantic Stream      : Semantic memory operations
    - Procedural Stream    : Procedural memory operations
    - Associative Stream   : Associative structure operations
    - Consolidation Stream : Consolidation operations
    - Forgetting Stream    : Forgetting/expiration operations
    - Index Stream         : Index updates
    - Relationship Stream  : Memory relationship changes

Never answers (these are owned by other systems):
    - What perception observed (Perception owns)
    - What cognition concluded (Cognition owns)
    - What consciousness experienced (Consciousness owns)
    - What action should execute (Action owns)
"""

from dataclasses import dataclass, field
from typing import (
    Dict,
    List,
    Optional,
    Any,
    Tuple,
    Protocol,
    runtime_checkable,
)
from enum import Enum, auto
import time
import uuid


# =============================================================================
# MEMORY OPERATION KINDS
# =============================================================================

class MemoryOperationKind(Enum):
    """
    Types of memory operations that can be recorded.
    
    Each kind represents a specific semantic operation on memory artifacts:
        ENCODE:       Create new memory representation
        STORE:        Persist memory to storage
        RETRIEVE:     Fetch memory from storage (request)
        RECALL:       Bring memory into conscious awareness
        UPDATE:       Modify existing memory
        CONSOLIDATE:  Stabilize and integrate memories
        MERGE:        Combine multiple memory representations
        SPLIT:        Separate combined representation
        LINK:         Create association between memories
        UNLINK:       Remove association between memories
        EXPIRE:       Mark memory as expired (still in storage)
        FORGET:       Actively remove memory from active state
        ARCHIVE:      Move memory to archive storage
        RESTORE:      Restore archived memory to active storage
        INVALIDATE:   Mark memory as no longer valid/accurate
    """
    ENCODE = "encode"
    STORE = "store"
    RETRIEVE = "retrieve"
    RECALL = "recall"
    UPDATE = "update"
    CONSOLIDATE = "consolidate"
    MERGE = "merge"
    SPLIT = "split"
    LINK = "link"
    UNLINK = "unlink"
    EXPIRE = "expire"
    FORGET = "forget"
    ARCHIVE = "archive"
    RESTORE = "restore"
    INVALIDATE = "invalidate"


class MemoryType(Enum):
    """
    Types of memory that can be operated on.
    
    | Type            | Description                                    |
    |-----------------|------------------------------------------------|
    | SEMANTIC        | Factual knowledge, concepts, meanings          |
    | EPISODIC        | Personal experiences with context              |
    | AUTOBIOGRAPHICAL| Life history and self-narrative               |
    | PROCEDURAL      | Skills, habits, "how-to" knowledge             |
    | WORKING         | Short-term active memory buffer                |
    | SENSORY         | Brief sensory impressions (iconic/echoic)     |
    | IMPLICIT        | Unconscious memory (priming, conditioning)    |
    | EXPLICIT        | Conscious recollection                         |
    """
    SEMANTIC = "semantic"
    EPISODIC = "episodic"
    AUTOBIOGRAPHICAL = "autobiographical"
    PROCEDURAL = "procedural"
    WORKING = "working"
    SENSORY = "sensory"
    IMPLICIT = "implicit"
    EXPLICIT = "explicit"


# =============================================================================
# MEMORY RECORD TYPES
# =============================================================================

@dataclass(frozen=True)
class MemoryRecordId:
    """Unique identifier for a memory record within its stream."""
    value: str
    
    @classmethod
    def generate(cls) -> "MemoryRecordId":
        return cls(value=f"mem:{uuid.uuid4().hex[:16]}")
    
    def __str__(self) -> str:
        return self.value


@dataclass(frozen=True)
class MemoryArtifactReference:
    """
    Reference to a memory artifact.
    
    An artifact reference provides traceability without implying ownership
    transfer. It may point to content that is:
        - Currently available
        - Expired (but not deleted from canonical history)
        - Archived
        - Redacted per privacy policy
    """
    artifact_id: str  # UUID or other unique identifier
    memory_type: MemoryType
    version: int = 1
    
    # Optional location reference (path, URL, etc.)
    storage_location: Optional[str] = None
    
    # Content hash for integrity verification
    content_hash: Optional[str] = None
    
    def __str__(self) -> str:
        return f"{self.artifact_id}:{self.memory_type.value}:v{self.version}"


@dataclass(frozen=True)
class MemoryRecord:
    """
    Immutable record in a memory stream.
    
    Represents a committed memory operation with full provenance and context.
    
    Fields:
        record_id:           Unique identifier within the stream
        stream_id:           Which memory stream this belongs to
        memory_record_id:    Reference to the memory artifact being operated on
        
        # Operation metadata
        operation_kind:      What operation was performed (encode, store, etc.)
        timestamp:           When operation occurred
        owner:               Who performed the operation
        
        # Memory artifact details
        memory_type:         Type of memory (semantic, episodic, etc.)
        source_reference:    Where this came from (external input, perception, etc.)
        
        # Traceability
        correlation_id:      Group related records
        causation_id:        Direct cause reference
        
        # Provenance & trust
        provenance:          Source chain and processing history
        confidence:          0.0-1.0 confidence in record accuracy
        trust:               0.0-1.0 trust in source
        
        # Lifecycle
        privacy:             Privacy class (public, private, confidential)
        expiration:          When this memory expires (optional)
        
        # Specialized fields per operation type
        retrieval_score:     For retrieval operations - ranking score
        consolidation_generation: For consolidation - which generation this belongs to
        metadata:            Additional structured data
    """
    
    record_id: MemoryRecordId
    
    # Stream position
    stream_id: str  # Full stream identifier (namespace:kind:name)
    sequence_number: int
    generation_id: str  # Generation identifier
    
    # Operation kind and memory type
    operation_kind: MemoryOperationKind
    memory_type: MemoryType
    
    # Artifact reference being operated on
    memory_record_id: Optional[str] = None
    artifact_reference: Optional[MemoryArtifactReference] = None
    
    # Timestamps - event_time comes first, then created_at (both have defaults now)
    event_time_utc: float = field(default_factory=time.time)  # When the event occurred
    created_at_utc: float = field(default_factory=time.time)  # When record was created
    
    # Owner information
    owner: Optional[str] = None  # Who performed the operation
    
    # Source and context
    source_reference: Optional[str] = None  # External source reference
    
    # Traceability
    correlation_id: Optional[str] = None
    causation_id: Optional[str] = None
    parent_record_id: Optional[str] = None  # Predecessor in sequence
    
    # Provenance & trust metrics
    provenance: Dict[str, Any] = field(default_factory=dict)
    confidence: float = 1.0
    trust: float = 1.0
    
    # Lifecycle attributes
    privacy_class: str = "private"  # public, private, confidential, restricted
    expiration: Optional[float] = None  # Unix timestamp or None for no expiry
    
    # Operation-specific fields
    retrieval_score: Optional[float] = None  # For retrieval operations
    consolidation_generation: int = 0  # For consolidation operations
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    # Status
    status: str = "committed"  # proposed, validated, committed, expired, redacted
    
    def is_expired(self) -> bool:
        """Check if this record has expired."""
        return self.expiration is not None and time.time() > self.expiration


# =============================================================================
# STREAM IDENTIFIERS (PREDEFINED)
# =============================================================================

MEMORY_STREAM_NAMESPACE = "memory"

# Encoding Stream - Records memory encoding operations
STREAM_MEMORY_ENCODING = f"{MEMORY_STREAM_NAMESPACE}:encoding:operations"
MEMORY_ENCODING_STREAM_ID = STREAM_MEMORY_ENCODING

# Storage Stream - Records storage operations
STREAM_MEMORY_STORAGE = f"{MEMORY_STREAM_NAMESPACE}:storage:operations"
MEMORY_STORAGE_STREAM_ID = STREAM_MEMORY_STORAGE

# Retrieval Stream - Records retrieval requests and results
STREAM_MEMORY_RETRIEVAL = f"{MEMORY_STREAM_NAMESPACE}:retrieval:operations"
MEMORY_RETRIEVAL_STREAM_ID = STREAM_MEMORY_RETRIEVAL

# Recall Stream - Records conscious recall operations
STREAM_MEMORY_RECALL = f"{MEMORY_STREAM_NAMESPACE}:recall:operations"
MEMORY_RECALL_STREAM_ID = STREAM_MEMORY_RECALL

# Working Memory Stream - Records working memory operations
STREAM_WORKING_MEMORY = f"{MEMORY_STREAM_NAMESPACE}:working:operations"
WORKING_MEMORY_STREAM_ID = STREAM_WORKING_MEMORY

# Episodic Memory Stream - Records episodic memory operations
STREAM_EPISODIC_MEMORY = f"{MEMORY_STREAM_NAMESPACE}:episodic:operations"
EPISODIC_MEMORY_STREAM_ID = STREAM_EPISODIC_MEMORY

# Semantic Memory Stream - Records semantic memory operations
STREAM_SEMANTIC_MEMORY = f"{MEMORY_STREAM_NAMESPACE}:semantic:operations"
SEMANTIC_MEMORY_STREAM_ID = STREAM_SEMANTIC_MEMORY

# Procedural Memory Stream - Records procedural memory operations
STREAM_PROCEDURAL_MEMORY = f"{MEMORY_STREAM_NAMESPACE}:procedural:operations"
PROCEDURAL_MEMORY_STREAM_ID = STREAM_PROCEDURAL_MEMORY

# Associative Memory Stream - Records association changes
STREAM_ASSOCIATIVE_MEMORY = f"{MEMORY_STREAM_NAMESPACE}:associative:operations"
ASSOCIATIVE_MEMORY_STREAM_ID = STREAM_ASSOCIATIVE_MEMORY

# Consolidation Stream - Records consolidation operations
STREAM_CONSOLIDATION = f"{MEMORY_STREAM_NAMESPACE}:consolidation:operations"
CONSOLIDATION_STREAM_ID = STREAM_CONSOLIDATION

# Forgetting Stream - Records forgetting/expiration operations
STREAM_FORGETTING = f"{MEMORY_STREAM_NAMESPACE}:forgetting:operations"
FORGETTING_STREAM_ID = STREAM_FORGETTING

# Memory Index Stream - Records index updates
STREAM_MEMORY_INDEX = f"{MEMORY_STREAM_NAMESPACE}:index:updates"
MEMORY_INDEX_STREAM_ID = STREAM_MEMORY_INDEX

# Memory Relationship Stream - Records relationship changes
STREAM_MEMORY_RELATIONSHIP = f"{MEMORY_STREAM_NAMESPACE}:relationship:changes"
MEMORY_RELATIONSHIP_STREAM_ID = STREAM_MEMORY_RELATIONSHIP


# =============================================================================
# MEMORY OPERATION BUILDERS (Mutable construction before immutability)
# =============================================================================

@dataclass
class MemoryRecordBuilder:
    """
    Builder pattern for constructing memory records.
    
    Allows mutable construction before producing an immutable record via build().
    """
    
    # Required fields
    stream_id: str
    operation_kind: MemoryOperationKind
    event_time_utc: float = field(default_factory=time.time)
    memory_type: MemoryType = MemoryType.SEMANTIC
    
    # Optional fields with defaults
    correlation_id: Optional[str] = None
    causation_id: Optional[str] = None
    parent_record_id: Optional[str] = None
    owner: Optional[str] = None
    source_reference: Optional[str] = None
    memory_record_id: Optional[str] = None
    artifact_reference: Optional[MemoryArtifactReference] = None
    
    # Provenance & trust (0.0-1.0)
    confidence: float = 1.0
    trust: float = 1.0
    
    # Lifecycle attributes
    privacy_class: str = "private"
    expiration: Optional[float] = None
    
    # Operation-specific
    retrieval_score: Optional[float] = None
    consolidation_generation: int = 0
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def set_correlation_id(self, correlation_id: str) -> "MemoryRecordBuilder":
        self.correlation_id = correlation_id
        return self
    
    def set_causation_id(self, causation_id: str) -> "MemoryRecordBuilder":
        self.causation_id = causation_id
        return self
    
    def set_parent_record_id(self, parent_record_id: str) -> "MemoryRecordBuilder":
        self.parent_record_id = parent_record_id
        return self
    
    def set_owner(self, owner: str) -> "MemoryRecordBuilder":
        self.owner = owner
        return self
    
    def set_source_reference(self, source: str) -> "MemoryRecordBuilder":
        self.source_reference = source
        return self
    
    def set_memory_record_id(self, record_id: str) -> "MemoryRecordBuilder":
        self.memory_record_id = record_id
        return self
    
    def set_artifact_reference(self, ref: MemoryArtifactReference) -> "MemoryRecordBuilder":
        self.artifact_reference = ref
        return self
    
    def set_confidence(self, confidence: float) -> "MemoryRecordBuilder":
        """Set confidence (0.0-1.0)."""
        self.confidence = max(0.0, min(1.0, confidence))
        return self
    
    def set_trust(self, trust: float) -> "MemoryRecordBuilder":
        """Set trust level (0.0-1.0)."""
        self.trust = max(0.0, min(1.0, trust))
        return self
    
    def set_privacy_class(self, privacy_class: str) -> "MemoryRecordBuilder":
        self.privacy_class = privacy_class
        return self
    
    def set_expiration(self, expiration_timestamp: float) -> "MemoryRecordBuilder":
        """Set expiration timestamp."""
        self.expiration = expiration_timestamp
        return self
    
    def set_retrieval_score(self, score: float) -> "MemoryRecordBuilder":
        """Set retrieval score (for retrieval operations)."""
        self.retrieval_score = max(0.0, min(1.0, score))
        return self
    
    def add_metadata(self, key: str, value: Any) -> "MemoryRecordBuilder":
        self.metadata[key] = value
        return self
    
    def set_consolidation_generation(self, gen: int) -> "MemoryRecordBuilder":
        """Set consolidation generation (for consolidation operations)."""
        self.consolidation_generation = gen
        return self
    
    def build(self) -> MemoryRecord:
        """
        Build an immutable MemoryRecord from this builder.
        
        Validates required fields and returns frozen dataclass instance.
        """
        # Validate required fields
        if not self.stream_id:
            raise ValueError("stream_id is required")
        if not self.operation_kind:
            raise ValueError("operation_kind is required")
        
        return MemoryRecord(
            record_id=MemoryRecordId.generate(),
            stream_id=self.stream_id,
            sequence_number=0,  # Will be set by stream infrastructure
            generation_id="",   # Will be set by stream infrastructure
            operation_kind=self.operation_kind,
            memory_type=self.memory_type,
            memory_record_id=self.memory_record_id,
            artifact_reference=self.artifact_reference,
            event_time_utc=self.event_time_utc,
            created_at_utc=time.time(),
            owner=self.owner,
            source_reference=self.source_reference,
            correlation_id=self.correlation_id,
            causation_id=self.causation_id,
            parent_record_id=self.parent_record_id,
            provenance={},
            confidence=self.confidence,
            trust=self.trust,
            privacy_class=self.privacy_class,
            expiration=self.expiration,
            retrieval_score=self.retrieval_score,
            consolidation_generation=self.consolidation_generation,
            metadata=self.metadata,
        )


# =============================================================================
# UTILITY FUNCTIONS
# =============================================================================

def create_memory_record(
    stream_id: str,
    operation_kind: MemoryOperationKind,
    memory_type: MemoryType = MemoryType.SEMANTIC,
) -> MemoryRecordBuilder:
    """
    Create a new MemoryRecordBuilder with the specified parameters.
    
    Args:
        stream_id: The full stream identifier
        operation_kind: What memory operation is being performed
        memory_type: Type of memory being operated on
        
    Returns:
        A builder for constructing the record
    """
    return MemoryRecordBuilder(
        stream_id=stream_id,
        operation_kind=operation_kind,
        memory_type=memory_type,
    )


def format_record_id(stream_id: str, generation: int, sequence: int) -> str:
    """Format a canonical record ID from stream position."""
    return f"{stream_id}:{generation}:{sequence}"


# =============================================================================
# EXPORTS
# =============================================================================

__all__ = [
    # Enums
    "MemoryOperationKind",
    "MemoryType",
    
    # Record types
    "MemoryRecordId",
    "MemoryArtifactReference",
    "MemoryRecord",
    
    # Stream IDs
    "MEMORY_STREAM_NAMESPACE",
    "STREAM_MEMORY_ENCODING", "MEMORY_ENCODING_STREAM_ID",
    "STREAM_MEMORY_STORAGE", "MEMORY_STORAGE_STREAM_ID",
    "STREAM_MEMORY_RETRIEVAL", "MEMORY_RETRIEVAL_STREAM_ID",
    "STREAM_MEMORY_RECALL", "MEMORY_RECALL_STREAM_ID",
    "STREAM_WORKING_MEMORY", "WORKING_MEMORY_STREAM_ID",
    "STREAM_EPISODIC_MEMORY", "EPISODIC_MEMORY_STREAM_ID",
    "STREAM_SEMANTIC_MEMORY", "SEMANTIC_MEMORY_STREAM_ID",
    "STREAM_PROCEDURAL_MEMORY", "PROCEDURAL_MEMORY_STREAM_ID",
    "STREAM_ASSOCIATIVE_MEMORY", "ASSOCIATIVE_MEMORY_STREAM_ID",
    "STREAM_CONSOLIDATION", "CONSOLIDATION_STREAM_ID",
    "STREAM_FORGETTING", "FORGETTING_STREAM_ID",
    "STREAM_MEMORY_INDEX", "MEMORY_INDEX_STREAM_ID",
    "STREAM_MEMORY_RELATIONSHIP", "MEMORY_RELATIONSHIP_STREAM_ID",
    
    # Builders
    "MemoryRecordBuilder",
    "create_memory_record",
    
    # Utilities
    "format_record_id",
]