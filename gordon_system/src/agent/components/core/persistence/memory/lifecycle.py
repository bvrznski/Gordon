# Memory Lifecycle Management
# ============================

"""
Memory lifecycle management for expiration, tombstones, and cleanup.

Provides:
- MemoryExpirationManager: Automatic expiration handling
- MemoryTombstone: Logical deletion tracking with evidence preservation
"""

import threading
import time
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any
from enum import Enum

from .contracts import (
    MemoryRecord,
    MemoryLifecycleState,
    MemoryKind,
)


# =============================================================================
# Expiration Status
# =============================================================================

class ExpirationStatus(Enum):
    """Status of a memory record's expiration."""
    ACTIVE = "active"         # Within retention period
    EXPIRING_SOON = "expiring_soon"  # Will expire soon (within 7 days)
    EXPIRED = "expired"       # Past expiration time


@dataclass(frozen=True)
class ExpirationResult:
    """Result of an expiration check."""
    memory_id: str
    status: ExpirationStatus
    expires_at: Optional[float]
    reason: str = ""


# =============================================================================
# Memory Expiration Manager
# =============================================================================

class MemoryExpirationManager:
    """
    Manages memory record expiration based on retention policies.
    
    Key Responsibilities:
    - Track expiring records
    - Mark expired records appropriately
    - Provide expiration status for queries
    
    NOT responsible for:
    - Deciding retention periods (owned by semantic authority)
    - Automatically deleting expired memories
    - Archival decisions
    
    Usage:
        manager = MemoryExpirationManager()
        
        # Check if record is expired
        result = manager.check_expiration(record)
        
        # Get records that should be expired
        expired = await manager.get_expired_memories(current_time)
    """
    
    def __init__(self, default_retention_seconds: float = 86400.0) -> None:
        """
        Initialize the expiration manager.
        
        Args:
            default_retention_seconds: Default retention period in seconds
                                      (default: 7 days)
        """
        self._lock = threading.RLock()
        self._default_retention = default_retention_seconds
        
        # Track records by expiration time for efficient lookup
        self._expiration_index: Dict[float, List[str]] = {}
        
        # Statistics
        self._stats = {
            "checks": 0,
            "expired_count": 0,
            "expiring_soon_count": 0,
        }
    
    def check_expiration(self, record: MemoryRecord, current_time: Optional[float] = None) -> ExpirationResult:
        """
        Check if a memory record has expired.
        
        Args:
            record: The memory record to check
            current_time: Current timestamp (uses time.time() if None)
            
        Returns:
            ExpirationResult with status and details
        """
        current = current_time or time.time()
        
        # Get expiration time from record or use default
        expires_at = record.expires_at
        
        if expires_at is None:
            # Apply default retention
            created_at = record.created_at
            expires_at = created_at + self._default_retention
        
        with self._lock:
            self._stats["checks"] += 1
            
            if current >= expires_at:
                return ExpirationResult(
                    memory_id=record.memory_id,
                    status=ExpirationStatus.EXPIRED,
                    expires_at=expires_at,
                    reason="Past expiration time"
                )
            
            # Check if expiring soon (within 7 days)
            days_until_expiration = (expires_at - current) / 86400
            if days_until_expiration <= 7:
                return ExpirationResult(
                    memory_id=record.memory_id,
                    status=ExpirationStatus.EXPIRING_SOON,
                    expires_at=expires_at,
                    reason=f"Expiring in {days_until_expiration:.1f} days"
                )
            
            return ExpirationResult(
                memory_id=record.memory_id,
                status=ExpirationStatus.ACTIVE,
                expires_at=expires_at,
                reason="Within retention period"
            )
    
    async def get_expired_memories(self, current_time: Optional[float] = None) -> List[str]:
        """
        Get list of memory IDs that have expired.
        
        Note: This is a placeholder - would query repository in production
        to find records with past expiration times.
        
        Args:
            current_time: Current timestamp (uses time.time() if None)
            
        Returns:
            List of expired memory IDs
        """
        # For now, return empty list - in production would query repository
        # for records where lifecycle_state == ACTIVE and expires_at < current_time
        return []
    
    async def expire_records(
        self,
        record_ids: List[str],
        repository  # MemoryRepository type hint requires forward reference
    ) -> int:
        """
        Expire records by updating their lifecycle state.
        
        Args:
            record_ids: IDs of records to mark as expired
            repository: The memory repository for updates
            
        Returns:
            Number of records successfully expired
        """
        from .repository import MemoryRepository  # Local import
        
        expired_count = 0
        
        with self._lock:
            for record_id in record_ids:
                try:
                    # This would be implemented with actual repository interaction
                    # For now, just count
                    expired_count += 1
                except Exception:
                    continue
            
            self._stats["expired_count"] += expired_count
        
        return expired_count
    
    def get_stats(self) -> Dict[str, Any]:
        """Get expiration manager statistics."""
        with self._lock:
            return {
                "default_retention_seconds": self._default_retention,
                **self._stats,
            }


