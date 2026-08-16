# Canonical Prediction Error Base Types
# ======================================
"""
Base infrastructure for Prediction Error Network Phase 4.9.2.

This module provides:
    - Immutable identity types (with stable equality)
    - Revision tracking
    - Provenance tracking
    - Schema versioning
    - Canonical serialization support

PHASE BOUNDARY:
    This is pure semantic infrastructure with NO runtime dependencies.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Final
from uuid import UUID


# =============================================================================
# SEMANTIC IDENTITIES (IMMUTABLE)
# =============================================================================

@dataclass(frozen=True, slots=True)
class SemanticIdentity:
    """
    Immutable semantic identity with stable equality.
    
    Rules:
        - Empty identities are rejected at construction
        - Identities must be deterministically unique within scope
        - UUID4 is used for generation where external randomness is prohibited
          (identities should be externally supplied in Phase 4.9.2)
    """
    value: str
    
    def __post_init__(self) -> None:
        if not self.value or not isinstance(self.value, str):
            raise ValueError("SemanticIdentity must have a non-empty string value")
    
    def __eq__(self, other: Any) -> bool:
        if not isinstance(other, SemanticIdentity):
            return False
        return self.value == other.value
    
    def __hash__(self) -> int:
        return hash(self.value)
    
    def __str__(self) -> str:
        return f"SemanticIdentity({self.value})"


@dataclass(frozen=True, slots=True)
class RequestIdentity(SemanticIdentity):
    """Identity for a comparison request."""
    pass


@dataclass(frozen=True, slots=True)
class PredictionErrorIdentity(SemanticIdentity):
    """Identity for a prediction error."""
    pass


# =============================================================================
# OBSERVATION REFERENCE (EXTERNAL SUPPLY)
# =============================================================================

@dataclass(frozen=True, slots=True)
class ObservationReference:
    """
    Reference to an external observation.
    
    Rules:
        - Observation authority is external
        - No ownership transfer occurs via reference
        - Authority and revision are preserved from source
    """
    identity: SemanticIdentity
    modality: str  # e.g., "vision", "audio", "language"
    timestamp_ref: SemanticIdentity | None = None  # Semantic, not wall-clock
    authority: str | None = None


# =============================================================================
# ERROR PROVENANCE (TRACKING)
# =============================================================================

@dataclass(frozen=True, slots=True)
class ErrorProvenance:
    """
    Immutable provenance tracking for prediction errors.
    
    Fields:
        request_identity:       Source comparison request identity
        prediction_identity:    Predicted entity identity
        observation_identity:   Observed entity reference
        policy_reference:       Comparison policy applied
        trace_events:           Structural trace of error construction
    """
    request_identity: RequestIdentity
    prediction_identity: SemanticIdentity
    observation_identity: SemanticIdentity
    policy_reference: str | None = None
    trace_events: tuple[str, ...] = field(default_factory=tuple)


# =============================================================================
# REVISION TRACKING
# =============================================================================

@dataclass(frozen=True, slots=True)
class Revision:
    """
    Immutable revision tracking with semantic versioning.
    
    Rules:
        - Major, minor, patch must be non-negative integers
        - Build metadata and pre-release are optional strings
    """
    major: int = 1
    minor: int = 0
    patch: int = 0
    build_metadata: str | None = None
    prerelease: str | None = None
    
    def __post_init__(self) -> None:
        if self.major < 0 or self.minor < 0 or self.patch < 0:
            raise ValueError("Revision components must be non-negative")
    
    def __str__(self) -> str:
        version = f"{self.major}.{self.minor}.{self.patch}"
        if self.prerelease:
            version += f"-{self.prerelease}"
        if self.build_metadata:
            version += f"+{self.build_metadata}"
        return version


# =============================================================================
# SCHEMA VERSIONING
# =============================================================================

@dataclass(frozen=True, slots=True)
class SchemaVersion:
    """
    Immutable schema version with stable identifier.
    
    Rules:
        - Schema identity and version must be non-empty
    """
    schema_id: str
    version: str
    
    def __post_init__(self) -> None:
        if not self.schema_id or not isinstance(self.schema_id, str):
            raise ValueError("SchemaVersion schema_id must be non-empty string")
        if not self.version or not isinstance(self.version, str):
            raise ValueError("SchemaVersion version must be non-empty string")


# =============================================================================
# CANONICAL SERIALIZATION ENVELOPE
# =============================================================================

@dataclass(frozen=True, slots=True)
class SerializationEnvelope:
    """
    Immutable serialization envelope for deterministic serialization.
    
    Fields:
        schema:           Schema identifier (e.g., "gordon.prediction_error.state")
        schema_version:   Schema version string
        kind:             Concrete type discriminator
        payload:          Serialized content (deterministic format)
        provenance:       Optional provenance metadata
    """
    schema: str
    schema_version: str
    kind: str
    payload: dict[str, Any]
    provenance: ErrorProvenance | None = None
    
    def __post_init__(self) -> None:
        if not self.schema or not isinstance(self.schema, str):
            raise ValueError("SerializationEnvelope schema must be non-empty")
        if not self.schema_version or not isinstance(self.schema_version, str):
            raise ValueError("SerializationEnvelope schema_version must be non-empty")
        if not self.kind or not isinstance(self.kind, str):
            raise ValueError("SerializationEnvelope kind must be non-empty")


# =============================================================================
# UTILITY CONSTANTS
# =============================================================================

CANONICAL_SCHEMA_PREFIX: Final[str] = "gordon.prediction_error"
DEFAULT_SCHEMA_VERSION: Final[str] = "1.0.0"