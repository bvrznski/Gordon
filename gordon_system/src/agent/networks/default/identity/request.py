# Identity Integration Request Models
# ====================================

"""
Immutable models for identity integration requests, purposes, subjects, and scopes.

ARCHITECTURAL PRINCIPLES:
    • All dataclasses are frozen (deeply immutable)
    • No runtime dependencies (no imports from Core or Execution)
    • Bounded by explicit limits
    • Semantic content only (no live objects)
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Tuple, Optional, FrozenSet
from datetime import datetime


# =============================================================================
# ID TYPES
# =============================================================================

IdentityIntegrationRequestId = str
"""Unique identifier for an identity integration request."""

InternalContextId = str
"""Reference to an InternalContext instance."""

InternalEpisodeId = str
"""Reference to an InternalEpisode instance."""

InternalThoughtId = str
"""Reference to an InternalThought instance."""

CorrelationId = str
"""Correlation ID for distributed tracing."""

CausationId = Optional[str]
"""Causation ID if request results from another event."""


# =============================================================================
# IDENTITY INTEGRATION PURPOSE - What identity integration is trying to accomplish
# =============================================================================

@dataclass(frozen=True, slots=True)
class IdentityIntegrationPurpose:
    """
    Immutable description of the identity integration purpose.
    
    Purpose defines what the integration is trying to accomplish without
    embedding runtime implementation details.
    
    PROPERTIES:
        • kind: Canonical purpose category (IdentityIntegrationPurposeKind.*)
        • statement: Human-readable description
        • expected_context: What context projections are needed
        • allowed_products: Which product kinds may be produced
        • completion_rules: Conditions for successful completion
        • recursion_limit: How deep recursive integration is allowed
        • required_confidence: Minimum confidence threshold
    """
    
    kind: str  # IdentityIntegrationPurposeKind.*
    """The canonical purpose category."""
    
    statement: str = ""
    """Human-readable description of what this integration does."""
    
    expected_context: Tuple[str, ...] = field(default_factory=tuple)
    """Required context projections (e.g., 'memory', 'identity')."""
    
    allowed_products: Tuple[str, ...] = field(default_factory=tuple)
    """Product kinds this purpose is allowed to produce."""
    
    completion_rules: Tuple[str, ...] = field(default_factory=tuple)
    """Conditions that must be met for successful completion."""
    
    recursion_limit: int = 3
    """Maximum recursive integration depth."""
    
    required_confidence: float = 0.5
    """Minimum confidence level required (0.0 to 1.0)."""
    
    @classmethod
    def self_model_review(cls) -> IdentityIntegrationPurpose:
        """Create a self-model review purpose."""
        return cls(
            kind="self_model_review",
            statement="Review and assess the current self-model for consistency",
            expected_context=("identity", "memory", "narrative"),
            allowed_products=(
                "identity_aspect_summary",
                "identity_continuity_report",
                "identity_consistency_report",
                "identity_coherence_report",
            ),
            completion_rules=("at_least_one_assessment",),
            recursion_limit=2,
            required_confidence=0.6,
        )
    
    @classmethod
    def role_integration(cls) -> IdentityIntegrationPurpose:
        """Create a role integration purpose."""
        return cls(
            kind="role_integration",
            statement="Integrate roles into current context and identity",
            expected_context=("identity", "roles"),
            allowed_products=(
                "role_account",
                "identity_role_report",
            ),
            completion_rules=("all_active_roles_identified",),
            recursion_limit=1,
            required_confidence=0.5,
        )
    
    @classmethod
    def value_integration(cls) -> IdentityIntegrationPurpose:
        """Create a value integration purpose."""
        return cls(
            kind="value_integration",
            statement="Evaluate alignment between behavior and accepted values",
            expected_context=("identity", "behavior"),
            allowed_products=(
                "value_alignment_report",
                "identity_value_assessment",
            ),
            completion_rules=("at_least_one_value_assessed",),
            recursion_limit=2,
            required_confidence=0.5,
        )
    
    @classmethod
    def capability_self_assessment(cls) -> IdentityIntegrationPurpose:
        """Create a capability self-assessment purpose."""
        return cls(
            kind="capability_self_assessment",
            statement="Evaluate capability claims against observed performance",
            expected_context=("identity", "capabilities", "outcomes"),
            allowed_products=(
                "capability_self_assessment",
                "identity_capability_report",
            ),
            completion_rules=("at_least_one_capability_assessed",),
            recursion_limit=1,
            required_confidence=0.7,
        )


# =============================================================================
# IDENTITY SUBJECT - What is being integrated
# =============================================================================

@dataclass(frozen=True, slots=True)
class IdentitySubject:
    """
    Immutable description of the identity integration subject.
    
    Subject defines what identity components are being analyzed or evaluated
    without embedding live objects or full data structures.
    
    PROPERTIES:
        • kind: Canonical subject category (IdentitySubjectKind.*)
        • subject_id: ID reference to the subject entity
        • summary: Brief description of the subject
        • source_revision: Revision number at time of integration
        • artifact_references: References to relevant artifacts
        • temporal_bounds: Start and end times for relevance
    """
    
    kind: str  # IdentitySubjectKind.*
    """The canonical subject category."""
    
    subject_id: Optional[str] = None
    """ID reference to the subject entity (if applicable)."""
    
    summary: str = ""
    """Brief description of what is being integrated."""
    
    source_revision: int = 1
    """Source system revision number at integration start."""
    
    artifact_references: Tuple[str, ...] = field(default_factory=tuple)
    """References to relevant artifacts (memory IDs, thought IDs, etc.)."""
    
    temporal_bounds_start_utc: Optional[datetime] = None
    """Start of temporal relevance window."""
    
    temporal_bounds_end_utc: Optional[datetime] = None
    """End of temporal relevance window."""
    
    @classmethod
    def whole_agent(cls) -> IdentitySubject:
        """Create a subject for the whole agent identity."""
        return cls(
            kind="whole_agent",
            summary="Whole agent identity integration",
        )
    
    @classmethod
    def self_model(cls, model_id: str = "") -> IdentitySubject:
        """Create a subject for the internal self-model."""
        return cls(
            kind="self_model",
            subject_id=model_id or None,
            summary="Internal self-model representation",
        )
    
    @classmethod
    def role(cls, role_name: str) -> IdentitySubject:
        """Create a subject for a specific role."""
        return cls(
            kind="role",
            summary=f"Role integration: {role_name}",
        )
    
    @classmethod
    def value(cls, value_name: str) -> IdentitySubject:
        """Create a subject for a specific value."""
        return cls(
            kind="value",
            summary=f"Value integration: {value_name}",
        )
    
    @classmethod
    def commitment(cls, commitment_id: str) -> IdentitySubject:
        """Create a subject for a specific commitment."""
        return cls(
            kind="commitment",
            subject_id=commitment_id,
            summary=f"Commitment integration: {commitment_id}",
        )


# =============================================================================
# IDENTITY INTEGRATION SCOPE - Bounded constraints on integration
# =============================================================================

@dataclass(frozen=True, slots=True)
class IdentityIntegrationScope:
    """
    Immutable scope constraints for an identity integration episode.
    
    Scope prevents one integration from becoming unbounded by imposing
    explicit limits on resources and evidence.
    
    PROPERTIES:
        • maximum_identity_aspects: Hard limit on identity aspect collection
        • maximum_roles: Max roles to consider
        • maximum_values: Max values to consider
        • maximum_commitments: Max commitments to consider
        • maximum_capabilities: Max capabilities to assess
        • maximum_limitations: Max limitations to record
        • maximum_source_references: Max sources to consult
        • maximum_evidence_items: Max evidence items
        • maximum_temporal_range_seconds: Maximum age of relevant activity
        • maximum_plan_steps: Max steps in integration plan
        • maximum_products_expected: Expected upper bound on products
        • excluded_subjects: Subjects that must not be included
        • permitted_product_kinds: Which product kinds are allowed
        • required_confidence: Minimum confidence threshold
    """
    
    # Evidence limits
    maximum_identity_aspects: int = 50
    """Maximum identity aspects to collect."""
    
    maximum_roles: int = 20
    """Maximum roles to consider."""
    
    maximum_values: int = 30
    """Maximum values to consider."""
    
    maximum_commitments: int = 25
    """Maximum commitments to consider."""
    
    maximum_capabilities: int = 15
    """Maximum capabilities to assess."""
    
    maximum_limitations: int = 15
    """Maximum limitations to record."""
    
    # Source limits
    maximum_source_references: int = 100
    """Maximum source references to consult."""
    
    maximum_evidence_items: int = 200
    """Maximum evidence items to collect."""
    
    # Temporal limit
    maximum_temporal_range_seconds: float = 604800.0  # 7 days
    """Maximum age of relevant activity (in seconds)."""
    
    # Planning limits
    maximum_plan_steps: int = 30
    """Maximum steps in the integration plan."""
    
    maximum_products_expected: int = 25
    """Expected upper bound on identity products."""
    
    # Subject constraints
    excluded_subjects: Tuple[str, ...] = field(default_factory=tuple)
    """Subject IDs that must not be included."""
    
    permitted_product_kinds: Tuple[str, ...] = field(default_factory=tuple)
    """Which product kinds are permitted (empty = all)."""
    
    # Quality thresholds
    required_confidence: float = 0.5
    """Minimum confidence threshold for products."""
    
    maximum_recursion_depth: int = 3
    """Maximum recursive integration depth allowed."""
    
    require_new_evidence_for_recursion: bool = True
    """If true, child integrations need new evidence."""
    
    @classmethod
    def surface_level(cls) -> IdentityIntegrationScope:
        """Create a scope for shallow integration."""
        return cls(
            maximum_identity_aspects=25,
            maximum_roles=10,
            maximum_values=15,
            maximum_source_references=30,
            maximum_evidence_items=50,
            maximum_temporal_range_seconds=86400.0,  # 1 day
            maximum_plan_steps=10,
            maximum_products_expected=5,
        )
    
    @classmethod
    def standard_level(cls) -> IdentityIntegrationScope:
        """Create a scope for normal integration."""
        return cls(
            maximum_identity_aspects=50,
            maximum_roles=20,
            maximum_values=30,
            maximum_source_references=100,
            maximum_evidence_items=200,
            maximum_temporal_range_seconds=604800.0,  # 7 days
            maximum_plan_steps=30,
            maximum_products_expected=25,
        )
    
    @classmethod
    def deep_level(cls) -> IdentityIntegrationScope:
        """Create a scope for thorough integration."""
        return cls(
            maximum_identity_aspects=100,
            maximum_roles=40,
            maximum_values=60,
            maximum_source_references=200,
            maximum_evidence_items=500,
            maximum_temporal_range_seconds=2592000.0,  # 30 days
            maximum_plan_steps=50,
            maximum_products_expected=50,
        )


# =============================================================================
# IDENTITY PROJECTION REFERENCE - Reference to identity projection
# =============================================================================

@dataclass(frozen=True, slots=True)
class IdentityProjectionReference:
    """
    Immutable reference to an identity projection.
    
    The projection is owned by the Identity Capability and must not be mutated
    by this coordination layer.
    
    PROPERTIES:
        • revision_id: Revision identifier for the projection
        • captured_at_utc: When the projection was captured
        • confidence: Confidence in the projection's accuracy
        • completeness: How complete the projection is
        • source_authority: Authority that validated the projection
        • provenance: Where this projection came from
    """
    
    revision_id: str
    """Identity projection revision identifier."""
    
    captured_at_utc: datetime
    """When this identity projection was captured."""
    
    confidence: float = 1.0
    """Confidence in the projection's accuracy (0.0 to 1.0)."""
    
    completeness: float = 1.0
    """How complete the projection is (0.0 to 1.0)."""
    
    source_authority: str = "identity_authority"
    """Authority that validated this projection."""
    
    provenance: str = "canonical"
    """Provenance reference for the projection."""


