# Stream Replay-Assisted Recovery - Phase 3.11.7
# ==============================================

"""
Replay-assisted recovery infrastructure for Gordon's Semantic Stream subsystem.

This module implements:
    
    Replay-Driven Recovery:
        - Replay planning from checkpoint to cursor position
        - Bounded replay ranges based on retention policies
        - Side-effect policy enforcement during replay
        - Order preservation guarantees
        
    Key Principles:
        - Replay NEVER recreates committed history
        - Replay NEVER assigns new canonical sequence numbers
        - Replay preserves all integrity guarantees of original commits
        - Replay respects retention and replay policies

Architecture:
    
    Recovery → Checkpoint Loaded → Replay Started → [Records Delivered] → Cursor Restored
    
    The recovery process uses replay to reconstruct state by:
        1. Loading a validated checkpoint as starting point
        2. Playing back records from checkpoint position to current
        3. Reconstructing subscriber state during playback
        4. Validating final state against expected conditions
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple, Any, AsyncGenerator
from enum import Enum, auto
import time


# =============================================================================
# REPLAY MODES FOR RECOVERY
# =============================================================================

class RecoveryReplayMode(Enum):
    """
    Replay mode appropriate for recovery scenarios.
    
    Modes:
        STATE_RECONSTRUCTION: Rebuild subscriber state from history
        CURSOR_RECOVERY: Restore cursor position exactly
        INTEGRITY_VERIFICATION: Verify replay produces correct state
        STATE_SYNC: Synchronize multiple subscribers after failure
    """
    
    STATE_RECONSTRUCTION = "state_reconstruction"
    """Rebuild subscriber state from history."""
    
    CURSOR_RECOVERY = "cursor_recovery"
    """Restore cursor position exactly."""
    
    INTEGRITY_VERIFICATION = "integrity_verification"
    """Verify replay produces correct state."""
    
    STATE_SYNC = "state_sync"
    """Synchronize multiple subscribers after failure."""


# =============================================================================
# REPLAY-ASSISTED RECOVERY PLAN
# =============================================================================

@dataclass(frozen=True)
class ReplayRecoveryPlan:
    """
    Plan for using replay to assist recovery.
    
    Combines checkpoint restoration with replay execution.
    """
    
    plan_id: str
    
    # Checkpoint reference
    source_checkpoint_id: str
    """Checkpoint where recovery begins."""
    
    start_position: int
    """Sequence position in the checkpoint to begin replay."""
    
    # Replay range
    end_position: Optional[int] = None
    """Position to replay up to (exclusive). If None, use latest."""
    
    maximum_records: Optional[int] = None
    
    # Replay configuration
    replay_mode: RecoveryReplayMode = RecoveryReplayMode.STATE_RECONSTRUCTION
    side_effect_policy: str = "block-all"  # Never invoke side effects during recovery
    
    # Stream context
    stream_id: Optional[str] = None
    generation_id: Optional[int] = None
    
    steps: Tuple[str, ...] = field(default_factory=tuple)
    
    created_at_utc: float = field(default_factory=time.time)


class ReplayRecoveryDecision(Enum):
    """
    Decision about replay-assisted recovery eligibility.
    """
    
    ELIGIBLE = "eligible"
    """Replay recovery is appropriate."""
    
    NOT_ELIGIBLE_NO_CHECKPOINT = "not_eligible_no_checkpoint"
    """No valid checkpoint available."""
    
    NOT_ELIGIBLE_RETENTION_EXCEEDED = "not_eligible_retention_exceeded"
    """Records no longer retained for replay."""
    
    NOT_ELIGIBLE_ORDER_VIOLATION = "not_eligible_order_violation"
    """Cannot preserve ordering guarantees."""
    
    NOT_ELIGIBLE_SIDE_EFFECT_CONCERN = "not_eligible_side_effect_concern"
    """Side effects would violate policies."""


@dataclass(frozen=True)
class ReplayRecoveryPlanResult:
    """
    Result of replay recovery planning.
    """
    
    decision: ReplayRecoveryDecision
    plan: Optional[ReplayRecoveryPlan] = None
    error_message: str = ""


# =============================================================================
# REPLAY-ASSISTED RECOVERY PLANNER
# =============================================================================

class ReplayRecoveryPlanner:
    """
    Planner for replay-assisted recovery operations.
    
    Evaluates whether replay can safely assist in recovery by:
        - Checking checkpoint availability and validity
        - Verifying retention policy allows replay to target position
        - Confirming ordering guarantees can be maintained
        - Ensuring side-effect policies are respected
    """
    
    def __init__(
        self,
        retention_window_seconds: float = 86400.0,  # Default 24 hours
        max_replay_records: int = 10000,
        enforce_side_effect_policy: bool = True,
    ):
        """
        Initialize replay recovery planner.
        
        Args:
            retention_window_seconds: How long records are retained for replay
            max_replay_records: Maximum records to replay in one operation
            enforce_side_effect_policy: Block side-effecting operations during replay?
        """
        self._retention_window = retention_window_seconds
        self._max_replay_records = max_replay_records
        self._enforce_side_effects = enforce_side_effect_policy
    
    def plan_replay_recovery(
        self,
        stream_id: str,
        checkpoint_id: str,
        target_position: int,
        current_time_utc: Optional[float] = None,
        retention_info: Optional[Dict[str, Any]] = None,
    ) -> ReplayRecoveryPlanResult:
        """
        Plan replay-assisted recovery.
        
        Args:
            stream_id: Stream identifier
            checkpoint_id: Validated checkpoint to start from
            target_position: Position to reach after replay
            current_time_utc: Current time for retention calculations
            retention_info: Information about record retention
            
        Returns:
            ReplayRecoveryPlanResult with decision and plan
        """
        now = current_time_utc or time.time()
        
        # Get retention boundaries
        earliest_retainable = self._get_earliest_retainable_time(retention_info, now)
        target_position_info = self._get_position_info(target_position, retention_info)
        
        # Step 1: Check checkpoint validity
        if not self._validate_checkpoint(checkpoint_id):
            return ReplayRecoveryPlanResult(
                decision=ReplayRecoveryDecision.NOT_ELIGIBLE_NO_CHECKPOINT,
                error_message="Checkpoint is not valid or available",
            )
        
        # Step 2: Verify retention allows replay to target position
        if not self._verify_retention(target_position, earliest_retainable, now):
            return ReplayRecoveryPlanResult(
                decision=ReplayRecoveryDecision.NOT_ELIGIBLE_RETENTION_EXCEEDED,
                error_message="Records no longer retained for replay",
            )
        
        # Step 3: Check ordering guarantees
        if not self._verify_ordering_preservation(target_position_info):
            return ReplayRecoveryPlanResult(
                decision=ReplayRecoveryDecision.NOT_ELIGIBLE_ORDER_VIOLATION,
                error_message="Cannot preserve canonical ordering guarantees",
            )
        
        # Step 4: Verify side-effect policy can be enforced
        if self._enforce_side_effects and not self._can_enforce_side_effect_policy():
            return ReplayRecoveryPlanResult(
                decision=ReplayRecoveryDecision.NOT_ELIGIBLE_SIDE_EFFECT_CONCERN,
                error_message="Cannot safely enforce side-effect policy",
            )
        
        # Create replay recovery plan
        plan = ReplayRecoveryPlan(
            plan_id=f"replay-recovery:{time.monotonic_ns()}",
            source_checkpoint_id=checkpoint_id,
            start_position=target_position_info.get("last_committed", 0),
            end_position=target_position,
            maximum_records=min(
                self._max_replay_records,
                target_position - target_position_info.get("last_committed", 0)
            ),
            replay_mode=RecoveryReplayMode.STATE_RECONSTRUCTION,
            stream_id=stream_id,
        )
        
        return ReplayRecoveryPlanResult(
            decision=ReplayRecoveryDecision.ELIGIBLE,
            plan=plan,
        )
    
    def _get_earliest_retainable_time(
        self,
        retention_info: Optional[Dict[str, Any]],
        now: float,
    ) -> float:
        """Calculate earliest time records are still retained."""
        if retention_info and "retention_window" in retention_info:
            return now - retention_info["retention_window"]
        return now - self._retention_window
    
    def _get_position_info(
        self,
        position: int,
        retention_info: Optional[Dict[str, Any]],
    ) -> Dict[str, Any]:
        """Get information about a position for replay planning."""
        # In real implementation, would query stream state
        return {
            "last_committed": position - 100,  # Example: 100 records since checkpoint
            "is_retained": True,
            "ordering_verified": True,
        }
    
    def _validate_checkpoint(self, checkpoint_id: str) -> bool:
        """Validate that checkpoint is available and valid."""
        # In real implementation, would check checkpoint store
        return len(checkpoint_id) > 0
    
    def _verify_retention(
        self,
        target_position: int,
        earliest_time: float,
        now: float,
    ) -> bool:
        """Verify records are still retained for the replay range."""
        # Simplified check
        return True
    
    def _verify_ordering_preservation(self, position_info: Dict[str, Any]) -> bool:
        """Verify ordering guarantees can be maintained."""
        return position_info.get("ordering_verified", False)
    
    def _can_enforce_side_effect_policy(self) -> bool:
        """Check if side-effect policy can be enforced."""
        # In real implementation, would check stream configuration
        return True


# =============================================================================
# SUBSCRIBER RECOVERY MODULE
# =============================================================================

class SubscriberRecoveryMode(Enum):
    """
    Mode of subscriber recovery.
    
    Modes determine how subscriber state is restored:
        - COMPLETE: Restore full state including unacknowledged records
        - ACKNOWLEDGED_ONLY: Only restore acknowledged position
        - CHECKPOINT_BASED: Restore from saved checkpoint
    """
    
    COMPLETE = "complete"
    """Restore full subscriber state."""
    
    ACKNOWLEDGED_ONLY = "acknowledged_only"
    """Only restore acknowledged position."""
    
    CHECKPOINT_BASED = "checkpoint_based"
    """Restore from saved checkpoint."""


@dataclass(frozen=True)
class SubscriberRecoveryPlan:
    """
    Plan for subscriber recovery.
    """
    
    plan_id: str
    stream_id: str
    
    # Subscriber reference
    subscriber_id: str
    
    # Recovery scope
    mode: SubscriberRecoveryMode = SubscriberRecoveryMode.CHECKPOINT_BASED
    restore_unacknowledged: bool = False
    
    # State to restore
    checkpoint_id: Optional[str] = None
    last_ack_position: Optional[int] = None
    subscription_parameters: Dict[str, Any] = field(default_factory=dict)
    
    steps: Tuple[str, ...] = field(default_factory=tuple)


# =============================================================================
# PUBLISHER RECOVERY MODULE
# =============================================================================

class PublisherRecoveryMode(Enum):
    """
    Mode of publisher recovery.
    
    Modes:
        - CONTINUE: Continue publishing from last position
        - RESUME_AT_CHECKPOINT: Resume at checkpoint position
        - REVALIDATE_IDEMPOTENCY: Revalidate idempotency state
    """
    
    CONTINUE = "continue"
    """Continue publishing from last known position."""
    
    RESUME_AT_CHECKPOINT = "resume_at_checkpoint"
    """Resume at checkpoint position (new generation)."""
    
    REVALIDATE_IDEMPOTENCY = "revalidate_idempotency"
    """Revalidate idempotency state before continuing."""


@dataclass(frozen=True)
class PublisherRecoveryPlan:
    """
    Plan for publisher recovery.
    """
    
    plan_id: str
    stream_id: str
    
    # Publisher reference
    publisher_id: str
    
    # Recovery scope
    mode: PublisherRecoveryMode = PublisherRecoveryMode.CONTINUE
    
    # State to restore
    checkpoint_id: Optional[str] = None
    last_sequence_number: Optional[int] = None
    idempotency_state_restored: bool = True
    
    steps: Tuple[str, ...] = field(default_factory=tuple)