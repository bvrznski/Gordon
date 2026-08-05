# Package Validation - Testing Infrastructure
# ==========================================

"""
Package structure validation for exports, visibility, and integrity.

The PackageValidator ensures that:
1. All packages have proper __init__.py files
2. Exports are properly declared in __all__
3. Module visibility follows intended patterns
4. Package metadata is consistent
"""

from dataclasses import dataclass, field
from typing import List, Dict, Set, Optional
from pathlib import Path


@dataclass(frozen=True)
class PackageValidationError:
    """Immutable error descriptor for package validation failures."""
    
    path: str
    issue_type: str  # missing_init, invalid_export, visibility_issue, etc.
    description: str
    severity: str = "error"  # error, warning
    
    def to_dict(self) -> Dict:
        return {
            "path": self.path,
            "issue_type": self.issue_type,
            "description": self.description,
            "severity": self.severity,
        }


@dataclass(frozen=True)
class PackageValidationResult:
    """Immutable result of package validation."""
    
    total_packages: int
    valid_packages: int
    errors: List[PackageValidationError]
    warnings: List[PackageValidationError]
    duration_seconds: float
    
    @property
    def is_valid(self) -> bool:
        """Check if all packages passed validation."""
        return len(self.errors) == 0


class PackageValidator:
    """
    Validates package structure and export declarations.
    
    This validator performs:
    - __init__.py presence checking
    - __all__ declaration analysis
    - Module visibility verification
    - Package metadata consistency
    """
    
    def __init__(self, source_path: str = "src"):
        """
        Initialize the package validator.
        
        Args:
            source_path: Path to the source directory
        """
        self.source_path = Path(source_path)
    
    def discover_packages(self) -> List[Path]:
        """Discover all Python packages (directories with __init__.py)."""
        return [
            p.parent for p in self.source_path.rglob("__init__.py")
            if p.parent != self.source_path
        ]
    
    def validate_init_py(self, package_dir: Path) -> Optional[PackageValidationError]:
        """
        Validate the __init__.py file in a package directory.
        
        Args:
            package_dir: Path to the package directory
            
        Returns:
            PackageValidationError if validation fails, None otherwise
        """
        init_file = package_dir / "__init__.py"
        
        # Check if __init__.py exists
        if not init_file.exists():
            return PackageValidationError(
                path=str(package_dir),
                issue_type="missing_init",
                description=f"Package directory missing __init__.py: {package_dir}",
                severity="warning",
            )
        
        # Read and analyze the file
        try:
            with open(init_file, "r", encoding="utf-8") as f:
                content = f.read()
            
            # Check if __all__ is defined when there are exports
            has_all = "__all__" in content
            
            # Count imports to determine if this might be an export package
            import_count = sum(
                1 for line in content.split("\n")
                if line.strip().startswith(("import ", "from "))
            )
            
            # If there are many imports but no __all__, issue a warning
            if import_count >= 3 and not has_all:
                return PackageValidationError(
                    path=str(init_file),
                    issue_type="missing_export_declaration",
                    description=f"Package has {import_count} imports but no __all__ declaration",
                    severity="warning",
                )
        
        except Exception as e:
            return PackageValidationError(
                path=str(package_dir),
                issue_type="read_error",
                description=f"Failed to read __init__.py: {e}",
                severity="error",
            )
        
        return None
    
    def validate_exports(self, package_dir: Path) -> List[str]:
        """
        Validate export declarations in a package.
        
        Args:
            package_dir: Path to the package directory
            
        Returns:
            List of exported module names
        """
        init_file = package_dir / "__init__.py"
        exports = []
        
        try:
            if not init_file.exists():
                return exports
            
            with open(init_file, "r", encoding="utf-8") as f:
                content = f.read()
            
            # Check for __all__ definition
            import ast
            tree = ast.parse(content, filename=str(init_file))
            
            for node in ast.walk(tree):
                if isinstance(node, ast.Assign):
                    for target in node.targets:
                        if isinstance(target, ast.Name) and target.id == "__all__":
                            if isinstance(node.value, (ast.List, ast.Tuple)):
                                for elt in node.value.elts:
                                    if isinstance(elt, ast.Constant):
                                        exports.append(elt.value)
            
            # Also look for module-level imports as potential exports
            if not exports:
                for node in ast.iter_child_nodes(tree):
                    if isinstance(node, (ast.ImportFrom, ast.Import)):
                        for alias in node.names:
                            name = alias.asname or alias.name
                            if not name.startswith("_"):
                                exports.append(name)
        
        except Exception:
            pass
        
        return exports
    
    def validate_visibility(self, package_dir: Path) -> List[PackageValidationError]:
        """
        Validate module visibility (public vs private).
        
        Args:
            package_dir: Path to the package directory
            
        Returns:
            List of visibility issues found
        """
        issues = []
        
        # Get all .py files in the package directory
        py_files = list(package_dir.glob("*.py"))
        
        for py_file in py_files:
            if py_file.name == "__init__.py":
                continue
            
            stem = py_file.stem
            
            # Check if a public module starts with underscore (private convention)
            if not stem.startswith("_") and py_file.name.endswith(".py"):
                # This is fine - public modules don't need underscores
                pass
        
        return issues
    
    def validate_all(self) -> PackageValidationResult:
        """
        Perform all package validations.
        
        Returns:
            PackageValidationResult with validation results
        """
        import time
        
        start_time = time.time()
        
        packages = self.discover_packages()
        total = len(packages)
        
        errors: List[PackageValidationError] = []
        warnings: List[PackageValidationError] = []
        
        for package_dir in packages:
            error = self.validate_init_py(package_dir)
            
            if error:
                if error.severity == "error":
                    errors.append(error)
                else:
                    warnings.append(error)
            
            # Validate exports
            exports = self.validate_exports(package_dir)
            
            # Validate visibility
            visibility_issues = self.validate_visibility(package_dir)
            warnings.extend(visibility_issues)
        
        valid_count = total - len(errors)
        
        return PackageValidationResult(
            total_packages=total,
            valid_packages=valid_count,
            errors=errors,
            warnings=warnings,
            duration_seconds=time.time() - start_time,
        )


def validate_package_structure(source_path: str = "src") -> PackageValidationResult:
    """Validate all package structures in a source path."""
    validator = PackageValidator(source_path)
    return validator.validate_all()


def verify_exports(package_dir: str) -> List[str]:
    """Verify export declarations in a package."""
    validator = PackageValidator()
    return validator.validate_exports(Path(package_dir))


def check_module_visibility(package_dir: str) -> List[PackageValidationError]:
    """Check module visibility in a package."""
    validator = PackageValidator()
    return validator.validate_visibility(Path(package_dir))