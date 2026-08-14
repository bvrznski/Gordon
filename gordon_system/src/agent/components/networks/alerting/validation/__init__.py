# Alerting Network Validation Layer
# ===================================

"""
Validation layer for AlertingNetwork.

This layer provides contract, configuration, dependency, and architectural
validation without embedding runtime behavior.
"""

from gordon_system.src.agent.components.networks.alerting.validation.contracts import (
    validate_alerting_input,
)
from gordon_system.src.agent.components.networks.alerting.validation.configuration import (
    validate_alerting_config,
)
from gordon_system.src.agent.components.networks.alerting.validation.architecture import (
    ALERTING_INVARIANTS,
)

__all__ = (
    "validate_alerting_input",
    "validate_alerting_config",
    "ALERTING_INVARIANTS",
)