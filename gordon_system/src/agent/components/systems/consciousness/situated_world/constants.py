# Gordon Phase 5.7.7: Situated World - Constants
# ================================================

"""
Canonical constants for the Situated World capability.

This module defines:
* World identity types and states
* Environment type identifiers  
* Lifecycle states
* Capacity limits
* Determinism guarantees
"""

from __future__ import annotations

from typing import Final

# =============================================================================
# WORLD STATE CONSTANTS
# =============================================================================

WORLD_AVAILABLE: Final[str] = "world_available"
"""World is available and ready for contributions."""

WORLD_UNAVAILABLE: Final[str] = "world_unavailable"
"""World is unavailable (initializing or degraded)."""

WORLD_STATE_ACTIVE: Final[str] = "active"
"""World state is active and processing contributions."""

WORLD_STATE_DEGRADED: Final[str] = "degraded"
"""World state is degraded but partially functional."""

WORLD_STATE_FAILED: Final[str] = "failed"
"""World state has failed and requires recovery."""

# =============================================================================
# ENVIRONMENT TYPE IDENTIFIERS
# =============================================================================

ENV_TYPE_PHYSICAL: Final[str] = "physical"
"""Physical environment (sensors, devices, physical space)."""

ENV_TYPE_DESKTOP: Final[str] = "desktop"
"""Desktop environment (windows, applications, files)."""

ENV_TYPE_APPLICATION: Final[str] = "application"
"""Application-specific environment."""

ENV_TYPE_REPOSITORY: Final[str] = "repository"
"""Repository/environment context."""

ENV_TYPE_CONVERSATIONAL: Final[str] = "conversational"
"""Conversational context environment."""

ENV_TYPE_VIRTUAL: Final[str] = "virtual"
"""Virtual/simulated environment."""

ENV_TYPE_SIMULATED: Final[str] = "simulated"
"""Simulated environment for testing/development."""

# =============================================================================
# ENTITY RELATION AFFORDANCE CONSTRAINT KINDS
# =============================================================================

KIND_ENTITY: Final[str] = "entity"
"""Entity kind marker."""

KIND_RELATION: Final[str] = "relation"
"""Relation kind marker."""

KIND_AFFORDANCE: Final[str] = "affordance"
"""Affordance kind marker."""

KIND_CONSTRAINT: Final[str] = "constraint"
"""Constraint kind marker."""

# =============================================================================
# CONSTRAINT CATEGORIES
# =============================================================================

CONSTRAINT_ENVIRONMENTAL: Final[str] = "environmental"
"""Environmental constraints (physical limitations)."""

CONSTRAINT_POLICY: Final[str] = "policy"
"""Policy references (external policy decisions)."""

CONSTRAINT_SECURITY: Final[str] = "security"
"""Security decisions (authorization results)."""

# =============================================================================
# CAPACITY LIMITS
# =============================================================================

MAX_ENTITIES_PER_SNAPSHOT: Final[int] = 10000
"""Maximum entities in a single snapshot."""

MAX_RELATIONS_PER_SNAPSHOT: Final[int] = 50000
"""Maximum relations in a single snapshot."""

MAX_AFFORDANCES_PER_SNAPSHOT: Final[int] = 100000
"""Maximum affordances in a single snapshot."""

MAX_CONSTRAINTS_PER_SNAPSHOT: Final[int] = 1000
"""Maximum constraints in a single snapshot."""

MAX_TRANSITION_HISTORY: Final[int] = 1000
"""Maximum transitions to retain for replay."""

# =============================================================================
# DETERMINISM GUARANTEES
# =============================================================================

DETERMINISTIC_PUBLICATION: Final[bool] = True
"""Deterministic publication is enforced."""

DETERMINISTIC_REPLAY: Final[bool] = True
"""Replay must produce identical results."""

ORDERING_DEPENDENCIES: Final[tuple[str, ...]] = (
    "thread_scheduling",
    "hash_ordering", 
    "memory_addresses",
    "filesystem_ordering",
    "uncontrolled_randomness",
)
"""Ordering dependencies that must never affect publication."""

# =============================================================================
# PROVENANCE TRUST PRIVACY MARKERS
# =============================================================================

PROVENANCE_EXTERNAL: Final[str] = "external"
"""Contribution from external system."""

PROVENANCE_INTERNAL: Final[str] = "internal"
"""Contribution generated internally."""

TRUST_LEVEL_UNTRUSTED: Final[str] = "untrusted"
"""Low trust contribution."""

TRUST_LEVEL_MEDIUM: Final[str] = "medium"
"""Medium trust contribution."""

TRUST_LEVEL_HIGH: Final[str] = "high"
"""High trust contribution."""

PRIVACY_PUBLIC: Final[str] = "public"
"""Publicly accessible world state."""

PRIVACY_INTERNAL: Final[str] = "internal"
"""Internal only world state."""

# =============================================================================
# EXECUTION CYCLE INTEGRATION
# =============================================================================

EXECUTION_GENERATION_DEFAULT: Final[int] = 1
"""Default generation for new execution cycles."""

EXECUTION_GENERATION_MAX_SKIP: Final[int] = 100
"""Maximum generations that can be skipped."""

EXECUTION_TIMEOUT_SECONDS: Final[float] = 5.0
"""Maximum time for world state update per cycle."""