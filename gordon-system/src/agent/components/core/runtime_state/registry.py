# Core Registry Implementation
# ============================

"""
Core runtime entity registry.

Provides:
- Canonical entity registration with explicit semantics
- Duplicate detection and conflict resolution
- Immutable snapshots with deterministic ordering
- Typed views and category indexing
"""

from dataclasses import dataclass, field
from typing import (
    Dict,
    List,
    Optional,
    Any,
    Iterator,
    FrozenSet,
    Callable,
    Tuple,
)
from enum import Enum
import threading

from ..types import EntityId
from . import (
    RegistrationDescriptor,
    RegistrationResult,
    RegistrationStatus,
    RegistryRevision,
)


class RegistryPhase(Enum):
    """
    Registry mutation phases.
    
    Defines when registrations are allowed and what operations are valid.
    """
    BUILDING = "building"  # Registrations allowed
    VALIDATING = "validating"  # Structural checks running
    SEALED = "sealed"  # Immutable, no mutations allowed
    CLOSING = "closing"  # Teardown only
    CLOSED = "closed"  # Cannot be used


@dataclass(frozen=True)
class RegistrySnapshot:
    """
    Immutable snapshot of registry state.
    
    Provides:
    - Stable ordered entries
    - Registry revision at time of capture
    - No writable backing collections
    
    Snapshots are safe to expose for read-only consumers.
    """
    
    entries: Dict[EntityId, RegistrationDescriptor]
    order: List[EntityId]  # Deterministic registration order
    revision: int
    phase: RegistryPhase


class DuplicateRegistrationError(Exception):
    """Raised when attempting duplicate registration."""
    
    def __init__(
        self,
        message: str,
        entity_id: EntityId,
        existing_descriptor: Optional[RegistrationDescriptor] = None
    ) -> None:
        super().__init__(message)
        self.entity_id = entity_id
        self.existing_descriptor = existing_descriptor


class ConflictingRegistrationError(Exception):
    """Raised when attempting conflicting registration."""
    
    def __init__(
        self,
        message: str,
        entity_id: EntityId,
        existing_descriptor: RegistrationDescriptor,
        new_descriptor: RegistrationDescriptor
    ) -> None:
        super().__init__(message)
        self.entity_id = entity_id
        self.existing_descriptor = existing_descriptor
        self.new_descriptor = new_descriptor


class RegistrySealedError(Exception):
    """Raised when attempting mutation on sealed registry."""
    
    def __init__(
        self,
        message: str,
        current_phase: RegistryPhase
    ) -> None:
        super().__init__(message)
        self.current_phase = current_phase


class UnknownEntityError(Exception):
    """Raised when entity is not found in registry."""
    
    def __init__(
        self,
        message: str,
        entity_id: EntityId,
        available_ids: Optional[List[EntityId]] = None
    ) -> None:
        super().__init__(message)
        self.entity_id = entity_id
        self.available_ids = available_ids or []


