# Default Network Integration Contracts - Architecture Tree (Phase 4.3.13)
# =========================================================================

"""
Architecture tree for the Default Network Integration Contracts package.

This module defines the structural representation of the integration contract layer.
"""

from __future__ import annotations


class IntegrationContractsTree:
    """Represent the architecture tree for Phase 4.3.13."""
    
    PACKAGE_NAME = "default_network_integration"
    VERSION = "0.1.0"
    
    # =============================================================================
    # DIRECTORY STRUCTURE (Phase 4.3.13)
    # =============================================================================
    
    DIRECTORIES = [
        "execution/",
        "core/",
        "context/",
        "capabilities/",
        "networks/",
        "authorities/",
        "projections/",
        "proposals/",
        "diagnostics/",
        "replay/",
        "validation/",
    ]
    
    # =============================================================================
    # PORT DEFINITIONS (Phase 4.3.13)
    # =============================================================================
    
    INBOUND_PORTS = [
        {
            "id": "invocation",
            "name": "DefaultNetworkInvocationPort",
            "direction": "INBOUND",
            "description": "Execution invokes Default Network for one bounded semantic progression",
        },
        {
            "id": "context_projection",
            "name": "InternalContextProjectionPort",
            "direction": "INBOUND",
            "description": "External context projection is supplied to the network",
        },
        {
            "id": "memory_projection",
            "name": "MemoryProjectionPort",
            "direction": "INBOUND",
            "description": "Memory projection is supplied to the network",
        },
        {
            "id": "identity_projection",
            "name": "IdentityProjectionPort",
            "direction": "INBOUND",
            "description": "Identity projection is supplied to the network",
        },
        {
            "id": "observation_projection",
            "name": "ObservationProjectionPort",
            "direction": "INBOUND",
            "description": "Observation projection is supplied to the network",
        },
        {
            "id": "workspace_feedback",
            "name": "WorkspaceFeedbackProjectionPort",
            "direction": "INBOUND",
            "description": "Workspace feedback is supplied to the network",
        },
    ]
    
    OUTBOUND_PORTS = [
        {
            "id": "reflection_request",
            "name": "ReflectionCapabilityRequestPort",
            "direction": "OUTBOUND",
            "description": "Request reflection capability for semantic computation",
        },
        {
            "id": "simulation_request",
            "name": "SimulationCapabilityRequestPort",
            "direction": "OUTBOUND",
            "description": "Request simulation capability for counterfactual analysis",
        },
        {
            "id": "narrative_request",
            "name": "NarrativeCapabilityRequestPort",
            "direction": "OUTBOUND",
            "description": "Request narrative integration support",
        },
        {
            "id": "memory_projection_request",
            "name": "MemoryProjectionRequestPort",
            "direction": "OUTBOUND",
            "description": "Request memory projection refresh",
        },
        {
            "id": "predictive_request",
            "name": "PredictiveCapabilityRequestPort",
            "direction": "OUTBOUND",
            "description": "Request predictive capability for forecasting",
        },
    ]
    
    # =============================================================================
    # ARCHITECTURAL INVARIANTS (Phase 4.3.13)
    # =============================================================================
    
    ARCHITECTURAL_INVARIANTS = [
        "DEFAULT-INT-INV-001: Every integration occurs through an explicit typed port",
        "DEFAULT-INT-INV-002: Every port has one explicit semantic owner and direction",
        "DEFAULT-INT-INV-003: Ports define semantics; adapters define delivery",
        "DEFAULT-INT-INV-004: No contract contains a live external implementation object",
        "DEFAULT-INT-INV-005: Every inbound result references a known outbound request",
        "DEFAULT-INT-INV-006: Every authority decision references a known proposal and target revision",
        "DEFAULT-INT-INV-007: Correlation and causation remain distinct",
        "DEFAULT-INT-INV-008: Every externally deliverable request has an idempotency key",
        "DEFAULT-INT-INV-009: Duplicate delivery does not cause duplicate semantic effects",
        "DEFAULT-INT-INV-010: Arrival order is not used unless the contract declares ordering semantics",
        "DEFAULT-INT-INV-011: Schema version is distinct from semantic entity revision",
        "DEFAULT-INT-INV-012: Compatibility is validated before payload integration",
        "DEFAULT-INT-INV-013: Adapters may not strengthen factuality",
        "DEFAULT-INT-INV-014: Adapters may not weaken privacy or disclosure restrictions",
        "DEFAULT-INT-INV-015: Adapters may not fabricate missing authority or provenance",
    ]
    
    # =============================================================================
    # CONTRACT CATEGORIES (Phase 4.3.13)
    # =============================================================================
    
    CONTRACT_CATEGORIES = [
        {
            "name": "Inbound Invocation Contract",
            "description": "Allows an authorized caller to request one bounded Default Network progression",
            "contract_type": "DefaultNetworkInvocation",
        },
        {
            "name": "Inbound Projection Contract",
            "description": "Supplies immutable externally owned semantic state",
            "contract_types": [
                "IdentityProjection",
                "MemoryProjection",
                "ObservationProjection",
                "WorkspaceFeedbackProjection",
            ],
        },
        {
            "name": "Inbound Result Contract",
            "description": "Supplies the result of a previously issued external request",
            "contract_type": "CapabilityResultEnvelope",
        },
        {
            "name": "Inbound Authority-Decision Contract",
            "description": "Supplies a decision from an external owner",
            "contract_types": [
                "WorkspaceAdmissionDecision",
                "IdentityRevisionDecision",
                "ExecutiveReviewDecision",
            ],
        },
        {
            "name": "Outbound Capability-Request Contract",
            "description": "Requests externally owned specialized computation",
            "contract_types": [
                "ReflectionCapabilityRequest",
                "SimulationCapabilityRequest",
                "MemoryProjectionRequest",
            ],
        },
        {
            "name": "Outbound Proposal Contract",
            "description": "Asks an external authority to review a possible change or action",
            "contract_types": [
                "MemoryUpdateProposal",
                "IdentityRevisionProposal",
                "WorkspaceSubmissionProposal",
            ],
        },
    ]
    
    # =============================================================================
    # OWNERSHIP (Phase 4.3.13)
    # =============================================================================
    
    OWNERSHIP = {
        "default_network_integration_layer": [
            "integration-domain contracts",
            "port definitions",
            "immutable request and result envelopes",
            "correlation requirements",
            "causation requirements",
            "idempotency requirements",
            "authority references",
            "revision references",
            "type discriminators",
            "schema versions",
            "factuality propagation rules",
            "privacy propagation rules",
            "disclosure propagation rules",
            "bounded diagnostics",
            "integration validation",
            "compatibility declarations",
            "conformance tests",
            "integration documentation",
        ],
        "NOT_OWNED": [
            "provider selection",
            "service discovery",
            "network transport",
            "message brokers",
            "event buses",
            "RPC frameworks",
            "HTTP clients",
            "retries",
            "runtime deadlines",
            "queues",
            "scheduling",
            "task execution",
            "worker assignment",
            "resource allocation",
            "persistence engines",
            "authentication implementation",
            "authorization implementation",
            "external subsystem state",
            "dependency-injection framework configuration",
        ],
    }


def get_architecture_tree() -> dict:
    """Return the complete architecture tree as a dictionary."""
    return {
        "package_name": IntegrationContractsTree.PACKAGE_NAME,
        "version": IntegrationContractsTree.VERSION,
        "directories": IntegrationContractsTree.DIRECTORIES,
        "inbound_ports": IntegrationContractsTree.INBOUND_PORTS,
        "outbound_ports": IntegrationContractsTree.OUTBOUND_PORTS,
        "architectural_invariants": IntegrationContractsTree.ARCHITECTURAL_INVARIANTS,
        "contract_categories": IntegrationContractsTree.CONTRACT_CATEGORIES,
        "ownership": IntegrationContractsTree.OWNERSHIP,
    }


if __name__ == "__main__":
    import json
    print(json.dumps(get_architecture_tree(), indent=2))