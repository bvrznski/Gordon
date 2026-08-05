# Engineering Utilities Infrastructure
# ====================================
"""
Engineering utilities infrastructure for Gordon development tooling.

This module provides canonical abstractions for:
- CLI utilities
- Repository inspection
- Diagnostics
- Scaffolding
- Code search helpers

ARCHITECTURAL PRINCIPLES:
- Engineering utilities are deterministic
- Developer workflows are reproducible
- Tooling is extensible
- Documentation reflects implementation
"""
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from core.development.utilities import cli, inspection, diagnostics, scaffolding

__all__ = [
    "cli",
    "inspection", 
    "diagnostics",
    "scaffolding",
]