# =============================================================================
# Memory Tombstone
# =============================================================================

class MemoryTombstone:
    """
    Tracks logical deletion of memory records.
    
    When a record is deleted, instead of removing it completely, we create
    a tombstone that marks the deletion while preserving evidence.
    
    Usage:
        # Delete record (creates tombstone)
        repository = InMemoryMemoryRepository()
        await repository.delete("mem-123")
        
        # Tombstone is created automatically with lifecycle_state = DELETED
    """
    
    def __init__(self) -> None:
        """Initialize the tombstone tracker."""
        self._lock = threading.RLock()
        self._tombstones: Dict[str, Dict[str, Any]] = {}
        
        # Statistics
        self._stats = {
            "tombstones_created": 0,
            "tombstones_resolved": 0,
        }
    
    def record_deletion(
        self,
        memory_id: str,
        deleted_at: Optional[float] = None,
        reason: str = "unknown"
    ) -> Dict[str, Any]:
        """
        Record a logical deletion with tombstone evidence.
        
        Args:
            memory_id: ID of the deleted record
            deleted_at: When deletion occurred (uses time.time() if None)
            reason: Reason for deletion
            
        Returns:
            Tombstone record with deletion evidence
        """
        current_time = deleted_at or time.time()
        
        tombstone = {
            "memory_id": memory_id,
            "deleted_at": current_time,
            "reason": reason,
            "version_at_deletion": None,  # Would be populated by repository
        }
        
        with self._lock:
            self._tombstones[memory_id] = tombstone
            self._stats["tombstones_created"] += 1
        
        return tombstone
    
    def get_tombstone(self, memory_id: str) -> Optional[Dict[str, Any]]:
        """
        Get tombstone information for a deleted record.
        
        Args:
            memory_id: ID of the deleted record
            
        Returns:
            Tombstone record if found, None otherwise
        """
        with self._lock:
            return self._tombstones.get(memory_id)
    
    def is_tombstoned(self, memory_id: str) -> bool:
        """Check if a record has been tombstoned (deleted)."""
        with self._lock:
            return memory_id in self._tombstones
    
    def resolve_tombstone(
        self,
        memory_id: str,
        resolution: str = "verified"
    ) -> Optional[Dict[str, Any]]:
        """
        Resolve a tombstone as verified.
        
        Args:
            memory_id: ID of the deleted record
            resolution: Resolution type (e.g., "verified", "reverted")
            
        Returns:
            Updated tombstone if found, None otherwise
        """
        with self._lock:
            if memory_id not in self._tombstones:
                return None
            
            tombstone = self._tombstones[memory_id]
            tombstone["resolved_at"] = time.time()
            tombstone["resolution"] = resolution
            
            self._stats["tombstones_resolved"] += 1
            return tombstone
    
    def get_stats(self) -> Dict[str, Any]:
        """Get tombstone statistics."""
        with self._lock:
            return {
                "active_tombstones": len(self._tombstones),
                **self._stats,
            }


# =============================================================================
# Lifecycle Coordinator (Interface)
# =============================================================================

class MemoryLifecycleCoordinator:
    """
    Coordinates memory lifecycle operations.
    
    This interface defines the lifecycle coordination contract.
    Implementation is provided by the runtime system.
    
    NOT responsible for:
    - Semantic decisions about retention
    - Archival policies
    - Deletion authorization
    
    This is purely infrastructure for tracking state transitions.
    """
    
    async def transition_state(
        self,
        memory_id: str,
        from_state: MemoryLifecycleState,
        to_state: MemoryLifecycleState,
        reason: str = "unknown"
    ) -> bool:
        """
        Transition a memory record between lifecycle states.
        
        Args:
            memory_id: ID of the record
            from_state: Current state (for validation)
            to_state: Target state
            reason: Reason for transition
            
        Returns:
            True if transition succeeded, False otherwise
        """
        raise NotImplementedError
    
    async def get_lifecycle_history(
        self,
        memory_id: str
    ) -> List[Dict[str, Any]]:
        """Get lifecycle history for a record."""
        raise NotImplementedError


__all__ = [
    "ExpirationStatus",
    "ExpirationResult",
    "MemoryExpirationManager",
    "MemoryTombstone",
    "MemoryLifecycleCoordinator",
]