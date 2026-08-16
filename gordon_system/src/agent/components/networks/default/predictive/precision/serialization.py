# Precision Serialization - Phase 4.9.4
# =======================================

"""
Serialization support for Precision Estimation Engine.

Provides canonical deterministic serialization for precision estimates and landscapes.
"""

from __future__ import annotations

import json
from typing import Any


def serialize_precision_estimate(estimate: dict[str, Any]) -> str:
    """
    Serialize a precision estimate to JSON string.
    
    Args:
        estimate: PrecisionEstimate as dictionary
        
    Returns:
        Deterministic JSON string representation
    """
    # Ensure deterministic ordering by sorting keys
    return json.dumps(estimate, sort_keys=True, indent=None, separators=(",", ":"))


def deserialize_precision_estimate(json_str: str) -> dict[str, Any]:
    """
    Deserialize a precision estimate from JSON string.
    
    Args:
        json_str: Serialized precision estimate
        
    Returns:
        PrecisionEstimate as dictionary
    """
    return json.loads(json_str)


def serialize_precision_landscape(landscape: dict[str, Any]) -> str:
    """
    Serialize a precision landscape to JSON string.
    
    Args:
        landscape: PrecisionLandscape as dictionary
        
    Returns:
        Deterministic JSON string representation
    """
    return json.dumps(landscape, sort_keys=True, indent=None, separators=(",", ":"))


def deserialize_precision_landscape(json_str: str) -> dict[str, Any]:
    """
    Deserialize a precision landscape from JSON string.
    
    Args:
        json_str: Serialized precision landscape
        
    Returns:
        PrecisionLandscape as dictionary
    """
    return json.loads(json_str)