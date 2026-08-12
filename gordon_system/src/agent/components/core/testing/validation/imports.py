# Import Validation - Testing Infrastructure
# ==========================================

"""
Import validation for cycles, side effects, and path integrity.

The ImportValidator ensures that:
1. No circular import dependencies exist
2. Imports don't cause side effects during module loading
3. All import paths are valid and resolvable
"""

from dataclasses import dataclass, field
from typing import List, Dict, Set, Optional, Tuple
from pathlib import Path
import ast
import sys


@dataclass(frozen=True)
class ImportCycle:
    """Immutable representation of an import cycle."""
    
    path: List[str]  # List of modules forming the cycle
    start_module: str
    
    def __str__(self) -> str:
        return " → ".join(self.path) + " → " + self.start_module


@dataclass(frozen=True)
class ImportSideEffect:
    """Immutable representation of a detected side effect."""
    
    module: str
    location: str  # File path and line number
    description: str
    
    def to_dict(self) -> Dict:
        return {
            "module": self.module,
            "location": self.location,
            "description": self.description,
        }


@dataclass(frozen=True)
class ImportValidationResult:
    """Immutable result of import validation."""
    
    total_modules: int
    modules_with_cycles: List[ImportCycle]
    modules_with_side_effects: List[ImportSideEffect]
    invalid_imports: List[str]  # List of failed import paths
    duration_seconds: float
    
    @property
    def is_valid(self) -> bool:
        """Check if validation passed."""
        return (
            len(self.modules_with_cycles) == 0
            and len(self.modules_with_side_effects) == 0
            and len(self.invalid_imports) == 0
        )


