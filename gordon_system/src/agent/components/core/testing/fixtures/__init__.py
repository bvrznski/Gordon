# Fixtures Subpackage - Testing Infrastructure
# ==========================================

"""
Fixtures subpackage for fixture architecture and lifecycle management.

This module provides:
- Fixture registry with dependency graph
- Fixture scopes (function, class, module, session)
- Fixture cleanup verification
"""

from .registry import (
    FixtureRegistry,
    FixtureScope,
    FixtureBuilder,
    fixture as fixture_decorator,
)
from .lifecycle import (
    FixtureLifecycle,
    verify_cleanup,
)

__all__ = [
    # Registry
    "FixtureRegistry",
    "FixtureScope",
    "FixtureBuilder",
    "fixture_decorator",
    
    # Lifecycle
    "FixtureLifecycle",
    "verify_cleanup",
]
