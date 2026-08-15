# Gordon Workspace Network - Phase 4.6 Metadata
# ==============================================

"""
Phase: 4.6
Canonical subsystem: Workspace Network (Global Workspace Network, GWN)
Architectural layer: Network Layer
Status: PHASE 4.6.1 COMPLETE - Canonical semantic foundations established

This package implements the canonical Workspace Network subsystem which coordinates
bounded global cognitive availability through Candidate admission, evaluation,
competitive arbitration, selection, activation, broadcast, and distribution.

VERSION: 0.1.0-alpha
"""

__version__ = "0.1.0-alpha"
__author__ = "Gordon Cognitive Agent Team"
__status__ = "alpha"

# =============================================================================
# PHASE COMPLETION FLAGS
# =============================================================================

PHASE_4_6_1_COMPLETE = True     # Canonical semantic foundations (semantic specification)
PHASE_4_6_2_COMPLETE = True     # Repository discovery & legacy inventory
PHASE_4_6_3_COMPLETE = False    # Canonical Workspace semantics (superseded by 4.6.1)
PHASE_4_6_4_PENDING = False     # Workspace Content implementation
PHASE_4_6_5_PENDING = False     # Candidate admission implementation
PHASE_4_6_6_PENDING = False     # Candidate Pool implementation
PHASE_4_6_7_PENDING = False     # Evaluation implementation
PHASE_4_6_8_PENDING = False     # Competition implementation
PHASE_4_6_9_PENDING = False     # Selection implementation
PHASE_4_6_10_PENDING = False    # Activation implementation
PHASE_4_6_11_PENDING = False    # Broadcast implementation
PHASE_4_6_12_PENDING = False    # Distribution contracts implementation
PHASE_4_6_13_PENDING = False    # State architecture implementation
PHASE_4_6_14_PENDING = False    # History, Lineage, Delta, Transition implementation
PHASE_4_6_15_PENDING = False    # Runtime cycle implementation
PHASE_4_6_16_PENDING = False    # Observability implementation
PHASE_4_6_17_PENDING = False    # Configuration implementation
PHASE_4_6_18_PENDING = False    # Serialization and migration implementation
PHASE_4_6_19_PENDING = False    # Final certification implementation

# =============================================================================
# ARCHITECTURAL BOUNDARIES
# =============================================================================

COGNITIVE_AUTHORITIES_REMAIN_EXTERNAL = True
WORKING_MEMORY_EXTERNAL = True
EXECUTIVE_COORDINATION_EXTERNAL = True
CORE_RUNTIME_EXTERNAL = True

# =============================================================================
# CANONICAL DEFINITION
# =============================================================================

CANONICAL_DEFINITION = """
The Workspace Network is Gordon's bounded inter-capability coordination network
for admitting, evaluating, competitively arbitrating, selecting, and globally
exposing currently relevant cognitive content to eligible consumers.

It answers: Which information becomes globally available? How is selective
broadcasting achieved? What integrates across cognitive systems?

It does NOT own: perception, reasoning, memory, Working Memory, planning,
imagination, motivation, Decisions, Actions, execution, capability implementations,
persistent domain State, knowledge, transport infrastructure.
"""

# =============================================================================
# PHASE 4.6.1 STATUS - SEMANTIC FOUNDATIONS COMPLETE
# =============================================================================

"""
Phase 4.6.1 established canonical semantic foundations for the Workspace Network.

The semantic specification document at:
    docs/agent/architecture/phase-4.6.1-semantic-specification.md

defines what the Workspace Network is, not how it operates at runtime.

All subsequent phases (4.6.2-4.6.19) must derive their meaning from Phase 4.6.1.
"""