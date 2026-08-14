# Alerting Network Integration Contracts - Phase 4.1.6
# ======================================================
#
# Canonical integration contracts separating the Alerting Network from
# all downstream Gordon subsystems.
#
# ARCHITECTURAL PRINCIPLE:
# The Alerting Network is computationally complete and independent.
# All interactions with other systems occur through explicit, typed contracts.
# The Network never depends on implementation details of consumers.

"""
Canonical Integration Contracts for AlertingNetwork - Phase 4.1.6

This module establishes the immutable contracts governing all interactions
between the Alerting Network and downstream Gordon subsystems.

ARCHITECTURAL PRINCIPLES:
========================

Contract Ownership:
- The Alerting Network CONSUMES context but NEVER owns it
- The Alerting Network PROVIDES assessments but NEVER decides their fate
- All ownership remains with the original owner system

Dependency Direction:
    Capability/Executive
        ↓ (provides context, consumes assessment)
    Alerting Contract Layer
        ↓ (consumes input, provides output)
    Alerting Network
        ↓ (computational implementation)
    Computational Pipeline

The Network may depend ONLY on contracts. Never on implementations.

INPUT CONTRACTS (Network consumes):
- AlertingSignalProvider: Provides normalized signals
- AlertingContextProvider: Provides contextual modifiers
- AlertingStateProvider: Provides computational state

OUTPUT CONTRACTS (Network provides):
- AlertingAssessmentConsumer: Consumes completed assessments
- AlertingDiagnosticsSink: Receives traces/diagnostic data

CONFIGURATION:
- AlertingConfigurationProvider: Supports runtime-independent configuration

VALIDATION:
- AlertingValidationContract: Defines validation expectations
"""

from gordon_system.src.agent.components.networks.alerting.integration.contracts import (
    # Input Contracts (Network consumes)
    AlertingSignalProvider,
    AlertingContextProvider,
    AlertingStateProvider,
    
    # Output Contracts (Network provides)
    AlertingAssessmentConsumer,
    AlertingDiagnosticsSink,
    
    # Configuration
    AlertingConfigurationProvider,
    
    # Validation
    AlertingValidationContract,
)

from gordon_system.src.agent.components.networks.alerting.integration.types import (
    # Type definitions
    AssessmentDelivery,
    ContextSnapshot,
    SignalBatch,
    TracingEvent,
)

__all__ = (
    # Input Contracts
    "AlertingSignalProvider",
    "AlertingContextProvider", 
    "AlertingStateProvider",
    
    # Output Contracts
    "AlertingAssessmentConsumer",
    "AlertingDiagnosticsSink",
    
    # Configuration
    "AlertingConfigurationProvider",
    
    # Validation
    "AlertingValidationContract",
    
    # Types
    "AssessmentDelivery",
    "ContextSnapshot",
    "SignalBatch",
    "TracingEvent",
)