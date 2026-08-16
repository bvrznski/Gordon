# Canonical World Synchronization Serialization - Phase 4.9.6
# ============================================================
"""
Serialization support for WorldModelSynchronization subsystem.
No runtime dependencies; pure semantic definitions.
"""
from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(frozen=True, slots=True)
class Serializer:
    """
    Immutable serializer for world synchronization objects.
    
    Methods:
        serialize_snapshot:    Serialize snapshot to dict
        deserialize_snapshot:  Deserialize snapshot from dict
        serialize_graph:       Serialize graph to dict
        deserialize_graph:     Deserialize graph from dict
    
    Rules:
        - Serializer remains immutable
        - Round-trip serialization preserves semantics
    """
    identity: str = "serializer"


@dataclass(frozen=True, slots=True)
class Deserializer:
    """
    Immutable deserializer for world synchronization objects.
    
    Methods:
        deserialize_snapshot:  Deserialize snapshot from dict
        deserialize_graph:     Deserialize graph from dict
    
    Rules:
        - Deserializer remains immutable
        - Validation applied during deserialization
    """
    identity: str = "deserializer"


@dataclass(frozen=True, slots=True)
class SerializationEngine:
    """
    Engine for world synchronization serialization.
    
    Methods:
        serialize:  Serialize object to canonical format
        deserialize: Deserialize from canonical format
    
    Rules:
        - Deterministic output
        - Round-trip consistency preserved
    """
    identity: str = "serialization_engine"