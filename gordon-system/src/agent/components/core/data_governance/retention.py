# Retention Coordinator - Canonical Authority
# ===========================================

"""
Retention coordinator for retention policies, schedule management,
and expiration tracking.

PHASE 3.7.21 REMEDIATION:
- Records own their retention schedules (part of InformationRecord)
- Coordinator validates and tracks retention state for provenance
"""

import threading
import time
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any
from enum import Enum

from .models import (
    RetentionPolicy,
    RetentionSchedule,
    ExpirationStatus,
    RetentionExtension,
)


# =============================================================================
# Retention Scheduler - PHASE 3.7.21 REMEDIATION
# =============================================================================

class RetentionScheduler:
    """Scheduling engine for retention operations."""
    
    def __init__(self) -> None:
        self._schedules: Dict[str, RetentionSchedule] = {}
        self._lock = threading.RLock()
    
    def add_schedule(self, schedule: RetentionSchedule) -> None:
        """Add a retention schedule."""
        with self._lock:
            self._schedules[schedule.information_id] = schedule
    
    def get_schedule(self, information_id: str) -> Optional[RetentionSchedule]:
        """Get a retention schedule by information ID."""
        with self._lock:
            return self._schedules.get(information_id)
    
    def remove_schedule(self, information_id: str) -> None:
        """Remove a retention schedule."""
        with self._lock:
            if information_id in self._schedules:
                del self._schedules[information_id]
    
    @property
    def scheduled_count(self) -> int:
        """Get count of active schedules."""
        with self._lock:
            return len(self._schedules)
    
    def get_expiring_soon(self, within_days: int = 7) -> List[str]:
        """
        Get information IDs that will expire soon.
        
        Args:
            within_days: Number of days to look ahead
            
        Returns:
            List of information IDs expiring within the specified period
        """
        with self._lock:
            now = time.time()
            threshold = now + (within_days * 86400)
            
            return [
                info_id for info_id, schedule in self._schedules.items()
                if schedule.expires_at is not None and 
                   now <= schedule.expires_at <= threshold
            ]
    
    def get_expired(self) -> List[str]:
        """Get information IDs that have expired."""
        with self._lock:
            now = time.time()
            
            return [
                info_id for info_id, schedule in self._schedules.items()
                if schedule.expires_at is not None and 
                   now > schedule.expires_at
            ]
    
    def get_all_scheduled(self) -> List[RetentionSchedule]:
        """Get all scheduled information."""
        with self._lock:
            return list(self._schedules.values())


# =============================================================================
# Retention Coordinator - PHASE 3.7.21 REMEDIATION
# =============================================================================