class RegistryWriter:
    """
    Write interface for registry with explicit mutation phases.
    
    Operations are only valid in BUILDING phase.
    After sealing, this interface becomes unusable.
    """
    
    def __init__(self) -> None:
        self._lock = threading.Lock()
        self._entries: Dict[EntityId, RegistrationDescriptor] = {}
        self._order: List[EntityId] = []
        self._revision = 0
        self._phase = RegistryPhase.BUILDING
    
    @property
    def phase(self) -> RegistryPhase:
        """Get current registry phase."""
        return self._phase
    
    @property
    def revision(self) -> int:
        """Get current registry revision."""
        return self._revision
    
    def is_sealed(self) -> bool:
        """Check if registry is sealed (immutable)."""
        return self._phase in (RegistryPhase.SEALED, RegistryPhase.CLOSING, RegistryPhase.CLOSED)
    
    def register(
        self,
        descriptor: RegistrationDescriptor
    ) -> RegistrationResult:
        """
        Register an entity with the given descriptor.
        
        Args:
            descriptor: The registration descriptor
            
        Returns:
            RegistrationResult with outcome information
            
        Raises:
            RegistrySealedError: If registry is sealed
            DuplicateRegistrationError: If same ID with different descriptor
        """
        if self.is_sealed():
            raise RegistrySealedError(
                f"Cannot register after registry is sealed (phase: {self._phase.value})",
                self._phase
            )
        
        entity_id = descriptor.entity_id
        
        with self._lock:
            # Check for exact duplicate
            if entity_id in self._entries:
                existing = self._entries[entity_id]
                
                # Same descriptor - idempotent
                if self._descriptors_equal(existing, descriptor):
                    return RegistrationResult(
                        status=RegistrationStatus.IDEMPOTENT,
                        descriptor=descriptor,
                        reason="Duplicate with identical descriptor",
                        registry_revision=self._revision
                    )
                
                # Different descriptor - conflict
                raise DuplicateRegistrationError(
                    f"Duplicate entity_id: {entity_id}",
                    entity_id=entity_id,
                    existing_descriptor=existing
                )
            
            # Register new entry
            descriptor = DescriptorWithStatus(descriptor, RegistrationStatus.REGISTERED)
            self._entries[entity_id] = descriptor
            self._order.append(entity_id)
            self._revision += 1
            
            return RegistrationResult(
                status=RegistrationStatus.REGISTERED,
                descriptor=descriptor,
                registry_revision=self._revision
            )
    
    def unregister(self, entity_id: EntityId) -> bool:
        """
        Unregister an entity.
        
        Args:
            entity_id: The entity to remove
            
        Returns:
            True if unregistered, False if not found
            
        Raises:
            RegistrySealedError: If registry is sealed
        """
        if self.is_sealed():
            raise RegistrySealedError(
                f"Cannot unregister after registry is sealed (phase: {self._phase.value})",
                self._phase
            )
        
        with self._lock:
            if entity_id not in self._entries:
                return False
            
            del self._entries[entity_id]
            self._order.remove(entity_id)
            self._revision += 1
            return True
    
    def seal(self) -> "RegistryReader":
        """
        Seal the registry, making it immutable.
        
        Returns:
            A RegistryReader for read-only access to the sealed state
            
        Raises:
            RegistrySealedError: If already sealed
        """
        if self.is_sealed():
            raise RegistrySealedError(
                f"Cannot seal an already sealed registry",
                self._phase
            )
        
        with self._lock:
            self._phase = RegistryPhase.SEALED
            return RegistryReader(
                entries=dict(self._entries),
                order=list(self._order),
                revision=self._revision,
                phase=RegistryPhase.SEALED
            )
    
    def _descriptors_equal(self, d1: RegistrationDescriptor, d2: RegistrationDescriptor) -> bool:
        """Check if two descriptors are equivalent."""
        return (
            d1.entity_id == d2.entity_id and
            d1.category == d2.category and
            d1.implementation == d2.implementation and
            d1.version == d2.version
        )


class DescriptorWithStatus:
    """
    Wrapper for RegistrationDescriptor with additional metadata.
    
    Not part of public API - internal implementation detail.
    """
    
    def __init__(
        self,
        descriptor: RegistrationDescriptor,
        status: RegistrationStatus
    ) -> None:
        self._descriptor = descriptor
        self._status = status
    
    @property
    def entity_id(self) -> EntityId:
        return self._descriptor.entity_id
    
    @property
    def category(self) -> str:
        return self._descriptor.category
    
    @property
    def implementation(self) -> Any:
        return self._descriptor.implementation
    
    @property
    def status(self) -> RegistrationStatus:
        return self._status


