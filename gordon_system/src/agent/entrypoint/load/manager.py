"""Gordon Agent Loading Manager.

Phase 3.7.31-I: Agent Component Loading Architecture
====================================================

Canonical component loading coordinator - the one canonical authority for
loading operations.
"""

from __future__ import annotations

import asyncio
import hashlib
import inspect
import os
import time
import uuid
from dataclasses import dataclass, field
from pathlib import Path
from typing import (
    Any,
    Callable,
    Dict,
    FrozenSet,
    List,
    Optional,
    Set,
    Tuple,
)

from .types import (
    AgentLoadRequest,
    LoadDescriptor,
    LoadDescriptorSet,
    LoadPlan,
    LoadPhase,
    ComponentKind,
    DependencyDeclaration,
    CapabilityDeclaration,
)
from .exceptions import (
    AgentLoadError,
    DescriptorDiscoveryError,
    DescriptorValidationError,
    DuplicateComponentError,
    MissingDependencyError,
    DependencyCycleError,
    AmbiguousCapabilityProviderError,
    LoadPlanError,
    StaleLoadPlanError,
    ComponentConstructionError,
)

import copy


# =============================================================================
# LOAD OPERATION IDENTITY
# =============================================================================


@dataclass(frozen=True)
class LoadOperationIdentity:
    """Unique identifiers for a single load operation."""
    
    request_id: str
    """Load request ID."""
    
    descriptor_set_id: Optional[str] = None
    dependency_graph_id: Optional[str] = None
    capability_resolution_id: Optional[str] = None
    load_plan_id: Optional[str] = None
    
    @classmethod
    def create(cls, request_id: str) -> "LoadOperationIdentity":
        return cls(request_id=request_id)


# =============================================================================
# DEPENDENCY GRAPH
# =============================================================================


@dataclass(frozen=True)
class DependencyEdge:
    """Edge in the dependency graph."""
    
    source: str
    target: str
    edge_type: str = "required"


@dataclass(frozen=True)
class DependencyGraph:
    """Immutable dependency graph for a load operation."""
    
    graph_id: str
    nodes: FrozenSet[str]
    edges: Tuple[DependencyEdge, ...]
    
    @property
    def node_count(self) -> int:
        return len(self.nodes)
    
    @property
    def edge_count(self) -> int:
        return len(self.edges)


# =============================================================================
# CAPABILITY RESOLUTION RESULT
# =============================================================================


@dataclass(frozen=True)
class CapabilityProviderSelection:
    """Resolved provider selection for a capability."""
    
    capability_id: str
    provider_component_id: str
    version: str = "1.0.0"
    
    @classmethod
    def create(cls, capability_id: str, provider_component_id: str,
               version: str = "1.0.0") -> "CapabilityProviderSelection":
        return cls(capability_id=capability_id,
                   provider_component_id=provider_component_id,
                   version=version)


# =============================================================================
# COMPONENT CONSTRUCTION RESULT
# =============================================================================


@dataclass(frozen=True)
class ComponentConstructionResult:
    """Result of constructing one component."""
    
    sequence_number: int
    component_id: str
    runtime_identity: Optional[str] = None
    constructor_reference: Optional[Any] = None
    dependencies_resolved: Tuple[str, ...] = field(default_factory=tuple)
    rollback_registration_id: Optional[str] = None
    optional_outcome: Optional[str] = None
    error_message: Optional[str] = None
    
    @property
    def is_success(self) -> bool:
        return self.error_message is None and self.optional_outcome is None
    
    @property
    def is_optional_skipped(self) -> bool:
        return self.optional_outcome is not None and "skipped" in str(self.optional_outcome).lower()
    
    @property
    def needs_rollback(self) -> bool:
        """Check if this component needs rollback on failure."""
        return self.rollback_registration_id is not None
    
    @property
    def has_error(self) -> bool:
        """Check if this construction resulted in an error."""
        return self.error_message is not None or self.optional_outcome is not None


# =============================================================================
# AGENT LOAD RESULT
# =============================================================================


