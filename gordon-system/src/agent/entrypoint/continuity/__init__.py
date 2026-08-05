# Entrypoint Continuity
# ======================

"""
Entrypoint continuity - the when of checkpoint operations.

This package owns:
    - Previous runtime detection
    - Process-generation initialization
    - Startup continuity sequencing
    - Restore-before-admission invocation
    - Checkpoint scheduling triggers
    - Important-transition checkpoint triggers
    - Signal-aware final checkpoint requests
    - Controlled-shutdown continuity finalization

Architecture boundary:
    Entrypoint Continuity owns WHEN operations occur.
    Core Continuity owns HOW they work.

Phase: 3.7.36-I - Runtime Continuity & Crash-Recovery Integration
"""

from .facade import (
    EntrypointContinuityFacade,
)

__all__ = [
    "EntrypointContinuityFacade",
]