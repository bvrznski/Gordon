# Maintenance Automation Infrastructure
# =====================================
"""
Maintenance automation infrastructure for Gordon development tooling.

This module provides canonical abstractions for:
- Technical debt analysis
- Dead code detection
- Duplicate detection
- Dependency cleanup
- Repository normalization

ARCHITECTURAL PRINCIPLES:
- Maintenance workflows are idempotent
- Technical debt tracking is mandatory
- Automated maintenance preserves integrity
- Repository health checks run continuously
"""
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from core.development.maintenance import tasks, analysis, cleanup

__all__ = [
    "tasks",
    "analysis", 
    "cleanup",
]