# =============================================================================
# IDENTITY SOURCE REFERENCE - Reference to identity evidence source
# =============================================================================

@dataclass(frozen=True, slots=True)
class IdentitySourceReference:
    """
    Immutable reference to an identity evidence source.
    
    Every source must preserve:
        • Source ID (who generated it)
        • Source owner
        • Source revision (version number)
        • Authority level (how authoritative it is)
        • Factuality classification (what kind of statement it is)
        • Provenance tracking
    
    PROPERTIES:
        • source_id: Unique identifier for the source
        • source_owner: Owner of the source system
        • source_revision: Source revision at capture time
        • source_kind: What type of source (IdentitySourceKind.*)
        • factuality: Factuality classification (FactualityClassification.*)
        • authority: Authority level (AuthorityLevel.*)
        • captured_at_utc: When the source was captured
        • relevance: Relevance score to identity integration
        • privacy_classification: Privacy level of the source
    """
    
    source_id: str
    """Unique identifier for this source."""
    
    source_owner: str = ""
    """Owner of the source system (Identity, Memory, etc.)."""
    
    source_revision: int = 1
    """Source revision number at capture time."""
    
    source_kind: str  # IdentitySourceKind.*
    """What kind of source (IdentitySourceKind.*)."""
    
    factuality: str  # FactualityClassification.*
    """Factuality classification (what kind of statement this is)."""
    
    authority: str  # AuthorityLevel.*
    """Authority level that validated this source."""
    
    captured_at_utc: datetime
    """When this source was captured."""
    
    relevance: float = 1.0
    """Relevance score to identity integration (0.0 to 1.0)."""
    
    privacy_classification: str = "public"
    """Privacy classification of the source content."""


