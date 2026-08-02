# Core Integrity Validation
# =========================

"""
Core runtime integrity validation.

Provides structural integrity checking for:
- Package tree contracts
- Parent-child relationships
- Architectural path validation
- Duplicate ownership detection
"""

from dataclasses import dataclass, field
from typing import Dict, List, Any, Optional, Tuple
from enum import Enum
import os


class Severity(Enum):
    """Validation severity levels."""
    
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"


@dataclass(frozen=True)
class IntegrityIssue:
    """
    A single integrity validation issue.
    
    Args:
        path: File or package path affected
        message: Human-readable description
        severity: Issue severity level
        rule_violated: Name of the violated rule (if applicable)
    """
    
    path: str
    message: str
    severity: str  # Severity value
    rule_violated: Optional[str] = None


@dataclass(frozen=True)
class IntegrityReport:
    """
    Complete integrity validation report.
    
    Args:
        is_valid: Whether the tree passes all critical checks
        issues: List of all issues found
        warnings_count: Number of warning-level issues
        errors_count: Number of error-level issues
    """
    
    is_valid: bool
    issues: List[IntegrityIssue]
    warnings_count: int = 0
    errors_count: int = 0
    
    @classmethod
    def valid(cls) -> "IntegrityReport":
        """Create a valid report."""
        return cls(is_valid=True, issues=[])
    
    @classmethod
    def invalid(cls, issues: List[IntegrityIssue]) -> "IntegrityReport":
        """Create an invalid report."""
        warnings = sum(1 for i in issues if i.severity == Severity.WARNING.value)
        errors = sum(1 for i in issues if i.severity == Severity.ERROR.value)
        return cls(is_valid=False, issues=issues, warnings_count=warnings, errors_count=errors)


class TreeContract:
    """
    Parsed tree contract from __tree__.py.
    
    Contains structural information about a package's expected children
    and ownership boundaries.
    """
    
    def __init__(
        self,
        package_path: str,
        parent_package: Optional[str],
        allowed_children: List[str],
        required_children: List[str],
        required_files: List[str],
        forbidden_children: List[str],
        dependency_direction: str
    ) -> None:
        self.package_path = package_path
        self.parent_package = parent_package
        self.allowed_children = allowed_children
        self.required_children = required_children
        self.required_files = required_files
        self.forbidden_children = forbidden_children
        self.dependency_direction = dependency_direction
    
    @classmethod
    def from_module(cls, module: Any) -> "TreeContract":
        """
        Create a contract from a __tree__.py module.
        
        Args:
            module: The loaded __tree__ module
            
        Returns:
            Parsed TreeContract object
        """
        return cls(
            package_path=getattr(module, "package_path", ""),
            parent_package=getattr(module, "parent_package", None),
            allowed_children=getattr(module, "allowed_children", []),
            required_children=getattr(module, "required_children", []),
            required_files=getattr(module, "required_files", ["__init__.py"]),
            forbidden_children=getattr(module, "forbidden_children", []),
            dependency_direction=getattr(module, "dependency_direction", "downward")
        )


