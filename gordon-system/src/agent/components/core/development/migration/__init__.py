# Migration Workflow Infrastructure
# =================================
"""
Migration workflow infrastructure for Gordon development tooling.

This module provides canonical abstractions for:
- Repository migrations
- Configuration migrations
- Schema migrations
- API migrations
- Compatibility migrations

ARCHITECTURAL PRINCIPLES:
- Migrations are reversible where practical
- Version history is preserved
- Rollback planning is mandatory
- Data integrity must be maintained
"""
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from core.development.migration import workflows, steps, versions

__all__ = [
    "workflows",
    "steps", 
    "versions",
]