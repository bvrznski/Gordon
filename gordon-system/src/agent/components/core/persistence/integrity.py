# Integrity Protection
# ====================

"""
Integrity protection for persisted artifacts.

This module provides:
- ContentDigest: Immutable content identifier
- ChecksumAlgorithm: Supported hashing algorithms
- IntegrityMetadata: Attached to all persisted artifacts
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any
from enum import Enum, auto
import uuid
import time
import hashlib


# =============================================================================
# Checksum Algorithms
# =============================================================================

class ChecksumAlgorithm(Enum):
    """Supported checksum algorithms."""
    
    SHA256 = "sha256"
    SHA3_256 = "sha3_256"
    BLAKE2B = "blake2b"
    MD5 = "md5"  # Only for non-security contexts


# =============================================================================
# Content Digest
# =============================================================================

@dataclass(frozen=True)
class ContentDigest:
    """
    Immutable content identifier.
    
    A content digest is a cryptographic hash of content that serves as
    its identity. Two identical contents always produce the same digest.
    """
    
    # Hash value (hex string)
    hash_value: str
    
    # Algorithm used to compute the hash
    algorithm: ChecksumAlgorithm
    
    # Original content size before hashing
    original_size_bytes: int
    
    @classmethod
    def compute(
        cls,
        data: bytes,
        algorithm: ChecksumAlgorithm = ChecksumAlgorithm.SHA256,
    ) -> "ContentDigest":
        """Compute a digest for the given data."""
        if algorithm == ChecksumAlgorithm.SHA256:
            hash_value = hashlib.sha256(data).hexdigest()
        elif algorithm == ChecksumAlgorithm.SHA3_256:
            hash_value = hashlib.sha3_256(data).hexdigest()
        elif algorithm == ChecksumAlgorithm.BLAKE2B:
            hash_value = hashlib.blake2b(data).hexdigest()
        elif algorithm == ChecksumAlgorithm.MD5:
            hash_value = hashlib.md5(data).hexdigest()
        else:
            raise ValueError(f"Unsupported algorithm: {algorithm}")
        
        return cls(
            hash_value=hash_value,
            algorithm=algorithm,
            original_size_bytes=len(data),
        )
    
    def verify(self, data: bytes) -> bool:
        """Verify that the given data matches this digest."""
        computed = ContentDigest.compute(data, self.algorithm)
        return computed.hash_value == self.hash_value
    
    def __str__(self) -> str:
        return f"{self.algorithm.value}:{self.hash_value[:16]}"


# =============================================================================
# Integrity Metadata
# =============================================================================

@dataclass(frozen=True)
class IntegrityMetadata:
    """
    Integrity metadata attached to persisted artifacts.
    
    Every artifact in persistent storage includes this metadata to enable
    integrity verification on read and corruption detection.
    """
    
    # Content digest (SHA256 by default)
    content_digest: ContentDigest
    
    # Storage location info
    storage_key: str
    object_id: Optional[str] = None  # If different from content address
    
    # Timestamps
    created_at: float = field(default_factory=time.monotonic)
    
    # Checksum verification on read
    verify_on_read: bool = True
    
    # Encryption info (if applicable)
    encrypted: bool = False
    encryption_key_id: Optional[str] = None
    
    @classmethod
    def create(
        cls,
        data: bytes,
        storage_key: str,
        algorithm: ChecksumAlgorithm = ChecksumAlgorithm.SHA256,
    ) -> "IntegrityMetadata":
        """Create integrity metadata for data being persisted."""
        digest = ContentDigest.compute(data, algorithm)
        
        return cls(
            content_digest=digest,
            storage_key=storage_key,
            object_id=None,
        )
    
    def verify(self, data: bytes) -> bool:
        """Verify the data against stored digest."""
        return self.content_digest.verify(data)


# =============================================================================
# Artifact Integrity Checker
# =============================================================================

class ArtifactIntegrityChecker:
    """
    Verifies integrity of persisted artifacts.
    
    Usage:
        checker = ArtifactIntegrityChecker()
        
        # Read artifact with verification
        metadata, data = await checker.read_with_verification(storage_key)
        
        if not metadata.verify(data):
            # Handle corruption
            pass
    """
    
    def __init__(self) -> None:
        self._verification_count = 0
        self._corruption_count = 0
        self._drift_reconciliation_enabled = True
    
    @property
    def drift_reconciliation_enabled(self) -> bool:
        """Check if automatic drift reconciliation is enabled."""
        return self._drift_reconciliation_enabled
    
    def enable_drift_reconciliation(self, enabled: bool = True) -> None:
        """Enable or disable automatic drift reconciliation."""
        self._drift_reconciliation_enabled = enabled
    
    async def read_with_verification(
        self,
        storage_key: str,
        expected_digest: Optional[ContentDigest] = None,
    ) -> tuple[IntegrityMetadata, bytes]:
        """
        Read an artifact and verify its integrity.
        
        Args:
            storage_key: Where to find the artifact
            expected_digest: If provided, verify against this
            
        Returns:
            Tuple of (metadata, data)
            
        Raises:
            IntegrityError: If verification fails
        """
        # In production, this would read from storage backend
        # For now, return placeholder
        
        metadata = IntegrityMetadata(
            content_digest=ContentDigest.compute(b"placeholder_data"),
            storage_key=storage_key,
        )
        
        data = b"placeholder_data"
        
        self._verification_count += 1
        
        if expected_digest and not metadata.verify(data):
            self._corruption_count += 1
            raise IntegrityError(
                f"Integrity check failed for {storage_key}"
            )
        
        return metadata, data
    
    async def read_with_drift_detection(
        self,
        storage_key: str,
        expected_metadata: Optional[IntegrityMetadata] = None,
    ) -> tuple[IntegrityMetadata, bytes, bool]:
        """
        Read an artifact and detect any drift from expected state.
        
        Args:
            storage_key: Where to find the artifact
            expected_metadata: If provided, compare against this
            
        Returns:
            Tuple of (metadata, data, has_drift)
            
        Raises:
            IntegrityError: If corruption detected
        """
        metadata, data = await self.read_with_verification(storage_key)
        
        # Check for drift if expected metadata provided
        has_drift = False
        
        if expected_metadata:
            # Compare content digests (primary indicator of state change)
            if metadata.content_digest.hash_value != expected_metadata.content_digest.hash_value:
                has_drift = True
                if self._drift_reconciliation_enabled:
                    # In production, would attempt automatic reconciliation
                    # For now, log and return drift flag
                    pass
        
        return metadata, data, has_drift
    
    def get_diagnostics(self) -> Dict[str, Any]:
        """Get checker diagnostics."""
        return {
            "verification_count": self._verification_count,
            "corruption_count": self._corruption_count,
            "drift_reconciliation_enabled": self._drift_reconciliation_enabled,
        }


# =============================================================================
# Integrity Errors
# =============================================================================

class IntegrityError(Exception):
    """Raised when integrity verification fails."""
    
    def __init__(self, message: str, artifact_id: Optional[str] = None):
        super().__init__(message)
        self.artifact_id = artifact_id


class CorruptedArtifactError(IntegrityError):
    """Raised when an artifact is detected as corrupted."""
    
    def __init__(self, message: str, artifact_id: Optional[str] = None, expected_digest: Optional[str] = None):
        super().__init__(message, artifact_id)
        self.expected_digest = expected_digest
        self.actual_digest = None  # Would be set during verification


class DriftReconciler:
    """
    Handles persistence drift reconciliation.
    
    Usage:
        reconciler = DriftReconciler()
        
        # Check for drift and attempt automatic reconciliation
        has_drift, result = await reconciler.reconcile_if_drift(storage_key, expected_state)
    """
    
    def __init__(self) -> None:
        self._reconciliation_attempts = 0
        self._successful_reconciliations = 0
    
    async def reconcile_if_drift(
        self,
        storage_key: str,
        expected_state: Dict[str, Any],
    ) -> tuple[bool, bool]:
        """
        Check for drift and attempt automatic reconciliation.
        
        Args:
            storage_key: Storage location of artifact
            expected_state: Expected state
            
        Returns:
            Tuple of (has_drift, reconciliation_success)
        """
        self._reconciliation_attempts += 1
        
        # In production, would:
        # 1. Read current state from storage
        # 2. Compare with expected state
        # 3. Attempt automatic reconciliation if drift detected
        # 4. Update storage if reconciliation succeeds
        
        # For now, return placeholder (drift exists but reconciliation not automated)
        has_drift = False  # Placeholder - would be determined by actual comparison
        
        if has_drift and self._reconciliation_attempts > 0:
            self._successful_reconciliations += 1
            return True, True
        
        return has_drift, False
    
    def get_diagnostics(self) -> Dict[str, Any]:
        """Get reconciler diagnostics."""
        return {
            "reconciliation_attempts": self._reconciliation_attempts,
            "successful_reconciliations": self._successful_reconciliations,
        }


__all__ = [
    # Algorithm
    "ChecksumAlgorithm",
    
    # Digest
    "ContentDigest",
    
    # Metadata
    "IntegrityMetadata",
    
    # Checker
    "ArtifactIntegrityChecker",
    
    # Errors
    "IntegrityError",
    "CorruptedArtifactError",
    
    # Reconciliation
    "DriftReconciler",
]
