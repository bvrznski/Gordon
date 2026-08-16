# Memory Foundations - Phase 5.1 Canonical Semantic Substrate
# =============================================================

"""
Memory Foundations: The semantic substrate for Gordon's persistent memory system.

This module implements the foundation layer of the Memory System as specified in
Phase 5.1 of the Gordon Cognitive Architecture.

Architecture Summary:
    ┌─────────────────────────────────────────────────────────────────┐
    │                    MEMORY SYSTEM                                │
    ├─────────────────────────────────────────────────────────────────┤
    │                                                                 │
    │   owns                                                          │
    │   └── Memory Substrate (persistent semantic medium)            │
    │        ├── Memory Artifacts (semantic units)                   │
    │        ├── Memory Relations (semantic graph edges)             │
    │        ├── Memory Identities (stable identifiers)              │
    │        ├── Memory Revisions (versioned evolution)              │
    │        ├── Memory Provenance (origin tracking)                 │
    │        ├── Memory Validity (validation states)                 │
    │        └── Memory State (substrate summary)                    │
    │                                                                 │
    │   exposes                                                       │
    │        ├── Memory Projection (immutable view)                  │
    │        └── Memory Query (read-only access)                     │
    │                                                                 │
    └─────────────────────────────────────────────────────────────────┘

Core Principles:
    - Memory is a persistent semantic substrate, not storage
    - Artifacts are immutable; revisions create new artifacts
    - Identity survives revisions
    - Provenance is complete and preserved
    - Relations form a semantic graph
    - Ownership is exclusive to Memory System
"""

# =============================================================================
# FOUNDATION LAYER EXPORTS (lazy imports to avoid circular deps)
# =============================================================================

from .artifact import MemoryArtifact, MemoryArtifactKind, MemoryArtifactStatus, MemoryArtifactBuilder


__all__ = [
    "MemoryArtifact",
    "MemoryArtifactKind",
    "MemoryArtifactStatus",
    "MemoryArtifactBuilder",
]