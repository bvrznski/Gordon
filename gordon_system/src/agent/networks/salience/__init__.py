# Gordon Salience Network
# =======================
#
# Canonical implementation of the Salience Network subsystem (Phase 4.8.1).
#
# ARCHITECTURAL PURPOSE:
# ----------------------
# The Salience Network estimates semantic importance across all cognitive domains.
#
# It answers: "What deserves cognitive importance?"
# It never answers: "What should the agent do?"
#
# PRIMARY FUNCTION:
# -----------------
# Semantic evaluation of significance, relevance, novelty, urgency,
# conflict significance, uncertainty significance, prediction-error significance,
# and motivational significance.
#
# ARCHITECTURAL BOUNDARIES:
# -------------------------
# The Salience Network evaluates significance but does NOT own:
#
#   - Attention allocation (owned by Attention Network)
#   - Executive control (owned by Executive Network)
#   - Planning (owned by Planning subsystem)
#   - Reasoning (owned by Reasoning subsystem)
#   - Decision formation (owned by Decision Network)
#   - Working Memory (externally owned)
#   - Runtime services (owned by Core)
#
# The Salience Network DOES own:
#
#   - Semantic salience definitions
#   - Significance estimation contracts
#   - Relevance representation
#   - Novelty representation
#   - Urgency representation
#   - Salience ontology and state
#   - Salience evaluation frameworks
#
# ARCHITECTURAL INVARIANTS:
# -------------------------
# SAL-INV-001: Significance is a semantic property, not an execution signal.
# SAL-INV-002: Salience evaluation never triggers runtime behavior directly.
# SAL-INV-003: Architecture remains declarative and immutable.
# SAL-INV-004: Ownership boundaries are strict and explicit.
# SAL-INV-005: No runtime dependencies in architectural definitions.
# SAL-INV-006: All artifacts are deeply immutable frozen dataclasses.
# SAL-INV-007: Serialization is deterministic for equivalent inputs.
# SAL-INV-008: Validation is purely structural, never behavioral.
# SAL-INV-009: Architecture is runtime-neutral (no threads, no scheduling).
# SAL-INV-010: All dependencies form an acyclic directed graph.
#
# ARCHITECTURAL PRINCIPLES:
# -------------------------
# 1. Canonical definitions only (no duplicates)
# 2. Deeply immutable artifacts (frozen dataclasses)
# 3. External time providers (never use datetime.now, time.time internally)
# 4. External identity providers (never generate UUIDs internally)
# 5. Bounded collections with explicit limits
# 6. Typed State changes via Delta and Transition
# 7. Semantic-time preservation throughout lifecycle
# 8. Runtime-neutral contracts (no runtime dependencies in semantics)
# 9. Deterministic outputs for equivalent inputs
# 10. Import safety (no side effects at import time)

from __future__ import annotations

# =============================================================================
# CANONICAL METADATA (Phase 4.8.1 - Architecture Only)
# =============================================================================

from .__meta__ import (
    __version__,
    PACKAGE_NAME,
    DISPLAY_NAME,
    ARCHITECTURAL_LAYER,
    PACKAGE_STATUS,
    IMPLEMENTATION_PHASE,
    CANONICAL,
)

# =============================================================================
# PHASE 4.8.1: Base Architectural Abstractions
# =============================================================================

from .architecture import (
    BaseSalienceArchitecture,
    BaseSalienceDefinition,
    BaseSalienceIdentity,
    BaseSalienceOwnership,
    BaseSalienceRelationship,
    BaseSalienceContext,
    SalienceArchitecture,
    SalienceIdentity,
    SalienceDefinition,
    SalienceOwnership,
    SalienceResponsibility,
    SalienceScope,
)

# =============================================================================
# PHASE 4.8.1: Ownership Model
# =============================================================================

