# Functionality Inventory - Phase 3.13.4
# ======================================

"""
Inventory APIs for querying Functionality classification.

Provides deterministic inventories grouped by:
    - Primary functionality markers
    - Exemption categories
    - Classification status
"""

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Tuple
import threading

from .metaclass import CoreFunctionalityMetadata
from .registry import FunctionalityRegistry


@dataclass(frozen=True)
class InventoryGroup:
    """A group of classes in the inventory."""
    
    category: str  # e.g., "ForCore", "Exempt", "Missing"
    count: int
    entries: Tuple[CoreFunctionalityMetadata, ...]
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "category": self.category,
            "count": self.count,
            "entries": [
                e.to_dict() if hasattr(e, "to_dict") else str(e)
                for e in self.entries
            ],
        }


class FunctionalityInventory:
    """
    Inventory of all classified classes.
    
    Provides deterministic grouping and querying of classes by:
        - Primary functionality marker
        - Exemption kind
        - Classification status
    
    THREAD SAFETY:
        All operations are thread-safe using a lock.
    """
    
    def __init__(self, registry: FunctionalityRegistry):
        self._lock = threading.RLock()
        self._registry = registry
        self._groups: Dict[str, List[CoreFunctionalityMetadata]] = {}
        self._last_snapshot_version = -1
    
    def _ensure_updated(self) -> None:
        """Ensure inventory is updated with current registry state."""
        with self._lock:
            # Check if snapshot has changed
            registry_stats = self._registry.get_statistics()
            
            if registry_stats.registry_version > self._last_snapshot_version:
                self._rebuild_groups()
                self._last_snapshot_version = registry_stats.registry_version
    
    def _rebuild_groups(self) -> None:
        """Rebuild all inventory groups from current registry state."""
        # Clear existing groups
        self._groups.clear()
        
        # Get snapshot from registry
        snapshot = self._registry.snapshot()
        
        for entry in snapshot.entries.values():
            metadata = entry.metadata
            
            # Determine group category based on primary marker or status
            if metadata.primary_marker_name:
                group_key = f"by_{metadata.primary_marker_name}"
            elif "exempt" in metadata.classification_status.value:
                group_key = "by_exempt"
            elif "conflicting" in metadata.classification_status.value:
                group_key = "by_conflicting"
            else:
                group_key = "by_unclassified"
            
            if group_key not in self._groups:
                self._groups[group_key] = []
            
            self._groups[group_key].append(metadata)
    
    def get_group(self, category: str) -> InventoryGroup:
        """Get inventory group by category."""
        with self._lock:
            self._ensure_updated()
            
            entries = tuple(self._groups.get(category, []))
            
            return InventoryGroup(
                category=category,
                count=len(entries),
                entries=entries,
            )
    
    def list_by_functionality(self, marker_name: str) -> Tuple[CoreFunctionalityMetadata, ...]:
        """List all classes with a specific primary functionality."""
        with self._lock:
            self._ensure_updated()
            
            group_key = f"by_{marker_name}"
            return tuple(self._groups.get(group_key, []))
    
    def list_exempted(self) -> Tuple[CoreFunctionalityMetadata, ...]:
        """List all exempted classes."""
        with self._lock:
            self._ensure_updated()
            
            return tuple(self._groups.get("by_exempt", []))
    
    def list_conflicting(self) -> Tuple[CoreFunctionalityMetadata, ...]:
        """List all conflicting classifications."""
        with self._lock:
            self._ensure_updated()
            
            return tuple(self._groups.get("by_conflicting", []))
    
    def list_unclassified(self) -> Tuple[CoreFunctionalityMetadata, ...]:
        """List all unclassified classes (no primary marker)."""
        with self._lock:
            self._ensure_updated()
            
            return tuple(self._groups.get("by_unclassified", []))
    
    def get_all_groups(self) -> Dict[str, InventoryGroup]:
        """Get all inventory groups."""
        with self._lock:
            self._ensure_updated()
            
            result = {}
            for key, entries in self._groups.items():
                result[key] = InventoryGroup(
                    category=key,
                    count=len(entries),
                    entries=tuple(entries),
                )
            return result
    
    def get_statistics(self) -> Dict[str, int]:
        """Get inventory statistics."""
        with self._lock:
            self._ensure_updated()
            
            stats: Dict[str, int] = {}
            for key, entries in self._groups.items():
                stats[key] = len(entries)
            return stats


def create_functionality_inventory(registry: FunctionalityRegistry) -> FunctionalityInventory:
    """
    Create a new functionality inventory from a registry.
    
    Args:
        registry: The FunctionalityRegistry to build inventory from
        
    Returns:
        FunctionalityInventory instance
    """
    return FunctionalityInventory(registry)


__all__ = [
    # Dataclasses
    "InventoryGroup",
    
    # Classes
    "FunctionalityInventory",
    
    # Factory functions
    "create_functionality_inventory",
]