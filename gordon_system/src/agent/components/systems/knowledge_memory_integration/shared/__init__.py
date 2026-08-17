# Knowledge-Memory Integration Shared Modules
# ==============================================

"""
Shared contract definitions for Knowledge-Memory Integration.

This module provides the foundational types used throughout the
Knowledge-Memory Integration layer:
- Request/Response models for cross-system operations
- Confidence and uncertainty tracking
- Provenance and synchronization metadata
"""

from .request import (
    RequestKind,
    TemporalScope,
    SemanticScope,
    KnowledgeMemoryRequest,
)

from .response import (
    ResponseStatus,
    ResultKind,
    KnowledgeMemoryResponse,
)

__all__ = [
    "RequestKind",
    "TemporalScope",
    "SemanticScope",
    "KnowledgeMemoryRequest",
    "ResponseStatus",
    "ResultKind",
    "KnowledgeMemoryResponse",
]