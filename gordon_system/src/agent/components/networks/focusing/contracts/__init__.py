# Focusing Network Contracts
# ===========================

"""
Contract interfaces for the FocusingNetwork.

These define stable architectural contracts that decouple the network from
implementation details of producers and consumers. The FocusingNetwork depends
only on these contracts, never concrete implementations.
"""

from gordon_system.src.agent.components.networks.focusing.contracts.inputs import (
    FocusCandidateProvider,
    FocusContextProvider,
)
from gordon_system.src.agent.components.networks.focusing.contracts.outputs import (
    FocusAssessmentConsumer,
    FocusDiagnosticsSink,
)
from gordon_system.src.agent.components.networks.focusing.contracts.providers import (
    FocusStateProvider,
    FocusConfigurationProvider,
)
from gordon_system.src.agent.components.networks.focusing.contracts.consumers import (
    FocusInputConsumer,
)

__all__ = [
    "FocusCandidateProvider",
    "FocusContextProvider",
    "FocusAssessmentConsumer",
    "FocusDiagnosticsSink",
    "FocusStateProvider",
    "FocusConfigurationProvider",
    "FocusInputConsumer",
]