# Canonical Predictive Base Types
# ================================
"""
Base infrastructure for Predictive Processing Network Phase 4.9.1.

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
          (identities should be externally supplied in Phase 4.9.1)
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
    """Identity for a prediction request."""
    pass


@dataclass(frozen=True, slots=True)
class PredictionIdentity(SemanticIdentity):
    """Identity for a generated prediction."""
    pass


@dataclass(frozen=True, slots=True)
class BeliefIdentity(SemanticIdentity):
    """Identity for belief state projection."""
    pass


@dataclass(frozen=True, slots=True)
class WorldModelIdentity(SemanticIdentity):
    """Identity for world model projection."""
    pass


@dataclass(frozen=True, slots=True)
class HypothesisIdentity(SemanticIdentity):
    """Identity for a predictive hypothesis."""
    pass


@dataclass(frozen=True, slots=True)
class ScenarioIdentity(SemanticIdentity):
    """Identity for a counterfactual scenario."""
    pass


@dataclass(frozen=True, slots=True)
class LatentStateIdentity(SemanticIdentity):
    """Identity for latent state projection."""
    pass


@dataclass(frozen=True, slots=True)
class LatentTrajectoryIdentity(SemanticIdentity):
    """Identity for latent trajectory."""
    pass


@dataclass(frozen=True, slots=True)
class ForecastIdentity(SemanticIdentity):
    """Identity for a contextual forecast."""
    pass


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
        - Revisions enable semantic version comparison where needed
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
        - Versions enable round-trip compatibility checking
    """
    schema_id: str
    version: str
    
    def __post_init__(self) -> None:
        if not self.schema_id or not isinstance(self.schema_id, str):
            raise ValueError("SchemaVersion schema_id must be non-empty string")
        if not self.version or not isinstance(self.version, str):
            raise ValueError("SchemaVersion version must be non-empty string")


# =============================================================================
# PROVENANCE TRACKING
# =============================================================================

@dataclass(frozen=True, slots=True)
class PredictionProvenance:
    """
    Immutable provenance tracking for predictions.
    
    Fields:
        request_identity:       Source request identity
        subject_identity:       Predicted subject identity
        world_model_revision:   World model revision used
        belief_revision:        Belief projection revision used
        generative_model_id:    Generator model reference
        policy_reference:       Policy applied during generation
        context_ids:            Context references used
        assumption_references:  Material assumptions tracked
        constraint_references:  Applied constraints tracked
        derivation_relations:   How this prediction relates to others
    """
    request_identity: RequestIdentity | None = None
    subject_identity: SemanticIdentity | None = None
    world_model_revision: Revision | None = None
    belief_revision: Revision | None = None
    generative_model_id: str | None = None
    policy_reference: str | None = None
    context_ids: tuple[SemanticIdentity, ...] = field(default_factory=tuple)
    assumption_references: tuple[str, ...] = field(default_factory=tuple)
    constraint_references: tuple[str, ...] = field(default_factory=tuple)
    derivation_relations: tuple[str, ...] = field(default_factory=tuple)


@dataclass(frozen=True, slots=True)
class BeliefProvenance:
    """Provenance for belief state projections."""
    source: str
    timestamp_ref: SemanticIdentity | None = None  # Semantic, not wall-clock


@dataclass(frozen=True, slots=True)
class WorldModelProvenance:
    """Provenance for world model projections."""
    source: str
    revision: Revision


@dataclass(frozen=True, slots=True)
class CounterfactualProvenance:
    """Provenance for counterfactual scenarios and predictions."""
    base_scenario_identity: ScenarioIdentity | None = None
    modification_count: int = 0


# =============================================================================
# PREDICTIVE STATE IDENTITIES
# =============================================================================

@dataclass(frozen=True, slots=True)
class StateIdentity(SemanticIdentity):
    """Identity for a predictive state snapshot."""
    pass


@dataclass(frozen=True, slots=True)
class PolicyIdentity(SemanticIdentity):
    """Identity for prediction policy configuration."""
    pass


@dataclass(frozen=True, slots=True)
class GenerativeModelIdentity(SemanticIdentity):
    """Identity for generative model provider."""
    pass


# =============================================================================
# PREDICTIVE SUBJECT REFERENCE (EXTERNAL SUPPLY)
# =============================================================================

@dataclass(frozen=True, slots=True)
class PredictiveSubjectReference:
    """
    Reference to the semantic subject of a prediction.
    
    Rules:
        - Subject identity comes from external authority
        - No ownership transfer occurs via reference
        - Authority and revision are preserved from source
    """
    identity: SemanticIdentity
    kind: str  # e.g., "environment", "object", "event", "goal"
    owner: str | None = None  # External authority name
    authority: str | None = None  # External authority reference
    revision: Revision = field(default_factory=Revision)
    schema_ref: str | None = None


# =============================================================================
# CANONICAL SERIALIZATION ENVELOPE
# =============================================================================

@dataclass(frozen=True, slots=True)
class SerializationEnvelope:
    """
    Immutable serialization envelope for deterministic serialization.
    
    Fields:
        schema:           Schema identifier (e.g., "gordon.predictive.state")
        schema_version:   Schema version string
        kind:             Concrete type discriminator
        payload:          Serialized content (deterministic format)
        provenance:       Optional provenance metadata
    """
    schema: str
    schema_version: str
    kind: str
    payload: dict[str, Any]
    provenance: PredictionProvenance | None = None
    
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

CANONICAL_SCHEMA_PREFIX: Final[str] = "gordon.predictive"

DEFAULT_SCHEMA_VERSION: Final[str] = "1.0.0"