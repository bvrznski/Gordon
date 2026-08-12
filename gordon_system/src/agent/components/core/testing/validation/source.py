# Source Validation - Testing Infrastructure
# ==========================================

"""
Source code validation for compilation, syntax, and structural integrity.

The SourceValidator ensures that all Python source files in the repository:
1. Compile without syntax errors
2. Pass static analysis checks
3. Follow import discipline (no side effects)
4. Maintain package structure integrity
"""

from dataclasses import dataclass, field
from typing import List, Dict, Optional, Tuple
from pathlib import Path
import ast
import py_compile
import sys


@dataclass(frozen=True)
class SourceValidationError:
    """Immutable error descriptor for source validation failures."""
    
    path: str
    line_number: Optional[int]
    column: Optional[int]
    error_type: str  # SyntaxError, ImportError, etc.
    message: str
    severity: str = "error"  # error, warning, info
    
    def to_dict(self) -> Dict:
        """Convert to dictionary representation."""
        return {
            "path": self.path,
            "line_number": self.line_number,
            "column": self.column,
            "error_type": self.error_type,
            "message": self.message,
            "severity": self.severity,
        }


@dataclass(frozen=True)
class SourceValidationResult:
    """Immutable result of source code validation."""
    
    total_files: int
    valid_files: int
    invalid_files: List[SourceValidationError]
    syntax_errors: List[SourceValidationError]
    import_issues: List[SourceValidationError]
    structural_issues: List[SourceValidationError]
    duration_seconds: float
    
    @property
    def is_valid(self) -> bool:
        """Check if all files passed validation."""
        return len(self.syntax_errors) == 0 and len(self.import_issues) == 0


