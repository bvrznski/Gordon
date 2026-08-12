"""Authority Discovery Manager.

Discovers and catalogs runtime authorities in the system.
"""

import ast
from pathlib import Path
from typing import Dict, List, Optional, Set, Tuple

from .inventory import (
    RuntimeAuthority,
    DependencyGraph,
    DependencyEdge,
)


# =============================================================================
# KNOWN AUTHORITY PATTERNS
# =============================================================================


AUTHORITY_PATTERNS = {
    # Kernel authorities
    "Kernel": ("kernel",),

    # Lifecycle authorities  
    "Lifecycle": ("lifecycle",),

    # Runtime state authorities
    "Runtime State": ("runtime_state",),

    # Registry authorities
    "Registry": ("registry",),

    # Runtime context authorities
    "Runtime Context": ("context",),

    # Execution authorities
    "Execution": ("execution",),

    # Scheduling authorities
    "Scheduler": ("scheduling", "scheduler"),

    # Cancellation authorities
    "Cancellation": ("execution",),

    # Shutdown authorities
    "Shutdown": ("shutdown", "runtime_state", "synchronization"),

    # Health authorities
    "Health": ("health",),

    # Integrity authorities
    "Integrity": ("integrity",),

    # Recovery authorities
    "Recovery": ("recovery",),

    # Configuration authorities
    "Configuration": ("configuration",),

    # Dependency authorities
    "Dependency": ("dependency",),
}


class AuthorityDiscoveryManager:
    """
    Discovers and catalogs runtime authorities in the system.

    A runtime authority is a canonical source of responsibility for
    specific aspects of runtime behavior.
    """

    def __init__(self) -> None:
        """Initialize the authority discovery manager."""
        self._authority_cache: Dict[str, Tuple[RuntimeAuthority, ...]] = {}

    def discover_authorities(
        self,
        repository_path: str
    ) -> Tuple[RuntimeAuthority, ...]:
        """
        Discover all runtime authorities in the system.

        This scans for classes and patterns that represent canonical
        authority implementations.

        Args:
            repository_path: Path to the repository root

        Returns:
            Tuple of discovered RuntimeAuthority instances
        """
        repo_path = Path(repository_path)
        authorities: List[RuntimeAuthority] = []

        # Look for authority patterns in key directories (all under core/)
        for category, keywords in AUTHORITY_PATTERNS.items():
            author = self._get_authority_owner(category)

            for pkg_name in keywords:
                pkg_path = repo_path / "src" / "agent" / "components" / "core" / pkg_name

                if not pkg_path.exists():
                    continue

                for py_file in pkg_path.rglob("*.py"):
                    tree = self._parse_module(py_file)
                    if tree is None:
                        continue

                    # Find authority classes
                    for class_def in self._find_authority_classes(tree, category):
                        authorities.append(RuntimeAuthority(
                            name=class_def.name,
                            category=category,
                            implementation=f"gordon.system.components.core.{pkg_name}.{class_def.name}",
                            owner=author,
                            public_interface=self._get_public_interface(class_def),
                            dependencies=set(),
                            optional_dependencies=set(),
                            scope="runtime",
                            version="1.0.0"
                        ))

        return tuple(authorities)

    def _parse_module(self, file_path: Path) -> Optional[ast.Module]:
        """Parse a Python module and return its AST."""
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()
            return ast.parse(content, filename=str(file_path))
        except (SyntaxError, OSError):
            return None

    def _find_authority_classes(
        self,
        tree: ast.Module,
        category: str
    ) -> List[ast.ClassDef]:
        """Find authority classes in a module."""
        authorities: List[ast.ClassDef] = []

        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef):
                # Check class name patterns
                name_lower = node.name.lower()

                is_authority = (
                    "authority" in name_lower or
                    "controller" in name_lower or
                    "store" in name_lower or
                    "registry" in name_lower or
                    "coordinator" in name_lower or
                    "manager" in name_lower or
                    node.name.endswith("State") or
                    node.name.endswith("Controller") or
                    node.name.endswith("Registry")
                )

                if is_authority:
                    authorities.append(node)

        return authorities

    def _get_public_interface(self, class_def: ast.ClassDef) -> Tuple[str, ...]:
        """Get the public interface methods of a class."""
        interface: List[str] = []

        for item in class_def.body:
            if isinstance(item, ast.AsyncFunctionDef):
                name = item.name
                # Public async method
                if not name.startswith("_"):
                    interface.append(name)
            elif isinstance(item, ast.FunctionDef):
                name = item.name
                # Public sync method
                if not name.startswith("_"):
                    interface.append(name)

        return tuple(interface)

    def _get_authority_owner(self, category: str) -> str:
        """Get the owner for an authority category."""
        owners = {
            "Kernel": "Runtime Core Team",
            "Lifecycle": "Runtime Core Team",
            "Runtime State": "Runtime Core Team",
            "Registry": "Runtime Core Team",
            "Runtime Context": "Runtime Core Team",
            "Execution": "Execution Team",
            "Scheduler": "Execution Team",
            "Cancellation": "Execution Team",
            "Shutdown": "Runtime Core Team",
            "Health": "Observability Team",
            "Integrity": "Recovery Team",
            "Recovery": "Recovery Team",
            "Configuration": "Core Infrastructure Team",
            "Dependency": "Core Infrastructure Team",
        }
        return owners.get(category, "Unknown")

    def build_dependency_graph(
        self,
        authorities: Tuple[RuntimeAuthority, ...]
    ) -> DependencyGraph:
        """
        Build a dependency graph from authority information.

        Args:
            authorities: Discovered authorities

        Returns:
            DependencyGraph representing authority relationships
        """
        edges: List[DependencyEdge] = []

        for auth in authorities:
            # Each authority has implicit dependencies on types and exceptions
            edges.append(DependencyEdge(
                from_entity=auth.implementation,
                to_entity="types.EntityId",
                type_="runtime"
            ))

            # Add optional dependencies based on category
            if auth.category == "Recovery":
                edges.append(DependencyEdge(
                    from_entity=auth.implementation,
                    to_entity="health.HealthAggregator",
                    type_="optional"
                ))
            elif auth.category == "Execution":
                edges.append(DependencyEdge(
                    from_entity=auth.implementation,
                    to_entity="runtime_state.RuntimeStateStore",
                    type_="runtime"
                ))

        return DependencyGraph(edges=tuple(edges))

    def get_authorities_by_category(
        self,
        authorities: Tuple[RuntimeAuthority, ...],
        category: str
    ) -> Tuple[RuntimeAuthority, ...]:
        """Get all authorities in a specific category."""
        return tuple(a for a in authorities if a.category == category)