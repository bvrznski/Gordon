# CI/CD Pipeline Infrastructure
# =============================
"""
CI/CD pipeline infrastructure for Gordon development tooling.

This module provides canonical abstractions for:
- Continuous integration workflows
- Pull request validation
- Architecture checks
- Automated testing

ARCHITECTURAL PRINCIPLES:
- CI validates every architectural change
- Releases are versioned
- Repository automation is idempotent
- Build artifacts are traceable
"""
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from core.development.cicd import pipeline, stages, hooks

__all__ = [
    "pipeline",
    "stages", 
    "hooks",
]