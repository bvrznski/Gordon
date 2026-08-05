# Migration Manager
# =================

"""
Schema migration, evolution, and compatibility management.

This module provides:
- MigrationManager: Canonical schema-migration authority
- Migration graph for version transitions
- Schema transformation paths
- Compatibility evaluation and validation
- Side-effect-free migration execution

Key principle: Migrations transform stored schemas. They never mutate
source artifacts in place - always produce a new versioned representation.
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any, Callable
from enum import Enum, auto
import uuid
import time


# =============================================================================
# Schema Identifiers
# =============================================================================

@dataclass(frozen=True)
class MigrationId:
    value: str
    
    @classmethod
    def generate(cls) -> "MigrationId":
        return cls(value=str(uuid.uuid4()))
    
    def __str__(self) -> str:
        return self.value


@dataclass(frozen=True)
class SchemaVersion:
    domain: str
    version: int
    
    def __str__(self) -> str:
        return f"{self.domain}:v{self.version}"


# =============================================================================
# Migration Types
# =============================================================================

class MigrationType(Enum):
    ADD_FIELD = "add_field"
    REMOVE_FIELD = "remove_field"
    RENAME_FIELD = "rename_field"
    CHANGE_DEFAULT = "change_default"
    ENUM_CHANGE = "enum_change"
    NUMERIC_WIDENING = "numeric_widening"
    NUMERIC_NARROWING = "numeric_narrowing"
    COLLECTION_CHANGE = "collection_change"
    OPTIONAL_TO_REQUIRED = "optional_to_required"
    REQUIRED_TO_OPTIONAL = "required_to_optional"
    NESTED_SCHEMA_CHANGE = "nested_schema_change"


class MigrationDirection(Enum):
    FORWARD = "forward"  # Old -> New
    BACKWARD = "backward"  # New -> Old


# =============================================================================
# Migration Edge
# =============================================================================

@dataclass(frozen=True)
class MigrationEdge:
    """An edge in the migration graph (one version transition)."""
    
    migration_id: MigrationId
    
    source_version: int
    target_version: int
    
    domain: str
    
    # Implementation details
    implementation_identity: str  # e.g., "module.ClassName"
    deterministic: bool  # Always produces same output for same input
    reversible: bool   # Can we go back to original?
    
    # Validation
    validation_passed: bool = True
    expected_information_loss: float = 0.0  # 0.0 to 1.0
    
    # Provenance
    created_at: float = field(default_factory=time.monotonic)


# =============================================================================
# Migration Graph
# =============================================================================

@dataclass(frozen=True)
class MigrationGraph:
    """A directed graph of migration edges."""
    
    domain: str
    
    # Edges by version pairs: (from, to) -> edge
    edges: Dict[tuple[int, int], MigrationEdge] = field(default_factory=dict)
    
    def add_edge(self, edge: MigrationEdge) -> None:
        """Add a migration edge."""
        key = (edge.source_version, edge.target_version)
        self.edges[key] = edge
    
    def find_path(
        self,
        source_version: int,
        target_version: int
    ) -> Optional[List[MigrationEdge]]:
        """
        Find a path from source to target version.
        
        Returns:
            List of edges forming the path, or None if no path exists
        """
        # Simplified - would use graph traversal algorithm in production
        
        if source_version == target_version:
            return []
        
        # Direct edge check
        direct_key = (source_version, target_version)
        if direct_key in self.edges:
            return [self.edges[direct_key]]
        
        # Try reverse for backward migration
        reverse_key = (target_version, source_version)
        if reverse_key in self.edges and self.edges[reverse_key].reversible:
            return [self.edges[reverse_key]]
        
        # No path found
        return None
    
    def has_cycle(self) -> bool:
        """Check if the graph contains cycles."""
        # Simplified - would use DFS cycle detection in production
        return False
    
    def get_versions(self) -> List[int]:
        """Get all versions in the graph."""
        versions = set()
        for (from_v, to_v) in self.edges.keys():
            versions.add(from_v)
            versions.add(to_v)
        return list(versions)


# =============================================================================
# Migration Request and Result Types
# =============================================================================

@dataclass(frozen=True)
class MigrationRequest:
    request_id: str
    
    domain: str
    source_version: int
    target_version: int
    
    # Input data to migrate
    input_data: Dict[str, Any]
    
    # Options
    dry_run: bool = False  # Validate without writing
    validate_only: bool = False  # Only check if migration is possible


@dataclass(frozen=True)
class MigrationResult:
    result_id: str
    
    request_id: str
    
    status: "MigrationStatus"
    timestamp: float
    
    # Success case
    output_data: Optional[Dict[str, Any]] = None
    used_migrations: List[MigrationEdge] = field(default_factory=list)
    
    # Details
    information_loss: float = 0.0
    transformations_applied: List[str] = field(default_factory=list)
    
    # Failure case
    error_message: Optional[str] = None
    
    @property
    def success(self) -> bool:
        return self.status == MigrationStatus.COMPLETED


class MigrationStatus(Enum):
    REQUESTED = "requested"
    VALIDATING = "validating"
    PLANNING = "planning"
    EXECUTING = "executing"
    COMPLETED = "completed"
    FAILED = "failed"


# =============================================================================
# Compatibility Result
# =============================================================================

@dataclass(frozen=True)
class CompatibilityResult:
    """Result of schema compatibility check."""
    
    is_compatible: bool
    
    # For incompatible schemas, the migration path if available
    migration_path: Optional[List[MigrationEdge]] = None
    
    # Detailed info
    missing_fields: List[str] = field(default_factory=list)
    extra_fields: List[str] = field(default_factory=list)
    type_mismatches: Dict[str, str] = field(default_factory=dict)  # field -> (expected, actual)


# =============================================================================
# Migration Manager
# =============================================================================

class MigrationManager:
    """
    Canonical schema-migration authority.
    
    Manages:
        - Migration graph construction and validation
        - Path selection for version transitions
        - Deterministic migration execution
        - Compatibility evaluation
    
    Usage:
        manager = MigrationManager()
        
        # Register migrations
        manager.register_migration(
            domain="state_a",
            source_version=1,
            target_version=2,
            migration_fn=transform_v1_to_v2,
            deterministic=True,
            reversible=False
        )
        
        # Check compatibility
        compat = manager.check_compatibility("state_a", 1, 3)
        
        if not compat.is_compatible and compat.migration_path:
            # Can migrate via path
            result = await manager.migrate(MigrationRequest(
                request_id=str(uuid.uuid4()),
                domain="state_a",
                source_version=1,
                target_version=3,
                input_data=data_from_v1
            ))
    """
    
    def __init__(self) -> None:
        # Graphs by domain
        self._graphs: Dict[str, MigrationGraph] = {}
        
        # Registry of migration implementations
        self._implementations: Dict[str, Callable[[Dict[str, Any]], Dict[str, Any]]] = {}
        
        # Metrics
        self._migrate_count = 0
    
    def register_migration(
        self,
        domain: str,
        source_version: int,
        target_version: int,
        migration_fn: Callable[[Dict[str, Any]], Dict[str, Any]],
        deterministic: bool = True,
        reversible: bool = False
    ) -> None:
        """Register a migration edge."""
        if domain not in self._graphs:
            self._graphs[domain] = MigrationGraph(domain=domain)
        
        edge = MigrationEdge(
            migration_id=MigrationId.generate(),
            source_version=source_version,
            target_version=target_version,
            domain=domain,
            implementation_identity=f"{migration_fn.__module__}.{migration_fn.__name__}",
            deterministic=deterministic,
            reversible=reversible,
        )
        
        self._graphs[domain].add_edge(edge)
        self._implementations[edge.migration_id.value] = migration_fn
    
    def check_compatibility(
        self,
        domain: str,
        source_version: int,
        target_version: int
    ) -> CompatibilityResult:
        """Check if a version transition is compatible."""
        if domain not in self._graphs:
            return CompatibilityResult(is_compatible=False)
        
        graph = self._graphs[domain]
        
        # Same version - always compatible
        if source_version == target_version:
            return CompatibilityResult(is_compatible=True)
        
        # Check for path
        path = graph.find_path(source_version, target_version)
        
        if not path:
            # No migration path available
            return CompatibilityResult(
                is_compatible=False,
                missing_fields=[],
                extra_fields=[],
                type_mismatches={},
            )
        
        return CompatibilityResult(
            is_compatible=True,
            migration_path=path,
        )
    
    async def migrate(
        self,
        request: MigrationRequest
    ) -> MigrationResult:
        """
        Migrate data from source to target version.
        
        Args:
            request: The migration request
            
        Returns:
            Result with migrated data or error
        """
        if domain := request.domain:
            pass  # Use domain
        
        graph = self._graphs.get(request.domain)
        if not graph:
            return MigrationResult(
                result_id=str(uuid.uuid4()),
                request_id=request.request_id,
                status=MigrationStatus.FAILED,
                timestamp=time.monotonic(),
                error_message=f"No migration graph for domain '{request.domain}'",
            )
        
        # Check compatibility
        compat = self.check_compatibility(
            request.domain,
            request.source_version,
            request.target_version
        )
        
        if not compat.is_compatible:
            return MigrationResult(
                result_id=str(uuid.uuid4()),
                request_id=request.request_id,
                status=MigrationStatus.FAILED,
                timestamp=time.monotonic(),
                error_message=f"No migration path from v{request.source_version} to v{request.target_version}",
            )
        
        # Execute migrations in sequence
        data = dict(request.input_data)
        used_migrations: List[MigrationEdge] = []
        
        for edge in compat.migration_path:
            impl_key = edge.implementation_identity
            
            if impl_key not in self._implementations:
                return MigrationResult(
                    result_id=str(uuid.uuid4()),
                    request_id=request.request_id,
                    status=MigrationStatus.FAILED,
                    timestamp=time.monotonic(),
                    error_message=f"No implementation for migration {edge.migration_id}",
                )
            
            # Apply transformation
            try:
                data = self._implementations[impl_key](data)
                used_migrations.append(edge)
                
                if request.dry_run or request.validate_only:
                    continue
                
            except Exception as e:
                return MigrationResult(
                    result_id=str(uuid.uuid4()),
                    request_id=request.request_id,
                    status=MigrationStatus.FAILED,
                    timestamp=time.monotonic(),
                    error_message=f"Migration failed: {e}",
                )
        
        self._migrate_count += 1
        
        return MigrationResult(
            result_id=str(uuid.uuid4()),
            request_id=request.request_id,
            status=MigrationStatus.COMPLETED,
            timestamp=time.monotonic(),
            output_data=data,
            used_migrations=used_migrations,
            information_loss=0.0,
        )
    
    def get_graph(self, domain: str) -> Optional[MigrationGraph]:
        """Get the migration graph for a domain."""
        return self._graphs.get(domain)
    
    def get_diagnostics(self) -> Dict[str, Any]:
        """Get migration manager diagnostics."""
        return {
            "domains_with_migrations": list(self._graphs.keys()),
            "total_edges": sum(len(g.edges) for g in self._graphs.values()),
            "migrate_count": self._migrate_count,
        }


__all__ = [
    # Identifiers
    "MigrationId",
    "SchemaVersion",
    
    # Types
    "MigrationType",
    "MigrationDirection",
    
    # Edge and graph
    "MigrationEdge",
    "MigrationGraph",
    
    # Request and result types
    "MigrationRequest",
    "MigrationResult",
    "MigrationStatus",
    
    # Compatibility
    "CompatibilityResult",
    
    # Manager
    "MigrationManager",
]