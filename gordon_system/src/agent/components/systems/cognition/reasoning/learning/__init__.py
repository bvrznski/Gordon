# Learning Reasoning - Phase 7.24
# =================================

"""
Learning Reasoning subsystem for Gordon Cognitive Architecture.

This module provides canonical implementations of all learning reasoning contracts:

    LearningDescriptor      - Metadata about learning operations
    LearningSessionIdentity - Identity for learning sessions
    LearningPipeline        - Pipeline of learning stages
    KnowledgeAcquisition    - Knowledge acquisition with evidence
    GeneralizationModel     - Generalized concepts from examples
    LearningRefinement      - Model refinements with rationale
    ExperienceIntegration   - Integration of learned knowledge
    LearningFailure         - Failure records with diagnostics
    LearningGovernance      - Governance evaluation of learning
    LearningValidation      - Validation results for learning

Learning Reasoning transforms evaluated experience into permanent cognitive
improvements. It never performs persistent storage directly.

See Phase 7.24 specification for full architectural details.
"""

from gordon_system.src.agent.components.systems.cognition.reasoning.learning.shared import (
    LearningDescriptor,
    LearningSessionIdentity,
    LearningMode,
    LearningLifecycle,
)

from gordon_system.src.agent.components.systems.cognition.reasoning.learning.acquisition import (
    KnowledgeAcquisition,
    AcquisitionPolicy,
    AcquisitionMetrics,
)

from gordon_system.src.agent.components.systems.cognition.reasoning.learning.failure import (
    LearningFailure,
)

from gordon_system.src.agent.components.systems.cognition.reasoning.learning.governance import (
    LearningGovernance,
    GovernanceViolation,
)

from gordon_system.src.agent.components.systems.cognition.reasoning.learning.validation import (
    LearningValidation,
)

__all__ = [
    # Shared
    "LearningDescriptor",
    "LearningSessionIdentity",
    "LearningMode",
    "LearningLifecycle",
    
    # Acquisition
    "KnowledgeAcquisition",
    "AcquisitionPolicy",
    "AcquisitionMetrics",
    
    # Failure
    "LearningFailure",
    
    # Governance
    "LearningGovernance",
    "GovernanceViolation",
    
    # Validation
    "LearningValidation",
]