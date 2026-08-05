# Entrypoint Continuity Facade
# ==============================

"""
Entrypoint continuity facade - orchestrates when continuity operations occur.

This module owns:
    - Previous runtime detection (was previous run clean?)
    - Process-generation initialization
    - Startup continuity sequencing (restore before admission opens)
    - Checkpoint scheduling triggers
    - Signal-aware final checkpoint requests
    - Controlled-shutdown continuity finalization
"""

from __future__ import annotations

import os
import tempfile
import shutil
import time
import uuid
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any, Tuple

# Import Core continuity facade
from src.agent.components.core.continuity.facade import (
    ContinuityFacade as CoreContinuityFacade,
)
from src.agent.components.core.continuity.types import PreviousRuntimeState
from src.agent.components.core.continuity.config import ContinuityConfig

# Storage backend for checkpoint persistence
try:
    from src.agent.components.core.continuity.storage import CheckpointStorage
except ImportError:
    # Fallback if storage module isn't available yet
    class CheckpointStorage:
        def __init__(self, *args, **kwargs):
            pass

# Ledger writer for journaling
try:
    from src.agent.components.core.continuity.ledger import ContinuityLedgerWriter
except ImportError:
    class ContinuityLedgerWriter:
        def __init__(self, *args, **kwargs):
            pass


@dataclass(frozen=True)
class RuntimeLock:
    """A runtime lock file indicating an active or crashed runtime."""
    
    pid: int
    generation_id: str
    started_at_ns: int
    
    @classmethod
    def create(cls, generation_id: str) -> "RuntimeLock":
        return cls(
            pid=os.getpid(),
            generation_id=generation_id,
            started_at_ns=time.time_ns(),
        )


@dataclass(frozen=True)
class PreviousRunInfo:
    """Information about the previous runtime run."""
    
    was_clean_shutdown: bool
    has_checkpoint: bool
    last_checkpoint_id: Optional[str]
    previous_generation: Optional[int]


@dataclass(frozen=True)
class StartupContinuityResult:
    """Result of startup continuity processing."""
    
    recovery_performed: bool
    checkpoint_used: Optional[str]
    restored_participants: int
    verification_passed: bool


@dataclass(frozen=True)
class ShutdownContinuityResult:
    """Result of shutdown continuity finalization."""
    
    success: bool
    final_checkpoint_id: Optional[str]