@dataclass(frozen=True)
class AgentLoadResult:
    """Immutable result of a loading operation."""
    
    load_id: str
    request_id: str
    descriptor_set_id: str
    dependency_graph_id: str
    capability_resolution_id: str
    load_plan_id: str
    configuration_fingerprint: str
    start_time_ns: int
    end_time_ns: Optional[int]
    total_duration_seconds: float
    component_results: Tuple[ComponentConstructionResult, ...]
    required_components_loaded: int
    optional_components_skipped: int
    optional_components_failed: int
    lazy_components_deferred: int
    primary_failure: Optional[str]
    secondary_failures: Tuple[str, ...]
    partial_construction_summary: str
    rollback_status: str
    residual_resources: Tuple[str, ...]
    operational_interface_available: bool
    degraded_restrictions: Tuple[str, ...]
    
    @property
    def is_success(self) -> bool:
        return (self.primary_failure is None and
                self.required_components_loaded > 0)
    
    @property
    def has_failures(self) -> bool:
        return self.primary_failure is not None
    
    @classmethod
    def create(cls, load_id: str, request_id: str, descriptor_set_id: str,
               dependency_graph_id: str, capability_resolution_id: str,
               load_plan_id: str, configuration_fingerprint: str,
               component_results: Tuple[ComponentConstructionResult, ...],
               start_time_ns: int, end_time_ns: Optional[int] = None,
               primary_failure: Optional[str] = None,
               secondary_failures: Optional[Tuple[str, ...]] = None) -> "AgentLoadResult":
        now_ns = int(time.time() * 1_000_000_000) if end_time_ns is None else end_time_ns
        duration_seconds = (now_ns - start_time_ns) / 1_000_000_000
        
        success_count = sum(1 for r in component_results if r.is_success)
        optional_skipped = sum(
            1 for r in component_results
            if r.optional_outcome is not None and "skipped" in str(r.optional_outcome).lower()
        )
        
        return cls(
            load_id=load_id, request_id=request_id,
            descriptor_set_id=descriptor_set_id,
            dependency_graph_id=dependency_graph_id,
            capability_resolution_id=capability_resolution_id,
            load_plan_id=load_plan_id,
            configuration_fingerprint=configuration_fingerprint,
            start_time_ns=start_time_ns, end_time_ns=end_time_ns,
            total_duration_seconds=duration_seconds,
            component_results=component_results,
            required_components_loaded=success_count - optional_skipped,
            optional_components_skipped=optional_skipped,
            optional_components_failed=sum(1 for r in component_results
                                          if r.error_message is not None and r.is_optional_skipped),
            lazy_components_deferred=0,
            primary_failure=primary_failure,
            secondary_failures=secondary_failures or (),
            partial_construction_summary=f"{success_count} components loaded" if success_count > 0 else "none",
            rollback_status="not_needed" if primary_failure is None else "in_progress",
            residual_resources=(),
            operational_interface_available=success_count > 0,
            degraded_restrictions=tuple(["some optional components were unavailable"] if optional_skipped > 0 else []),
        )
    
    @classmethod
    def success(cls, load_id: str, request_id: str, descriptor_set_id: str,
                dependency_graph_id: str, capability_resolution_id: str,
                load_plan_id: str, configuration_fingerprint: str,
                component_results: Tuple[ComponentConstructionResult, ...],
                start_time_ns: int) -> "AgentLoadResult":
        return cls.create(load_id=load_id, request_id=request_id,
                         descriptor_set_id=descriptor_set_id,
                         dependency_graph_id=dependency_graph_id,
                         capability_resolution_id=capability_resolution_id,
                         load_plan_id=load_plan_id,
                         configuration_fingerprint=configuration_fingerprint,
                         component_results=component_results,
                         start_time_ns=start_time_ns,
                         end_time_ns=int(time.time() * 1_000_000_000))
    
    @classmethod
    def failure(cls, load_id: str, request_id: str, descriptor_set_id: str,
                dependency_graph_id: str, capability_resolution_id: str,
                load_plan_id: str, configuration_fingerprint: str,
                component_results: Tuple[ComponentConstructionResult, ...],
                primary_failure: str, secondary_failures: Optional[Tuple[str, ...]] = None,
                start_time_ns: int = 0) -> "AgentLoadResult":
        return cls.create(load_id=load_id, request_id=request_id,
                         descriptor_set_id=descriptor_set_id,
                         dependency_graph_id=dependency_graph_id,
                         capability_resolution_id=capability_resolution_id,
                         load_plan_id=load_plan_id,
                         configuration_fingerprint=configuration_fingerprint,
                         component_results=component_results,
                         start_time_ns=start_time_ns,
                         primary_failure=primary_failure,
                         secondary_failures=secondary_failures)


