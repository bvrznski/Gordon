# Gordon Cognitive Architecture - Phase 4.11.7
# ===========================================
"""
Orchestration Identity Models
=============================

Immutable identity models for orchestration components.
All identities are deterministic and immutable.
"""

from __future__ import annotations

from dataclasses import dataclass, field
import hashlib


@dataclass(frozen=True, slots=True)
class OrchestrationIdentity:
    """
    Immutable identity for an orchestration artifact.
    
    ORCHESTRATION-LAW-001: Every orchestration plan possesses one stable semantic identity
    ORCHESTRATION-LAW-002: Orchestration identity remains independent from runtime execution
    ORCHESTRATION-LAW-004: Identity shall preserve orchestration scope
    ORCHESTRATION-LAW-005: Identity shall preserve originating goal
    ORCHESTRATION-LAW-006: Identity shall preserve provenance
    
    IDENTITY-INV-001: Identity is immutable (deeply frozen)
    IDENTITY-INV-002: Identity has no runtime references
    IDENTITY-LAW-003: Equivalent requests produce equivalent identities
    """
    
    value: str = ""
    """The identity string."""
    
    scope_ref: str = ""
    """Reference to orchestration scope."""
    
    goal_ref: str = ""
    """Reference to originating goal."""
    
    @classmethod
    def from_content(cls, content: str, scope_ref: str = "", goal_ref: str = "") -> OrchestrationIdentity:
        """
        Create an identity from content using deterministic hashing.
        
        Args:
            content: Content to hash for identity generation
            scope_ref: Reference to orchestration scope (optional)
            goal_ref: Reference to originating goal (optional)
            
        Returns:
            A new OrchestrationIdentity instance
        """
        # Deterministic hash - no randomness or wall-clock time
        hash_input = f"{scope_ref}:{goal_ref}:{content}"
        identity_hash = hashlib.sha256(hash_input.encode("utf-8")).hexdigest()[:16]
        
        return cls(
            value=f"orch:{identity_hash}",
            scope_ref=scope_ref,
            goal_ref=goal_ref,
        )
    
    def __str__(self) -> str:
        return self.value


@dataclass(frozen=True, slots=True)
class CycleIdentity:
    """
    Immutable identity for a cognitive cycle.
    
    CYCLE-LAW-001: Every orchestration belongs to exactly one Cognitive Cycle
    CYCLE-LAW-003: Cycle boundaries shall remain explicit
    
    IDENTITY-INV-001: Identity is immutable (deeply frozen)
    IDENTITY-INV-002: Identity has no runtime references
    """
    
    value: str = ""
    """The cycle identity string."""
    
    kind: str = ""  # CycleKind.*
    """Type of cycle."""
    
    sequence_index: int = 0
    """Sequence index within an epoch."""
    
    @classmethod
    def create(cls, scope_ref: str = "", kind: str = "", sequence_index: int = 0) -> CycleIdentity:
        """
        Create a new cycle identity.
        
        Args:
            scope_ref: Reference to orchestration scope (optional)
            kind: Kind of cycle (optional)
            sequence_index: Sequence index within epoch
            
        Returns:
            A new CycleIdentity instance
        """
        # Deterministic generation - no randomness or wall-clock time
        hash_input = f"{scope_ref}:{kind}:{sequence_index}"
        identity_hash = hashlib.sha256(hash_input.encode("utf-8")).hexdigest()[:12]
        
        return cls(
            value=f"cycle:{identity_hash}",
            kind=kind,
            sequence_index=sequence_index,
        )
    
    def __str__(self) -> str:
        return self.value


@dataclass(frozen=True, slots=True)
class StageIdentity:
    """
    Immutable identity for an execution stage.
    
    STAGE-LAW-001: Every execution stage possesses one stable identity
    STAGE-LAW-002: Every stage belongs to exactly one orchestration plan
    
    IDENTITY-INV-001: Identity is immutable (deeply frozen)
    IDENTITY-INV-002: Identity has no runtime references
    """
    
    value: str = ""
    """The stage identity string."""
    
    cycle_ref: str = ""
    """Reference to the parent cycle."""
    
    kind: str = ""  # StageKind.*
    """Type of stage."""
    
    index_in_cycle: int = 0
    """Index within the cycle for ordering."""
    
    @classmethod
    def create(cls, cycle_ref: str, kind: str, index_in_cycle: int) -> StageIdentity:
        """
        Create a new stage identity.
        
        Args:
            cycle_ref: Reference to parent cycle
            kind: Kind of stage
            index_in_cycle: Index within the cycle
            
        Returns:
            A new StageIdentity instance
        """
        hash_input = f"{cycle_ref}:{kind}:{index_in_cycle}"
        identity_hash = hashlib.sha256(hash_input.encode("utf-8")).hexdigest()[:10]
        
        return cls(
            value=f"stage:{identity_hash}",
            cycle_ref=cycle_ref,
            kind=kind,
            index_in_cycle=index_in_cycle,
        )
    
    def __str__(self) -> str:
        return self.value


@dataclass(frozen=True, slots=True)
class ParticipantIdentity:
    """
    Immutable identity for a cycle participant.
    
    PARTICIPANT-LAW-001: Every participant represents exactly one cognitive network
    PARTICIPANT-LAW-004: Optional participants remain distinguishable
    
    IDENTITY-INV-001: Identity is immutable (deeply frozen)
    IDENTITY-INV-002: Identity has no runtime references
    """
    
    value: str = ""
    """The participant identity string."""
    
    network_ref: str = ""
    """Reference to the cognitive network."""
    
    role: str = ""  # ParticipantRole.*
    """Participant's role in the cycle."""
    
    is_mandatory: bool = True
    """Whether this participant is mandatory."""
    
    @classmethod
    def create(cls, network_ref: str, role: str, is_mandatory: bool = True) -> ParticipantIdentity:
        """
        Create a new participant identity.
        
        Args:
            network_ref: Reference to cognitive network
            role: Role in the cycle
            is_mandatory: Whether mandatory
            
        Returns:
            A new ParticipantIdentity instance
        """
        hash_input = f"{network_ref}:{role}:{is_mandatory}"
        identity_hash = hashlib.sha256(hash_input.encode("utf-8")).hexdigest()[:10]
        
        return cls(
            value=f"participant:{identity_hash}",
            network_ref=network_ref,
            role=role,
            is_mandatory=is_mandatory,
        )
    
    def __str__(self) -> str:
        return self.value