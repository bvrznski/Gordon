# Workspace Integration State Subpackage
# ======================================

"""
State tracking and history for workspace integration episodes.

ARCHITECTURAL PRINCIPLES:
    - All dataclasses are frozen (deeply immutable)
    - No runtime dependencies
    - Bounded by explicit limits
"""

from __future__ import annotations


__all__ = [
    "WorkspaceIntegrationState",
]