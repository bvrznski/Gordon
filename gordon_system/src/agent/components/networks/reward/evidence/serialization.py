# Reward Network - Evidence Serialization
# =======================================

"""
Evidence serialization module.

Provides deterministic serialization and deserialization for evidence items.
"""

from __future__ import annotations

import json
from dataclasses import asdict
from typing import Any


def serialize_evidence(evidence: dict | Any) -> str:
    """
    Serialize an evidence dictionary to JSON string.

    Args:
        evidence: Evidence dictionary or object to serialize

    Returns:
        JSON string representation
    """
    if hasattr(evidence, "__dataclass_fields__"):
        # It's a dataclass - convert to dict first
        evidence_dict = asdict(evidence)
    elif isinstance(evidence, dict):
        evidence_dict = evidence
    else:
        raise ValueError(f"Cannot serialize type {type(evidence)}")

    return json.dumps(evidence_dict)


def deserialize_evidence(json_str: str) -> dict:
    """
    Deserialize JSON string to evidence dictionary.

    Args:
        json_str: JSON string representation

    Returns:
        Evidence dictionary
    """
    return json.loads(json_str)


def serialize_evidence_batch(
    evidences: tuple[dict, ...], separator: str = "\n"
) -> str:
    """
    Serialize a batch of evidence items to a single string.

    Args:
        evidences: Tuple of evidence dictionaries
        separator: String separating individual JSON objects

    Returns:
        Combined serialized string
    """
    return separator.join(serialize_evidence(e) for e in evidences)


def deserialize_evidence_batch(json_str: str, separator: str = "\n") -> tuple[dict, ...]:
    """
    Deserialize a combined string to evidence dictionary batch.

    Args:
        json_str: Combined JSON string
        separator: String separating individual JSON objects

    Returns:
        Tuple of evidence dictionaries
    """
    parts = json_str.strip().split(separator)
    return tuple(deserialize_evidence(part) for part in parts if part.strip())