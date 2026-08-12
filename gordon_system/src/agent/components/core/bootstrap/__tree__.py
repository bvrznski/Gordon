# Bootstrap Package Tree Contract
# =================================

"""
Declarative tree contract for the core bootstrap package.

This file defines structural guarantees without implementation.
"""

from typing import Dict, Any, List, Optional


def get_tree() -> Dict[str, Any]:
    """Return the declarative tree contract for this package."""
    
    return {
        "package_kind": "infrastructure",
        
        # Canonical path in repository
        "canonical_path": "gordon.system.src.agent.components.core.bootstrap",
        
        # Semantic owner responsible for this package
        "semantic_owner": "Core Team",
        
        # Owned concepts (what this package provides)
        "owned_concepts": [
            "startup stages model",
            "bootstrap request and context types",
            "configuration acquisition pipeline",
            "environment fact collection",
            "preflight check system",
            "loading descriptors and plans",
            "factory materialization contracts",
            "initialization orchestration",
            "rollback mechanism",
            "startup handoff",
        ],
        
        # Excluded concepts (what this package does NOT own)
        "excluded_concepts": [
            "cognitive initialization semantics",
            "runtime activation (kernel responsibility)",
            "network coordination (networks layer)",
            "domain-specific policy decisions",
            "global service location",
            "arbitrary import-time registration",
        ],
        
        # Required files in package directory
        "required_files": [
            "__init__.py",   # Main exports
            "__meta__.py",   # Declarative metadata
            "__tree__.py",   # Structural contract (this file)
        ],
        
        # Allowed child packages (for extensions)
        "allowed_children": [],
        
        # Forbidden children (should not appear in this package)
        "forbidden_children": [
            "runtime/",      # Runtime implementations belong elsewhere
            "kernel/",       # Kernel assembly is separate phase
            "loader.py",     # No implicit loading on import
        ],
        
        # Required child packages (none for this infrastructure package)
        "required_children": [],
        
        # Allowed dependency prefixes
        "allowed_dependency_prefixes": [
            "gordon.system.src.agent.components.core.types",
            "gordon.system.src.agent.components.core.contracts",
            "gordon.system.src.agent.components.core.exceptions",
            "gordon.system.src.agent.components.core.configuration",
            "gordon.system.src.agent.components.core.runtime_state",
        ],
        
        # Forbidden dependency prefixes
        "forbidden_dependency_prefixes": [
            "gordon.system.src.agent.capabilities.",  # Core must not depend on capabilities
            "gordon.system.src.agent.networks.",      # Core must not depend on networks
            "gordon.system.src.agent.systems.",       # Systems is lower layer
        ],
        
        # Local invariants (package-specific guarantees)
        "local_invariants": [
            "BootstrapContext is NOT the final RuntimeContext",
            "Startup stages describe progress, not entity lifecycle states",
            "No import-time registration or activation occurs",
            "Configuration precedence is deterministic and explicit",
            "Loading order follows topological sort of dependencies",
            "Rollback reverses successful operations in reverse order",
        ],
    }


TREE = get_tree()

__all__ = ["TREE", "get_tree"]