# Gordon Cognitive Architecture - Phase 4.11.2
# ===========================================

"""
Coordination Epoch Models
=========================

Canonical immutable models for coordination epochs.

COORDINATION EPOCH OVERVIEW
-------------------------
A CoordinationEpoch groups semantically related CoordinationCycles.
Examples:
- One user request
- One task episode
- One sensorimotor episode
- One planning episode
- One alert-response episode

EPOCH INVARIANTS
================
- Epochs remain immutable after construction
- Epoch identity remains stable across revisions
- Epochs group semantically related cycles
- Epoch completion conditions remain explicit
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum, auto
from typing import Optional


# =============================================================================
# COORDINATION EPOCH STATUS
# =============================================================================

class CoordinationEpochStatus(Enum):
    """
    Canonical status enumeration for coordination epochs.
    
    EPOCH-LAW-011: Epoch cancellation remains a semantic state
    EPOCH-LAW-012: The semantic layer shall not perform runtime cancellation
    
    COORD-EPOCH-STATUS-INV-001: Status is immutable once set
    """
    OPEN = "open"
    """Epoch has been opened and is accepting new cycles."""
    
    ACTIVE = "active"
    """Epoch has active cycles being processed."""
    
    QUIESCENT = "quiescent"
    """Epoch is waiting for new cycles but remains open."""
    
    COMPLETING = "completing"
    """Epoch completion conditions are satisfied, finalization in progress."""
    
    COMPLETE = "complete"
    """Epoch completed successfully."""
    
    FAILED = "failed"
    """Epoch failed due to policy violation or other error."""
    
    CANCELLED = "cancelled"
    """Epoch was cancelled (semantic state only)."""
    
    SUPERSEDED = "superseded"
    """Epoch has been superseded by a later epoch."""
    
    UNKNOWN = "unknown"
    """Epoch status cannot be determined."""


# =============================================================================
# COORDINATION EPOCH IDENTITY
# =============================================================================

@dataclass(frozen=True, slots=True)
class CoordinationEpochIdentity:
    """
    Immutable identity for a coordination epoch.
    
    EPOCH-LAW-001: Every CoordinationEpoch shall possess stable semantic identity
    EPOCH-LAW-002: Epoch identity shall remain stable across epoch revisions
    
    COORD-EPOCH-ID-INV-001: Identity is immutable (deeply frozen)
    COORD-EPOCH-ID-INV-002: Identity has no runtime references
    """
    identity: str = ""
    """Unique identifier for this epoch."""
    
    parent_epoch_identity: Optional[str] = None
    """Reference to parent epoch if this is a revision."""
    
    sequence_index: int = 0
    """Sequence index within parent epoch if applicable."""
    
    @classmethod
    def from_context(cls, context_ref: str) -> CoordinationEpochIdentity:
        """
        Create an epoch identity from a context reference.
        
        Args:
            context_ref: Reference to the triggering context
            
        Returns:
            A new CoordinationEpochIdentity instance
        """
        return cls(
            identity=f"epoch:{context_ref}",
            parent_epoch_identity=None,
            sequence_index=0,
        )
    
    def __str__(self) -> str:
        if self.parent_epoch_identity and self.sequence_index > 0:
            return f"{self.identity}:r{self.sequence_index}"
        return self.identity


# =============================================================================
# COORDINATION EPOCH MODEL
# =============================================================================

@dataclass(frozen=True, slots=True)
class CoordinationEpoch:
    """
    Immutable epoch model for coordination.
    
    EPOCH-LAW-003: Epochs shall group semantically related Coordination Cycles
    EPOCH-LAW-004: Epochs shall remain immutable after construction
    EPOCH-LAW-005: Epoch revisions shall create new immutable revisions
    
    COORD-EPOCH-INV-001: Epoch is immutable (deeply frozen)
    COORD-EPOCH-INV-002: Epoch has no runtime references
    """
    epoch_identity: CoordinationEpochIdentity = field(
        default_factory=CoordinationEpochIdentity
    )
    """Identity of this coordination epoch."""
    
    parent_epoch_reference: Optional[str] = None
    """Reference to parent epoch if this is a revision."""
    
    triggering_context_reference: Optional[str] = None
    """Reference to the context that triggered this epoch."""
    
    coordination_domain: str = "global"
    """Coordination domain (from CoordinationDomain enum)."""
    
    membership_revision: int = 1
    """Revision of the active membership configuration."""
    
    policy_revision: int = 1
    """Revision of the active coordination policy."""
    
    cycle_references: tuple[str, ...] = ()
    """References to cycles in this epoch."""
    
    opening_semantic_time_ref: Optional[str] = None
    """Reference to semantic time at epoch opening."""
    
    closing_semantic_time_ref: Optional[str] = None
    """Reference to semantic time at epoch closure."""
    
    status: str = "open"
    """Status of the epoch (from CoordinationEpochStatus)."""
    
    completion_condition: Optional[str] = None
    """Declarative condition for epoch completion."""
    
    findings: tuple[str, ...] = ()
    """Findings from epoch processing."""
    
    limitations: tuple[str, ...] = ()
    """Limitations on this epoch."""
    
    provenance_ref: Optional[str] = None
    """Reference to epoch provenance record."""
    
    revision: int = 1
    """Revision number of this epoch."""
    
    @classmethod
    def open_epoch(
        cls,
        context_ref: str,
        domain: str = "global",
        membership_rev: int = 1,
        policy_rev: int = 1,
        completion_condition: Optional[str] = None,
        provenance_ref: Optional[str] = None,
    ) -> CoordinationEpoch:
        """
        Create a new open coordination epoch.
        
        Args:
            context_ref: Reference to triggering context
            domain: Coordination domain
            membership_rev: Membership configuration revision
            policy_rev: Policy revision
            completion_condition: Declarative completion condition
            provenance_ref: Provenance reference
            
        Returns:
            A new open CoordinationEpoch instance
        """
        return cls(
            epoch_identity=CoordinationEpochIdentity.from_context(context_ref),
            triggering_context_reference=context_ref,
            coordination_domain=domain,
            membership_revision=membership_rev,
            policy_revision=policy_rev,
            opening_semantic_time_ref=f"semantic:open:{context_ref}",
            status="open",
            completion_condition=completion_condition,
            provenance_ref=provenance_ref,
        )
    
    def complete(
        self,
        closing_time_ref: Optional[str] = None,
        findings: tuple[str, ...] = (),
        limitations: tuple[str, ...] = (),
    ) -> CoordinationEpoch:
        """
        Create a completed revision of this epoch.
        
        Args:
            closing_time_ref: Reference to semantic time at closure
            findings: Findings from epoch processing
            limitations: Limitations on this epoch
            
        Returns:
            A new completed CoordinationEpoch instance
        """
        return CoordinationEpoch(
            epoch_identity=CoordinationEpochIdentity(
                identity=self.epoch_identity.identity,
                parent_epoch_identity=str(self.epoch_identity),
                sequence_index=self.revision,
            ),
            triggering_context_reference=self.triggering_context_reference,
            coordination_domain=self.coordination_domain,
            membership_revision=self.membership_revision,
            policy_revision=self.policy_revision,
            cycle_references=self.cycle_references,
            opening_semantic_time_ref=self.opening_semantic_time_ref,
            closing_semantic_time_ref=closing_time_ref or f"semantic:close:{self.epoch_identity.identity}",
            status="complete",
            completion_condition=self.completion_condition,
            findings=findings + self.findings,
            limitations=limitations + self.limitations,
            provenance_ref=self.provenance_ref,
            revision=self.revision + 1,
        )
    
    def fail(
        self,
        failure_findings: tuple[str, ...],
    ) -> CoordinationEpoch:
        """
        Create a failed revision of this epoch.
        
        Args:
            failure_findings: Findings describing the failure
            
        Returns:
            A new failed CoordinationEpoch instance
        """
        return CoordinationEpoch(
            epoch_identity=CoordinationEpochIdentity(
                identity=self.epoch_identity.identity,
                parent_epoch_identity=str(self.epoch_identity),
                sequence_index=self.revision,
            ),
            triggering_context_reference=self.triggering_context_reference,
            coordination_domain=self.coordination_domain,
            membership_revision=self.membership_revision,
            policy_revision=self.policy_revision,
            cycle_references=self.cycle_references,
            opening_semantic_time_ref=self.opening_semantic_time_ref,
            closing_semantic_time_ref=f"semantic:fail:{self.epoch_identity.identity}",
            status="failed",
            completion_condition=self.completion_condition,
            findings=failure_findings + self.findings,
            limitations=self.limitations,
            provenance_ref=self.provenance_ref,
            revision=self.revision + 1,
        )
    
    def add_cycle(self, cycle_ref: str) -> CoordinationEpoch:
        """
        Create a new epoch with an additional cycle reference.
        
        Args:
            cycle_ref: Reference to the cycle being added
            
        Returns:
            A new CoordinationEpoch instance with the added cycle
        """
        return CoordinationEpoch(
            epoch_identity=CoordinationEpochIdentity(
                identity=self.epoch_identity.identity,
                parent_epoch_identity=self.epoch_identity.parent_epoch_identity,
                sequence_index=self.revision,
            ),
            triggering_context_reference=self.triggering_context_reference,
            coordination_domain=self.coordination_domain,
            membership_revision=self.membership_revision,
            policy_revision=self.policy_revision,
            cycle_references=self.cycle_references + (cycle_ref,),
            opening_semantic_time_ref=self.opening_semantic_time_ref,
            closing_semantic_time_ref=self.closing_semantic_time_ref,
            status=self.status,
            completion_condition=self.completion_condition,
            findings=self.findings,
            limitations=self.limitations,
            provenance_ref=self.provenance_ref,
            revision=self.revision + 1,
        )


# =============================================================================
# COORDINATION DOMAIN
# =============================================================================

class CoordinationDomain(Enum):
    """
    Canonical coordination domains.
    
    COORD-DOMAIN-INV-001: Domain is immutable once set
    
    DOMAINS:
    - GLOBAL: All networks, all phases
    - LANGUAGE: Language processing only
    - SENSORIMOTOR: Sensorimotor coupling only
    - NAVIGATION: Spatial navigation only
    - SOCIAL: Social interaction only
    - INTERNAL: Internal default-mode processing
    - EXECUTIVE: Executive evaluation only
    - ALERT_RESPONSE: Alert handling and interruption
    - TASK: Task-specific coordination
    """
    GLOBAL = "global"
    """Global coordination across all networks."""
    
    LANGUAGE = "language"
    """Language processing domain."""
    
    SENSORIMOTOR = "sensorimotor"
    """Sensorimotor coupling domain."""
    
    NAVIGATION = "navigation"
    """Spatial navigation domain."""
    
    SOCIAL = "social"
    """Social interaction domain."""
    
    INTERNAL = "internal"
    """Default-mode internal processing domain."""
    
    EXECUTIVE = "executive"
    """Executive evaluation domain."""
    
    ALERT_RESPONSE = "alert_response"
    """Alert handling and interruption domain."""
    
    TASK = "task"
    """Task-specific coordination domain."""


# =============================================================================
# SEMANTIC FINGERPRINT FOR EPOCH
# =============================================================================

@dataclass(frozen=True, slots=True)
class EpochSemanticFingerprint:
    """
    Immutable semantic fingerprint for an epoch.
    
    FINGERPRINT-INV-001: Fingerprint is deterministic
    FINGERPRINT-INV-002: Fingerprint has no runtime references
    
    FINGERPRINT-LAW-001: Semantic fingerprints shall be deterministic
    FINGERPRINT-LAW-007: Fingerprint schema version shall remain explicit
    """
    epoch_ref: str = ""
    """Reference to the epoch."""
    
    schema_version: str = "1.0.0"
    """Version of fingerprint schema."""
    
    canonical_hash: str = ""
    """Canonical hash of epoch content."""
    
    @classmethod
    def from_epoch(cls, epoch: CoordinationEpoch) -> EpochSemanticFingerprint:
        """
        Create a fingerprint for an epoch.
        
        Args:
            epoch: The epoch to fingerprint
            
        Returns:
            A new EpochSemanticFingerprint instance
        """
        # In implementation, this would compute hash from canonical serialization
        return cls(
            epoch_ref=str(epoch.epoch_identity),
            schema_version="1.0.0",
            canonical_hash=f"hash:{epoch.epoch_identity.identity}:{epoch.revision}",
        )