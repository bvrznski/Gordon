# Oriented Network Executive Integration Authority
# ===============================================

"""
Executive Integration Authority Types for Phase 4.7.6.

SEMANTIC INTEGRATION LAWS (Phase 4.7.6):
    INTEGRATION-LAW-002: Executive Network remains the sole owner of executive control.
    INTEGRATION-LAW-007: Integration never transfers ownership.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, Any, Tuple


@dataclass(frozen=True)
class ExecutiveAuthority:
    """
    Authority information for executive network integration.
    
    SEMANTIC LAWS (Phase 4.7.6):
        INTEGRATION-LAW-002: Executive Network remains the sole owner of executive control.
        INTEGRATION-LAW-008: Every subsystem possesses exactly one architectural authority.
    """
    
    identity: str = field(default="unnamed")
    """Unique semantic identifier for this authority"""
    
    source: str = "executive_network"
    """Source of executive authority"""
    
    scope: Tuple[str, ...] = field(default_factory=tuple)
    """Scope of authority (e.g., 'control', 'arbitration', 'supervision')"""
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "identity": self.identity,
            "source": self.source,
            "scope": self.scope,
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> ExecutiveAuthority:
        return cls(
            identity=data.get("identity", "unnamed"),
            source=data.get("source", "executive_network"),
            scope=tuple(data.get("scope", [])),
        )
    
    def validate(self) -> Tuple[bool, Tuple[str, ...]]:
        errors = []
        if not self.identity:
            errors.append("identity must be non-empty")
        return (len(errors) == 0, tuple(errors))


__all__ = ["ExecutiveAuthority"]