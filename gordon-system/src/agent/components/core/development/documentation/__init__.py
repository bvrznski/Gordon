# Documentation Infrastructure
# ============================
"""
Documentation infrastructure for Gordon development tooling.

This module provides canonical abstractions for:
- Architecture documentation
- API reference generation
- Tutorial generation
- Operational guides

ARCHITECTURAL PRINCIPLES:
- Documentation is versioned
- Public APIs are documented
- Documentation is generated where practical
- Developer tools use canonical contracts
"""
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from core.development.documentation import generators, validators, templates

__all__ = [
    "generators",
    "validators", 
    "templates",
]