# Scientific Reasoning Shared Contracts - Phase 7.34
# =====================================================

"""
Shared contract types for the scientific reasoning subsystem.

This module provides canonical implementations of all scientific reasoning contracts:

    ScientificDescriptor     - Metadata about scientific operations
    ScientificMode           - Scientific reasoning modes
    ScientificState          - Lifecycle states
"""

from gordon_system.src.agent.components.systems.cognition.reasoning.scientific.shared.descriptor import (
    ScientificDescriptor,
    ScientificMode,
    ScientificState,
)

__all__ = [
    # Descriptor
    "ScientificDescriptor",
    "ScientificMode",
    "ScientificState",
]