# =============================================================================
# CANONICAL LOADER IMPLEMENTATION
# =============================================================================


class AgentLoadManager:
    """Canonical Agent loading authority."""
    
    DEFAULT_SEARCH_ROOTS: Tuple[str, ...] = ("src/agent/components",)
    ALLOWED_IMPORT_PREFIXES: Tuple[str, ...] = (
        "src.agent.components.",
        "gordon.system.src.agent.components.",
    )
    
    def __init__(self,
                 search_roots: Optional[Tuple[str, ...]] = None,
                 allowed_prefixes: Optional[Tuple[str, ...]] = None,
                 clock: Optional[Callable[[], int]] = None,
                 uuid_generator: Optional[Callable[[], str]] = None):
        self._search_roots = search_roots or self.DEFAULT_SEARCH_ROOTS
        self._allowed_prefixes = allowed_prefixes or self.ALLOWED_IMPORT_PREFIXES
        self._clock = clock or (lambda: int(time.time() * 1_000_000_000))
        self._uuid_generator = uuid_generator or (lambda: str(uuid.uuid4()))
    
    async def load_components(self, request: AgentLoadRequest) -> AgentLoadResult:
        """Load components according to the plan."""
        start_ns = self._clock()
        load_id = f"load_{request.plan_id}_{self._uuid_generator()[:8]}"
        
        try:
            descriptor_set = await self._discover_descriptors(
                load_id=load_id,
                search_roots=self._search_roots,
                included_packages=request.included_packages or frozenset(),
                excluded_packages=request.excluded_packages or frozenset(),
            )
            
            operation_identity = LoadOperationIdentity.create(request.plan_id)
            operation_identity.descriptor_set_id = descriptor_set.set_id
            
            dep_graph = self._build_dependency_graph(descriptor_set)
            operation_identity.dependency_graph_id = f"graph_{dep_graph.graph_id[:8]}"
            
            # Detect cycles before generating load plan
            cycle_path = self._detect_cycle_in_graph(dep_graph)
            if cycle_path:
                raise DependencyCycleError(
                    load_id=load_id,
                    message=f"Dependency cycle detected: {' -> '.join(cycle_path)}",
                    edge_types=["required"],
                    cycle_path=list(cycle_path))
            
            provider_selections = await self._resolve_capabilities(
                load_id=load_id, descriptors=descriptor_set.descriptors)
            operation_identity.capability_resolution_id = f"capability_{uuid.uuid4().hex[:8]}"
            
            load_plan = await self._generate_load_plan(
                load_id=load_id, descriptor_set=descriptor_set,
                dependency_graph=dep_graph,
                capability_selections=provider_selections,
                config_fingerprint=request.config_fingerprint)
            operation_identity.load_plan_id = load_plan.plan_id
            
            validated_plan = await self._validate_and_freeze_plan(
                load_id=load_id, plan=load_plan, descriptor_set=descriptor_set)
            
            results, primary_failure = await self._execute_load_plan(
                load_id=load_id, plan=validated_plan,
                config_fingerprint=request.config_fingerprint)
            
            if primary_failure:
                return AgentLoadResult.failure(
                    load_id=load_id, request_id=request.plan_id,
                    descriptor_set_id=descriptor_set.set_id,
                    dependency_graph_id=dep_graph.graph_id,
                    capability_resolution_id=operation_identity.capability_resolution_id,
                    load_plan_id=validated_plan.plan_id,
                    configuration_fingerprint=request.config_fingerprint,
                    component_results=tuple(results),
                    primary_failure=primary_failure, start_time_ns=start_ns)
            
            return AgentLoadResult.success(
                load_id=load_id, request_id=request.plan_id,
                descriptor_set_id=descriptor_set.set_id,
                dependency_graph_id=dep_graph.graph_id,
                capability_resolution_id=operation_identity.capability_resolution_id,
                load_plan_id=validated_plan.plan_id,
                configuration_fingerprint=request.config_fingerprint,
                component_results=tuple(results),
                start_time_ns=start_ns)
        
        except AgentLoadError as e:
            return AgentLoadResult.failure(
                load_id=load_id if 'load_id' in dir() else "unknown",
                request_id=request.plan_id, descriptor_set_id="not_generated",
                dependency_graph_id="not_generated",
                capability_resolution_id="not_generated",
                load_plan_id="not_generated",
                configuration_fingerprint=request.config_fingerprint,
                component_results=(), primary_failure=str(e),
                start_time_ns=start_ns)
    
    async def request_load_plan(self, launch_id: str, config_fingerprint: str) -> LoadPlan:
        """Request a load plan for the given configuration."""
        return LoadPlan.create(
            request_id=f"plan_{launch_id}",
            descriptor_set_id="unknown",
            dependency_graph_id="unknown",
            capability_resolution_id="unknown",
            configuration_fingerprint=config_fingerprint,
            phases=tuple(LoadPhase),
            entries=())
    
    async def _discover_descriptors(self, load_id: str, search_roots: Tuple[str, ...],
                                    included_packages: FrozenSet[str],
                                    excluded_packages: FrozenSet[str]) -> LoadDescriptorSet:
        """Discover and extract descriptors from __load__.py files."""
        descriptors: List[LoadDescriptor] = []
        
        for root in search_roots:
            if not os.path.exists(root):
                continue
            for dirpath, _, filenames in os.walk(root):
                if "__load__.py" in filenames:
                    load_file = Path(dirpath) / "__load__.py"
                    try:
                        component_id = self._extract_component_id(load_file)
                        desc = LoadDescriptor(
                            schema_version="1.0.0", component_id=component_id,
                            component_kind=ComponentKind.SERVICE,
                            package_id=f"src.agent.components.{component_id}",
                            implementation_path=f"src.agent.components.{component_id}.impl",
                            load_phase=LoadPhase.RUNTIME_INFRASTRUCTURE)
                        descriptors.append(desc)
                    except Exception:
                        continue
        
        return LoadDescriptorSet.create(
            request_id=load_id, source_roots=search_roots,
            descriptors=tuple(descriptors))
    
    def _extract_component_id(self, file_path: Path) -> str:
        """Extract component ID from a __load__.py path."""
        return file_path.parent.name.replace("_", "-")
    
    def _build_dependency_graph(self, descriptor_set: LoadDescriptorSet) -> DependencyGraph:
        """Build dependency graph from descriptors."""
        nodes = frozenset(desc.component_id for desc in descriptor_set.descriptors)
        
        edges: List[DependencyEdge] = []
        for desc in descriptor_set.descriptors:
            for dep in desc.required_dependencies:
                if dep.target in nodes:
                    edges.append(DependencyEdge(source=desc.component_id,
                                               target=dep.target, edge_type="required"))
            for dep in desc.optional_dependencies:
                if dep.target in nodes:
                    edges.append(DependencyEdge(source=desc.component_id,
                                               target=dep.target, edge_type="optional"))
        
        graph_id = f"graph_{hashlib.sha256(str(edges).encode()).hexdigest()[:16]}"
        return DependencyGraph(graph_id=graph_id, nodes=nodes, edges=tuple(edges))
    
    def _detect_cycle_in_graph(self, graph: DependencyGraph) -> Optional[Tuple[str, ...]]:
        """
        Detect cycles in the dependency graph using Kahn's algorithm.
        
        Returns a cycle path if found, None otherwise.
        Uses topological sort with DFS-based cycle detection.
        """
        nodes_set = set(graph.nodes)
        # Build adjacency list
        adj: Dict[str, List[str]] = {node: [] for node in nodes_set}
        in_degree: Dict[str, int] = {node: 0 for node in nodes_set}
        
        for edge in graph.edges:
            if edge.source in adj and edge.target in adj:
                adj[edge.source].append(edge.target)
                in_degree[edge.target] += 1
        
        # Kahn's algorithm with cycle detection
        queue = [node for node in nodes_set if in_degree[node] == 0]
        visited_count = 0
        visited_order: List[str] = []
        
        while queue:
            node = queue.pop(0)
            visited_order.append(node)
            visited_count += 1
            
            for neighbor in adj[node]:
                in_degree[neighbor] -= 1
                if in_degree[neighbor] == 0:
                    queue.append(neighbor)
        
        # If we didn't visit all nodes, there's a cycle
        if visited_count != len(nodes_set):
            # Find the cycle using DFS
            return self._find_cycle_dfs(graph)
        
        return None
    
    def _find_cycle_dfs(self, graph: DependencyGraph) -> Tuple[str, ...]:
        """
        Find and return a cycle in the dependency graph.
        
        Returns an ordered tuple of node IDs forming a cycle.
        Uses DFS with recursion stack to detect back edges.
        """
        nodes_set = set(graph.nodes)
        adj: Dict[str, List[str]] = {node: [] for node in nodes_set}
        
        for edge in graph.edges:
            if edge.source in adj and edge.target in adj:
                adj[edge.source].append(edge.target)
        
        visited: Set[str] = set()
        rec_stack: Set[str] = set()
        parent: Dict[str, Optional[str]] = {node: None for node in nodes_set}
        
        def dfs(node: str) -> Optional[List[str]]:
            visited.add(node)
            rec_stack.add(node)
            
            for neighbor in adj[node]:
                if neighbor not in visited:
                    parent[neighbor] = node
                    cycle_path = dfs(neighbor)
                    if cycle_path is not None:
                        return cycle_path
                elif neighbor in rec_stack:
                    # Found a back edge - extract the cycle
                    cycle: List[str] = [neighbor]
                    current = node
                    while current != neighbor:
                        cycle.append(current)
                        current = parent.get(current)
                        if current is None:
                            break
                    cycle.append(neighbor)
                    return list(reversed(cycle))
            
            rec_stack.remove(node)
            return None
        
        for node in nodes_set:
            if node not in visited:
                result = dfs(node)
                if result is not None:
                    return tuple(result)
        
        # Fallback: return empty tuple if no cycle found
        return ()
    
    async def _resolve_capabilities(self, load_id: str,
                                    descriptors: Tuple[LoadDescriptor, ...]) -> Tuple[CapabilityProviderSelection, ...]:
        """Resolve required capabilities to providers."""
        capability_providers: Dict[str, List[LoadDescriptor]] = {}
        
        for desc in descriptors:
            for cap in desc.provided_capabilities:
                if cap.name not in capability_providers:
                    capability_providers[cap.name] = []
                capability_providers[cap.name].append(desc)
        
        selections: List[CapabilityProviderSelection] = []
        for cap_name, providers in capability_providers.items():
            if len(providers) == 0:
                continue
            sorted_providers = sorted(providers,
                                      key=lambda d: getattr(d, 'priority', 0), reverse=True)
            provider = sorted_providers[0]
            selections.append(CapabilityProviderSelection.create(
                capability_id=cap_name, provider_component_id=provider.component_id,
                version=getattr(provider, 'version', '1.0.0')))
        
        return tuple(selections)
    
    async def _generate_load_plan(self, load_id: str, descriptor_set: LoadDescriptorSet,
                                  dependency_graph: DependencyGraph,
                                  capability_selections: Tuple[CapabilityProviderSelection, ...],
                                  config_fingerprint: str) -> LoadPlan:
        """Generate deterministic load plan."""
        entries: List[LoadPlanEntry] = []
        
        for i, desc in enumerate(descriptor_set.descriptors):
            dep_ids = tuple(e.target for e in dependency_graph.edges
                           if e.source == desc.component_id and e.edge_type == "required")
            
            entry = LoadPlanEntry(
                sequence_number=i, component_id=desc.component_id,
                component_kind=desc.component_kind, phase=desc.load_phase,
                priority=desc.priority, dependency_ids=dep_ids,
                required_capability_providers=frozenset(),
                implementation_path=desc.implementation_path,
                factory_path=desc.factory_path,
                configuration_projection=None,
                runtime_scope=desc.runtime_scope,
                lifecycle_scope=desc.lifecycle_scope,
                required=desc.required, eager=desc.eager,
                rollback_contract=desc.rollback_contract)
            entries.append(entry)
        
        phases_in_order = tuple(LoadPhase)
        entries.sort(key=lambda e: (
            phases_in_order.index(e.phase) if e.phase in phases_in_order else 999,
            -e.priority, e.component_id))
        
        for i, entry in enumerate(entries):
            entries[i] = dataclass_replace(entry, sequence_number=i)
        
        required_ids = frozenset(e.component_id for e in entries if e.required)
        optional_ids = frozenset(e.component_id for e in entries if not e.required)
        
        plan_fingerprint = hashlib.sha256(
            str(tuple(e.component_id for e in entries)).encode()).hexdigest()[:16]
        
        return LoadPlan.create(
            request_id=load_id, descriptor_set_id=descriptor_set.set_id,
            dependency_graph_id=dependency_graph.graph_id,
            capability_resolution_id=f"capability_{uuid.uuid4().hex[:8]}",
            configuration_fingerprint=config_fingerprint,
            phases=tuple(LoadPhase), entries=tuple(entries),
            required_components=required_ids, optional_components=optional_ids,
            fingerprint=plan_fingerprint)
    
    async def _validate_and_freeze_plan(self, load_id: str, plan: LoadPlan,
                                        descriptor_set: LoadDescriptorSet) -> LoadPlan:
        """Validate and freeze a load plan."""
        seen_ids = set()
        for entry in plan.entries:
            if entry.component_id in seen_ids:
                raise LoadPlanError(load_id=load_id,
                                   message=f"Duplicate component ID in plan: {entry.component_id}")
            seen_ids.add(entry.component_id)
        
        # Verify fingerprint before freezing
        if not plan.fingerprint or len(plan.fingerprint) != 16:
            raise LoadPlanError(
                load_id=load_id,
                message="Load plan fingerprint not computed or invalid")
        
        for entry in plan.entries:
            for dep_id in entry.dependency_ids:
                if dep_id not in seen_ids and dep_id not in plan.required_components:
                    raise MissingDependencyError(
                        load_id=load_id, message=f"Missing dependency: {dep_id}",
                        missing_id=dep_id, depending_component=entry.component_id)
        
        return plan
    
    async def _execute_load_plan(self, load_id: str, plan: LoadPlan,
                                 config_fingerprint: str) -> Tuple[Tuple[ComponentConstructionResult, ...], Optional[str]]:
        """Execute the load plan."""
        results: List[ComponentConstructionResult] = []
        
        for entry in plan.entries:
            try:
                impl_ref = self._import_implementation(load_id=load_id,
                                                      path=entry.implementation_path)
                constructor_result = self._construct_component(
                    load_id=load_id, entry=entry,
                    implementation_ref=impl_ref,
                    config_fingerprint=config_fingerprint)
                results.append(constructor_result)
            except Exception as e:
                if entry.required:
                    return (tuple(results), f"Required component '{entry.component_id}' failed: {e}")
                else:
                    results.append(ComponentConstructionResult(
                        sequence_number=entry.sequence_number, component_id=entry.component_id,
                        optional_outcome="skipped", error_message=str(e)))
        
        return tuple(results), None
    
    def _import_implementation(self, load_id: str, path: str) -> Optional[Any]:
        """Import implementation module."""
        return None  # Placeholder
    
    def _construct_component(self, load_id: str, entry: LoadPlanEntry,
                            implementation_ref: Optional[Any],
                            config_fingerprint: str) -> ComponentConstructionResult:
        """Construct a component instance."""
        return ComponentConstructionResult(
            sequence_number=entry.sequence_number,
            component_id=entry.component_id,
            runtime_identity=f"runtime_{entry.component_id}_{uuid.uuid4().hex[:8]}",
            constructor_reference=None, dependencies_resolved=entry.dependency_ids)


# =============================================================================
# HELPER FUNCTIONS
# =============================================================================


def dataclass_replace(instance: Any, **kwargs) -> Any:
    """Replace fields in a frozen dataclass."""
    import copy
    new_instance = copy.copy(instance)
    for key, value in kwargs.items():
        object.__setattr__(new_instance, key, value)
    return new_instance


# =============================================================================
# EXPORTS
# =============================================================================

__all__ = [
    "LoadOperationIdentity", "DependencyEdge", "DependencyGraph",
    "CapabilityProviderSelection", "ComponentConstructionResult",
    "AgentLoadResult", "AgentLoadManager"]
