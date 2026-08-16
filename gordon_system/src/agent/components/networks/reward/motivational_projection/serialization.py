# Motivational Projection Network - Serialization (Phase 4.10.6)
# ================================================================

"""
Serialization utilities for Phase 4.10.6.

This module provides deterministic JSON serialization and deserialization
for all motivational projection components.
"""

from __future__ import annotations

import json
from dataclasses import asdict
from typing import Any, Dict, Tuple


def serialize_projection(projection: dict) -> str:
    """Serialize a projection to JSON string."""
    return json.dumps({
        "projection_id": projection.get("projection_id", ""),
        "target_drive": projection.get("target_drive", ""),
        "reward_domain": projection.get("reward_domain", ""),
        "confidence": float(projection.get("confidence", 1.0)),
        "uncertainty": float(projection.get("uncertainty", 0.0)),
        "provenance": projection.get("provenance", ""),
    }, sort_keys=True)


def deserialize_projection(json_str: str) -> dict:
    """Deserialize a projection from JSON string."""
    data = json.loads(json_str)
    return {
        "projection_id": data.get("projection_id", ""),
        "target_drive": data.get("target_drive", ""),
        "reward_domain": data.get("reward_domain", ""),
        "confidence": float(data.get("confidence", 1.0)),
        "uncertainty": float(data.get("uncertainty", 0.0)),
        "provenance": data.get("provenance", ""),
    }


def serialize_tension(tension: dict) -> str:
    """Serialize a tension to JSON string."""
    return json.dumps({
        "tension_id": tension.get("tension_id", ""),
        "participating_projections": tuple(tension.get("participating_projections", [])),
        "tension_type": tension.get("tension_type", ""),
        "severity": float(tension.get("severity", 0.5)),
        "confidence": float(tension.get("confidence", 1.0)),
    }, sort_keys=True)


def serialize_synergy(synergy: dict) -> str:
    """Serialize a synergy to JSON string."""
    return json.dumps({
        "synergy_id": synergy.get("synergy_id", ""),
        "participating_projections": tuple(synergy.get("participating_projections", [])),
        "synergy_type": synergy.get("synergy_type", ""),
        "strength": float(synergy.get("strength", 0.5)),
        "confidence": float(synergy.get("confidence", 1.0)),
    }, sort_keys=True)


def serialize_field(field_data: dict) -> str:
    """Serialize a motivational reward field to JSON string."""
    return json.dumps({
        "field_id": field_data.get("field_id", ""),
        "drive_projections": tuple(field_data.get("drive_projections", [])),
        "tensions": tuple(field_data.get("tensions", [])),
        "synergies": tuple(field_data.get("synergies", [])),
        "confidence": float(field_data.get("confidence", 0.5)),
        "tension_count": field_data.get("tension_count", 0),
        "synergy_count": field_data.get("synergy_count", 0),
    }, sort_keys=True)


def serialize_state(state_data: dict) -> str:
    """Serialize a motivational projection state to JSON string."""
    return json.dumps({
        "state_id": state_data.get("state_id", ""),
        "revision": int(state_data.get("revision", 0)),
        "motivational_reward_field": state_data.get("motivational_reward_field", {}),
        "projection_hierarchy": tuple(state_data.get("projection_hierarchy", [])),
        "temporal_partitions": tuple(state_data.get("temporal_partitions", [])),
        "confidence": float(state_data.get("confidence", 0.5)),
        "uncertainty": float(state_data.get("uncertainty", 0.0)),
    }, sort_keys=True)


def serialize_result(result: dict) -> str:
    """Serialize a projection result to JSON string."""
    return json.dumps({
        "state_id": result.get("state_id", ""),
        "motivational_reward_field": result.get("motivational_reward_field", {}),
        "projection_hierarchy": tuple(result.get("projection_hierarchy", [])),
        "temporal_partitions": tuple(result.get("temporal_partitions", [])),
        "confidence": float(result.get("confidence", 0.5)),
        "uncertainty": float(result.get("uncertainty", 0.0)),
        "projections_created": tuple(result.get("projections_created", [])),
        "tensions_identified": tuple(result.get("tensions_identified", [])),
        "synergies_identified": tuple(result.get("synergies_identified", [])),
        "findings": tuple(result.get("findings", [])),
        "limitations": tuple(result.get("limitations", [])),
        "trace": tuple(result.get("trace", [])),
        "status": result.get("status", ""),
    }, sort_keys=True)


def serialize_list(items: Tuple[dict, ...]) -> str:
    """Serialize a list of items to JSON string."""
    return json.dumps([serialize_projection(i) for i in items], sort_keys=True)


__all__ = [
    "serialize_projection",
    "deserialize_projection",
    "serialize_tension",
    "serialize_synergy",
    "serialize_field",
    "serialize_state",
    "serialize_result",
    "serialize_list",
]