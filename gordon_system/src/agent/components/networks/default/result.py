# Default Network Result Models
# =============================

"""
Canonical DefaultNetwork result models for runtime-neutral coordination.

All result models are deeply immutable to ensure deterministic behavior,
replayability, and thread safety. No live objects, callbacks, or runtime
handles may be embedded in these models.

PHASE 4.3.12: Runtime-Neutral Result Contracts
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Tuple, Optional, Dict, Any, TYPE_CHECKING
from datetime import datetime

if TYPE_CHECKING:
    from .internal_episode.episode import InternalEpisode
    from .internal_thought.thought import InternalThought


# =============================================================================
# DEFAULT NETWORK RESULT PROVENANCE
# =============================================================================

@dataclass(frozen=True, slots=True)
class DefaultNetworkResultProvenance:
    """
    Complete provenance record for a DefaultNetwork result.
    
    Tracks origin and chain of custody without embedding runtime references.
    """
    
    # Request reference (required - no defaults)
    request_id: str
    
    # Processing metadata (required - no defaults)
    processed_at_utc: datetime
    prior_state_revision: int
    resulting_state_revision: int
    
    # Optional fields with defaults - must come after required fields
    processing_version: str = "1.0.0"
    
    # Configuration state
    configuration_revision: Optional[str] = None
    
    @classmethod
    def new(
        cls,
        request_id: str,
        processed_at_utc: datetime,
        prior_state_revision: int,
        resulting_state_revision: int,
    ) -> DefaultNetworkResultProvenance:
        """Create a new provenance record."""
        return cls(
            request_id=request_id,
            processed_at_utc=processed_at_utc,
            processing_version="1.0.0",
            configuration_revision=None,
            prior_state_revision=prior_state_revision,
            resulting_state_revision=resulting_state_revision,
        )


# =============================================================================
# DEFAULT NETWORK RESULT
# =============================================================================

@dataclass(frozen=True, slots=True)
class DefaultNetworkResult:
    """
    Canonical result contract from Default Network coordination.
    
    This is the primary output contract for one bounded semantic progression.
    
    ARCHITECTURAL INVARIANTS:
        DEFAULT-RES-INV-001: Result is immutable (deeply frozen dataclass with tuples)
        DEFAULT-RES-INV-002: Result contains no runtime references (no threads, no callbacks)
        DEFAULT-RES-INV-003: All semantic products preserve their specialized types
        DEFAULT-RES-INV-004: External requests are typed and bounded
        DEFAULT-RES-INV-005: Proposals are advisory only - not applied
        DEFAULT-RES-INV-006: State transitions are explicit records, not runtime actions
        
    PROPERTIES:
        • request_id: Reference to originating request
        • selected_path: Which path was chosen and why
        
    COORDINATION:
        • episode: The InternalEpisode being coordinated
        • products: Generated semantic products
        
    INTERNAL COGNITION:
        • internal_thoughts: Generated internally generated thoughts
        
    EXTERNAL INTERFACE:
        • external_requests: Requests for external computation (NOT executed)
        • proposals: Advisory proposals for other systems (NOT applied)
        
    OUTCOME:
        • outcome: Result of the coordination
        • continuation: Recommended next steps (advisory only)
        
    STATE MANAGEMENT:
        • state: Current DefaultNetworkState after this progression
        • transitions: Records of all state changes
        
    OBSERVABILITY:
        • diagnostics: Processing diagnostics and explanations
        • provenance: Complete origin and custody record
    
    NOT RESPONSIBLE FOR:
        • Executing external requests
        • Applying proposals
        • Mutating external state
        • Creating runtime threads or tasks
        • Scheduling continuation
    """
    
    # Request reference
    request_id: str
    """Reference to the originating request."""
    
    # Path selection
    selected_path: DefaultNetworkPathSelection
    """Which path was chosen and why."""
    
    # Episode coordination
    episode: InternalEpisode
    """The InternalEpisode being coordinated."""
    
    # Products (semantic outputs)
    products: Tuple[DefaultNetworkProduct, ...]
    """Generated semantic products."""
    
    # Internal cognition
    internal_thoughts: Tuple[InternalThought, ...]
    """Generated internally generated thoughts."""
    
    # External interface
    external_requests: Tuple[DefaultNetworkExternalRequest, ...]
    """Requests for external computation (NOT executed by network)."""
    
    proposals: Tuple[DefaultNetworkProposal, ...]
    """Advisory proposals for other systems (NOT applied by network)."""
    
    # Outcome and continuation
    outcome: DefaultNetworkOutcome
    """Result of the coordination."""
    
    continuation: DefaultNetworkContinuation
    """Recommended next steps (advisory only)."""
    
    # State management
    state: DefaultNetworkState
    """Current DefaultNetworkState after this progression."""
    
    transitions: Tuple[DefaultNetworkTransition, ...]
    """Records of all state changes."""
    
    # Observability
    diagnostics: DefaultNetworkDiagnostics
    """Processing diagnostics and explanations."""
    
    provenance: DefaultNetworkResultProvenance
    """Complete origin and custody record."""
    
    @classmethod
    def new(
        cls,
        request_id: str,
        selected_path: DefaultNetworkPathSelection,
        episode: InternalEpisode,
        products: Tuple[DefaultNetworkProduct, ...],
        internal_thoughts: Tuple[InternalThought, ...],
        external_requests: Tuple[DefaultNetworkExternalRequest, ...],
        proposals: Tuple[DefaultNetworkProposal, ...],
        outcome: DefaultNetworkOutcome,
        continuation: DefaultNetworkContinuation,
        state: DefaultNetworkState,
        transitions: Tuple[DefaultNetworkTransition, ...],
        diagnostics: DefaultNetworkDiagnostics,
        provenance: DefaultNetworkResultProvenance,
    ) -> DefaultNetworkResult:
        """Create a new result instance."""
        return cls(
            request_id=request_id,
            selected_path=selected_path,
            episode=episode,
            products=products,
            internal_thoughts=internal_thoughts,
            external_requests=external_requests,
            proposals=proposals,
            outcome=outcome,
            continuation=continuation,
            state=state,
            transitions=transitions,
            diagnostics=diagnostics,
            provenance=provenance,
        )


# =============================================================================
# DEFAULT NETWORK PATH SELECTION
# =============================================================================

@dataclass(frozen=True, slots=True)
class DefaultNetworkPathSelection:
    """
    Record of path selection reasoning.
    
    Explains which path was chosen and why others were excluded.
    """
    
    selected_path: str  # DefaultNetworkPath.*
    """The selected path."""
    
    considered_paths: Tuple[str, ...]
    """Paths that were considered."""
    
    exclusion_reasons: Tuple[str, ...]
    """Reasons why other paths were not selected."""
    
    confidence: float
    """Confidence in the selection (0.0 to 1.0)."""
    
    missing_prerequisites: Tuple[str, ...] = field(default_factory=tuple)
    """Missing prerequisites that would be needed for this path."""
    
    provenance: Optional[DefaultNetworkResultProvenance] = None
    """Provenance record."""
    
    @classmethod
    def new(
        cls,
        selected_path: str,
        considered_paths: Tuple[str, ...],
        exclusion_reasons: Tuple[str, ...],
        confidence: float,
    ) -> DefaultNetworkPathSelection:
        """Create a new path selection record."""
        return cls(
            selected_path=selected_path,
            considered_paths=considered_paths,
            exclusion_reasons=exclusion_reasons,
            confidence=confidence,
            missing_prerequisites=(),
            provenance=None,
        )


# =============================================================================
# DEFAULT NETWORK PRODUCT
# =============================================================================

@dataclass(frozen=True, slots=True)
class DefaultNetworkProduct:
    """
    Canonical product envelope for semantic outputs.
    
    Each product preserves the specialized subsystem's canonical type.
    Products are never flattened into generic dictionaries.
    """
    
    # Identity
    product_id: str
    """Unique identifier for this product."""
    
    # Kind (which subsystem produced it)
    kind: str  # DefaultNetworkProductKind.*
    """The kind of product."""
    
    # Payload (preserves specialized type)
    payload_type: str
    """The specialized payload type name."""
    
    payload_ref: str
    """Reference to the actual payload (not embedded)."""
    
    # Quality assessment
    confidence: float = 0.5
    """Confidence in this product (0.0 to 1.0)."""
    
    completeness_status: str = "partial"
    """Completeness status."""
    
    factuality: str = "unknown"
    """Factuality classification."""
    
    # Origin
    produced_by_path: Optional[str] = None
    """Which path produced this product."""
    
    episode_id: Optional[str] = None
    """Episode that produced this product."""
    
    provenance: Optional[DefaultNetworkResultProvenance] = None
    """Provenance record."""
    
    @classmethod
    def from_thought(cls, thought: InternalThought) -> DefaultNetworkProduct:
        """Create a product from an InternalThought."""
        return cls(
            product_id=f"product:{thought.thought_id}",
            kind="internal_thought",
            payload_type="InternalThought",
            payload_ref=thought.thought_id,
            confidence=thought.assessment.confidence,
            completeness_status="complete",
            factuality="inferred",
            produced_by_path=None,
            episode_id=thought.provenance.originating_episode_id,
            provenance=None,
        )
    
    @classmethod
    def from_payload(cls, kind: str, payload_type: str, payload_ref: str) -> DefaultNetworkProduct:
        """Create a product from a payload reference."""
        return cls(
            product_id=f"product:{hash((kind, payload_type, payload_ref)) & 0xFFFFFFFFFFFFFFFF:x}",
            kind=kind,
            payload_type=payload_type,
            payload_ref=payload_ref,
            confidence=0.5,
            completeness_status="partial",
            factuality="unknown",
            produced_by_path=None,
            episode_id=None,
            provenance=None,
        )


# =============================================================================
# DEFAULT NETWORK PROPOSAL
# =============================================================================

@dataclass(frozen=True, slots=True)
class DefaultNetworkProposal:
    """
    Canonical tagged proposal envelope for advisory recommendations.
    
    Proposals are NEVER applied by the Default Network - they are only
    advisory and must be processed by external authorities.
    """
    
    # Identity (required - no defaults)
    proposal_id: str
    """Unique identifier for this proposal."""
    
    kind: str  # DefaultNetworkProposalKind.*
    """The kind of proposal."""
    
    intended_authority: str  # Authority.*
    """Which external authority should process this."""
    
    payload_type: str
    """The specialized payload type name."""
    
    payload_ref: str
    """Reference to the actual payload (not embedded)."""
    
    supporting_products: Tuple[str, ...]
    """Product IDs that support this proposal."""
    
    # Optional fields with defaults - must come after required fields
    confidence: float = 0.5
    """Confidence in this proposal (0.0 to 1.0)."""
    
    evidence: str = ""
    """Supporting evidence (brief description)."""
    
    limitations: str = ""
    """Limitations or caveats."""
    
    origin_path: Optional[str] = None
    """Which path generated this proposal."""
    
    episode_id: Optional[str] = None
    """Episode that produced this proposal."""
    
    provenance: Optional[DefaultNetworkResultProvenance] = None
    """Provenance record."""
    
    @classmethod
    def new(
        cls,
        kind: str,
        intended_authority: str,
        payload_type: str,
        payload_ref: str,
        supporting_products: Tuple[str, ...],
        confidence: float = 0.5,
    ) -> DefaultNetworkProposal:
        """Create a new proposal."""
        return cls(
            proposal_id=f"proposal:{hash((kind, intended_authority, payload_type, payload_ref)) & 0xFFFFFFFFFFFFFFFF:x}",
            kind=kind,
            intended_authority=intended_authority,
            payload_type=payload_type,
            payload_ref=payload_ref,
            confidence=confidence,
            supporting_products=supporting_products,
            evidence="",
            limitations="",
            origin_path=None,
            episode_id=None,
            provenance=None,
        )


# Import types from state that are needed by the result module

from .state import (
    DefaultNetworkOutcome,
    DefaultNetworkContinuation,
    DefaultNetworkDiagnostics,
)

# =============================================================================
# DEFAULT NETWORK EXTERNAL REQUEST
# =============================================================================

@dataclass(frozen=True, slots=True)
class DefaultNetworkExternalRequest:
    """
    Canonical external request envelope for capability requests.
    
    External requests are NEVER executed by the Default Network - they
    are typed proposals that must be processed by external capabilities.
    """
    
    # Identity and correlation
    request_id: str
    """Unique identifier for this external request."""
    
    originating_request_id: str
    """Reference to the DefaultNetworkRequest that produced this."""
    
    episode_id: Optional[str]
    """Reference to the InternalEpisode (if any)."""
    
    step_id: Optional[str]
    """The coordination step that requires this result."""
    
    # Capability specification
    category: str  # DefaultNetworkExternalRequestCategory.*
    """The capability category needed."""
    
    operation_kind: str
    """The specific operation requested."""
    
    expected_result_contract: str
    """Contract for expected result type."""
    
    # Input projection (bounded)
    input_projection_ref: str
    """Reference to bounded input projection."""
    
    constraints: Tuple[str, ...]
    """Additional constraints."""
    
    # Idempotency
    idempotency_key: Optional[str] = None
    """Key for idempotent retry."""
    
    # Chaining
    correlation_id: Optional[str] = None
    """For distributed tracing."""
    
    causation_id: Optional[str] = None
    """Causation chain reference."""
    
    # Quality
    expected_confidence_threshold: float = 0.5
    """Minimum confidence threshold for result."""
    
    provenance: Optional[DefaultNetworkResultProvenance] = None
    """Provenance record."""
    
    @classmethod
    def new(
        cls,
        category: str,
        operation_kind: str,
        expected_result_contract: str,
        input_projection_ref: str,
    ) -> DefaultNetworkExternalRequest:
        """Create a new external request."""
        return cls(
            request_id=f"external:{hash((category, operation_kind, expected_result_contract)) & 0xFFFFFFFFFFFFFFFF:x}",
            originating_request_id="",
            episode_id=None,
            step_id=None,
            category=category,
            operation_kind=operation_kind,
            expected_result_contract=expected_result_contract,
            input_projection_ref=input_projection_ref,
            constraints=(),
            idempotency_key=None,
            correlation_id=None,
            causation_id=None,
            expected_confidence_threshold=0.5,
            provenance=None,
        )