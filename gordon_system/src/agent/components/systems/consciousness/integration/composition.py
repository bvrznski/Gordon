# Gordon Phase 5.7.8-I: Conscious Integration - Composite Snapshot Builder
# ===============================================================================

"""
Composite snapshot construction from engine references.
"""

from __future__ import annotations

import time
from dataclasses import dataclass, field
from typing import Tuple, Dict, Optional

from .types import (
    EngineSnapshotReference,
    EngineGenerationMap,
    UnresolvedReference,
    CompositeSnapshot,
)
from .constants import CONSISTENCY_LEVEL_STRICT


@dataclass(frozen=True)
class CompositionResult:
    """
    Result of a composite snapshot composition operation.
    """

    succeeded: bool = True
    """Whether composition completed."""

    new_snapshot: Optional[CompositeSnapshot] = None
    """Newly composed snapshot (if successful)."""

    partial_success: bool = False
    """Whether this was a partial success with degraded modes."""

    skipped_engines: Tuple[str, ...] = field(default_factory=tuple)
    """Engines that were skipped (optional, unavailable)."""

    rejected_snapshots: Dict[str, str] = field(default_factory=dict)
    """Engine ID -> rejection reason for invalid snapshots."""

    degradation_modes: Tuple[str, ...] = field(default_factory=tuple)
    """Degradation modes applied during composition."""

    @property
    def is_degraded(self) -> bool:
        """Check if this result represents degraded operation."""
        return self.partial_success or len(self.degradation_modes) > 0


