# Workspace Restoration Module
# ============================

"""
Canonical Restoration models for workspace states.

Restoration semantics define how workspace state can be reconstructed from
persisted records while preserving semantic integrity and traceability.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Tuple


@dataclass(frozen=True)
class RestorationCandidate:
    """
    A candidate for restoration from persistent storage.
    
    Captures the information needed to restore a workspace state without
    embedding runtime dependencies.
    """
    
    # State reference
    state_id: str = ""
    """ID of the state to be restored."""
    
    revision: int = 0
    """Revision number of the state to be restored."""
    
    # Persistence record reference
    persistence_record_id: str = ""
    """ID of the persistence record containing the state data."""
    
    storage_location: str = ""
    """Location/URI where persisted data is stored."""
    
    storage_hash: str = ""
    """Hash of persisted data for integrity verification."""
    
    # Restoration metadata
    restored_from_utc: float = 0.0
    """When data was originally persisted (semantic reference)."""
    
    restoration_authority_id: str = ""
    """Authority that created the persistence record."""
    
    # Validity checks
    hash_verified: bool = False
    """Whether storage hash verification succeeded."""
    
    schema_compatible: bool = True
    """Whether the stored data is compatible with current schema version."""


@dataclass(frozen=True)
class RestorationRequest:
    """
    A request to restore a workspace state.
    
    Captures the intent and context for restoration without runtime dependencies.
    """
    
    # Request identity
    request_id: str = ""
    """Unique identifier for this restoration request."""
    
    # Request details
    target_state_id: str = ""
    """ID of the state to be restored."""
    
    target_revision: int = 0
    """Revision of the state to be restored (0 means latest)."""
    
    # Context
    requesting_authority_id: str = ""
    """Authority making the restoration request."""
    
    restoration_reason: str = ""
    """Reason for the restoration request."""
    
    timestamp_utc: float = 0.0
    """When request was made (semantic reference)."""
    
    # Constraints
    require_hash_verification: bool = True
    """Whether hash verification is required."""
    
    allow_schema_migration: bool = False
    """Whether schema migration is allowed if needed."""


@dataclass(frozen=True)
class RestorationValidation:
    """
    Validation of a restoration attempt.
    
    Captures the results of semantic validation for restoration without runtime dependencies.
    """
    
    # Validation result
    valid: bool = False
    """Whether restoration passed all validation checks."""
    
    validation_kind: str = "semantic"
    """Kind of validation performed (semantic, integrity, schema)."""
    
    # Validation details
    candidate_state_id: str = ""
    """ID of the state that was validated."""
    
    validation_errors: Tuple[str, ...] = field(default_factory=tuple)
    """Any validation errors encountered."""
    
    validation_warnings: Tuple[str, ...] = field(default_factory=tuple)
    """Any validation warnings."""
    
    # Timestamps
    validated_at_utc: float = 0.0
    """When validation occurred (semantic reference)."""
    
    # Integrity checks
    hash_match: bool = True
    """Whether stored hash matches computed hash."""
    
    schema_compatible: bool = True
    """Whether data schema is compatible."""


@dataclass(frozen=True)
class RestorationOutcome:
    """
    Result of a restoration operation.
    
    Captures whether restoration succeeded and what state was produced,
    without runtime dependencies.
    """
    
    # Outcome status
    success: bool = False
    """Whether restoration completed successfully."""
    
    restoration_kind: str = "full"
    """Kind of restoration (full, partial, schema-migrated)."""
    
    # State produced
    restored_state_id: str = ""
    """ID of the restored state (if successful)."""
    
    restored_revision: int = 0
    """Revision of the restored state."""
    
    # Validation
    validation: RestorationValidation = field(default_factory=RestorationValidation)
    """Validation results for the restoration."""
    
    error_message: str = ""
    """Error description if restoration failed."""
    
    # Timestamps
    started_at_utc: float = 0.0
    """When restoration began (semantic reference)."""
    
    completed_at_utc: float = 0.0
    """When restoration completed (semantic reference)."""


# =============================================================================
# EXPORTS
# =============================================================================

__all__: tuple[str, ...] = (
    "RestorationCandidate",
    "RestorationRequest",
    "RestorationValidation",
    "RestorationOutcome",
)