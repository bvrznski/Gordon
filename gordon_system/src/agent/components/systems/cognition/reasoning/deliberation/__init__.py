# Reasoning Deliberation - Phase 7.0
# ====================================

"""
Deliberation comparing alternatives and selecting preferred ones.

Deliberation preserves explicit record of why an alternative was chosen.
"""

from gordon_system.src.agent.components.systems.cognition.reasoning.shared.deliberation import (
    Deliberation,
    DeliberationPipeline,
)


__all__ = [
    "Deliberation",
    "DeliberationPipeline",
]