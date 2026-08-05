"""Module Discovery Manager.

Discovers and analyzes modules within packages.
"""

import ast
from pathlib import Path
from typing import Dict, List, Optional, Set, Tuple

from .inventory import (
    ModuleMetadata,
    PackageMetadata,
    APIType,
    LifecycleParticipation,
)


class ModuleDiscoveryManager:
    """
    Discovers and analyzes modules within packages.

    This manager parses Python source files to extract:
    - Classes, functions, protocols
    - Imports and exports
    - Runtime participation info

    It is:
    - Deterministic: Same input produces same output
    - Repository-driven: Only reads files from disk
    - Read-only: Never modifies anything
    """

    def __init__(self) -> None:
        """Initialize the module discovery manager."""
        self._cache: Dict[str, ast.Module] = {}

    def parse_module(self, file_path: Path) -> Optional[ast.Module]:
        """
        Parse a Python module and return its AST.

        Args:
            file_path: Path to the Python file

        Returns:
            AST of the module, or None if parsing fails
        """
        key = str(file_path)
        if key in self._cache:
            return self._cache[key]

        try:
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()

            tree = ast.parse(content, filename=str(file_path))
            self._cache[key] = tree
            return tree

        except (SyntaxError, OSError):
            return None

    def extract_api_items(self, tree: ast.Module) -> Tuple[Set[str], Set[str]]:
        """
        Extract public and private API items from a module.

        Args:
            tree: AST of the module

        Returns:
            Tuple of (public_api_set, private_api_set)
        """
        public_api: Set[str] = set()
        private_api: Set[str] = set()

        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef):
                name = node.name
                if self._is_exported(tree, name):
                    public_api.add(name)
                else:
                    private_api.add(name)

            elif isinstance(node, ast.FunctionDef):
                name = node.name
                if self._is_exported(tree, name):
                    public_api.add(name)
                else:
                    private_api.add(name)

            elif isinstance(node, ast.Assign):
                for target in node.targets:
                    if isinstance(target, ast.Name):
                        name = target.id
                        if not name.startswith("_"):
                            public_api.add(name)

        return public_api, private_api

    def _is_exported(self, tree: ast.Module, name: str) -> bool:
        """Check if a symbol is exported via __all__."""
        for node in ast.walk(tree):
            if isinstance(node, ast.Assign):
                for target in node.targets:
                    if isinstance(target, ast.Name) and target.id == "__all__":
                        if isinstance(node.value, ast.List):
                            for elt in node.value.elts:
                                if isinstance(elt, ast.Constant) and elt.value == name:
                                    return True
        return False

    def extract_imports(self, tree: ast.Module) -> Tuple[Set[str], Set[str]]:
        """
        Extract import relationships from a module.

        Args:
            tree: AST of the module

        Returns:
            Tuple of (internal_imports, external_imports)
        """
        internal: Set[str] = set()
        external: Set[str] = set()

        for node in ast.walk(tree):
            if isinstance(node, ast.ImportFrom):
                if node.module:
                    if node.level > 0:
                        internal.add(f".{node.module}")
                    else:
                        parts = node.module.split(".")
                        if len(parts) > 1 and parts[0] == "gordon":
                            internal.add(node.module)
                        else:
                            external.add(node.module)
            elif isinstance(node, ast.Import):
                for alias in node.names:
                    name = alias.name
                    parts = name.split(".")
                    if parts[0] == "gordon":
                        internal.add(name)
                    else:
                        external.add(name)

        return internal, external

    def extract_classes(self, tree: ast.Module) -> Set[str]:
        """Extract all class names from a module."""
        classes: Set[str] = set()
        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef):
                classes.add(node.name)
        return classes

    def extract_functions(self, tree: ast.Module) -> Set[str]:
        """Extract all function names (top-level only) from a module."""
        functions: Set[str] = set()
        for node in ast.walk(tree):
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                if node.col_offset == 0:
                    functions.add(node.name)
        return functions

    def extract_protocols(self, tree: ast.Module) -> Set[str]:
        """Extract protocol class names from a module."""
        protocols: Set[str] = set()
        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef):
                name_lower = node.name.lower()
                if "protocol" in name_lower or node.name.endswith("Protocol"):
                    protocols.add(node.name)
        return protocols

    def extract_dataclasses(self, tree: ast.Module) -> Set[str]:
        """Extract dataclass names from a module."""
        dataclasses: Set[str] = set()
        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef):
                has_dataclass_decorator = False
                for deco in node.decorator_list:
                    if isinstance(deco, ast.Name) and deco.id == "dataclass":
                        has_dataclass_decorator = True
                        break
                    elif isinstance(deco, ast.Call):
                        if isinstance(deco.func, ast.Name) and deco.func.id == "dataclass":
                            has_dataclass_decorator = True
                            break

                name_lower = node.name.lower()
                if has_dataclass_decorator or "data" in name_lower:
                    dataclasses.add(node.name)
        return dataclasses

    def extract_enums(self, tree: ast.Module) -> Set[str]:
        """Extract enum class names from a module."""
        enums: Set[str] = set()
        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef):
                has_enum_base = False
                for base in node.bases:
                    if isinstance(base, ast.Name) and base.id == "Enum":
                        has_enum_base = True
                        break

                if has_enum_base or node.name.endswith("Type") or node.name.endswith("Status"):
                    enums.add(node.name)
        return enums

    def classify_lifecycle_participation(
        self,
        tree: ast.Module,
        file_path: Path
    ) -> LifecycleParticipation:
        """
        Classify how a module participates in the lifecycle.

        Args:
            tree: AST of the module
            file_path: Path to the module

        Returns:
            Lifecycle participation level
        """
        has_startup = False
        has_shutdown = False

        for node in ast.walk(tree):
            if isinstance(node, ast.AsyncFunctionDef):
                name = node.name.lower()
                if "startup" in name or "start" in name:
                    has_startup = True
                if "shutdown" in name or "stop" in name:
                    has_shutdown = True

        if has_startup and has_shutdown:
            return LifecycleParticipation.FULL_LIFECYCLE
        elif has_startup:
            return LifecycleParticipation.STARTUP
        elif has_shutdown:
            return LifecycleParticipation.SHUTDOWN
        else:
            return LifecycleParticipation.NONE

    def discover_modules(
        self,
        repository_path: str,
        packages: Tuple[PackageMetadata, ...]
    ) -> Tuple[ModuleMetadata, ...]:
        """
        Discover all modules in the specified packages.

        Args:
            repository_path: Path to the repository root
            packages: Packages to scan

        Returns:
            Tuple of ModuleMetadata for all discovered modules
        """
        repo_path = Path(repository_path)
        modules: List[ModuleMetadata] = []

        for pkg in packages:
            pkg_path = repo_path / pkg.path

            if not pkg_path.exists():
                continue

            for py_file in pkg_path.rglob("*.py"):
                rel_path = py_file.relative_to(repo_path)

                if py_file.name == "__init__.py":
                    continue

                tree = self.parse_module(py_file)
                if tree is None:
                    continue

                public_api, private_api = self.extract_api_items(tree)
                internal_imports, external_imports = self.extract_imports(tree)

                classes = self.extract_classes(tree)
                functions = self.extract_functions(tree)
                protocols = self.extract_protocols(tree)
                dataclasses = self.extract_dataclasses(tree)
                enums = self.extract_enums(tree)

                lifecycle = self.classify_lifecycle_participation(tree, py_file)
                module_name = py_file.stem

                modules.append(ModuleMetadata(
                    name=module_name,
                    path=str(rel_path),
                    package_name=pkg.name,
                    purpose=f"{module_name.replace('_', ' ')} module",
                    responsibility=f"Provides {module_name.replace('_', ' ')} functionality",
                    imports=internal_imports | external_imports,
                    internal_imports=internal_imports,
                    external_imports=external_imports,
                    exports=tuple(public_api | private_api),
                    public_api=tuple(public_api),
                    private_api=tuple(private_api),
                    classes=classes,
                    functions=functions,
                    protocols=protocols,
                    dataclasses=dataclasses,
                    enums=enums,
                    lifecycle_participation=lifecycle,
                    health_participation="health" in module_name.lower(),
                    recovery_participation="recovery" in module_name.lower() or "failure" in module_name.lower()
                ))

        return tuple(modules)