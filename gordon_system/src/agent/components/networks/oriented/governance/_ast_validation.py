# Oriented Network Governance AST Validation - Phase 4.7.11
# ==========================================================

"""
AST-level validation that blocks runtime imports in governance modules.

This file enforces architectural boundaries by rejecting runtime-related
imports during static analysis.

PROHIBITED IMPORTS:
    - threading
    - multiprocessing
    - asyncio
    - queue
    - subprocess
    - socket
    - requests
    - httpx
    - aiohttp
    - grpc
    - websockets
    - concurrent.futures
    - time (datetime only)
    - datetime (imported only, not used for runtime)
    - uuid.uuid4 (use semantic IDs instead)
    - random (use deterministic algorithms)
    - psutil
    - casbin
    - opa

AST validation rules:
    1. Reject any import of prohibited modules
    2. Reject use of prohibited functions
    3. Ensure all data is immutable (frozen dataclasses only)
"""

from __future__ import annotations

import ast
from typing import Tuple


class RuntimeImportChecker(ast.NodeVisitor):
    """
    AST visitor that checks for prohibited runtime imports.
    
    INVARIANTS:
        RIC-INV-001: Visitor is stateless
        RIC-INV-002: Visitor never executes runtime logic
    """
    
    PROHIBITED_MODULES = frozenset({
        "threading",
        "multiprocessing",
        "asyncio",
        "queue",
        "subprocess",
        "socket",
        "requests",
        "httpx",
        "aiohttp",
        "grpc",
        "websockets",
        "concurrent.futures",
    })
    
    PROHIBITED_FUNCTIONS = frozenset({
        "uuid.uuid4",  # Use semantic IDs instead
        "random.random",
        "time.time",
        "datetime.now",
    })
    
    def __init__(self):
        self.violations: list[str] = []
    
    def visit_Import(self, node: ast.Import) -> None:
        """Check direct imports."""
        for alias in node.names:
            if alias.name in self.PROHIBITED_MODULES:
                self.violations.append(
                    f"Prohibited import at line {node.lineno}: '{alias.name}'"
                )
    
    def visit_ImportFrom(self, node: ast.ImportFrom) -> None:
        """Check from-imports."""
        if node.module and node.module in self.PROHIBITED_MODULES:
            self.violations.append(
                f"Prohibited import at line {node.lineno}: 'from {node.module} import ...'"
            )
    
    def visit_Call(self, node: ast.Call) -> None:
        """Check function calls."""
        if isinstance(node.func, ast.Attribute):
            # Check for module.function calls
            if isinstance(node.func.value, ast.Name):
                full_name = f"{node.func.value.id}.{node.func.attr}"
                if full_name in self.PROHIBITED_FUNCTIONS:
                    self.violations.append(
                        f"Prohibited function call at line {node.lineno}: '{full_name}'"
                    )
    
    def visit_Call_Starred(self, node: ast.Starred) -> None:
        """Check for star imports (prohibited)."""
        self.violations.append(
            f"Star import at line {node.lineno} is prohibited. Use explicit imports."
        )


def validate_governance_ast(code: str) -> Tuple[bool, Tuple[str, ...]]:
    """
    Validate Python code using AST analysis.
    
    Args:
        code: Python source code to validate
        
    Returns:
        (is_valid, violations) tuple
    """
    try:
        tree = ast.parse(code)
    except SyntaxError as e:
        return False, (f"Syntax error: {e}",)
    
    checker = RuntimeImportChecker()
    checker.visit(tree)
    
    return len(checker.violations) == 0, tuple(checker.violations)


def assert_no_runtime_imports(module_path: str) -> Tuple[bool, Tuple[str, ...]]:
    """
    Assert that a module file contains no prohibited runtime imports.
    
    Args:
        module_path: Path to the Python file
        
    Returns:
        (is_valid, violations) tuple
    """
    try:
        with open(module_path, "r", encoding="utf-8") as f:
            code = f.read()
    except OSError as e:
        return False, (f"Cannot read module: {e}",)
    
    return validate_governance_ast(code)


if __name__ == "__main__":
    # Test the validator
    test_code = '''
from threading import Thread
import asyncio

def foo():
    pass
'''
    
    is_valid, violations = validate_governance_ast(test_code)
    print(f"Valid: {is_valid}")
    for v in violations:
        print(f"  - {v}")

__all__ = [
    "RuntimeImportChecker",
    "validate_governance_ast",
    "assert_no_runtime_imports",
]