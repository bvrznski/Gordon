"""Runtime Topology Manager.

Constructs and analyzes runtime topology graphs.
"""

from pathlib import Path
from typing import Dict, List, Optional, Set, Tuple

from .inventory import (
    RuntimeAuthority,
    TopologyNode,
    TopologyEdge,
)


class RuntimeTopologyManager:
    """
    Constructs and analyzes runtime topology for the system.
    
    Represents topology using immutable graph models describing:
    - Kernel
    - Runtime services
    - Schedulers
    - Registries
    - Lifecycle participants
    - Resources
    - Communication paths
    - Execution paths
    
    It is:
    - Deterministic: Same input produces same output
    - Read-only: Never modifies runtime state
    """
    
    def __init__(self) -> None:
        """Initialize the runtime topology manager."""
        self._node_cache: Dict[str, TopologyNode] = {}
        self._edge_cache: Dict[Tuple[str, str], List[TopologyEdge]] = {}
    
    def build_runtime_topology(
        self,
        authorities: Tuple[RuntimeAuthority, ...]
    ) -> Tuple[Tuple[TopologyNode, ...], Tuple[TopologyEdge, ...]]:
        """
        Build runtime topology from authority information.
        
        Args:
            authorities: Discovered runtime authorities
            
        Returns:
            Tuple of (nodes, edges) representing the topology
        """
        nodes: List[TopologyNode] = []
        edges: List[TopologyEdge] = []
        
        # Create nodes for each authority
        for auth in authorities:
            node = TopologyNode(
                id=auth.implementation,
                name=auth.name,
                category=auth.category,
                type_="class",
                owner=auth.owner,
                scope=auth.scope,
                lifecycle_state="ready"
            )
            self._node_cache[auth.implementation] = node
            nodes.append(node)
        
        # Create edges based on authority relationships
        for auth in authorities:
            # Authority depends on types
            edges.append(TopologyEdge(
                from_node=auth.implementation,
                to_node="types.EntityId",
                type_="dependency"
            ))
            
            # Add dependency edges based on authority category
            if auth.category == "Recovery":
                edges.append(TopologyEdge(
                    from_node=auth.implementation,
                    to_node="health.HealthAggregator",
                    type_="communication"
                ))
            elif auth.category == "Execution":
                edges.append(TopologyEdge(
                    from_node=auth.implementation,
                    to_node="runtime_state.RuntimeStateStore",
                    type_="dependency"
                ))
        
        # Add kernel node
        kernel_node = TopologyNode(
            id="kernel.Kernel",
            name="Kernel",
            category="Kernel",
            type_="class",
            owner="Runtime Core Team",
            scope="runtime",
            lifecycle_state="ready"
        )
        nodes.append(kernel_node)
        
        # Kernel depends on all authorities
        for node in nodes:
            if node.category != "Kernel":
                edges.append(TopologyEdge(
                    from_node=kernel_node.id,
                    to_node=node.id,
                    type_="coordination"
                ))
        
        return tuple(nodes), tuple(edges)
    
    def discover_runtime_objects(
        self,
        repository_path: str
    ) -> Tuple[Tuple[TopologyNode, ...], Tuple[TopologyEdge, ...]]:
        """
        Discover runtime objects by analyzing class patterns.
        
        Args:
            repository_path: Path to the repository root
            
        Returns:
            Tuple of (nodes, edges)
        """
        nodes: List[TopologyNode] = []
        edges: List[TopologyEdge] = []
        
        repo_path = Path(repository_path)
        
        # Look for known runtime object patterns
        patterns = [
            ("Scheduler", "execution", "Execution"),
            ("Registry", "registry", "Runtime"),
            ("StateStore", "runtime_state", "Runtime State"),
            ("Controller", "lifecycle", "Lifecycle"),
            ("Coordinator", "*", "Various"),
        ]
        
        for py_file in repo_path.rglob("*.py"):
            if "test" in str(py_file):
                continue
            
            # Extract class names from file
            classes = self._extract_classes(py_file)
            
            for class_name, pkg, category in patterns:
                if class_name.lower() in classes:
                    node = TopologyNode(
                        id=f"{pkg}.{class_name}",
                        name=class_name,
                        category=category,
                        type_="class",
                        owner=self._get_owner_for_category(category),
                        scope="runtime"
                    )
                    nodes.append(node)
                    
                    # Add edges to related nodes
                    for existing_node in nodes:
                        if existing_node.id != node.id:
                            edges.append(TopologyEdge(
                                from_node=node.id,
                                to_node=existing_node.id,
                                type_="dependency"
                            ))
        
        return tuple(nodes), tuple(edges)
    
    def _extract_classes(self, file_path: Path) -> Set[str]:
        """Extract class names from a Python file."""
        classes: Set[str] = set()
        
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()
            
            for line in content.split("\n"):
                if line.strip().startswith("class "):
                    parts = line.split()
                    if len(parts) >= 2:
                        class_name = parts[1].split("(")[0]
                        classes.add(class_name)
        except (OSError, UnicodeDecodeError):
            pass
        
        return classes
    
    def _get_owner_for_category(self, category: str) -> str:
        """Get the owner for a topology category."""
        owners = {
            "Kernel": "Runtime Core Team",
            "Runtime State": "Runtime Core Team",
            "Runtime": "Runtime Core Team",
            "Execution": "Execution Team",
            "Lifecycle": "Runtime Core Team",
            "Recovery": "Recovery Team",
            "Observability": "Observability Team",
        }
        return owners.get(category, "Unknown")
    
    def get_nodes_by_category(
        self,
        nodes: Tuple[TopologyNode, ...],
        category: str
    ) -> Tuple[TopologyNode, ...]:
        """Get all nodes in a specific category."""
        return tuple(n for n in nodes if n.category == category)
    
    def get_node_neighbors(
        self,
        edges: Tuple[TopologyEdge, ...],
        node_id: str
    ) -> List[str]:
        """Get all nodes that have an edge to or from the given node."""
        neighbors: Set[str] = set()
        
        for edge in edges:
            if edge.from_node == node_id:
                neighbors.add(edge.to_node)
            elif edge.to_node == node_id:
                neighbors.add(edge.from_node)
        
        return list(neighbors)
    
    def get_path(
        self,
        edges: Tuple[TopologyEdge, ...],
        from_node: str,
        to_node: str
    ) -> Optional[List[str]]:
        """
        Find a path between two nodes.
        
        Uses BFS for shortest path finding.
        
        Args:
            edges: Topology edges
            from_node: Source node ID
            to_node: Target node ID
            
        Returns:
            List of node IDs forming the path, or None if no path exists
        """
        # Build adjacency list
        adj: Dict[str, Set[str]] = {}
        for edge in edges:
            if edge.from_node not in adj:
                adj[edge.from_node] = set()
            adj[edge.from_node].add(edge.to_node)
        
        # BFS
        visited: Set[str] = {from_node}
        queue: List[List[str]] = [[from_node]]
        
        while queue:
            path = queue.pop(0)
            current = path[-1]
            
            if current == to_node:
                return path
            
            for neighbor in adj.get(current, set()):
                if neighbor not in visited:
                    visited.add(neighbor)
                    queue.append(path + [neighbor])
        
        return None