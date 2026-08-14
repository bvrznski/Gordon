# Alerting Network Package Tree Contract
# =======================================
#
# This module defines the architectural tree contract for the AlertingNetwork.
# It specifies package responsibility, child module responsibilities, allowed and
# forbidden imports, public API boundaries, and extension policy.

"""
Alerting Network Package Architecture Contract
=============================================

Canonical Name:
    AlertingNetwork

Architectural Role:
    Exogenous attention-demand coordination network

Layer:
    Network (signal coordination, not implementation)

Operational Status:
    Phase 4.1.1 scaffolded but non-operational for full assessment
"""

from __future__ import annotations

# =============================================================================
# PACKAGE RESPONSIBILITY
# =============================================================================

PACKAGE_RESPONSIBILITY = """
The AlertingNetwork implements exogenous attention-demand coordination under the
canonical name AlertingNetwork.

It converts bounded signal evidence into advisory AlertingAssessment objects.
It does not maintain endogenous focus, authorize interruption, schedule
execution, route events, or perform actions.

The package owns:
    - alerting-domain vocabulary
    - immutable contracts (AlertingInput, AlertingContext, AlertingAssessment)
    - configuration architecture
    - state machine contracts (for later phases)
    - validation logic for contracts

The package does NOT own:
    - perceptual truth
    - global novelty truth
    - active objective
    - task policy
    - interruption authority
    - scheduling authority
    - action selection
"""

# =============================================================================
# CHILD MODULE RESPONSIBILITIES
# =============================================================================

CHILD_MODULE_RESOLVING = {
    # Core contracts and definitions
    "enums": """
        Alerting-specific enumerations (Level, Recommendation, ReasonCategory,
        Modality, SourceKind).
    """,
    
    "models": """
        Immutable data classes for input, context, assessment, features,
        modulation, reasons, provenance, and state snapshots.
    """,
    
    "configuration": """
        Immutable configuration architecture with nested value objects.
        Contains only contracts; no computational logic.
    """,
    
    "protocol": """
        Canonical abstract interface (AlertingNetworkProtocol).
        Defines assess(), snapshot_state(), reset() signatures.
    """,
    
    "network": """
        Concrete implementation of AlertingNetworkProtocol.
        For Phase 4.1.1: shell that rejects assessment calls until later phases.
    """,
    
    "exceptions": """
        Custom exception types for alerting domain errors.
    """,
    
    # Contracts package (contracts/)
    "contracts.identifiers": """
        Type aliases and identifier contracts (AlertingSignalId,
        AlertingAssessmentId, etc.).
    """,
    
    "contracts.input": """
        Input validation rules for AlertingInput.
    """,
    
    "contracts.context": """
        Context validation rules for AlertingContext.
    """,
    
    "contracts.features": """
        Features validation and bounds checking.
    """,
    
    "contracts.modulation": """
        Modulation composition constraints.
    """,
    
    "contracts.assessment": """
        Assessment invariants and cross-field consistency rules.
    """,
    
    "contracts.reasons": """
        Reason structure validity and completeness.
    """,
    
    "contracts.provenance": """
        Provenance tracking requirements.
    """,
    
    "contracts.state": """
        State transition contracts (for later phases).
    """,
    
    # Composition package (composition/)
    "composition.dependencies": """
        Dependency container (AlertingNetworkDependencies) withClockProtocol,
        IdentityProvider, MetricsPort, TracePort.
    """,
    
    # Validation package (validation/)
    "validation.contracts": """
        Contract validation functions.
    """,
    
    "validation.configuration": """
        Configuration validation.
    """,
    
    "validation.architecture": """
        Architectural invariants and forbidden dependency checks.
    """,
}

# =============================================================================
# ALLOWED IMPORT DIRECTIONS
# =============================================================================