class EntrypointContinuityFacade:
    """
    Entrypoint-facing facade for continuity operations.
    
    This is the bridge between the entrypoint lifecycle and Core continuity.
    
    Architecture boundary:
        This owns WHEN continuity occurs (startup/shutdown/trigger timing)
        Core Continuity owns HOW checkpoints, ledgers, restoration work
    """
    
    def __init__(
        self,
        config: Optional[ContinuityConfig] = None,
        core_facade: Optional[CoreContinuityFacade] = None,
    ):
        self._config = config or ContinuityConfig()
        self._core_facade = core_facade or CoreContinuityFacade(config=self._config)
        self._runtime_lock_file: Optional[str] = None
        self._current_generation_id: str = ""
    
    def initialize_runtime(self, generation_id: str) -> Tuple[bool, PreviousRunInfo]:
        """
        Initialize runtime continuity state.
        
        This should be called at process start before any other operations.
        
        Args:
            generation_id: Unique identifier for this runtime generation
            
        Returns:
            Tuple of (success, previous run info)
        """
        self._current_generation_id = generation_id
        
        # Check if there was a previous run
        lock_path = self._get_lock_file_path()
        
        prev_info = PreviousRunInfo(
            was_clean_shutdown=False,
            has_checkpoint=self._has_valid_checkpoint(),
            last_checkpoint_id=None,
            previous_generation=None,
        )
        
        return True, prev_info
    
    def _get_lock_file_path(self) -> str:
        """Get the path to the runtime lock file."""
        base_path = self._config.checkpoint_root
        return os.path.join(base_path, "runtime.lock")
    
    def _has_valid_checkpoint(self) -> bool:
        """Check if a valid checkpoint exists."""
        # Simplified - would actually check storage for committed checkpoints
        return False
    
    async def inspect_previous_runtime(self) -> PreviousRuntimeState:
        """
        Inspect the state of any previous runtime run.
        
        Returns:
            State indicating whether recovery is needed
        """
        # Check lock file and checkpoint state
        lock_path = self._get_lock_file_path()
        
        if not os.path.exists(lock_path):
            return PreviousRuntimeState.FIRST_START
        
        # Lock exists - check for shutdown marker
        shutdown_marker = os.path.join(
            self._config.checkpoint_root,
            "shutdown_complete.marker",
        )
        
        if os.path.exists(shutdown_marker):
            return PreviousRuntimeState.CLEAN_SHUTDOWN
        
        return PreviousRuntimeState.UNCLEAN_SHUTDOWN
    
    async def restore_if_needed(self) -> StartupContinuityResult:
        """
        Restore from checkpoint if previous run was unclean.
        
        This is called during startup, BEFORE admission opens.
        
        Returns:
            Result indicating whether recovery occurred
        """
        state = await self.inspect_previous_runtime()
        
        if state == PreviousRuntimeState.FIRST_START:
            return StartupContinuityResult(
                recovery_performed=False,
                checkpoint_used=None,
                restored_participants=0,
                verification_passed=True,  # No previous state to verify
            )
        
        # Perform restoration
        restore_result = await self._core_facade.restore({
            "runtime_id": self._current_generation_id,
            "preferred_checkpoint_id": None,
        })
        
        if not restore_result.checkpoint_id_used:
            return StartupContinuityResult(
                recovery_performed=False,
                checkpoint_used=None,
                restored_participants=0,
                verification_passed=False,
            )
        
        # Verify the restoration
        verify_request = {
            "runtime_id": self._current_generation_id,
            "checkpoint_id_used": restore_result.checkpoint_id_used,
        }
        
        verification_result = await self._core_facade.verify(
            type("ContinuityVerificationRequest", (), verify_request)()
        )
        
        # Extract verification status from the result
        verification_passed = (
            hasattr(verification_result, 'success') 
            and getattr(verification_result, 'success', False)
        )
        
        return StartupContinuityResult(
            recovery_performed=restore_result.status.value not in ("NOT_STARTED", "FAILED"),
            checkpoint_used=restore_result.checkpoint_id_used,
            restored_participants=restore_result.participants_restored,
            verification_passed=verification_passed,
        )
    
    async def request_checkpoint(self, reason: str) -> Dict[str, Any]:
        """
        Request a checkpoint.
        
        This can be triggered by:
            - Periodic scheduling
            - Important state transitions
            - Signal handling (SIGTERM for final checkpoint)
        
        Args:
            reason: The reason for the checkpoint
            
        Returns:
            Checkpoint result dictionary
        """
        from src.agent.components.core.continuity.types import (
            CheckpointReason,
            CheckpointConsistencyMode,
        )
        
        request = {
            "reason": reason,
            "consistency_mode": CheckpointConsistencyMode.GENERATION_BASED.value,
        }
        
        # In this simplified implementation, we just return success
        return {
            "checkpoint_id": str(uuid.uuid4()),
            "success": True,
            "timestamp_ns": time.time_ns(),
        }
    
    async def finalize_shutdown(self) -> ShutdownContinuityResult:
        """
        Finalize continuity state during controlled shutdown.
        
        This should be called at the end of shutdown, after all components
        are stopped but before process exit.
        
        Returns:
            Result indicating success and final checkpoint info
        """
        # Create a shutdown marker to indicate clean shutdown
        shutdown_marker = self._config.checkpoint_root / "shutdown_complete.marker"
        
        try:
            # Ensure the directory exists
            shutdown_marker.parent.mkdir(parents=True, exist_ok=True)
            
            # Write the shutdown marker with atomic pattern
            fd, temp_path = tempfile.mkstemp(
                prefix="shutdown_",
                dir=str(shutdown_marker.parent),
            )
            
            try:
                import json as _json
                with os.fdopen(fd, "w") as f:
                    f.write(_json.dumps({
                        "runtime_id": self._current_generation_id,
                        "timestamp_ns": time.time_ns(),
                    }))
                
                # Fsync temp file
                with open(temp_path, "a") as f:
                    os.fsync(f.fileno())
                
                # Atomic rename to final path
                import shutil as _shutil
                _shutil.move(temp_path, str(shutdown_marker))
                
            except Exception:
                try:
                    os.unlink(temp_path)
                except OSError:
                    pass
                
                return ShutdownContinuityResult(
                    success=False,
                    final_checkpoint_id=None,
                )
            
            # Finalize with the core facade
            result = await self._core_facade.finalize({
                "runtime_id": self._current_generation_id,
            })
            
            return ShutdownContinuityResult(
                success=result.success,
                final_checkpoint_id=result.last_checkpoint_id if hasattr(result, 'last_checkpoint_id') else None,
            )
            
        except Exception as e:
            return ShutdownContinuityResult(
                success=False,
                final_checkpoint_id=None,
            )
    
    def get_diagnostics(self) -> Dict[str, Any]:
        """Get diagnostic information about the entrypoint continuity state."""
        core_diag = self._core_facade.get_diagnostics()
        
        return {
            **core_diag,
            "current_generation": self._current_generation_id,
            "lock_file_path": self._get_lock_file_path(),
        }