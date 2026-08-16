# Gordon Cognitive Architecture - Phase 4.5.11
# ==============================================
#
"""
Serialization Exception Hierarchy

This module defines all exceptions used in the Action Selection serialization system.
All exceptions are deeply immutable and safe for use in serialization contexts.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Tuple


# =============================================================================
# BASE SERIALIZATION ERROR
# =============================================================================

@dataclass(frozen=True, slots=True)
class ActionSelectionSerializationError(Exception):
    """
    Base exception for all Action Selection serialization errors.
    
    This is the root of the exception hierarchy. All serialization-related
    exceptions should inherit from this type.
    
    IMPORTANT:
        - Exceptions are deeply immutable
        - No runtime State in exceptions
        - Exception messages are deterministic
        - No circular references in exception data
    """
    
    message: str = ""
    """Human-readable error description."""
    
    artifact_kind: str | None = None
    """The artifact kind involved (if applicable)."""
    
    artifact_identity: str | None = None
    """The artifact identity involved (if applicable)."""
    
    context: Tuple[str, ...] = field(default_factory=tuple)
    """Additional context for error diagnosis."""
    
    def __str__(self) -> str:
        parts = [f"ActionSelectionSerializationError"]
        if self.artifact_kind:
            parts.append(f"[{self.artifact_kind}]")
        if self.message:
            parts.append(f": {self.message}")
        return "".join(parts)


# =============================================================================
# ENCODING ERRORS
# =============================================================================

@dataclass(frozen=True, slots=True)
class ActionSelectionEncodingError(ActionSelectionSerializationError):
    """Exception raised during canonical encoding."""
    
    input_artifact_kind: str | None = None
    """The kind of artifact being encoded."""
    
    encoding_profile: str | None = None
    """The encoding profile attempted."""
    
    def __str__(self) -> str:
        parts = [f"ActionSelectionEncodingError"]
        if self.input_artifact_kind:
            parts.append(f"[{self.input_artifact_kind}]")
        if self.message:
            parts.append(f": {self.message}")
        return "".join(parts)


# =============================================================================
# DECODING ERRORS
# =============================================================================

@dataclass(frozen=True, slots=True)
class ActionSelectionDecodingError(ActionSelectionSerializationError):
    """Exception raised during canonical decoding."""
    
    format_name: str | None = None
    """The document format attempted."""
    
    schema_identity: str | None = None
    """The schema identity (if known)."""
    
    def __str__(self) -> str:
        parts = [f"ActionSelectionDecodingError"]
        if self.format_name:
            parts.append(f"[{self.format_name}]")
        if self.message:
            parts.append(f": {self.message}")
        return "".join(parts)


@dataclass(frozen=True, slots=True)
class ActionSelectionDuplicateKeyError(ActionSelectionDecodingError):
    """Duplicate key detected during JSON decode."""
    
    duplicate_key: str = ""
    """The duplicate key value."""
    
    def __str__(self) -> str:
        return f"ActionSelectionDuplicateKeyError: Duplicate key '{self.duplicate_key}'"


@dataclass(frozen=True, slots=True)
class ActionSelectionCorruptionError(ActionSelectionDecodingError):
    """Document corruption detected."""
    
    corruption_type: str = ""
    """Type of corruption (e.g., truncated, invalid_utf8)."""
    
    location: Tuple[int, int] | None = None
    """Byte offset where corruption detected (if applicable)."""
    
    def __str__(self) -> str:
        parts = [f"ActionSelectionCorruptionError[{self.corruption_type}]"]
        if self.location:
            parts.append(f" at byte {self.location[0]}")
        if self.message:
            parts.append(f": {self.message}")
        return "".join(parts)


# =============================================================================
# SCHEMA ERRORS
# =============================================================================

@dataclass(frozen=True, slots=True)
class ActionSelectionSchemaError(ActionSelectionSerializationError):
    """Exception related to schema validation or resolution."""
    
    schema_identity: str | None = None
    """The schema identity involved."""
    
    schema_version: str | None = None
    """The schema version involved."""
    
    def __str__(self) -> str:
        parts = [f"ActionSelectionSchemaError"]
        if self.schema_identity:
            parts.append(f"[{self.schema_identity}")
            if self.schema_version:
                parts.append(f":{self.schema_version}]")
            else:
                parts.append("]")
        if self.message:
            parts.append(f": {self.message}")
        return "".join(parts)


@dataclass(frozen=True, slots=True)
class ActionSelectionSchemaIdentityError(ActionSelectionSchemaError):
    """Invalid or unrecognized schema identity."""
    
    def __str__(self) -> str:
        parts = [f"ActionSelectionSchemaIdentityError"]
        if self.schema_identity:
            parts.append(f"[{self.schema_identity}]")
        if self.message:
            parts.append(f": {self.message}")
        return "".join(parts)


@dataclass(frozen=True, slots=True)
class ActionSelectionSchemaVersionError(ActionSelectionSchemaError):
    """Invalid or unsupported schema version."""
    
    expected_version: str | None = None
    """Expected schema version."""
    
    def __str__(self) -> str:
        parts = [f"ActionSelectionSchemaVersionError"]
        if self.schema_identity:
            parts.append(f"[{self.schema_identity}")
            if self.expected_version:
                parts.append(f": expected={self.expected_version}]")
            else:
                parts.append("]")
        if self.message:
            parts.append(f": {self.message}")
        return "".join(parts)


# =============================================================================
# MIGRATION ERRORS
# =============================================================================

@dataclass(frozen=True, slots=True)
class ActionSelectionMigrationError(ActionSelectionSerializationError):
    """Exception during migration."""
    
    source_schema: str | None = None
    """Source schema identity."""
    
    target_schema: str | None = None
    """Target schema identity."""
    
    step_index: int | None = None
    """Step index where error occurred (if applicable)."""
    
    def __str__(self) -> str:
        parts = [f"ActionSelectionMigrationError"]
        if self.source_schema and self.target_schema:
            parts.append(f"[{self.source_schema} -> {self.target_schema}]")
        elif self.source_schema:
            parts.append(f"[from {self.source_schema}]")
        if self.message:
            parts.append(f": {self.message}")
        return "".join(parts)


@dataclass(frozen=True, slots=True)
class ActionSelectionMigrationConflictError(ActionSelectionMigrationError):
    """Migration conflict detected."""
    
    conflict_type: str = ""
    """Type of conflict (e.g., field_value_mismatch)."""
    
    def __str__(self) -> str:
        parts = [f"ActionSelectionMigrationConflictError[{self.conflict_type}]"]
        if self.source_schema and self.target_schema:
            parts.append(f"[{self.source_schema} -> {self.target_schema}]")
        if self.message:
            parts.append(f": {self.message}")
        return "".join(parts)


# =============================================================================
# REPLAY ERRORS
# =============================================================================

@dataclass(frozen=True, slots=True)
class ActionSelectionReplayError(ActionSelectionSerializationError):
    """Exception during replay."""
    
    replay_mode: str | None = None
    """The replay mode attempted."""
    
    checkpoint_index: int | None = None
    """Checkpoint index where error occurred (if applicable)."""
    
    def __str__(self) -> str:
        parts = [f"ActionSelectionReplayError"]
        if self.replay_mode:
            parts.append(f"[{self.replay_mode}]")
        if self.message:
            parts.append(f": {self.message}")
        return "".join(parts)


@dataclass(frozen=True, slots=True)
class ActionSelectionReplayDivergenceError(ActionSelectionReplayError):
    """Replay diverged from expected result."""
    
    divergence_type: str = ""
    """Type of divergence (e.g., identity_mismatch)."""
    
    def __str__(self) -> str:
        parts = [f"ActionSelectionReplayDivergenceError[{self.divergence_type}]"]
        if self.message:
            parts.append(f": {self.message}")
        return "".join(parts)


# =============================================================================
# DIGEST ERRORS
# =============================================================================

@dataclass(frozen=True, slots=True)
class ActionSelectionDigestError(ActionSelectionSerializationError):
    """Exception during digest computation or verification."""
    
    digest_kind: str | None = None
    """The digest kind (e.g., structural, semantic)."""
    
    def __str__(self) -> str:
        parts = [f"ActionSelectionDigestError"]
        if self.digest_kind:
            parts.append(f"[{self.digest_kind}]")
        if self.message:
            parts.append(f": {self.message}")
        return "".join(parts)


# =============================================================================
# UTILITY FUNCTIONS
# =============================================================================

def create_encoding_error(
    message: str,
    artifact_kind: str | None = None,
    artifact_identity: str | None = None,
) -> ActionSelectionEncodingError:
    """Create an encoding error with common context."""
    return ActionSelectionEncodingError(
        message=message,
        artifact_kind=artifact_kind,
        artifact_identity=artifact_identity,
    )


def create_decoding_error(
    message: str,
    format_name: str | None = None,
    schema_identity: str | None = None,
) -> ActionSelectionDecodingError:
    """Create a decoding error with common context."""
    return ActionSelectionDecodingError(
        message=message,
        format_name=format_name,
        schema_identity=schema_identity,
    )


def create_schema_error(
    message: str,
    schema_identity: str | None = None,
    schema_version: str | None = None,
) -> ActionSelectionSchemaError:
    """Create a schema error with common context."""
    return ActionSelectionSchemaError(
        message=message,
        schema_identity=schema_identity,
        schema_version=schema_version,
    )


def create_migration_error(
    message: str,
    source_schema: str | None = None,
    target_schema: str | None = None,
) -> ActionSelectionMigrationError:
    """Create a migration error with common context."""
    return ActionSelectionMigrationError(
        message=message,
        source_schema=source_schema,
        target_schema=target_schema,
    )


def create_replay_error(
    message: str,
    replay_mode: str | None = None,
) -> ActionSelectionReplayError:
    """Create a replay error with common context."""
    return ActionSelectionReplayError(
        message=message,
        replay_mode=replay_mode,
    )
