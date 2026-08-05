# Checkpoint Storage Backend
# ===========================

"""
Checkpoint storage infrastructure for continuity operations.

This module provides:
    - Atomic checkpoint file writes with temp file + rename pattern
    - fsync() durability guarantees
    - Checkpoint manifest management
    - Fragment persistence and retrieval
    - Cleanup of old checkpoints

Architecture:
    The storage backend implements an atomic commit protocol:
        1. Write to temporary file (.tmp extension)
        2. Fsync the temp file
        3. Rename temp → permanent
        4. Fsync the directory
        5. Clean up any orphaned temp files

This ensures crash safety - if a crash occurs, either:
    - The checkpoint is fully committed (rename succeeded)
    - Only temp files exist (safe to delete on startup)
"""

from __future__ import annotations

import asyncio
import os
import tempfile
import uuid
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum, auto
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any, AsyncIterator
import hashlib
import json


class StorageOperation(Enum):
    """Types of storage operations."""
    
    CHECKPOINT_WRITE = "CHECKPOINT_WRITE"
    CHECKPOINT_READ = "CHECKPOINT_READ"
    CHECKPOINT_DELETE = "CHECKPOINT_DELETE"
    MANIFEST_WRITE = "MANIFEST_WRITE"
    TEMP_FILE_CREATE = "TEMP_FILE_CREATE"


@dataclass(frozen=True)
class StorageMetrics:
    """Metrics for storage operations."""
    
    total_writes: int
    total_reads: int
    total_deletes: int
    failed_writes: int
    fsync_count: int
    rename_count: int


@dataclass(frozen=True)
class CheckpointInfo:
    """
    Metadata about a stored checkpoint.
    
    This is the manifest that describes what's stored and how to verify it.
    """
    
    checkpoint_id: str  # Hex string of UUID
    runtime_generation: int
    created_at_ns: int
    fragment_count: int
    required_fragment_count: int
    fragments: Dict[str, str]  # participant_id -> storage_key
    checksums: Dict[str, str]  # fragment key -> SHA256 hex
    total_size_bytes: int
    storage_path: str
    manifest_checksum: str
    
    @classmethod
    def empty(cls) -> "CheckpointInfo":
        return cls(
            checkpoint_id="",
            runtime_generation=0,
            created_at_ns=0,
            fragment_count=0,
            required_fragment_count=0,
            fragments={},
            checksums={},
            total_size_bytes=0,
            storage_path="",
            manifest_checksum="",
        )
    
    def is_valid(self) -> bool:
        """Check if this checkpoint info is valid."""
        return (
            self.checkpoint_id
            and self.fragment_count > 0
            and self.storage_path
            and self.manifest_checksum
        )


@dataclass(frozen=True)
class StorageResult:
    """Result of a storage operation."""
    
    success: bool
    operation: StorageOperation
    checkpoint_id: Optional[str] = None
    path: Optional[str] = None
    error_message: Optional[str] = None
    
    @classmethod
    def succeeded(cls, operation: StorageOperation, path: str) -> "StorageResult":
        return cls(success=True, operation=operation, path=path)
    
    @classmethod
    def failed(cls, operation: StorageOperation, error: str) -> "StorageResult":
        return cls(success=False, operation=operation, error_message=error)