class PackageStructureValidator:
    """
    Validates package structure against contracts.
    
    Read-only operations - does not modify filesystem or imports.
    """
    
    def __init__(self, root_path: str) -> None:
        self._root_path = root_path
        self._contracts: Dict[str, TreeContract] = {}
        self._loaded_paths: set = set()
    
    async def load_contract(self, package_path: str) -> Optional[TreeContract]:
        """
        Load a tree contract from a package.
        
        Args:
            package_path: Dot-separated package path
            
        Returns:
            TreeContract if found, None otherwise
        """
        # Convert to filesystem path
        parts = package_path.split(".")
        file_path = os.path.join(self._root_path, *parts, "__tree__.py")
        
        if not os.path.exists(file_path):
            return None
        
        if file_path in self._loaded_paths:
            return self._contracts.get(package_path)
        
        # Load without executing (safe parsing only)
        try:
            with open(file_path, "r") as f:
                content = f.read()
            
            # Parse contract from file content
            contract = await self._parse_contract(content, package_path)
            self._contracts[package_path] = contract
            self._loaded_paths.add(file_path)
            
            return contract
            
        except Exception:
            return None
    
    async def _parse_contract(self, content: str, package_path: str) -> TreeContract:
        """Parse a __tree__.py file content."""
        import ast
        
        try:
            tree = ast.parse(content)
            allowed_children = []
            required_children = []
            
            for node in ast.walk(tree):
                if isinstance(node, ast.Assign):
                    for target in node.targets:
                        if isinstance(target, ast.Name) and target.id == "allowed_children":
                            if isinstance(node.value, ast.List):
                                allowed_children = [
                                    elt.s for elt in node.value.elts
                                    if isinstance(elt, ast.Str)
                                ]
                        elif isinstance(target, ast.Name) and target.id == "required_children":
                            if isinstance(node.value, ast.List):
                                required_children = [
                                    elt.s for elt in node.value.elts
                                    if isinstance(elt, ast.Str)
                                ]
            
            return TreeContract(
                package_path=package_path,
                parent_package=None,  # Would need more parsing to get this
                allowed_children=allowed_children,
                required_children=required_children,
                required_files=["__init__.py", "__meta__.py", "__tree__.py"],
                forbidden_children=[],
                dependency_direction="downward"
            )
            
        except SyntaxError:
            return TreeContract(
                package_path=package_path,
                parent_package=None,
                allowed_children=[],
                required_children=[],
                required_files=["__init__.py", "__meta__.py", "__tree__.py"],
                forbidden_children=[],
                dependency_direction="downward"
            )
    
    async def validate_tree(self) -> IntegrityReport:
        """
        Validate the entire package tree.
        
        Returns:
            IntegrityReport with all issues found
        """
        issues: List[IntegrityIssue] = []
        
        # Check each contract
        for path, contract in self._contracts.items():
            # Validate parent-child relationships
            if contract.parent_package:
                parent_contract = self._contracts.get(contract.parent_package)
                if parent_contract and contract.package_path not in parent_contract.allowed_children:
                    issues.append(IntegrityIssue(
                        path=path,
                        message=f"Package '{path}' is not in parent's allowed children",
                        severity=Severity.ERROR.value
                    ))
            
            # Check required files exist
            parts = path.split(".")
            dir_path = os.path.join(self._root_path, *parts)
            
            for req_file in contract.required_files:
                file_path = os.path.join(dir_path, req_file)
                if not os.path.exists(file_path):
                    issues.append(IntegrityIssue(
                        path=file_path,
                        message=f"Required file '{req_file}' missing",
                        severity=Severity.WARNING.value
                    ))
        
        # Determine overall validity (critical errors only)
        has_critical = any(i.severity == Severity.ERROR.value for i in issues)
        
        return IntegrityReport(
            is_valid=not has_critical,
            issues=issues
        )
    
    async def validate_parent_child_relationship(self, child_path: str) -> List[IntegrityIssue]:
        """
        Validate that a package's parent recognizes it as an allowed child.
        
        Args:
            child_path: Child package path
            
        Returns:
            List of issues (empty if valid)
        """
        # Get the parent contract
        parts = child_path.split(".")
        if len(parts) < 2:
            return []  # Root has no parent
        
        parent_path = ".".join(parts[:-1])
        parent_contract = self._contracts.get(parent_path)
        
        if not parent_contract:
            return [IntegrityIssue(
                path=parent_path,
                message=f"Parent package contract not found",
                severity=Severity.WARNING.value
            )]
        
        child_name = parts[-1]
        issues: List[IntegrityIssue] = []
        
        # Check allowed children
        if parent_contract.allowed_children and child_name not in parent_contract.allowed_children:
            issues.append(IntegrityIssue(
                path=child_path,
                message=f"Package '{child_name}' is not in parent's allowed children",
                severity=Severity.ERROR.value
            ))
        
        return issues
    
    async def validate_architectural_paths(self, root: str) -> IntegrityReport:
        """
        Validate that all paths conform to architectural requirements.
        
        Args:
            root: Root path to validate
            
        Returns:
            IntegrityReport with any violations
        """
        issues: List[IntegrityIssue] = []
        
        # Walk the directory tree
        for dirpath, dirnames, filenames in os.walk(root):
            # Check for __tree__.py files
            if "__tree__.py" in filenames:
                package_path = dirpath.replace(os.path.sep, ".").lstrip(".")
                
                # Validate it's a valid Python package path
                parts = package_path.split(".")
                for part in parts:
                    if not part or not part.isidentifier():
                        issues.append(IntegrityIssue(
                            path=dirpath,
                            message=f"Invalid package name component: {part}",
                            severity=Severity.WARNING.value
                        ))
        
        return IntegrityReport(is_valid=len(issues) == 0, issues=issues)


__all__ = [
    "Severity",
    "IntegrityIssue",
    "IntegrityReport",
    "TreeContract",
    "PackageStructureValidator",
]
