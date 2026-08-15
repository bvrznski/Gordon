# Executive Network Package Tree Documentation
# ============================================

"""
Executive Network Package Structure (Phase 4.4.1).

This module documents the canonical package structure and module relationships.
"""

from typing import Dict, Tuple

PACKAGE_TREE: Dict[str, any] = {
    "executive": {
        "__init__.py": "Package root - canonical public API",
        "__meta__.py": "Package metadata (version, ownership, roadmap)",
        "__tree__.py": "This file - package structure documentation",
        
        # Architecture core
        "network.py": "ExecutiveNetwork protocol and implementation",
        "architecture.py": "Architectural definitions and invariants",
        "ownership.py": "Responsibility ownership matrix",
        "boundaries.py": "Boundary definitions with other systems",
        "configuration.py": "Configuration types and defaults",
        
        # Enums and constants
        "enums.py": "Canonical enum definitions",
        "exceptions.py": "Exception types",
        
        # Contracts package
        "contracts/": {
            "__init__.py": "Contracts package root",
            "network.py": "ExecutiveNetwork contract",
            "state.py": "ExecutiveState contract",
            "context.py": "ExecutiveContext contract",
            "task_set.py": "ExecutiveTaskSet contract",
            "request.py": "ExecutiveRequest contract",
            "result.py": "ExecutiveResult contract",
            "product.py": "ExecutiveProduct contract",
            "proposal.py": "ExecutiveProposal contract",
            "outcome.py": "ExecutiveOutcome contract",
            "continuation.py": "ExecutiveContinuation contract",
            "authority.py": "ExecutiveAuthority contract",
            "validation.py": "Architecture validation contracts",
        },
        
        # State package
        "state/": {
            "__init__.py": "State package root",
            "reference.py": "Immutable state references",
            "revision.py": "Revision tracking and versioning",
            "snapshot.py": "State snapshot types",
        },
        
        # Integration package (external system contracts)
        "integration/": {
            "__init__.py": "Integration package root",
            "execution.py": "Execution integration contracts",
            "core.py": "Core integration contracts",
            "planning.py": "Planning integration contracts",
            "reasoning.py": "Reasoning integration contracts",
            "decision.py": "Decision integration contracts",
            "action_selection.py": "ActionSelection integration contracts",
            "action_execution.py": "ActionExecution integration contracts",
            "alerting.py": "AlertingNetwork integration contracts",
            "focusing.py": "FocusingNetwork integration contracts",
            "default.py": "DefaultNetwork integration contracts",
            "motivation.py": "Motivation integration contracts",
            "working_memory.py": "WorkingMemory integration contracts",
            "workspace.py": "Workspace integration contracts",
            "memory.py": "Memory integration contracts",
            "monitoring.py": "Monitoring integration contracts",
            "policy.py": "Policy integration contracts",
            "security.py": "Security integration contracts",
            "communication.py": "Communication integration contracts",
        },
        
        # Diagnostics package
        "diagnostics/": {
            "__init__.py": "Diagnostics package root",
            "event.py": "Executive diagnostic events",
            "projection.py": "Executive state projections for diagnostics",
        },
        
        # Validation package
        "validation/": {
            "__init__.py": "Validation package root",
            "architecture.py": "Architectural validation rules",
            "ownership.py": "Ownership boundary validation",
            "dependencies.py": "Dependency direction validation",
            "public_api.py": "Public API contract validation",
            "invariants.py": "Architectural invariants validation",
        },
        
        # Documentation
        "docs/": {
            "architecture.md": "Architecture overview documentation",
            "ownership.md": "Responsibility ownership matrix",
            "boundaries.md": "System boundaries and interfaces",
            "terminology.md": "Glossary of executive terms",
            "roadmap.md": "Implementation roadmap by phase",
        },
    }
}

# =============================================================================
# PACKAGE DEPENDENCY DIRECTION
# =============================================================================

DEPENDENCY_DIRECTIONS: Tuple[str, ...] = (
    # Executive Network depends on (NOT the other way around):
    "gordon_system.src.agent.architecture",  # Architecture contracts
    
    # Executive Network does NOT depend on:
    # - Core implementations (only architecture)
    # - Execution implementations (only contracts)
    # - Concrete Planning/Reasoning implementations
    # - Runtime schedulers/workers
    # - External services/providers
)

# =============================================================================
# EXPORT POLICY
# =============================================================================

__all__: Tuple[str, ...] = (
    "PACKAGE_TREE",
    "DEPENDENCY_DIRECTIONS",
)

if __name__ == "__main__":
    import json
    
    def serialize_tree(tree: Dict) -> str:
        """Serialize the tree to a JSON-like string."""
        lines = []
        
        def walk(d: Dict, indent: int = 0):
            for k, v in d.items():
                prefix = "  " * indent
                if isinstance(v, dict):
                    lines.append(f"{prefix}{k}/")
                    walk(v, indent + 1)
                else:
                    lines.append(f"{prefix}{k}")
        
        walk(tree)
        return "\n".join(lines)
    
    print(serialize_tree(PACKAGE_TREE))