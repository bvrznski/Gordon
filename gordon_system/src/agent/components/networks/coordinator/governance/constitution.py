# Gordon Cognitive Architecture - Phase 4.11.9
# ===========================================

"""
Cognitive Coordination Governance (CCG) - Constitution
======================================================

Canonical immutable constitution definitions.
The Constitution defines architectural invariants - nothing may violate them.

Following:
* CONSTITUTION-LAW-001 through CONSTITUTION-LAW-008
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Final
from collections import OrderedDict

from .principle import ConstitutionalPrinciple, CanonicalPrinciples


# =============================================================================
# CONSTITUTION IDENTITY
# =============================================================================

@dataclass(frozen=True, slots=True)
class ConstitutionIdentity:
    """
    Immutable identity for a constitution.
    
    CONSTITUTION-ID-INV-001: Constitution identity is immutable
    CONSTITUTION-ID-INV-002: Identity has no runtime references
    
    CONSTITUTION-LAW-007: Constitutional interpretation shall remain deterministic
    CONSTITUTION-LAW-008: Constitution publication shall remain immutable
    """
    constitution_version: str = "1.0.0"
    """Version identifier for this constitution."""
    
    created_at_sequence: int = 0
    """Sequence number when this constitution was established."""
    
    def __str__(self) -> str:
        return f"constitution:{self.constitution_version}:{self.created_at_sequence}"


# =============================================================================
# CONSTITUTION
# =============================================================================

@dataclass(frozen=True, slots=True)
class Constitution:
    """
    Immutable constitutional framework defining architectural invariants.
    
    The Constitution establishes the immutable principles that constrain every
    future decision. It never changes during execution - revisions create new
    constitutions.
    
    CONSTITUTION-LAW-001: Every Gordon architecture possesses exactly one active Constitution
    CONSTITUTION-LAW-002: The Constitution defines immutable architectural principles
    CONSTITUTION-LAW-003: Constitutional revisions shall create new constitutional versions
    CONSTITUTION-LAW-004: Previous constitutions shall remain historically inspectable
    CONSTITUTION-LAW-005: Constitutional principles shall preserve provenance
    CONSTITUTION-LAW-006: Constitution revisions shall preserve lineage
    CONSTITUTION-LAW-007: Constitutional interpretation shall remain deterministic
    CONSTITUTION-LAW-008: Constitution publication shall remain immutable
    
    CCG-CONS-INV-001: Constitution is immutable (deeply frozen)
    CCG-CONS-INV-002: Constitution has no runtime references
    """
    constitution_identity: ConstitutionIdentity
    """Unique identity for this constitution."""
    
    constitutional_principles: tuple[ConstitutionalPrinciple, ...]
    """All constitutional principles defined by this constitution."""
    
    governing_policies: tuple[str, ...] = field(default_factory=tuple)
    """Reference strings to policies governed by this constitution."""
    
    authority_model_ref: str = "default"
    """Reference to the authority model definition."""
    
    trust_domain_definitions: tuple[str, ...] = field(default_factory=tuple)
    """References to trust domain definitions."""
    
    revision_history: tuple[ConstitutionIdentity, ...] = field(default_factory=tuple)
    """History of previous constitutional versions (newer first)."""
    
    provenance_ref: str | None = None
    """Reference to constitution provenance record."""
    
    @classmethod
    def create(
        cls,
        version: str = "1.0.0",
        sequence_index: int = 0,
        principles: tuple[ConstitutionalPrinciple, ...] | None = None,
        policies: tuple[str, ...] | None = None,
        authority_model_ref: str = "default",
        trust_domains: tuple[str, ...] | None = None,
        history: tuple[ConstitutionIdentity, ...] | None = None,
    ) -> Constitution:
        """
        Create a new constitution instance.
        
        Args:
            version: Version identifier
            sequence_index: Creation sequence number
            principles: Constitutional principles (uses canonical if not specified)
            policies: Governing policy references
            authority_model_ref: Reference to authority model
            trust_domains: Trust domain definition references
            history: Previous constitution versions
            
        Returns:
            A new Constitution instance
        """
        return cls(
            constitution_identity=ConstitutionIdentity(version, sequence_index),
            constitutional_principles=principles or CanonicalPrinciples.all_principles(),
            governing_policies=policies or (),
            authority_model_ref=authority_model_ref,
            trust_domain_definitions=trust_domains or (),
            revision_history=history or (),
            provenance_ref=None,
        )
    
    @classmethod
    def canonical(cls) -> Constitution:
        """
        Create the canonical constitution with all default principles.
        
        Returns:
            The canonical Constitution instance for Gordon
        """
        return cls.create(
            version="1.0.0",
            sequence_index=0,
            principles=CanonicalPrinciples.all_principles(),
            policies=("coordination", "orchestration"),
            authority_model_ref="canonical:hierarchy:1.0.0",
            trust_domains=("core", "coordination", "memory", "experimental"),
        )
    
    def get_principle_by_name(self, name: str) -> ConstitutionalPrinciple | None:
        """
        Get a principle by its name.
        
        Args:
            name: The principle name
            
        Returns:
            The principle or None if not found
        """
        for p in self.constitutional_principles:
            if p.principle_name == name:
                return p
        return None
    
    def get_principle_by_identity(self, identity: str) -> ConstitutionalPrinciple | None:
        """
        Get a principle by its identity.
        
        Args:
            identity: The principle identity
            
        Returns:
            The principle or None if not found
        """
        for p in self.constitutional_principles:
            if p.principle_identity == identity:
                return p
        return None
    
    def is_principle_violated(self, principle_name: str) -> bool:
        """
        Check if a principle can be violated.
        
        Args:
            principle_name: The name of the principle
            
        Returns:
            True if the principle exists and is mandatory
        """
        p = self.get_principle_by_name(principle_name)
        return p is not None and p.mandatory
    
    def has_authority_model(self, model_ref: str) -> bool:
        """
        Check if a specific authority model is defined.
        
        Args:
            model_ref: The authority model reference
            
        Returns:
            True if the model matches
        """
        return self.authority_model_ref == model_ref


# =============================================================================
# CONSTITUTIONAL EVOLUTION PROPOSAL
# =============================================================================

@dataclass(frozen=True, slots=True)
class ConstitutionalEvolutionProposal:
    """
    Immutable proposal for constitutional evolution.
    
    CONSTITUTION-EVOL-INV-001: Proposal is immutable
    CONSTITUTION-EVOL-INV-002: Proposal has no runtime references
    
    EVOLUTION-LAW-001: Constitutional evolution shall remain explicit
    EVOLUTION-LAW-002: Every constitutional revision shall preserve historical constitutions
    EVOLUTION-LAW-003: Evolution proposals shall remain inspectable
    EVOLUTION-LAW-004: Review shall precede approval
    EVOLUTION-LAW-005: Approval shall precede publication
    """
    proposal_id: str
    """Unique identifier for this evolution proposal."""
    
    current_constitution_ref: ConstitutionIdentity
    """Reference to the constitution being evolved."""
    
    proposed_principles: tuple[ConstitutionalPrinciple, ...]
    """Proposed constitutional principles (full set)."""
    
    change_summary: str
    """Human-readable summary of changes."""
    
    proposer_identity: str = "unknown"
    """Identity of the proposal proposer."""
    
    created_at_sequence: int = 0
    """Sequence number when proposal was created."""
    
    review_status: str = "pending"
    """Status of the review process."""
    
    approved_by: tuple[str, ...] = field(default_factory=tuple)
    """Identities of approvers."""
    
    effective_after_sequence: int = 0
    """Sequence number after which this becomes active."""
    
    @classmethod
    def create(
        cls,
        proposal_id: str,
        current_constitution_ref: ConstitutionIdentity,
        change_summary: str,
        proposer_identity: str = "unknown",
        sequence_index: int = 0,
    ) -> ConstitutionalEvolutionProposal:
        """
        Create a new evolution proposal.
        
        Args:
            proposal_id: Unique identifier for the proposal
            current_constitution_ref: The constitution being proposed for change
            change_summary: Description of proposed changes
            proposer_identity: Identity of the proposer
            sequence_index: Creation sequence number
            
        Returns:
            A new ConstitutionalEvolutionProposal instance
        """
        return cls(
            proposal_id=proposal_id,
            current_constitution_ref=current_constitution_ref,
            proposed_principles=(),
            change_summary=change_summary,
            proposer_identity=proposer_identity,
            created_at_sequence=sequence_index,
            review_status="pending",
            approved_by=(),
            effective_after_sequence=0,
        )
    
    def add_approver(self, approver_id: str) -> ConstitutionalEvolutionProposal:
        """Add an approver and return a new proposal."""
        return ConstitutionalEvolutionProposal(
            proposal_id=self.proposal_id,
            current_constitution_ref=self.current_constitution_ref,
            proposed_principles=self.proposed_principles,
            change_summary=self.change_summary,
            proposer_identity=self.proposer_identity,
            created_at_sequence=self.created_at_sequence,
            review_status="approved",
            approved_by=(*self.approved_by, approver_id),
            effective_after_sequence=self.effective_after_sequence,
        )