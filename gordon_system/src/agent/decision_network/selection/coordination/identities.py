# Gordon Cognitive Architecture - Phase 4.5.10
# ===========================================

"""
Coordination Identity, Revision, Reference, Correlation, and Causation Types.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import NewType
import uuid


# =============================================================================
# CANONICAL SCHEMA VERSION
# =============================================================================

ActionSelectionCoordinationSchemaVersion = str
"""Canonical schema version for coordination contracts."""


# =============================================================================
# COORDINATION IDENTITIES
# =============================================================================

@dataclass(frozen=True)
class ActionSelectionCoordinationIdentity:
    """
    Unique identifier for a coordination lifecycle.
    
    Every coordination request-response cycle has one stable identity that
    persists through revisions when the purpose remains the same.
    """
    
    value: str = field(default_factory=lambda: f"coord_{uuid.uuid4().hex[:16]}")
    """Unique coordination identifier."""
    
    @classmethod
    def from_value(cls, value: str) -> ActionSelectionCoordinationIdentity:
        """Create identity from an explicit string value."""
        return cls(value=value)
    
    @classmethod
    def from_request_id(cls, request_id: str) -> ActionSelectionCoordinationIdentity:
        """Create coordination identity from a request identifier."""
        return cls(value=f"coord_{request_id}")


@dataclass(frozen=True)
class ActionSelectionCoordinationRevision:
    """
    Revision number for a coordination artifact.
    
    Monotonically increasing revision tracking preserves history while allowing
    updates. Revisions are distinct from state revisions and subsystem revisions.
    """
    
    value: int = 1
    """Monotonically increasing revision number."""
    
    @classmethod
    def initial(cls) -> ActionSelectionCoordinationRevision:
        """Create the initial (first) coordination revision."""
        return cls(value=1)
    
    @classmethod
    def next(cls, current: ActionSelectionCoordinationRevision) -> ActionSelectionCoordinationRevision:
        """Get the next revision number."""
        return cls(value=current.value + 1)


# =============================================================================
# COORDINATION REFERENCES
# =============================================================================

@dataclass(frozen=True)
class ActionSelectionCoordinationReference:
    """
    Reference to a specific coordination artifact revision.
    
    Combines identity and revision to reference an exact coordination artifact.
    """
    
    identity: ActionSelectionCoordinationIdentity
    """The coordination identity being referenced."""
    
    revision: ActionSelectionCoordinationRevision = field(default_factory=ActionSelectionCoordinationRevision.initial)
    """The revision of that identity."""
    
    @classmethod
    def initial(cls) -> ActionSelectionCoordinationReference:
        """Create a reference to the initial coordination artifact."""
        return cls(
            identity=ActionSelectionCoordinationIdentity(),
            revision=ActionSelectionCoordinationRevision.initial()
        )


# =============================================================================
# STATE REFERENCES
# =============================================================================

@dataclass(frozen=True)
class ActionSelectionStateReference:
    """
    Reference to an exact Action Selection State revision.
    
    Every coordination request must reference exactly one Action Selection State
    revision. This ensures responses can be validated against the expected state.
    """
    
    identity: str = ""
    """Action Selection State identity."""
    
    revision: int = 1
    """Exact state revision number."""
    
    @classmethod
    def from_state(cls, identity: str, revision: int) -> ActionSelectionStateReference:
        """Create a state reference from explicit values."""
        return cls(identity=identity, revision=revision)


@dataclass(frozen=True)
class ActionSelectionArtifactReference:
    """
    Reference to an Action Selection artifact (candidate, action, selected_action).
    
    Used in coordination to reference artifacts without embedding them.
    """
    
    artifact_type: str = ""  # e.g., "candidate", "action", "selected_action"
    """Type of the referenced artifact."""
    
    identity: str = ""
    """Artifact identity."""
    
    revision: int = 1
    """Artifact revision number."""
    
    @classmethod
    def candidate(cls, identity: str, revision: int) -> ActionSelectionArtifactReference:
        """Create a candidate reference."""
        return cls(artifact_type="candidate", identity=identity, revision=revision)
    
    @classmethod
    def action(cls, identity: str, revision: int) -> ActionSelectionArtifactReference:
        """Create an action reference."""
        return cls(artifact_type="action", identity=identity, revision=revision)
    
    @classmethod
    def selected_action(cls, identity: str, revision: int) -> ActionSelectionArtifactReference:
        """Create a selected action reference."""
        return cls(artifact_type="selected_action", identity=identity, revision=revision)


# =============================================================================
# EXTERNAL SUBSYSTEM REFERENCES
# =============================================================================

@dataclass(frozen=True)
class ExternalSubsystemOwnerReference:
    """
    Reference to an external subsystem owner.
    
    Identifies the owner of a subsystem without embedding implementation details.
    """
    
    subsystem_kind: str = ""  # e.g., "executive", "planning", "policy"
    """External subsystem kind."""
    
    owner_identity: str = ""
    """Owner identity (for multi-instance subsystems)."""
    
    @classmethod
    def from_kind(cls, subsystem_kind: str) -> ExternalSubsystemOwnerReference:
        """Create a reference from subsystem kind only."""
        return cls(subsystem_kind=subsystem_kind)
    
    @classmethod
    def full_ref(
        cls,
        subsystem_kind: str,
        owner_identity: str
    ) -> ExternalSubsystemOwnerReference:
        """Create a full reference with both subsystem and owner."""
        return cls(subsystem_kind=subsystem_kind, owner_identity=owner_identity)


@dataclass(frozen=True)
class ExternalProductReference:
    """
    Reference to an external product artifact.
    
    References external artifacts produced in response to coordination requests.
    """
    
    product_type: str = ""  # e.g., "plan", "policy_review", "capability_projection"
    """Type of external product."""
    
    identity: str = ""
    """Product identity."""
    
    revision: int = 1
    """Product revision number."""
    
    @classmethod
    def from_kind(cls, product_type: str, identity: str, revision: int) -> ExternalProductReference:
        """Create a reference from explicit values."""
        return cls(product_type=product_type, identity=identity, revision=revision)


# =============================================================================
# CORRELATION IDENTITIES
# =============================================================================

@dataclass(frozen=True)
class ActionSelectionCorrelationId:
    """
    Unique identifier for correlation between coordination artifacts.
    
    Correlation links requests, responses, acknowledgements, and integration records
    without implying causation. Two artifacts may share a correlation context
    without one causing the other.
    """
    
    value: str = field(default_factory=lambda: f"corr_{uuid.uuid4().hex[:16]}")
    """Unique correlation identifier."""
    
    @classmethod
    def from_request_and_response(
        cls,
        request_id: ActionSelectionCoordinationIdentity,
        response_id: ActionSelectionCoordinationResponseIdentity
    ) -> ActionSelectionCorrelationId:
        """Create a correlation ID from request and response references."""
        return cls(value=f"corr_{request_id.value}_{response_id.value}")


@dataclass(frozen=True)
class ActionSelectionCorrelationReference:
    """
    Reference to a correlation context.
    
    Preserves the exact correlation identity and revision for traceability.
    """
    
    correlation_id: ActionSelectionCorrelationId
    """The correlation identifier."""
    
    revision: int = 1
    """Correlation reference revision (for updates)."""
    
    @classmethod
    def from_id(cls, correlation_id: ActionSelectionCorrelationId) -> ActionSelectionCorrelationReference:
        """Create a correlation reference from a correlation ID."""
        return cls(correlation_id=correlation_id)


# =============================================================================
# CAUSATION REFERENCES
# =============================================================================

@dataclass(frozen=True)
class ActionSelectionCausationRelation:
    """
    Causal relation between coordination artifacts.
    
    Defines the semantic cause-effect relationships between coordination artifacts.
    Correlation and causation are distinct - two artifacts may be correlated without
    one causing the other.
    """
    
    kind: str = "UNKNOWN"  # See CAUSATION_KINDS for valid values
    """Causal relation kind."""
    
    @classmethod
    def requested_by_state(cls) -> ActionSelectionCausationRelation:
        """The request was requested by state."""
        return cls(kind="REQUESTED_BY_STATE")
    
    @classmethod
    def responds_to_request(cls) -> ActionSelectionCausationRelation:
        """The response responds to the request."""
        return cls(kind="RESPONDS_TO_REQUEST")
    
    @classmethod
    def acknowledges_response(cls) -> ActionSelectionCausationRelation:
        """The acknowledgement acknowledges the response."""
        return cls(kind="ACKNOWLEDGES_RESPONSE")
    
    @classmethod
    def integrated_by_delta(cls) -> ActionSelectionCausationRelation:
        """The integration was derived from delta."""
        return cls(kind="INTEGRATED_BY_DELTA")
    
    @classmethod
    def produced_by_transition(cls) -> ActionSelectionCausationRelation:
        """The transition was produced by the integration."""
        return cls(kind="PRODUCES_TRANSITION")


@dataclass(frozen=True)
class ActionSelectionCausationReference:
    """
    Reference to a causation relation.
    
    Preserves exact causal relationships between coordination artifacts.
    """
    
    source_artifact: str = ""  # e.g., "request", "response", "acknowledgement"
    """Type of source artifact."""
    
    source_identity: str = ""
    """Source artifact identity."""
    
    source_revision: int = 1
    """Source artifact revision."""
    
    relation: ActionSelectionCausationRelation = field(default_factory=ActionSelectionCausationRelation)
    """The causal relation to this artifact."""
    
    target_artifact: str = ""  # e.g., "response", "acknowledgement", "integration"
    """Type of target artifact."""
    
    target_identity: str = ""
    """Target artifact identity."""
    
    @classmethod
    def from_request_to_response(
        cls,
        request_ref: ActionSelectionCoordinationReference,
        response_id: ActionSelectionCoordinationResponseIdentity
    ) -> ActionSelectionCausationReference:
        """Create a causation reference from request to its response."""
        return cls(
            source_artifact="request",
            source_identity=request_ref.identity.value,
            source_revision=request_ref.revision.value,
            relation=ActionSelectionCausationRelation.responds_to_request(),
            target_artifact="response",
            target_identity=response_id.value
        )


# =============================================================================
# CANONICAL CAUSATION KINDS
# =============================================================================

CAUSATION_KINDS = frozenset({
    "REQUESTED_BY_STATE",
    "REQUESTED_BY_CONTINUATION",
    "RESPONDS_TO_REQUEST",
    "ACKNOWLEDGES_RESPONSE",
    "INTEGRATED_BY_DELTA",
    "PRODUCES_TRANSITION",
    "INVALIDATES_COORDINATION",
    "SUPERSEDES_COORDINATION",
    "DERIVED_FROM_PROJECTION",
    "PROJECTED_FROM_STATE",
    "PROJECTED_FROM_SELECTED_ACTION",
    "RESPONDED_TO_BY_EXECUTION",
    "UNKNOWN",
})