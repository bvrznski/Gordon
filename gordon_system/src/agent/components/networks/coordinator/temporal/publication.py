# Gordon Cognitive Architecture - Phase 4.11.2
# ===========================================

"""
Coordination Publication Models
===============================

Canonical immutable models for publication windows and projections.

PUBLICATION OVERVIEW
--------------------
The publication window defines when networks may publish projections.
Outside the window, working state may continue evolving, but published
projections remain stable.

PUBLICATION STAGES:
- Open Publication (window open)
- Projection accepted (validation passes)
- Window closes (no more changes)
- Synchronization (consumes accepted projections)
- CoordinationState constructed
- Publication complete

PUBLICATION INVARIANTS
======================
- Accepted projections remain immutable after window closure
- Working state continues evolving outside publication window
- No projection modifications after closure without new cycle
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum, auto
from typing import Optional


# =============================================================================
# PUBLICATION WINDOW STATUS
# =============================================================================

class PublicationWindowStatus(Enum):
    """
    Canonical status enumeration for publication windows.
    
    WINDOW-LAW-010: Window ordering shall remain deterministic
    
    STATES:
    - PENDING: Window not yet opened
    - OPEN: Accepting projections
    - CLOSING: Closing window (no new accepts)
    - CLOSED: Window closed, frozen state
    - INVALID: Window is invalid
    - SUPERSEDED: Window superseded by newer one
    """
    PENDING = "pending"
    """Window not yet opened."""
    
    OPEN = "open"
    """Accepting projections."""
    
    CLOSING = "closing"
    """Closing window, no new accepts."""
    
    CLOSED = "closed"
    """Window closed, frozen state."""
    
    INVALID = "invalid"
    """Window is invalid."""
    
    SUPERSEDED = "superseded"
    """Window superseded by newer one."""
    
    UNKNOWN = "unknown"
    """Window status cannot be determined."""


# =============================================================================
# PROJECTION PUBLICATION INTENTION
# =============================================================================

class ProjectionPublicationIntention(Enum):
    """
    Canonical publication intentions.
    
    PUBLICATION-INTENTION-INV-001: Intention is immutable once set
    
    INTENTIONS:
    - NEW: Newly produced projection
    - REPLACE: Replace previous projection
    - REUSE: Reuse existing projection (unchanged)
    - WITHDRAW: Withdraw from participation
    - CORRECT: Correct a previous publication
    - CONFIRM_UNCHANGED: Confirm no change
    - DEFER: Defer to next cycle
    """
    NEW = "new"
    """Identifies a newly produced projection."""
    
    REPLACE = "replace"
    """Replaces the referenced previous projection."""
    
    REUSE = "reuse"
    """Reuses existing projection (unchanged)."""
    
    WITHDRAW = "withdraw"
    """Withdraws from participation in this cycle."""
    
    CORRECT = "correct"
    """Corrects a previous publication."""
    
    CONFIRM_UNCHANGED = "confirm_unchanged"
    """Confirms no change to previous state."""
    
    DEFER = "defer"
    """Defers participation to next cycle."""
    
    UNKNOWN = "unknown"
    """Publication intention cannot be determined."""


# =============================================================================
# PROJECTION ACCEPTANCE STATUS
# =============================================================================

class ProjectionAcceptanceStatus(Enum):
    """
    Canonical acceptance statuses.
    
    ACCEPTANCE-INV-001: Acceptance status is immutable once set
    
    STATUSES:
    - ACCEPTED: Accepted without issues
    - ACCEPTED_WITH_LIMITATIONS: Accepted but with known limitations
    - REUSED: Reused existing projection (unchanged)
    - DEFERRED: Deferred to next cycle
    - REJECTED: Rejected due to validation failure
    - STALE: Projection is stale (outdated)
    - INCOMPATIBLE: Incompatible with current policy
    """
    ACCEPTED = "accepted"
    """Accepted without issues."""
    
    ACCEPTED_WITH_LIMITATIONS = "accepted_with_limitations"
    """Accepted but with known limitations."""
    
    REUSED = "reused"
    """Reused existing projection (unchanged)."""
    
    DEFERRED = "deferred"
    """Deferred to next cycle."""
    
    REJECTED = "rejected"
    """Rejected due to validation failure."""
    
    STALE = "stale"
    """Projection is stale (outdated)."""
    
    INCOMPATIBLE = "incompatible"
    """Incompatible with current policy."""
    
    UNKNOWN = "unknown"
    """Acceptance status cannot be determined."""


# =============================================================================
# PROJECTION ACCEPTANCE MODEL
# =============================================================================

@dataclass(frozen=True, slots=True)
class ProjectionAcceptance:
    """
    Immutable result of projection acceptance.
    
    ACCEPTANCE-LAW-001: Every Projection Publication shall produce exactly one
    Projection Acceptance result
    
    ACCEPTANCE-LAW-002: Acceptance status shall remain explicit
    
    COORD-ACCEPTANCE-INV-001: Acceptance is immutable (deeply frozen)
    COORD-ACCEPTANCE-INV-002: Acceptance has no runtime references
    """
    publication_ref: str = ""
    """Reference to the accepted projection publication."""
    
    status: str = "unknown"
    """Acceptance status (from ProjectionAcceptanceStatus)."""
    
    effective_projection_ref: Optional[str] = None
    """Reference to the effective projection (may be reused)."""
    
    reasons: tuple[str, ...] = ()
    """Reasons for this acceptance decision."""
    
    findings: tuple[str, ...] = ()
    """Findings from validation."""
    
    limitations: tuple[str, ...] = ()
    """Limitations on this acceptance."""
    
    provenance_ref: Optional[str] = None
    """Reference to acceptance provenance record."""
    
    @classmethod
    def accept(
        cls,
        publication_ref: str,
        effective_projection_ref: Optional[str] = None,
        findings: tuple[str, ...] = (),
        limitations: tuple[str, ...] = (),
        provenance_ref: Optional[str] = None,
    ) -> ProjectionAcceptance:
        """
        Create an acceptance result for a valid projection.
        
        Args:
            publication_ref: Reference to the publication
            effective_projection_ref: Reference to effective projection
            findings: Validation findings
            limitations: Acceptance limitations
            provenance_ref: Provenance reference
            
        Returns:
            A new ProjectionAcceptance instance
        """
        return cls(
            publication_ref=publication_ref,
            status="accepted",
            effective_projection_ref=effective_projection_ref or publication_ref,
            findings=findings,
            limitations=limitations,
            provenance_ref=provenance_ref,
        )
    
    @classmethod
    def accept_with_limitations(
        cls,
        publication_ref: str,
        effective_projection_ref: Optional[str] = None,
        reasons: tuple[str, ...] = (),
        findings: tuple[str, ...] = (),
        limitations: tuple[str, ...] = (),
        provenance_ref: Optional[str] = None,
    ) -> ProjectionAcceptance:
        """
        Create an acceptance result with known limitations.
        
        Args:
            publication_ref: Reference to the publication
            effective_projection_ref: Reference to effective projection
            reasons: Reason explanations
            findings: Validation findings
            limitations: Acceptance limitations
            provenance_ref: Provenance reference
            
        Returns:
            A new ProjectionAcceptance instance
        """
        return cls(
            publication_ref=publication_ref,
            status="accepted_with_limitations",
            effective_projection_ref=effective_projection_ref or publication_ref,
            reasons=reasons,
            findings=findings + limitations,
            limitations=limitations,
            provenance_ref=provenance_ref,
        )
    
    @classmethod
    def reuse(
        cls,
        publication_ref: str,
        reused_projection_ref: str,
        provenance_ref: Optional[str] = None,
    ) -> ProjectionAcceptance:
        """
        Create an acceptance result for a reused projection.
        
        Args:
            publication_ref: Reference to the publication
            reused_projection_ref: Reference to the reused projection
            provenance_ref: Provenance reference
            
        Returns:
            A new ProjectionAcceptance instance
        """
        return cls(
            publication_ref=publication_ref,
            status="reused",
            effective_projection_ref=reused_projection_ref,
            reasons=("reusing existing unchanged projection",),
            provenance_ref=provenance_ref,
        )
    
    @classmethod
    def defer(
        cls,
        publication_ref: str,
        reason: str = "deferred_to_next_cycle",
        provenance_ref: Optional[str] = None,
    ) -> ProjectionAcceptance:
        """
        Create a deferred acceptance result.
        
        Args:
            publication_ref: Reference to the publication
            reason: Reason for deferral
            provenance_ref: Provenance reference
            
        Returns:
            A new ProjectionAcceptance instance
        """
        return cls(
            publication_ref=publication_ref,
            status="deferred",
            reasons=(reason,),
            provenance_ref=provenance_ref,
        )
    
    @classmethod
    def reject(
        cls,
        publication_ref: str,
        rejection_reasons: tuple[str, ...],
        findings: tuple[str, ...] = (),
        limitations: tuple[str, ...] = (),
        provenance_ref: Optional[str] = None,
    ) -> ProjectionAcceptance:
        """
        Create a rejected acceptance result.
        
        Args:
            publication_ref: Reference to the publication
            rejection_reasons: Reasons for rejection
            findings: Validation findings
            limitations: Rejection limitations
            provenance_ref: Provenance reference
            
        Returns:
            A new ProjectionAcceptance instance
        """
        return cls(
            publication_ref=publication_ref,
            status="rejected",
            reasons=rejection_reasons,
            findings=findings + tuple(rejection_reasons),
            limitations=limitations,
            provenance_ref=provenance_ref,
        )
    
    @classmethod
    def stale(
        cls,
        publication_ref: str,
        invalidating_dependency: str,
        stale_projection_ref: Optional[str] = None,
        provenance_ref: Optional[str] = None,
    ) -> ProjectionAcceptance:
        """
        Create a stale projection acceptance result.
        
        Args:
            publication_ref: Reference to the publication
            invalidating_dependency: Dependency that invalidated this projection
            stale_projection_ref: Reference to the stale projection (if any)
            provenance_ref: Provenance reference
            
        Returns:
            A new ProjectionAcceptance instance
        """
        return cls(
            publication_ref=publication_ref,
            status="stale",
            effective_projection_ref=stale_projection_ref,
            reasons=(f"invalidated by dependency change: {invalidating_dependency}",),
            findings=("projection is stale",),
            limitations=("stale projection accepted with limitations",),
            provenance_ref=provenance_ref,
        )


# =============================================================================
# PUBLICATION WINDOW MODEL
# =============================================================================

@dataclass(frozen=True, slots=True)
class ProjectionPublicationWindow:
    """
    Immutable publication window model.
    
    PUBLICATION-WINDOW-INV-001: Window is immutable (deeply frozen)
    PUBLICATION-WINDOW-INV-002: Window has no runtime references
    
    WINDOW-LAW-001: Every CoordinationCycle shall possess exactly one canonical
    Publication Window
    
    WINDOW-LAW-003: Publication Window state shall remain explicit
    """
    window_identity: str = ""
    """Unique identifier for this publication window."""
    
    cycle_ref: Optional[str] = None
    """Reference to the parent coordination cycle."""
    
    status: str = "pending"
    """Window status (from PublicationWindowStatus)."""
    
    accepted_networks: tuple[str, ...] = ()
    """Network kinds that have accepted projections."""
    
    expected_networks: tuple[str, ...] = ()
    """Network kinds expected to publish in this window."""
    
    required_networks: tuple[str, ...] = ()
    """Network kinds whose projections are required."""
    
    optional_networks: tuple[str, ...] = ()
    """Network kinds whose projections are optional."""
    
    opening_semantic_time_ref: Optional[str] = None
    """Reference to semantic time at window opening."""
    
    closing_semantic_time_ref: Optional[str] = None
    """Reference to semantic time at window closure."""
    
    accepted_projection_references: tuple[str, ...] = ()
    """References to accepted projections."""
    
    rejected_projection_references: tuple[str, ...] = ()
    """References to rejected projections."""
    
    deferred_projection_references: tuple[str, ...] = ()
    """References to deferred projections."""
    
    closure_reason: Optional[str] = None
    """Reason for window closure."""
    
    findings: tuple[str, ...] = ()
    """Findings from window management."""
    
    limitations: tuple[str, ...] = ()
    """Limitations on this window."""
    
    provenance_ref: Optional[str] = None
    """Reference to window provenance record."""
    
    revision: int = 1
    """Revision number of this window."""
    
    @classmethod
    def open_window(
        cls,
        cycle_ref: str,
        expected_networks: tuple[str, ...],
        required_networks: tuple[str, ...],
        opening_time_ref: Optional[str] = None,
    ) -> ProjectionPublicationWindow:
        """
        Create an open publication window for a cycle.
        
        Args:
            cycle_ref: Reference to the parent coordination cycle
            expected_networks: Networks expected to publish
            required_networks: Networks whose projections are required
            opening_time_ref: Semantic time reference at opening
            
        Returns:
            A new open ProjectionPublicationWindow instance
        """
        return cls(
            window_identity=f"window:{cycle_ref}",
            cycle_ref=cycle_ref,
            status="open",
            expected_networks=expected_networks,
            required_networks=required_networks,
            optional_networks=tuple(n for n in expected_networks if n not in required_networks),
            opening_semantic_time_ref=opening_time_ref or f"semantic:open:{cycle_ref}",
        )
    
    def accept_projection(
        self,
        projection_ref: str,
        network_kind: str,
    ) -> ProjectionPublicationWindow:
        """
        Create a new window with an accepted projection.
        
        Args:
            projection_ref: Reference to the accepted projection
            network_kind: Network kind that published
            
        Returns:
            A new ProjectionPublicationWindow instance
        """
        return ProjectionPublicationWindow(
            window_identity=self.window_identity,
            cycle_ref=self.cycle_ref,
            status=self.status,
            accepted_networks=self.accepted_networks + (network_kind,),
            expected_networks=self.expected_networks,
            required_networks=self.required_networks,
            optional_networks=self.optional_networks,
            opening_semantic_time_ref=self.opening_semantic_time_ref,
            closing_semantic_time_ref=self.closing_semantic_time_ref,
            accepted_projection_references=self.accepted_projection_references + (projection_ref,),
            rejected_projection_references=self.rejected_projection_references,
            deferred_projection_references=self.deferred_projection_references,
            closure_reason=self.closure_reason,
            findings=self.findings,
            limitations=self.limitations,
            provenance_ref=self.provenance_ref,
            revision=self.revision + 1,
        )
    
    def close_window(
        self,
        closure_reason: Optional[str] = None,
        findings: tuple[str, ...] = (),
        limitations: tuple[str, ...] = (),
    ) -> ProjectionPublicationWindow:
        """
        Create a new window with closed status.
        
        Args:
            closure_reason: Reason for closure
            findings: Findings from window management
            limitations: Limitations on this window
            
        Returns:
            A new ProjectionPublicationWindow instance in closed state
        """
        return ProjectionPublicationWindow(
            window_identity=self.window_identity,
            cycle_ref=self.cycle_ref,
            status="closed",
            accepted_networks=self.accepted_networks,
            expected_networks=self.expected_networks,
            required_networks=self.required_networks,
            optional_networks=self.optional_networks,
            opening_semantic_time_ref=self.opening_semantic_time_ref,
            closing_semantic_time_ref=closure_reason or f"semantic:close:{self.cycle_ref}",
            accepted_projection_references=self.accepted_projection_references,
            rejected_projection_references=self.rejected_projection_references,
            deferred_projection_references=self.deferred_projection_references,
            closure_reason=closure_reason,
            findings=findings + self.findings,
            limitations=limitations + self.limitations,
            provenance_ref=self.provenance_ref,
            revision=self.revision + 1,
        )


# =============================================================================
# NETWORK PROJECTION PUBLICATION MODEL
# =============================================================================

@dataclass(frozen=True, slots=True)
class NetworkProjectionPublication:
    """
    Immutable projection publication model.
    
    PUBLICATION-LAW-001: Projection Publication shall remain distinct from
    Network Projection
    
    PUBLICATION-LAW-002: Every publication shall reference exactly one publishing
    network
    
    COORD-PUBLICATION-INV-001: Publication is immutable (deeply frozen)
    COORD-PUBLICATION-INV-002: Publication has no runtime references
    """
    publication_ref: str = ""
    """Unique reference to this publication."""
    
    network_identity_ref: str = ""
    """Reference to the publishing network identity."""
    
    epoch_ref: Optional[str] = None
    """Reference to the parent coordination epoch."""
    
    cycle_ref: Optional[str] = None
    """Reference to the coordination cycle."""
    
    projection_ref: Optional[str] = None
    """Reference to the actual projection (not the publication)."""
    
    publication_intention: str = "unknown"
    """Publication intention (from ProjectionPublicationIntention)."""
    
    replaces_projection_ref: Optional[str] = None
    """Reference to the projection this replaces (if any)."""
    
    dependency_revision_set: tuple[str, ...] = ()
    """Set of dependency revisions at publication time."""
    
    semantic_fingerprint: Optional[str] = None
    """Semantic fingerprint of the projection content."""
    
    confidence: float = 0.5
    """Confidence in this publication."""
    
    uncertainty: float = 0.5
    """Uncertainty about this publication."""
    
    semantic_time_ref: Optional[str] = None
    """Reference to semantic time at publication."""
    
    provenance_ref: Optional[str] = None
    """Reference to publication provenance record."""
    
    @classmethod
    def new_projection(
        cls,
        network_ref: str,
        epoch_ref: str,
        cycle_ref: str,
        projection_ref: str,
        dependency_revisions: tuple[str, ...],
        confidence: float = 0.5,
        uncertainty: float = 0.5,
        provenance_ref: Optional[str] = None,
    ) -> NetworkProjectionPublication:
        """
        Create a new projection publication.
        
        Args:
            network_ref: Reference to publishing network
            epoch_ref: Reference to parent epoch
            cycle_ref: Reference to coordination cycle
            projection_ref: Reference to actual projection
            dependency_revisions: Set of dependency revisions
            confidence: Confidence in this publication
            uncertainty: Uncertainty about this publication
            provenance_ref: Provenance reference
            
        Returns:
            A new NetworkProjectionPublication instance
        """
        return cls(
            publication_ref=f"pub:{network_ref}:{cycle_ref}:new",
            network_identity_ref=network_ref,
            epoch_ref=epoch_ref,
            cycle_ref=cycle_ref,
            projection_ref=projection_ref,
            publication_intention="new",
            dependency_revision_set=dependency_revisions,
            confidence=confidence,
            uncertainty=uncertainty,
            provenance_ref=provenance_ref,
        )
    
    def replace(
        self,
        replaces_ref: str,
        new_projection_ref: Optional[str] = None,
    ) -> NetworkProjectionPublication:
        """
        Create a replacement publication.
        
        Args:
            replaces_ref: Reference to the projection being replaced
            new_projection_ref: Optional reference to new projection
            
        Returns:
            A new replacement NetworkProjectionPublication instance
        """
        return NetworkProjectionPublication(
            publication_ref=f"pub:{self.network_identity_ref}:{self.cycle_ref}:replace",
            network_identity_ref=self.network_identity_ref,
            epoch_ref=self.epoch_ref,
            cycle_ref=self.cycle_ref,
            projection_ref=new_projection_ref or self.projection_ref,
            publication_intention="replace",
            replaces_projection_ref=replaces_ref,
            dependency_revision_set=self.dependency_revision_set,
            confidence=self.confidence,
            uncertainty=self.uncertainty,
            provenance_ref=self.provenance_ref,
        )
    
    def reuse(
        self,
        reused_ref: str,
        new_projection_ref: Optional[str] = None,
    ) -> NetworkProjectionPublication:
        """
        Create a reuse publication.
        
        Args:
            reused_ref: Reference to the projection being reused
            new_projection_ref: Optional reference to same projection
            
        Returns:
            A new reuse NetworkProjectionPublication instance
        """
        return NetworkProjectionPublication(
            publication_ref=f"pub:{self.network_identity_ref}:{self.cycle_ref}:reuse",
            network_identity_ref=self.network_identity_ref,
            epoch_ref=self.epoch_ref,
            cycle_ref=self.cycle_ref,
            projection_ref=new_projection_ref or self.projection_ref,
            publication_intention="reuse",
            replaces_projection_ref=reused_ref,
            dependency_revision_set=self.dependency_revision_set,
            confidence=self.confidence,
            uncertainty=self.uncertainty,
            provenance_ref=self.provenance_ref,
        )
    
    def withdraw(
        self,
    ) -> NetworkProjectionPublication:
        """
        Create a withdrawal publication.
        
        Returns:
            A new withdrawal NetworkProjectionPublication instance
        """
        return NetworkProjectionPublication(
            publication_ref=f"pub:{self.network_identity_ref}:{self.cycle_ref}:withdraw",
            network_identity_ref=self.network_identity_ref,
            epoch_ref=self.epoch_ref,
            cycle_ref=self.cycle_ref,
            projection_ref=self.projection_ref,
            publication_intention="withdraw",
            replaces_projection_ref=self.replaces_projection_ref,
            dependency_revision_set=self.dependency_revision_set,
            confidence=0.0,
            uncertainty=1.0,
            provenance_ref=self.provenance_ref,
        )
    
    def correct(
        self,
        corrected_ref: str,
    ) -> NetworkProjectionPublication:
        """
        Create a correction publication.
        
        Args:
            corrected_ref: Reference to the projection being corrected
            
        Returns:
            A new correction NetworkProjectionPublication instance
        """
        return NetworkProjectionPublication(
            publication_ref=f"pub:{self.network_identity_ref}:{self.cycle_ref}:correct",
            network_identity_ref=self.network_identity_ref,
            epoch_ref=self.epoch_ref,
            cycle_ref=self.cycle_ref,
            projection_ref=corrected_ref,
            publication_intention="correct",
            replaces_projection_ref=corrected_ref,
            dependency_revision_set=self.dependency_revision_set,
            confidence=min(self.confidence + 0.1, 1.0),
            uncertainty=max(self.uncertainty - 0.1, 0.0),
            provenance_ref=self.provenance_ref,
        )