# =============================================================================
# IDENTITY INTEGRATION REQUEST - Main request type
# =============================================================================

@dataclass(frozen=True, slots=True)
class IdentityIntegrationRequest:
    """
    Immutable request to perform one bounded identity integration episode.
    
    The request is semantic - it contains references to data but does not
    contain live objects or runtime handles. It defines WHAT should be
    integrated, not HOW the integration should be implemented.
    
    PROPERTIES:
        • request_id: Unique identifier for this request
        • purpose: What kind of identity integration is being requested
        • subject: What identity components are being integrated
        • scope: Bounded constraints on the integration
        • context_id: Reference to InternalContext revision
        • context_revision: Context version at request time
        • identity_projection: Reference to current identity projection
        • source_references: References to evidence sources
        • expected_products: Which products are desired
        • completion_requirements: Success criteria
        • originating_episode_id: Parent episode if derived
        • originating_thought_ids: Thoughts that triggered this request
        • requested_by: Who/what made the request
        • correlation_id: For distributed tracing
        • causation_id: If results from another event
        • provenance: Where this request originated
    
    BOUNDEDNESS:
        Every limit is explicit. Overflow must be recorded.
    
    NOT RESPONSIBLE FOR:
        - Executing integration algorithms
        - Allocating runtime resources
        - Scheduling execution
        - Storing persistent results
    """
    
    # Identity and metadata
    request_id: IdentityIntegrationRequestId
    """Unique identifier for this request."""
    
    purpose: IdentityIntegrationPurpose
    """What kind of identity integration is being requested."""
    
    subject: IdentitySubject
    """What identity components are being integrated."""
    
    scope: IdentityIntegrationScope
    """Bounded constraints on the identity integration."""
    
    # Context binding
    context_id: InternalContextId
    """Reference to InternalContext revision."""
    
    context_revision: int = 1
    """Context version at request time."""
    
    # Identity projection reference (from Identity Capability)
    identity_projection: IdentityProjectionReference
    """Reference to current identity projection."""
    
    source_references: Tuple[IdentitySourceReference, ...] = field(default_factory=tuple)
    """References to evidence sources."""
    
    # Product expectations
    expected_products: FrozenSet[str] = field(default_factory=frozenset)
    """Product kinds expected from this integration."""
    
    completion_requirements: Tuple[str, ...] = field(default_factory=tuple)
    """Explicit conditions for successful completion."""
    
    # Origin tracking
    originating_episode_id: Optional[InternalEpisodeId] = None
    """ID of parent episode if derived from one."""
    
    originating_thought_ids: Tuple[InternalThoughtId, ...] = field(
        default_factory=tuple
    )
    """Thought IDs that triggered this request."""
    
    # Coordination metadata
    requested_by: str = "DEFAULT_NETWORK"
    """Who/what made the request (IdentityIntegrationRequester.*)."""
    
    correlation_id: CorrelationId = ""
    """Correlation ID for distributed tracing."""
    
    causation_id: Optional[CausationId] = None
    """Causation ID if this results from another event."""
    
    provenance: str = "canonical"
    """Provenance reference (where request type is documented)."""
    
    # Timestamps
    requested_at_utc: datetime = field(default_factory=datetime.utcnow)
    """When the request was created."""
    
    @classmethod
    def new(
        cls,
        purpose: IdentityIntegrationPurpose,
        subject: IdentitySubject,
        scope: IdentityIntegrationScope,
        context_id: str,
        identity_projection: IdentityProjectionReference,
        request_id: Optional[str] = None,
    ) -> IdentityIntegrationRequest:
        """
        Create a new identity integration request with default metadata.
        
        Args:
            purpose: The purpose of this identity integration
            subject: What identity components are being integrated
            scope: Bounded constraints on the integration
            context_id: Reference to the InternalContext revision
            identity_projection: Reference to current identity projection
            request_id: Optional explicit ID (auto-generated if None)
            
        Returns:
            New IdentityIntegrationRequest instance with valid metadata
        """
        return cls(
            request_id=request_id or f"identity_integration_request_{id(purpose)}",
            purpose=purpose,
            subject=subject,
            scope=scope,
            context_id=context_id,
            identity_projection=identity_projection,
            expected_products=frozenset(scope.permitted_product_kinds),
        )
    
    def can_produce_product(self, product_kind: str) -> bool:
        """Check if this request is allowed to produce a given product kind."""
        permitted = self.scope.permitted_product_kinds
        return not permitted or product_kind in permitted
    
    def exceeds_scope_limits(
        self,
        aspects_count: int,
        roles_count: int,
        values_count: int,
        commitments_count: int,
        capabilities_count: int,
        limitations_count: int,
        sources_count: int,
        evidence_count: int,
        products_count: int,
    ) -> Tuple[str, ...]:
        """
        Check if counts exceed scope limits.
        
        Args:
            aspects_count: Number of identity aspects collected
            roles_count: Number of roles identified
            values_count: Number of values identified
            commitments_count: Number of commitments identified
            capabilities_count: Number of capabilities assessed
            limitations_count: Number of limitations recorded
            sources_count: Number of source references used
            evidence_count: Number of evidence items collected
            products_count: Number of products generated
            
        Returns:
            List of exceeded limits (empty if within bounds)
        """
        violations = []
        
        if aspects_count > self.scope.maximum_identity_aspects:
            violations.append("identity_aspects_limit_exceeded")
        
        if roles_count > self.scope.maximum_roles:
            violations.append("roles_limit_exceeded")
        
        if values_count > self.scope.maximum_values:
            violations.append("values_limit_exceeded")
        
        if commitments_count > self.scope.maximum_commitments:
            violations.append("commitments_limit_exceeded")
        
        if capabilities_count > self.scope.maximum_capabilities:
            violations.append("capabilities_limit_exceeded")
        
        if limitations_count > self.scope.maximum_limitations:
            violations.append("limitations_limit_exceeded")
        
        if sources_count > self.scope.maximum_source_references:
            violations.append("source_references_limit_exceeded")
        
        if evidence_count > self.scope.maximum_evidence_items:
            violations.append("evidence_limit_exceeded")
        
        if products_count > self.scope.maximum_products_expected:
            violations.append("products_limit_exceeded")
        
        return tuple(violations)