ALLOWED_IMPORTS = {
    # Alerting can import Core contracts
    "alerting.*": [
        "^gordon_system\\.src\\.agent\\.core\\.",
        "^gordon_system\\.src\\.agent\\.architecture\\.",
    ],
    
    # Alerting cannot import:
    # - Concrete Execution types
    # - Other Network implementations (Focusing, Salience, etc.)
    # - Legacy alerting code
    "alerting.*": [
        "^gordon_system\\.src\\.agent\\.execution\\.threads\\.",
        "^gordon_system\\.src\\.agent\\.execution\\.loops\\.",
        "^gordon_system\\.src\\.agent\\.execution\\.cycles\\.",
        "^gordon_system\\.src\\.agent\\.components\\.networks\\.focusing\\.",
        "^gordon_system\\.src\\.agent\\.components\\.networks\\.salience\\.",
    ],
}

# =============================================================================
# FORBIDDEN IMPORTS
# =============================================================================

FORBIDDEN_IMPORTS = [
    # Cannot import concrete Execution types
    "from gordon_system.src.agent.execution.threads import ConcreteThread",
    "import gordon_system.src.agent.execution.loops.ConcreteLoop",
    
    # Cannot import other Network implementations
    "from gordon_system.src.agent.components.networks.focusing import FocusingNetwork",
    
    # Cannot import scheduler or action systems
    "import gordon_system.src.agent.core.scheduling",
    "import gordon_system.src.agent.execution.action",
]

# =============================================================================
# PUBLIC API
# =============================================================================

PUBLIC_API = {
    "classes": [
        "AlertingNetwork",
        "AlertingNetworkConfig",
        "AlertingInput",
        "AlertingContext",
        "AlertingAssessment",
        "AlertingFeatures",
        "AlertingModulation",
        "AlertingReason",
        "AlertingProvenance",
        "AlertingStateTransitionRecord",
        "AlertingNetworkStateSnapshot",
    ],
    
    "enums": [
        "AlertingLevel",
        "AlertingRecommendation",
        "AlertingSourceKind",
        "AlertingModality",
        "AlertingReasonCategory",
        "AlertingStateTransition",
    ],
}

# =============================================================================
# PRIVATE IMPLEMENTATION AREAS
# =============================================================================

PRIVATE_IMPLEMENTATION = {
    "state": """
        State store contracts and implementations (private, for later phases).
    """,
    
    "projection": """
        Input projection adapters (for later phases).
    """,
    
    "detection": """
        Signal detection algorithms (for later phases).
    """,
    
    "estimation": """
        Demand estimation algorithms (for later phases).
    """,
    
    "modulation": """
        Modulation computation (for later phases).
    """,
    
    "explanation": """
        Explanation generation (for later phases).
    """,
    
    "composition.factory": """
        Network factory functions.
    """,
}

# =============================================================================
# STATE OWNER
# =============================================================================

STATE_OWNER = """
The AlertingNetwork may own only bounded computational state:
    - Recent signal summary (bounded history)
    - Temporal baseline statistics
    - Habituation state
    - Refractory state
    - Diagnostic counters

It does NOT own:
    - Cognitive goals
    - Active task state
    - Full perceptual history
    - Global event history
    - Long-term memory
"""

# =============================================================================
# INTEGRATION BOUNDARIES
# =============================================================================

INTEGRATION_BOUNDARIES = """
Future Integration Points:

Input Side (downstream producers):
    Perception / Telemetry / System Events
        ↓
    AlertingInput (canonical projection)
        ↓
    AlertingNetwork

Output Side (consumers):
    AlertingAssessment (advisory evidence)
        ↓
    Executive / Arbitration / Workspace adapters

Neither Alerting nor Focusing should directly interact. Their outputs are
independently consumable by downstream arbitration.
"""

# =============================================================================
# EXTENSION POLICY
# =============================================================================

