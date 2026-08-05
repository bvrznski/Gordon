# Core Restart Architecture (Phase 3.7.10)
# ==========================================

"""
Core restart architecture for Phase 3.7.10.

Restart is one possible recovery action - it is NOT recovery by itself.
Restart must follow proper coordination through RecoveryCoordinator.

Key principles:
    - One authoritative generation per managed entity
    - Generation fencing prevents duplicate active generations
    - Stale generations are rejected automatically
"""

from .coordinator import RestartCoordinator, DefaultRestartCoordinator
from .contracts import RestartContract, RestartKind

__all__ = [
    # Canonical coordinator
    "RestartCoordinator",
    "DefaultRestartCoordinator",
    
    # Contracts
    "RestartContract",
    "RestartKind",
]