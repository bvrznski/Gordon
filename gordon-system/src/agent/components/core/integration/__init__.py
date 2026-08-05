# Runtime Integration Layer - Readiness, Admission, Operational State
# ======================================================================

"""
Integration layer for readiness, admission, and operational state authorities.

This module provides:
- Cross-authority coordination
- State synchronization
- Revocation propagation (readiness → admission → operational)
- Multi-runtime isolation
"""

from dataclasses import dataclass, field
from typing import Dict, List, Tuple, Optional, Any, Callable
from enum import Enum
import time


# =============================================================================
# INTEGRATION CONFIGURATION
# =============================================================================

@dataclass(frozen=True)
class IntegrationConfig:
    """Configuration for integration between authorities."""
    # State sync intervals (seconds)
    state_sync_interval: float = 1.0
    
    # Revocation propagation delay
    revocation_delay_seconds: float = 0.0  # No delay by default
    
    # Multi-runtime isolation settings
    isolate_by_runtime_id: bool = True
    
    # Timeout for cross-authority calls
    call_timeout_seconds: float = 30.0


# =============================================================================
# STATE SYNCHRONIZATION
# =============================================================================

class StateSyncStatus(Enum):
    """Status of state synchronization."""
    SYNCHRONIZED = "synchronized"
    OUT_OF_SYNC = "out_of_sync"
    UNKNOWN = "unknown"


@dataclass(frozen=True)
class StateSyncResult:
    """Result of a state synchronization attempt."""
    runtime_id: str
    timestamp_utc: float
    
    readiness_version: int
    admission_version: int
    operational_version: int
    
    status: StateSyncStatus
    drift_detected: bool = False
    sync_errors: Tuple[str, ...] = field(default_factory=tuple)


# =============================================================================
# INTEGRATION CONTROLLER
# =============================================================================

