# Focusing Network Architecture Tree
# ====================================

"""
Architectural structure and dependency map for the FocusingNetwork.

This module documents the complete package hierarchy and relationships between
modules, providing a navigable view of the network's architecture.
"""

from typing import Tuple

from gordon_system.src.agent.components.networks.focusing import (
    __version__,
    enums,
    constants,
    configuration as config,
    protocol,
    contracts,
    targets,
    state,
)

class FocusingArchitecture:
    """
    Documentation class for FocusingNetwork architecture tree.

    This provides a structured view of the package hierarchy and architectural status.
    
    ARCHITECTURAL FREEZE STATUS (Phase 4.2.14):
        - Frozen Date: August 14, 2026
        - Version: 1.0.0
        - Status: STABLE
        
    All public contracts, ownership boundaries, dependency graph, and computational
    pipeline are immutable unless changed through formal architectural revision.
    """

    @staticmethod
    def get_version() -> str:
        """Return the package version."""
        return __version__
    
    @staticmethod
    def is_frozen() -> bool:
        """Check if architecture is frozen (Phase 4.2.14)."""
        return True
    
    @staticmethod
    def freeze_date() -> str:
        """Return the architectural freeze date."""
        return "August 14, 2026"
    
    @staticmethod
    def get_freeze_status() -> str:
        """Return the current freeze status."""
        if FocusingArchitecture.is_frozen():
            return f"FREEZE COMPLETE (v{FocusingArchitecture.get_version()})"
        return "ACTIVE DEVELOPMENT"

    @staticmethod
    def list_modules() -> Tuple[str, ...]:
        """List all top-level modules in the FocusingNetwork."""
        return (
            "__init__",
            "__meta__",
            "__tree__",
            "enums",
            "constants",
            "configuration",
            "protocol",
            "contracts",
            "targets",
            "state",
            "priority",
            "relevance",
            "precision",
            "persistence",
            "bias",
            "allocation",
            "arbitration",
            "assessment",
            "routing",
            "validation",
            "telemetry",
        )

    @staticmethod
    def get_module_dependencies(module_name: str) -> Tuple[str, ...]:
        """Get dependencies for a specific module."""
        dependencies = {
            "enums": (),
            "constants": (),
            "models": ("enums",),
            "config": ("constants",),
            "protocol": ("enums", "models", "config"),
            "network": ("enums", "models", "config", "protocol"),
            "contracts": ("models",),
            "targets": ("models",),
            "state": ("models",),
            "priority": ("models",),
            "relevance": ("models",),
            "precision": ("models",),
            "persistence": ("models",),
            "bias": ("models",),
            "allocation": ("models",),
            "arbitration": ("models",),
            "assessment": ("models",),
            "routing": ("network",),
            "validation": ("models",),
            "telemetry": (),
        }
        return dependencies.get(module_name, ())


def print_tree() -> None:
    """Print a visual representation of the architecture tree."""
    print("FocusingNetwork Architecture Tree")
    print("=" * 40)
    print()
    print("focusing/")
    print("├── __init__.py      - Package exports")
    print("├── __meta__.py      - Package metadata")
    print("├── __tree__.py      - This file")
    print()
    print("├── enums.py         - Enumerations (FocusModality, PriorityLevel, etc.)")
    print("├── constants.py     - Default values and bounds")
    print("├── config.py        - Immutable configuration")
    print("├── models.py        - Data models and contracts")
    print("├── protocol.py      - Protocol definitions")
    print("└── network.py       - Main orchestration (FocusingNetwork)")
    print()
    print("Subsystems:")
    print("├── contracts/       - Interface contracts")
    print("│   ├── inputs.py")
    print("│   ├── outputs.py")
    print("│   ├── providers.py")
    print("│   └── consumers.py")
    print()
    print("├── targets/         - Focus target models")
    print("│   ├── target.py")
    print("│   ├── descriptors.py")
    print("│   ├── priorities.py")
    print("│   └── relationships.py")
    print()
    print("├── state/           - State models")
    print("│   ├── state.py")
    print("│   ├── persistence.py")
    print("│   ├── history.py")
    print("│   ├── snapshots.py")
    print("│   └── transitions.py")
    print()
    print("Subsystems:")
    print("├── priority/        - Priority computation")
    print("│   ├── aggregation.py")
    print("│   ├── weighting.py")
    print("│   ├── normalization.py")
    print("│   └── modulation.py")
    print()
    print("├── relevance/       - Relevance evaluation")
    print("│   ├── filtering.py")
    print("│   ├── context.py")
    print("│   ├── competition.py")
    print("│   └── suppression.py")
    print()
    print("├── precision/       - Precision estimation")
    print("│   ├── estimation.py")
    print("│   ├── allocation.py")
    print("│   ├── uncertainty.py")
    print("│   └── bandwidth.py")
    print()
    print("├── persistence/     - Persistence analysis")
    print("│   ├── maintenance.py")
    print("│   ├── decay.py")
    print("│   ├── recovery.py")
    print("│   └── stability.py")
    print()
    print("├── bias/            - Bias computation")
    print("│   ├── generation.py")
    print("│   ├── modality.py")
    print("│   ├── spatial.py")
    print("│   ├── temporal.py")
    print("│   └── memory.py")
    print()
    print("├── allocation/      - Resource allocation")
    print("│   ├── budgets.py")
    print("│   ├── allocator.py")
    print("│   ├── enforcement.py")
    print("│   └── release.py")
    print()
    print("├── arbitration/     - Conflict resolution")
    print("│   ├── conflict.py")
    print("│   ├── endogenous.py")
    print("│   ├── exogenous.py")
    print("│   └── resolution.py")
    print()
    print("├── assessment/      - Final aggregation")
    print("│   ├── assessment.py")
    print("│   ├── diagnostics.py")
    print("│   ├── confidence.py")
    print("│   └── explanation.py")
    print()
    print("└── routing/         - Output routing")
    print("    ├── router.py")
    print("    ├── dispatch.py")
    print("    └── outputs.py")


if __name__ == "__main__":
    print_tree()

