# Persistence Domains and State Classification
# ============================================

"""
State taxonomy, durability classes, ownership models, and domain definitions.

This module defines:
- StateDomain: A named collection of related state
- StateDomainId: Unique identifier for a state domain
- DurabilityClass: Required durability guarantees for state
- StateOwner: Entity that owns and manages state
"""

from dataclasses import dataclass, field
from enum import Enum, auto
from typing import NewType, Dict, Any, Optional
import uuid


# =============================================================================
# State Domain Identifiers
# =============================================================================

StateDomainId = NewType("StateDomainId", str)


@dataclass(frozen=True)
class RuntimeId:
    """Unique identifier for a runtime instance."""
    value: str
    
    @classmethod
    def generate(cls) -> "RuntimeId":
        """Generate a new unique runtime ID."""
        return cls(value=str(uuid.uuid4()))
    
    def __str__(self) -> str:
        return self.value


@dataclass(frozen=True)
class BootSessionId:
    """Unique identifier for a boot session."""
    value: str
    
    @classmethod
    def generate(cls) -> "BootSessionId":
        """Generate a new unique boot session ID."""
        return cls(value=str(uuid.uuid4()))
    
    def __str__(self) -> str:
        return self.value


# =============================================================================
# Durability Classes
# =============================================================================

class DurabilityClass(Enum):
    """
    State durability requirements.
    
    Each class defines required backend guarantees, flush requirements,
    transaction requirements, and recovery objectives.
    """
    
    # No persistence required - state lives only during runtime
    NONE = "none"
    
    # State survives only the current process lifetime
    PROCESS_LIFETIME = "process_lifetime"
    
    # State survives restart within same runtime instance
    RUNTIME_LIFETIME = "runtime_lifetime"
    
    # State survives process restart (default for recoverable state)
    RESTART_RECOVERABLE = "restart_recoverable"
    
    # State survives host restart
    HOST_RESTART_RECOVERABLE = "host_restart_recoverable"
    
    # State is durable with strong guarantees
    DURABLE = "durable"
    
    # State is replicated across nodes
    REPLICATED = "replicated"
    
    # State is archival (long-term retention)
    ARCHIVAL = "archival"


@dataclass(frozen=True)
class DurabilityRequirements:
    """Required durability guarantees for a state domain."""
    
    durability_class: DurabilityClass
    
    # Backend guarantees
    requires_atomic_write: bool = False
    requires_transaction: bool = False
    requires_flush_on_write: bool = False
    requires_fsync: bool = False
    
    # Retention requirements
    min_retention_seconds: float = 0.0
    max_history_length: int = 1000
    
    # Recovery objectives
    recovery_point_objective_seconds: float = 60.0  # RPO
    recovery_time_objective_seconds: float = 30.0   # RTO
    
    # Validation policy
    requires_integrity_check_on_read: bool = True
    requires_checksum_verification: bool = True


# =============================================================================
# State Ownership
# =============================================================================

StateOwner = NewType("StateOwner", str)


@dataclass(frozen=True)
class OwnerIdentity:
    """Identity of a state owner."""
    
    owner_id: StateOwner
    component_name: Optional[str] = None
    instance_id: Optional[str] = None


# =============================================================================
# State Domain Definition
# =============================================================================

@dataclass(frozen=True)
class StateDomain:
    """
    A named collection of related state with defined ownership and durability.
    
    Every state domain must declare:
        - owner: Entity that owns the state (not persistence!)
        - persistence_owner: Entity responsible for persistence coordination
        - durability_class: Required durability guarantees
        - schema_version: Current schema version for serialization
        - persistence_participation: Whether this domain participates in checkpoints
        - snapshot_support: Whether snapshots are supported
    """
    
    domain_id: StateDomainId
    
    # Ownership
    owner: OwnerIdentity
    persistence_owner: Optional[StateOwner] = None  # Defaults to owner if not specified
    
    # Durability
    durability_class: DurabilityClass = DurabilityClass.RESTART_RECOVERABLE
    
    # Serialization
    schema_version: int = 1
    serialization_format: str = "canonical_json"
    
    # Persistence participation
    persistence_participation: bool = True
    checkpoint_support: bool = True
    journal_support: bool = False
    snapshot_support: bool = True
    
    # Migration strategy
    migration_strategy: str = "explicit"  # explicit, automatic, none
    
    # Retention
    retention_seconds: float = 86400.0  # 24 hours default
    max_retained_versions: int = 10
    
    # Sensitivity
    is_sensitive: bool = False
    encryption_required: bool = False
    
    # External dependencies
    external_dependencies: list[str] = field(default_factory=list)
    
    @property
    def is_durable(self) -> bool:
        """Check if state requires durable persistence."""
        return self.durability_class in (
            DurabilityClass.RESTART_RECOVERABLE,
            DurabilityClass.HOST_RESTART_RECOVERABLE,
            DurabilityClass.DURABLE,
            DurabilityClass.REPLICATED,
            DurabilityClass.ARCHIVAL,
        )
    
    @property
    def requirements(self) -> DurabilityRequirements:
        """Get durability requirements for this domain."""
        return DurabilityRequirements(
            durability_class=self.durability_class,
            requires_atomic_write=self.durability_class in (
                DurabilityClass.DURABLE, DurabilityClass.REPLICATED, DurabilityClass.ARCHIVAL
            ),
            requires_transaction=self.durability_class in (
                DurabilityClass.HOST_RESTART_RECOVERABLE, DurabilityClass.DURABLE,
                DurabilityClass.REPLICATED, DurabilityClass.ARCHIVAL
            ),
            requires_fsync=self.durability_class == DurabilityClass.ARCHIVAL,
            min_retention_seconds=self.retention_seconds,
            max_history_length=self.max_retained_versions,
        )


# =============================================================================
# State Domain Registry
# =============================================================================

class StateDomainRegistry:
    """
    Registry of all state domains in the runtime.
    
    Provides:
        - Domain discovery and lookup
        - Domain validation
        - Ownership verification
    
    Usage:
        registry = StateDomainRegistry()
        
        # Register a domain
        domain = StateDomain(
            domain_id=StateDomainId("runtime_state"),
            owner=OwnerIdentity(owner_id="runtime", component_name="state")
        )
        registry.register(domain)
        
        # Look up a domain
        found = registry.get(StateDomainId("runtime_state"))
    """
    
    def __init__(self) -> None:
        self._domains: Dict[StateDomainId, StateDomain] = {}
        self._lock = None  # Would use threading.Lock in production
    
    def register(self, domain: StateDomain) -> None:
        """Register a state domain."""
        if domain.domain_id in self._domains:
            raise ValueError(f"Domain {domain.domain_id} already registered")
        self._domains[domain.domain_id] = domain
    
    def get(self, domain_id: StateDomainId) -> Optional[StateDomain]:
        """Get a registered domain by ID."""
        return self._domains.get(domain_id)
    
    def list_all(self) -> list[StateDomain]:
        """List all registered domains."""
        return list(self._domains.values())
    
    def get_by_owner(self, owner: StateOwner) -> list[StateDomain]:
        """Get all domains owned by a specific entity."""
        return [
            d for d in self._domains.values()
            if d.owner.owner_id == owner
        ]


__all__ = [
    # Identifiers
    "RuntimeId",
    "BootSessionId",
    
    # Durability
    "DurabilityClass",
    "DurabilityRequirements",
    
    # Ownership
    "StateOwner",
    "OwnerIdentity",
    
    # Domains
    "StateDomain",
    "StateDomainId",
    "StateDomainRegistry",
]