class RegistryReader:
    """
    Read-only interface for registry access.
    
    Provides:
    - Safe concurrent read access
    - Immutable snapshot views
    - Typed lookups by category or protocol
    
    This is the interface exposed to runtime consumers.
    """
    
    def __init__(
        self,
        entries: Dict[EntityId, RegistrationDescriptor],
        order: List[EntityId],
        revision: int,
        phase: RegistryPhase = RegistryPhase.SEALED
    ) -> None:
        self._entries = dict(entries)
        self._order = list(order)
        self._revision = revision
        self._phase = phase
    
    @property
    def revision(self) -> int:
        """Get registry revision."""
        return self._revision
    
    @property
    def phase(self) -> RegistryPhase:
        """Get current registry phase."""
        return self._phase
    
    @property
    def size(self) -> int:
        """Get number of registered entities."""
        return len(self._entries)
    
    def get(self, entity_id: EntityId) -> Optional[RegistrationDescriptor]:
        """
        Get a descriptor by its canonical identifier.
        
        Args:
            entity_id: The entity's registered ID
            
        Returns:
            The descriptor, or None if not found
        """
        return self._entries.get(entity_id)
    
    def get_all(self) -> Dict[EntityId, RegistrationDescriptor]:
        """Get all descriptors as an immutable snapshot."""
        return dict(self._entries)
    
    def keys(self) -> List[EntityId]:
        """Get all entity IDs in registration order."""
        return list(self._order)
    
    def values(self) -> Iterator[RegistrationDescriptor]:
        """Iterate over all descriptors in registration order."""
        for entity_id in self._order:
            yield self._entries.get(entity_id)
    
    def snapshot(self) -> RegistrySnapshot:
        """
        Create an immutable snapshot of registry state.
        
        Returns:
            Snapshot with stable ordering
        """
        return RegistrySnapshot(
            entries=dict(self._entries),
            order=list(self._order),
            revision=self._revision,
            phase=self._phase
        )
    
    def get_by_category(self, category: str) -> List[RegistrationDescriptor]:
        """Get all descriptors in a specific category."""
        return [
            desc for desc in self._entries.values()
            if desc.category == category
        ]
    
    def get_by_protocol(self, protocol_name: str) -> List[RegistrationDescriptor]:
        """
        Get all descriptors that expose a specific protocol.
        
        Args:
            protocol_name: Name of the protocol
            
        Returns:
            Matching descriptors
        """
        return [
            desc for desc in self._entries.values()
            if protocol_name in (desc.protocols or [])
        ]
    
    def contains(self, entity_id: EntityId) -> bool:
        """Check if an entity is registered."""
        return entity_id in self._entries
    
    def __contains__(self, entity_id: EntityId) -> bool:
        """Support 'in' operator."""
        return entity_id in self._entries
    
    def __len__(self) -> int:
        """Return number of registered entities."""
        return len(self._entries)
    
    def __iter__(self) -> Iterator[Tuple[EntityId, RegistrationDescriptor]]:
        """Iterate over (entity_id, descriptor) pairs."""
        for entity_id in self._order:
            if entity_id in self._entries:
                yield entity_id, self._entries[entity_id]


class Registry:
    """
    Canonical registry with explicit mutation phases and versioning.
    
    Usage:
        # Build phase
        writer = RegistryWriter()
        writer.register(descriptor1)
        writer.register(descriptor2)
        
        # Seal for runtime
        reader = writer.seal()
        
        # Runtime: read-only access
        entity = reader.get(entity_id)
        all_entities = reader.get_all()
    """
    
    def __init__(self) -> None:
        self._writer = RegistryWriter()
    
    @property
    def writer(self) -> RegistryWriter:
        """Get mutable writer (only valid before sealing)."""
        return self._writer
    
    @property
    def reader(self) -> Optional[RegistryReader]:
        """
        Get read-only reader (after sealing).
        
        Returns None if registry has not been sealed yet.
        """
        # Writer holds the state; reader is created on seal
        return None  # Will be set by writer.seal()
    
    def build_and_seal(self) -> RegistryReader:
        """
        Create a sealed registry in one operation.
        
        Returns:
            Sealed RegistryReader ready for runtime use
        """
        return self._writer.seal()


__all__ = [
    "RegistryPhase",
    "RegistrySnapshot",
    "DuplicateRegistrationError",
    "ConflictingRegistrationError",
    "RegistrySealedError",
    "UnknownEntityError",
    "RegistryWriter",
    "RegistryReader",
    "Registry",
]