class CompositeSnapshotBuilder:
    """
    Builder for composite conscious context snapshots.

    This class coordinates the collection of committed engine references,
    validates generation alignment, and constructs the final composite snapshot.
    """

    def __init__(self, consistency_level: str = CONSISTENCY_LEVEL_STRICT):
        """
        Initialize the builder with consistency requirements.

        Args:
            consistency_level: The strictness level for composition
        """
        self._consistency_level = consistency_level
        self._engine_refs: Dict[str, EngineSnapshotReference] = {}
        self._unresolved_refs: list[UnresolvedReference] = []
        self._skipped_engines: set[str] = set()
        self._rejection_reasons: dict[str, str] = {}

    @property
    def consistency_level(self) -> str:
        """Get the current consistency level."""
        return self._consistency_level

    def add_engine_reference(
        self,
        engine_id: str,
        ref: EngineSnapshotReference,
    ) -> bool:
        """
        Add an engine snapshot reference.

        Args:
            engine_id: The engine identifier
            ref: Snapshot reference from the engine

        Returns:
            True if accepted, False if rejected (invalid or unavailable)
        """
        # Validate engine ID
        if not engine_id:
            self._rejection_reasons[engine_id] = "Invalid engine ID"
            return False

        # Check if this is an optional engine we should skip
        if not ref and self._is_optional_engine(engine_id):
            self._skipped_engines.add(engine_id)
            return True  # Optional engines don't block composition

        if ref:
            self._engine_refs[engine_id] = ref
        else:
            # Missing required engine is an error
            self._rejection_reasons[engine_id] = "Required engine unavailable"
            return False

        return True

    def record_unresolved_reference(
        self,
        referencing_engine_id: str,
        referenced_entity_type: str,
        reference_value: str,
        resolution_status: str = "unresolved",
    ) -> None:
        """
        Record an unresolved reference during composition.

        Args:
            referencing_engine_id: Engine holding the reference
            referenced_entity_type: Type of the entity being referenced
            reference_value: The raw reference value
            resolution_status: Classification (unresolved/remembered/hypothetical)
        """
        self._unresolved_refs.append(
            UnresolvedReference(
                referencing_engine_id=referencing_engine_id,
                referenced_entity_type=referenced_entity_type,
                reference_value=reference_value,
                resolution_status=resolution_status,
                confidence=0.5 if resolution_status == "remembered" else 0.0,
            )
        )

    def _is_optional_engine(self, engine_id: str) -> bool:
        """Check if an engine is optional for current consistency level."""
        from .constants import OPTIONAL_ENGINE_IDS

        return engine_id in OPTIONAL_ENGINE_IDS

    def build(
        self,
        context_id: str,
        previous_generation: int = 0,
    ) -> CompositionResult:
        """
        Build the composite snapshot.

        This validates all collected references, checks generation alignment,
        and produces a final immutable snapshot.

        Args:
            context_id: Context ID for the new snapshot
            previous_generation: Previous generation number

        Returns:
            Result with either new snapshot or failure details
        """
        start_time = time.time()

        # Validate required engines are present
        from .constants import REQUIRED_ENGINE_IDS

        missing_required = []
        for req in REQUIRED_ENGINE_IDS:
            if req not in self._engine_refs:
                if self.consistency_level == CONSISTENCY_LEVEL_STRICT:
                    return CompositionResult(
                        succeeded=False,
                        partial_success=False,
                    )
                else:
                    # In degraded mode, we may allow missing optional engines
                    if not self._is_optional_engine(req):
                        missing_required.append(req)

        # Build generation map from collected references
        gen_map = EngineGenerationMap(
            engine_ids=tuple(self._engine_refs.keys()),
            generation_map={k: v.generation for k, v in self._engine_refs.items()},
        )

        # Determine degradation modes
        degradation_modes: list[str] = []
        if len(missing_required) > 0:
            degradation_modes.append("required_engines_unavailable")
        
        if len(self._rejection_reasons) > 0:
            degradation_modes.append("engine_snapshots_rejected")

        if len(self._skipped_engines) > 0:
            degradation_modes.append("optional_engines_skipped")

        # Build the composite snapshot
        refs_dict = {}
        for engine_id, ref in self._engine_refs.items():
            field_name = f"{engine_id}_ref"
            if hasattr(CompositeSnapshot, field_name):
                refs_dict[field_name] = ref

        new_snapshot = CompositeSnapshot(
            context_id=context_id,
            generation=previous_generation + 1,
            previous_generation=previous_generation,
            created_at_utc=start_time,
            engine_generation_map=gen_map,
            unresolved_references=tuple(self._unresolved_refs),
            degradation_modes=tuple(degradation_modes) if degradation_modes else (),
        )

        # Apply references
        new_snapshot = self._apply_engine_references(new_snapshot, refs_dict)

        return CompositionResult(
            succeeded=True,
            new_snapshot=new_snapshot,
            partial_success=len(degradation_modes) > 0,
            skipped_engines=tuple(self._skipped_engines),
            rejected_snapshots=self._rejection_reasons,
            degradation_modes=tuple(degradation_modes),
        )

    def _apply_engine_references(
        self, snapshot: CompositeSnapshot, refs_dict: Dict[str, EngineSnapshotReference]
    ) -> CompositeSnapshot:
        """Apply engine references to a snapshot."""
        # Update specific reference fields
        updates = {}
        for field_name in [
            "experiential_field_ref",
            "intentional_context_ref",
            "temporal_context_ref",
            "presence_ref",
            "awareness_ref",
            "perspective_ref",
            "situated_world_ref",
        ]:
            if field_name in refs_dict:
                updates[field_name] = refs_dict.get(field_name)
        
        # Use with_transitions method
        return snapshot.with_transitions(**updates)

    def reset(self) -> None:
        """Reset the builder for a new composition."""
        self._engine_refs.clear()
        self._unresolved_refs.clear()
        self._skipped_engines.clear()
        self._rejection_reasons.clear()


def compose_initial_snapshot(context_id: str) -> CompositeSnapshot:
    """
    Create an initial empty composite snapshot.

    Args:
        context_id: Context ID for the snapshot

    Returns:
        Initial composite snapshot with generation 0
    """
    return CompositeSnapshot.initial(context_id)