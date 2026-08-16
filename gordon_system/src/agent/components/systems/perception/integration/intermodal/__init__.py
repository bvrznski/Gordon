# Intermodal Correspondence - Phase 5.2.3
# =======================================

"""
Intermodal Correspondence: Evaluates relationships between artifacts from different modalities.

Correspondence answers:
    Do these artifacts appear to refer to the same entity, event, state,
    interval or environmental occurrence?
"""

from gordon_system.src.agent.components.systems.perception.integration.intermodal.request import IntermodalCorrespondenceRequest
from gordon_system.src.agent.components.systems.perception.integration.intermodal.result import (
    IntermodalCorrespondenceResult,
    CorrespondenceStatus,
    CorrespondenceEvidence,
    EvidenceKind,
)
from gordon_system.src.agent.components.systems.perception.integration.intermodal.correspondence import (
    IntermodalCorrespondence,
)
from gordon_system.src.agent.components.systems.perception.integration.intermodal.evidence import (
    CorrespondenceEvidence as EvidenceType,
)
from gordon_system.src.agent.components.systems.perception.integration.intermodal.alternative import (
    CorrespondenceAlternative,
)

__all__ = [
    "IntermodalCorrespondenceRequest",
    "IntermodalCorrespondenceResult",
    "CorrespondenceStatus",
    "IntermodalCorrespondence",
    "EvidenceType",
    "CorrespondenceAlternative",
]