from .architecture import (
    SalienceArchitectureReference,
    SalienceArchitectureRelationship,
    SalienceArchitectureRequirement,
    SalienceArchitectureAuthority,
    SalienceArchitectureOwner,
    SalienceArchitectureProjection,
)

# =============================================================================
# PHASE 4.8.1: Responsibility Model
# =============================================================================

from .architecture import (
    SalienceResponsibilityReference,
    SalienceResponsibilityRelationship,
    SalienceResponsibilityRequirement,
    SalienceResponsibilityAuthority,
    SalienceResponsibilityOwner,
    SalienceResponsibilityProjection,
)

# =============================================================================
# PHASE 4.8.1: Context Model
# =============================================================================

from .architecture import (
    SalienceContextReference,
    SalienceContextRelationship,
    SalienceContextRequirement,
    SalienceContextAuthority,
    SalienceContextOwner,
    SalienceContextProjection,
)

# =============================================================================
# PHASE 4.8.1: Repository Integration
# =============================================================================

from .integration import (
    SalienceRepositoryRegistry,
    SalienceArchitectureLayer,
    SalienceDependencyGraph,
    SalienceOwnershipGraph,
)

# =============================================================================
# PHASE 4.8.1: Serialization Framework
# =============================================================================

from .serialization import (
    SalienceSerializer,
    SalienceDeserializer,
    SalienceSchemaVersion,
    SalienceRevision,
)

# =============================================================================
# PHASE 4.8.1: Validation Framework
# =============================================================================

from .validation import (
    SalienceValidator,
    SalienceValidationResult,
    SalienceValidationError,
    SalienceOwnershipInvariant,
    SalienceArchitectureInvariant,
)

__all__ = [
    # Metadata
    "__version__",
    "PACKAGE_NAME",
    "DISPLAY_NAME",
    "ARCHITECTURAL_LAYER",
    "PACKAGE_STATUS",
    "IMPLEMENTATION_PHASE",
    "CANONICAL",
    
    # Base Architectural Abstractions (Phase 4.8.1)
    "BaseSalienceArchitecture",
    "BaseSalienceDefinition",
    "BaseSalienceIdentity",
    "BaseSalienceOwnership",
    "BaseSalienceRelationship",
    "BaseSalienceContext",
    
    # Architectural Identity (Phase 4.8.1)
    "SalienceArchitecture",
    "SalienceIdentity",
    "SalienceDefinition",
    "SalienceOwnership",
    "SalienceResponsibility",
    "SalienceScope",
    
    # Ownership Model (Phase 4.8.1)
    "SalienceArchitectureReference",
    "SalienceArchitectureRelationship",
    "SalienceArchitectureRequirement",
    "SalienceArchitectureAuthority",
    "SalienceArchitectureOwner",
    "SalienceArchitectureProjection",
    
    # Responsibility Model (Phase 4.8.1)
    "SalienceResponsibilityReference",
    "SalienceResponsibilityRelationship",
    "SalienceResponsibilityRequirement",
    "SalienceResponsibilityAuthority",
    "SalienceResponsibilityOwner",
    "SalienceResponsibilityProjection",
    
    # Context Model (Phase 4.8.1)
    "SalienceContextReference",
    "SalienceContextRelationship",
    "SalienceContextRequirement",
    "SalienceContextAuthority",
    "SalienceContextOwner",
    "SalienceContextProjection",
    
    # Repository Integration (Phase 4.8.1)
    "SalienceRepositoryRegistry",
    "SalienceArchitectureLayer",
    "SalienceDependencyGraph",
    "SalienceOwnershipGraph",
    
    # Serialization Framework (Phase 4.8.1)
    "SalienceSerializer",
    "SalienceDeserializer",
    "SalienceSchemaVersion",
    "SalienceRevision",
    
    # Validation Framework (Phase 4.8.1)
    "SalienceValidator",
    "SalienceValidationResult",
    "SalienceValidationError",
    "SalienceOwnershipInvariant",
    "SalienceArchitectureInvariant",
]