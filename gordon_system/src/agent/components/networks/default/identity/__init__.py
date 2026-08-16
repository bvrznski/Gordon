# Identity Integration Module
# ===========================

"""
Identity integration coordination module.

This module implements the canonical coordination architecture through which the
Default Network integrates identity-relevant information into internally generated
cognition without owning authoritative identity authority.
"""

from gordon_system.src.agent.networks.default.identity.request import (
    IdentityIntegrationRequest,
)
from gordon_system.src.agent.networks.default.identity.purpose import (
    IdentityIntegrationPurpose,
)
from gordon_system.src.agent.networks.default.identity.subject import (
    IdentitySubject,
)
from gordon_system.src.agent.networks.default.identity.scope import (
    IdentityIntegrationScope,
)
from gordon_system.src.agent.networks.default.identity.episode import (
    IdentityIntegrationEpisode,
)
from gordon_system.src.agent.networks.default.identity.plan import (
    IdentityIntegrationPlan,
)
from gordon_system.src.agent.networks.default.identity.source import (
    IdentitySourceReference,
)
from gordon_system.src.agent.networks.default.identity.aspect import (
    IdentityAspect,
)
from gordon_system.src.agent.networks.default.identity.role import (
    IdentityRole,
)
from gordon_system.src.agent.networks.default.identity.value import (
    IdentityValueProjection,
)
from gordon_system.src.agent.networks.default.identity.commitment import (
    IdentityCommitmentProjection,
)
from gordon_system.src.agent.networks.default.identity.capability import (
    IdentityCapabilityAssessment,
)
from gordon_system.src.agent.networks.default.identity.limitation import (
    IdentityLimitationProjection,
)
from gordon_system.src.agent.networks.default.identity.claim import (
    IdentityClaim,
)
from gordon_system.src.agent.networks.default.identity.evidence import (
    IdentityEvidence,
)
from gordon_system.src.agent.networks.default.identity.continuity import (
    IdentityContinuityAssessment,
)
from gordon_system.src.agent.networks.default.identity.consistency import (
    IdentityConsistencyAssessment,
)
from gordon_system.src.agent.networks.default.identity.coherence import (
    IdentityCoherenceAssessment,
)
from gordon_system.src.agent.networks.default.identity.conflict import (
    IdentityConflict,
)
from gordon_system.src.agent.networks.default.identity.tension import (
    IdentityTension,
)
from gordon_system.src.agent.networks.default.identity.gap import (
    IdentityGap,
)
from gordon_system.src.agent.networks.default.identity.change import (
    IdentityChangeAssessment,
)
from gordon_system.src.agent.networks.default.identity.revision import (
    IdentityRevisionProposal,
)
from gordon_system.src.agent.networks.default.identity.product import (
    IdentityProduct,
)
from gordon_system.src.agent.networks.default.identity.outcome import (
    IdentityIntegrationOutcome,
)
from gordon_system.src.agent.networks.default.identity.continuation import (
    IdentityIntegrationContinuation,
)
from gordon_system.src.agent.networks.default.identity.configuration import (
    IdentityIntegrationConfig,
)
from gordon_system.src.agent.networks.default.identity.state.model import (
    IdentityIntegrationState,
)

__all__ = [
    # Requests and scope
    "IdentityIntegrationRequest",
    "IdentityIntegrationPurpose",
    "IdentitySubject",
    "IdentityIntegrationScope",
    "IdentityProjectionReference",
    "IdentitySourceReference",
    # Episode and plan
    "IdentityIntegrationEpisode",
    "IdentityIntegrationPlan",
    # Identity structures
    "IdentityAspect",
    "IdentityRole",
    "IdentityValueProjection",
    "IdentityCommitmentProjection",
    "IdentityCapabilityAssessment",
    "IdentityLimitationProjection",
    "IdentityClaim",
    "IdentityEvidence",
    # Assessments
    "IdentityContinuityAssessment",
    "IdentityConsistencyAssessment",
    "IdentityCoherenceAssessment",
    "IdentityConflict",
    "IdentityTension",
    "IdentityGap",
    "IdentityChangeAssessment",
    # Revision and products
    "IdentityRevisionProposal",
    "IdentityProduct",
    "IdentityIntegrationOutcome",
    "IdentityIntegrationContinuation",
    # Configuration and state
    "IdentityIntegrationConfig",
    "IdentityIntegrationState",
]