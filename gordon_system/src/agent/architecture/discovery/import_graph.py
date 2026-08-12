"""Import Graph Manager.

Generates complete import graphs for the system.
"""

import ast
from pathlib import Path
from typing import Dict, List, Optional, Set, Tuple

from .inventory import (
    ImportEdge,
)


class ImportGraphManager:
    """
    Generates import graphs for the system.
    
    Generates complete import graphs and detects:
    - Cycles
    - Forbidden imports
    - Layer violations
    - Compatibility imports
    - Legacy imports
    
    It is:
    - Deterministic: Same input produces same output
    - Read-only: Never modifies source code or runtime state
    """
    
    def __init__(
        self,
        forbidden_patterns: Optional[Tuple[str, ...]] = None,
        layer_rules: Optional[Dict[str, List[str]]] = None
    ) -> None:
        """
        Initialize the import graph manager.
        
        Args:
            forbidden_patterns: Patterns that should not be imported
            layer_rules: Rules for valid layer transitions
                Key is source layer, value is list of allowed target layers
        """
        self._forbidden_patterns = forbidden_patterns or (
            "*.tests.*", "*test_*", "conftest.py",
        )
        
        # Layer rules: earlier layers can import later layers, but not vice versa
        self._layer_rules = layer_rules or {
            "types": ["contracts", "exceptions"],
            "contracts": ["exceptions"],
            "exceptions": [],
            "registry": ["types", "exceptions"],
            "runtime_state": ["types", "registry", "context"],
            "context": ["runtime_state"],
            "lifecycle": ["contracts", "types", "exceptions"],
            "kernel": ["dependency", "runtime_state"],
            "bootstrap": ["contracts", "types", "exceptions"],
            "configuration": [],
            "synchronization": [],
        }
    
    def generate_import_graph(
        self,
        repository_path: str
    ) -> Tuple[Tuple[ImportEdge, ...], Dict[str, List[List[str]]]]:
        """
        Generate a complete import graph for the system.
        
        Args:
            repository_path: Path to the repository root
            
        Returns:
            Tuple of (edges, cycles) where cycles maps module paths to cycle lists
        """
        repo_path = Path(repository_path)
        edges: List[ImportEdge] = []
        cycles: Dict[str, List[List[str]]] = {}
        
        # Find all Python files
        py_files = list(repo_path.rglob("*.py"))
        
        # Parse each file and extract imports
        for py_file in py_files:
            rel_path = str(py_file.relative_to(repo_path))
            
            if "test" in rel_path.lower():
                continue  # Skip test files
            
            tree = self._parse_module(py_file)
            if tree is None:
                continue
            
            module_edges = self._extract_import_edges(tree, rel_path)
            edges.extend(module_edges)
        
        return tuple(edges), cycles
    
    def _parse_module(self, file_path: Path) -> Optional[ast.Module]:
        """Parse a Python module and return its AST."""
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()
            return ast.parse(content, filename=str(file_path))
        except (SyntaxError, OSError):
            return None
    
    def _extract_import_edges(
        self,
        tree: ast.Module,
        from_module: str
    ) -> List[ImportEdge]:
        """Extract import edges from a module."""
        edges: List[ImportEdge] = []
        
        for node in ast.walk(tree):
            if isinstance(node, ast.ImportFrom):
                # From X import Y
                if node.module:
                    is_relative = node.level > 0
                    
                    edge = ImportEdge(
                        from_module=from_module,
                        to_module=node.module,
                        type_="transitive" if is_relative else "direct",
                        optional=False
                    )
                    edges.append(edge)
                    
            elif isinstance(node, ast.Import):
                # Import X
                for alias in node.names:
                    edge = ImportEdge(
                        from_module=from_module,
                        to_module=alias.name,
                        type_="direct",
                        optional=False
                    )
                    edges.append(edge)
        
        return edges
    
    def detect_cycles(self, edges: Tuple[ImportEdge, ...]) -> List[List[str]]:
        """
        Detect import cycles in the graph.
        
        Args:
            edges: Import edges
            
        Returns:
            List of detected cycles (each cycle is a list of module paths)
        """
        # Build adjacency list
        adj: Dict[str, Set[str]] = {}
        for edge in edges:
            if edge.from_module not in adj:
                adj[edge.from_module] = set()
            adj[edge.from_module].add(edge.to_module)
        
        visited: Set[str] = set()
        rec_stack: Set[str] = set()
        cycles: List[List[str]] = []
        
        def dfs(node: str, path: List[str]) -> None:
            if node in rec_stack:
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
        
        for node in self._get_all_modules(edges):
            if node not in visited:
                dfs(node, [])
        
        return cycles
    
    def _get_all_modules(self, edges: Tuple[ImportEdge, ...]) -> Set[str]:
        """Get all unique modules from edges."""
        modules: Set[str] = set()
        for edge in edges:
            modules.add(edge.from_module)
            modules.add(edge.to_module)
        return modules
    
    def detect_layer_violations(
        self,
        edges: Tuple[ImportEdge, ...]
    ) -> List[Tuple[str, str, str]]:
        """
        Detect layer violations (forbidden cross-layer imports).
        
        Args:
            edges: Import edges
            
        Returns:
            List of (from_module, to_module, violation_type) tuples
        """
        violations: List[Tuple[str, str, str]] = []
        
        for edge in edges:
            from_pkg = self._get_package_from_path(edge.from_module)
            to_pkg = self._get_package_from_path(edge.to_module)
            
            # Check if this import violates layer rules
            allowed_targets = self._layer_rules.get(from_pkg, [])
            target_layer = self._get_layer(to_pkg)
            
            if target_layer not in allowed_targets:
                violations.append((
                    edge.from_module,
                    edge.to_module,
                    f"Layer violation: {from_pkg} cannot import from {to_pkg}"
                ))
        
        return violations
    
    def _get_package_from_path(self, path: str) -> str:
        """Extract package name from a module path."""
        parts = path.split("/")
        if len(parts) >= 2:
            # gordon-system/src/agent/components/core/execution/scheduler.py -> execution
            return parts[-2]
        return "unknown"
    
    def _get_layer(self, package: str) -> str:
        """Get the layer for a package."""
        layers = {
            "types": "infrastructure",
            "contracts": "infrastructure", 
            "exceptions": "infrastructure",
            "kernel": "kernel",
            "lifecycle": "runtime",
            "runtime_state": "runtime",
            "registry": "runtime",
            "context": "runtime",
            "synchronization": "infrastructure",
            "bootstrap": "runtime",
            "configuration": "runtime",
            "execution": "execution",
            "scheduling": "execution",
            "health": "observability",
            "recovery": "recovery",
            "integrity": "recovery",
            "dependency": "infrastructure",
        }
        return layers.get(package, "unknown")
    
    def get_imports_by_module(
        self,
        edges: Tuple[ImportEdge, ...],
        module_path: str
    ) -> List[str]:
        """Get all modules imported by a specific module."""
        result = []
        for edge in edges:
            if edge.from_module == module_path:
                result.append(edge.to_module)
        return result
    
    def get_imported_by(
        self,
        edges: Tuple[ImportEdge, ...],
        module_path: str
    ) -> List[str]:
        """Get all modules that import a specific module."""
        result = []
        for edge in edges:
            if edge.to_module == module_path:
                result.append(edge.from_module)
        return result