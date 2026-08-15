# Executive Demand Persistence Types
# ===================================

"""
Types for assessing demand persistence.

Demand persistence may differ from conflict persistence. One conflict may
be persistent while demand declines after successful mitigation.
"""

from __future__ import annotations

from typing import Tuple


class ExecutiveDemandPersistence:
    """
    Classes for executive demand persistence assessment.
    
    Demand persistence may differ from conflict persistence. One conflict may
    be persistent while demand declines after successful mitigation.
    """
    
    TRANSIENT = "transient"
    TEMPORARY = "temporary"
    PERSISTENT = "persistent"
    RECURRING = "recurring"
    ESCALATING = "escalating"
    DECLINING = "declining"
    RESOLVED = "resolved"
    UNKNOWN = "unknown"

    @classmethod
    def all_classes(cls) -> Tuple[str, ...]:
        return tuple(v for k, v in vars(cls).items() if not k.startswith('_') and isinstance(v, str))


__all__: Tuple[str, ...] = ("ExecutiveDemandPersistence",)