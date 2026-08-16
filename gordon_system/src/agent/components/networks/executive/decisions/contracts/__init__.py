# Gordon Executive Decision Contracts - Phase 4.4.10A
# ======================================================

"""
Executive Decision Contract System.

This package defines the immutable semantic contracts that form the
foundation of the Executive Decision system.
"""

from gordon_system.src.agent.networks.executive.decisions.contracts.identity import (
    DecisionIdentity,
)

from gordon_system.src.agent.networks.executive.decisions.contracts.artifact import (
    ExecutiveArtifact,
)

from gordon_system.src.agent.networks.executive.decisions.contracts.decision import (
    ExecutiveDecision,
    DecisionKind,
    DecisionState,
    DecisionHorizon,
    DecisionStability,
)

from gordon_system.src.agent.networks.executive.decisions.contracts.revision import (
    DecisionRevision,
)

# Revision is imported through decision module
from gordon_system.src.agent.networks.executive.decisions.contracts.commitment import (
    DecisionCommitment,
)

from gordon_system.src.agent.networks.executive.decisions.contracts.recommendation import (
    DecisionRecommendation,
)

from gordon_system.src.agent.networks.executive.decisions.contracts.authority import (
    DecisionAuthority,
    AuthorityLevel,
    AuthorityRole,
)

from gordon_system.src.agent.networks.executive.decisions.contracts.ownership import (
    DecisionOwnership,
    OwnershipKind,
)

from gordon_system.src.agent.networks.executive.decisions.contracts.provenance import (
    DecisionProvenance,
    ProvenanceSource,
    ProvenanceLink,
)

from gordon_system.src.agent.networks.executive.decisions.contracts.context import (
    DecisionContext,
    ContextScope,
    ContextKind,
)

from gordon_system.src.agent.networks.executive.decisions.contracts.composition import (
    DecisionComposition,
    DecisionAssumptions,
    DecisionConstraints,
    DecisionDependencies,
)

from gordon_system.src.agent.networks.executive.decisions.contracts.evidence import (
    DecisionEvidence,
    EvidenceSource,
    EvidenceKind,
)

from gordon_system.src.agent.networks.executive.decisions.contracts.justification import (
    DecisionJustification,
)

from gordon_system.src.agent.networks.executive.decisions.contracts.metadata import (
    DecisionMetadata,
)

from gordon_system.src.agent.networks.executive.decisions.contracts.references import (
    DecisionReference,
    ReferenceKind,
)

__all__ = [
    # Core contracts
    "ExecutiveDecision",
    "DecisionRevision",
    "DecisionCommitment",
    "DecisionRecommendation",
    # Identity and lifecycle
    "DecisionIdentity",
    "ExecutiveArtifact",
    # Authority and ownership
    "DecisionAuthority",
    "AuthorityLevel",
    "AuthorityRole",
    "DecisionOwnership",
    "OwnershipKind",
    # Provenance and lineage
    "DecisionProvenance",
    "ProvenanceSource",
    "ProvenanceLink",
    # Context and scope
    "DecisionContext",
    "ContextScope",
    "ContextKind",
    # Composition
    "DecisionComposition",
    "DecisionAssumptions",
    "DecisionConstraints",
    "DecisionDependencies",
    # Evidence and reasoning support
    "DecisionEvidence",
    "EvidenceSource",
    "EvidenceKind",
    "DecisionJustification",
    # Metadata and references
    "DecisionMetadata",
    "DecisionReference",
    "ReferenceKind",
    # Classification enums
    "DecisionKind",
    "DecisionState",
    "DecisionHorizon",
    "DecisionStability",
]