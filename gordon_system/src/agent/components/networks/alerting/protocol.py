# Alerting Network Protocol
# =========================

"""
Canonical abstract protocol for the AlertingNetwork.

This module defines the AlertingNetworkProtocol that all AlertingNetwork
implementations must satisfy. It describes the public interface for assessing
exogenous attention demand.
"""

from __future__ import annotations

from typing import Protocol, Optional

from gordon_system.src.agent.components.networks.alerting.models import (
    AlertingInput,
    AlertingAssessment,
    AlertingNetworkStateSnapshot,
)


class AlertingNetworkProtocol(Protocol):
    """
    Canonical abstract protocol for AlertingNetwork.

    This defines the minimal interface that any AlertingNetwork implementation
    must provide. It does not specify runtime behavior, only the contract for
    assessment and state management.
    """

    def assess(
        self,
        alerting_input: AlertingInput,
    ) -> AlertingAssessment:
        """
        Assess exogenous attention demand for a signal.

        Args:
            alerting_input: A canonical projection of evidence relevant to
                exogenous attention.

        Returns:
            An immutable AlertingAssessment containing:
                - Demand score (0.0 to 1.0)
                - Confidence in the assessment
                - AlertingLevel classification
                - Advisory AlertingRecommendation
                - Computed features for explainability
                - Modulation evidence
                - Reasons for the assessment
                - Provenance tracking

        Note:
            The assessment is advisory only. It does NOT command behavior.
            Downstream consumers decide whether and how to act on it.
        """
        ...

    def snapshot_state(
        self,
    ) -> AlertingNetworkStateSnapshot:
        """
        Produce an immutable snapshot of the network's internal state.

        Returns:
            An AlertingNetworkStateSnapshot containing:
                - Bounded temporal baseline statistics
                - Recent signal history summary
                - Habituation state
                - Refractory state
                - Diagnostic counters

        Note:
            The snapshot captures only bounded computational state. It does NOT
            include cognitive goals, active task state, or global history.
        """
        ...

    def reset(
        self,
        reset_request: "AlertingResetRequest",
    ) -> AlertingNetworkStateSnapshot:
        """
        Reset the network to a clean state.

        Args:
            reset_request: Specifies what should be reset (e.g., all state,
                only habituation, only refractory).

        Returns:
            A fresh AlertingNetworkStateSnapshot after reset.
        """
        ...