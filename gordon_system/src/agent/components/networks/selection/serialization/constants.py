# Gordon Cognitive Architecture - Phase 4.5.11
# ==============================================
#
"""
Canonical Serialization Constants and Enumerations

This module defines all canonical constants used throughout the serialization system.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Literal


# =============================================================================
# DOCUMENT FORMAT ENUMERATION
# =============================================================================

@dataclass(frozen=True)
class DocumentFormat:
    """
    Canonical document format identifier.
    
    Each format must reproduce the same canonical semantic payload.
    Binary encoding is not allowed to define different semantics.
    
    FORMATS:
        CANONICAL_JSON          : UTF-8 JSON with deterministic representation
        CANONICAL_CBOR          : Concise Binary Object Representation (optional)
        CANONICAL_MESSAGEPACK   : MessagePack binary format (optional)
        CANONICAL_INTERNAL_DATA : Internal Python data structures (no serialization)
        UNKNOWN                 : Unrecognized or unsupported format
    """
    
    name: str = "CANONICAL_JSON"
    """Canonical format name."""
    
    @property
    def is_json(self) -> bool:
        """Whether this is a JSON-based format."""
        return self.name in ("CANONICAL_JSON",)
    
    @property
    def is_binary(self) -> bool:
        """Whether this is a binary format."""
        return self.name in ("CANONICAL_CBOR", "CANONICAL_MESSAGEPACK")


# Format constants
CANONICAL_JSON = DocumentFormat(name="CANONICAL_JSON")
"""Canonical JSON format - UTF-8, deterministic, no BOM."""

CANONICAL_CBOR = DocumentFormat(name="CANONICAL_CBOR")
"""Optional CBOR format (if supported)."""

CANONICAL_MESSAGEPACK = DocumentFormat(name="CANONICAL_MESSAGEPACK")
"""Optional MessagePack format (if supported)."""

CANONICAL_INTERNAL_DATA = DocumentFormat(name="CANONICAL_INTERNAL_DATA")
"""Internal Python data structures (no serialization)."""

UNKNOWN_FORMAT = DocumentFormat(name="UNKNOWN")
"""Unknown or unsupported format."""


# =============================================================================
# SCHEMA EVOLUTION KIND ENUMERATION
# =============================================================================

@dataclass(frozen=True)
class SchemaEvolutionKind:
    """
    Category of schema evolution.
    
    EVOLUTION CATEGORIES:
        ADDITIVE_COMPATIBLE     : Additive changes, fully backward compatible
        CLARIFYING_COMPATIBLE   : Clarification or typo fix, no semantic change
        REPRESENTATION_COMPATIBLE: Representation refinement, same semantics
        VALIDATION_TIGHTENING   : Stricter validation, may reject previously valid artifacts
        VALIDATION_RELAXATION   : Looser validation, accept more artifacts
        DEPRECATION             : Field or value marked as deprecated
        FIELD_RENAME            : Field renamed, identity preserved
        FIELD_SPLIT             : Single field split into multiple fields
        FIELD_MERGE             : Multiple fields merged into one
        ENUM_EXTENSION          : New enum values added
        ENUM_REPLACEMENT        : Enum structure changed
        UNION_EXTENSION         : Union type extended with new members
        TYPE_CHANGE             : Field type changed
        SEMANTIC_CHANGE         : Meaning of field or artifact changes
        BREAKING_CHANGE         : Changes that break backward compatibility
        UNKNOWN                 : Unknown evolution category
    """
    
    kind: str = "ADDITIVE_COMPATIBLE"
    """Canonical evolution kind."""
    
    @property
    def is_compatible(self) -> bool:
        """Whether this evolution is compatible (no breaking changes)."""
        return self.kind in (
            "ADDITIVE_COMPATIBLE",
            "CLARIFYING_COMPATIBLE",
            "REPRESENTATION_COMPATIBLE",
            "VALIDATION_TIGHTENING",  # May reject old artifacts but not break
            "VALIDATION_RELAXATION",
            "DEPRECATION",
            "FIELD_RENAME",
            "ENUM_EXTENSION",
            "UNION_EXTENSION",
        )
    
    @property
    def is_breaking(self) -> bool:
        """Whether this evolution breaks backward compatibility."""
        return self.kind in ("BREAKING_CHANGE", "TYPE_CHANGE", "SEMANTIC_CHANGE")


# Evolution kind constants
ADDITIVE_COMPATIBLE = SchemaEvolutionKind(kind="ADDITIVE_COMPATIBLE")
"""Additive changes, fully backward compatible."""

CLARIFYING_COMPATIBLE = SchemaEvolutionKind(kind="CLARIFYING_COMPATIBLE")
"""Clarification or typo fix, no semantic change."""

REPRESENTATION_COMPATIBLE = SchemaEvolutionKind(kind="REPRESENTATION_COMPATIBLE")
"""Representation refinement, same semantics."""

VALIDATION_TIGHTENING = SchemaEvolutionKind(kind="VALIDATION_TIGHTENING")
"""Stricter validation, may reject previously valid artifacts."""

VALIDATION_RELAXATION = SchemaEvolutionKind(kind="VALIDATION_RELAXATION")
"""Looser validation, accept more artifacts."""

DEPRECATION = SchemaEvolutionKind(kind="DEPRECATION")
"""Field or value marked as deprecated."""

FIELD_RENAME = SchemaEvolutionKind(kind="FIELD_RENAME")
"""Field renamed, identity preserved."""

FIELD_SPLIT = SchemaEvolutionKind(kind="FIELD_SPLIT")
"""Single field split into multiple fields."""

FIELD_MERGE = SchemaEvolutionKind(kind="FIELD_MERGE")
"""Multiple fields merged into one."""

ENUM_EXTENSION = SchemaEvolutionKind(kind="ENUM_EXTENSION")
"""New enum values added."""

ENUM_REPLACEMENT = SchemaEvolutionKind(kind="ENUM_REPLACEMENT")
"""Enum structure changed."""

UNION_EXTENSION = SchemaEvolutionKind(kind="UNION_EXTENSION")
"""Union type extended with new members."""

TYPE_CHANGE = SchemaEvolutionKind(kind="TYPE_CHANGE")
"""Field type changed - requires migration."""

SEMANTIC_CHANGE = SchemaEvolutionKind(kind="SEMANTIC_CHANGE")
"""Meaning of field or artifact changes."""

BREAKING_CHANGE = SchemaEvolutionKind(kind="BREAKING_CHANGE")
"""Changes that break backward compatibility."""


# =============================================================================
# COMPATIBILITY DIMENSION ENUMERATION
# =============================================================================

@dataclass(frozen=True)
class CompatibilityDimension:
    """
    Dimension of compatibility assessment.
    
    Each dimension must be assessed separately.
    A single boolean "compatible" is insufficient.
    
    DIMENSIONS:
        READ_COMPATIBLE         : Can read artifacts from target schema
        WRITE_COMPATIBLE        : Can write to target schema
        ROUND_TRIP_COMPATIBLE   : encode(decode(artifact)) equals artifact
        SEMANTIC_COMPATIBLE     : Decoded artifact has same semantic meaning
        REPLAY_COMPATIBLE       : Can replay from serialized artifacts
        MIGRATION_COMPATIBLE    : Migration between schemas is possible
        DIGEST_COMPATIBLE       : Digest computation is compatible
        PROJECTION_COMPATIBLE   : Projections are preserved correctly
        PRESERVATION_COMPATIBLE : Long-term preservation support
    """
    
    dimension: str = "READ_COMPATIBLE"
    """Canonical compatibility dimension."""
    
    @property
    def requires_migration(self) -> bool:
        """Whether this dimension requires migration to achieve compatibility."""
        return self.dimension in (
            "MIGRATION_COMPATIBLE",
            "ROUND_TRIP_COMPATIBLE",  # May need representation migration
        )


# Compatibility dimension constants
READ_COMPATIBLE = CompatibilityDimension(dimension="READ_COMPATIBLE")
"""Can read artifacts from target schema."""

WRITE_COMPATIBLE = CompatibilityDimension(dimension="WRITE_COMPATIBLE")
"""Can write to target schema."""

ROUND_TRIP_COMPATIBLE = CompatibilityDimension(dimension="ROUND_TRIP_COMPATIBLE")
"""encode(decode(artifact)) equals artifact."""

SEMANTIC_COMPATIBLE = CompatibilityDimension(dimension="SEMANTIC_COMPATIBLE")
"""Decoded artifact has same semantic meaning."""

REPLAY_COMPATIBLE = CompatibilityDimension(dimension="REPLAY_COMPATIBLE")
"""Can replay from serialized artifacts."""

MIGRATION_COMPATIBLE = CompatibilityDimension(dimension="MIGRATION_COMPATIBLE")
"""Migration between schemas is possible."""

DIGEST_COMPATIBLE = CompatibilityDimension(dimension="DIGEST_COMPATIBLE")
"""Digest computation is compatible."""

PROJECTION_COMPATIBLE = CompatibilityDimension(dimension="PROJECTION_COMPATIBLE")
"""Projections are preserved correctly."""

PRESERVATION_COMPATIBLE = CompatibilityDimension(dimension="PRESERVATION_COMPATIBLE")
"""Long-term preservation support."""


# =============================================================================
# MIGRATION STEP KIND ENUMERATION
# =============================================================================

@dataclass(frozen=True)
class MigrationStepKind:
    """
    Type of migration step.
    
    Every migration step must be typed for deterministic execution.
    
    STEP KINDS:
        RENAME_FIELD            : Rename a field to new canonical name
        ADD_FIELD             : Add an optional field with default value
        REMOVE_FIELD          : Remove a field (with loss)
        SPLIT_FIELD           : Split single field into multiple fields
        MERGE_FIELDS          : Merge multiple fields into one
        CHANGE_TYPE           : Change field type (requires conversion)
        MAP_ENUM              : Map old enum values to new ones
        WRAP_UNION            : Wrap value in union type discriminator
        UNWRAP_UNION          : Remove union wrapper
        NORMALIZE_IDENTIFIER  : Normalize identifier representation
        NORMALIZE_REFERENCE   : Normalize reference format
        NORMALIZE_COLLECTION  : Reorder or deduplicate collections
        REORDER_CANONIC_FORM  : Reorder fields to canonical order
        MOVE_EXTENSION_FIELD  : Relocate extension field
        REVISE_SCHEMA_METADATA: Update schema metadata
        RECOMPUTE_DIGEST      : Recompute digests after migration
        PRESERVE_OPAQUE_FIELD : Preserve unknown field opaquely
        QUARANTINE_FIELD      : Mark field as quarantined
        GENERAL               : General purpose migration step
    """
    
    kind: str = "GENERAL"
    """Migration step kind."""


# Step kind constants
RENAME_FIELD = MigrationStepKind(kind="RENAME_FIELD")
"""Rename a field to new canonical name."""

ADD_FIELD = MigrationStepKind(kind="ADD_FIELD")
"""Add an optional field with default value."""

REMOVE_FIELD = MigrationStepKind(kind="REMOVE_FIELD")
"""Remove a field (with loss)."""

SPLIT_FIELD = MigrationStepKind(kind="SPLIT_FIELD")
"""Split single field into multiple fields."""

MERGE_FIELDS = MigrationStepKind(kind="MERGE_FIELDS")
"""Merge multiple fields into one."""

CHANGE_TYPE = MigrationStepKind(kind="CHANGE_TYPE")
"""Change field type (requires conversion)."""

MAP_ENUM = MigrationStepKind(kind="MAP_ENUM")
"""Map old enum values to new ones."""

WRAP_UNION = MigrationStepKind(kind="WRAP_UNION")
"""Wrap value in union type discriminator."""

UNWRAP_UNION = MigrationStepKind(kind="UNWRAP_UNION")
"""Remove union wrapper."""

NORMALIZE_IDENTIFIER = MigrationStepKind(kind="NORMALIZE_IDENTIFIER")
"""Normalize identifier representation."""

NORMALIZE_REFERENCE = MigrationStepKind(kind="NORMALIZE_REFERENCE")
"""Normalize reference format."""

NORMALIZE_COLLECTION = MigrationStepKind(kind="NORMALIZE_COLLECTION")
"""Reorder or deduplicate collections."""

REORDER_CANONIC_FORM = MigrationStepKind(kind="REORDER_CANONIC_FORM")
"""Reorder fields to canonical order."""

MOVE_EXTENSION_FIELD = MigrationStepKind(kind="MOVE_EXTENSION_FIELD")
"""Relocate extension field."""

REVISE_SCHEMA_METADATA = MigrationStepKind(kind="REVISE_SCHEMA_METADATA")
"""Update schema metadata."""

RECOMPUTE_DIGEST = MigrationStepKind(kind="RECOMPUTE_DIGEST")
"""Recompute digests after migration."""

PRESERVE_OPAQUE_FIELD = MigrationStepKind(kind="PRESERVE_OPAQUE_FIELD")
"""Preserve unknown field opaquely."""

QUARANTINE_FIELD = MigrationStepKind(kind="QUARANTINE_FIELD")
"""Mark field as quarantined."""

GENERAL = MigrationStepKind(kind="GENERAL")
"""General purpose migration step."""


# =============================================================================
# REPLAY MODE ENUMERATION
# =============================================================================

@dataclass(frozen=True)
class ReplayMode:
    """
    Mode of replay operation.
    
    Each mode specifies what type of reconstruction is performed.
    
    MODES:
        ARTIFACT_RECONSTRUCTION : Reconstruct single artifact from document
        STATE_RECONSTRUCTION    : Reconstruct state from history
        DELTA_REPLAY            : Replay delta documents to reconstruct state
        TRANSITION_REPLAY       : Replay transitions between states
        HISTORY_REPLAY          : Replay full history of changes
        LINEAGE_REPLAY          : Replay lineage graph relationships
        COORDINATION_REPLAY     : Replay coordination messages
        MIGRATION_REPLAY        : Verify migration determinism
        DIGEST_VERIFICATION     : Verify digest consistency
        COMPATIBILITY_VERIFICATION: Verify compatibility assumptions
        AUDIT_REPLAY            : Replay for audit trail verification
        PROJECTION_RECONSTRUCTION: Reconstruct specific artifact projection
    """
    
    mode: str = "ARTIFACT_RECONSTRUCTION"
    """Replay mode."""


# Replay mode constants
ARTIFACT_RECONSTRUCTION = ReplayMode(mode="ARTIFACT_RECONSTRUCTION")
"""Reconstruct single artifact from document."""

STATE_RECONSTRUCTION = ReplayMode(mode="STATE_RECONSTRUCTION")
"""Reconstruct state from history."""

DELTA_REPLAY = ReplayMode(mode="DELTA_REPLAY")
"""Replay delta documents to reconstruct state."""

TRANSITION_REPLAY = ReplayMode(mode="TRANSITION_REPLAY")
"""Replay transitions between states."""

HISTORY_REPLAY = ReplayMode(mode="HISTORY_REPLAY")
"""Replay full history of changes."""

LINEAGE_REPLAY = ReplayMode(mode="LINEAGE_REPLAY")
"""Replay lineage graph relationships."""

COORDINATION_REPLAY = ReplayMode(mode="COORDINATION_REPLAY")
"""Replay coordination messages."""

MIGRATION_REPLAY = ReplayMode(mode="MIGRATION_REPLAY")
"""Verify migration determinism."""

DIGEST_VERIFICATION = ReplayMode(mode="DIGEST_VERIFICATION")
"""Verify digest consistency."""

COMPATIBILITY_VERIFICATION = ReplayMode(mode="COMPATIBILITY_VERIFICATION")
"""Verify compatibility assumptions."""

AUDIT_REPLAY = ReplayMode(mode="AUDIT_REPLAY")
"""Replay for audit trail verification."""

PROJECTION_RECONSTRUCTION = ReplayMode(mode="PROJECTION_RECONSTRUCTION")
"""Reconstruct specific artifact projection."""


# =============================================================================
# DEFAULTS
# =============================================================================

DEFAULT_DOCUMENT_FORMAT: DocumentFormat = CANONICAL_JSON
"""Default document format for serialization."""

DEFAULT_SCHEMA_VERSION_MAJOR: int = 1
"""Default major version number."""

DEFAULT_SCHEMA_VERSION_MINOR: int = 0
"""Default minor version number."""

DEFAULT_SCHEMA_VERSION_PATCH: int = 0
"""Default patch version number."""

DEFAULT_COMPATIBILITY_POLICY: str = "STRICT"
"""Default compatibility policy."""