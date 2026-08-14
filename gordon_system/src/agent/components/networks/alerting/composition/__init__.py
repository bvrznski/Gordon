# Alerting Network Composition Layer
# ====================================

"""
Composition layer for AlertingNetwork.

This layer provides dependency injection, factory patterns, and object
construction logic. It ensures the network is built from validated,
non-fabricated components.
"""

from gordon_system.src.agent.components.networks.alerting.composition.dependencies import (
    AlertingNetworkDependencies,
)

__all__ = ("AlertingNetworkDependencies",)