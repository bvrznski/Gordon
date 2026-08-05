# Continuity Configuration
# ========================

"""
Configuration for continuity infrastructure.
"""

from __future__ import annotations

import os
from dataclasses import dataclass, field
from typing import Optional


# =============================================================================
# DEFAULTS
# =============================================================================

DEFAULT_CHECKPOINT_INTERVAL_SECONDS: float = 300.0  # 5 minutes
MAXIMUM_CHECKPOINT_DURATION_SECONDS: float = 60.0
LEDGER_FLUSH_INTERVAL_SECONDS: float = 60.0
MAXIMUM_RETAINED_CHECKPOINTS: int = 10
MAXIMUM_LEDGER_SEGMENT_SIZE_BYTES: int = 10 * 1024 * 1024  # 10 MB
MAXIMUM_LEDGER_RETENTION_DAYS: int = 30
CHECKPOINT_ROOT_DEFAULT: str = "var/gordon/runtime-continuity/"
LEDGER_ROOT_DEFAULT: str = "var/gordon/runtime-continuity/ledger/"
RECOVERY_REPORT_ROOT_DEFAULT: str = "var/gordon/runtime-continuity/recovery/"


# =============================================================================
# CHECKSUM ALGORITHMS
# =============================================================================

CHECKSUM_ALGORITHM_SHA256: str = "sha256"
CHECKSUM_ALGORITHM_CRC32: str = "crc32"


# =============================================================================
# COMPRESSION MODES
# =============================================================================

COMPRESSION_NONE: str = "none"
COMPRESSION_ZLIB: str = "zlib"
COMPRESSION_LZ4: str = "lz4"


# =============================================================================
# CONFIGURATION DATACLASS
# =============================================================================

