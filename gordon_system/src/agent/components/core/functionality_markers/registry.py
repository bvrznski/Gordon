# Functionality Registry - Phase 3.13.4
# ======================================

"""
Canonical Functionality Registry for Core class classification records.

This module implements:
    - One canonical registry mapping stable class identities to metadata
    - Duplicate registration protection
    - Registry sealing for production determinism
    - Immutable snapshots for reflection and inventory queries
    - Typed findings for rejected classes
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import (
    TYPE_CHECKING,
    Any,
    Dict,
    List,
    Optional,
    Tuple,
    Type,
    TypeVar,
    Union,
)
from enum import Enum, auto
import threading
import time

from .metaclass import CoreFunctionalityMetadata


if TYPE_CHECKING:
    from . import CoreFunctionality


T = TypeVar("T")


class RegistryState(Enum):
    """Registry lifecycle state."""
    
    CREATED = "created"         # Just initialized
    COLLECTING = "collecting"   # Accepting registrations (development/test)
    SEALED = "sealed"          # Immutable, no new registrations (production)
    INVALID = "invalid"        # Corrupted or in invalid state


@dataclass(frozen=True)
class RegistryEntry:
    """A single registry entry."""
    
    class_identity: str  # Fully qualified class name
    metadata: CoreFunctionalityMetadata
    
    def __hash__(self) -> int:
        return hash(self.class_identity)


@dataclass(frozen=True)
class RejectedRegistration:
    """Record of a registration that was rejected."""
    
    class_identity: str
    reason: str
    findings: Tuple[str, ...]
    timestamp: float = field(default_factory=time.monotonic)


@dataclass(frozen=True)
class RegistrySnapshot:
    """
    Immutable snapshot of registry state.
    
    Used for reflection queries and inventory generation.
    """
    
    schema_version: str
    registry_version: int
    created_at: float  # monotonic timestamp
    sealed: bool
    
    class_count: int
    valid_count: int
    exempt_count: int
    legacy_count: int
    invalid_count: int
    
    entries: Dict[str, RegistryEntry]
    rejected: Tuple[RejectedRegistration, ...]
    
    def get(self, class_identity: str) -> Optional[RegistryEntry]:
        """Get entry by class identity."""
        return self.entries.get(class_identity)
    
    def find_by_marker(self, marker_name: str) -> List[RegistryEntry]:
        """Find all entries with a specific primary marker."""
        results = []
        for entry in self.entries.values():
            if (
                entry.metadata.primary_functionality and
                entry.metadata.primary_functionality.__name__ == marker_name
            ):
                results.append(entry)
        return results
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "schema_version": self.schema_version,
            "registry_version": self.registry_version,
            "created_at": self.created_at,
            "sealed": self.sealed,
            "class_count": self.class_count,
            "valid_count": self.valid_count,
            "exempt_count": self.exempt_count,
            "legacy_count": self.legacy_count,
            "invalid_count": self.invalid_count,
            "entries": {
                k: v.metadata.to_dict()
                for k, v in self.entries.items()
            },
            "rejected": [
                {
                    "class_identity": r.class_identity,
                    "reason": r.reason,
                    "findings": list(r.findings),
                    "timestamp": r.timestamp,
                }
                for r in self.rejected
            ],
        }


@dataclass(frozen=True)
class RegistryStatistics:
    """Registry statistics for diagnostics."""
    
    registered_class_count: int
    valid_direct_count: int
    valid_inherited_count: int
    exempt_count: int
    legacy_count: int
    missing_count: int
    conflict_count: int
    rejected_count: int
    sealed: bool
    registry_version: int
    schema_version: str
    last_failure_category: Optional[str]
    integrity_status: str


class FunctionalityRegistry:
    """
    Thread-safe canonical Functionality registry.
    
    Provides:
        - Stable class identity as key (fully qualified name)
        - One-to-one mapping of class to metadata record
        - Duplicate and conflict detection
        - Registry sealing for production determinism
        - Immutable snapshots for queries
    
    THREAD SAFETY:
        All operations are thread-safe using a lock.
        After sealing, only read operations modify state (snapshots).
    
    PRODUCTION BEHAVIOR:
        Once sealed, the registry becomes immutable.
        Attempted registrations after sealing raise an error.
    """
    
    def __init__(self) -> None:
        self._lock = threading.RLock()
        
        # Main registry: class_identity -> RegistryEntry
        self._entries: Dict[str, RegistryEntry] = {}
        
        # Index by marker for quick lookups
        self._marker_index: Dict[str, List[str]] = {}  # marker_name -> [class_identities]
        
        # Rejected registrations (for invalid classes)
        self._rejected: List[RejectedRegistration] = []
        
        # Registry state
        self._state: RegistryState = RegistryState.CREATED
        
        # Versioning
        self._version: int = 0
        self._schema_version: str = "1.0.0"
        
        # Statistics
        self._last_failure_category: Optional[str] = None
    
    def register(self, metadata: CoreFunctionalityMetadata) -> Tuple[bool, List[str]]:
        """
        Register a class with its Functionality metadata.
        
        Args:
            metadata: The CoreFunctionalityMetadata for the class
            
        Returns:
            Tuple of (success, list_of_findings)
            
        Raises:
            RegistrySealedError: If registry is sealed
            DuplicateRegistrationError: If class already registered with different metadata
        """
        with self._lock:
            if self._state == RegistryState.SEALED:
                raise RegistrySealedError(
                    f"Cannot register after registry is sealed. "
                    f"Class: {metadata.qualified_name}"
                )
            
            findings: List[str] = []
            
            # Check for duplicate registration
            existing_entry = self._entries.get(metadata.qualified_name)
            if existing_entry:
                if existing_entry.metadata != metadata:
                    findings.append(
                        f"DUPLICATE_CONFLICTING_REGISTRATION: "
                        f"Class {metadata.qualified_name} is already registered "
                        f"with different metadata"
                    )
                    self._last_failure_category = "DUPLICATE_CONFLICTING_REGISTRATION"
                    return False, findings
                
                # Same metadata - already registered
                return True, findings
            
            # Create entry and add to registry
            entry = RegistryEntry(
                class_identity=metadata.qualified_name,
                metadata=metadata
            )
            
            self._entries[metadata.qualified_name] = entry
            
            # Update marker index
            if metadata.primary_marker_name:
                if metadata.primary_marker_name not in self._marker_index:
                    self._marker_index[metadata.primary_marker_name] = []
                self._marker_index[metadata.primary_marker_name].append(
                    metadata.qualified_name
                )
            
            # Increment version
            self._version += 1
            
            return True, findings
    
    def reject_registration(
        self,
        class_identity: str,
        reason: str,
        findings: Tuple[str, ...]
    ) -> None:
        """Record a rejected registration with findings."""
        with self._lock:
            if self._state == RegistryState.SEALED:
                # In sealed state, we still record rejections for audit
                pass
            
            rejection = RejectedRegistration(
                class_identity=class_identity,
                reason=reason,
                findings=findings
            )
            self._rejected.append(rejection)
    
    def get(self, class_identity: str) -> Optional[CoreFunctionalityMetadata]:
        """
        Get metadata for a registered class.
        
        Args:
            class_identity: Fully qualified class name
            
        Returns:
            CoreFunctionalityMetadata if registered, None otherwise
        """
        with self._lock:
            entry = self._entries.get(class_identity)
            return entry.metadata if entry else None
    
    def get_by_marker(self, marker_name: str) -> List[CoreFunctionalityMetadata]:
        """Get all classes with a specific primary marker."""
        with self._lock:
            results = []
            for class_id in self._marker_index.get(marker_name, []):
                entry = self._entries.get(class_id)
                if entry:
                    results.append(entry.metadata)
            return results
    
    def snapshot(self) -> RegistrySnapshot:
        """
        Create an immutable snapshot of registry state.
        
        Used for reflection queries and inventory generation.
        """
        with self._lock:
            valid_count = 0
            exempt_count = 0
            legacy_count = 0
            invalid_count = 0
            
            for entry in self._entries.values():
                status = entry.metadata.classification_status
                if status.value.startswith("valid_"):
                    valid_count += 1
                elif "exempt" in status.value:
                    exempt_count += 1
                elif "legacy" in status.value or "pending" in status.value:
                    legacy_count += 1
                else:
                    invalid_count += 1
            
            return RegistrySnapshot(
                schema_version=self._schema_version,
                registry_version=self._version,
                created_at=time.monotonic(),
                sealed=self._state == RegistryState.SEALED,
                class_count=len(self._entries),
                valid_count=valid_count,
                exempt_count=exempt_count,
                legacy_count=legacy_count,
                invalid_count=invalid_count,
                entries=dict(self._entries),
                rejected=tuple(self._rejected),
            )
    
    def seal(self) -> None:
        """Seal the registry - no further registrations allowed."""
        with self._lock:
            if self._state == RegistryState.CREATED:
                self._state = RegistryState.COLLECTING
            
            if self._state == RegistryState.COLLECTING:
                self._state = RegistryState.SEALED
    
    def reset_for_tests(self) -> None:
        """Reset registry to initial state for testing."""
        with self._lock:
            self._entries.clear()
            self._marker_index.clear()
            self._rejected.clear()
            self._version = 0
            self._last_failure_category = None
            self._state = RegistryState.CREATED
    
    def get_statistics(self) -> RegistryStatistics:
        """Get registry statistics for diagnostics."""
        with self._lock:
            valid_direct = 0
            valid_inherited = 0
            exempt = 0
            
            for entry in self._entries.values():
                src = entry.metadata.classification_source
                status = entry.metadata.classification_status
                
                if "direct" in status.value.lower():
                    valid_direct += 1
                elif "inherited" in status.value.lower():
                    valid_inherited += 1
                elif "exempt" in status.value.lower():
                    exempt += 1
            
            return RegistryStatistics(
                registered_class_count=len(self._entries),
                valid_direct_count=valid_direct,
                valid_inherited_count=valid_inherited,
                exempt_count=exempt,
                legacy_count=sum(1 for e in self._entries.values() 
                               if "legacy" in e.metadata.classification_status.value),
                missing_count=sum(1 for e in self._entries.values() 
                                if "missing" in e.metadata.requirement_status.value),
                conflict_count=sum(1 for e in self._entries.values() 
                                 if "conflicting" in e.metadata.classification_status.value),
                rejected_count=len(self._rejected),
                sealed=self._state == RegistryState.SEALED,
                registry_version=self._version,
                schema_version=self._schema_version,
                last_failure_category=self._last_failure_category,
                integrity_status="valid" if self._state != RegistryState.INVALID else "invalid",
            )
    
    @property
    def is_sealed(self) -> bool:
        """Check if registry is sealed."""
        with self._lock:
            return self._state == RegistryState.SEALED
    
    @property
    def size(self) -> int:
        """Return number of registered classes."""
        with self._lock:
            return len(self._entries)


class RegistrySealedError(RuntimeError):
    """Raised when attempting to register after registry is sealed."""


class DuplicateRegistrationError(RuntimeError):
    """Raised when attempting duplicate registration with different metadata."""


# =============================================================================
# REFLECTION API
# =============================================================================


def get_functionality_metadata(
    class_or_identity: Union[Type[Any], str],
    registry: FunctionalityRegistry
) -> Optional[CoreFunctionalityMetadata]:
    """
    Get Functionality metadata for a class.
    
    Args:
        class_or_identity: Class object or fully qualified name
        registry: The FunctionalityRegistry to query
        
    Returns:
        CoreFunctionalityMetadata if found, None otherwise
    """
    if isinstance(class_or_identity, type):
        identity = f"{class_or_identity.__module__}.{class_or_identity.__qualname__}"
    else:
        identity = class_or_identity
    
    return registry.get(identity)


def get_primary_functionality(
    class_or_identity: Union[Type[Any], str],
    registry: FunctionalityRegistry
) -> Optional[Type["CoreFunctionality"]]:
    """Get primary Functionality marker for a class."""
    metadata = get_functionality_metadata(class_or_identity, registry)
    return metadata.primary_functionality if metadata else None


def list_by_functionality(
    marker_name: str,
    registry: FunctionalityRegistry
) -> List[CoreFunctionalityMetadata]:
    """List all classes with a specific primary functionality."""
    return registry.get_by_marker(marker_name)


def snapshot_functionality_registry(
    registry: FunctionalityRegistry
) -> RegistrySnapshot:
    """Create an immutable snapshot of the registry."""
    return registry.snapshot()


__all__ = [
    # States and types
    "RegistryState",
    "RegistryEntry",
    "RejectedRegistration",
    "RegistrySnapshot",
    "RegistryStatistics",
    
    # Registry class
    "FunctionalityRegistry",
    "RegistrySealedError",
    "DuplicateRegistrationError",
    
    # Reflection API functions
    "get_functionality_metadata",
    "get_primary_functionality",
    "list_by_functionality",
    "snapshot_functionality_registry",
]