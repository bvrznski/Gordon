# Core Integrity Interface
# ========================

"""
Core integrity interface - defines contracts for data and state verification.

Integrity checks ensure that data has not been corrupted or tampered with,
providing confidence in the system's correctness.

ARCHITECTURAL PRINCIPLES:
- Integrity verification is separate from health checks
- Multiple checksum/hash algorithms supported
- Results are cached to avoid redundant computation
"""

from typing import Protocol, Optional, List, Dict, Any
from dataclasses import dataclass
from enum import Enum


class IntegrityAlgorithm(Enum):
    """Supported integrity verification algorithms."""
    MD5 = "md5"
    SHA1 = "sha1"
    SHA256 = "sha256"
    SHA384 = "sha384"
    SHA512 = "sha512"
    BLAKE2B = "blake2b"
    CRC32 = "crc32"


@dataclass(frozen=True)
class IntegrityResult:
    """
    Result of an integrity verification.
    
    Args:
        resource_id: The ID of the verified resource
        expected_hash: The hash we expected to find
        actual_hash: The hash we computed
        algorithm: Which algorithm was used
        is_valid: Whether the integrity check passed
        timestamp_utc: When the check was performed
        details: Additional verification information
    """
    resource_id: str
    expected_hash: str
    actual_hash: str
    algorithm: IntegrityAlgorithm
    is_valid: bool = True
    timestamp_utc: float = 0.0
    details: Dict[str, Any] = None  # type: ignore


@dataclass(frozen=True)
class IntegrityRecord:
    """
    Record of an integrity verification for persistence.
    
    Args:
        record_id: Unique ID for this record
        resource_id: The verified resource
        hash_value: The hash at the time of verification
        algorithm: Which algorithm was used
        timestamp_utc: When verification occurred
        verified_by: Component that performed the check
    """
    record_id: str
    resource_id: str
    hash_value: str
    algorithm: IntegrityAlgorithm
    timestamp_utc: float = 0.0
    verified_by: str = "unknown"


class IIntegrityVerifier(Protocol):
    """
    Interface for integrity verifiers.
    
    Verifiers compute and verify checksums/hashes of data to ensure
    it hasn't been corrupted or tampered with.
    """
    
    @property
    def verifier_id(self) -> str:
        """Get the unique ID of this integrity verifier."""
        ...
    
    async def compute_hash(
        self,
        data: Any,
        algorithm: IntegrityAlgorithm = IntegrityAlgorithm.SHA256,
    ) -> str:
        """
        Compute a hash value for some data.
        
        Args:
            data: The data to hash (bytes or string)
            algorithm: Which hashing algorithm to use
            
        Returns:
            Hexadecimal hash string
        """
        ...
    
    async def verify_integrity(
        self,
        resource_id: str,
        expected_hash: str,
        actual_data: Any,
        algorithm: IntegrityAlgorithm = IntegrityAlgorithm.SHA256,
    ) -> IntegrityResult:
        """
        Verify that data has the expected hash.
        
        Args:
            resource_id: ID of the resource being verified
            expected_hash: The hash we expect to find
            actual_data: The data to verify
            algorithm: Which hashing algorithm to use
            
        Returns:
            Result indicating whether verification passed
        """
        ...
    
    async def get_integrity_report(
        self,
        resource_id: str,
    ) -> Optional[IntegrityResult]:
        """Get the most recent integrity report for a resource."""
        ...


class IIntegrityStore(Protocol):
    """
    Interface for storing and retrieving integrity records.
    
    The store maintains a history of integrity checks for audit trails
    and long-term verification capabilities.
    """
    
    async def record_integrity(
        self,
        record: IntegrityRecord,
    ) -> None:
        """Store an integrity record."""
        ...
    
    async def get_integrity_history(
        self,
        resource_id: str,
        limit: int = 100,
    ) -> List[IntegrityRecord]:
        """
        Get integrity history for a resource.
        
        Args:
            resource_id: The resource to look up
            limit: Maximum number of records to return
            
        Returns:
            List of integrity records, most recent first
        """
        ...
    
    async def find_records_by_hash(
        self,
        hash_value: str,
        algorithm: IntegrityAlgorithm,
    ) -> List[IntegrityRecord]:
        """Find all records with a specific hash value."""
        ...


class IIntegrityObserver(Protocol):
    """
    Interface for components that observe integrity changes.
    
    Observers can react when integrity verification fails,
    triggering security responses or recovery actions.
    """
    
    async def on_integrity_verified(
        self,
        result: IntegrityResult,
    ) -> None:
        """Called when a resource passes integrity verification."""
        ...
    
    async def on_integrity_failed(
        self,
        result: IntegrityResult,
    ) -> None:
        """
        Called when an integrity check fails.
        
        This typically indicates data corruption or tampering and should
        trigger immediate investigation or remediation.
        """
        ...


class IntegrityError(Exception):
    """Raised when integrity verification fails."""
    pass


class HashMismatchError(IntegrityError):
    """
    Raised when computed hash doesn't match expected hash.
    
    Args:
        resource_id: ID of the affected resource
        expected_hash: The hash we expected
        actual_hash: The hash we actually found
        algorithm: Which algorithm was used
    """
    
    def __init__(
        self,
        resource_id: str,
        expected_hash: str,
        actual_hash: str,
        algorithm: IntegrityAlgorithm,
    ):
        super().__init__(
            f"Integrity check failed for {resource_id}: "
            f"expected {expected_hash}, got {actual_hash} ({algorithm.value})"
        )
        self.resource_id = resource_id
        self.expected_hash = expected_hash
        self.actual_hash = actual_hash
        self.algorithm = algorithm


__all__ = [
    "IntegrityAlgorithm",
    "IntegrityResult",
    "IntegrityRecord",
    "IIntegrityVerifier",
    "IIntegrityStore",
    "IIntegrityObserver",
    "IntegrityError",
    "HashMismatchError",
]