@dataclass(frozen=True)
class ContinuityConfig:
    """
    Configuration for the continuity infrastructure.
    
    All configuration values have sensible defaults and can be overridden
    via environment variables.
    """
    
    # Checkpoint configuration
    checkpoint_interval_seconds: float = DEFAULT_CHECKPOINT_INTERVAL_SECONDS
    maximum_checkpoint_duration_seconds: float = MAXIMUM_CHECKPOINT_DURATION_SECONDS
    
    # Ledger configuration
    ledger_flush_interval_seconds: float = LEDGER_FLUSH_INTERVAL_SECONDS
    maximum_ledger_segment_size_bytes: int = MAXIMUM_LEDGER_SEGMENT_SIZE_BYTES
    maximum_ledger_retention_days: int = MAXIMUM_LEDGER_RETENTION_DAYS
    
    # Storage locations (relative to runtime root)
    checkpoint_root: str = CHECKPOINT_ROOT_DEFAULT
    ledger_root: str = LEDGER_ROOT_DEFAULT
    recovery_report_root: str = RECOVERY_REPORT_ROOT_DEFAULT
    
    # Checkpoint behavior
    maximum_retained_checkpoints: int = MAXIMUM_RETAINED_CHECKPOINTS
    compression_mode: str = COMPRESSION_ZLIB  # Default to zlib for balance of speed/size
    checksum_algorithm: str = CHECKSUM_ALGORITHM_SHA256
    
    # Timeout configuration (seconds)
    quiescence_timeout_seconds: float = 10.0
    participant_timeout_seconds: float = 30.0
    restore_timeout_seconds: float = 120.0
    verification_timeout_seconds: float = 30.0
    checkpoint_transaction_timeout_seconds: float = 60.0
    
    # Recovery behavior
    require_all_required_participants: bool = True  # If False, recovery succeeds with degraded state
    allow_recovery_without_checkpoint: bool = False  # If True, start fresh if no checkpoint
    
    @classmethod
    def from_environment(cls, prefix: str = "GORDON_CONTINUITY_") -> "ContinuityConfig":
        """
        Create configuration from environment variables.
        
        Args:
            prefix: Environment variable prefix (default: GORDON_CONTINUITY_)
            
        Returns:
            Configured ContinuityConfig instance
        """
        def get_env_int(name: str, default: int) -> int:
            env_key = f"{prefix}{name}"
            value = os.environ.get(env_key)
            if value is not None:
                try:
                    return int(value)
                except ValueError:
                    pass
            return default
        
        def get_env_float(name: str, default: float) -> float:
            env_key = f"{prefix}{name}"
            value = os.environ.get(env_key)
            if value is not None:
                try:
                    return float(value)
                except ValueError:
                    pass
            return default
        
        def get_env_str(name: str, default: str) -> str:
            env_key = f"{prefix}{name}"
            return os.environ.get(env_key, default)
        
        return cls(
            checkpoint_interval_seconds=get_env_float("CHECKPOINT_INTERVAL_SECONDS", DEFAULT_CHECKPOINT_INTERVAL_SECONDS),
            maximum_checkpoint_duration_seconds=get_env_float("MAXIMUM_CHECKPOINT_DURATION_SECONDS", MAXIMUM_CHECKPOINT_DURATION_SECONDS),
            ledger_flush_interval_seconds=get_env_float("LEDGER_FLUSH_INTERVAL_SECONDS", LEDGER_FLUSH_INTERVAL_SECONDS),
            maximum_ledger_segment_size_bytes=get_env_int("MAXIMUM_LEDGER_SEGMENT_SIZE_BYTES", MAXIMUM_LEDGER_SEGMENT_SIZE_BYTES),
            maximum_ledger_retention_days=get_env_int("MAXIMUM_LEDGER_RETENTION_DAYS", MAXIMUM_LEDGER_RETENTION_DAYS),
            checkpoint_root=get_env_str("CHECKPOINT_ROOT", CHECKPOINT_ROOT_DEFAULT),
            ledger_root=get_env_str("LEDGER_ROOT", LEDGER_ROOT_DEFAULT),
            recovery_report_root=get_env_str("RECOVERY_REPORT_ROOT", RECOVERY_REPORT_ROOT_DEFAULT),
            maximum_retained_checkpoints=get_env_int("MAXIMUM_RETAINED_CHECKPOINTS", MAXIMUM_RETAINED_CHECKPOINTS),
            compression_mode=get_env_str("COMPRESSION_MODE", COMPRESSION_ZLIB),
            checksum_algorithm=get_env_str("CHECKSUM_ALGORITHM", CHECKSUM_ALGORITHM_SHA256),
            quiescence_timeout_seconds=get_env_float("QUIESCENCE_TIMEOUT_SECONDS", 10.0),
            participant_timeout_seconds=get_env_float("PARTICIPANT_TIMEOUT_SECONDS", 30.0),
            restore_timeout_seconds=get_env_float("RESTORE_TIMEOUT_SECONDS", 120.0),
            verification_timeout_seconds=get_env_float("VERIFICATION_TIMEOUT_SECONDS", 30.0),
            checkpoint_transaction_timeout_seconds=get_env_float("CHECKPOINT_TRANSACTION_TIMEOUT_SECONDS", 60.0),
        )

    def to_dict(self) -> dict:
        """Return configuration as a dictionary."""
        return {
            "checkpoint_interval_seconds": self.checkpoint_interval_seconds,
            "maximum_checkpoint_duration_seconds": self.maximum_checkpoint_duration_seconds,
            "ledger_flush_interval_seconds": self.ledger_flush_interval_seconds,
            "maximum_ledger_segment_size_bytes": self.maximum_ledger_segment_size_bytes,
            "maximum_ledger_retention_days": self.maximum_ledger_retention_days,
            "checkpoint_root": self.checkpoint_root,
            "ledger_root": self.ledger_root,
            "recovery_report_root": self.recovery_report_root,
            "maximum_retained_checkpoints": self.maximum_retained_checkpoints,
            "compression_mode": self.compression_mode,
            "checksum_algorithm": self.checksum_algorithm,
            "quiescence_timeout_seconds": self.quiescence_timeout_seconds,
            "participant_timeout_seconds": self.participant_timeout_seconds,
            "restore_timeout_seconds": self.restore_timeout_seconds,
            "verification_timeout_seconds": self.verification_timeout_seconds,
            "checkpoint_transaction_timeout_seconds": self.checkpoint_transaction_timeout_seconds,
            "require_all_required_participants": self.require_all_required_participants,
            "allow_recovery_without_checkpoint": self.allow_recovery_without_checkpoint,
        }