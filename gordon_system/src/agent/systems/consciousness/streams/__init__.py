# Consciousness Streams - Phase 3.11.9 Canonical Semantic Streaming Architecture
# ===============================================================================

"""
Consciousness Streams: Semantic transport layer for immutable conscious experience.

This module implements the canonical semantic stream architecture for all Consciousness
subsystems as specified in Phase 3.11.9.

Consciousness System owns:
    - conscious field construction
    - intentional context
    - temporal consciousness
    - presence
    - perspective
    - situated world
    - phenomenal integration

Consciousness Streams own:
    - publication
    - ordering
    - subscriptions
    - replay
    - checkpoints
    - delivery
    - observability

Architectural Position:
    Perception → Consciousness System → Conscious Experience → Consciousness Stream → Networks → Capabilities → Systems

Consciousness Streams transport immutable conscious experience records.

They never answer: What should be believed? What should be remembered?
             What action should be taken?

They always answer:
    - What entered conscious experience?
    - What remained present?
    - What disappeared?
    - When did this occur?
    - Which perspective was active?
    - Under which intentional context?
    - With what phenomenal binding?
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple, Any
from enum import Enum, auto
import time
import uuid

# Import core stream infrastructure (Phase 3.11.x)
from gordon_system.src.agent.components.core.streams import (
    StreamId,
    StreamKind,
    StreamRecordId,
    StreamGenerationId,
    StreamRecord,
    StreamCommit,
    StreamPosition,
    ProducerId,
    CorrelationId,
    ArtifactReference,
    ArtifactTypeId,
    RecordType,
    RecordStatus,
    StreamRecordBuilder,
    CommitAuthority,
)
from gordon_system.src.agent.components.core.streams import dataclass_replace

# =============================================================================
# CONSCIOUS RECORD KINDS - Categories of conscious experience records
# =============================================================================


class ConsciousRecordKind(Enum):
    """Categories of consciousness stream records."""
    # Field transitions
    FIELD_ENTERED = "field_entered"             # Something entered conscious field
    FIELD_EXITED = "field_exited"               # Something exited conscious field
    OBJECT_FOREGROUNDED = "object_foregrounded"  # Object became foreground
    OBJECT_BACKGROUNDED = "object_backgrounded"  # Object became background
    CONTEXT_SHIFTED = "context_shifted"         # Context reorganized
    FIELD_REORGANIZED = "field_reorganized"     # Field structure changed
    
    # Intentional context transitions
    INTENTIONAL_TARGET_CHANGED = "intentional_target_changed"
    INTENTIONAL_TRANSITION = "intentional_transition"
    CONTEXTUAL_SHIFT = "contextual_shift"
    RELATION_CHANGE = "relation_change"
    
    # Presence states
    PRESENCE_ESTABLISHED = "presence_established"   # New presence
    PRESENCE_REMOVED = "presence_removed"           # Presence ended
    PRESENCE_INTENSIFIED = "presence_intensified"   # Got more present
    PRESENCE_FADED = "presence_faded"               # Fading away
    
    # Temporal consciousness
    RETENTION_ACTIVATED = "retention_activated"     # Past content in retention
    PRIMAL_IMPRESSION = "primal_impression"         # Now-ness of current
    PROTENTION_ACTIVATED = "protention_activated"   # Anticipation active
    CONTINUITY_ESTABLISHED = "continuity_established"
    CONTINUITY_INTERRUPTED = "continuity_interrupted"
    CONTINUITY_RESTORED = "continuity_restored"
    
    # Perspective
    PERSPECTIVE_SHIFT = "perspective_shift"         # Change in point of view
    HORIZON_EXPANDED = "horizon_expanded"           # Broader context seen
    HORIZON_CONTRACTED = "horizon_contracted"       # Narrower focus
    
    # Phenomenal binding
    PERCEPTUAL_BINDING = "perceptual_binding"       # Sensory elements bound
    TEMPORAL_BINDING = "temporal_binding"           # Time-bound binding
    CONTEXTUAL_BINDING = "contextual_binding"       # Context integration
    SELF_REFERENCE_BINDING = "self_reference_binding"
    MULTIMODAL_BINDING = "multimodal_binding"
    WORKSPACE_ADMISSION = "workspace_admission"     # Admitted to conscious workspace
    INTEGRATION_COMPLETED = "integration_completed"


class TemporalConsciousnessMode(Enum):
    """Modes of temporal consciousness structure."""
    RETENTION_ONLY = "retention_only"           # Focused on past retention
    PRIMAL_IMPRESSION_ONLY = "primal_impression"  # Pure now-ness
    PROTENTION_ONLY = "protention_only"         # Focused on anticipation
    FULL_CONSCIOUSNESS = "full_consciousness"   # Retention + impression + protention


class PerspectiveType(Enum):
    """Types of conscious perspectives."""
    FIRST_PERSON = "first_person"     # Self-centered perspective
    THIRD_PERSON = "third_person"     # Observer perspective
    MULTI_PERSPECTIVAL = "multi_perspectival"  # Multiple perspectives held
    PERSPECTIVE_LESS = "perspective_less"      # Non-dual awareness


class PhenomenalBindingMode(Enum):
    """Modes of phenomenal binding."""
    PERCEPTUAL = "perceptual"           # Sensory element binding
    TEMPORAL = "temporal"               # Temporal integration
    CONTEXTUAL = "contextual"           # Context integration
    SELF_REFERENCE = "self_reference"   # Self-awareness binding
    MULTIMODAL = "multimodal"           # Multi-sensory binding


# =============================================================================
# CONSCIOUS RECORD METADATA
# =============================================================================

@dataclass(frozen=True)
class ConsciousRecordMetadata:
    """Metadata for a conscious record."""
    
    # Field context
    field_position: int  # Position in current conscious field (0 = foreground)
    
    # Intentional context
    intentional_object: Optional[str] = None
    intentional_relation: Optional[str] = None  # e.g., "about", "towards"
    
    # Presence tracking
    presence_level: float = 1.0  # 0.0 to 1.0
    
    # Temporal context
    temporal_position: str = "now"  # now, recent_past, soon_to_come
    retention_depth: int = 0        # How far back in retention (0 = immediate)
    
    # Perspective
    perspective: PerspectiveType = PerspectiveType.FIRST_PERSON
    
    # Phenomenal binding context
    binding_mode: Optional[PhenomenalBindingMode] = None
    bound_elements: Tuple[str, ...] = field(default_factory=tuple)
    
    # Salience and confidence
    salience: float = 1.0      # How salient this experience is
    confidence: float = 1.0    # Confidence in this record
    
    # Provenance
    source_reference: Optional[str] = None


@dataclass(frozen=True)
class ConsciousContinuity:
    """Records consciousness continuity state."""
    
    continuity_id: str
    established_at_utc: float
    interrupted_at_utc: Optional[float] = None
    restored_at_utc: Optional[float] = None
    interruption_reason: Optional[str] = None
    
    @property
    def is_continuing(self) -> bool:
        """Check if continuity is ongoing."""
        return self.interrupted_at_utc is None


# =============================================================================
# CONSCIOUS RECORD - Immutable Semantic Unit for Conscious Experience
# =============================================================================

@dataclass(frozen=True)
class ConsciousRecord:
    """
    Immutable conscious record representing an element of conscious experience.
    
    A conscious record contains:
        - Identity (record_id, stream position)
        - Experience (what entered consciousness)
        - Context (intentional object, presence, temporal position)
        - Perspective (point of view)
        - Binding (how it integrates with other elements)
        - Continuity reference
    
    Conscious records are immutable after creation - new records represent
    new conscious experiences.
    """
    
    # Identity
    record_id: StreamRecordId
    stream_id: StreamId
    consciousness_record_id: str  # Unique ID within consciousness streams
    
    # Record kind and type
    record_kind: ConsciousRecordKind
    subkind: Optional[str] = None  # More specific classification
    
    # Timestamps (distinct temporal semantics)
    event_time_utc: float      # When the experience occurred
    publication_time_utc: float = field(default_factory=time.time)  # When published
    
    # Position and ordering
    generation_id: StreamGenerationId
    sequence_number: int
    
    # Experience payload
    experience_payload: Dict[str, Any]  # The conscious content
    
    # Metadata
    metadata: ConsciousRecordMetadata
    
    # Continuity reference (links to continuity state)
    continuity_reference: Optional[str] = None
    
    # Semantic context
    correlation_id: Optional[CorrelationId] = None  # Groups related experiences
    causation_id: Optional[CorrelationId] = None    # What caused this record
    
    # Artifact reference (for large payloads)
    artifact_reference: Optional[ArtifactReference] = None
    
    @classmethod
    def create_builder(
        cls,
        stream_id: StreamId,
        generation_id: StreamGenerationId,
        record_kind: ConsciousRecordKind,
    ) -> "ConsciousRecordBuilder":
        """Create a new conscious record builder."""
        return ConsciousRecordBuilder(stream_id, generation_id, record_kind)
    
    @property
    def position(self) -> StreamPosition:
        """Get the stream position of this conscious record."""
        return StreamPosition(
            stream_id=self.stream_id,
            generation_id=self.generation_id,
            sequence_number=self.sequence_number
        )
    
    def with_correlation(self, correlation_id: CorrelationId) -> "ConsciousRecord":
        """Return a copy with correlation ID set."""
        return dataclass_replace(self, correlation_id=correlation_id)
    
    def to_stream_record(
        self,
        record_type: RecordType = RecordType.EVENT
    ) -> StreamRecord:
        """Convert to generic stream record for transport."""
        payload = {
            "consciousness_record_id": self.consciousness_record_id,
            "record_kind": self.record_kind.value,
            "subkind": self.subkind,
            "experience_payload": self.experience_payload,
            "metadata": {
                "field_position": self.metadata.field_position,
                "intentional_object": self.metadata.intentional_object,
                "intentional_relation": self.metadata.intentional_relation,
                "presence_level": self.metadata.presence_level,
                "temporal_position": self.metadata.temporal_position,
                "retention_depth": self.metadata.retention_depth,
                "perspective": self.metadata.perspective.value,
                "binding_mode": self.metadata.binding_mode.value if self.metadata.binding_mode else None,
                "bound_elements": list(self.metadata.bound_elements),
                "salience": self.metadata.salience,
                "confidence": self.metadata.confidence,
            },
        }
        
        return StreamRecord(
            record_id=self.record_id,
            status=RecordStatus.COMMITTED,
            sequence_number=self.sequence_number,
            generation_id=self.generation_id,
            stream_id=self.stream_id,
            event_time_utc=self.event_time_utc,
            created_at_utc=self.publication_time_utc,
            payload=payload,
            artifact_reference=self.artifact_reference,
        )


# =============================================================================
# CONSCIOUS RECORD BUILDER - Mutable Construction
# =============================================================================

class ConsciousRecordBuilder:
    """
    Mutable builder for constructing conscious records.
    
    Usage:
        builder = ConsciousRecordBuilder(stream_id, generation_id, record_kind)
        builder.set_experience_payload(data)
        builder.set_metadata(metadata)
        builder.set_correlation(correlation_id)
        consciousness_record = builder.build()
    """
    
    def __init__(self, stream_id: StreamId, generation_id: StreamGenerationId, record_kind: ConsciousRecordKind):
        self.stream_id = stream_id
        self.generation_id = generation_id
        self.record_kind = record_kind
        
        # Record-specific fields
        self.consciousness_record_id: Optional[str] = None
        self.subkind: Optional[str] = None
        self.event_time_utc: float = 0.0  # Will be set in build()
        
        # Experience payload
        self.experience_payload: Dict[str, Any] = {}
        
        # Metadata
        self.metadata: ConsciousRecordMetadata = ConsciousRecordMetadata(
            field_position=0,
            presence_level=1.0,
            salience=1.0,
            confidence=1.0,
        )
        
        # Continuity
        self.continuity_reference: Optional[str] = None
        
        # Correlation
        self.correlation_id: Optional[CorrelationId] = None
        self.causation_id: Optional[CorrelationId] = None
        
        # Internal state
        self._built: bool = False
    
    def set_consciousness_record_id(self, record_id: str) -> "ConsciousRecordBuilder":
        """Set the consciousness record ID."""
        if self._built:
            raise ValueError("Cannot modify built record")
        self.consciousness_record_id = record_id
        return self
    
    def set_subkind(self, subkind: str) -> "ConsciousRecordBuilder":
        """Set the subkind (more specific classification)."""
        if self._built:
            raise ValueError("Cannot modify built record")
        self.subkind = subkind
        return self
    
    def set_experience_payload(self, payload: Dict[str, Any]) -> "ConsciousRecordBuilder":
        """Set the conscious experience payload."""
        if self._built:
            raise ValueError("Cannot modify built record")
        self.experience_payload = dict(payload)
        return self
    
    def set_event_time(self, utc_time: float) -> "ConsciousRecordBuilder":
        """Set the event timestamp (when experience occurred)."""
        if self._built:
            raise ValueError("Cannot modify built record")
        self.event_time_utc = utc_time
        return self
    
    def set_metadata(self, metadata: ConsciousRecordMetadata) -> "ConsciousRecordBuilder":
        """Set the conscious record metadata."""
        if self._built:
            raise ValueError("Cannot modify built record")
        self.metadata = metadata
        return self
    
    def set_continuity_reference(self, continuity_ref: str) -> "ConsciousRecordBuilder":
        """Set the continuity reference for this record."""
        if self._built:
            raise ValueError("Cannot modify built record")
        self.continuity_reference = continuity_ref
        return self
    
    def set_correlation(self, correlation_id: CorrelationId) -> "ConsciousRecordBuilder":
        """Set correlation ID for grouping related experiences."""
        if self._built:
            raise ValueError("Cannot modify built record")
        self.correlation_id = correlation_id
        return self
    
    def build(self) -> ConsciousRecord:
        """
        Build the immutable conscious record.
        
        This consumes the builder - it cannot be reused after this call.
        """
        if self._built:
            raise ValueError("Cannot build again from built builder")
        
        # Generate IDs if not set
        consciousness_record_id = self.consciousness_record_id or f"conscious-{uuid.uuid4().hex[:16]}"
        
        record = ConsciousRecord(
            record_id=StreamRecordId(self.generation_id, 0),  # Will be assigned at commit
            stream_id=self.stream_id,
            consciousness_record_id=consciousness_record_id,
            record_kind=self.record_kind,
            subkind=self.subkind,
            event_time_utc=self.event_time_utc or time.time(),
            publication_time_utc=time.time(),
            generation_id=self.generation_id,
            sequence_number=0,  # Will be assigned at commit
            experience_payload=dict(self.experience_payload),
            metadata=self.metadata,
            continuity_reference=self.continuity_reference,
            correlation_id=self.correlation_id,
            causation_id=self.causation_id,
        )
        
        self._built = True
        return record


# =============================================================================
# STREAM IDENTIFIERS - Consciousness Stream ID Utilities
# =============================================================================

def make_conscious_field_stream_id() -> StreamId:
    """Create consciousness field stream identifier."""
    return StreamId.from_parts("consciousness", "experiential-field")


def make_intentional_context_stream_id() -> StreamId:
    """Create intentional context stream identifier."""
    return StreamId.from_parts("consciousness", "intentional-context")


def make_presence_stream_id() -> StreamId:
    """Create presence stream identifier."""
    return StreamId.from_parts("consciousness", "presence-dynamics")


def make_temporal_consciousness_stream_id() -> StreamId:
    """Create temporal consciousness stream identifier."""
    return StreamId.from_parts("consciousness", "temporal-experience")


def make_perspective_stream_id() -> StreamId:
    """Create perspective stream identifier."""
    return StreamId.from_parts("consciousness", "perspective-dynamics")


def make_situated_world_stream_id() -> StreamId:
    """Create situated world stream identifier."""
    return StreamId.from_parts("consciousness", "situated-world")


def make_phenomenal_binding_stream_id() -> StreamId:
    """Create phenomenal binding stream identifier."""
    return StreamId.from_parts("consciousness", "phenomenal-binding")


def get_record_kind_for_stream(stream_id: StreamId) -> Optional[ConsciousRecordKind]:
    """Determine record kind from stream ID."""
    name = stream_id.value
    if "field" in name:
        return ConsciousRecordKind.FIELD_ENTERED
    elif "intentional" in name:
        return ConsciousRecordKind.INTENTIONAL_TARGET_CHANGED
    elif "presence" in name:
        return ConsciousRecordKind.PRESENCE_ESTABLISHED
    elif "temporal" in name:
        return ConsciousRecordKind.PRIMAL_IMPRESSION
    elif "perspective" in name:
        return ConsciousRecordKind.PERSPECTIVE_SHIFT
    elif "world" in name:
        return ConsciousRecordKind.CONTEXT_SHIFTED
    elif "binding" in name:
        return ConsciousRecordKind.PERCEPTUAL_BINDING
    return None


# =============================================================================
# INTEGRATION WITH PERCEPTION STREAMS
# =============================================================================

@dataclass(frozen=True)
class PerceptionConsciousnessLink:
    """Links perception stream records to consciousness experience."""
    
    percept_record_id: StreamRecordId  # From perception streams
    conscious_record_id: str            # In consciousness streams
    binding_mode: PhenomenalBindingMode
    integration_time_utc: float = field(default_factory=time.time)


@dataclass(frozen=True)
class ConsciousnessIntegrationPoint:
    """Integration point between perception and consciousness."""
    
    stream_id: StreamId                # Perception stream
    integration_stream_id: StreamId    # Consciousness stream
    linked_records: Tuple[PerceptionConsciousnessLink, ...]
    integration_context: str           # Context of integration


# =============================================================================
# EXPORTS
# =============================================================================

__all__ = [
    # Record kinds
    "ConsciousRecordKind",
    "TemporalConsciousnessMode",
    "PerspectiveType",
    "PhenomenalBindingMode",
    
    # Metadata
    "ConsciousRecordMetadata",
    "ConsciousContinuity",
    
    # Records
    "ConsciousRecord",
    "ConsciousRecordBuilder",
    
    # Stream identifiers
    "make_conscious_field_stream_id",
    "make_intentional_context_stream_id",
    "make_presence_stream_id",
    "make_temporal_consciousness_stream_id",
    "make_perspective_stream_id",
    "make_situated_world_stream_id",
    "make_phenomenal_binding_stream_id",
    "get_record_kind_for_stream",
    
    # Integration
    "PerceptionConsciousnessLink",
    "ConsciousnessIntegrationPoint",
]