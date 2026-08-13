# Memory System - Phase 3.11.11 Canonical Semantic Stream Architecture
# =================================================================

"""
Memory System: Persistent representation and storage for memory artifacts.

Architecture:
    Perception → Consciousness → Cognition → Memory (persistent) → Streams (transport)

Memory System owns:
    - Persistent representation of memories
    - Storage engines and backends
    - Indexes and retrieval structures
    - Consolidation policies
    - Forgetting policies

Memory Streams own:
    - Publication of memory operations
    - Ordering of committed records
    - Replay for consumers
    - Checkpointing for recovery
"""

# Import core types
from .streams import (
    # Enums
    MemoryOperationKind,
    MemoryType,
    
    # Record types
    MemoryRecordId,
    MemoryArtifactReference,
    MemoryRecord,
    
    # Stream IDs
    MEMORY_STREAM_NAMESPACE,
    STREAM_MEMORY_ENCODING, MEMORY_ENCODING_STREAM_ID,
    STREAM_MEMORY_STORAGE, MEMORY_STORAGE_STREAM_ID,
    STREAM_MEMORY_RETRIEVAL, MEMORY_RETRIEVAL_STREAM_ID,
    STREAM_MEMORY_RECALL, MEMORY_RECALL_STREAM_ID,
    STREAM_WORKING_MEMORY, WORKING_MEMORY_STREAM_ID,
    STREAM_EPISODIC_MEMORY, EPISODIC_MEMORY_STREAM_ID,
    STREAM_SEMANTIC_MEMORY, SEMANTIC_MEMORY_STREAM_ID,
    STREAM_PROCEDURAL_MEMORY, PROCEDURAL_MEMORY_STREAM_ID,
    STREAM_ASSOCIATIVE_MEMORY, ASSOCIATIVE_MEMORY_STREAM_ID,
    STREAM_CONSOLIDATION, CONSOLIDATION_STREAM_ID,
    STREAM_FORGETTING, FORGETTING_STREAM_ID,
    STREAM_MEMORY_INDEX, MEMORY_INDEX_STREAM_ID,
    STREAM_MEMORY_RELATIONSHIP, MEMORY_RELATIONSHIP_STREAM_ID,
    
    # Builders
    MemoryRecordBuilder,
    create_memory_record,
    format_record_id,
)

__all__ = [
    "MemoryOperationKind",
    "MemoryType",
    "MemoryRecordId",
    "MemoryArtifactReference",
    "MemoryRecord",
    "MEMORY_STREAM_NAMESPACE",
    "STREAM_MEMORY_ENCODING", "MEMORY_ENCODING_STREAM_ID",
    "STREAM_MEMORY_STORAGE", "MEMORY_STORAGE_STREAM_ID",
    "STREAM_MEMORY_RETRIEVAL", "MEMORY_RETRIEVAL_STREAM_ID",
    "STREAM_MEMORY_RECALL", "MEMORY_RECALL_STREAM_ID",
    "STREAM_WORKING_MEMORY", "WORKING_MEMORY_STREAM_ID",
    "STREAM_EPISODIC_MEMORY", "EPISODIC_MEMORY_STREAM_ID",
    "STREAM_SEMANTIC_MEMORY", "SEMANTIC_MEMORY_STREAM_ID",
    "STREAM_PROCEDURAL_MEMORY", "PROCEDURAL_MEMORY_STREAM_ID",
    "STREAM_ASSOCIATIVE_MEMORY", "ASSOCIATIVE_MEMORY_STREAM_ID",
    "STREAM_CONSOLIDATION", "CONSOLIDATION_STREAM_ID",
    "STREAM_FORGETTING", "FORGETTING_STREAM_ID",
    "STREAM_MEMORY_INDEX", "MEMORY_INDEX_STREAM_ID",
    "STREAM_MEMORY_RELATIONSHIP", "MEMORY_RELATIONSHIP_STREAM_ID",
    "MemoryRecordBuilder",
    "create_memory_record",
    "format_record_id",
]