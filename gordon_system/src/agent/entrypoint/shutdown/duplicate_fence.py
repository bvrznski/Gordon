# File-Based Duplicate Shutdown Fence
# ======================================
"""
Implementation of file-based fencing for duplicate shutdown detection.

Phase 3.7.34-I: Agent Entrypoint Shutdown Coordination Remediation

Architecture:
    The Coordinator delegates shutdown to Core but maintains ownership of
    the fence mechanism. This ensures only one shutdown process can execute
    at a time.
    
Fence Mechanism:
    - Uses atomic file lock via os.open() with O_CREAT|O_EXCL
    - Stores execution ID in lock file for tracking
    - Removes lock on successful shutdown completion
    - Handles stale locks with TTL-based expiration
"""

import os
import time
import uuid
import json
import glob
from typing import Optional, Dict, Any
from dataclasses import dataclass, field

# Default fence directory (configurable via environment)
FENCE_DIR = "/tmp/gordon_shutdown_fence"


@dataclass(frozen=True)
class FenceState:
    """Current state of the shutdown fence."""
    
    is_locked: bool
    lock_file_path: str
    lock_holder_id: Optional[str] = None
    lock_created_at: float = field(default_factory=time.time)
    ttl_seconds: float = 300.0  # 5 minute TTL for stale locks


class DuplicateShutdownFence:
    """
    File-based fence to prevent duplicate shutdown execution.
    
    Uses atomic file creation with O_CREAT|O_EXCL flags to ensure
    only one process can acquire the lock at a time.
    
    Lock file format (JSON):
        {
            "execution_id": "uuid",
            "runtime_id": "runtime_identifier",
            "created_at": timestamp,
            "ttl_seconds": 300.0
        }
    """
    
    def __init__(
        self,
        runtime_id: str,
        fence_dir: str = FENCE_DIR,
        ttl_seconds: float = 300.0
    ):
        """
        Initialize the fence.
        
        Args:
            runtime_id: The runtime to fence against duplicate shutdowns
            fence_dir: Directory where lock files are stored
            ttl_seconds: Time-to-live for stale lock detection (default: 5 min)
        """
        self._runtime_id = runtime_id
        self._fence_dir = fence_dir
        self._ttl_seconds = ttl_seconds
        
        # Generate unique execution ID for this fence attempt
        self._execution_id = str(uuid.uuid4())
        
        # Lock file path (one per runtime_id)
        self._lock_file_path = os.path.join(
            fence_dir, f"shutdown_{runtime_id.replace('/', '_')}.lock"
        )
        
        # Current lock state
        self._is_locked: bool = False
        
    @property
    def lock_file_path(self) -> str:
        """Return the path to the lock file."""
        return self._lock_file_path
    
    @property
    def is_locked(self) -> bool:
        """Check if this instance currently holds the lock."""
        return self._is_locked
    
    def acquire_lock(self) -> tuple[bool, Optional[str]]:
        """
        Attempt to acquire the shutdown fence lock.
        
        Returns:
            Tuple of (acquired: bool, existing_execution_id_or_none)
        """
        # Ensure fence directory exists
        os.makedirs(self._fence_dir, exist_ok=True)
        
        try:
            # Atomic file creation - fails if file already exists
            fd = os.open(
                self._lock_file_path,
                os.O_CREAT | os.O_EXCL | os.O_WRONLY,
                0o644
            )
            
            # Write lock metadata
            lock_data = {
                "execution_id": self._execution_id,
                "runtime_id": self._runtime_id,
                "created_at": time.time(),
                "ttl_seconds": self._ttl_seconds
            }
            
            os.write(fd, json.dumps(lock_data).encode("utf-8"))
            os.close(fd)
            
            self._is_locked = True
            return True, None
            
        except FileExistsError:
            # Lock file exists - check if it's stale or valid
            return False, self._check_existing_lock()
    
    def _check_existing_lock(self) -> Optional[str]:
        """
        Check an existing lock to determine if it's still valid.
        
        Returns:
            Existing execution ID if lock is valid, None if stale/expired
        """
        try:
            with open(self._lock_file_path, "r") as f:
                lock_data = json.load(f)
            
            created_at = lock_data.get("created_at", 0)
            ttl = lock_data.get("ttl_seconds", self._ttl_seconds)
            
            # Check if lock has expired (stale)
            if time.time() - created_at > ttl:
                return None  # Stale lock, will be cleaned up
            
            # Valid existing lock
            return lock_data.get("execution_id")
            
        except (OSError, json.JSONDecodeError):
            # Corrupted or unreadable lock file - treat as stale
            return None
    
    def release_lock(self) -> bool:
        """
        Release the shutdown fence lock.
        
        Returns:
            True if lock was released, False if it wasn't held
        """
        if not self._is_locked:
            return False
        
        try:
            os.remove(self._lock_file_path)
            self._is_locked = False
            return True
            
        except OSError:
            # Lock file may have been removed by another process
            self._is_locked = False
            return False
    
    def cleanup_stale_locks(self) -> int:
        """
        Remove stale locks that have exceeded their TTL.
        
        Returns:
            Count of removed locks
        """
        if not os.path.exists(self._fence_dir):
            return 0
        
        count = 0
        lock_files = glob.glob(os.path.join(self._fence_dir, "*.lock"))
        
        for lock_file in lock_files:
            try:
                with open(lock_file, "r") as f:
                    lock_data = json.load(f)
                
                created_at = lock_data.get("created_at", 0)
                ttl = lock_data.get("ttl_seconds", self._ttl_seconds)
                
                if time.time() - created_at > ttl:
                    os.remove(lock_file)
                    count += 1
                    
            except (OSError, json.JSONDecodeError):
                # Corrupted file - remove it
                try:
                    os.remove(lock_file)
                    count += 1
                except OSError:
                    pass
        
        return count


def get_fence_state(runtime_id: str, fence_dir: str = FENCE_DIR) -> FenceState:
    """
    Get current fence state for a runtime.
    
    Args:
        runtime_id: The runtime to check
        fence_dir: Directory where lock files are stored
        
    Returns:
        FenceState with current lock status
    """
    lock_file_path = os.path.join(fence_dir, f"shutdown_{runtime_id.replace('/', '_')}.lock")
    
    if not os.path.exists(lock_file_path):
        return FenceState(
            is_locked=False,
            lock_file_path=lock_file_path
        )
    
    try:
        with open(lock_file_path, "r") as f:
            lock_data = json.load(f)
        
        created_at = lock_data.get("created_at", 0)
        ttl = lock_data.get("ttl_seconds", 300.0)
        
        return FenceState(
            is_locked=True,
            lock_file_path=lock_file_path,
            lock_holder_id=lock_data.get("execution_id"),
            lock_created_at=created_at,
            ttl_seconds=ttl
        )
        
    except (OSError, json.JSONDecodeError):
        # Corrupted file - report as not locked (will be cleaned up)
        return FenceState(
            is_locked=False,
            lock_file_path=lock_file_path
        )