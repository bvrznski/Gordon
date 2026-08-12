# API Documentation Validation - Testing Infrastructure
# ==========================================

"""
API documentation validation for public interface, stability annotations,
and example code.

The APIDocValidator ensures that:
1. Public APIs are properly documented
2. Stability annotations (stable, experimental, deprecated) are consistent
3. Example code is valid and up-to-date
"""

from dataclasses import dataclass, field
from typing import List, Dict, Optional
from pathlib import Path
import ast
import re


@dataclass(frozen=True)
class APIDocError:
    """Immutable error descriptor for API documentation issues."""
    
    path: str
    symbol_name: str  # Class or function name
    issue_type: str   # missing_docstring, invalid_stability, etc.
    description: str
    severity: str = "warning"
    
    def to_dict(self) -> Dict:
        return {
            "path": self.path,
            "symbol_name": self.symbol_name,
            "issue_type": self.issue_type,
            "description": self.description,
            "severity": self.severity,
        }


@dataclass(frozen=True)
class APIDocValidationResult:
    """Immutable result of API documentation validation."""
    
    total_symbols: int
    documented_symbols: int
    errors: List[APIDocError]
    stability_issues: List[str]  # List of symbols with stability issues
    duration_seconds: float
    
    @property
    def is_valid(self) -> bool:
        """Check if all API documentation passed validation."""
        return len(self.errors) == 0


