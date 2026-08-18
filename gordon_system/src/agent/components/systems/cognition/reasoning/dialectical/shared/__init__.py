# Dialectical Reasoning - Shared Contracts
# =========================================

"""
Canonical Dialectical Contracts for Phase 7.17.

This module contains the shared contract types that define the dialectical
reasoning architecture: arguments, counterarguments, conflicts, syntheses,
consensus models, validation results, failure records, governance evaluations,
and health metrics.

All contracts are immutable (frozen dataclasses) to preserve traceability.
"""

from .descriptor import DialecticalDescriptor, DialecticalState
from .argument_set import ArgumentSet
from .construction import ArgumentConstruction, CounterArgumentAnalysis
from .conflicts import ConflictResolution
from .synthesis import SynthesisConstruction
from .consensus import ConsensusDiscovery
from .refinement import DialecticalRefinement
from .validation import DialecticalValidationResult
from .failure import DialecticalFailure
from .governance import DialecticalGovernance
from .health import DialecticalHealth
from .diagnostics import DialecticalDiagnostics

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