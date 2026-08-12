"""Dependency Discovery Manager.

Discovers and analyzes dependencies between components.
"""

import ast
from pathlib import Path
from typing import Dict, List, Optional, Set, Tuple

from .inventory import (
    DependencyEdge,
    DependencyGraph,
)


class DependencyDiscoveryManager:
    """
    Discovers and catalogs dependencies in the system.
    
    Builds independent graphs for:
    - Package dependencies
    - Runtime dependencies  
    - Construction dependencies
    - Activation dependencies
    - Shutdown dependencies
    
    It is:
    - Deterministic: Same input produces same output
    - Read-only: Never modifies anything
    """
    
    def __init__(self) -> None:
        """Initialize the dependency discovery manager."""
        self._cache: Dict[str, Tuple[DependencyEdge, ...]] = {}
    
    def discover_dependencies(
        self,
        repository_path: str
    ) -> DependencyGraph:
        """
        Discover all dependencies in the system.
        
        Args:
            repository_path: Path to the repository root
            
        Returns:
            DependencyGraph containing all discovered dependencies
        """
        repo_path = Path(repository_path)
        edges: List[DependencyEdge] = []
        
        # Find all Python files and analyze their imports
        for py_file in repo_path.rglob("*.py"):
            rel_path = str(py_file.relative_to(repo_path))
            
            if "test" in rel_path.lower():
                continue  # Skip test files
            
            tree = self._parse_module(py_file)
            if tree is None:
                continue
            
            # Extract imports and add as dependencies
            file_edges = self._extract_dependencies(tree, rel_path)
            edges.extend(file_edges)
        
        return DependencyGraph(edges=tuple(edges))
    
    def _parse_module(self, file_path: Path) -> Optional[ast.Module]:
        """Parse a Python module and return its AST."""
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()
            return ast.parse(content, filename=str(file_path))
        except (SyntaxError, OSError):
            return None
    
    def _extract_dependencies(
        self,
        tree: ast.Module,
        from_module: str
    ) -> List[DependencyEdge]:
        """Extract dependency edges from a module."""
        edges: List[DependencyEdge] = []
        
        for node in ast.walk(tree):
            if isinstance(node, ast.ImportFrom):
                # From X import Y - X is the dependency
                if node.module:
                    dep_name = self._normalize_import_path(node.module)
                    if dep_name and dep_name != from_module:
                        edges.append(DependencyEdge(
                            from_entity=from_module,
                            to_entity=dep_name,
                            type_="runtime",
                            required=True
                        ))
                        
            elif isinstance(node, ast.Import):
                # Import X - X is the dependency
                for alias in node.names:
                    dep_name = self._normalize_import_path(alias.name)
                    if dep_name and dep_name != from_module:
                        edges.append(DependencyEdge(
                            from_entity=from_module,
                            to_entity=dep_name,
                            type_="runtime",
                            required=True
                        ))
        
        return edges
    
    def _normalize_import_path(self, import_path: str) -> Optional[str]:
        """Normalize an import path for comparison."""
        # Remove leading dots (relative imports)
        normalized = import_path.lstrip(".")
        
        # Only track internal imports (gordon.*)
        if normalized.startswith("gordon"):
            return normalized
        
        return None
    
    def build_package_dependency_graph(
        self,
        repository_path: str
    ) -> DependencyGraph:
        """
        Build a graph of package-level dependencies.
        
        This is coarser than module-level dependencies.
        
        Args:
            repository_path: Path to the repository root
            
        Returns:
            Package dependency graph
        """
        edges: List[DependencyEdge] = []
        
        # Extract package names from imports
        pkg_deps: Dict[str, Set[str]] = {}
        
        repo_path = Path(repository_path)
        # Support both gordon_system (current) and gordon-system legacy paths
        gordon_paths = ["src/agent", "gordon_system/src/agent"]
        found = False
        for gordon_path in gordon_paths:
            pattern = f"{gordon_path}/components/**/*.py"
            if any(pattern in str(p) for p in repo_path.rglob("*.py")):
                found = True
                break
        # Use a more flexible pattern that works regardless of repo directory name
        for py_file in repo_path.rglob("**/agent/components/**/*.py"):
            rel_path = str(py_file.relative_to(repo_path))
            
            # Skip test files and the discovery module itself
            if "test" in rel_path.lower() or "discovery" in rel_path:
                continue
            
            tree = self._parse_module(py_file)
            if tree is None:
                continue
            
            # Get package name from path (now using flexible index based on structure)
            parts = rel_path.split("/")
            try:
                # Find the index of "agent/components" to determine correct pkg_name index
                agent_idx = parts.index("agent") if "agent" in parts else -1
                if agent_idx >= 0 and len(parts) > agent_idx + 2:
                    pkg_name = parts[agent_idx + 2]  # component name after agent/components
                else:
                    pkg_name = parts[-2] if len(parts) > 1 else "unknown"
            except (ValueError, IndexError):
                pkg_name = "unknown"
            
            for node in ast.walk(tree):
                if isinstance(node, ast.ImportFrom) and node.module:
                    dep_pkg = self._get_package_from_module(node.module)
                    if dep_pkg and dep_pkg != pkg_name:
                        if pkg_name not in pkg_deps:
                            pkg_deps[pkg_name] = set()
                        pkg_deps[pkg_name].add(dep_pkg)
        
        # Convert to edges
        for from_pkg, deps in pkg_deps.items():
            for to_pkg in deps:
                edges.append(DependencyEdge(
                    from_entity=from_pkg,
                    to_entity=to_pkg,
                    type_="runtime",
                    required=True
                ))
        
        return DependencyGraph(edges=tuple(edges))
    
    def _get_package_from_module(self, module_path: str) -> Optional[str]:
        """Extract package name from a module path."""
        # gordon.system.components.execution.scheduler -> execution
        parts = module_path.split(".")
        
        if len(parts) >= 4 and parts[0] == "gordon":
            return parts[3]
        
        return None
    
    def detect_cycles(
        self,
        graph: DependencyGraph
    ) -> List[List[str]]:
        """
        Detect cycles in a dependency graph.
        
        Uses DFS-based cycle detection.
        
        Args:
            graph: The dependency graph to analyze
            
        Returns:
            List of cycles found (each cycle is a list of nodes)
        """
        # Build adjacency list
        adj: Dict[str, Set[str]] = {}
        for edge in graph.edges:
            if edge.from_entity not in adj:
                adj[edge.from_entity] = set()
            adj[edge.from_entity].add(edge.to_entity)
        
        # DFS-based cycle detection
        visited: Set[str] = set()
        rec_stack: Set[str] = set()
        cycles: List[List[str]] = []
        
        def dfs(node: str, path: List[str]) -> None:
            if node in rec_stack:
                # Found a cycle
                cycle_start = path.index(node)
                cycle = path[cycle_start:] + [node]
                cycles.append(cycle)
                return
            
            if node in visited:
                return
            
            visited.add(node)
            rec_stack.add(node)
            
            for neighbor in adj.get(node, set()):
                dfs(neighbor, path + [node])
            
            rec_stack.remove(node)
        
        for node in graph.vertices:
            if node not in visited:
                dfs(node, [])
        
        return cycles
    
    def topological_sort(
        self,
        graph: DependencyGraph
    ) -> List[str]:
        """
        Perform topological sort on a dependency graph.
        
        Args:
            graph: The dependency graph to sort
            
        Returns:
            List of nodes in topological order (dependencies first)
            
        Raises:
            ValueError: If the graph contains cycles
        """
        # Check for cycles
        cycles = self.detect_cycles(graph)
        if cycles:
            raise ValueError(f"Cannot topologically sort cyclic dependencies: {cycles}")
        
        # Kahn's algorithm
        in_degree: Dict[str, int] = {}
        adj: Dict[str, Set[str]] = {}
        
        for edge in graph.edges:
            if edge.from_entity not in adj:
                adj[edge.from_entity] = set()
            adj[edge.from_entity].add(edge.to_entity)
            
            in_degree.setdefault(edge.from_entity, 0)
            in_degree[edge.to_entity] = in_degree.get(edge.to_entity, 0) + 1
        
        # Initialize with nodes that have no incoming edges
        queue: List[str] = [n for n in graph.vertices if in_degree.get(n, 0) == 0]
        result: List[str] = []
        
        while queue:
            node = queue.pop(0)
            result.append(node)
            
            for neighbor in adj.get(node, set()):
                in_degree[neighbor] -= 1
                if in_degree[neighbor] == 0:
                    queue.append(neighbor)
        
        return result
    
    def discover_dependencies_v2(
        self,
        repository_path: str
    ) -> DependencyGraph:
        """
        Discover all dependencies in the system using flexible path detection.
        
        Args:
            repository_path: Path to the repository root
            
        Returns:
            DependencyGraph containing all discovered dependencies
        """
        repo_path = Path(repository_path)
        edges: List[DependencyEdge] = []
        
        # Find all Python files and analyze their imports
        for py_file in repo_path.rglob("**/*.py"):
            rel_path = str(py_file.relative_to(repo_path))
            
            if "test" in rel_path.lower():
                continue
            
            tree = self._parse_module(py_file)
            if tree is None:
                continue
            
            # Extract module name from path
            file_parts = py_file.with_suffix('').parts
            try:
                # Find agent directory and extract module from there
                agent_idx = next(i for i, p in enumerate(file_parts) if p == "agent")
                module_name = ".".join(file_parts[agent_idx:])
            except (ValueError, StopIteration):
                continue
            
            edges.extend(self._extract_dependencies(tree, module_name))
        
        return DependencyGraph(edges=tuple(edges))
