"""Architecture layer - structural patterns and organization.

Phase 3.7.1: Architecture Discovery Framework
=============================================

Phase 3.7.2: Authority, Dependency, Package, Import, Ownership
===============================================================

This package provides deterministic, repository-driven architecture discovery
and immutable architecture modeling capabilities for Gordon Core.
"""

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .discovery import (
        PackageDiscoveryManager,
        ModuleDiscoveryManager,
        AuthorityDiscoveryManager,
        DependencyDiscoveryManager,
        ImportGraphManager,
        RuntimeTopologyManager,
        ArchitectureReportManager,
        MetricsManager,
    )
    
    from .authority import (
        AuthorityKind,
        AuthorityScope,
        AuthorityId,
        RuntimeIdentity,
        AuthorityDescriptor,
        MutationRights,
        AuthorityReference,
        RegistrationStatus,
        RegistrationRequest,
        RegistrationResult,
        AuthorityRelationship,
        AuthorityRelationshipEntry,
        AuthoritySnapshot,
        AuthorityFinding,
        AuthorityReport,
        AuthorityRegistry,
    )
    
    from .duplicate_detection import (
        DuplicateAuthorityType,
        DuplicateAuthorityFinding,
        AuthorityConflict,
        HiddenAuthorityKind,
        HiddenAuthorityFinding,
        ServiceLocatorPattern,
        ServiceLocatorFinding,
        DuplicateAuthorityReport,
        HiddenAuthorityReport,
        ServiceLocatorReport,
        DuplicateAuthorityDetector,
        HiddenAuthorityDetector,
        ServiceLocatorDetector,
        detect_architecture_issues,
    )
    
    from .snapshot import (
        AuthoritySnapshotEntry,
        OwnershipGraphSnapshot,
        DependencyGraphSnapshot,
        RegistrySnapshotEntry,
        StateOwnerSnapshot,
        ArchitectureSnapshot,
        ArchitectureIntegrityManager,
    )

__all__ = [
    "discovery",
    "authority",
    "duplicate_detection",
    "snapshot",
]
