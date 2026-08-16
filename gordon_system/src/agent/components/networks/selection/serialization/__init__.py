# Gordon Cognitive Architecture - Phase 4.5.11
# ==============================================
#
"""
Action Selection Serialization Module

This module provides canonical serialization infrastructure for Action Selection artifacts.

PHASE: 4.5.11 — SERIALIZATION, CANONICAL ENCODING, SCHEMA EVOLUTION,
MIGRATION, REPLAY, DIGESTS, AND LONG-TERM COMPATIBILITY

OVERVIEW:
---------
This phase establishes deterministic, reversible, bounded, schema-aware
transformation between immutable Action Selection semantic artifacts and
transport-neutral canonical data representations.

ARCHITECTURAL PRINCIPLES:
--------------------------
1. Canonical serialization preserves semantic identity and meaning
2. Encoding and decoding perform no external work
3. Decoding never generates new semantic identities
4. Schema version, schema revision, artifact revision remain distinct
5. Unknown fields never grant authority, approval, or execution permission

ARTIFACT COVERAGE:
-----------------
- ActionSelectionOutcome
- FinalActionSelectionRequest
- ActionSelectionState
- ActionSelectionHistory
- ActionSelectionLineage
- ActionSelectionDelta
- ActionSelectionTransition
- ActionSelectionContinuation
- ActionSelectionFrontier
- SelectedAction
- And all related metadata artifacts

ARCHITECTURE:
-------------
serialization/
├── __init__.py          # This file - module exports
├── constants.py         # Canonical constants and enumerations
├── exceptions.py        # Serialization error hierarchy
│
├── canonical/           # Canonical value system
│   ├── document.py      # Top-level envelope structure
│   ├── payload.py       # Canonical data representation
│   ├── identifiers.py   # Typed identifiers
│   ├── revisions.py     # Revision representations
│   ├── references.py    # Artifact references
│   └── ordering.py      # Canonical collection ordering
│
├── formats/             # Encoding profiles
│   ├── json_profile.py  # Canonical JSON format
│   ├── cbor_profile.py  # Optional CBOR format (if supported)
│   └── messagepack_profile.py  # Optional MessagePack (if supported)
│
├── schema/              # Schema architecture
│   ├── identities.py    # Schema identity types
│   ├── versions.py      # Version management
│   ├── descriptors.py   # Field and union descriptors
│   ├── registry.py      # Runtime-neutral schema registry
│   └── compatibility.py # Compatibility assessment
│
├── codec/               # Encoder/Decoder contracts
│   ├── encoder.py       # Pure encoding API
│   ├── decoder.py       # Pure decoding API
│   ├── requests.py      # Request/result types
│   └── results.py
│
├── migration/           # Schema evolution and migration
│   ├── identities.py    # Migration identity types
│   ├── plan.py          # Migration plan structure
│   ├── steps.py         # Typed migration step kinds
│   ├── executor.py      # Pure migration function
│   └── result.py        # Migration result type
│
├── replay/              # Deterministic replay
│   ├── envelope.py      # Replay envelope structure
│   ├── plan.py          # Replay plan
│   ├── checkpoints.py   # Checkpoint tracking
│   └── result.py        # Replay result
│
├── digest/              # Deterministic digests
│   ├── algorithms.py    # Algorithm selection
│   ├── domains.py       # Domain separation
│   ├── digest.py        # Base digest type
│   ├── structural.py    # Structural digests
│   └── semantic.py      # Semantic digests
│
├── preservation/        # Long-term preservation
│   ├── profile.py       # Preservation profiles
│   ├── archive.py       # Archive formats
│   └── quarantine.py    # Quarantine handling
│
└── api.py               # Public API surface

NO EXTERNAL DEPENDENCIES:
-------------------------
- No database clients
- No file system access
- No network calls
- No pickle or eval/exec
- No external service invocation
"""

from __future__ import annotations

# Re-export public API for convenience
from gordon_system.src.agent.action.selection.serialization.constants import (
    DocumentFormat,
    SchemaEvolutionKind,
    CompatibilityDimension,
    MigrationStepKind,
    ReplayMode,
)

from gordon_system.src.agent.action.selection.serialization.exceptions import (
    ActionSelectionSerializationError,
    ActionSelectionEncodingError,
    ActionSelectionDecodingError,
    ActionSelectionDuplicateKeyError,
    ActionSelectionSchemaError,
    ActionSelectionMigrationError,
    ActionSelectionReplayError,
)

# Canonical types
from gordon_system.src.agent.action.selection.serialization.canonical.identifiers import (
    ActionSelectionCanonicalIdentifier,
)

from gordon_system.src.agent.action_selection.serialization.canonical.revisions import (
    ActionSelectionCanonicalRevision,
)

from gordon_system.src.agent.action_selection.serialization.canonical.references import (
    ActionSelectionCanonicalReference,
)

# Schema types
from gordon_system.src.agent.action.selection.serialization.schema.identities import (
    ActionSelectionSchemaIdentity,
)

from gordon_system.src.agent.action.selection.serialization.schema.versions import (
    ActionSelectionSchemaVersion,
)

from gordon_system.src.agent.action_selection.serialization.schema.descriptors import (
    ActionSelectionFieldDescriptor,
    ActionSelectionUnionDescriptor,
    ActionSelectionEnumDescriptor,
)

# Codec types
from gordon_system.src.agent.action.selection.serialization.codec.requests import (
    ActionSelectionEncodingRequest,
    ActionSelectionDecodingRequest,
)

from gordon_system.src.agent.action.selection.serialization.codec.results import (
    ActionSelectionEncodingResult,
    ActionSelectionDecodingResult,
)

__all__: tuple[str, ...] = (
    # Constants
    "DocumentFormat",
    "SchemaEvolutionKind",
    "CompatibilityDimension",
    "MigrationStepKind",
    "ReplayMode",
    
    # Exceptions
    "ActionSelectionSerializationError",
    "ActionSelectionEncodingError",
    "ActionSelectionDecodingError",
    "ActionSelectionDuplicateKeyError",
    "ActionSelectionSchemaError",
    "ActionSelectionMigrationError",
    "ActionSelectionReplayError",
    
    # Canonical types
    "ActionSelectionCanonicalIdentifier",
    "ActionSelectionCanonicalRevision",
    "ActionSelectionCanonicalReference",
    
    # Schema types
    "ActionSelectionSchemaIdentity",
    "ActionSelectionSchemaVersion",
    "ActionSelectionFieldDescriptor",
    "ActionSelectionUnionDescriptor",
    "ActionSelectionEnumDescriptor",
    
    # Codec types
    "ActionSelectionEncodingRequest",
    "ActionSelectionDecodingRequest",
    "ActionSelectionEncodingResult",
    "ActionSelectionDecodingResult",
)