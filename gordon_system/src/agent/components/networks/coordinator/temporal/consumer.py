# Gordon Cognitive Architecture - Phase 4.11.2
# ===========================================

"""
Coordination Consumer Models
============================

Canonical immutable models for consumer requests and views.

CONSUMER OVERVIEW
-----------------
Consumers access CoordinationState through published artifacts, never through
direct network access or partially constructed states. This reduces coupling
between coordinated networks.

CONSUMER INVARIANTS:
- Consumers only see fully published states
- Consumer views are filtered projections of the state
- Consumer requests specify requirements explicitly

VIEW INVARIANTS:
- Views remain policy-controlled and deterministic
- Views preserve relevant information for each consumer
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum, auto
from typing import Optional


# =============================================================================
# CONSUMER VIEW STATUS
# =============================================================================

class CoordinationStateViewStatus(Enum):
    """
    Canonical view statuses.
    
    VIEW-LAW-010: View construction shall remain deterministic
    
    STATUSES:
    - PENDING: View not yet constructed
    - GENERATED: View successfully generated
    - PARTIAL: Generated but with limited content
    - RESTRICTED: Consumer lacks required permissions
    """
    PENDING = "pending"
    """View not yet constructed."""
    
    GENERATED = "generated"
    """View successfully generated."""
    
    PARTIAL = "partial"
    """Generated but with limited content."""
    
    RESTRICTED = "restricted"
    """Consumer lacks required permissions."""
    
    UNKNOWN = "unknown"
    """View status unknown."""


# =============================================================================
# COORDINATION STATE CONSUMPTION REQUEST MODEL
# =============================================================================

@dataclass(frozen=True, slots=True)
class CoordinationStateConsumptionRequest:
    """
    Immutable consumer request for coordination state.
    
    CONSUMER-LAW-001: Consumers shall access Coordination through published
    state artifacts
    
    CONSUMER-LAW-005: Consumer limitation tolerance shall remain explicit
    
    COORD-CONSUME-INV-001: Request is immutable (deeply frozen)
    COORD-CONSUME-INV-002: Request has no runtime references
    """
    consumer_network_ref: str = ""
    """Reference to the requesting network."""
    
    required_epoch_ref: Optional[str] = None
    """Required epoch reference (optional)."""
    
    required_cycle_ref: Optional[str] = None
    """Required cycle reference (optional)."""
    
    required_domain: Optional[str] = None
    """Required coordination domain (optional)."""
    
    required_capabilities: tuple[str, ...] = ()
    """Required capabilities for this consumption."""
    
    minimum_compatibility: str = "compatible"
    """Minimum acceptable compatibility level."""
    
    accepted_limitations: tuple[str, ...] = ()
    """Limitations this consumer can tolerate."""
    
    semantic_context_ref: Optional[str] = None
    """Reference to semantic context."""
    
    provenance_ref: Optional[str] = None
    """Reference to request provenance record."""
    
    @classmethod
    def for_network(
        cls,
        network_ref: str,
        minimum_compatibility: str = "compatible",
    ) -> CoordinationStateConsumptionRequest:
        """
        Create a consumption request for a specific network.
        
        Args:
            network_ref: Reference to the requesting network
            minimum_compatibility: Minimum acceptable compatibility level
            
        Returns:
            A new CoordinationStateConsumptionRequest instance
        """
        return cls(
            consumer_network_ref=network_ref,
            minimum_compatibility=minimum_compatibility,
        )


# =============================================================================
# COORDINATION STATE VIEW MODEL
# =============================================================================

@dataclass(frozen=True, slots=True)
class CoordinationStateView:
    """
    Immutable filtered view of a coordination state.
    
    CONSUMER-LAW-007: Consumer access shall preserve provenance
    
    VIEW-LAW-001: Every Coordination State View shall reference one source
    Coordination State
    
    COORD-VIEW-INV-001: View is immutable (deeply frozen)
    COORD-VIEW-INV-002: View has no runtime references
    """
    view_identity: str = ""
    """Unique identifier for this view."""
    
    source_state_ref: Optional[str] = None
    """Reference to the source CoordinationState."""
    
    consumer_network_ref: str = ""
    """Reference to the consuming network."""
    
    permitted_projection_refs: tuple[str, ...] = ()
    """Projection references this consumer may see."""
    
    permitted_graph_regions: tuple[str, ...] = ()
    """Graph regions this consumer may access."""
    
    relevant_conflicts: tuple[str, ...] = ()
    """Conflicts relevant to this consumer."""
    
    relevant_constraints: tuple[str, ...] = ()
    """Constraints relevant to this consumer."""
    
    confidence: float = 0.5
    """Consumer's confidence in the view."""
    
    uncertainty: float = 0.5
    """Consumer's uncertainty about the view."""
    
    status: str = "pending"
    """View status (from CoordinationStateViewStatus)."""
    
    findings: tuple[str, ...] = ()
    """Findings about this view."""
    
    limitations: tuple[str, ...] = ()
    """Limitations on this view."""
    
    provenance_ref: Optional[str] = None
    """Reference to view provenance record."""
    
    @classmethod
    def from_state(
        cls,
        source_state_ref: str,
        consumer_network_ref: str,
        permitted_projections: tuple[str, ...],
        permitted_graphs: tuple[str, ...],
        confidence: float = 0.5,
        uncertainty: float = 0.5,
    ) -> CoordinationStateView:
        """
        Create a view from a coordination state.
        
        Args:
            source_state_ref: Reference to the source CoordinationState
            consumer_network_ref: Reference to consuming network
            permitted_projections: Projections this consumer may access
            permitted_graphs: Graph regions this consumer may access
            confidence: Consumer's confidence in the view
            uncertainty: Consumer's uncertainty about the view
            
        Returns:
            A new CoordinationStateView instance
        """
        return cls(
            view_identity=f"view:{source_state_ref}:{consumer_network_ref}",
            source_state_ref=source_state_ref,
            consumer_network_ref=consumer_network_ref,
            permitted_projection_refs=permitted_projections,
            permitted_graph_regions=permitted_graphs,
            confidence=confidence,
            uncertainty=uncertainty,
            status="generated",
        )
    
    def with_limitations(
        self,
        limitations: tuple[str, ...],
    ) -> CoordinationStateView:
        """
        Create a new view with additional limitations.
        
        Args:
            limitations: Limitation descriptions
            
        Returns:
            A new CoordinationStateView instance
        """
        return CoordinationStateView(
            view_identity=self.view_identity,
            source_state_ref=self.source_state_ref,
            consumer_network_ref=self.consumer_network_ref,
            permitted_projection_refs=self.permitted_projection_refs,
            permitted_graph_regions=self.permitted_graph_regions,
            relevant_conflicts=self.relevant_conflicts,
            relevant_constraints=self.relevant_constraints,
            confidence=max(0.0, self.confidence - 0.1),
            uncertainty=min(1.0, self.uncertainty + 0.1),
            status="partial",
            findings=self.findings + limitations,
            limitations=limitations + self.limitations,
            provenance_ref=self.provenance_ref,
        )


