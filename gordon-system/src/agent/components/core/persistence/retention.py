# Retention and Garbage Collection
# ================================
#
# DEPRECATED - This module contains a duplicate RetentionManager class.
#
# The canonical RetentionManager is now in:
#   gordon-system/src/agent/components/core/data_governance/retention.py
#
# This legacy implementation remains for backward compatibility but should not be used
# in new code. All retention management should flow through the data_governance module.
#
# For migration: Replace all imports from persistence.retention with:
#   from gordon.system.agent.components.core.data_governance import RetentionManager

"""
Legacy retention policies and garbage collection for persisted artifacts.

WARNING: This is a legacy module. The canonical implementation has moved to
gordon-system/src/agent/components/core/data_governance/retention.py

This duplicate implementation will be removed in Phase 3.7.22.
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any
from enum import Enum, auto
import uuid
import time


# =============================================================================
# Retention Classes (Preserved for backward compatibility)
# =============================================================================

class RetentionClass(Enum):
    """
    Categories of retention requirements.
    
    DEPRECATED: Use data_governance.models.RetentionPolicy instead.
    """
    
    # No retention - delete immediately after use
    NONE = "none"
    
    # Keep for process lifetime only
    PROCESS_LIFETIME = "process_lifetime"
    
    # Keep for runtime lifetime (current boot session)
    RUNTIME_LIFETIME = "runtime_lifetime"
    
    # Keep until explicitly deleted
    UNLIMITED = "unlimited"
    
    # Short-term: 24 hours
    SHORT_TERM = "short_term"
    
    # Medium-term: 7 days
    MEDIUM_TERM = "medium_term"
    
    # Long-term: 30 days
    LONG_TERM = "long_term"
    
    # Compliance/audit: 1 year minimum
    COMPLIANCE = "compliance"
    
    # Archival: 5+ years
    ARCHIVAL = "archival"


# =============================================================================
# Retention Policy (Legacy - DO NOT USE)
# =============================================================================

@dataclass(frozen=True)
class RetentionPolicy:
    """
    Policy for retaining artifacts.
    
    DEPRECATED: Use data_governance.models.RetentionPolicy instead.
    """
    
    policy_id: str
    
    # Retention class
    retention_class: RetentionClass
    
    # Minimum retention time (seconds)
    min_retention_seconds: float = 0.0
    
    # Maximum history length (number of versions to keep)
    max_history_length: int = 100
    
    created_at: float = field(default_factory=time.monotonic)
    
    @classmethod
    def for_class(cls, retention_class: RetentionClass) -> "RetentionPolicy":
        """Create a policy for the given class."""
        defaults = {
            RetentionClass.NONE: (0.0, 1),
            RetentionClass.PROCESS_LIFETIME: (0.0, 1),
            RetentionClass.RUNTIME_LIFETIME: (0.0, 10),
            RetentionClass.UNLIMITED: (86400.0 * 365, 1000),  # 1 year min
            RetentionClass.SHORT_TERM: (86400.0, 7),  # 24h min, 7 versions
            RetentionClass.MEDIUM_TERM: (86400.0 * 7, 30),  # 7 days min, 30 versions
            RetentionClass.LONG_TERM: (86400.0 * 30, 12),  # 30 days min, 12 versions
            RetentionClass.COMPLIANCE: (86400.0 * 365, 1000),  # 1 year minimum
            RetentionClass.ARCHIVAL: (86400.0 * 365 * 5, 100),  # 5 years minimum
        }
        
        min_retention, max_history = defaults.get(retention_class, (0.0, 1))
        
        return cls(
            policy_id=str(uuid.uuid4()),
            retention_class=retention_class,
            min_retention_seconds=min_retention,
            max_history_length=max_history,
        )


# =============================================================================
# Retention Manager - DEPRECATED
# =============================================================================

class RetentionManager:
    """
    Manages retention policies and garbage collection.
    
    DEPRECATED: This is a duplicate of the canonical RetentionManager
    in data_governance/retention.py. All new code should use that instead.
    
    Usage (deprecated):
        manager = RetentionManager(runtime_id="runtime_123")
        
        # Get retention class for an artifact type
        policy = manager.get_policy(RetentionClass.SHORT_TERM)
        
        # Evaluate artifacts for deletion
        evaluation = await manager.evaluate_retention(policy, artifact_ids)
    """
    
    def __init__(self, runtime_id: str) -> None:
        self._runtime_id = runtime_id
        
        # Default policies by retention class
        self._policies: Dict[RetentionClass, RetentionPolicy] = {}
        
        # Track deleted artifacts for audit
        self._deleted_artifacts: List[str] = []
        
        # Metrics
        self._evaluation_count = 0
        self._gc_plan_count = 0
    
    @property
    def runtime_id(self) -> str:
        return self._runtime_id
    
    def get_policy(
        self,
        retention_class: RetentionClass,
    ) -> RetentionPolicy:
        """
        Get the policy for a retention class.
        
        DEPRECATED: Use data_governance.RetentionManager.get_policy() instead.
        """
        if retention_class not in self._policies:
            self._policies[retention_class] = RetentionPolicy.for_class(
                retention_class
            )
        
        return self._policies[retention_class]
    
    def evaluate_retention(
        self,
        policy: RetentionPolicy,
        artifact_ids: List[str],
        created_ats: Dict[str, float],
    ) -> "RetentionEvaluation":
        """
        Evaluate artifacts for retention.
        
        DEPRECATED: Use data_governance.RetentionManager instead.
        """
        self._evaluation_count += 1
        
        current_time = time.monotonic()
        
        retained = []
        eligible_for_deletion = []
        
        for artifact_id in artifact_ids:
            created_at = created_ats.get(artifact_id, current_time)
            
            # Check minimum retention time
            age = current_time - created_at
            
            if age < policy.min_retention_seconds:
                retained.append(artifact_id)
            elif len(retained) >= policy.max_history_length:
                eligible_for_deletion.append(artifact_id)
            else:
                retained.append(artifact_id)
        
        return RetentionEvaluation(
            evaluation_id=str(uuid.uuid4()),
            policy=policy,
            total_count=len(artifact_ids),
            retained_count=len(retained),
            eligible_for_deletion_count=len(eligible_for_deletion),
            retained=retained,
            eligible_for_deletion=eligible_for_deletion,
        )
    
    def create_gc_plan(
        self,
        evaluation: "RetentionEvaluation",
        dry_run: bool = False,
    ) -> "GarbageCollectionPlan":
        """
        Create a garbage collection plan from an evaluation.
        
        DEPRECATED: Use data_governance.RetentionManager instead.
        """
        self._gc_plan_count += 1
        
        return GarbageCollectionPlan(
            plan_id=str(uuid.uuid4()),
            runtime_id=self._runtime_id,
            checkpoints_to_delete=[
                aid for aid in evaluation.eligible_for_deletion
                if "checkpoint" in aid.lower()
            ],
            snapshots_to_delete=[
                aid for aid in evaluation.eligible_for_deletion
                if "snapshot" in aid.lower()
            ],
            journal_segments_to_delete=[
                aid for aid in evaluation.eligible_for_deletion
                if "journal" in aid.lower()
            ],
            dry_run=dry_run,
        )
    
    def record_deletion(self, artifact_id: str) -> None:
        """Record that an artifact was successfully deleted."""
        self._deleted_artifacts.append(artifact_id)
    
    def get_diagnostics(self) -> Dict[str, Any]:
        """Get manager diagnostics."""
        return {
            "runtime_id": self._runtime_id,
            "policies_registered": len(self._policies),
            "evaluation_count": self._evaluation_count,
            "gc_plan_count": self._gc_plan_count,
            "deleted_artifacts_count": len(self._deleted_artifacts),
        }


# =============================================================================
# Retention Evaluation (Preserved for backward compatibility)
# =============================================================================

@dataclass(frozen=True)
class RetentionEvaluation:
    """Result of evaluating retention for a set of artifacts."""
    
    evaluation_id: str
    
    # Policy applied
    policy: RetentionPolicy
    
    # Artifacts evaluated
    total_count: int
    retained_count: int
    eligible_for_deletion_count: int
    
    # Artifacts by status
    retained: List[str] = field(default_factory=list)
    eligible_for_deletion: List[str] = field(default_factory=list)
    
    created_at: float = field(default_factory=time.monotonic)


# =============================================================================
# Garbage Collection Plan (Preserved for backward compatibility)
# =============================================================================

@dataclass(frozen=True)
class GarbageCollectionPlan:
    """
    A plan for garbage collection.
    
    DEPRECATED: Use data_governance models instead.
    """
    
    plan_id: str
    
    runtime_id: str
    boot_session_id: Optional[str] = None
    
    # Artifacts to delete
    checkpoints_to_delete: List[str] = field(default_factory=list)
    snapshots_to_delete: List[str] = field(default_factory=list)
    journal_segments_to_delete: List[str] = field(default_factory=list)
    
    # Dependencies to check
    dependency_check: bool = True
    
    # Safety settings
    dry_run: bool = False  # Don't actually delete if True
    cascade: bool = False  # Delete dependents as well
    
    created_at: float = field(default_factory=time.monotonic)


@dataclass(frozen=True)
class GarbageCollectionResult:
    """Result of a garbage collection operation."""
    
    result_id: str
    
    request_id: str
    runtime_id: str
    
    status: "GarbageCollectionStatus"
    timestamp: float = field(default_factory=time.monotonic)
    
    # Details
    artifacts_deleted: int = 0
    artifacts_failed: int = 0
    
    deleted_ids: List[str] = field(default_factory=list)
    failed_ids: List[str] = field(default_factory=list)
    error_messages: List[str] = field(default_factory=list)
    
    @property
    def success(self) -> bool:
        return self.status == GarbageCollectionStatus.COMPLETED


class GarbageCollectionStatus(Enum):
    """Status of garbage collection."""
    
    REQUESTED = "requested"
    PLANNING = "planning"
    VALIDATING = "validating"
    DELETING = "deleting"
    COMPLETED = "completed"
    PARTIAL = "partial"
    FAILED = "failed"


# =============================================================================
# Retention Decision (Preserved for backward compatibility)
# =============================================================================

@dataclass(frozen=True)
class RetentionDecision:
    """A decision about whether to retain or delete an artifact."""
    
    decision_id: str
    
    artifact_type: str  # e.g., "checkpoint", "snapshot", "journal_segment"
    artifact_id: str
    
    # Current state
    created_at: float
    retention_class: RetentionClass
    
    # Decision
    should_retain: bool
    
    # Reason for decision
    reason: str
    
    # If deleting, when can deletion occur
    earliest_deletion_time: Optional[float] = None
    
    created_at_decision: float = field(default_factory=time.monotonic)


__all__ = [
    # DEPRECATED - Legacy classes (use data_governance instead)
    "RetentionClass",
    "RetentionPolicy",
    "RetentionDecision",
    "RetentionEvaluation",
    "GarbageCollectionPlan",
    "GarbageCollectionResult",
    "GarbageCollectionStatus",
    "RetentionManager",  # Deprecated - use data_governance.RetentionManager
]