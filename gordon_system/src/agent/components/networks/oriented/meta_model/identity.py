# Oriented Network Canonical Identity Specification
# ================================================

"""
Canonical identity specification for the Orientation Meta-Model.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True) 
class OrientationIdentity:
    """
    Canonical identity specification.
    
    The single unique identifier for this architecture that remains
    consistent across all views and representations.
    """
    
    unique_id: str = "oriented-network-meta-model-v4.7.12"
    """The canonical unique identifier."""
    
    semantic_identity: str = "OrientedNetwork.MetaModel"
    """Identity preserved across all views."""
    
    version_identifier: str = "4.7.12"
    """Current meta-model version."""
    
    def get_canonical_name(self) -> str:
        """Return the canonical name for this identity."""
        return "Oriented Network Meta-Model"