class RuntimeIntegrationController:
    """
    Coordinates readiness, admission, and operational state.
    
    This is NOT an authority for any domain. Instead, it:
        - Synchronizes state between authorities
        - Propagates revocations across boundaries
        - Validates cross-domain consistency
    
    Invariants maintained:
        1. Operational mode requires valid readiness
        2. Admission opened requires operational mode permits it
        3. Readiness revocation closes/restricts admission
    """
    
    def __init__(
        self,
        runtime_id: str,
        config: Optional[IntegrationConfig] = None
    ):
        self._runtime_id = runtime_id
        self._config = config or IntegrationConfig()
        
        # Lock for thread safety
        self._lock = __import__('threading').RLock()
        
        # References to authorities (set by caller)
        self._readiness_controller: Optional[Any] = None
        self._admission_controller: Optional[Any] = None
        self._operational_authority: Optional[Any] = None
        
        # State tracking
        self._last_sync_time: float = 0.0
        self._state_versions: Dict[str, int] = {}
    
    def set_readiness_controller(self, controller: Any) -> None:
        """Set reference to readiness controller."""
        with self._lock:
            self._readiness_controller = controller
    
    def set_admission_controller(self, controller: Any) -> None:
        """Set reference to admission controller."""
        with self._lock:
            self._admission_controller = controller
    
    def set_operational_authority(self, authority: Any) -> None:
        """Set reference to operational authority."""
        with self._lock:
            self._operational_authority = authority
    
    # -------------------------------------------------------------------------
    # State Synchronization
    # -------------------------------------------------------------------------
    
    async def sync_state(self) -> StateSyncResult:
        """
        Synchronize state between authorities.
        
        Checks for consistency and drift between:
            - Readiness status
            - Admission status  
            - Operational mode
        
        Returns:
            StateSyncResult with synchronization status
        """
        with self._lock:
            now = time.time()
            
            # Get current states
            readiness_version = 0
            admission_version = 0
            operational_version = 0
            
            if self._readiness_controller:
                try:
                    snapshot = self._readiness_controller.get_snapshot()
                    readiness_version = getattr(snapshot, 'state_version', 0)
                except Exception:
                    pass
            
            if self._admission_controller:
                try:
                    snapshot = self._admission_controller.get_snapshot()
                    admission_version = getattr(snapshot, 'state_version', 0)
                except Exception:
                    pass
            
            if self._operational_authority:
                try:
                    operational_state = getattr(self._operational_authority, 'state', None)
                    operational_version = hash(str(operational_state)) % (2**31) if operational_state else 0
                except Exception:
                    pass
            
            # Determine sync status
            drift_detected = self._check_drift(
                readiness_version,
                admission_version,
                operational_version
            )
            
            if not drift_detected and all(v > 0 for v in [
                readiness_version, admission_version, operational_version
            ]):
                status = StateSyncStatus.SYNCHRONIZED
            else:
                status = StateSyncStatus.OUT_OF_SYNC
            
            self._last_sync_time = now
            self._state_versions['readiness'] = readiness_version
            self._state_versions['admission'] = admission_version
            self._state_versions['operational'] = operational_version
            
            return StateSyncResult(
                runtime_id=self._runtime_id,
                timestamp_utc=now,
                readiness_version=readiness_version,
                admission_version=admission_version,
                operational_version=operational_version,
                status=status,
                drift_detected=drift_detected
            )
    
    def _check_drift(
        self,
        readiness_version: int,
        admission_version: int,
        operational_version: int
    ) -> bool:
        """Check for state drift between authorities."""
        # Compare versions - if they've diverged significantly, there's drift
        max_version = max(readiness_version, admission_version, operational_version)
        
        # Allow some tolerance but flag significant differences
        tolerance = 100  # Configurable
        
        return any(
            abs(v - max_version) > tolerance
            for v in [readiness_version, admission_version, operational_version]
        )
    
    # -------------------------------------------------------------------------
    # Revocation Propagation
    # -------------------------------------------------------------------------
    
    async def handle_readiness_revoked(self, reason: str) -> None:
        """
        Handle readiness revocation - must close/restrict admission.
        
        When readiness is revoked, we must prevent new work from entering
        because the runtime can no longer safely accept it.
        """
        with self._lock:
            if not self._admission_controller:
                return
            
            # Close or restrict admission based on reason severity
            is_critical = "failure" in reason.lower() or "lost" in reason.lower()
            
            if is_critical:
                # Critical readiness loss - close admission completely
                try:
                    self._admission_controller.close_admission(f"Readiness revoked: {reason}")
                except Exception:
                    pass  # Don't let errors prevent revocation handling
            else:
                # Non-critical - restrict rather than close
                try:
                    self._admission_controller.revoke_admission(f"Readiness degraded: {reason}")
                except Exception:
                    pass
    
    async def handle_operational_transition(
        self,
        from_mode: str,
        to_mode: str
    ) -> None:
        """
        Handle operational state transition - may affect admission.
        
        Examples:
            - OPERATIONAL → DEGRADED: May restrict admission classes
            - DEGRADED → OPERATIONAL: May restore admission
            - OPERATIONAL → STOPPING: Close admission, drain queue
        """
        with self._lock:
            if not self._admission_controller:
                return
            
            if to_mode in ("STOPPING", "STOPPED"):
                # Closing for shutdown/quiescence
                try:
                    self._admission_controller.close_admission(f"Operational transition to {to_mode}")
                except Exception:
                    pass
            
            elif to_mode == "DEGRADED":
                # May want to restrict admission classes
                try:
                    self._admission_controller.revoke_admission("Entering degraded mode")
                except Exception:
                    pass
    
    async def validate_transition_to_operational(
        self,
        readiness_ready: bool,
        admission_open: bool
    ) -> Tuple[bool, List[str]]:
        """
        Validate whether transition to operational is allowed.
        
        Returns:
            Tuple of (allowed, list of blockers if not allowed)
        """
        blockers = []
        
        # Check readiness requirement
        if not readiness_ready:
            blockers.append("Readiness not satisfied")
        
        # Check admission status
        if not admission_open:
            blockers.append("Admission not open")
        
        return len(blockers) == 0, blockers
    
    # -------------------------------------------------------------------------
    # State Queries
    # -------------------------------------------------------------------------
    
    def get_integration_snapshot(self) -> Dict[str, Any]:
        """Get a snapshot of integration state."""
        with self._lock:
            readiness_state = None
            admission_state = None
            operational_state = None
            
            if self._readiness_controller:
                try:
                    readiness_state = self._readiness_controller.get_status().value
                except Exception:
                    pass
            
            if self._admission_controller:
                try:
                    snapshot = self._admission_controller.get_snapshot()
                    admission_state = getattr(snapshot, 'status', None)
                except Exception:
                    pass
            
            if self._operational_authority:
                try:
                    operational_state = str(getattr(self._operational_authority, 'state', None))
                except Exception:
                    pass
            
            return {
                "runtime_id": self._runtime_id,
                "last_sync_time": self._last_sync_time,
                "readiness_status": readiness_state,
                "admission_status": admission_state,
                "operational_state": operational_state,
                "state_versions": dict(self._state_versions)
            }


# =============================================================================
# PUBLIC API EXPORTS
# =============================================================================

__all__ = [
    # Configuration
    "IntegrationConfig",
    
    # State sync
    "StateSyncStatus",
    "StateSyncResult",
    
    # Integration controller
    "RuntimeIntegrationController",
]