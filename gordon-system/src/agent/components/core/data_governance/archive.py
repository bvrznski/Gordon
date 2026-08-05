# Archive Manager - Canonical Authority
# ======================================

"""
Archive manager for archival policies, archive lifecycle management,
and recovery operations.

PHASE 3.7.21 REMEDIATION:
- Records own their archive state (lifecycle_state = ARCHIVED)
- ArchiveManager validates and tracks archives for provenance
"""

import threading
import time
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any
from enum import Enum

from .models import (
    ArchiveRequest,
    ArchiveDecision,
    ArchiveRecord,
    ArchiveEvidence,
)


# =============================================================================
# Storage Backend Interface (for actual archival)
# =============================================================================

class StorageBackend:
    """Interface for archive storage backends."""
    
    async def store(self, data: bytes, location: str) -> None:
        """Store data at the given location."""
        raise NotImplementedError
    
    async def retrieve(self, location: str) -> bytes:
        """Retrieve data from the given location."""
        raise NotImplementedError
    
    async def delete(self, location: str) -> None:
        """Delete data at the given location."""
        raise NotImplementedError
    
    async def exists(self, location: str) -> bool:
        """Check if data exists at the given location."""
        raise NotImplementedError


# =============================================================================
# Archive Manager - PHASE 3.7.21 REMEDIATION
# =============================================================================

class ArchiveManager:
    """
    Canonical authority for archival management.
    
    PHASE 3.7.21 REMEDIATION PRINCIPLES:
    1. Records own their archive state (lifecycle_state = ARCHIVED)
    2. ArchiveManager validates and tracks archives for provenance
    3. No central archive manager - each record owns its lifecycle state
    
    Core Responsibilities:
    1. Archive request validation and processing
    2. Archive record creation with evidence
    3. Recovery from archive
    4. Provenance preservation during archival
    
    Non-Responsibilities (moved to records):
    - Storing archive state on records (InformationRecord.lifecycle_state = ARCHIVED)
    
    Usage:
        # Create manager
        manager = ArchiveManager()
        
        # Process an archive request (record owns its lifecycle state)
        record = await manager.process_archive_request(
            information_id="data-123",
            reason="Retention period expired, archiving for compliance",
            include_provenance=True,
        )
        
        # The record itself has lifecycle_state=LifecycleState.ARCHIVED
    """
    
    def __init__(self) -> None:
        """Initialize the archive manager."""
        self._lock = threading.RLock()
        
        # Archive records by information ID
        self._archives: Dict[str, ArchiveRecord] = {}
        
        # Storage backend (for actual archival)
        self._backend: Optional[StorageBackend] = None
        
        # Archive evidence history for provenance
        self._evidence: Dict[str, List[ArchiveEvidence]] = {}
        
        # Statistics
        self._stats = {
            "total_archived": 0,
            "archival_failures": 0,
        }
    
    def set_backend(self, backend: StorageBackend) -> None:
        """Set the storage backend for archival operations."""
        with self._lock:
            self._backend = backend
    
    async def process_archive_request(
        self,
        information_id: str,
        reason: str,
        priority: int = 1,
        include_provenance: bool = True,
    ) -> ArchiveRecord:
        """
        Process an archive request.
        
        PHASE 3.7.21: The record itself owns its lifecycle state (ARCHIVED).
        This method creates the archive record for provenance.
        
        Args:
            information_id: ID of the information to archive
            reason: Reason for archival
            priority: Priority level (lower = higher)
            include_provenance: Whether to preserve provenance
            
        Returns:
            ArchiveRecord created for provenance tracking
        """
        with self._lock:
            archive_record = ArchiveRecord(
                archive_id=f"archive_{time.monotonic_ns()}",
                information_id=information_id,
                archive_time=time.time(),
                archive_location=f"/archive/{information_id[:2]}/{information_id}",
                provenance_preserved=include_provenance,
                checksum=None,  # Can be computed if needed
            )
            
            self._archives[information_id] = archive_record
            
            # Create evidence for provenance
            decision = ArchiveDecision.APPROVED
            if priority > 1:
                decision = ArchiveDecision.DEFERRED
            
            evidence = ArchiveEvidence(
                information_id=information_id,
                archive_record=archive_record,
                decision=decision,
                timestamp=time.time(),
                operator="archive_manager"
            )
            
            if information_id not in self._evidence:
                self._evidence[information_id] = []
            self._evidence[information_id].append(evidence)
            
            # Update stats
            self._stats["total_archived"] += 1
            
            return archive_record
    
    async def get_archive(self, information_id: str) -> Optional[ArchiveRecord]:
        """Get an archive record by information ID."""
        with self._lock:
            return self._archives.get(information_id)
    
    async def retrieve_from_archive(
        self,
        archive_id: str,
    ) -> Optional[bytes]:
        """
        Retrieve data from archive.
        
        Args:
            archive_id: ID of the archive
            
        Returns:
            Archived data if found and backend available
        """
        with self._lock:
            record = None
            for info_id, archived in self._archives.items():
                if archived.archive_id == archive_id:
                    record = archived
                    break
            
            if record is None or self._backend is None:
                return None
            
            try:
                location = f"/archive/{record.information_id[:2]}/{record.information_id}"
                data = await self._backend.retrieve(location)
                return data
            except Exception:
                return None
    
    async def delete_from_archive(self, archive_id: str) -> bool:
        """
        Delete an item from the archive.
        
        Args:
            archive_id: ID of the archive to delete
            
        Returns:
            True if deleted successfully
        """
        with self._lock:
            record = None
            info_id = None
            for iid, archived in self._archives.items():
                if archived.archive_id == archive_id:
                    record = archived
                    info_id = iid
                    break
            
            if record is None or self._backend is None:
                return False
            
            try:
                location = f"/archive/{record.information_id[:2]}/{record.information_id}"
                await self._backend.delete(location)
                
                # Remove from archives
                if info_id in self._archives:
                    del self._archives[info_id]
                
                return True
            except Exception:
                return False
    
    def get_evidence(self, information_id: str) -> List[ArchiveEvidence]:
        """Get archive evidence for provenance."""
        with self._lock:
            return list(self._evidence.get(information_id, []))
    
    def get_stats(self) -> Dict[str, Any]:
        """Get archive statistics."""
        with self._lock:
            return {
                "total_archived": self._stats["total_archived"],
                "archival_failures": self._stats["archival_failures"],
                "active_archives": len(self._archives),
            }


__all__ = [
    "StorageBackend",
    "ArchiveManager",
]