# Gordon Phase 5.7.4-I: Temporal Context Engine - Retention
# ===============================================================================
"""
Retention module for bounded previous-generation context references.
"""

from __future__ import annotations

import time
from dataclasses import dataclass, field
from typing import Tuple, Dict, Optional


@dataclass(frozen=True)
class RetentionRecord:
    """
    Immutable record of a retained previous-generation context reference.
    
    Retention records maintain bounded references to prior Experiential Field
    generations that remain immediately available for continuity preservation.
    
    Key properties:
        - Bounded: Limited to MAX_RETENTION_HISTORY generations
        - Non-duplicating: Never duplicates memory ownership
        - Provenance-preserving: Links to source generation for lineage tracking
    """
    
    retention_id: str = field(default_factory=lambda: f"ret-{time.time()}")
    """Unique identifier for this retention record."""
    
    field_generation: int = 0
    """Generation number of the retained Experiential Field context."""
    
    field_context_id: Optional[str] = None
    """Context ID reference to the retained generation."""
    
    timestamp_utc: float = field(default_factory=time.time)
    """When this retention record was created."""
    
    provenance: Optional[str] = None
    """Provenance chain linking back to source context."""
    
    trust_level: float = 1.0
    """Trust level of this retention reference (0.0-1.0)."""
    
    privacy_classification: str = "internal"
    """Privacy classification for this record."""
    
    @classmethod
    def from_field_snapshot(
        cls,
        field_generation: int,
        field_context_id: Optional[str] = None,
        provenance: Optional[str] = None,
        trust_level: float = 1.0,
    ) -> "RetentionRecord":
        """
        Create a retention record from an Experiential Field snapshot.
        
        Args:
            field_generation: Generation number of the EF context
            field_context_id: Context ID reference (optional)
            provenance: Provenance chain (optional)
            trust_level: Trust level for this reference
            
        Returns:
            New RetentionRecord with the provided values
        """
        return cls(
            field_generation=field_generation,
            field_context_id=field_context_id,
            provenance=provenance,
            trust_level=trust_level,
        )


class RetentionRegistry:
    """
    Registry for bounded retention records.
    
    Maintains a bounded collection of retention references to previous
    generations, enforcing maximum history limits and ensuring proper cleanup.
    """
    
    def __init__(self, max_history: int = 10):
        """
        Initialize the retention registry.
        
        Args:
            max_history: Maximum number of retention records to maintain
        """
        self._max_history: int = max_history
        """Maximum history window size."""
        
        self._records: Dict[str, RetentionRecord] = {}
        """Internal storage for retention records by ID."""
        
        self._generations: Dict[int, str] = {}
        """Map from generation number to record ID for lookup."""
    
    @property
    def registered_count(self) -> int:
        """Get the current count of registered retention records."""
        return len(self._records)
    
    @property
    def history_size(self) -> int:
        """Get the current size of the history window."""
        return self.registered_count
    
    def register(
        self,
        record: RetentionRecord,
    ) -> Tuple[bool, Optional[str]]:
        """
        Register a retention record.
        
        Enforces bounded history by removing oldest entries if necessary.
        
        Args:
            record: The retention record to register
            
        Returns:
            Tuple of (success, error_message if failed)
        """
        # Remove oldest records if at capacity
        while len(self._records) >= self._max_history:
            # Find and remove the oldest record
            oldest_id = min(
                self._records.keys(),
                key=lambda k: self._records[k].timestamp_utc
            )
            self._unregister(oldest_id)
        
        # Register the new record
        self._records[record.retention_id] = record
        self._generations[record.field_generation] = record.retention_id
        
        return True, None
    
    def unregister(self, generation: int) -> Tuple[bool, Optional[str]]:
        """
        Unregister a retention record by its field generation.
        
        Args:
            generation: Generation number of the record to remove
            
        Returns:
            Tuple of (success, error_message if failed)
        """
        record_id = self._generations.get(generation)
        if record_id is None:
            return False, f"Retention record for generation {generation} not found"
        
        self._unregister(record_id)
        return True, None
    
    def _unregister(self, record_id: str) -> None:
        """Internal unregister that removes both mappings."""
        record = self._records.pop(record_id, None)
        if record is not None and record.field_generation in self._generations:
            del self._generations[record.field_generation]
    
    def get(self, generation: int) -> Optional[RetentionRecord]:
        """
        Get a retention record by field generation.
        
        Args:
            generation: Generation number to look up
            
        Returns:
            RetentionRecord if found, None otherwise
        """
        record_id = self._generations.get(generation)
        return self._records.get(record_id) if record_id else None
    
    def get_all(self) -> Tuple[RetentionRecord, ...]:
        """Get all registered retention records as an immutable tuple."""
        return tuple(sorted(
            self._records.values(),
            key=lambda r: r.field_generation
        ))
    
    def get_recent_history(self, count: int = 5) -> Tuple[RetentionRecord, ...]:
        """
        Get the most recent retention history entries.
        
        Args:
            count: Number of recent entries to return
            
        Returns:
            Tuple of most recent retention records (sorted by generation)
        """
        all_records = self.get_all()
        if len(all_records) <= count:
            return all_records
        return all_records[-count:]
    
    def clear(self) -> None:
        """Clear all registered retention records."""
        self._records.clear()
        self._generations.clear()


@dataclass(frozen=True)
class RetentionBoundaries:
    """
    Bounded constraints for retention configuration.
    
    Defines the upper and lower bounds of the retention window,
    including history limits and timeout constraints.
    """
    
    max_history: int = 10
    """Maximum number of generations to retain."""
    
    min_history: int = 1
    """Minimum number of generations to retain (for continuity)."""
    
    ttl_seconds: float = 3600.0
    """Time-to-live for retention records in seconds."""
    
    @classmethod
    def default(cls) -> "RetentionBoundaries":
        """Get the default retention boundaries."""
        return cls()
    
    @classmethod
    def strict(cls) -> "RetentionBoundaries":
        """Get strict boundaries (minimal history, short TTL)."""
        return cls(max_history=3, ttl_seconds=60.0)
    
    @classmethod
    def generous(cls) -> "RetentionBoundaries":
        """Get generous boundaries (maximal history, long TTL)."""
        return cls(max_history=20, ttl_seconds=7200.0)


__all__: Tuple[str, ...] = (
    "RetentionRecord",
    "RetentionRegistry",
    "RetentionBoundaries",
)