# =============================================================================
# STATE PUBLICATION MODEL
# =============================================================================

@dataclass(frozen=True, slots=True)
class CoordinationStatePublication:
    """
    Immutable state publication model.
    
    STATE-PUBLICATION-LAW-001: Only validated Coordination States may be published
    
    STATE-PUBLICATION-LAW-006: Published states shall remain immutable
    
    COORD-PUBLISH-INV-001: Publication is immutable (deeply frozen)
    COORD-PUBLISH-INV-002: Publication has no runtime references
    """
    publication_identity: str = ""
    """Unique identifier for this publication."""
    
    epoch_ref: Optional[str] = None
    """Reference to the parent coordination epoch."""
    
    cycle_ref: Optional[str] = None
    """Reference to the source coordination cycle."""
    
    state_ref: Optional[str] = None
    """Reference to the published CoordinationState."""
    
    publication_status: str = "pending"
    """Publication status (from StatePublicationStatus)."""
    
    consumer_scope: tuple[str, ...] = ()
    """Networks that may consume this publication."""
    
    replaces_state_ref: Optional[str] = None
    """Reference to state this replaces (if any)."""
    
    confidence: float = 0.5
    """Confidence in the published state."""
    
    uncertainty: float = 0.5
    """Uncertainty about the published state."""
    
    findings: tuple[str, ...] = ()
    """Findings from validation."""
    
    limitations: tuple[str, ...] = ()
    """Limitations on this publication."""
    
    semantic_time_ref: Optional[str] = None
    """Reference to semantic time at publication."""
    
    provenance_ref: Optional[str] = None
    """Reference to publication provenance record."""
    
    @classmethod
    def publish_state(
        cls,
        state_ref: str,
        cycle_ref: str,
        epoch_ref: Optional[str] = None,
        consumer_scope: tuple[str, ...] = (),
        confidence: float = 1.0,
        uncertainty: float = 0.0,
    ) -> CoordinationStatePublication:
        """
        Create a state publication.
        
        Args:
            state_ref: Reference to the published CoordinationState
            cycle_ref: Reference to source coordination cycle
            epoch_ref: Reference to parent epoch (optional)
            consumer_scope: Networks that may consume this
            confidence: Confidence in the state
            uncertainty: Uncertainty about the state
            
        Returns:
            A new CoordinationStatePublication instance
        """
        return cls(
            publication_identity=f"pub:{state_ref}",
            epoch_ref=epoch_ref,
            cycle_ref=cycle_ref,
            state_ref=state_ref,
            publication_status="published",
            consumer_scope=consumer_scope,
            confidence=confidence,
            uncertainty=uncertainty,
        )
    
    def with_limitations(
        self,
        limitations: tuple[str, ...],
    ) -> CoordinationStatePublication:
        """
        Create a publication with known limitations.
        
        Args:
            limitations: Limitation descriptions
            
        Returns:
            A new CoordinationStatePublication instance
        """
        return CoordinationStatePublication(
            publication_identity=self.publication_identity,
            epoch_ref=self.epoch_ref,
            cycle_ref=self.cycle_ref,
            state_ref=self.state_ref,
            publication_status="published_with_limitations",
            consumer_scope=self.consumer_scope,
            replaces_state_ref=self.replaces_state_ref,
            confidence=max(0.0, self.confidence - 0.1),
            uncertainty=min(1.0, self.uncertainty + 0.1),
            findings=self.findings + limitations,
            limitations=limitations + self.limitations,
            semantic_time_ref=self.semantic_time_ref,
            provenance_ref=self.provenance_ref,
        )


