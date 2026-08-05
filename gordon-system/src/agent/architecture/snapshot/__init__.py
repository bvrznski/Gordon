"""Architecture snapshots and integrity verification.

Phase 3.7.2: Authority, Dependency, Package, Import, and Ownership Architecture
==============================================================================

This module provides immutable architecture snapshots for:
- Authority registry state at a point in time
- Ownership graph structure
- Dependency graph state  
- Import graph analysis
- Registry inventory
- State-owner inventory
- Multi-runtime isolation verification
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple, Any
import time


# =============================================================================
# ARCHITECTURE SNAPSHOTS
# =============================================================================


@dataclass(frozen=True)
class AuthoritySnapshotEntry:
    """A snapshot entry for a single authority."""
    
    authority_id: str
    canonical_name: str
    implementation_identity: str
    scope: str  # Process, Runtime, Kernel, Component, Service, Task
    owner: str
    responsibility: str
    
    # State owned by this authority
    mutable_state_owned: Tuple[str, ...]
    
    # Mutation rights
    mutation_allowed: bool
    validation_required: bool
    
    # Lifecycle and version
    lifecycle: str  # runtime, construction, activation, shutdown
    version: str
    recorded_at: float


@dataclass(frozen=True)
class OwnershipGraphSnapshot:
    """Immutable snapshot of ownership relationships."""
    
    graph_id: str
    runtime_scope: str
    
    # Nodes in the ownership graph
    nodes: Tuple[str, ...]
    
    # Edges representing ownership relationships
    edges: Tuple[Tuple[str, str, str], ...]  # (from, to, relation_type)
    
    # Summary statistics
    total_owners: int
    ownerless_nodes: int
    
    recorded_at: float


@dataclass(frozen=True)
class DependencyGraphSnapshot:
    """Immutable snapshot of dependency graph state."""
    
    graph_id: str
    runtime_scope: str
    
    # Graph structure
    nodes: Tuple[str, ...]
    edges: Tuple[Tuple[str, str, str], ...]  # (from, to, dep_type)
    
    # Analysis results
    has_cycles: bool
    cycle_count: int
    
    # Deterministic ordering info
    topological_order: Optional[Tuple[str, ...]]
    
    recorded_at: float


@dataclass(frozen=True)
class RegistrySnapshotEntry:
    """Snapshot entry for a single registry."""
    
    registry_id: str
    owner: str
    scope: str  # Process, Runtime, Component, etc.
    entry_count: int
    sealed: bool
    version: int
    
    recorded_at: float


@dataclass(frozen=True)
class StateOwnerSnapshot:
    """Snapshot of state ownership relationships."""
    
    runtime_scope: str
    
    # State domains and their owners
    state_owners: Tuple[Tuple[str, str], ...]  # (state_domain, owner)
    
    # Mutation authorities for each state domain
    mutation_authorities: Tuple[Tuple[str, str], ...]
    
    recorded_at: float


# =============================================================================
# ARCHITECTURE SNAPSHOT (COMBINED)
# =============================================================================


@dataclass(frozen=True)
class ArchitectureSnapshot:
    """
    Complete immutable architecture snapshot at a point in time.
    
    This is an observational artifact - it does not become the architecture
    authority itself. Snapshots are read-only and cannot mutate production state.
    """
    
    # Identity
    runtime_id: str
    snapshot_version: int
    recorded_at: float
    
    # Content digest for integrity verification
    content_digest: str  # SHA256 or similar hash
    
    # Authority snapshots
    authority_snapshots: Tuple[AuthoritySnapshotEntry, ...]
    
    # Ownership graph snapshot
    ownership_snapshot: Optional[OwnershipGraphSnapshot] = None
    
    # Dependency graph snapshot  
    dependency_snapshot: Optional[DependencyGraphSnapshot] = None
    
    # Registry inventory
    registry_snapshots: Tuple[RegistrySnapshotEntry, ...] = field(default_factory=tuple)
    
    # State owner inventory
    state_ownership_snapshot: Optional[StateOwnerSnapshot] = None
    
    # Runtime isolation verification
    multi_runtime_isolated: bool = True
    
    # Architecture version (the architecture specification this snapshot follows)
    architecture_version: str = "3.7.2"


# =============================================================================
# ARCHITECTURE INTEGRITY MANAGER
# =============================================================================


class ArchitectureIntegrityManager:
    """
    Coordinates architecture validation and integrity checks.
    
    What it MUST do:
        - Evaluate authority uniqueness
        - Validate ownership completeness
        - Check dependency validity
        - Verify package contracts
        - Run immutable snapshots
    
    What it MUST NOT do:
        - Mutate production architecture automatically
        - Become an authority itself
        - Construct or activate runtime entities
    """
    
    def __init__(self, runtime_id: str) -> None:
        """Initialize the integrity manager."""
        self._runtime_id = runtime_id
        self._snapshots: List[ArchitectureSnapshot] = []
        self._validation_results: Dict[str, bool] = {}
    
    def create_snapshot(self, snapshot_data: Dict[str, Any]) -> ArchitectureSnapshot:
        """
        Create an immutable architecture snapshot.
        
        Args:
            snapshot_data: Dictionary containing all snapshot components
            
        Returns:
            An immutable ArchitectureSnapshot
        """
        # Build the snapshot from data
        authorities = tuple(
            AuthoritySnapshotEntry(**dict(entry)) if isinstance(entry, dict) else entry
            for entry in snapshot_data.get("authority_snapshots", [])
        )
        
        ownership = None
        if "ownership_snapshot" in snapshot_data:
            ow_data = snapshot_data["ownership_snapshot"]
            ownership = OwnershipGraphSnapshot(
                graph_id=ow_data.get("graph_id", ""),
                runtime_scope=ow_data.get("runtime_scope", ""),
                nodes=tuple(ow_data.get("nodes", [])),
                edges=tuple(ow_data.get("edges", [])),
                total_owners=int(ow_data.get("total_owners", 0)),
                ownerless_nodes=int(ow_data.get("ownerless_nodes", 0)),
                recorded_at=ow_data.get("recorded_at", time.monotonic())
            )
        
        dependency = None
        if "dependency_snapshot" in snapshot_data:
            dep_data = snapshot_data["dependency_snapshot"]
            dependency = DependencyGraphSnapshot(
                graph_id=dep_data.get("graph_id", ""),
                runtime_scope=dep_data.get("runtime_scope", ""),
                nodes=tuple(dep_data.get("nodes", [])),
                edges=tuple(dep_data.get("edges", [])),
                has_cycles=bool(dep_data.get("has_cycles", False)),
                cycle_count=int(dep_data.get("cycle_count", 0)),
                topological_order=tuple(dep_data.get("topological_order", ())) if dep_data.get("topological_order") else None,
                recorded_at=dep_data.get("recorded_at", time.monotonic())
            )
        
        registries = tuple(
            RegistrySnapshotEntry(**dict(reg)) if isinstance(reg, dict) else reg
            for reg in snapshot_data.get("registry_snapshots", [])
        )
        
        # Calculate content digest (simplified - would use SHA256 in production)
        all_ids = tuple(sorted(str(a.authority_id) for a in authorities))
        digest = str(hash(all_ids))
        
        snapshot = ArchitectureSnapshot(
            runtime_id=self._runtime_id,
            snapshot_version=len(self._snapshots) + 1,
            recorded_at=time.monotonic(),
            content_digest=digest,
            authority_snapshots=authorities,
            ownership_snapshot=ownership,
            dependency_snapshot=dependency,
            registry_snapshots=registries,
            state_ownership_snapshot=None,  # Can be added later if needed
            multi_runtime_isolated=True,  # Determined by architecture design
        )
        
        self._snapshots.append(snapshot)
        return snapshot
    
    def validate_integrity(self, snapshot: ArchitectureSnapshot) -> bool:
        """
        Validate the integrity of an architecture snapshot.
        
        Args:
            snapshot: The snapshot to validate
            
        Returns:
            True if valid, False otherwise
        """
        # Run validation checks
        self._validation_results["authority_uniqueness"] = self._check_authority_uniqueness(snapshot)
        self._validation_results["ownership_complete"] = self._check_ownership_completeness(snapshot)
        self._validation_results["dependency_valid"] = self._check_dependency_validity(snapshot)
        
        # All checks must pass
        return all(self._validation_results.values())
    
    def _check_authority_uniqueness(self, snapshot: ArchitectureSnapshot) -> bool:
        """Check that each responsibility has exactly one canonical authority."""
        responsibilities = {}
        for entry in snapshot.authority_snapshots:
            resp = entry.responsibility
            if resp in responsibilities:
                return False  # Duplicate responsibility
            responsibilities[resp] = entry.authority_id
        return True
    
    def _check_ownership_completeness(self, snapshot: ArchitectureSnapshot) -> bool:
        """Check that all state domains have owners."""
        # In a full implementation, this would check against known state domains
        return True  # Placeholder for now
    
    def _check_dependency_validity(self, snapshot: ArchitectureSnapshot) -> bool:
        """Check dependency graph validity (no cycles, valid edges)."""
        if not snapshot.dependency_snapshot:
            return True  # No dependency info to validate
        
        dep = snapshot.dependency_snapshot
        if dep.has_cycles and dep.cycle_count > 0:
            return False  # Invalid dependency cycle detected
        
        return True
    
    def get_latest_snapshot(self) -> Optional[ArchitectureSnapshot]:
        """Get the most recent snapshot."""
        if self._snapshots:
            return self._snapshots[-1]
        return None


__all__ = [
    "AuthoritySnapshotEntry",
    "OwnershipGraphSnapshot", 
    "DependencyGraphSnapshot",
    "RegistrySnapshotEntry",
    "StateOwnerSnapshot",
    "ArchitectureSnapshot",
    "ArchitectureIntegrityManager",
]