class APIDocValidator:
    """
    Validates public API documentation.
    
    This validator performs:
    - Public API identification
    - Docstring presence and completeness checking
    - Stability annotation verification
    - Example code validation
    """
    
    def __init__(self, source_path: str = "src"):
        """
        Initialize the API documentation validator.
        
        Args:
            source_path: Path to the source directory
        """
        self.source_path = Path(source_path)
    
    def discover_public_symbols(self, filepath: Path) -> List[Dict]:
        """
        Discover public symbols in a file.
        
        Args:
            filepath: Path to the Python file
            
        Returns:
            List of symbol information dictionaries
        """
        symbols = []
        
        try:
            with open(filepath, "r", encoding="utf-8") as f:
                content = f.read()
            
            tree = ast.parse(content, filename=str(filepath))
            
            for node in ast.walk(tree):
                if isinstance(node, (ast.ClassDef, ast.FunctionDef)):
                    name = node.name
                    
                    # Skip private and protected symbols
                    if name.startswith("_"):
                        continue
                    
                    docstring = ast.get_docstring(node)
                    
                    symbol_info = {
                        "name": name,
                        "type": "class" if isinstance(node, ast.ClassDef) else "function",
                        "docstring": docstring,
                        "line_number": node.lineno,
                        "path": str(filepath),
                    }
                    
                    # Check for decorators
                    decorator_names = []
                    for dec in node.decorator_list:
                        if isinstance(dec, ast.Name):
                            decorator_names.append(dec.id)
                        elif isinstance(dec, ast.Attribute):
                            decorator_names.append(dec.attr)
                    
                    symbol_info["decorators"] = decorator_names
                    
                    symbols.append(symbol_info)
        
        except Exception:
            pass
        
        return symbols
    
    def validate_docstring(self, docstring: Optional[str], symbol_name: str) -> List[APIDocError]:
        """
        Validate a docstring for completeness.
        
        Args:
            docstring: The docstring content
            symbol_name: Name of the symbol being documented
            
        Returns:
            List of documentation errors found
        """
        errors = []
        
        if not docstring:
            errors.append(
                APIDocError(
                    path="unknown",
                    symbol_name=symbol_name,
                    issue_type="missing_docstring",
                    description=f"Missing docstring for {symbol_name}",
                    severity="warning",
                )
            )
            return errors
        
        # Check for basic structure
        lines = docstring.strip().split("\n")
        
        if len(lines) < 2:
            errors.append(
                APIDocError(
                    path="unknown",
                    symbol_name=symbol_name,
                    issue_type="insufficient_docstring",
                    description=f"Docstring too short for {symbol_name}",
                    severity="info",
                )
            )
        else:
            # Check for summary line
            first_line = lines[0].strip()
            
            if not first_line.endswith((".", ":", ";")):
                errors.append(
                    APIDocError(
                        path="unknown",
                        symbol_name=symbol_name,
                        issue_type="missing_summary_punctuation",
                        description=f"First line should end with punctuation: {first_line}",
                        severity="info",
                    )
                )
        
        return errors
    
    def validate_stability_annotations(self, symbols: List[Dict]) -> List[str]:
        """
        Validate stability annotations on public symbols.
        
        Args:
            symbols: List of symbol information dictionaries
            
        Returns:
            List of symbols with stability issues
        """
        issues = []
        
        valid_stability_markers = {
            "@stable": "stable",
            "@experimental": "experimental", 
            "@deprecated": "deprecated",
        }
        
        for symbol in symbols:
            docstring = symbol.get("docstring", "")
            
            # Check for stability markers
            found_markers = [
                marker for marker in valid_stability_markers.keys()
                if marker in docstring.lower()
            ]
            
            # If there are multiple stability markers, that's an issue
            if len(found_markers) > 1:
                issues.append(f"{symbol['name']}: Multiple stability markers found")
        
        return issues
    
    def validate_example_code(self, docstring: Optional[str]) -> List[APIDocError]:
        """
        Validate example code in a docstring.
        
        Args:
            docstring: The docstring content
            
        Returns:
            List of errors found
        """
        errors = []
        
        if not docstring:
            return errors
        
        # Find example code blocks (marked with >>> or ... for doctests)
        lines = docstring.split("\n")
        in_example = False
        example_lines = []
        
        for line in lines:
            stripped = line.strip()
            
            if stripped.startswith(">>>") or stripped.startswith("..."):
                in_example = True
                example_lines.append(line)
            elif in_example and (stripped == "" or stripped.startswith("#")):
                continue
            elif in_example:
                # Validate the collected example code
                try:
                    # Join lines and try to compile
                    example_code = "\n".join(example_lines)
                    compile(example_code, "<docstring>", "exec")
                except SyntaxError as e:
                    errors.append(
                        APIDocError(
                            path="unknown",
                            symbol_name="example",
                            issue_type="invalid_example_code",
                            description=f"Example code syntax error: {e.msg}",
                            severity="error",
                        )
                    )
                
                in_example = False
                example_lines = []
        
        return errors
    
    def validate_public_api(self, filepath: Path) -> APIDocValidationResult:
        """
        Validate API documentation for a file.
        
        Args:
            filepath: Path to the Python file
            
        Returns:
            APIDocValidationResult with validation results
        """
        symbols = self.discover_public_symbols(filepath)
        
        all_errors: List[APIDocError] = []
        stability_issues: List[str] = []
        documented_count = 0
        
        for symbol in symbols:
            docstring = symbol.get("docstring")
            
            if docstring:
                documented_count += 1
            
            errors = self.validate_docstring(docstring, symbol["name"])
            all_errors.extend(errors)
        
        stability_issues = self.validate_stability_annotations(symbols)
        
        return APIDocValidationResult(
            total_symbols=len(symbols),
            documented_symbols=documented_count,
            errors=all_errors,
            stability_issues=stability_issues,
            duration_seconds=0.0,  # Not tracking for individual file
        )
    
    def validate_all(self) -> APIDocValidationResult:
        """
        Validate API documentation across all Python files.
        
        Returns:
            APIDocValidationResult with validation results
        """
        import time
        
        start_time = time.time()
        
        py_files = list(self.source_path.rglob("*.py"))
        
        all_errors: List[APIDocError] = []
        all_stability_issues: List[str] = []
        total_symbols = 0
        documented_symbols = 0
        
        for filepath in py_files:
            result = self.validate_public_api(filepath)
            all_errors.extend(result.errors)
            all_stability_issues.extend(result.stability_issues)
            total_symbols += result.total_symbols
            documented_symbols += result.documented_symbols
        
        return APIDocValidationResult(
            total_symbols=total_symbols,
            documented_symbols=documented_symbols,
            errors=all_errors,
            stability_issues=list(set(all_stability_issues)),
            duration_seconds=time.time() - start_time,
        )


def validate_public_api(source_path: str = "src") -> List[APIDocError]:
    """Validate public API documentation."""
    validator = APIDocValidator(source_path)
    
    errors = []
    for filepath in source_path.rglob("*.py"):
        result = validator.validate_public_api(filepath)
        errors.extend(result.errors)
    
    return errors


def check_stability_annotations(source_path: str = "src") -> List[str]:
    """Check stability annotations on public symbols."""
    validator = APIDocValidator(source_path)
    
    issues = []
    for filepath in source_path.rglob("*.py"):
        result = validator.validate_public_api(filepath)
        issues.extend(result.stability_issues)
    
    return list(set(issues))


def verify_example_code(docstring: Optional[str]) -> List[APIDocError]:
    """Verify example code in a docstring."""
    validator = APIDocValidator()
    return validator.validate_example_code(docstring)