# =============================================================================
# STATE PUBLICATION STATUS ENUM
# =============================================================================

class StatePublicationStatus(Enum):
    """
    Canonical publication statuses.
    
    STATUSES:
    - PENDING: Not yet published
    - PUBLISHED: Published without issues
    - PUBLISHED_WITH_LIMITATIONS: Published but with known limitations
    - WITHHELD: Publication withheld due to validation failure
    - SUPERSEDED: Superseded by newer publication
    """
    PENDING = "pending"
    """Not yet published."""
    
    PUBLISHED = "published"
    """Published without issues."""
    
    PUBLISHED_WITH_LIMITATIONS = "published_with_limitations"
    """Published but with known limitations."""
    
    WITHHELD = "withheld"
    """Publication withheld due to validation failure."""
    
    SUPERSEDED = "superseded"
    """Superseded by newer publication."""
    
    UNKNOWN = "unknown"
    """Publication status unknown."""


# =============================================================================
# CONSUMER VIEW BUILDER
# =============================================================================

@dataclass(frozen=True, slots=True)
class CoordinationStateViewBuilder:
    """
    Immutable builder for consumer views.
    
    CONSUMER-VIEW-BUILDER-INV-001: Builder is deterministic
    
    Inputs:
    - Source CoordinationState
    - Consumer request
    - Policy
    
    Output: CoordinationStateView
    """
    
    @classmethod
    def build_view(
        cls,
        state_ref: str,
        consumer_request: CoordinationStateConsumptionRequest,
        permitted_projections: tuple[str, ...],
        permitted_graphs: tuple[str, ...],
    ) -> CoordinationStateView:
        """
        Build a view for a consumer request.
        
        Args:
            state_ref: Reference to source CoordinationState
            consumer_request: The consumption request
            permitted_projections: Projections this consumer may see
            permitted_graphs: Graph regions this consumer may access
            
        Returns:
            A new CoordinationStateView instance
        """
        return CoordinationStateView(
            view_identity=f"view:{state_ref}:{consumer_request.consumer_network_ref}",
            source_state_ref=state_ref,
            consumer_network_ref=consumer_request.consumer_network_ref,
            permitted_projection_refs=permitted_projections,
            permitted_graph_regions=permitted_graphs,
            confidence=0.5,
            uncertainty=0.5,
            status="generated",
        )