# Learning Reasoning Shared Contracts - Phase 7.24
# ================================================

"""
Shared contract types for the learning reasoning subsystem.

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
    LearningHealth          - Health metrics for learning
"""

from gordon_system.src.agent.components.systems.cognition.reasoning.learning.shared.descriptor import (
    LearningDescriptor,
    LearningSessionIdentity,
    LearningMode,
    LearningLifecycle,
)

__all__ = [
    # Descriptor
    "LearningDescriptor",
    "LearningSessionIdentity",
    "LearningMode",
    "LearningLifecycle",
]