# Filesystem Effector Implementation
# ===================================

"""
Filesystem effectors for the Action Runtime.

This module provides side-effecting operations on the filesystem that
pass through the canonical execution authority.

Architecture:
    ActionRuntime (ActionExecutor)
        ↓ dispatches
    FilesystemEffector
        ↓ executes
    Actual filesystem modification

Key principles:
    - Path validation and traversal prevention
    - Explicit path roots (allowed directories)
    - Side effect reporting
    - Idempotency classification
    - Rollback support where possible
"""

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Tuple
from enum import Enum, auto
import os
import uuid
import time
import tempfile

from . import (
    EffectorId,
    ToolContract,
    EffectorContract,
    ActionRequest,
    ExecutionResult,
    ExecutionStatus,
)


class FilesystemOperation(Enum):
    """Filesystem operations supported by effectors."""
    
    # Read operations (low risk)
    READ_FILE = "read_file"
    LIST_DIRECTORY = "list_directory"
    CHECK_EXISTS = "check_exists"
    GET_METADATA = "get_metadata"
    
    # Write operations (medium risk)
    WRITE_FILE = "write_file"
    APPEND_FILE = "append_file"
    CREATE_DIRECTORY = "create_directory"
    
    # Delete operations (high risk)
    DELETE_FILE = "delete_file"
    DELETE_DIRECTORY = "delete_directory"
    MOVE_FILE = "move_file"
    COPY_FILE = "copy_file"


@dataclass(frozen=True)
class PathPolicy:
    """
    Policy for path validation.
    
    Args:
        allowed_roots: List of absolute paths that are valid targets
        deny_patterns: List of regex patterns to reject
        require_absolute: Whether relative paths are rejected
        max_depth: Maximum path component depth
    """
    
    allowed_roots: Tuple[str, ...]
    deny_patterns: Tuple[str, ...] = ()
    require_absolute: bool = True
    max_depth: int = 32


@dataclass(frozen=True)
class FilesystemEffect:
    """A single filesystem side effect."""
    
    operation: str  # e.g., "read", "write", "delete"
    path: str
    timestamp: float
    bytes_changed: Optional[int] = None
    is_directory: bool = False


@dataclass(frozen=True)
class FilesystemResult:
    """
    Result of a filesystem operation.
    
    Args:
        operation: The operation performed
        success: Whether the operation succeeded
        path: Target path
        content_hash: Hash of file contents (if applicable)
        bytes_read: Bytes read (for read ops)
        bytes_written: Bytes written (for write ops)
        side_effects: List of actual effects made
    """
    
    operation: str
    success: bool
    path: str
    
    # Content-related
    content_hash: Optional[str] = None
    content_length: Optional[int] = None
    
    # Side effects
    side_effects: Tuple[FilesystemEffect, ...] = field(default_factory=tuple)
    
    # Timing
    started_at: float = field(default_factory=time.monotonic)
    completed_at: Optional[float] = None


# =============================================================================
# PATH VALIDATION
# =============================================================================


def validate_path(path: str, policy: PathPolicy) -> Tuple[bool, Optional[str]]:
    """
    Validate a path against security policy.
    
    Args:
        path: The path to validate
        policy: The validation policy
        
    Returns:
        (is_valid, error_message)
    """
    # Check for absolute path if required
    if policy.require_absolute and not os.path.isabs(path):
        return False, f"Path must be absolute: {path}"
    
    # Resolve the full path
    try:
        resolved = os.path.realpath(path)
    except (OSError, ValueError) as e:
        return False, f"Invalid path: {e}"
    
    # Check against allowed roots
    in_allowed_root = any(
        resolved.startswith(root.rstrip(os.sep) + os.sep) or resolved == root
        for root in policy.allowed_roots
    )
    
    if not in_allowed_root:
        return False, f"Path outside allowed roots: {resolved}"
    
    # Check deny patterns (simplified - would use regex in production)
    for pattern in policy.deny_patterns:
        if pattern in path:
            return False, f"Path matches deny pattern: {pattern}"
    
    # Check depth
    depth = len(path.split(os.sep))
    if depth > policy.max_depth:
        return False, f"Path exceeds maximum depth ({depth} > {policy.max_depth})"
    
    return True, None


# =============================================================================
# FILESYSTEM EFFECTOR IMPLEMENTATION
# =============================================================================


