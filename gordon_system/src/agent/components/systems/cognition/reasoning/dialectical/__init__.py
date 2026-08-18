# Dialectical Reasoning - Phase 7.17
# ==================================

"""
Dialectical Reasoning for the Gordon Cognitive Architecture.

This package implements dialectical reasoning as described in Phase 7.17 of the
Gordon architecture specification.

Dialectical Reasoning is Gordon's truth refinement engine. Instead of assuming
a single reasoning path is correct, it actively constructs competing explanations
and forces them into structured comparison.

Usage:
    from gordon_system.src.agent.components.systems.cognition.reasoning.dialectical.shared import (
        DialecticalDescriptor,
        ArgumentSet,
        SynthesisConstruction,
        ConsensusDiscovery,
    )

    # Create a dialectical session descriptor
    descriptor = DialecticalDescriptor.create(
        semantic_identity="dialectics:example",
        reasoning_goal="Resolve competing explanations for X"
    )
"""

from .shared import (
    DialecticalDescriptor,
    DialecticalState,
    ArgumentSet,
    ArgumentConstruction,
    CounterArgumentAnalysis,
    ConflictResolution,
    SynthesisConstruction,
    ConsensusDiscovery,
    DialecticalRefinement,
    DialecticalValidationResult,
    DialecticalFailure,
    DialecticalGovernance,
    DialecticalHealth,
    DialecticalDiagnostics,
)

__all__ = [
    "DialecticalDescriptor",
    "DialecticalState",
    "ArgumentSet",
    "ArgumentConstruction",
    "CounterArgumentAnalysis",
    "ConflictResolution",
    "SynthesisConstruction",
    "ConsensusDiscovery",
    "DialecticalRefinement",
    "DialecticalValidationResult",
    "DialecticalFailure",
    "DialecticalGovernance",
    "DialecticalHealth",
    "DialecticalDiagnostics",
]

__version__ = "1.0.0"