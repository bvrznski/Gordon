# Derived Memory - Phase 5.1.6 Canonical Implementation
# =========================================================
"""
Derived Memory: Semantic inference layer that computes higher-order artifacts.

Purpose:
    Compute new semantic artifacts from existing memory, never observations.
    
The derived memory system produces:

Causal derivations
    Cause-effect relationships, dependency structures, mechanisms

Counterfactual derivations  
    Alternative histories, hypothetical events, intervention analysis

Predictive derivations
    Future states, expected observations, anticipated events

Derived Memory Laws:
    DERIVATION-LAW-001: Every derivation produces a new semantic interpretation
    DERIVATION-LAW-002: Derivations never modify source memory artifacts
    DERIVATION-LAW-003: Derivations preserve source identity
    DERIVATION-LAW-004: Derivations preserve provenance
    DERIVATION-LAW-005: Derivations preserve revision history
    DERIVATION-LAW-006: Derivations expose supporting evidence
    DERIVATION-LAW-007: Derivations remain independently testable
    DERIVATION-LAW-008: Derivation behavior remains deterministic

Architecture Contract:
    Memory Artifacts → Evidence Selection → Inference → Validation → Derived Artifact
"""

from __future__ import annotations

# Import derivation base contracts using relative imports for portability
try:
    from .derivation import (
        DerivationKind,
        DerivationStatus,
        SupportingEvidence,
        DerivationProvenance,
        DerivationMetrics,
        MemoryDerivation,
        MemoryDerivationBuilder,
        DerivationValidator,
    )
    from .evidence import (
        EvidenceKind,
        EvidenceItem,
        EvidenceCollection,
        EvidenceValidator,
        EvidenceBuilder,
    )
    from .provenance import (
        DerivationProvenanceSource,
        DerivationProvenanceRecord,
        DerivationProvenanceBuilder,
        DerivationProvenanceChain,
        DerivationProvenanceChainBuilder,
        DerivationProvenanceValidator,
    )
    from .statistics import (
        DerivationStatisticsBucket,
        DerivationStatistics,
        DerivationStatisticsBuilder,
        MetricDistribution,
    )
    from .diagnostics import (
        DerivationDiagnostic,
        DerivationDiagnostics,
        DerivationDiagnosticBuilder,
        DerivationDiagnosticsBuilder,
    )
    from .health import (
        DerivationHealth,
        HealthStatus,
        DerivationHealthBuilder,
        DerivationHealthChecker,
    )
except ImportError as e:
    raise ImportError(
        f"Failed to import derived memory modules. "
        f"Ensure all derived submodules exist and are properly defined: {e}"
    )

__all__ = [
    # Kinds
    "DerivationKind",
    
    # Status
    "DerivationStatus",
    
    # Core contracts
    "SupportingEvidence",
    "DerivationProvenance",
    "DerivationMetrics",
    "MemoryDerivation",
    "MemoryDerivationBuilder",
    "DerivationValidator",
    
    # Evidence
    "EvidenceKind",
    "EvidenceItem",
    "EvidenceCollection",
    "EvidenceValidator",
    "EvidenceBuilder",
    
    # Provenance
    "DerivationProvenanceSource",
    "DerivationProvenanceRecord",
    "DerivationProvenanceBuilder",
    "DerivationProvenanceChain",
    "DerivationProvenanceChainBuilder",
    "DerivationProvenanceValidator",
    
    # Statistics
    "DerivationStatisticsBucket",
    "DerivationStatistics",
    "DerivationStatisticsBuilder",
    "MetricDistribution",
    
    # Diagnostics
    "DerivationDiagnostic",
    "DerivationDiagnostics",
    "DerivationDiagnosticBuilder",
    "DerivationDiagnosticsBuilder",
    
    # Health
    "DerivationHealth",
    "HealthStatus",
    "DerivationHealthBuilder",
    "DerivationHealthChecker",
]