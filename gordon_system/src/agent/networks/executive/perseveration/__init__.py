# Executive Network Perseveration Module
# =======================================

"""
Canonical executive perseverance and perseveration detection for Phase 4.4.8.

Perseveration is defined as:
    The maladaptive persistence or repeated reactivation of an executive
    configuration, strategy, task set, response, reasoning path, action
    candidate, or control pattern despite evidence that continuation is
    ineffective, invalid, obsolete, or harmful.

Perseveration is NOT ordinary persistence.
Persistence is adaptive when the active configuration remains justified.

This module provides detection and assessment of perseverative patterns
to distinguish them from appropriate persistence.
"""

from __future__ import annotations

# Core perseverance contracts
from gordon_system.src.agent.networks.executive.perseveration.assessment import (
    ExecutivePerseverationAssessment,
)

from gordon_system.src.agent.networks.executive.perseveration.kind import (
    ExecutivePerseverationKind,
)

from gordon_system.src.agent.networks.executive.perseveration.status import (
    ExecutivePerseverationStatus,
)

from gordon_system.src.agent.networks.executive.perseveration.severity import (
    ExecutivePerseverationSeverity,
)

from gordon_system.src.agent.networks.executive.perseveration.persistence import (
    ExecutivePerseverationPersistence,
)

__all__ = [
    "ExecutivePerseverationAssessment",
    "ExecutivePerseverationKind",
    "ExecutivePerseverationStatus",
    "ExecutivePerseverationSeverity",
    "ExecutivePerseverationPersistence",
]