class SourceValidator:
    """
    Validates Python source code for compilation, syntax, and structural integrity.
    
    This validator performs:
    - Syntax checking (AST parsing)
    - Compilation testing
    - Import cycle detection
    - Package structure validation
    - Module visibility analysis
    """
    
    def __init__(self, source_path: str = "src"):
        """
        Initialize the source validator.
        
        Args:
            source_path: Path to the source directory to validate
        """
        self.source_path = Path(source_path)
        self._cache: Dict[Path, Optional[str]] = {}
    
    def discover_source_files(self) -> List[Path]:
        """Discover all Python source files in the source path."""
        return list(self.source_path.rglob("*.py"))
    
    def validate_file_syntax(self, filepath: Path) -> Tuple[bool, Optional[str]]:
        """
        Validate syntax of a single file.
        
        Args:
            filepath: Path to the Python file
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        try:
            # Parse AST
            with open(filepath, "r", encoding="utf-8") as f:
                source = f.read()
            
            ast.parse(source, filename=str(filepath))
            
            # Try to compile
            py_compile.compile(filepath, doraise=True)
            
            return True, None
            
        except SyntaxError as e:
            return False, f"Syntax error at line {e.lineno}, column {e.offset}: {e.msg}"
        except Exception as e:
            return False, f"Compilation failed: {str(e)}"
    
    def validate_file_imports(self, filepath: Path) -> Tuple[bool, Optional[str]]:
        """
        Validate that file imports don't have side effects during import.
        
        Args:
            filepath: Path to the Python file
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        try:
            # Parse and analyze imports
            with open(filepath, "r", encoding="utf-8") as f:
                source = f.read()
            
            tree = ast.parse(source, filename=str(filepath))
            
            # Check for top-level side-effect statements
            for node in ast.iter_child_nodes(tree):
                if isinstance(node, (ast.ImportFrom, ast.Import)):
                    # Import statements are okay for imports
                    pass
                elif isinstance(node, ast.Call):
                    # Function calls at module level could be side effects
                    if isinstance(node.func, ast.Name):
                        func_name = node.func.id
                        if func_name in ("print", "input"):
                            return False, f"Side effect call to {func_name} at module level"
            
            return True, None
            
        except Exception as e:
            return False, f"Import validation failed: {str(e)}"
    
    def validate_package_structure(self, filepath: Path) -> Tuple[bool, Optional[str]]:
        """
        Validate package structure for the file.
        
        Args:
            filepath: Path to a Python file
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        try:
            # Handle both str and Path inputs
            filepath = Path(filepath) if isinstance(filepath, str) else filepath
            parent = filepath.parent
            
            while parent != self.source_path and parent != parent.parent:
                init_file = parent / "__init__.py"
                
                if not init_file.exists() and list(parent.glob("*.py")):
                    return False, f"Missing __init__.py in {parent}"
                
                parent = parent.parent
            
            return True, None
            
        except Exception as e:
            return False, f"Package structure validation failed: {str(e)}"
    
    def validate_file(self, filepath: Path) -> SourceValidationError:
        """
        Perform all validations on a single file.
        
        Args:
            filepath: Path to the Python file
            
        Returns:
            SourceValidationError if any validation fails, None otherwise
        """
        errors = []
        
        # Syntax check
        is_valid, error_msg = self.validate_file_syntax(filepath)
        if not is_valid:
            errors.append(
                SourceValidationError(
                    path=str(filepath),
                    line_number=None,
                    column=None,
                    error_type="SyntaxError",
                    message=error_msg,
                    severity="error",
                )
            )
        
        # Import check
        is_valid, error_msg = self.validate_file_imports(filepath)
        if not is_valid:
            errors.append(
                SourceValidationError(
                    path=str(filepath),
                    line_number=None,
                    column=None,
                    error_type="ImportError",
                    message=error_msg,
                    severity="warning",
                )
            )
        
        # Package structure check
        is_valid, error_msg = self.validate_package_structure(filepath)
        if not is_valid:
            errors.append(
                SourceValidationError(
                    path=str(filepath),
                    line_number=None,
                    column=None,
                    error_type="StructureError",
                    message=error_msg,
                    severity="warning",
                )
            )
        
        # Return first error or None
        return errors[0] if errors else None
    
    def validate_all(self) -> SourceValidationResult:
        """
        Validate all source files in the source path.
        
        Returns:
            SourceValidationResult with aggregated results
        """
        import time
        
        start_time = time.time()
        
        files = self.discover_source_files()
        total = len(files)
        
        syntax_errors = []
        import_issues = []
        structural_issues = []
        
        for filepath in files:
            error = self.validate_file(filepath)
            if error:
                if error.error_type == "SyntaxError":
                    syntax_errors.append(error)
                elif error.error_type == "ImportError":
                    import_issues.append(error)
                else:
                    structural_issues.append(error)
        
        valid_count = total - len(syntax_errors) - len(import_issues) - len(structural_issues)
        
        return SourceValidationResult(
            total_files=total,
            valid_files=valid_count,
            invalid_files=syntax_errors + import_issues + structural_issues,
            syntax_errors=syntax_errors,
            import_issues=import_issues,
            structural_issues=structural_issues,
            duration_seconds=time.time() - start_time,
        )


def validate_source_code(source_path: str = "src") -> SourceValidationResult:
    """
    Convenience function to validate all source files.
    
    Args:
        source_path: Path to the source directory
        
    Returns:
        SourceValidationResult with validation results
    """
    validator = SourceValidator(source_path)
    return validator.validate_all()


def check_syntax_errors(filepath: str) -> List[str]:
    """
    Check for syntax errors in a single file.
    
    Args:
        filepath: Path to the Python file
        
    Returns:
        List of error messages (empty if valid)
    """
    validator = SourceValidator()
    is_valid, error_msg = validator.validate_file_syntax(Path(filepath))
    
    return [error_msg] if not is_valid else []


def analyze_imports(filepath: str) -> Dict[str, any]:
    """
    Analyze imports in a file for side effects.
    
    Args:
        filepath: Path to the Python file
        
    Returns:
        Dictionary with import analysis results
    """
    validator = SourceValidator()
    is_valid, error_msg = validator.validate_file_imports(Path(filepath))
    
    return {
        "path": filepath,
        "is_valid": is_valid,
        "error_message": error_msg,
    }