class ImportValidator:
    """
    Validates Python imports for cycles, side effects, and integrity.
    
    This validator performs:
    - Circular import detection using DFS
    - Side effect detection during module import
    - Path resolution validation
    - Module visibility analysis
    """
    
    def __init__(self, source_path: str = "src", package_root: Optional[str] = None):
        """
        Initialize the import validator.
        
        Args:
            source_path: Path to the source directory
            package_root: Root package name (e.g., 'agent')
        """
        self.source_path = Path(source_path)
        self.package_root = package_root or "src"
        self._import_graph: Dict[str, Set[str]] = {}
    
    def discover_modules(self) -> List[Path]:
        """Discover all Python modules in the source path."""
        return list(self.source_path.rglob("*.py"))
    
    def parse_imports(self, filepath: Path) -> List[Tuple[str, str]]:
        """
        Parse imports from a file.
        
        Args:
            filepath: Path to the Python file
            
        Returns:
            List of (import_type, module_name) tuples
        """
        imports = []
        
        try:
            with open(filepath, "r", encoding="utf-8") as f:
                tree = ast.parse(f.read(), filename=str(filepath))
            
            for node in ast.walk(tree):
                if isinstance(node, ast.ImportFrom):
                    if node.module:
                        module_name = node.module
                    elif node.level:
                        # Relative import
                        module_name = "." * node.level + "relative"
                    else:
                        continue
                    
                    imports.append(("from", module_name))
                
                elif isinstance(node, ast.Import):
                    for alias in node.names:
                        imports.append(("import", alias.name))
        
        except Exception:
            pass
        
        return imports
    
    def build_import_graph(self) -> Dict[str, Set[str]]:
        """
        Build an import graph from all discovered modules.
        
        Returns:
            Dictionary mapping module names to sets of imported modules
        """
        self._import_graph = {}
        
        for filepath in self.discover_modules():
            module_name = self._filepath_to_module(filepath)
            
            imports = self.parse_imports(filepath)
            imported_modules = {mod for _, mod in imports if not mod.startswith(".")}
            
            self._import_graph[module_name] = imported_modules
        
        return self._import_graph
    
    def detect_cycles(self) -> List[ImportCycle]:
        """
        Detect circular import dependencies using DFS.
        
        Returns:
            List of detected cycles
        """
        graph = self.build_import_graph()
        cycles = []
        
        visited: Set[str] = set()
        rec_stack: Set[str] = set()
        path: List[str] = []
        
        def dfs(node: str) -> None:
            visited.add(node)
            rec_stack.add(node)
            path.append(node)
            
            for neighbor in graph.get(node, set()):
                if neighbor not in visited:
                    dfs(neighbor)
                elif neighbor in rec_stack:
                    # Found a cycle
                    cycle_start = path.index(neighbor)
                    cycle_path = path[cycle_start:] + [neighbor]
                    cycles.append(
                        ImportCycle(
                            path=cycle_path,
                            start_module=neighbor,
                        )
                    )
            
            path.pop()
            rec_stack.remove(node)
        
        for module in graph:
            if module not in visited:
                dfs(module)
        
        return cycles
    
    def detect_side_effects(self, filepath: Path) -> List[ImportSideEffect]:
        """
        Detect side effects during import.
        
        Args:
            filepath: Path to the Python file
            
        Returns:
            List of detected side effects
        """
        effects = []
        
        try:
            with open(filepath, "r", encoding="utf-8") as f:
                source = f.read()
            
            tree = ast.parse(source, filename=str(filepath))
            
            # Check for top-level statements that might cause side effects
            for node in ast.iter_child_nodes(tree):
                if isinstance(node, (ast.ImportFrom, ast.Import)):
                    continue
                
                # Function calls at module level
                if isinstance(node, ast.Expr) and isinstance(node.value, ast.Call):
                    func = node.value.func
                    if isinstance(func, ast.Name):
                        call_name = func.id
                        effects.append(
                            ImportSideEffect(
                                module=str(filepath),
                                location=f"module-level call to {call_name}",
                                description=f"Module calls {call_name} at import time",
                            )
                        )
                
                # Class or function definitions with decorators that might have side effects
                elif isinstance(node, (ast.ClassDef, ast.FunctionDef)):
                    for decorator in node.decorator_list:
                        if isinstance(decorator, ast.Call):
                            effects.append(
                                ImportSideEffect(
                                    module=str(filepath),
                                    location=f"{node.name} decorator call",
                                    description="Decorator has side effect during import",
                                )
                            )
        
        except Exception:
            pass
        
        return effects
    
    def validate_import_paths(self) -> List[str]:
        """
        Validate that all imported modules are resolvable.
        
        Returns:
            List of unresolvable import paths
        """
        invalid = []
        
        for filepath in self.discover_modules():
            imports = self.parse_imports(filepath)
            
            for _, module_name in imports:
                # Skip relative imports and built-ins
                if module_name.startswith(".") or module_name.startswith("builtins"):
                    continue
                
                # Try to resolve the module
                try:
                    parts = module_name.split(".")
                    __import__(parts[0])
                except ImportError:
                    invalid.append(module_name)
        
        return invalid
    
    def validate_all(self) -> ImportValidationResult:
        """
        Perform all import validations.
        
        Returns:
            ImportValidationResult with validation results
        """
        import time
        
        start_time = time.time()
        
        modules = self.discover_modules()
        total = len(modules)
        
        cycles = self.detect_cycles()
        side_effects: List[ImportSideEffect] = []
        
        for filepath in modules:
            effects = self.detect_side_effects(filepath)
            side_effects.extend(effects)
        
        invalid_imports = self.validate_import_paths()
        
        return ImportValidationResult(
            total_modules=total,
            modules_with_cycles=cycles,
            modules_with_side_effects=side_effects,
            invalid_imports=list(set(invalid_imports)),  # Deduplicate
            duration_seconds=time.time() - start_time,
        )
    
    def _filepath_to_module(self, filepath: Path) -> str:
        """Convert a file path to a module name."""
        try:
            relative_path = filepath.relative_to(self.source_path)
            parts = list(relative_path.parts)
            
            # Remove .py extension from last part
            if parts and parts[-1].endswith(".py"):
                parts[-1] = parts[-1][:-3]
            
            return ".".join(p for p in parts if p != "__init__")
        except ValueError:
            return str(filepath)


def check_import_cycles(source_path: str = "src") -> List[ImportCycle]:
    """Check for circular import dependencies."""
    validator = ImportValidator(source_path)
    return validator.detect_cycles()


def detect_side_effects(filepath: str) -> List[ImportSideEffect]:
    """Detect side effects in a file."""
    validator = ImportValidator()
    return validator.detect_side_effects(Path(filepath))


def validate_import_paths(source_path: str = "src") -> List[str]:
    """Validate that all import paths are resolvable."""
    validator = ImportValidator(source_path)
    return validator.validate_import_paths()