EXTENSION_POLICY = """
Extension Rules:
    1. New contract fields must be backward compatible (optional).
    2. New enum values must not break existing comparisons.
    3. Network behavior changes require phase bump.
    4. No breaking changes in public contracts between phases.

Future Phases:
    4.1.2  Alerting Signal Models and Computational State
    4.1.3  Alerting Feature Extraction and Temporal Analysis
    4.1.4  Alerting Demand Estimation and Modulation
    4.1.5  Alerting Network Runtime-Neutral Implementation
    4.1.6  Alerting Integration Contracts
    4.1.7  Alerting Behavioral and Computational Validation
    4.1.8  Alerting Architectural Audit
    4.1.9  Alerting Remediation
    4.1.10 Alerting Final Certification
"""

# =============================================================================
# CANONICAL STATEMENT
# =============================================================================

CANONICAL_STATEMENT = """
AlertingNetwork implements exogenous attention-demand coordination under the
canonical name AlertingNetwork. It converts bounded signal evidence into advisory
AlertingAssessment objects. It does not maintain endogenous focus, authorize
interruption, schedule execution, route events, or perform actions.
"""

# =============================================================================
# ARCHITECTURAL INVARIANTS
# =============================================================================

ARCHITECTURAL_INVARIANTS = {
    "ALERT-INV-001": "AlertingNetwork produces advisory assessments only.",
    "ALERT-INV-002": "AlertingNetwork never authorizes interruption.",
    "ALERT-INV-003": "AlertingNetwork never schedules execution.",
    "ALERT-INV-004": "AlertingNetwork never maintains endogenous focus.",
    "ALERT-INV-005": "AlertingNetwork state is bounded computational state.",
    "ALERT-INV-006": "AlertingNetwork accepts immutable projected input.",
    "ALERT-INV-007": "AlertingNetwork returns immutable assessment output.",
    "ALERT-INV-008": "Unknown modality is never silently converted.",
    "ALERT-INV-009": "AlertingNetwork has no production dependency on legacy code.",
    "ALERT-INV-010": "AlertingNetwork has no direct dependency on concrete sibling Networks.",
    "ALERT-INV-011": "Alerting and Focusing remain separate authorities.",
    "ALERT-INV-012": "Attention demand and behavioral authority remain separate.",
}

# =============================================================================
# ARCHITECTURAL LAWS
# =============================================================================

ARCHITECTURAL_LAWS = {
    "ALERT-LAW-001": "Unexpected demand is evidence, not authority.",
    "ALERT-LAW-002": "Externally driven attention and internally directed focus are distinct.",
    "ALERT-LAW-003": "A signal may request attention without winning attention.",
    "ALERT-LAW-004": "Alerting detects; arbitration resolves; execution transitions; Core performs.",
    "ALERT-LAW-005": "The Network coordinates alerting evidence but does not absorb its source domains.",
    "ALERT-LAW-006": "Agent-oriented functionality takes precedence over literal biological replication.",
    "ALERT-LAW-007": "Biological inspiration may justify mechanisms but never software ownership.",
    "ALERT-LAW-008": "All Alerting state must be bounded, local, and computational.",
    "ALERT-LAW-009": "Every assessment must be explainable through explicit evidence.",
    "ALERT-LAW-010": "No critical signal classification may directly become a runtime command.",
}

# =============================================================================
# ANTI-PATTERNS (PROHIBITED)
# =============================================================================

ANTI_PATTERNS = [
    "ExogenousAttentionNetwork = AlertingNetwork  # No compatibility aliases",
    "self._system = ExogenousAttentionSystem()  # No legacy wrapper",
    "self.current_focus_target = ...  # No focus ownership",
    "return InterruptCurrentThread(...)  # No direct interruption",
    "network.force_capture(...)  # No force capture",
    "return EmergencyStop(...)  # No emergency command",
    "self._focusing_network.suppress(...)  # No direct sibling call",
    "scheduler.preempt(thread_id)  # No direct scheduler call",
    "while self._running: process_signals()  # No runtime loop",
]