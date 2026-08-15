# Workspace Integration Request Models
# =====================================

"""
Immutable request models for workspace integration.

ARCHITECTURAL PRINCIPLES:
    - All dataclasses are frozen (deeply immutable)
    - No runtime dependencies (no imports from Core or Execution)
    - Bounded by explicit limits
    - Semantic content only (no live objects)
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Tuple, Optional, FrozenSet
from datetime import datetime


# =============================================================================
# ID TYPES
# =============================================================================

WorkspaceIntegrationRequestId = str
"""Unique identifier for a workspace integration request."""


# =============================================================================
# WORKSPACE INTEGRATION PURPOSE
# =============================================================================

@dataclass(frozen=True, slots=True)
class WorkspaceIntegrationPurpose:
    """
    Immutable description of the workspace integration purpose.
    
    Purpose defines what the integration is trying to accomplish without
    embedding runtime implementation details.
    
    PROPERTIES:
        • kind: Canonical purpose category (WorkspaceIntegrationPurposeKind.*)
        • statement: Human-readable description
        • expected_products: Which products are desired
        • allowed_source_kinds: Source kinds that may be used
        • completion_rules: Conditions for successful completion
        • recursion_limit: Maximum recursion depth if applicable
    """
    
    kind: str  # WorkspaceIntegrationPurposeKind.*
    """The canonical purpose category."""
    
    statement: str = ""
    """Human-readable description of what this integration does."""
    
    expected_products: Tuple[str, ...] = field(default_factory=tuple)
    """Product kinds this purpose is allowed to produce."""
    
    allowed_source_kinds: Tuple[str, ...] = field(default_factory=tuple)
    """Source product kinds that may be referenced."""
    
    completion_rules: Tuple[str, ...] = field(default_factory=tuple)
    """Conditions that must be met for successful completion."""
    
    recursion_limit: int = 3
    """Maximum recursive integration depth."""
    
    @classmethod
    def prepare_candidate(cls) -> WorkspaceIntegrationPurpose:
        """Create a candidate preparation purpose."""
        return cls(
            kind="prepare_candidate",
            statement="Prepare a workspace candidate from internal content",
            expected_products=("workspace_candidate", "submission_proposal"),
            allowed_source_kinds=(
                "internal_thought",
                "reflection",
                "simulation",
                "narrative",
                "identity",
                "memory",
                "prediction",
            ),
        )
    
    @classmethod
    def revise_candidate(cls, target_candidate_id: str) -> WorkspaceIntegrationPurpose:
        """Create a candidate revision purpose."""
        return cls(
            kind="revise_candidate",
            statement=f"Revise workspace candidate {target_candidate_id}",
            expected_products=("workspace_candidate",),
            allowed_source_kinds=(),
        )
    
    @classmethod
    def process_admission_decision(cls, decision_kind: str) -> WorkspaceIntegrationPurpose:
        """Create an admission decision processing purpose."""
        return cls(
            kind="process_admission_decision",
            statement=f"Process {decision_kind} admission decision",
            expected_products=("outcome", "continuation"),
            allowed_source_kinds=(),
        )


# =============================================================================
# WORKSPACE INTEGRATION SUBJECT
# =============================================================================

@dataclass(frozen=True, slots=True)
class WorkspaceIntegrationSubject:
    """
    Immutable description of the workspace integration subject.
    
    Subject defines what is being proposed to the workspace without embedding
    live objects or full data structures.
    
    PROPERTIES:
        • kind: Canonical subject category (WorkspaceIntegrationSubjectKind.*)
        • subject_id: ID reference to the subject entity
        • summary: Brief description of the subject
        • source_revision: Revision number at time of integration
        • artifact_references: References to relevant artifacts
    """
    
    kind: str  # WorkspaceIntegrationSubjectKind.*
    """The canonical subject category."""
    
    subject_id: Optional[str] = None
    """ID reference to the subject entity (if applicable)."""
    
    summary: str = ""
    """Brief description of what is being integrated."""
    
    source_revision: int = 1
    """Source system revision number at integration start."""
    
    artifact_references: Tuple[str, ...] = field(default_factory=tuple)
    """References to relevant artifacts (thought IDs, etc.)."""
    
    @classmethod
    def internal_thought(cls, thought_id: str) -> WorkspaceIntegrationSubject:
        """Create a subject for an InternalThought."""
        return cls(
            kind="internal_thought",
            subject_id=thought_id,
            summary=f"InternalThought {thought_id}",
        )
    
    @classmethod
    def reflection_product(cls, product_id: str) -> WorkspaceIntegrationSubject:
        """Create a subject for a reflection product."""
        return cls(
            kind="reflective_product",
            subject_id=product_id,
            summary=f"ReflectiveProduct {product_id}",
        )
    
    @classmethod
    def concern(cls, description: str = "") -> WorkspaceIntegrationSubject:
        """Create a subject for an internally generated concern."""
        return cls(
            kind="concern",
            summary=description or "Internally generated concern",
        )


# =============================================================================
# WORKSPACE INTEGRATION SCOPE
# =============================================================================

@dataclass(frozen=True, slots=True)
class WorkspaceIntegrationScope:
    """
    Immutable scope constraints for a workspace integration episode.
    
    Scope prevents one integration from becoming unbounded by imposing
    explicit limits on resources and evidence.
    
    PROPERTIES:
        • maximum_source_products: Hard limit on source product references
        • maximum_candidates: Max candidates to prepare
        • maximum_content_references: Max content references per candidate
        • maximum_evidence_references: Max evidence references
        • maximum_audiences: Max audience recommendations
        • maximum_conflicts: Max conflict references
        • required_confidence: Minimum confidence threshold
    """
    
    # Source product limits
    maximum_source_products: int = 20
    """Maximum source products that may be referenced."""
    
    maximum_candidates: int = 5
    """Maximum candidates to prepare per episode."""
    
    maximum_content_references: int = 100
    """Maximum content references per candidate."""
    
    maximum_evidence_references: int = 50
    """Maximum evidence references per candidate."""
    
    # Assessment limits
    maximum_audiences: int = 10
    """Maximum audience recommendations."""
    
    maximum_conflicts: int = 20
    """Maximum conflict references."""
    
    maximum_duplicates: int = 10
    """Maximum duplicate assessments."""
    
    # Quality thresholds
    required_confidence: float = 0.5
    """Minimum confidence threshold for candidates."""
    
    minimum_value: float = 0.3
    """Minimum recommended value threshold."""
    
    require_factuality: bool = True
    """If true, candidates must have factuality assessed."""
    
    # Recurrence limits
    maximum_admission_attempts: int = 3
    """Maximum admission attempts for same candidate."""
    
    maximum_resubmissions: int = 2
    """Maximum resubmissions after rejection."""
    
    maximum_deferrals: int = 2
    """Maximum deferrals before requiring revision."""
    
    @classmethod
    def surface_level(cls) -> WorkspaceIntegrationScope:
        """Create a scope for shallow integration."""
        return cls(
            maximum_source_products=10,
            maximum_candidates=2,
            maximum_content_references=30,
            maximum_evidence_references=15,
            maximum_audiences=5,
            required_confidence=0.6,
        )
    
    @classmethod
    def standard_level(cls) -> WorkspaceIntegrationScope:
        """Create a scope for normal integration."""
        return cls(
            maximum_source_products=20,
            maximum_candidates=5,
            maximum_content_references=100,
            maximum_evidence_references=50,
            maximum_audiences=10,
            required_confidence=0.5,
        )
    
    @classmethod
    def deep_level(cls) -> WorkspaceIntegrationScope:
        """Create a scope for thorough integration."""
        return cls(
            maximum_source_products=50,
            maximum_candidates=10,
            maximum_content_references=200,
            maximum_evidence_references=100,
            maximum_audiences=20,
            required_confidence=0.7,
        )


# =============================================================================
# WORKSPACE SOURCE PRODUCT REFERENCE
# =============================================================================

@dataclass(frozen=True, slots=True)
class WorkspaceSourceProductReference:
    """
    Immutable reference to a source product that may be used by a candidate.
    
    Every reference must preserve origin information without embedding live
    objects or full data structures.
    
    PROPERTIES:
        • kind: Source product kind (WorkspaceSourceProductKind.*)
        • product_id: ID reference to the source product
        • source_owner: Owner of the source system
        • source_revision: Revision at time of integration
        • factuality: Factuality assessment (optional)
        • confidence: Confidence in the source (0.0 to 1.0)
        • privacy: Privacy classification
    """
    
    kind: str  # WorkspaceSourceProductKind.*
    """The source product kind."""
    
    product_id: str
    """ID reference to the source product."""
    
    source_owner: str = "DEFAULT_NETWORK"
    """Owner of the source system."""
    
    source_revision: int = 1
    """Revision at time of integration."""
    
    factuality: Optional[str] = None
    """Factuality assessment (if available)."""
    
    confidence: float = 0.5
    """Confidence in the source (0.0 to 1.0)."""
    
    privacy: str = "internal"
    """Privacy classification."""
    
    artifact_reference: Optional[str] = None
    """Optional artifact reference (file, memory ID, etc.)."""
    
    @classmethod
    def internal_thought(
        cls,
        thought_id: str,
        confidence: float = 0.5,
        factuality: Optional[str] = None,
    ) -> WorkspaceSourceProductReference:
        """Create a reference to an InternalThought."""
        return cls(
            kind="internal_thought",
            product_id=thought_id,
            source_owner="DEFAULT_NETWORK",
            confidence=confidence,
            factuality=factuality,
        )
    
    @classmethod
    def reflection_product(
        cls,
        product_id: str,
        confidence: float = 0.5,
    ) -> WorkspaceSourceProductReference:
        """Create a reference to a reflection product."""
        return cls(
            kind="reflection",
            product_id=product_id,
            source_owner="DEFAULT_NETWORK",
            confidence=confidence,
        )


# =============================================================================
# WORKSPACE INTEGRATION REQUEST
# =============================================================================

@dataclass(frozen=True, slots=True)
class WorkspaceIntegrationRequest:
    """
    Immutable request to perform one bounded workspace integration episode.
    
    The request is semantic - it contains references to data but does not
    contain live objects or runtime handles. It defines WHAT should be
    integrated, not HOW the integration should be implemented.
    
    PROPERTIES:
        • request_id: Unique identifier for this request
        • purpose: What kind of integration is being requested
        • subject: What is being integrated
        • scope: Bounded constraints on the integration
        • context_id: Reference to InternalContext revision
        • context_revision: Context version at request time
        • source_product_references: Source products that may be used
        • existing_candidate_references: Existing candidates to consider
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
    request_id: WorkspaceIntegrationRequestId
    """Unique identifier for this request."""
    
    purpose: WorkspaceIntegrationPurpose
    """What kind of integration is being requested."""
    
    subject: WorkspaceIntegrationSubject
    """What is being integrated."""
    
    scope: WorkspaceIntegrationScope
    """Bounded constraints on the integration."""
    
    # Context binding
    context_id: str
    """Reference to InternalContext revision."""
    
    context_revision: int = 1
    """Context version at request time."""
    
    # Origin tracking
    originating_episode_id: Optional[str] = None
    """ID of parent episode if derived from one."""
    
    originating_thought_ids: Tuple[str, ...] = field(default_factory=tuple)
    """Thought IDs that triggered this request."""
    
    # Product expectations
    expected_products: FrozenSet[str] = field(default_factory=frozenset)
    """Product kinds expected from this integration."""
    
    completion_requirements: Tuple[str, ...] = field(default_factory=tuple)
    """Explicit conditions for successful completion."""
    
    # Coordination metadata
    requested_by: str = "DEFAULT_NETWORK"
    """Who/what made the request (WorkspaceIntegrationRequester.*)."""
    
    correlation_id: str = ""
    """Correlation ID for distributed tracing."""
    
    causation_id: Optional[str] = None
    """Causation ID if this results from another event."""
    
    provenance: str = "canonical"
    """Provenance reference (where request type is documented)."""
    
    # Timestamps
    requested_at_utc: datetime = field(default_factory=datetime.utcnow)
    """When the request was created."""
    
    @classmethod
    def new(
        cls,
        purpose: WorkspaceIntegrationPurpose,
        subject: WorkspaceIntegrationSubject,
        scope: WorkspaceIntegrationScope,
        context_id: str,
        request_id: Optional[str] = None,
    ) -> WorkspaceIntegrationRequest:
        """
        Create a new workspace integration request with default metadata.
        
        Args:
            purpose: The purpose of this integration
            subject: What is being integrated
            scope: Bounded constraints on the integration
            context_id: Reference to the InternalContext revision
            request_id: Optional explicit ID (auto-generated if None)
            
        Returns:
            New WorkspaceIntegrationRequest instance with valid metadata
        """
        return cls(
            request_id=request_id or f"workspace_integration_{id(purpose)}",
            purpose=purpose,
            subject=subject,
            scope=scope,
            context_id=context_id,
            expected_products=frozenset(scope.allowed_source_kinds),
        )
    
    def can_produce_product(self, product_kind: str) -> bool:
        """Check if this request is allowed to produce a given product kind."""
        return product_kind in self.expected_products
    
    def exceeds_scope_limits(
        self,
        source_count: int,
        candidate_count: int,
        evidence_count: int,
    ) -> Tuple[str, ...]:
        """
        Check if counts exceed scope limits.
        
        Args:
            source_count: Number of source products referenced
            candidate_count: Number of candidates prepared
            evidence_count: Number of evidence references
            
        Returns:
            List of exceeded limits (empty if within bounds)
        """
        violations = []
        if source_count > self.scope.maximum_source_products:
            violations.append("source_limit_exceeded")
        if candidate_count > self.scope.maximum_candidates:
            violations.append("candidate_limit_exceeded")
        if evidence_count > self.scope.maximum_evidence_references:
            violations.append("evidence_limit_exceeded")
        return tuple(violations)