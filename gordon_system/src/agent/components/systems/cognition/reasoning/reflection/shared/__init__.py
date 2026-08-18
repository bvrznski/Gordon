# Reflection Reasoning - Shared Components
# =========================================

"""
Shared components for reflection reasoning system.

This module provides:
- Reflection descriptors and metadata
- Reflection sets (scope definition)
- Pipeline orchestration
- Experience synthesis
- Self-explanation
- Lesson extraction
- Consolidation
- Validation
- Governance
- Diagnostics
"""

from gordon_system.src.agent.components.systems.cognition.reasoning.reflection.shared.descriptor import (
    ReflectionDescriptor,
)

from gordon_system.src.agent.components.systems.cognition.reasoning.reflection.shared.reflection_set import (
    ReflectionSet,
)

from gordon_system.src.agent.components.systems.cognition.reasoning.reflection.shared.pipeline import (
    ReflectionPipeline,
    ReflectionStage,
)

from gordon_system.src.agent.components.systems.cognition.reasoning.reflection.shared.synthesis import (
    ExperienceSynthesis,
    ExperienceSynthesisManagement,
)

from gordon_system.src.agent.components.systems.cognition.reasoning.reflection.shared.explanation import (
    SelfExplanation,
    SelfExplanationManagement,
)

from gordon_system.src.agent.components.systems.cognition.reasoning.reflection.shared.lessons import (
    ExtractedLesson,
    LessonManagement,
)

from gordon_system.src.agent.components.systems.cognition.reasoning.reflection.shared.consolidation import (
    ConsolidationCandidate,
    ReflectionConsolidation,
    ConsolidationManagement,
)

from gordon_system.src.agent.components.systems.cognition.reasoning.reflection.shared.validation import (
    ReflectionValidation,
    ReflectionFailure,
    ReflectionGovernance,
)

from gordon_system.src.agent.components.systems.cognition.reasoning.reflection.shared.diagnostics import (
    ReflectionHealth,
    ReflectionDiagnostics,
)

__all__ = [
    # Shared
    "ReflectionDescriptor",
    "ReflectionSet",
    "ReflectionPipeline",
    "ReflectionStage",
    # Synthesis
    "ExperienceSynthesis",
    "ExperienceSynthesisManagement",
    # Explanation
    "SelfExplanation",
    "SelfExplanationManagement",
    # Lessons
    "ExtractedLesson",
    "LessonManagement",
    # Consolidation
    "ConsolidationCandidate",
    "ReflectionConsolidation",
    "ConsolidationManagement",
    # Validation
    "ReflectionValidation",
    "ReflectionFailure",
    "ReflectionGovernance",
    # Diagnostics
    "ReflectionHealth",
    "ReflectionDiagnostics",
]