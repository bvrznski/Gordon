# Gordon Phase 5.7.3-I: Intentional Context Engine
# ===============================================================================
#
# Canonical package for the Intentional Context Engine.
#

"""
Canonical Intentional Context Engine for Gordon.

The Intentional Context Engine represents Gordon's current directed cognitive
context. It answers: "What is the agent presently directed toward?"

It organizes relationships between the current experiential field and
intentional objects. It never performs reasoning, never grants truth,
never grants authorization, and never executes actions.
"""

from gordon.agent.components.systems.consciousnessengine import IntentionalContextEngine

__all__: tuple[str, ...] = (
    "IntentionalContextEngine",
)