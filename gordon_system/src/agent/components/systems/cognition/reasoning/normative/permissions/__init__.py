# Normative Permissions Module
# ============================

"""
Permission analysis module for normative reasoning.

This module provides:
    - Permission identification and categorization
    - Permission scope tracking
    - Permission exceptions
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Tuple, Optional
import time
import uuid


@dataclass(frozen=True)
class PermissionState:
    """Current state of a permission."""
    
    state_id: str = field(default_factory=lambda: f"permission_state:{uuid.uuid4().hex[:16]}")
    permission_name: str
    granted: bool = True
    scope: str = "unrestricted"  # unrestricted, limited, conditional
    
    @classmethod
    def create(cls, permission_name: str, granted: bool = True,
               scope: str = "unrestricted") -> "PermissionState":
        return cls(permission_name=permission_name, granted=granted, scope=scope)


__all__ = ["PermissionState"]