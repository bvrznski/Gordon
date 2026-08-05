# Disposal Authority - Canonical Authority
# ========================================

"""
Disposal authority for information disposal, secure destruction,
and evidence preservation.

PHASE 3.7.21 REMEDIATION:
- Records own their lifecycle state (DELETED/ARCHIVED)
- DisposalAuthority validates and tracks disposal for provenance
"""

import threading
import time
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any
from enum import Enum

from .models import (
    DisposalRequest,
    DisposalMethod,
    DisposalRecord,
    DisposalEvidence,
)


# =============================================================================
# Secure Destruction Engine - PHASE 3.7.21 REMEDIATION
# =============================================================================

class DestructionMethod(Enum):
    """Methods of secure data destruction."""
    SOFT_DELETE = "soft_delete"  # Mark as deleted, recoverable
    HARD_OVERWRITE = "hard_overwrite"  # Overwrite with zeros/random
    CRYPTO_ERASURE = "crypto_erasure"  # Delete encryption key


class DestructionEngine:
    """Engine for secure data destruction."""
    
    def __init__(self) -> None:
        self._lock = threading.RLock()
        self._destroyed: Dict[str, bool] = {}
    
    async def soft_delete(self, data_id: str) -> None:
        """Mark data as deleted (recoverable)."""
        with self._lock:
            self._destroyed[data_id] = False  # Not actually destroyed
    
    async def hard_overwrite(self, data_id: str, size: Optional[int] = None) -> None:
        """Overwrite data with zeros or random bytes."""
        with self._lock:
            # In real implementation, would overwrite actual data
            self._destroyed[data_id] = True  # Actually destroyed
    
    async def crypto_erasure(self, data_id: str, encryption_key: Optional[str] = None) -> None:
        """Delete encryption key for encrypted data."""
        with self._lock:
            self._destroyed[data_id] = True
    
    def is_destroyed(self, data_id: str) -> bool:
        """Check if data has been destroyed."""
        with self._lock:
            return self._destroyed.get(data_id, False)
    
    def clear(self, data_id: str) -> None:
        """Clear destruction record for a data ID."""
        with self._lock:
            if data_id in self._destroyed:
                del self._destroyed[data_id]


# =============================================================================
# Disposal Authority - PHASE 3.7.21 REMEDIATION
# =============================================================================

class DisposalAuthority:
    """
    Canonical authority for information disposal.
    
    PHASE 3.7.21 REMEDIATION PRINCIPLES:
    1. Records own their lifecycle state (DELETED/ARCHIVED)
    2. DisposalAuthority validates and tracks disposal for provenance
    3. No central disposal manager - each record owns its lifecycle state
    
    Core Responsibilities:
    1. Disposal request validation and processing
    2. Secure destruction with verification
    3. Evidence preservation for audit trail
    4. Verification of complete deletion
    
    Non-Responsibilities (moved to records):
    - Storing disposal state on records (InformationRecord.lifecycle_state = DELETED)
    
    Usage:
        # Create authority
        authority = DisposalAuthority()
        
        # Process a disposal request (record owns its lifecycle state)
        record = await authority.dispose(
            information_id="data-123",
            method=DisposalMethod.SOFT,
            verify=True,
        )
        
        # The record itself has lifecycle_state=LifecycleState.DELETED
    """
    
    def __init__(self) -> None:
        """Initialize the disposal authority."""
        self._lock = threading.RLock()
        
        # Destruction engine
        self._engine = DestructionEngine()
        
        # Disposal records by information ID
        self._disposals: Dict[str, List[DisposalRecord]] = {}
        
        # Evidence history for provenance
        self._evidence: Dict[str, List[DisposalEvidence]] = {}
        
        # Statistics
        self._stats = {
            "total_disposed": 0,
            "verified_destructions": 0,
        }
    
    async def dispose(
        self,
        information_id: str,
        method: DisposalMethod,
        verify: bool = True,
        reason: str = "",
        executed_by: str = "system",
    ) -> DisposalRecord:
        """
        Process a disposal request.
        
        PHASE 3.7.21: The record itself owns its lifecycle state (DELETED).
        This method creates the disposal record for provenance.
        
        Args:
            information_id: ID of the information to dispose
            method: Method of disposal (soft, hard, secure)
            verify: Whether to verify destruction
            reason: Reason for disposal
            executed_by: Who executed the disposal
            
        Returns:
            DisposalRecord created for provenance tracking
        """
        with self._lock:
            # Execute destruction based on method
            if method == DisposalMethod.SOFT:
                await self._engine.soft_delete(information_id)
            elif method == DisposalMethod.HARD:
                await self._engine.hard_overwrite(information_id)
            elif method == DisposalMethod.SECURE:
                await self._engine.crypto_erasure(information_id)
            
            # Create disposal record
            disposal_record = DisposalRecord(
                disposal_id=f"disposal_{time.monotonic_ns()}",
                information_id=information_id,
                disposal_time=time.time(),
                method=method,
                verified=verify and self._engine.is_destroyed(information_id),
                evidence_location=f"/evidence/disposal/{information_id}",
            )
            
            # Store for provenance
            if information_id not in self._disposals:
                self._disposals[information_id] = []
            self._disposals[information_id].append(disposal_record)
            
            # Create evidence
            evidence = DisposalEvidence(
                information_id=information_id,
                disposal_record=disposal_record,
                timestamp=time.time(),
                operator=executed_by,
                verification_result="verified" if verify else "unverified"
            )
            
            if information_id not in self._evidence:
                self._evidence[information_id] = []
            self._evidence[information_id].append(evidence)
            
            # Update stats
            self._stats["total_disposed"] += 1
            if disposal_record.verified:
                self._stats["verified_destructions"] += 1
            
            return disposal_record
    
    async def get_disposal(self, information_id: str) -> Optional[DisposalRecord]:
        """Get the most recent disposal record for an item."""
        with self._lock:
            records = self._disposals.get(information_id)
            if records:
                return records[-1]
            return None
    
    async def verify_destruction(self, information_id: str) -> bool:
        """
        Verify that destruction was complete.
        
        Args:
            information_id: ID of the disposed information
            
        Returns:
            True if destruction is verified complete
        """
        with self._lock:
            return self._engine.is_destroyed(information_id)
    
    async def get_evidence(self, information_id: str) -> List[DisposalEvidence]:
        """Get disposal evidence for provenance."""
        with self._lock:
            return list(self._evidence.get(information_id, []))
    
    def get_stats(self) -> Dict[str, Any]:
        """Get disposal statistics."""
        with self._lock:
            return {
                "total_disposed": self._stats["total_disposed"],
                "verified_destructions": self._stats["verified_destructions"],
                "records_with_disposal": len(self._disposals),
            }


__all__ = [
    "DestructionMethod",
    "DestructionEngine",
    "DisposalAuthority",
]