class FilesystemEffector:
    """
    Effector for filesystem operations.
    
    All filesystem modifications go through this effector which:
        - Validates paths against policy
        - Reports side effects accurately
        - Supports rollback where possible
        - Enforces idempotency where applicable
    """
    
    def __init__(
        self,
        runtime_id: str,
        allowed_roots: Optional[Tuple[str, ...]] = None,
    ):
        self._runtime_id = runtime_id
        
        # Default allowed roots (example - would be configured by policy)
        self._allowed_roots = allowed_roots or (
            tempfile.gettempdir(),
        )
        
        self._path_policy = PathPolicy(
            allowed_roots=self._allowed_roots,
            require_absolute=True,
            max_depth=32,
        )
        
        # Tracking for rollback support
        self._operation_history: List[Dict[str, Any]] = []
    
    @property
    def effector_id(self) -> EffectorId:
        """Get the effector's identity."""
        return EffectorId("filesystem")
    
    def get_contract(self) -> EffectorContract:
        """Get the effector's contract."""
        return EffectorContract(
            effector_id=self.effector_id,
            name="Filesystem Effector",
            target_domain="filesystem",
            side_effect_class="mutate",
            reversibility="partially_reversible",
            required_capability=None,  # Would be set by policy
            is_idempotent=False,
            timeout_seconds=60.0,
            cancellation_policy="cooperative",
            supports_rollback=True,
            rollback_operation="undo_last_operation",
            supports_dry_run=True,
        )
    
    async def execute(self, request: ActionRequest) -> ExecutionResult:
        """
        Execute a filesystem operation.
        
        Args:
            request: The action request containing the operation
            
        Returns:
            Execution result with side effect report
        """
        # Validate required fields
        if not request.effector_id or str(request.effector_id) != "filesystem":
            return ExecutionResult(
                action_id=request.action_id,
                invocation_id=request.invocation_id,
                status=ExecutionStatus.FAILED,
                error="This effector only handles filesystem operations",
            )
        
        operation = FilesystemOperation(request.operation)
        
        # Execute based on operation type
        if operation == FilesystemOperation.READ_FILE:
            return await self._execute_read_file(request)
        elif operation == FilesystemOperation.WRITE_FILE:
            return await self._execute_write_file(request)
        elif operation == FilesystemOperation.LIST_DIRECTORY:
            return await self._execute_list_directory(request)
        elif operation == FilesystemOperation.DELETE_FILE:
            return await self._execute_delete_file(request)
        else:
            return ExecutionResult(
                action_id=request.action_id,
                invocation_id=request.invocation_id,
                status=ExecutionStatus.FAILED,
                error=f"Unsupported filesystem operation: {request.operation}",
            )
    
    async def _execute_read_file(self, request: ActionRequest) -> ExecutionResult:
        """Execute a file read operation."""
        path = request.arguments.get("path", "")
        
        # Validate path
        is_valid, error = validate_path(path, self._path_policy)
        if not is_valid:
            return ExecutionResult(
                action_id=request.action_id,
                invocation_id=request.invocation_id,
                status=ExecutionStatus.FAILED,
                error=f"Path validation failed: {error}",
            )
        
        try:
            with open(path, "rb") as f:
                content = f.read()
            
            # Calculate hash
            import hashlib
            content_hash = hashlib.sha256(content).hexdigest()
            
            # Record side effect
            self._operation_history.append({
                "type": "read",
                "path": path,
                "timestamp": time.monotonic(),
                "bytes_read": len(content),
            })
            
            return ExecutionResult(
                action_id=request.action_id,
                invocation_id=request.invocation_id,
                status=ExecutionStatus.SUCCEEDED,
                value={
                    "content": content,  # In production, use a reference
                    "content_hash": content_hash,
                    "length": len(content),
                },
                side_effects_reported=(
                    {"type": "read", "path": path, "bytes_read": len(content)},
                ),
            )
            
        except FileNotFoundError:
            return ExecutionResult(
                action_id=request.action_id,
                invocation_id=request.invocation_id,
                status=ExecutionStatus.FAILED,
                error=f"File not found: {path}",
            )
        except PermissionError:
            return ExecutionResult(
                action_id=request.action_id,
                invocation_id=request.invocation_id,
                status=ExecutionStatus.FAILED,
                error=f"Permission denied: {path}",
            )
    
    async def _execute_write_file(self, request: ActionRequest) -> ExecutionResult:
        """Execute a file write operation."""
        path = request.arguments.get("path", "")
        content = request.arguments.get("content", b"")
        
        # Validate path
        is_valid, error = validate_path(path, self._path_policy)
        if not is_valid:
            return ExecutionResult(
                action_id=request.action_id,
                invocation_id=request.invocation_id,
                status=ExecutionStatus.FAILED,
                error=f"Path validation failed: {error}",
            )
        
        try:
            # Create directory if needed
            os.makedirs(os.path.dirname(path), exist_ok=True)
            
            with open(path, "wb") as f:
                f.write(content)
            
            # Record for rollback
            self._operation_history.append({
                "type": "write",
                "path": path,
                "timestamp": time.monotonic(),
                "content_hash_before": None,  # Would track pre-change hash
            })
            
            return ExecutionResult(
                action_id=request.action_id,
                invocation_id=request.invocation_id,
                status=ExecutionStatus.SUCCEEDED,
                value={
                    "success": True,
                    "bytes_written": len(content),
                },
                side_effects_reported=(
                    {"type": "write", "path": path, "bytes_written": len(content)},
                ),
            )
            
        except PermissionError:
            return ExecutionResult(
                action_id=request.action_id,
                invocation_id=request.invocation_id,
                status=ExecutionStatus.FAILED,
                error=f"Permission denied: {path}",
            )
    
    async def _execute_list_directory(self, request: ActionRequest) -> ExecutionResult:
        """Execute a directory listing operation."""
        path = request.arguments.get("path", "")
        
        # Validate path
        is_valid, error = validate_path(path, self._path_policy)
        if not is_valid:
            return ExecutionResult(
                action_id=request.action_id,
                invocation_id=request.invocation_id,
                status=ExecutionStatus.FAILED,
                error=f"Path validation failed: {error}",
            )
        
        try:
            entries = os.listdir(path)
            
            # Record side effect
            self._operation_history.append({
                "type": "list",
                "path": path,
                "timestamp": time.monotonic(),
                "entries_count": len(entries),
            })
            
            return ExecutionResult(
                action_id=request.action_id,
                invocation_id=request.invocation_id,
                status=ExecutionStatus.SUCCEEDED,
                value={
                    "entries": entries,
                    "count": len(entries),
                },
                side_effects_reported=(
                    {"type": "list", "path": path, "entries_count": len(entries)},
                ),
            )
            
        except NotADirectoryError:
            return ExecutionResult(
                action_id=request.action_id,
                invocation_id=request.invocation_id,
                status=ExecutionStatus.FAILED,
                error=f"Not a directory: {path}",
            )
        except PermissionError:
            return ExecutionResult(
                action_id=request.action_id,
                invocation_id=request.invocation_id,
                status=ExecutionStatus.FAILED,
                error=f"Permission denied: {path}",
            )
    
    async def _execute_delete_file(self, request: ActionRequest) -> ExecutionResult:
        """Execute a file delete operation (high risk)."""
        path = request.arguments.get("path", "")
        
        # Validate path
        is_valid, error = validate_path(path, self._path_policy)
        if not is_valid:
            return ExecutionResult(
                action_id=request.action_id,
                invocation_id=request.invocation_id,
                status=ExecutionStatus.FAILED,
                error=f"Path validation failed: {error}",
            )
        
        try:
            # Check if file exists
            if not os.path.exists(path):
                return ExecutionResult(
                    action_id=request.action_id,
                    invocation_id=request.invocation_id,
                    status=ExecutionStatus.FAILED,
                    error=f"File not found: {path}",
                )
            
            # Record for potential rollback (move to trash)
            backup_path = f"{path}.bak_{uuid.uuid4().hex[:8]}"
            os.rename(path, backup_path)
            
            self._operation_history.append({
                "type": "delete",
                "original_path": path,
                "backup_path": backup_path,
                "timestamp": time.monotonic(),
            })
            
            return ExecutionResult(
                action_id=request.action_id,
                invocation_id=request.invocation_id,
                status=ExecutionStatus.SUCCEEDED,
                value={
                    "success": True,
                    "moved_to_trash": backup_path,
                },
                side_effects_reported=(
                    {"type": "delete", "path": path, "trashed_to": backup_path},
                ),
            )
            
        except PermissionError:
            return ExecutionResult(
                action_id=request.action_id,
                invocation_id=request.invocation_id,
                status=ExecutionStatus.FAILED,
                error=f"Permission denied: {path}",
            )
    
    async def rollback(self, count: int = 1) -> Tuple[bool, List[str]]:
        """
        Rollback the last N filesystem operations.
        
        Args:
            count: Number of operations to rollback
            
        Returns:
            (success, list of affected paths)
        """
        results = []
        
        for _ in range(count):
            if not self._operation_history:
                break
            
            op = self._operation_history.pop()
            
            try:
                if op["type"] == "delete":
                    # Restore from trash
                    backup_path = op.get("backup_path")
                    original_path = op.get("original_path")
                    
                    if backup_path and os.path.exists(backup_path):
                        os.rename(backup_path, original_path)
                        results.append(f"Restored {original_path}")
                
            except Exception as e:
                results.append(f"Rollback failed: {e}")
        
        return len(results) == count, results
    
    def get_operation_history(self) -> List[Dict[str, Any]]:
        """Get the operation history for audit/debugging."""
        return list(self._operation_history)
    
    async def clear_history(self) -> None:
        """Clear the operation history."""
        self._operation_history.clear()


# =============================================================================
# CONVENIENCE FACTORY
# =============================================================================


def create_filesystem_effector(
    runtime_id: str,
    allowed_roots: Optional[Tuple[str, ...]] = None,
) -> FilesystemEffector:
    """
    Create a filesystem effector with sensible defaults.
    
    Args:
        runtime_id: The runtime ID for this effector
        allowed_roots: Allowed path roots (defaults to temp directory)
        
    Returns:
        Configured FilesystemEffector instance
    """
    return FilesystemEffector(runtime_id, allowed_roots)


__all__ = [
    # Enums
    "FilesystemOperation",
    
    # Data classes
    "PathPolicy",
    "FilesystemEffect",
    "FilesystemResult",
    
    # Classes
    "FilesystemEffector",
    
    # Functions
    "validate_path",
    "create_filesystem_effector",
]