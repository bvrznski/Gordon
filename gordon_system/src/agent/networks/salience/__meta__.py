# Gordon Salience Network Package Metadata
# ==========================================

"""
Package metadata for SalienceNetwork - Gordon's semantic salience network.

ARCHITECTURAL PURPOSE:
    The Salience Network estimates semantic importance across all cognitive domains.
    
ARCHITECTURAL LAYER:
    Cognitive Network Layer - Semantic Significance Evaluation

OWNERSHIP:
    Sole owner of: semantic salience, significance estimation, relevance representation,
    novelty representation, urgency representation, salience ontology and state.
"""

__version__: str = "0.1.0-alpha"
"""Package version string following semantic versioning."""

PACKAGE_NAME: str = "salience"
"""Canonical package identifier."""

DISPLAY_NAME: str = "Salience Network"
"""Human-readable display name for the package."""

ARCHITECTURAL_LAYER: str = "cognitive_network"
"""Architectural layer to which this package belongs."""

PACKAGE_STATUS: str = "architecture-phase-1"
"""Current implementation status of the package."""

IMPLEMENTATION_PHASE: str = "4.8.1"
"""Phase during which this package was scaffolded."""

CANONICAL: bool = True
"""Indicates whether this is a canonical implementation."""

LEGACY_NAMES: tuple[str, ...] = ()
"""Historical names that have been retired in favor of this package."""

RESPONSIBILITIES: tuple[str, ...] = (
    "semantic salience estimation",
    "significance evaluation framework",
    "relevance representation",
    "novelty representation",
    "urgency representation",
    "salience ontology maintenance",
    "contextual importance assessment",
)
"""Primary responsibilities of the Salience Network."""

FORBIDDEN_RESPONSIBILITIES: tuple[str, ...] = (
    "attention allocation",
    "executive control",
    "planning implementation",
    "reasoning implementation",
    "decision formation",
    "working memory management",
    "runtime scheduling",
    "behavioral execution",
    "cognitive resource allocation",
)
"""Responsibilities explicitly forbidden to this package."""

ARCHITECTURAL_OWNERSHIP: str = "Salience Network"
"""Canonical owner of the semantic salience contract."""

# Architectural Laws (Phase 4.8.1 - SAL-ARCHITECTURE-LAW-XXX)
ARCHITECTURAL_LAWS: tuple[str, ...] = (
    "SAL-ARCHITECTURE-LAW-001: Salience Network is sole owner of semantic salience",
    "SAL-ARCHITECTURE-LAW-002: Architecture defines ownership, never behavior",
    "SAL-ARCHITECTURE-LAW-003: Architecture never executes computation",
    "SAL-ARCHITECTURE-LAW-004: Architecture never allocates attention",
    "SAL-ARCHITECTURE-LAW-005: Architecture never performs executive control",
    "SAL-ARCHITECTURE-LAW-006: Architecture preserves subsystem identity",
    "SAL-ARCHITECTURE-LAW-007: Architecture remains deterministic",
    "SAL-ARCHITECTURE-LAW-008: Architecture remains immutable",
    "SAL-ARCHITECTURE-LAW-009: Every architectural relationship is explicit",
    "SAL-ARCHITECTURE-LAW-010: Every architectural dependency is explicit",
)

# Ownership Laws (Phase 4.8.1 - SAL-OWNERSHIP-LAW-XXX)
OWNERSHIP_LAWS: tuple[str, ...] = (
    "SAL-OWNERSHIP-LAW-001: Every concept has exactly one owner",
    "SAL-OWNERSHIP-LAW-002: Ownership never overlaps",
    "SAL-OWNERSHIP-LAW-003: Ownership is explicit and immutable",
    "SAL-OWNERSHIP-LAW-004: Ownership does not migrate between subsystems",
    "SAL-OWNERSHIP-LAW-005: Responsibilities derive from ownership",
)

# Repository Laws (Phase 4.8.1 - SAL-REPOSITORY-LAW-XXX)
REPOSITORY_LAWS: tuple[str, ...] = (
    "SAL-REPOSITORY-LAW-001: Every public object has validation",
    "SAL-REPOSITORY-LAW-002: Every public object has serialization",
    "SAL-REPOSITORY-LAW-003: Every public object has documentation",
    "SAL-REPOSITORY-LAW-004: Dependencies form acyclic graph",
    "SAL-REPOSITORY-LAW-005: Repository hierarchy is deterministic",
)

# Architectural Invariants (Phase 4.8.1 - SAL-INV-XXX)
ARCHITECTURAL_INVARIANTS: tuple[str, ...] = (
    "SAL-INV-001: Architecture remains semantic and declarative",
    "SAL-INV-002: Architecture is immutable and deterministic",
    "SAL-INV-003: No runtime behavior in architecture modules",
    "SAL-INV-004: Dependencies form acyclic directed graph",
    "SAL-INV-005: All ownership relationships are explicit",
)
"""Architectural laws governing the Salience Network."""