class CheckpointStorage:
    """
    Atomic checkpoint storage backend with fsync durability guarantees.
    
    This implementation provides crash-safe checkpoint writes using the
    temp file → atomic rename pattern with fsync() calls at critical points.
    """
    
    def __init__(self, root_path: str = "var/gordon/runtime-continuity/"):
        """
        Initialize the storage backend.
        
        Args:
            root_path: Root directory for storing checkpoints and manifests
        """
        self._root_path = Path(root_path)
        self._checkpoint_dir = self._root_path / "checkpoints"
        self._manifest_dir = self._root_path / "manifests"
        self._temp_dir = self._root_path / "tmp"
        
        # Storage metrics
        self._metrics = StorageMetrics(
            total_writes=0,
            total_reads=0,
            total_deletes=0,
            failed_writes=0,
            fsync_count=0,
            rename_count=0,
        )
    
    @property
    def root_path(self) -> Path:
        """Get the root storage path."""
        return self._root_path
    
    @property
    def metrics(self) -> StorageMetrics:
        """Get storage operation metrics."""
        return self._metrics
    
    async def initialize(self) -> None:
        """
        Initialize storage directories.
        
        Creates the directory structure and cleans up any orphaned temp files.
        """
        # Create directory structure
        for path in [self._checkpoint_dir, self._manifest_dir, self._temp_dir]:
            path.mkdir(parents=True, exist_ok=True)
        
        # Cleanup any orphaned temp files from previous crashes
        await self._cleanup_orphaned_temp_files()
    
    async def _cleanup_orphaned_temp_files(self) -> None:
        """Remove any temp files left over from crashed operations."""
        if not self._temp_dir.exists():
            return
        
        for temp_file in self._temp_dir.glob("*.tmp"):
            try:
                temp_file.unlink()
            except OSError:
                pass  # Skip files that can't be removed
    
    def _generate_temp_path(self, prefix: str = "checkpoint") -> Path:
        """Generate a unique temporary file path."""
        uid = uuid.uuid4().hex[:12]
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S%f")
        return self._temp_dir / f"{prefix}_{timestamp}_{uid}.tmp"
    
    async def _fsync_file(self, file_path: Path) -> bool:
        """
        Fsync a file to ensure writes are persisted to disk.
        
        Args:
            file_path: Path to the file to fsync
            
        Returns:
            True if successful, False otherwise
        """
        try:
            with open(file_path, "a") as f:
                f.flush()
                os.fsync(f.fileno())
            self._metrics = StorageMetrics(
                **self._metrics.__dict__,
                fsync_count=self._metrics.fsync_count + 1,
            )
            return True
        except OSError:
            return False
    
    async def _fsync_directory(self, dir_path: Path) -> bool:
        """
        Fsync a directory to ensure file creation is persisted.
        
        Args:
            dir_path: Path to the directory to fsync
            
        Returns:
            True if successful, False otherwise
        """
        try:
            dir_fd = os.open(str(dir_path), os.O_RDONLY | os.O_DIRECTORY)
            try:
                os.fsync(dir_fd)
            finally:
                os.close(dir_fd)
            return True
        except OSError:
            return False
    
    async def write_checkpoint(
        self,
        checkpoint_id: str,
        fragments: Dict[str, Any],
        metadata: Dict[str, Any],
    ) -> StorageResult:
        """
        Write a checkpoint with atomic commit protocol.
        
        The atomic protocol:
            1. Create temp file
            2. Write serialized data to temp file
            3. Fsync temp file
            4. Rename temp → permanent
            5. Fsync directory
            
        Args:
            checkpoint_id: Unique ID for this checkpoint
            fragments: Fragment data keyed by participant ID
            metadata: Checkpoint metadata (runtime generation, timestamps, etc.)
            
        Returns:
            StorageResult indicating success/failure
        """
        # Generate paths
        checkpoint_path = self._checkpoint_dir / f"{checkpoint_id}.json"
        temp_path = self._generate_temp_path("checkpoint")
        
        # Build manifest
        checksums = {}
        total_size = 0
        for participant_id, fragment in fragments.items():
            fragment_data = json.dumps(fragment, default=str).encode("utf-8")
            checksum = hashlib.sha256(fragment_data).hexdigest()
            checksums[participant_id] = checksum
            total_size += len(fragment_data)
        
        manifest = {
            "checkpoint_id": checkpoint_id,
            "runtime_generation": metadata.get("runtime_generation", 0),
            "created_at_ns": metadata.get("created_at_ns", 0),
            "fragment_count": len(fragments),
            "required_fragment_count": metadata.get("required_fragment_count", 0),
            "fragments": list(fragments.keys()),
            "checksums": checksums,
            "total_size_bytes": total_size,
        }
        
        manifest_checksum = hashlib.sha256(
            json.dumps(manifest, sort_keys=True).encode("utf-8")
        ).hexdigest()
        
        # Phase 1: Write to temp file
        try:
            with open(temp_path, "w") as f:
                json.dump({"manifest": manifest, "fragments": fragments}, f)
            
            # Phase 2: Fsync the temp file
            if not await self._fsync_file(temp_path):
                return StorageResult.failed(
                    StorageOperation.CHECKPOINT_WRITE,
                    "Failed to fsync temp file",
                )
            
            # Phase 3: Atomic rename (temp → permanent)
            checkpoint_path.parent.mkdir(parents=True, exist_ok=True)
            os.rename(str(temp_path), str(checkpoint_path))
            self._metrics = StorageMetrics(
                **self._metrics.__dict__,
                rename_count=self._metrics.rename_count + 1,
            )
            
            # Phase 4: Fsync the directory
            await self._fsync_directory(self._checkpoint_dir)
            
            self._metrics = StorageMetrics(
                **self._metrics.__dict__,
                total_writes=self._metrics.total_writes + 1,
            )
            
            return StorageResult.succeeded(
                StorageOperation.CHECKPOINT_WRITE,
                str(checkpoint_path),
            )
        
        except Exception as e:
            # Cleanup temp file on error
            try:
                if temp_path.exists():
                    temp_path.unlink()
            except OSError:
                pass
            
            self._metrics = StorageMetrics(
                **self._metrics.__dict__,
                failed_writes=self._metrics.failed_writes + 1,
            )
            
            return StorageResult.failed(
                StorageOperation.CHECKPOINT_WRITE,
                str(e),
            )
    
    async def read_checkpoint(self, checkpoint_id: str) -> Optional[CheckpointInfo]:
        """
        Read and validate a stored checkpoint.
        
        Args:
            checkpoint_id: ID of the checkpoint to read
            
        Returns:
            CheckpointInfo if found and valid, None otherwise
        """
        path = self._checkpoint_dir / f"{checkpoint_id}.json"
        
        try:
            with open(path, "r") as f:
                data = json.load(f)
            
            manifest = data.get("manifest", {})
            fragments = data.get("fragments", {})
            
            # Validate checksums
            for participant_id, stored_checksum in manifest.get("checksums", {}).items():
                fragment_str = json.dumps(fragments.get(participant_id, {}), default=str)
                computed = hashlib.sha256(fragment_str.encode("utf-8")).hexdigest()
                if computed != stored_checksum:
                    return None  # Corrupted
            
            self._metrics = StorageMetrics(
                **self._metrics.__dict__,
                total_reads=self._metrics.total_reads + 1,
            )
            
            return CheckpointInfo(
                checkpoint_id=manifest.get("checkpoint_id", ""),
                runtime_generation=manifest.get("runtime_generation", 0),
                created_at_ns=manifest.get("created_at_ns", 0),
                fragment_count=manifest.get("fragment_count", 0),
                required_fragment_count=manifest.get("required_fragment_count", 0),
                fragments={k: str(v) for k, v in fragments.items()},
                checksums=manifest.get("checksums", {}),
                total_size_bytes=manifest.get("total_size_bytes", 0),
                storage_path=str(path),
                manifest_checksum=manifest.get("manifest_checksum", ""),
            )
        
        except (OSError, json.JSONDecodeError, KeyError):
            return None
    
    async def list_checkpoints(self) -> List[str]:
        """
        List all stored checkpoint IDs.
        
        Returns:
            List of checkpoint ID strings
        """
        checkpoints = []
        if self._checkpoint_dir.exists():
            for path in self._checkpoint_dir.glob("*.json"):
                # Extract checkpoint_id from filename
                checkpoint_id = path.stem  # Remove .json extension
                checkpoints.append(checkpoint_id)
        
        return sorted(checkpoints)
    
    async def delete_checkpoint(self, checkpoint_id: str) -> StorageResult:
        """
        Delete a checkpoint.
        
        Args:
            checkpoint_id: ID of the checkpoint to delete
            
        Returns:
            StorageResult indicating success/failure
        """
        path = self._checkpoint_dir / f"{checkpoint_id}.json"
        
        try:
            if path.exists():
                path.unlink()
                await self._fsync_directory(self._checkpoint_dir)
                
                self._metrics = StorageMetrics(
                    **self._metrics.__dict__,
                    total_deletes=self._metrics.total_deletes + 1,
                )
                
                return StorageResult.succeeded(
                    StorageOperation.CHECKPOINT_DELETE,
                    str(path),
                )
            else:
                return StorageResult.failed(
                    StorageOperation.CHECKPOINT_DELETE,
                    "Checkpoint not found",
                )
        
        except OSError as e:
            return StorageResult.failed(
                StorageOperation.CHECKPOINT_DELETE,
                str(e),
            )
    
    async def write_manifest(self, checkpoint_id: str, manifest: Dict[str, Any]) -> StorageResult:
        """
        Write a standalone manifest file.
        
        This allows reading metadata without loading the full checkpoint.
        
        Args:
            checkpoint_id: ID of the checkpoint
            manifest: Manifest data to write
            
        Returns:
            StorageResult indicating success/failure
        """
        path = self._manifest_dir / f"{checkpoint_id}.json"
        temp_path = self._generate_temp_path("manifest")
        
        try:
            with open(temp_path, "w") as f:
                json.dump(manifest, f)
            
            if not await self._fsync_file(temp_path):
                return StorageResult.failed(
                    StorageOperation.MANIFEST_WRITE,
                    "Failed to fsync temp file",
                )
            
            path.parent.mkdir(parents=True, exist_ok=True)
            os.rename(str(temp_path), str(path))
            self._metrics = StorageMetrics(
                **self._metrics.__dict__,
                rename_count=self._metrics.rename_count + 1,
            )
            
            await self._fsync_directory(self._manifest_dir)
            
            self._metrics = StorageMetrics(
                **self._metrics.__dict__,
                total_writes=self._metrics.total_writes + 1,
            )
            
            return StorageResult.succeeded(
                StorageOperation.MANIFEST_WRITE,
                str(path),
            )
        
        except Exception as e:
            try:
                if temp_path.exists():
                    temp_path.unlink()
            except OSError:
                pass
            
            self._metrics = StorageMetrics(
                **self._metrics.__dict__,
                failed_writes=self._metrics.failed_writes + 1,
            )
            
            return StorageResult.failed(StorageOperation.MANIFEST_WRITE, str(e))
    
    def get_diagnostics(self) -> Dict[str, Any]:
        """Get diagnostic information about the storage backend."""
        checkpoint_count = len(list(self._checkpoint_dir.glob("*.json")))
        
        return {
            "root_path": str(self._root_path),
            "checkpoint_directory": str(self._checkpoint_dir),
            "manifest_directory": str(self._manifest_dir),
            "temp_directory": str(self._temp_dir),
            "total_checkpoints": checkpoint_count,
            "metrics": self._metrics.__dict__,
        }