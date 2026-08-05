"""Metrics Manager.

Generates repository metrics from discovery results.
"""

import ast
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

from .inventory import (
    ArchitectureInventory,
    PackageMetadata,
    ModuleMetadata,
    RuntimeAuthority,
)


class MetricsManager:
    """
    Generates repository metrics from architectural inventory data.
    
    Supports metrics including:
    - Packages
    - Modules
    - Classes
    - Protocols
    - Dataclasses
    - Enums
    - Functions
    - Public APIs
    - Mutable globals
    - Singletons
    - Authorities
    - Services
    - Registries
    - Schedulers
    - Entry points
    - Background loops
    
    Supports historical comparison through versioned snapshots.
    """
    
    def __init__(self) -> None:
        """Initialize the metrics manager."""
        self._cache: Dict[str, Dict[str, int]] = {}
    
    def compute_metrics(
        self,
        inventory: ArchitectureInventory
    ) -> Dict[str, int]:
        """
        Compute all repository metrics from inventory.
        
        Args:
            inventory: The architecture inventory
            
        Returns:
            Dictionary of metric names to counts
        """
        metrics = {
            "total_packages": len(inventory.packages),
            "total_modules": len(inventory.modules),
            "total_classes": 0,
            "total_functions": 0,
            "total_protocols": 0,
            "total_dataclasses": 0,
            "total_enums": 0,
            "total_authorities": len(inventory.runtime_authorities),
            "total_services": 0,
            "total_registries": 0,
            "total_schedulers": 0,
            "total_entry_points": len(inventory.entry_points),
            "total_background_loops": len(inventory.background_execution),
        }
        
        # Count classes, functions, etc. from modules
        for mod in inventory.modules:
            metrics["total_classes"] += len(mod.classes)
            metrics["total_functions"] += len(mod.functions)
            metrics["total_protocols"] += len(mod.protocols)
            metrics["total_dataclasses"] += len(mod.dataclasses)
            metrics["total_enums"] += len(mod.enums)
            
            # Count services, registries, schedulers
            for cls in mod.classes:
                if "Service" in cls or "service" in cls.lower():
                    metrics["total_services"] += 1
                elif "Registry" in cls or "registry" in cls.lower():
                    metrics["total_registries"] += 1
                elif "Scheduler" in cls or "scheduler" in cls.lower():
                    metrics["total_schedulers"] += 1
        
        return metrics
    
    def compute_metrics_from_path(
        self,
        repository_path: str,
        packages: Optional[Tuple[PackageMetadata, ...]] = None
    ) -> Dict[str, int]:
        """
        Compute metrics directly from file system.
        
        Args:
            repository_path: Path to the repository root
            
        Returns:
            Dictionary of metric names to counts
        """
        repo_path = Path(repository_path)
        metrics = {
            "packages": 0,
            "modules": 0,
            "classes": 0,
            "functions": 0,
            "protocols": 0,
            "dataclasses": 0,
            "enums": 0,
        }
        
        packages_to_scan = packages or ()
        
        if not packages_to_scan:
            # Scan all Python files
            for py_file in repo_path.rglob("*.py"):
                if "test" in str(py_file):
                    continue
                
                tree = self._parse_module(py_file)
                if tree is None:
                    continue
                
                file_metrics = self._count_definitions(tree)
                metrics["modules"] += 1
                metrics["classes"] += file_metrics["classes"]
                metrics["functions"] += file_metrics["functions"]
                metrics["protocols"] += file_metrics["protocols"]
                metrics["dataclasses"] += file_metrics["dataclasses"]
                metrics["enums"] += file_metrics["enums"]
                
                if py_file.name == "__init__.py":
                    metrics["packages"] += 1
        
        else:
            # Scan only specified packages
            for pkg in packages_to_scan:
                pkg_path = repo_path / pkg.path
                
                if not pkg_path.exists():
                    continue
                
                for py_file in pkg_path.rglob("*.py"):
                    tree = self._parse_module(py_file)
                    if tree is None:
                        continue
                    
                    file_metrics = self._count_definitions(tree)
                    metrics["modules"] += 1
                    metrics["classes"] += file_metrics["classes"]
                    metrics["functions"] += file_metrics["functions"]
                    metrics["protocols"] += file_metrics["protocols"]
                    metrics["dataclasses"] += file_metrics["dataclasses"]
                    metrics["enums"] += file_metrics["enums"]
        
        return metrics
    
    def _parse_module(self, file_path: Path) -> Optional[ast.Module]:
        """Parse a Python module and return its AST."""
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()
            return ast.parse(content, filename=str(file_path))
        except (SyntaxError, OSError):
            return None
    
    def _count_definitions(self, tree: ast.Module) -> Dict[str, int]:
        """Count definition types in a module."""
        counts = {
            "classes": 0,
            "functions": 0,
            "protocols": 0,
            "dataclasses": 0,
            "enums": 0,
        }
        
        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef):
                counts["classes"] += 1
                
                # Check for enum class
                for base in node.bases:
                    if isinstance(base, ast.Name) and base.id == "Enum":
                        counts["enums"] += 1
                    elif isinstance(base, ast.Attribute) and "Enum" in str(base.attr):
                        counts["enums"] += 1
                
                # Check for dataclass decorator
                for deco in node.decorator_list:
                    if isinstance(deco, ast.Name):
                        if deco.id == "dataclass":
                            counts["dataclasses"] += 1
                    elif isinstance(deco, ast.Call):
                        if isinstance(deco.func, ast.Name) and deco.func.id == "dataclass":
                            counts["dataclasses"] += 1
            
            elif isinstance(node, ast.FunctionDef) or isinstance(node, ast.AsyncFunctionDef):
                # Don't count methods as top-level functions
                if node.col_offset == 0:
                    counts["functions"] += 1
        
        return counts
    
    def compute_package_metrics(
        self,
        packages: Tuple[PackageMetadata, ...]
    ) -> Dict[str, Dict[str, int]]:
        """
        Compute metrics per package.
        
        Args:
            packages: Package metadata
            
        Returns:
            Dictionary mapping package name to its metrics
        """
        result = {}
        
        for pkg in packages:
            category_metrics = {
                "total_packages": len(packages),
                "packages_by_category": sum(1 for p in packages if p.category == pkg.category)
            }
            
            result[pkg.name] = category_metrics
        
        return result
    
    def compute_layer_metrics(
        self,
        packages: Tuple[PackageMetadata, ...]
    ) -> Dict[str, int]:
        """
        Compute metrics per architectural layer.
        
        Args:
            packages: Package metadata
            
        Returns:
            Dictionary mapping layer to package count
        """
        result: Dict[str, int] = {}
        
        for pkg in packages:
            layer = pkg.layer if pkg.layer else "Unknown"
            result[layer] = result.get(layer, 0) + 1
        
        return result
    
    def compute_category_metrics(
        self,
        packages: Tuple[PackageMetadata, ...]
    ) -> Dict[str, int]:
        """
        Compute metrics per package category.
        
        Args:
            packages: Package metadata
            
        Returns:
            Dictionary mapping category to package count
        """
        result: Dict[str, int] = {}
        
        for pkg in packages:
            cat = pkg.category.value
            result[cat] = result.get(cat, 0) + 1
        
        return result
    
    def compute_runtime_metrics(
        self,
        authorities: Tuple[RuntimeAuthority, ...]
    ) -> Dict[str, int]:
        """
        Compute runtime-specific metrics.
        
        Args:
            authorities: Runtime authority metadata
            
        Returns:
            Dictionary of runtime metrics
        """
        result = {
            "total_authorities": len(authorities),
        }
        
        # Count by category
        for auth in authorities:
            cat = auth.category.lower()
            key = f"authorities_{cat}"
            result[key] = result.get(key, 0) + 1
        
        return result
    
    def compute_history_snapshot(
        self,
        current_metrics: Dict[str, int],
        previous_metrics: Optional[Dict[str, int]] = None
    ) -> Dict[str, Any]:
        """
        Create a historical snapshot with comparison.
        
        Args:
            current_metrics: Current metrics
            previous_metrics: Previous metrics for comparison
            
        Returns:
            Snapshot dictionary with comparison info
        """
        snapshot = {
            "metrics": current_metrics,
            "timestamp": None,  # Will be set by caller
        }
        
        if previous_metrics:
            differences = {}
            for key in current_metrics:
                prev_val = previous_metrics.get(key, 0)
                curr_val = current_metrics[key]
                diff = curr_val - prev_val
                
                if diff != 0:
                    differences[key] = {
                        "current": curr_val,
                        "previous": prev_val,
                        "change": diff
                    }
            
            snapshot["differences"] = differences
        
        return snapshot


# Import RuntimeAuthority for type hints
from .inventory import RuntimeAuthority
