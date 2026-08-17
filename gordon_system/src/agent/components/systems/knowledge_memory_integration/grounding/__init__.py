# Knowledge-Memory Grounding Integration
# ======================================

"""
Grounding modules for Knowledge-Memory Integration.

Grounding links Knowledge Artifacts to retained Memory evidence,
ensuring that semantic commitments are traceable to their evidential basis.
"""

from .grounding import (
    KnowledgeMemoryGrounding,
    GroundingKind,
)

from .support_link import (
    KnowledgeMemorySupportLink,
    SupportKind,
)

from .contradiction_link import (
    KnowledgeMemoryContradictionLink,
    ContradictionKind,
)

__all__ = [
    "KnowledgeMemoryGrounding",
    "GroundingKind",
    "KnowledgeMemorySupportLink",
    "SupportKind",
    "KnowledgeMemoryContradictionLink",
    "ContradictionKind",
]