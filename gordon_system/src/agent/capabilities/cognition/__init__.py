# Cognition Streams - Phase 3.11.10 Canonical Semantic Streaming Architecture
# ==============================================================================

"""
Cognition Streams: Immutable semantic transport for cognitive artifacts.

This module implements the canonical semantic stream architecture for all Cognition
capabilities as specified in Phase 3.11.10.

Cognition Capabilities own:
    - interpretation
    - abstraction  
    - reasoning
    - prediction
    - evaluation
    - framing
    - grounding
    - reflection
    - simulation
    - strategy
    - planning
    - metacognition

Cognition Streams own:
    - publication
    - ordering
    - subscriptions
    - replay
    - checkpoints
    - delivery
    - observability

Architectural Position:
    Network Activation → Cognition Capability Invocation → Cognitive Artifact → 
    Cognition Stream Commit → Authorized Subscribers

Cognition Streams transport immutable cognitive artifacts.

They never answer: What state should change? What action should execute?
              They answer: What cognitive work occurred? What was the reasoning?
                          What uncertainty remains? How was this derived?
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple, Any, Protocol, runtime_checkable
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
# COGNITIVE ARTIFACT KINDS - Categories of cognitive work
# =============================================================================


class CognitiveArtifactKind(Enum):
    """Categories of cognition stream artifact records."""
    
    # Core reasoning types
    INTERPRETATION = "interpretation"           # Parsing and meaning assignment
    ABSTRACTION = "abstraction"                 # Generalized representation
    GROUNDING = "grounding"                     # World-reference grounding
    FRAMING = "framing"                         # Active frame selection
    REASONING = "reasoning"                     # Inference chain
    PREDICTION = "prediction"                   # Future-state estimate
    EVALUATION = "evaluation"                   # Assessment or score
    REFLECTION = "reflection"                   # Outcome/process review
    SIMULATION = "simulation"                   # Hypothetical scenario
    STRATEGY = "strategy"                       # Strategy proposal
    PLANNING_PROPOSAL = "planning_proposal"     # Plan candidate
    HYPOTHESIS = "hypothesis"                   # Proposed explanation
    UNCERTAINTY_UPDATE = "uncertainty_update"   # Confidence/uncertainty change
    
    # Cognitive meta-work types
    CONFLICT = "conflict"                       # Contradiction detected
    INTEGRATION = "integration"                 # Synthesized result
    METACOGNITIVE_ASSESSMENT = "metacognitive_assessment"  # Reasoning quality assessment
    LANGUAGE_INTERPRETATION = "language_interpretation"    # Linguistic form
    MENTALESE_TRANSFORMATION = "mentalese_transformation"  # Internal representation
    
    # Result and status types
    COGNITIVE_PROPOSAL = "cognitive_proposal"   # General proposal record
    COGNITIVE_RESULT = "cognitive_result"       # Result from capability
    COGNITIVE_REVISION = "cognitive_revision"   # Revised artifact
    COGNITIVE_VALIDATION = "cognitive_validation"  # Validation result
    COGNITIVE_REJECTION = "cognitive_rejection"    # Rejected proposal
    COGNITIVE_SUPERSESSION = "cognitive_supersession"  # Supersedes previous


class ConfidenceScope(Enum):
    """Scoping for confidence values."""
    INTERPRETATION = "interpretation"
    PREDICTION = "prediction"
    EVALUATION = "evaluation"
    REASONING = "reasoning"
    GROUNDING = "grounding"
    SIMULATION = "simulation"
    STRATEGY = "strategy"
    INTEGRATION = "integration"
    VALIDATION = "validation"


class UncertaintyType(Enum):
    """Structured uncertainty dimensions."""
    EPISTEMIC = "epistemic"         # Lack of knowledge
    ALEATORIC = "aleatoric"         # Inherent randomness
    MODEL = "model"                 # Model limitations
    SOURCE = "source"               # Source unreliability
    TEMPORAL = "temporal"           # Temporal instability
    SCOPE = "scope"                 # Scope uncertainty
    IDENTITY = "identity"           # Identity ambiguity
    CAUSAL = "causal"               # Causal ambiguity


class ProposalTarget(Enum):
    """Targets that proposals may affect."""
    MEMORY = "memory"
    KNOWLEDGE = "knowledge"
    CONSCIOUSNESS = "consciousness"
    PERCEPTION = "perception"
    STRATEGY = "strategy"
    PLAN = "plan"
    ACTION = "action"
    EVALUATION = "evaluation"


class ProposalStatus(Enum):
    """Proposal status states."""
    DRAFT = "draft"                 # Draft proposal
    SUBMITTED = "submitted"         # Submitted for review
    VALIDATED = "validated"         # Passed validation
    ACCEPTED = "accepted"           # Accepted by target owner
    REJECTED = "rejected"           # Rejected by target owner
    SUPERSEDED = "superseded"       # Superseded by newer proposal
    EXPIRED = "expired"             # Proposal expired


class ArtifactStatus(Enum):
    """Cognitive artifact status."""
    PROPOSED = "proposed"
    COMMITTED = "committed"
    VALIDATED = "validated"
    REJECTED = "rejected"
    SUPERSEDED = "superseded"
    EXPIRED = "expired"


# =============================================================================
# COGNITIVE ARTIFACT METADATA
# =============================================================================

@dataclass(frozen=True)
class CognitiveArtifactMetadata:
    """Metadata for a cognitive artifact."""
    
    # Semantic context
    input_references: Tuple[str, ...] = field(default_factory=tuple)  # Input record references
    
    # Output tracking
    output_reference: Optional[str] = None  # Main output reference
    
    # Network/execution context
    network_activation_reference: Optional[str] = None
    execution_reference: Optional[str] = None
    stage_reference: Optional[str] = None
    
    # Trust and privacy
    trust_level: float = 1.0        # 0.0-1.0, initial trust in artifact
    privacy_class: str = "internal"  # internal, restricted, public
    
    # Uncertainty
    epistemic_uncertainty: float = 0.0
    aleatoric_uncertainty: float = 0.0
    model_uncertainty: float = 0.0
    
    # Confidence per scope
    confidence_by_scope: Dict[ConfidenceScope, float] = field(default_factory=dict)
    
    # Provenance
    producing_capability: str  # Which capability produced this?
    producing_operation: Optional[str] = None  # Specific operation within capability
    
    # Lifecycle
    created_at_utc: float = field(default_factory=time.time)
    expires_at_utc: Optional[float] = None  # Optional expiration time
    
    # Validation status
    validation_status: ArtifactStatus = ArtifactStatus.PROPOSED
    
    # Correlation/causation
    correlation_id: Optional[CorrelationId] = None
    causation_id: Optional[str] = None


# =============================================================================
# COGNITIVE ARTIFACT - Immutable Semantic Unit for Cognitive Work
# =============================================================================

@dataclass(frozen=True)
class CognitiveArtifact:
    """
    Immutable cognitive artifact representing a unit of cognitive work.
    
    A cognitive artifact contains:
        - Identity (artifact_id, stream position)
        - Artifact kind (interpretation, reasoning, prediction, etc.)
        - Capability origin (which capability produced it)
        - Input context references
        - Output or result content
        - Uncertainty and confidence measures
        - Trust classification
        - Validation status
    
    Cognitive artifacts are immutable after creation - new artifacts represent
    new cognitive work.
    """
    
    # Identity
    artifact_id: str  # Unique ID within cognition streams
    stream_id: StreamId
    generation_id: StreamGenerationId
    sequence_number: int
    
    # Artifact classification
    artifact_kind: CognitiveArtifactKind
    subkind: Optional[str] = None  # More specific classification
    
    # Capability origin
    capability_id: str  # Which capability produced this?
    operation_id: Optional[str] = None  # Specific operation within capability
    
    # Input context
    input_references: Tuple[str, ...]  # References to input records
    
    # Output/result
    output_reference: Optional[str] = None  # Main output reference
    result_content: Dict[str, Any] = field(default_factory=dict)  # Inline result content
    
    # Timestamps
    created_at_utc: float  # When artifact was produced
    committed_at_utc: float = field(default_factory=time.time)  # When committed to stream
    
    # Status and validation
    status: ArtifactStatus = ArtifactStatus.PROPOSED
    proposal_target: Optional[ProposalTarget] = None  # If it's a proposal, who should act?
    
    # Uncertainty and confidence
    uncertainty_by_dimension: Dict[UncertaintyType, float] = field(default_factory=dict)
    confidence_by_scope: Dict[ConfidenceScope, float] = field(default_factory=dict)
    
    # Provenance
    trust_level: float = 1.0
    privacy_class: str = "internal"
    
    # Correlation/causation
    correlation_id: Optional[str] = None
    causation_id: Optional[str] = None
    
    # Artifact reference (for large payloads)
    artifact_reference: Optional[ArtifactReference] = None
    
    # Validation metadata
    validation_status: str = "unvalidated"  # unvalidated, validated, rejected
    rejection_reason: Optional[str] = None
    
    @classmethod
    def create_builder(
        cls,
        stream_id: StreamId,
        generation_id: StreamGenerationId,
        artifact_kind: CognitiveArtifactKind,
        capability_id: str,
        input_references: Tuple[str, ...],
    ) -> "CognitiveArtifactBuilder":
        """Create a new cognitive artifact builder."""
        return CognitiveArtifactBuilder(
            stream_id=stream_id,
            generation_id=generation_id,
            artifact_kind=artifact_kind,
            capability_id=capability_id,
            input_references=input_references
        )
    
    @property
    def position(self) -> StreamPosition:
        """Get the stream position of this cognitive artifact."""
        return StreamPosition(
            stream_id=self.stream_id,
            generation_id=self.generation_id,
            sequence_number=self.sequence_number
        )
    
    def with_correlation(self, correlation_id: str) -> "CognitiveArtifact":
        """Return a copy with correlation ID set."""
        return dataclass_replace(self, correlation_id=correlation_id)
    
    def with_status(self, status: ArtifactStatus) -> "CognitiveArtifact":
        """Return a copy with updated status."""
        return dataclass_replace(self, status=status)
    
    def to_stream_record(
        self,
        record_type: RecordType = RecordType.EVENT
    ) -> StreamRecord:
        """Convert to generic stream record for transport."""
        payload = {
            "artifact_id": self.artifact_id,
            "artifact_kind": self.artifact_kind.value,
            "subkind": self.subkind,
            "capability_id": self.capability_id,
            "operation_id": self.operation_id,
            "input_references": list(self.input_references),
            "output_reference": self.output_reference,
            "result_content": self.result_content,
            "status": self.status.value,
            "proposal_target": self.proposal_target.value if self.proposal_target else None,
            "uncertainty_by_dimension": {k.value: v for k, v in self.uncertainty_by_dimension.items()},
            "confidence_by_scope": {k.value: v for k, v in self.confidence_by_scope.items()},
            "trust_level": self.trust_level,
            "privacy_class": self.privacy_class,
        }
        
        return StreamRecord(
            record_id=StreamRecordId(self.generation_id, self.sequence_number),
            stream_id=self.stream_id,
            generation_id=self.generation_id,
            sequence_number=self.sequence_number,
            producer_id=ProducerId(self.capability_id),
            timestamp_utc=self.committed_at_utc,
            payload=payload,
            metadata={
                "record_type": record_type.value,
                "status": self.status.value,
                "artifact_kind": self.artifact_kind.value,
            },
            status=RecordStatus.COMMITTED
        )


# =============================================================================
# COGNITIVE ARTIFACT BUILDER - Mutable construction before immutability
# =============================================================================

class CognitiveArtifactBuilder:
    """Mutable builder for cognitive artifacts."""
    
    def __init__(
        self,
        stream_id: StreamId,
        generation_id: StreamGenerationId,
        artifact_kind: CognitiveArtifactKind,
        capability_id: str,
        input_references: Tuple[str, ...],
    ):
        self._stream_id = stream_id
        self._generation_id = generation_id
        self._artifact_kind = artifact_kind
        self._capability_id = capability_id
        self._input_references = input_references
        
        # Mutable fields (get frozen in build())
        self._artifact_id: Optional[str] = None
        self._subkind: Optional[str] = None
        self._operation_id: Optional[str] = None
        self._output_reference: Optional[str] = None
        self._result_content: Dict[str, Any] = {}
        self._created_at_utc: float = time.time()
        self._status: ArtifactStatus = ArtifactStatus.PROPOSED
        self._proposal_target: Optional[ProposalTarget] = None
        self._uncertainty_by_dimension: Dict[UncertaintyType, float] = {}
        self._confidence_by_scope: Dict[ConfidenceScope, float] = {}
        self._trust_level: float = 1.0
        self._privacy_class: str = "internal"
        self._correlation_id: Optional[str] = None
        self._causation_id: Optional[str] = None
        
    # Setters for mutable fields (chainable)
    
    def set_artifact_id(self, artifact_id: str) -> "CognitiveArtifactBuilder":
        """Set the artifact ID."""
        self._artifact_id = artifact_id
        return self
    
    def set_subkind(self, subkind: str) -> "CognitiveArtifactBuilder":
        """Set the subkind classification."""
        self._subkind = subkind
        return self
    
    def set_operation_id(self, operation_id: str) -> "CognitiveArtifactBuilder":
        """Set the operation ID within the capability."""
        self._operation_id = operation_id
        return self
    
    def set_output_reference(self, output_reference: str) -> "CognitiveArtifactBuilder":
        """Set the main output reference."""
        self._output_reference = output_reference
        return self
    
    def set_result_content(self, result_content: Dict[str, Any]) -> "CognitiveArtifactBuilder":
        """Set the inline result content."""
        self._result_content = result_content.copy()
        return self
    
    def add_uncertainty(self, uncertainty_type: UncertaintyType, value: float) -> "CognitiveArtifactBuilder":
        """Add uncertainty for a dimension (0.0-1.0)."""
        if not 0.0 <= value <= 1.0:
            raise ValueError(f"Uncertainty must be 0.0-1.0, got {value}")
        self._uncertainty_by_dimension[uncertainty_type] = value
        return self
    
    def add_confidence(self, scope: ConfidenceScope, value: float) -> "CognitiveArtifactBuilder":
        """Add confidence for a scope (0.0-1.0)."""
        if not 0.0 <= value <= 1.0:
            raise ValueError(f"Confidence must be 0.0-1.0, got {value}")
        self._confidence_by_scope[scope] = value
        return self
    
    def set_trust_level(self, level: float) -> "CognitiveArtifactBuilder":
        """Set trust level (0.0-1.0)."""
        if not 0.0 <= level <= 1.0:
            raise ValueError(f"Trust level must be 0.0-1.0, got {level}")
        self._trust_level = level
        return self
    
    def set_privacy_class(self, privacy_class: str) -> "CognitiveArtifactBuilder":
        """Set privacy class (internal, restricted, public)."""
        self._privacy_class = privacy_class
        return self
    
    def set_correlation_id(self, correlation_id: str) -> "CognitiveArtifactBuilder":
        """Set correlation ID for grouping."""
        self._correlation_id = correlation_id
        return self
    
    def set_causation_id(self, causation_id: str) -> "CognitiveArtifactBuilder":
        """Set causation ID (what caused this artifact)."""
        self._causation_id = causation_id
        return self
    
    def set_proposal_target(self, target: ProposalTarget) -> "CognitiveArtifactBuilder":
        """Set proposal target if this is a proposal."""
        self._proposal_target = target
        return self
    
    def set_status(self, status: ArtifactStatus) -> "CognitiveArtifactBuilder":
        """Set artifact status."""
        self._status = status
        return self
    
    # Build immutable artifact
    
    def build(self) -> CognitiveArtifact:
        """Build the immutable cognitive artifact."""
        if self._artifact_id is None:
            self._artifact_id = str(uuid.uuid4())
        
        return CognitiveArtifact(
            artifact_id=self._artifact_id,
            stream_id=self._stream_id,
            generation_id=self._generation_id,
            sequence_number=0,  # Will be set by commit authority
            artifact_kind=self._artifact_kind,
            subkind=self._subkind,
            capability_id=self._capability_id,
            operation_id=self._operation_id,
            input_references=self._input_references,
            output_reference=self._output_reference,
            result_content=self._result_content.copy(),
            created_at_utc=self._created_at_utc,
            committed_at_utc=time.time(),
            status=self._status,
            proposal_target=self._proposal_target,
            uncertainty_by_dimension=dict(self._uncertainty_by_dimension),
            confidence_by_scope=dict(self._confidence_by_scope),
            trust_level=self._trust_level,
            privacy_class=self._privacy_class,
            correlation_id=self._correlation_id,
            causation_id=self._causation_id,
        )


# =============================================================================
# COGNITIVE REQUEST - Request for cognitive work
# =============================================================================

@dataclass(frozen=True)
class CognitiveRequest:
    """
    Immutable request for cognitive work from a capability.
    
    A request specifies what cognitive work is needed but does NOT guarantee
    execution, completion, or acceptance.
    """
    
    # Identity
    request_id: str  # Unique request identifier
    
    # Requested work
    requested_capability: str  # Which capability?
    requested_operation: Optional[str] = None  # Specific operation within capability
    
    # Input references (what context to use)
    input_references: Tuple[str, ...] = field(default_factory=tuple)  # Record IDs or references
    
    # Context reference (existing context to apply)
    context_reference: Optional[str] = None
    
    # Constraints
    constraints: Dict[str, Any] = field(default_factory=dict)  # Operation constraints
    
    deadline_utc: Optional[float] = None  # Optional deadline for completion
    priority: int = 0  # Priority (higher = more urgent)
    
    # Uncertainty requirements (what uncertainty is acceptable?)
    uncertainty_requirements: Dict[UncertaintyType, float] = field(default_factory=dict)  # max values
    
    # Output contract (what kind of output expected?)
    output_contract: Optional[str] = None  # Contract reference or description
    
    # Requester
    requester: str  # Who requested this? (capability or network)
    
    # Semantic context
    correlation_id: Optional[str] = None
    causation_id: Optional[str] = None
    
    # Authorization context
    authorization_context_reference: Optional[str] = None
    
    # Trust and privacy
    trust_requirement: float = 0.5  # Minimum acceptable trust in inputs
    privacy_class: str = "internal"
    
    # Request lifecycle
    created_at_utc: float = field(default_factory=time.time)
    submitted_at_utc: Optional[float] = None
    admitted_at_utc: Optional[float] = None
    started_at_utc: Optional[float] = None
    completed_at_utc: Optional[float] = None
    
    status: str = "pending"  # pending, admitted, in_progress, completed, rejected, expired
    
    def is_expired(self) -> bool:
        """Check if request has exceeded its deadline."""
        if self.deadline_utc is None:
            return False
        return time.time() > self.deadline_utc


# =============================================================================
# COGNITIVE PROPOSAL - A proposal to affect state
# =============================================================================

@dataclass(frozen=True)
class CognitiveProposal:
    """
    Immutable cognitive proposal for state change.
    
    A proposal does NOT grant authority. It is a recommendation that the
    canonical owner of affected state may accept or reject.
    
    Every proposal must identify:
        - proposing capability
        - target owner (who owns the affected state?)
        - requested interpretation or state effect
        - evidence references
        - confidence
        - uncertainty
        - provenance
        - expiration
        - validation requirements
    """
    
    # Identity
    proposal_id: str  # Unique proposal identifier
    
    # Origin
    proposing_capability: str  # Which capability proposed this?
    
    # Target (who should act on it?)
    target_owner: ProposalTarget
    target_state_type: str  # e.g., "memory", "knowledge", "action"
    
    # Proposal content
    proposal_kind: str  # e.g., "interpretation", "prediction", "plan", "strategy"
    proposal_content: Dict[str, Any] = field(default_factory=dict)
    
    # Evidence
    evidence_references: Tuple[str, ...] = field(default_factory=tuple)
    
    # Uncertainty and confidence
    uncertainty_by_dimension: Dict[UncertaintyType, float] = field(default_factory=dict)
    confidence_by_scope: Dict[ConfidenceScope, float] = field(default_factory=dict)
    
    # Provenance
    provenance: Dict[str, str] = field(default_factory=dict)  # How was this derived?
    
    # Lifecycle
    created_at_utc: float = field(default_factory=time.time)
    expires_at_utc: Optional[float] = None
    
    # Validation
    validation_status: str = "unvalidated"  # unvalidated, validated, rejected
    validation_requirements: Dict[str, Any] = field(default_factory=dict)  # What's needed to validate?
    
    def is_expired(self) -> bool:
        """Check if proposal has expired."""
        if self.expires_at_utc is None:
            return False
        return time.time() > self.expires_at_utc
    
    def can_be_validated_by(self, validator: str) -> bool:
        """Check if a specific validator can validate this proposal."""
        # For now, allow any validator; can be refined based on policy
        return True


# =============================================================================
# COGNITIVE RESULT - A result from cognitive work
# =============================================================================

@dataclass(frozen=True)
class CognitiveResult:
    """
    Immutable result from completed cognitive work.
    
    Distinguishes between:
        - Proposed Result (hasn't been acted on by target owner)
        - Validated Result (passed validation)
        - Accepted Result (accepted by target owner)
        - Rejected Result (rejected by target owner)
        - Superseded Result (replaced by newer result)
        - Expired Result (no longer applicable)
        - Owner-Committed Effect (target owner committed the effect)
    """
    
    # Identity
    result_id: str  # Unique result identifier
    
    # Origin
    origin_artifact_id: str  # Which cognitive artifact produced this?
    originating_capability: str
    
    # Result classification
    result_kind: str  # e.g., "reasoning", "prediction", "evaluation"
    
    # Result content
    result_content: Dict[str, Any] = field(default_factory=dict)
    
    # Uncertainty and confidence
    uncertainty_by_dimension: Dict[UncertaintyType, float] = field(default_factory=dict)
    confidence_by_scope: Dict[ConfidenceScope, float] = field(default_factory=dict)
    
    # Status progression
    status: str = "proposed"  # proposed, validated, accepted, rejected, superseded, expired
    
    # Owner action
    owner_action_taken: bool = False  # Did target owner act on it?
    owner_action_at_utc: Optional[float] = None
    
    # Provenance
    provenance: Dict[str, str] = field(default_factory=dict)
    
    # Timestamps
    created_at_utc: float = field(default_factory=time.time)
    validated_at_utc: Optional[float] = None
    accepted_at_utc: Optional[float] = None
    rejected_at_utc: Optional[float] = None
    superseded_at_utc: Optional[float] = None
    expired_at_utc: Optional[float] = None
    
    # References to related artifacts
    related_artifact_ids: Tuple[str, ...] = field(default_factory=tuple)


# =============================================================================
# COGNITIVE REVISION - A revision of a previous artifact
# =============================================================================

@dataclass(frozen=True)
class CognitiveRevision:
    """
    Immutable record of a cognitive artifact revision.
    
    A revision must:
        - Have its own artifact identity
        - Reference the artifact being revised
        - Preserve the original artifact (don't mutate it)
        - State the reason for revision
        - Preserve provenance
        - Update confidence and uncertainty explicitly
        - Preserve trust and privacy
        - Indicate whether it supersedes the original
        - Identify the revising capability
    """
    
    # Identity
    revision_id: str  # Unique revision identifier
    
    # Revision chain
    revised_artifact_id: str  # Which artifact was revised?
    previous_revision_ids: Tuple[str, ...] = field(default_factory=tuple)  # Previous revisions in chain
    
    # Revision info
    revising_capability: str  # Who produced the revision?
    revision_reason: str  # Why was it revised?
    
    # New content
    revised_artifact_content: Dict[str, Any]
    
    # Updated metadata
    new_confidence_by_scope: Dict[ConfidenceScope, float] = field(default_factory=dict)
    new_uncertainty_by_dimension: Dict[UncertaintyType, float] = field(default_factory=dict)
    
    # Status
    is_supersession: bool = False  # Does this supersede the original?
    revision_order: int = 1  # Which revision in chain (1 = first)
    
    # Timestamps
    created_at_utc: float = field(default_factory=time.time)
    effective_from_utc: Optional[float] = None
    
    # Validation
    validation_status: str = "unvalidated"


# =============================================================================
# COGNITIVE CONFLICT - A detected contradiction
# =============================================================================

@dataclass(frozen=True)
class CognitiveConflict:
    """
    Immutable record of a cognitive conflict.
    
    Conflicts may be resolved by:
        - Executive Network arbitration
        - Metacognition assessment
        - Evaluation-based selection
        - Owner-specific resolution
    
    A conflict does NOT automatically require arbitrary selection.
    """
    
    # Identity
    conflict_id: str  # Unique conflict identifier
    
    # Conflict type
    conflict_kind: str  # e.g., "interpretation_conflict", "prediction_incompatible"
    
    # Conflicting elements
    element_a_artifact_id: str  # First conflicting artifact
    element_a_content_summary: Dict[str, Any]
    element_b_artifact_id: str  # Second conflicting artifact
    element_b_content_summary: Dict[str, Any]
    
    # Conflict description
    conflict_description: str
    conflict_type_detail: str  # e.g., "contradictory_predictions", "inconsistent_reasoning"
    
    # Resolution status
    is_resolved: bool = False
    resolution_reason: Optional[str] = None
    resolved_at_utc: Optional[float] = None
    
    # Routing for resolution
    routing_destination: Optional[str] = None  # Where should it be routed? (network, capability)
    
    # Timestamps
    detected_at_utc: float = field(default_factory=time.time)
    
    # Correlation
    correlation_id: Optional[str] = None


# =============================================================================
# COGNITIVE INTEGRATION - A synthesized result from multiple inputs
# =============================================================================

@dataclass(frozen=True)
class CognitiveIntegration:
    """
    Immutable record of cognitive integration (synthesis).
    
    Integration must preserve:
        - Source identities (don't erase origins)
        - Rejected alternatives
        - Uncertainty
        - Conflicting evidence
        - Trust distinctions
        - Privacy distinctions
    """
    
    # Identity
    integration_id: str  # Unique integration identifier
    
    # Input sources
    input_artifact_ids: Tuple[str, ...]  # Which artifacts were integrated?
    source_capabilities: Tuple[str, ...] = field(default_factory=tuple)  # Origin capabilities
    
    # Integration result
    integrated_result: Dict[str, Any]
    
    # Synthesis details
    synthesis_kind: str  # e.g., "interpretation_merge", "uncertainty_aggregation"
    synthesis_method: str  # How was it synthesized?
    
    # Resolved conflicts (if any)
    resolved_conflict_ids: Tuple[str, ...] = field(default_factory=tuple)
    rejected_alternatives: Tuple[Dict[str, Any], ...] = field(default_factory=tuple)
    
    # Integration quality
    integration_confidence: float = 1.0
    remaining_uncertainty_by_dimension: Dict[UncertaintyType, float] = field(default_factory=dict)
    
    # Provenance
    provenance: Dict[str, str] = field(default_factory=dict)  # Which sources, methods used?
    
    # Timestamps
    created_at_utc: float = field(default_factory=time.time)


# =============================================================================
# COGNITIVE UNCERTAINTY UPDATE - An update to uncertainty estimates
# =============================================================================

@dataclass(frozen=True)
class CognitiveUncertaintyUpdate:
    """
    Immutable record of an uncertainty estimate update.
    
    Uncertainty must not be represented by one ambiguous scalar when richer
    structure is available. Possible dimensions include:
        - epistemic uncertainty (lack of knowledge)
        - aleatoric uncertainty (inherent randomness)
        - model uncertainty (model limitations)
        - source uncertainty (source unreliability)
        - temporal uncertainty (temporal instability)
        - scope uncertainty (scope boundaries)
        - identity uncertainty (identity ambiguity)
        - causal uncertainty (causal ambiguity)
    """
    
    # Identity
    update_id: str  # Unique update identifier
    
    # Target of update
    target_artifact_id: str  # Which artifact's uncertainty is updated?
    
    # Update type
    update_type: str  # e.g., "confidence_increase", "uncertainty_decrease"
    
    # Dimension-specific updates
    dimension_updates: Dict[UncertaintyType, Tuple[float, float]] = field(default_factory=dict)
    # (old_value, new_value) for each dimension
    
    # Summary metrics
    epistemic_delta: Optional[float] = None  # Change in epistemic uncertainty
    aleatoric_delta: Optional[float] = None  # Change in aleatoric uncertainty
    
    # Confidence update
    confidence_deltas_by_scope: Dict[ConfidenceScope, float] = field(default_factory=dict)
    
    # Evidence for update
    evidence_references: Tuple[str, ...] = field(default_factory=tuple)
    
    # Timestamps
    created_at_utc: float = field(default_factory=time.time)


# =============================================================================
# COGNITIVE VALIDATION - A validation result for a cognitive artifact
# =============================================================================

@dataclass(frozen=True)
class CognitiveValidation:
    """
    Immutable record of a cognitive artifact validation.
    
    Validation checks may include:
        - identity verification
        - generation tracking
        - producer authenticity
        - schema compatibility
        - scope validation
        - trust and privacy bounds
        - metadata limits
        - lifecycle state
        - ordering validity
    """
    
    # Identity
    validation_id: str  # Unique validation identifier
    
    # Target of validation
    validated_artifact_id: str
    
    # Validation results per check
    checks: Dict[str, bool] = field(default_factory=dict)  # Check name -> passed?
    
    # Overall result
    is_valid: bool = False
    failure_reasons: Tuple[str, ...] = field(default_factory=tuple)
    
    # Validation metadata
    validator_id: str  # Who performed validation?
    validated_at_utc: float = field(default_factory=time.time)
    
    # Trust impact (does validation change trust?)
    trust_adjustment: float = 0.0  # Positive = increase, negative = decrease
    
    # Privacy impact
    privacy_impact: Dict[str, Any] = field(default_factory=dict)


# =============================================================================
# STREAM ID ENTITIES - Cognition-specific stream identifiers
# =============================================================================

def make_cognition_stream_id(stream_name: str) -> StreamId:
    """Create a cognition stream ID."""
    return StreamId(f"cognition:{stream_name}")


# Predefined stream IDs for common cognition streams
INTERPRETATION_STREAM_ID = make_cognition_stream_id("interpretation")
ABSTRACTION_STREAM_ID = make_cognition_stream_id("abstraction")
GROUNDING_STREAM_ID = make_cognition_stream_id("grounding")
FRAMING_STREAM_ID = make_cognition_stream_id("framing")
REASONING_STREAM_ID = make_cognition_stream_id("reasoning")
PREDICTION_STREAM_ID = make_cognition_stream_id("prediction")
EVALUATION_STREAM_ID = make_cognition_stream_id("evaluation")
REFLECTION_STREAM_ID = make_cognition_stream_id("reflection")
SIMULATION_STREAM_ID = make_cognition_stream_id("simulation")
STRATEGY_STREAM_ID = make_cognition_stream_id("strategy")
PLANNING_PROPOSAL_STREAM_ID = make_cognition_stream_id("planning_proposal")
HYPOTHESIS_STREAM_ID = make_cognition_stream_id("hypothesis")
UNCERTAINTY_REVISION_STREAM_ID = make_cognition_stream_id("uncertainty_revision")
COGNITIVE_CONFLICT_STREAM_ID = make_cognition_stream_id("cognitive_conflict")
COGNITIVE_INTEGRATION_STREAM_ID = make_cognition_stream_id("cognitive_integration")
METACOGNITIVE_ASSESSMENT_STREAM_ID = make_cognition_stream_id("metacognitive_assessment")
LANGUAGE_INTERPRETATION_STREAM_ID = make_cognition_stream_id("language_interpretation")
MENTALESE_TRANSFORMATION_STREAM_ID = make_cognition_stream_id("mentalese_transformation")

# Canonical parent stream
COGNITION_STREAM_ID = StreamId("cognition:artifacts")


# =============================================================================
# STREAM KIND ENUMERATION - Cognition streams have special kind
# =============================================================================

class CognitionStreamKind(Enum):
    """Categories of cognition streams."""
    
    # Semantic streams (by cognitive operation)
    INTERPRETATION = "interpretation"
    ABSTRACTION = "abstraction"
    GROUNDING = "grounding"
    FRAMING = "framing"
    REASONING = "reasoning"
    PREDICTION = "prediction"
    EVALUATION = "evaluation"
    REFLECTION = "reflection"
    SIMULATION = "simulation"
    STRATEGY = "strategy"
    PLANNING_PROPOSAL = "planning_proposal"
    HYPOTHESIS = "hypothesis"
    UNCERTAINTY_REVISION = "uncertainty_revision"
    
    # Meta streams
    COGNITIVE_CONFLICT = "cognitive_conflict"
    COGNITIVE_INTEGRATION = "cognitive_integration"
    METACOGNITIVE_ASSESSMENT = "metacognitive_assessment"
    
    # Language/representation streams
    LANGUAGE_INTERPRETATION = "language_interpretation"
    MENTALESE_TRANSFORMATION = "mentalese_transformation"
    
    # Canonical parent (all cognitive artifacts)
    ARTIFACTS = "artifacts"


# =============================================================================
# UTILITY FUNCTIONS
# =============================================================================

def compute_artifact_correlation_id(artifact: CognitiveArtifact) -> str:
    """Compute a deterministic correlation ID for an artifact based on its content."""
    import hashlib
    content_str = str(sorted(artifact.result_content.items())) if artifact.result_content else ""
    hash_value = hashlib.sha256(content_str.encode()).hexdigest()[:16]
    return f"correlation:{hash_value}"


def estimate_artifact_uncertainty(uncertainty_by_dimension: Dict[UncertaintyType, float]) -> float:
    """Estimate overall uncertainty from dimension-specific values (0.0-1.0)."""
    if not uncertainty_by_dimension:
        return 0.0
    return sum(uncertainty_by_dimension.values()) / len(uncertainty_by_dimension)


def estimate_artifact_confidence(confidence_by_scope: Dict[ConfidenceScope, float]) -> float:
    """Estimate overall confidence from scope-specific values (0.0-1.0)."""
    if not confidence_by_scope:
        return 1.0
    return sum(confidence_by_scope.values()) / len(confidence_by_scope)


# =============================================================================
# CONTRACT VERSION - Current contract version for this module
# =============================================================================

CONTRACT_VERSION_MAJOR = 1
CONTRACT_VERSION_MINOR = 0
CONTRACT_VERSION_PATCH = 0
CONTRACT_VERSION_STRING = f"{CONTRACT_VERSION_MAJOR}.{CONTRACT_VERSION_MINOR}.{CONTRACT_VERSION_PATCH}"