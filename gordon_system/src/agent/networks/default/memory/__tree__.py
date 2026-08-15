# Default Network Memory Integration - Module Tree
# ================================================

"""
Module tree for memory integration.

ARCHITECTURAL LAYOUT:
    default/
    └── memory/
        ├── __init__.py          # Main package exports
        ├── __meta__.py          # Package metadata
        ├── __tree__.py          # This file
        │
        ├── Enums and Kinds      # Classification systems
        │   ├── enums.py         # Enumerations
        │   ├── purpose.py       # Integration purposes
        │   ├── subject.py       # Integration subjects
        │   └── kind.py          # Additional kinds
        │
        ├── Core Models          # Request, scope, episode
        │   ├── request.py       # MemoryIntegrationRequest
        │   ├── scope.py         # Scope constraints
        │   ├── episode.py       # MemoryIntegrationEpisode
        │   └── plan.py          # Declarative plans
        │
        ├── Contracts            # Capability interfaces
        │   └── contracts/       # Contract definitions
        │
        ├── Projections          # Memory projections
        │   ├── projection.py    # Base projection reference
        │   ├── record.py        # Record projection
        │   ├── episodic.py      # Episodic memory projection
        │   ├── semantic.py      # Semantic memory projection
        │   ├── autobiographical.py  # Autobiographical projection
        │   ├── procedural.py    # Procedural reference
        │   └── recent_experience.py  # Recent experience
        │
        ├── Relationship Models  # Associations and links
        │   ├── association.py   # Memory associations
        │   ├── link.py          # Memory links
        │   └── cluster.py       # Cluster candidates
        │
        ├── Defect & Uncertainty # Conflict, gaps, duplicates
        │   ├── conflict.py      # Conflicts between memories
        │   ├── gap.py           # Missing memory gaps
        │   ├── duplication.py   # Duplicate candidates
        │   ├── inconsistency.py # Inconsistencies
        │   └── factuality.py    # Factuality and reconstruction
        │
        ├── Proposal Models      # Proposals for Memory authority
        │   ├── proposal.py      # Update, correction proposals
        │   ├── consolidation.py # Consolidation candidates
        │   ├── abstraction.py   # Abstraction candidates
        │   └── retrieval_cue.py # Retrieval cue proposals
        │
        ├── Outcome & Products   # Final results
        │   ├── product.py       # Memory products
        │   ├── outcome.py       # Outcomes and continuations
        │   └── continuation.py  # Continuation recommendations
        │
        ├── Assessment           # Relevance, freshness, confidence
        │   ├── relevance.py     # Relevance assessment
        │   ├── freshness.py     # Freshness assessment
        │   ├── confidence.py    # Confidence models
        │   └── completeness.py  # Completeness models
        │
        ├── State & History      # Coordination state
        │   ├── state/
        │   │   ├── __init__.py
        │   │   ├── model.py     # MemoryIntegrationState
        │   │   └── history.py   # History entries
        │   └── snapshot.py      # State snapshots
        │
        ├── Configuration        # Runtime settings
        │   └── configuration.py # Configuration model
        │
        └── Validation           # Boundary validation
            ├── __init__.py
            ├── request.py       # Request validation
            ├── scope.py         # Scope validation
            ├── episode.py       # Episode validation
            ├── projection.py    # Projection validation
            ├── factuality.py    # Factuality validation
            ├── conflicts.py     # Conflict validation
            ├── proposals.py     # Proposal validation
            └── architecture.py  # Architectural invariants

PROTOCOL:
    - All modules are frozen dataclasses (deeply immutable)
    - No runtime infrastructure dependencies
    - Semantic coordination only, no implementation details
"""

from __future__ import annotations


# =============================================================================
# CANONICAL FILE TREE
# =============================================================================

MEMORY_INTEGRATION_FILES = (
    # Core package
    "default/memory/__init__.py",
    "default/memory/__meta__.py",
    "default/memory/__tree__.py",  # This file
    
    # Enums and kinds
    "default/memory/enums.py",
    "default/memory/purpose.py",
    "default/memory/subject.py",
    
    # Core models
    "default/memory/request.py",
    "default/memory/scope.py",
    "default/memory/episode.py",
    "default/memory/plan.py",
    
    # Contracts (subdirectory)
    "default/memory/contracts/__init__.py",
    "default/memory/contracts/memory.py",
    "default/memory/contracts/retrieval.py",
    "default/memory/contracts/storage.py",
    "default/memory/contracts/validation.py",
    
    # Projections
    "default/memory/projection.py",
    "default/memory/record.py",
    "default/memory/episodic.py",
    "default/memory/semantic.py",
    "default/memory/autobiographical.py",
    "default/memory/procedural.py",
    "default/memory/recent_experience.py",
    
    # Relationship models
    "default/memory/association.py",
    "default/memory/link.py",
    "default/memory/cluster.py",
    
    # Defect and uncertainty
    "default/memory/conflict.py",
    "default/memory/gap.py",
    "default/memory/duplication.py",
    "default/memory/inconsistency.py",
    "default/memory/factuality.py",
    
    # Proposal models
    "default/memory/proposal.py",
    "default/memory/consolidation.py",
    "default/memory/abstraction.py",
    "default/memory/retrieval_cue.py",
    
    # Outcome and products
    "default/memory/product.py",
    "default/memory/outcome.py",
    "default/memory/continuation.py",
    
    # Assessment models
    "default/memory/relevance.py",
    "default/memory/freshness.py",
    "default/memory/confidence.py",
    "default/memory/completeness.py",
    
    # State and history (subdirectory)
    "default/memory/state/__init__.py",
    "default/memory/state/model.py",
    "default/memory/state/history.py",
    "default/memory/state/snapshot.py",
    
    # Configuration
    "default/memory/configuration.py",
    
    # Validation (subdirectory)
    "default/memory/validation/__init__.py",
    "default/memory/validation/request.py",
    "default/memory/validation/scope.py",
    "default/memory/validation/episode.py",
    "default/memory/validation/projection.py",
    "default/memory/validation/factuality.py",
    "default/memory/validation/conflicts.py",
    "default/memory/validation/proposals.py",
    "default/memory/validation/recursion.py",
    "default/memory/validation/architecture.py",
)


# =============================================================================
# MODULE DEPENDENCIES
# =============================================================================

def get_module_dependencies(module_name: str) -> tuple[str, ...]:
    """Get the dependencies for a module."""
    if module_name == "request":
        return ("purpose", "subject", "scope")
    elif module_name == "episode":
        return ("request", "plan", "outcome")
    elif module_name == "projection":
        return ("factuality",)
    elif module_name == "state/model":
        return ("episode", "outcome")
    else:
        return ()


# =============================================================================
# ARCHITECTURAL BOUNDARIES
# =============================================================================

ARCHITECTURAL_CONSTRAINTS = {
    "NO_RUNTIME_DEPENDENCIES": True,
    "ALL_DATACLASS frozen=True": True,
    "NO_STORE_IMPLEMENTATION": True,
    "NO_DIRECT_RETRIEVAL": True,
    "NO_PERSISTENCE_OWNERSHIP": True,
}