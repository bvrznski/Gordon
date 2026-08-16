# Oriented Network Serialization Support
# =======================================

"""
Serialization support for the Canonical Orientation Meta-Model.

Every representation shall support deterministic serialization.
"""

from __future__ import annotations

import json
from dataclasses import asdict, is_dataclass


def serialize(obj) -> dict:
    """
    Serialize a dataclass or object to a deterministic JSON-compatible dict.
    
    This function handles frozen dataclasses and produces consistent output.
    """
    if is_dataclass(obj):
        result = {}
        for field_name in dir(obj):
            if not field_name.startswith('_'):
                value = getattr(obj, field_name)
                result[field_name] = serialize(value)
        return result
    elif isinstance(obj, (list, tuple)):
        return [serialize(item) for item in obj]
    elif isinstance(obj, dict):
        return {k: serialize(v) for k, v in obj.items()}
    elif hasattr(obj, 'value'):
        return serialize(obj.value)
    else:
        return obj


def to_json(obj) -> str:
    """Convert object to deterministic JSON string."""
    return json.dumps(serialize(obj), sort_keys=True)


class SerializationMixin:
    """
    Mixin providing serialization support for meta-model components.
    
    This mixin adds serialization capabilities without affecting
    the immutable nature of the dataclasses it's mixed into.
    """
    
    def to_dict(self) -> dict:
        """Serialize to a dictionary."""
        return serialize(self)
    
    def to_json(self) -> str:
        """Serialize to JSON string."""
        return json.dumps(serialize(self), sort_keys=True)