class RetentionCoordinator:
    """
    Canonical authority for retention policy management.
    
    PHASE 3.7.21 REMEDIATION PRINCIPLES:
    1. Records own their retention schedules (RetentionSchedule in InformationRecord)
    2. Coordinator validates and tracks retention state for provenance
    3. No central retention manager - each record has its own schedule
    
    Core Responsibilities:
    1. Retention policy configuration and validation
    2. Schedule creation and validation
    3. Expiration tracking for observability
    4. Extension request handling
    
    Non-Responsibilities (moved to records):
    - Storing retention schedules on records (InformationRecord.retention_schedule)
    
    Usage:
        # Create coordinator
        coordinator = RetentionCoordinator()
        
        # Record a schedule for provenance (record owns the actual field)
        policy = RetentionPolicy(policy_id="default", retention_days=365)
        
        # The record itself owns its retention schedule:
        record = InformationRecord(
            information_id="data-123",
            content_hash="hash123",
            owner=OwnerIdentity(...),
            classification=ClassificationLevel.INTERNAL,
            lifecycle_state=LifecycleState.ACTIVE,
            retention_schedule=RetentionSchedule(
                information_id="data-123",
                policy=policy,
            ),
        )
        
        # Coordinator can validate and track for observability
        coordinator.validate_policy(policy)
    """
    
    def __init__(self) -> None:
        """Initialize the retention coordinator."""
        self._lock = threading.RLock()
        
        # Retention scheduler
        self._scheduler = RetentionScheduler()
        
        # Policy history (for provenance)
        self._policies: Dict[str, List[RetentionPolicy]] = {}
        
        # Extension history
        self._extensions: Dict[str, List[RetentionExtension]] = {}
        
        # Statistics
        self._stats = {
            "total_scheduled": 0,
            "expired_count": 0,
            "expiring_soon_count": 0,
        }
    
    def validate_policy(self, policy: RetentionPolicy) -> bool:
        """
        Validate a retention policy.
        
        Args:
            policy: Policy to validate
            
        Returns:
            True if the policy is valid
        """
        # Basic validation: positive retention days
        return policy.retention_days > 0
    
    async def create_schedule(
        self,
        information_id: str,
        policy: RetentionPolicy,
    ) -> RetentionSchedule:
        """
        Create a retention schedule for provenance tracking.
        
        PHASE 3.7.21: The record itself owns its retention_schedule field.
        This method only creates the schedule for validation and observability.
        
        Args:
            information_id: ID of the information
            policy: Retention policy to apply
            
        Returns:
            Created RetentionSchedule (record owns the actual value)
        """
        if not self.validate_policy(policy):
            raise ValueError(f"Invalid retention policy: {policy.policy_id}")
        
        schedule = RetentionSchedule(
            information_id=information_id,
            policy=policy,
            created_at=time.time(),
        )
        
        with self._lock:
            # Store for tracking
            existing_schedule = self._scheduler.get_schedule(information_id)
            if existing_schedule is not None:
                # Update the existing schedule
                schedule = RetentionSchedule(
                    information_id=information_id,
                    policy=policy,
                    created_at=existing_schedule.created_at,
                    expires_at=schedule.expires_at,
                    extensions=list(schedule.extensions or []),
                )
            
            self._scheduler.add_schedule(schedule)
            
            # Store policy for provenance
            if information_id not in self._policies:
                self._policies[information_id] = []
            self._policies[information_id].append(policy)
            
            # Update stats
            self._stats["total_scheduled"] += 1
        
        return schedule
    
    async def get_schedule(self, information_id: str) -> Optional[RetentionSchedule]:
        """Get a retention schedule by ID."""
        with self._lock:
            return self._scheduler.get_schedule(information_id)
    
    async def extend_retention(
        self,
        information_id: str,
        additional_days: int,
        reason: str = "",
        requested_by: str = "system",
        approved_by: str = "system",
    ) -> RetentionExtension:
        """
        Extend retention for an item.
        
        Args:
            information_id: ID of the information
            additional_days: Number of days to extend
            reason: Reason for extension
            requested_by: Who requested the extension
            approved_by: Who approved the extension
            
        Returns:
            RetentionExtension recorded for provenance
        """
        with self._lock:
            schedule = self._scheduler.get_schedule(information_id)
            
            if schedule is None:
                raise ValueError(f"No retention schedule found for {information_id}")
            
            # Create extension record
            original_expires = schedule.expires_at or (
                schedule.created_at + (schedule.policy.retention_days * 86400)
            )
            new_expires = original_expires + (additional_days * 86400)
            
            extension = RetentionExtension(
                original_expires_at=original_expires,
                extended_expires_at=new_expires,
                requested_by=requested_by,
                approved_by=approved_by,
                reason=reason,
                timestamp=time.time(),
            )
            
            # Store extension for provenance
            if information_id not in self._extensions:
                self._extensions[information_id] = []
            self._extensions[information_id].append(extension)
            
            return extension
    
    async def get_policy(self, policy_id: str) -> Optional[RetentionPolicy]:
        """
        Get a retention policy by ID.
        
        Args:
            policy_id: ID of the policy
            
        Returns:
            The policy if found
        """
        with self._lock:
            # Check policies for all information
            for policies in self._policies.values():
                for policy in policies:
                    if policy.policy_id == policy_id:
                        return policy
            return None
    
    def get_expiring_soon(self, within_days: int = 7) -> List[str]:
        """Get items expiring soon (for observability)."""
        with self._lock:
            return self._scheduler.get_expiring_soon(within_days)
    
    def get_expired(self) -> List[str]:
        """Get expired items (for observability)."""
        with self._lock:
            return self._scheduler.get_expired()
    
    def get_all_scheduled(self) -> List[RetentionSchedule]:
        """Get all scheduled items."""
        with self._lock:
            return self._scheduler.get_all_scheduled()
    
    def get_stats(self) -> Dict[str, Any]:
        """Get retention statistics."""
        with self._lock:
            expired = len(self._scheduler.get_expired())
            expiring = len(self._scheduler.get_expiring_soon())
            
            self._stats["expired_count"] = expired
            self._stats["expiring_soon_count"] = expiring
            
            return {
                "total_scheduled": self._stats["total_scheduled"],
                "expired": expired,
                "expiring_soon": expiring,
                "records_with_policy": len(self._policies),
                "extension_count": sum(len(exts) for exts in self._extensions.values()),
            }


__all__ = [
    "RetentionScheduler",
    "RetentionCoordinator",
]