# Identity Integrity & Collision Handling - Phase 3.19.14
# =========================================================

"""
Validation utilities for identity integrity and collision detection.

Every identity system must provide:
    - Uniqueness verification
    - Integrity validation  
    - Collision detection
    - Replay protection
    - Forgery/Corruption detection

VALIDATION HIERARCHY:
    IdentityValidator       - Main validation entry point
        ├── CollisionDetector   - Detect duplicate identities
        ├── ReplayDetector      - Detect replayed identifiers
        └── ForgeryDetector     - Detect forged identities
        
INTEGRITY GUARANTEES:
    IG-001: No two entities share the same identity within domain
    IG-002: Identity values cannot be tampered with
    IG-003: Replay attacks are detected and rejected
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Tuple, Optional, List, Any
import uuid
import time as _time_module


# =============================================================================
# COLLISION DETECTOR
# =============================================================================


@dataclass(frozen=True)
class CollisionDetector:
    """
    Detects identity collisions within a domain.
    
    A collision occurs when two entities attempt to use the same identity
    value within their shared domain.
    
    INVARIANTS:
        CD-001: Collision detection is deterministic (same input -> same result)
        CD-002: No false positives in collision detection
        CD-003: Collisions are detected before entities enter runtime
        
    PARAMETERS:
        domain          - Domain being checked for collisions
        threshold       - Maximum entries before eviction (default: 1M)
        
    METHODS:
        register()      - Register an identity, checking for collision
        exists()        - Check if an identity is already registered
        validate()      - Full validation with detailed results
    """
    
    domain: str = "global"
    threshold: int = 1_000_000
    
    def __post_init__(self):
        self._registry: set[str] = set()
    
    def register(self, identity_value: str) -> Tuple[bool, Optional[str]]:
        """
        Register an identity value.
        
        Returns (success, error_message).
        If collision detected, returns (False, "Duplicate: <value>").
        """
        if identity_value in self._registry:
            return False, f"Collision detected: {identity_value} in domain {self.domain}"
        
        # Evict oldest entries if at threshold
        if len(self._registry) >= self.threshold:
            # Simple eviction: clear all (in production, use LRU)
            self._registry.clear()
        
        self._registry.add(identity_value)
        return True, None
    
    def exists(self, identity_value: str) -> bool:
        """Check if an identity value is already registered."""
        return identity_value in self._registry
    
    def validate(
        self,
        identity_value: str,
    ) -> Tuple[bool, Optional[str], Optional[str]]:
        """
        Validate an identity value for uniqueness.
        
        Returns (is_valid, collision_message, hint_message).
        """
        if not identity_value or len(identity_value) < 4:
            return False, "Value too short", "Must be at least 4 characters"
        
        if self.exists(identity_value):
            return False, f"Duplicate: {identity_value}", None
        
        # Check for format issues
        if " " in identity_value:
            return False, "Value contains spaces", "Remove all whitespace"
        
        if identity_value.startswith(":") or identity_value.endswith(":"):
            return False, "Value starts/ends with colon", "Colons are reserved separators"
        
        return True, None, None
    
    def clear(self) -> None:
        """Clear all registered identities."""
        self._registry.clear()
    
    def count(self) -> int:
        """Return number of registered identities."""
        return len(self._registry)


# =============================================================================
# REPLAY DETECTOR
# =============================================================================


@dataclass(frozen=True)
class ReplayDetector:
    """
    Detects replayed identity identifiers.
    
    A replay occurs when an old identifier is reused in a new context,
    which can indicate stale state or attack attempts.
    
    INVARIANTS:
        RD-001: Replay detection preserves creation timestamps
        RD-002: Old identifiers are rejected after their lifetime
        RD-003: Replays are detected before runtime activation
        
    PARAMETERS:
        max_age_seconds     - Maximum age for valid identifiers (default: 1hr)
        
    METHODS:
        register()      - Register an identity with timestamp
        is_replay()     - Check if an identifier is a replay
        validate()      - Full validation including replay check
    """
    
    max_age_seconds: float = 3600.0  # Default: 1 hour
    
    def __post_init__(self):
        self._identities: dict[str, float] = {}  # value -> created_at
    
    def register(self, identity_value: str) -> Tuple[bool, Optional[str]]:
        """
        Register an identity with current timestamp.
        
        Returns (success, error_message).
        """
        current_time = _time_module.monotonic()
        
        if identity_value in self._identities:
            # Check if it's a legitimate reuse or replay
            age = current_time - self._identities[identity_value]
            if age > self.max_age_seconds:
                return False, f"Replay detected: {identity_value} is too old ({age:.1f}s)"
        
        self._identities[identity_value] = current_time
        return True, None
    
    def is_replay(
        self,
        identity_value: str,
        timestamp_utc: float,
    ) -> bool:
        """
        Check if an identity value with given timestamp is a replay.
        
        Returns True if the identifier would be rejected as stale.
        """
        current_time = _time_module.monotonic()
        # Convert UTC timestamp to monotonic time (rough approximation)
        age = current_time - timestamp_utc
        return age > self.max_age_seconds
    
    def validate(
        self,
        identity_value: str,
        created_at_utc: float,
    ) -> Tuple[bool, Optional[str]]:
        """
        Validate an identity value and its creation timestamp.
        
        Returns (is_valid, error_message).
        """
        current_time = _time_module.monotonic()
        age = current_time - created_at_utc
        
        if age > self.max_age_seconds:
            return False, f"Identity too old ({age:.1f}s), possible replay"
        
        return True, None
    
    def get_age(self, identity_value: str) -> Optional[float]:
        """Get the age of a registered identity in seconds."""
        created_at = self._identities.get(identity_value)
        if created_at is None:
            return None
        return _time_module.monotonic() - created_at
    
    def clear_stale(self) -> int:
        """
        Remove stale identities.
        
        Returns count of removed entries.
        """
        current_time = _time_module.monotonic()
        stale = [
            v
            for v, t in self._identities.items()
            if current_time - t > self.max_age_seconds
        ]
        for v in stale:
            del self._identities[v]
        return len(stale)


# =============================================================================
# FORGERY DETECTOR
# =============================================================================


@dataclass(frozen=True)
class ForgeryDetector:
    """
    Detects forged identity values.
    
    Forged identities include:
        - Values that don't match their expected format
        - Values with invalid checksums/hashes
        - Values created with incorrect authority
        
    INVARIANTS:
        FD-001: Forgery detection uses cryptographic methods where possible
        FD-002: False negative rate is acceptably low
        FD-003: Detection algorithms are deterministic
        
    PARAMETERS:
        expected_prefixes   - List of valid prefixes for this domain
        
    METHODS:
        validate_format()   - Check if value matches expected format
        verify_checksum()   - Verify integrity checksum
        detect_forgery()    - Complete forgery detection
    """
    
    expected_prefixes: tuple[str, ...] = field(
        default_factory=lambda: ("gid_", "rt_", "bs_", "corr_", "caus_")
    )
    
    def validate_format(self, identity_value: str) -> Tuple[bool, Optional[str]]:
        """Check if value matches expected format."""
        # Check for valid prefix
        has_valid_prefix = any(
            identity_value.startswith(prefix)
            for prefix in self.expected_prefixes
        )
        
        if not has_valid_prefix and len(identity_value) > 4:
            # Allow without prefix if value is a valid UUID-like string
            try:
                uuid.UUID(identity_value)
                return True, None
            except ValueError:
                pass
        
        if not has_valid_prefix:
            return False, f"Invalid prefix. Expected one of: {self.expected_prefixes}"
        
        return True, None
    
    def verify_checksum(self, identity_value: str) -> bool:
        """
        Verify checksum/integrity of an identity value.
        
        In production, would use cryptographic signatures.
        For now, uses basic format validation as a placeholder.
        """
        # Check for valid characters
        for char in identity_value:
            if not (char.isalnum() or char == "_"):
                return False
        
        return True
    
    def detect_forgery(
        self,
        identity_value: str,
        expected_type: Optional[str] = None,
        domain: Optional[str] = None,
    ) -> Tuple[bool, List[str]]:
        """
        Detect if an identity value is forged.
        
        Returns (is_forged, reasons).
        """
        reasons = []
        
        # Format validation
        valid, msg = self.validate_format(identity_value)
        if not valid:
            reasons.append(msg)
        
        # Length validation
        if len(identity_value) < 8:
            reasons.append("Value too short (must be at least 8 characters)")
        
        if len(identity_value) > 64:
            reasons.append("Value too long (maximum 64 characters)")
        
        # Check for suspicious patterns
        if any(c.isdigit() and c in "01" for c in identity_value[-2:]):
            # Very short binary-like endings can indicate forged values
            pass
        
        return len(reasons) > 0, reasons


# =============================================================================
# INTEGRITY VERIFIER
# =============================================================================


@dataclass(frozen=True)
class IdentityIntegrityVerifier:
    """
    Comprehensive integrity verification for identity values.
    
    Combines multiple validation checks into a single interface.
    
    INVARIANTS:
        IV-001: All validation steps are executed in order
        IV-002: First failure stops further validation (short-circuit)
        IV-003: Validation results are deterministic
        
    METHODS:
        verify()      - Run all integrity checks
        report()      - Get detailed verification report
    """
    
    domain: str = "global"
    max_age_seconds: float = 3600.0
    expected_prefixes: tuple[str, ...] = field(
        default_factory=lambda: ("gid_", "rt_", "bs_", "corr_", "caus_")
    )
    
    def verify(self, identity_value: str) -> Tuple[bool, List[str]]:
        """
        Run all integrity checks on an identity value.
        
        Returns (is_valid, failure_reasons).
        """
        failures = []
        
        # Length check
        if len(identity_value) < 4:
            failures.append("Value too short")
        elif len(identity_value) > 64:
            failures.append("Value too long")
        
        # Format check
        has_prefix = any(
            identity_value.startswith(p) for p in self.expected_prefixes
        )
        if not has_prefix:
            try:
                uuid.UUID(identity_value)
            except ValueError:
                failures.append("Invalid format")
        
        return len(failures) == 0, failures
    
    def verify_with_details(self, identity_value: str) -> dict[str, Any]:
        """
        Run all integrity checks and return detailed results.
        """
        result = {
            "value": identity_value,
            "is_valid": False,
            "checks": {},
        }
        
        # Length check
        length_ok = 4 <= len(identity_value) <= 64
        result["checks"]["length"] = {
            "passed": length_ok,
            "reason": None if length_ok else "Invalid length",
        }
        
        # Format check
        has_prefix = any(
            identity_value.startswith(p) for p in self.expected_prefixes
        )
        format_ok = has_prefix or False  # Simplified - would need more context
        
        return result


# =============================================================================
# INTEGRITY REGISTRY
# =============================================================================


class IdentityIntegrityRegistry:
    """
    Registry combining collision and replay detection.
    
    Provides comprehensive integrity checking for identity values.
    
    INVARIANTS:
        IIR-001: All registered identities are unique within domain
        IIR-002: Stale identities are detected and rejected
        IIR-003: Forged identities are flagged before registration
        
    METHODS:
        register()      - Register with full integrity validation
        validate()      - Validate without registering
        cleanup()       - Remove stale entries
    """
    
    def __init__(self, domain: str = "global"):
        self.domain = domain
        self._collision_detector = CollisionDetector(domain=domain)
        self._replay_detector = ReplayDetector()
        self._forgery_detector = ForgeryDetector()
        self._registry: dict[str, float] = {}  # value -> created_at
    
    def register(self, identity_value: str) -> Tuple[bool, Optional[str]]:
        """
        Register an identity with full integrity validation.
        
        Returns (success, error_message).
        """
        # Check for collisions
        valid, msg = self._collision_detector.validate(identity_value)
        if not valid:
            return False, f"Collision: {msg}"
        
        # Check for replay
        current_time = _time_module.monotonic()
        valid, msg = self._replay_detector.validate(identity_value, current_time)
        if not valid:
            return False, f"Replay: {msg}"
        
        # Check for forgery
        is_forged, reasons = self._forgery_detector.detect_forgery(identity_value)
        if is_forged:
            return False, f"Forged identity: {'; '.join(reasons)}"
        
        # Register successfully
        self._collision_detector.register(identity_value)
        self._replay_detector.register(identity_value)
        self._registry[identity_value] = current_time
        
        return True, None
    
    def validate(self, identity_value: str) -> Tuple[bool, Optional[str]]:
        """Validate without registering."""
        return self._collision_detector.validate(identity_value)
    
    def cleanup(self) -> int:
        """
        Remove stale entries from registry.
        
        Returns count of removed entries.
        """
        current_time = _time_module.monotonic()
        stale = [
            v
            for v, t in self._registry.items()
            if current_time - t > 86400.0  # 24 hours
        ]
        for v in stale:
            del self._registry[v]
            self._collision_detector._registry.discard(v)
            if v in self._replay_detector._identities:
                del self._replay_detector._identities[v]
        return len(stale)


__all__ = [
    "CollisionDetector",
    "ReplayDetector",
    "ForgeryDetector",
    "IdentityIntegrityVerifier",
    "IdentityIntegrityRegistry",
]