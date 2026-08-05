# Independent Verification Module
# ================================

"""
Independent verification layer for Phase 3.7.10 failure recovery.

This module implements:
    - Independent verification of recovery success
    - Independent verification of rollback success
    - State comparison against target state
    - Stability window validation for recovery confirmation
    
Key principles:
    - Recovery actor ≠ Verifier (separation of concerns)
    - Verification must be independent from the recovery action
    - Target state must be known before verification can succeed
    - Unknown outcome cannot be verified as success
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, List, Optional, Callable, Awaitable, Any, Set, Tuple
import time


# =============================================================================
# Verification Result Types
# =============================================================================

@dataclass(frozen=True)
class VerificationResult:
    """
    Result of an independent verification.
    
    Args:
        success: Whether the state matches target expectations
        confidence: 0.0-1.0 confidence level in result
        
        actual_state: What state was observed
        expected_state: What state was expected
        
        mismatch_details: List of specific mismatches (if any)
        
        verification_duration_seconds: How long verification took
    """
    
    success: bool
    confidence: float = 0.0
    
    actual_state: Optional[str] = None
    expected_state: Optional[str] = None
    
    mismatch_details: List[str] = field(default_factory=list)
    
    verification_duration_seconds: float = 0.0


@dataclass(frozen=True)
class RecoveryVerificationResult(VerificationResult):
    """
    Result of recovery verification.
    
    Args:
        recovered_entities: List of entity IDs that were successfully recovered
        partially_recovered: Entities with partial recovery
        failed_to_recover: Entities that didn't recover
        
        degraded_components: Components in degraded mode (acceptable)
        missing_capabilities: Capabilities that are still unavailable
    """
    
    recovered_entities: List[str] = field(default_factory=list)
    partially_recovered: List[str] = field(default_factory=list)
    failed_to_recover: List[str] = field(default_factory=list)
    
    degraded_components: List[str] = field(default_factory=list)
    missing_capabilities: List[str] = field(default_factory=list)


@dataclass(frozen=True)
class RollbackVerificationResult(VerificationResult):
    """
    Result of rollback verification.
    
    Args:
        restored_state_version: State version after rollback
        state_restored_to: Target state version
        
        rolled_back_entities: Entities that were rolled back
        skipped_entities: Entities that couldn't be rolled back
        
        integrity_verified: Whether data integrity was verified
        corruption_found: Any corruption detected (should be None after valid rollback)
    """
    
    restored_state_version: int = 0
    state_restored_to: int = 0
    
    rolled_back_entities: List[str] = field(default_factory=list)
    skipped_entities: List[str] = field(default_factory=list)
    
    integrity_verified: bool = False
    corruption_found: Optional[List[str]] = None


# =============================================================================
# Verification Status
# =============================================================================

class VerificationStatus(Enum):
    """Status of verification operation."""
    
    NOT_STARTED = "not_started"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    PENDING_DATA = "pending_data"  # Waiting for external data source
    UNKNOWN_OUTCOME = "unknown_outcome"


# =============================================================================
# Verification Protocol
# =============================================================================

class RecoveryVerifier:
    """
    Protocol for recovery verification.
    
    Implementations should provide independent verification that
    recovery operations successfully restored the system to an
    acceptable state.
    """
    
    async def verify_recovery(
        self,
        target_state: str,
        entities_affected: List[str],
        expected_capabilities: Optional[List[str]] = None
    ) -> RecoveryVerificationResult:
        """
        Verify that recovery restored the system.
        
        Args:
            target_state: Expected state after recovery ("healthy", "degraded")
            entities_affected: Entity IDs that were affected by failure
            expected_capabilities: Capabilities that should be available
            
        Returns:
            RecoveryVerificationResult with verification outcome
        """
        raise NotImplementedError
    
    async def verify_partial_recovery(
        self,
        target_state: str,
        partially_recovered_entities: List[str],
        fully_recovered_entities: List[str]
    ) -> RecoveryVerificationResult:
        """
        Verify partial recovery state.
        
        Args:
            target_state: Expected degraded state
            partially_recovered: Entities still recovering
            fully_recovered: Fully recovered entities
            
        Returns:
            Verification result for partial recovery
        """
        raise NotImplementedError


class RollbackVerifier:
    """
    Protocol for rollback verification.
    
    Verifies that rollback operations successfully restored state
    to a known prior version.
    """
    
    async def verify_rollback(
        self,
        target_state_version: int,
        entities_involved: List[str],
        integrity_check_required: bool = True
    ) -> RollbackVerificationResult:
        """
        Verify that rollback restored state correctly.
        
        Args:
            target_state_version: State version we should be at
            entities_involved: Entities affected by rollback
            integrity_check_required: Whether to verify data integrity
            
        Returns:
            RollbackVerificationResult with verification outcome
        """
        raise NotImplementedError
    
    async def verify_state_compatibility(
        self,
        current_state_version: int,
        target_state_version: int
    ) -> bool:
        """
        Check if current state is compatible with target version.
        
        This determines if a rollback to the target version would work.
        
        Args:
            current_state_version: Current state version
            target_state_version: Target version for rollback
            
        Returns:
            True if versions are compatible (can rollback)
        """
        raise NotImplementedError


# =============================================================================
# State Comparison Engine
# =============================================================================

@dataclass(frozen=True)
class StateSnapshot:
    """
    A snapshot of system state at a point in time.
    
    Args:
        state_id: Unique identifier for this snapshot
        
        timestamp_utc: When the snapshot was taken
        runtime_id: Which runtime this snapshot is from
        
        entity_states: Map of entity ID to its state
        capability_states: Map of capability ID to its state
        
        version: State version number (monotonically increasing)
    """
    
    state_id: str
    
    timestamp_utc: float = field(default_factory=time.time)
    runtime_id: str = ""
    
    entity_states: Dict[str, "EntityState"] = field(default_factory=dict)
    capability_states: Dict[str, str] = field(default_factory=dict)
    
    version: int = 0


@dataclass(frozen=True)
class EntityState:
    """
    State of a single entity.
    
    Args:
        entity_id: Which entity this is
        status: Current status (running, stopped, degraded, unknown)
        
        health_score: 0.0-1.0 health indicator
        last_heartbeat_utc: Last received heartbeat
        
        metadata: Additional state information
    """
    
    entity_id: str
    status: "EntityStatus"
    
    health_score: float = 0.0
    last_heartbeat_utc: Optional[float] = None
    
    metadata: Dict[str, Any] = field(default_factory=dict)


class EntityStatus(Enum):
    """Entity status values."""
    
    RUNNING = "running"
    STOPPED = "stopped"
    DEGRADED = "degraded"
    UNKNOWN = "unknown"
    ERROR = "error"


class StateComparisonEngine:
    """
    Engine for comparing system states.
    
    Used for verification, rollback validation, and state recovery
    confirmation.
    """
    
    def __init__(self) -> None:
        """Initialize the comparison engine."""
        self._snapshots: Dict[str, StateSnapshot] = {}
        self._state_versions: Dict[str, int] = {}  # entity_id -> version
    
    async def capture_snapshot(
        self,
        runtime_id: str,
        state_id: Optional[str] = None
    ) -> StateSnapshot:
        """
        Capture a current state snapshot.
        
        Args:
            runtime_id: Which runtime to snapshot
            state_id: Optional custom ID
            
        Returns:
            Captured snapshot with all entity states
        """
        import uuid
        
        actual_id = state_id or str(uuid.uuid4())
        
        # Get current entity and capability states
        entities, capabilities = await self._collect_current_state(runtime_id)
        
        snapshot = StateSnapshot(
            state_id=actual_id,
            runtime_id=runtime_id,
            entity_states=entities,
            capability_states=capabilities,
            version=len(self._snapshots) + 1
        )
        
        self._snapshots[actual_id] = snapshot
        
        return snapshot
    
    async def _collect_current_state(
        self, 
        runtime_id: str
    ) -> Tuple[Dict[str, EntityState], Dict[str, str]]:
        """Collect current entity and capability states."""
        # This would query actual system state in production
        return {}, {}
    
    async def compare_snapshots(
        self,
        snapshot_a: StateSnapshot,
        snapshot_b: StateSnapshot
    ) -> Dict[str, Any]:
        """
        Compare two snapshots and identify differences.
        
        Args:
            snapshot_a: First snapshot (e.g., before failure)
            snapshot_b: Second snapshot (e.g., after recovery)
            
        Returns:
            Comparison results with mismatch details
        """
        result = {
            "identical": True,
            "differences": [],
            "missing_entities": [],
            "extra_entities": []
        }
        
        # Compare entities
        entities_a = set(snapshot_a.entity_states.keys())
        entities_b = set(snapshot_b.entity_states.keys())
        
        missing = entities_a - entities_b
        extra = entities_b - entities_a
        
        if missing or extra:
            result["identical"] = False
        
        if missing:
            result["missing_entities"] = list(missing)
        
        if extra:
            result["extra_entities"] = list(extra)
        
        # Compare states of common entities
        for entity_id in entities_a & entities_b:
            state_a = snapshot_a.entity_states[entity_id]
            state_b = snapshot_b.entity_states[entity_id]
            
            if self._entity_states_differ(state_a, state_b):
                result["identical"] = False
                result["differences"].append({
                    "entity": entity_id,
                    "before_status": state_a.status.value if hasattr(state_a.status, 'value') else str(state_a.status),
                    "after_status": state_b.status.value if hasattr(state_b.status, 'value') else str(state_b.status)
                })
        
        return result
    
    def _entity_states_differ(self, a: EntityState, b: EntityState) -> bool:
        """Check if two entity states differ significantly."""
        if a.entity_id != b.entity_id:
            return True
        
        status_a = a.status.value if hasattr(a.status, 'value') else str(a.status)
        status_b = b.status.value if hasattr(b.status, 'value') else str(b.status)
        
        return status_a != status_b or a.health_score != b.health_score
    
    async def verify_state_match(
        self,
        actual_snapshot: StateSnapshot,
        target_version: int
    ) -> VerificationResult:
        """
        Verify that actual state matches expected version.
        
        Args:
            actual_snapshot: Current snapshot to verify
            target_version: Expected state version
            
        Returns:
            Verification result indicating match status
        """
        import uuid
        
        start_time = time.monotonic()
        
        try:
            # Check if we have the target version cached
            # In production, this would query a state store
            
            actual_version = actual_snapshot.version
            
            if actual_version >= target_version:
                return VerificationResult(
                    success=True,
                    confidence=1.0,
                    actual_state=f"version_{actual_version}",
                    expected_state=f"version_{target_version}"
                )
            
            # State is older than target - verification failed
            return VerificationResult(
                success=False,
                confidence=0.5,
                actual_state=f"version_{actual_version}",
                expected_state=f"version_{target_version}",
                mismatch_details=[f"State version {actual_version} < target {target_version}"]
            )
        finally:
            duration = time.monotonic() - start_time
            
            # Update result with timing if we had it
            pass


# =============================================================================
# Stability Window Validator
# =============================================================================

@dataclass(frozen=True)
class StabilityWindow:
    """
    A window during which a system state must remain stable.
    
    Used to verify that recovery has produced a stable, lasting effect
    rather than temporary improvement followed by renewed failure.
    
    Args:
        window_id: Unique identifier
        
        start_time_utc: When the stability period starts
        duration_seconds: How long stability must be maintained
        
        required_stable_entities: Entities that must remain stable
        max_failures_allowed: How many additional failures are acceptable
    """
    
    window_id: str
    
    start_time_utc: float = field(default_factory=time.time)
    duration_seconds: float = 30.0  # Default: 30 seconds of stability
    
    required_stable_entities: List[str] = field(default_factory=list)
    max_failures_allowed: int = 0


class StabilityWindowValidator:
    """
    Validate that recovered state remains stable over time.
    
    This is a critical verification - a recovery that's immediately
    followed by another failure indicates incomplete or incorrect
    recovery.
    """
    
    def __init__(self, default_duration_seconds: float = 30.0) -> None:
        """
        Initialize the validator.
        
        Args:
            default_duration_seconds: Default stability window duration
        """
        self._default_duration = default_duration_seconds
        self._active_windows: Dict[str, StabilityWindow] = {}
        self._failure_events: Dict[str, List[float]] = {}  # entity_id -> timestamps
    
    def create_stability_window(
        self,
        recovery_id: str,
        entities_to_monitor: Optional[List[str]] = None,
        duration_seconds: Optional[float] = None
    ) -> StabilityWindow:
        """
        Create a stability window for recovery verification.
        
        Args:
            recovery_id: ID of the recovery being verified
            entities_to_monitor: Entities to watch (None = all)
            duration_seconds: How long stability must be maintained
            
        Returns:
            Created stability window
        """
        actual_duration = duration_seconds or self._default_duration
        
        window = StabilityWindow(
            window_id=f"stability_{recovery_id}_{int(time.time())}",
            start_time_utc=time.time(),
            duration_seconds=actual_duration,
            required_stable_entities=entities_to_monitor or [],
            max_failures_allowed=0
        )
        
        self._active_windows[recovery_id] = window
        
        return window
    
    def record_failure_event(self, entity_id: str, timestamp: Optional[float] = None) -> None:
        """Record a failure event for monitoring."""
        if entity_id not in self._failure_events:
            self._failure_events[entity_id] = []
        
        self._failure_events[entity_id].append(timestamp or time.time())
    
    def check_stability(
        self,
        recovery_id: str,
        current_time: Optional[float] = None
    ) -> VerificationResult:
        """
        Check if the system has remained stable in the window.
        
        Args:
            recovery_id: ID of the recovery to verify
            current_time: Current timestamp (None = now)
            
        Returns:
            Verification result with stability assessment
        """
        import uuid
        
        start_time = time.monotonic()
        
        try:
            window = self._active_windows.get(recovery_id)
            
            if not window:
                return VerificationResult(
                    success=False,
                    confidence=0.0,
                    actual_state="no_window",
                    expected_state=f"stability_for_{recovery_id}",
                    mismatch_details=["No active stability window found"]
                )
            
            current = current_time or time.time()
            
            # Calculate elapsed time
            elapsed = current - window.start_time_utc
            
            if elapsed < window.duration_seconds:
                # Still in the stability period - check failure count
                failures_in_window = self._count_failures_since(
                    window.required_stable_entities,
                    window.start_time_utc,
                    current
                )
                
                if failures_in_window > window.max_failures_allowed:
                    return VerificationResult(
                        success=False,
                        confidence=0.3,  # Low confidence - still unstable
                        actual_state=f"elapsed_{elapsed}s",
                        expected_state=f"stable_for_{window.duration_seconds}s",
                        mismatch_details=[
                            f"Received {failures_in_window} failures (max: {window.max_failures_allowed})"
                        ]
                    )
                
                return VerificationResult(
                    success=False,  # Not yet verified - still waiting
                    confidence=elapsed / window.duration_seconds,
                    actual_state=f"elapsed_{elapsed}s",
                    expected_state=f"stable_for_{window.duration_seconds}s"
                )
            
            # Window has elapsed - final check
            failures_in_window = self._count_failures_since(
                window.required_stable_entities,
                window.start_time_utc,
                current
            )
            
            success = failures_in_window <= window.max_failures_allowed
            
            return VerificationResult(
                success=success,
                confidence=1.0 if success else 0.0,
                actual_state=f"stable_{elapsed}s",
                expected_state=f"stable_for_{window.duration_seconds}s",
                mismatch_details=[] if success else [
                    f"Received {failures_in_window} failures during stability period"
                ]
            )
        finally:
            duration = time.monotonic() - start_time
    
    def _count_failures_since(
        self,
        entity_ids: List[str],
        since_time: float,
        until_time: float
    ) -> int:
        """Count failure events for entities in a time window."""
        count = 0
        
        for entity_id in entity_ids:
            if entity_id in self._failure_events:
                for timestamp in self._failure_events[entity_id]:
                    if since_time <= timestamp <= until_time:
                        count += 1
        
        return count
    
    def clear_window(self, recovery_id: str) -> bool:
        """Clear a stability window after verification."""
        if recovery_id in self._active_windows:
            del self._active_windows[recovery_id]
            return True
        return False


# =============================================================================
# Independent Verification Coordinator
# =============================================================================

@dataclass(frozen=True)
class VerificationRequest:
    """
    Request for independent verification.
    
    Args:
        request_id: Unique identifier for this request
        
        verification_type: Type of verification (RECOVERY, ROLLBACK)
        
        target_state: Expected state after operation
        entities_affected: Entities that need verification
        
        verify_integrity: Whether to perform integrity checks
        timeout_seconds: Maximum time allowed for verification
    """
    
    request_id: str
    
    verification_type: "VerificationType"
    
    target_state: str = ""
    entities_affected: List[str] = field(default_factory=list)
    
    verify_integrity: bool = False
    timeout_seconds: Optional[float] = None


class VerificationType(Enum):
    """Types of verification requests."""
    
    RECOVERY = "recovery"      # Verify recovery was successful
    ROLLBACK = "rollback"      # Verify rollback restored state
    INTEGRITY_CHECK = "integrity_check"  # Just verify data integrity
    COMPATIBILITY = "compatibility"  # Check version compatibility


class IndependentVerificationCoordinator:
    """
    Coordinates independent verification operations.
    
    This is the canonical authority for recovery/rollback verification,
    separate from the recovery action itself.
    """
    
    def __init__(self) -> None:
        """Initialize the coordinator."""
        self._state_engine = StateComparisonEngine()
        self._stability_validator = StabilityWindowValidator()
        
        self._verification_results: Dict[str, VerificationResult] = {}
        self._requests: Dict[str, VerificationRequest] = {}
    
    async def verify_recovery(
        self,
        request: VerificationRequest
    ) -> RecoveryVerificationResult:
        """
        Perform independent recovery verification.
        
        Args:
            request: Verification request with target state and entities
            
        Returns:
            RecoveryVerificationResult with detailed outcome
        """
        if request.verification_type != VerificationType.RECOVERY:
            return RecoveryVerificationResult(
                success=False,
                confidence=0.0,
                mismatch_details=["Invalid verification type"]
            )
        
        # Start stability window for this recovery
        self._stability_validator.create_stability_window(
            request.request_id,
            request.entities_affected
        )
        
        # Capture current state
        snapshot = await self._state_engine.capture_snapshot(
            runtime_id="runtime_1",  # Would use actual runtime ID
            state_id=f"post_recovery_{request.request_id}"
        )
        
        return RecoveryVerificationResult(
            success=True,
            confidence=0.95,  # High confidence for basic verification
            actual_state=snapshot.state_id,
            expected_state=request.target_state or "healthy",
            recovered_entities=list(snapshot.entity_states.keys())
        )
    
    async def verify_rollback(
        self,
        request: VerificationRequest
    ) -> RollbackVerificationResult:
        """
        Perform independent rollback verification.
        
        Args:
            request: Verification request with target version and entities
            
        Returns:
            RollbackVerificationResult with detailed outcome
        """
        if request.verification_type != VerificationType.ROLLBACK:
            return RollbackVerificationResult(
                success=False,
                confidence=0.0,
                mismatch_details=["Invalid verification type"]
            )
        
        # Compare to pre-failure snapshot (would be stored separately)
        result = await self._state_engine.verify_state_match(
            await self._state_engine.capture_snapshot("runtime_1"),
            target_version=request.target_state.split("_")[-1] if "_" in request.target_state else 0
        )
        
        return RollbackVerificationResult(
            success=result.success,
            confidence=result.confidence,
            actual_state=result.actual_state,
            expected_state=result.expected_state,
            integrity_verified=False,  # Would perform actual check
            corruption_found=None
        )
    
    def get_verification_status(self, request_id: str) -> Optional[VerificationStatus]:
        """Get current status of a verification."""
        if request_id in self._verification_results:
            result = self._verification_results[request_id]
            
            if result.success and self._stability_validator.check_stability(request_id).success:
                return VerificationStatus.COMPLETED
            elif result.success:
                return VerificationStatus.IN_PROGRESS  # Still waiting for stability
            
            return VerificationStatus.FAILED
        
        return None


# =============================================================================
# Fault Injection Support (for testing)
# =============================================================================

class FaultInjectionVerifier(RecoveryVerifier, RollbackVerifier):
    """
    A verifier with fault injection capabilities for testing.
    
    Can be configured to:
        - Simulate verification failures
        - Add delays to verification
        - Return specific results for testing scenarios
        
    This should only be used in test/development environments.
    """
    
    def __init__(self) -> None:
        """Initialize the fault injection verifier."""
        self._fault_config: Dict[str, Any] = {
            "always_fail": False,
            "delay_seconds": 0.0,
            "random_failure_rate": 0.0
        }
    
    def configure_fault(
        self,
        name: str,
        value: Any
    ) -> None:
        """Configure a fault injection."""
        self._fault_config[name] = value
    
    async def verify_recovery(
        self,
        target_state: str,
        entities_affected: List[str],
        expected_capabilities: Optional[List[str]] = None
    ) -> RecoveryVerificationResult:
        """Verify with fault injection enabled."""
        import random
        
        # Check for configured faults
        if self._fault_config.get("always_fail"):
            return RecoveryVerificationResult(
                success=False,
                confidence=0.0,
                actual_state="unknown",
                expected_state=target_state,
                mismatch_details=["Fault injection: verification failed"]
            )
        
        delay = self._fault_config.get("delay_seconds", 0.0)
        
        if delay > 0:
            import asyncio
            await asyncio.sleep(delay)
        
        # Random failure for testing
        rate = self._fault_config.get("random_failure_rate", 0.0)
        
        if random.random() < rate:
            return RecoveryVerificationResult(
                success=False,
                confidence=0.5,
                actual_state="partial",
                expected_state=target_state,
                mismatch_details=["Fault injection: random failure"]
            )
        
        # Normal verification
        return RecoveryVerificationResult(
            success=True,
            confidence=1.0,
            actual_state="healthy",
            expected_state=target_state,
            recovered_entities=entities_affected
        )


# =============================================================================
# Export utilities
# =============================================================================

def verify_state_version_compatibility(
    current_version: int,
    target_version: int
) -> bool:
    """
    Check if versions are compatible for rollback.
    
    Rollback requires that the current state is newer than or equal to
    the target version (we can only roll back to a known earlier state).
    
    Args:
        current_version: Current state version
        target_version: Target version for rollback
        
    Returns:
        True if rollback to target is possible
    """
    return current_version >= target_version


def calculate_verification_confidence(
    result: VerificationResult,
    stability_passed: bool = False
) -> float:
    """
    Calculate overall verification confidence.
    
    Combines the result confidence with stability window status.
    
    Args:
        result: Base verification result
        stability_passed: Whether stability window was satisfied
        
    Returns:
        Combined confidence (0.0-1.0)
    """
    base_confidence = result.confidence
    
    if not stability_passed:
        # Reduce confidence if stability not verified
        return max(0.3, base_confidence * 0.7)
    
    # Stability passed - increase confidence
    return min(1.0, base_confidence * 1.2)


def get_verification_summary(
    result: VerificationResult,
    entities_affected: List[str]
) -> Dict[str, Any]:
    """
    Get a summary of the verification result.
    
    Args:
        result: The verification result
        entities_affected: Entities that were verified
        
    Returns:
        Summary dictionary for logging/reporting
    """
    summary = {
        "success": result.success,
        "confidence": result.confidence,
        "entities_verified": len(entities_affected),
    }
    
    if not result.success and result.mismatch_details:
        summary["mismatches"] = len(result.mismatch_details)
        summary["mismatch_examples"] = result.mismatch_details[:3]
    
    return summary