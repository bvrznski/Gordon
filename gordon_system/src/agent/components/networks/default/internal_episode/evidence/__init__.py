# Evidence Module Package
# =======================

"""
Evidence package for internal episode coordination.

Provides bounded, immutable evidence models for information collected during
episode processing.
"""

from __future__ import annotations

from .item import (
    InternalEpisodeEvidence,
    InternalEpisodeEvidenceId,
)

from .collection import (
    InternalEpisodeEvidenceCollection,
)

from .conflict import (
    InternalEpisodeEvidenceConflict,
    EvidenceConflictId,
)

from .provenance import (
    InternalEpisodeProvenance,
    RequestProvenance,
    ResultProvenance,
)

__all__ = [
    "InternalEpisodeEvidence",
    "InternalEpisodeEvidenceId",
    "InternalEpisodeEvidenceCollection",
    "InternalEpisodeEvidenceConflict",
    "EvidenceConflictId",
    "InternalEpisodeProvenance",
    "RequestProvenance",
    "ResultProvenance",
]