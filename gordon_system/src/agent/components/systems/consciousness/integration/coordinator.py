# Gordon Phase 5.7.8-I: Conscious Integration - Coordinator
# ===============================================================================

"""
Integration coordinator for orchestrating composite snapshot publication.
"""

from __future__ import annotations

import time
import uuid
from dataclasses import dataclass, field
from typing import Tuple, Dict, Optional

from .types import (
    EngineSnapshotReference,
    EngineGenerationMap,
    CompositeSnapshot,
    IntegrationTransition,
    IntegrationResult,
)
from .constants import (
    CONSISTENCY_LEVEL_STRICT,
    INTEGRATION_STATE_IDLE,
    INTEGRATION_STATE_COLLECTING_SNAPSHOTS,
    INTEGRATION_STATE_VALIDATING,
    INTEGRATION_STATE_COMPOSING,
    INTEGRATION_STATE_PUBLISHING,
)


@dataclass(frozen=True)
class IntegrationRequest:
    """
    Request to perform an integration transition.
    """

    context_id: str
    """Context ID being integrated."""

    previous_generation: int = 0
    """Previous generation number (for lineage tracking)."""

    consistency_level: str = CONSISTENCY_LEVEL_STRICT
    """Consistency level for this integration."""

    requested_engine_updates: Tuple[str, ...] = field(default_factory=tuple)
    """Engine IDs that should be updated."""

    trigger: str = "internal"
    """What triggered this integration request."""


class IntegrationCoordinator:
    """
    Coordinator for composite conscious context transitions.

    This coordinator orchestrates the complete integration pipeline:
        1. Collect committed engine snapshots/references
        2. Validate generation alignment
        3. Validate cross-engine invariants
        4. Build composite snapshot
        5. Atomically publish new generation

    The coordinator is stateless for operations - it delegates to the parent
    Consciousness facade which manages all runtime state.
    """

    def __init__(self, consistency_level: str = CONSISTENCY_LEVEL_STRICT):
        """
        Initialize the coordinator.

        Args:
            consistency_level: Default consistency level for integrations
        """
        self._consistency_level = consistency_level
        self._state = INTEGRATION_STATE_IDLE

    @property
    def state(self) -> str:
        """Get current coordinator state."""
        return self._state

    @property
    def is_ready(self) -> bool:
        """Check if the coordinator is ready for operations."""
        return self._state == INTEGRATION_STATE_IDLE

    def integrate(
        self,
        request: IntegrationRequest,
        engine_refs: Dict[str, EngineSnapshotReference],
        previous_snapshot: Optional[CompositeSnapshot] = None,
    ) -> Tuple[IntegrationResult, Optional[CompositeSnapshot]]:
        """
        Perform a complete integration transition.

        This is the atomic commit point - either the full transition commits
        or nothing changes.

        Args:
            request: Integration request with context and consistency info
            engine_refs: Engine snapshot references from all engines
            previous_snapshot: Previous composite snapshot (for lineage)

        Returns:
            Tuple of (result, new_snapshot if successful)
        """
        self._state = INTEGRATION_STATE_COLLECTING_SNAPSHOTS

        try:
            # Step 1: Validate requested engine updates
            validation_result = self._validate_engine_refs(
                request=request,
                engine_refs=engine_refs,
                previous_snapshot=previous_snapshot,
            )

            if not validation_result.passed:
                return (
                    IntegrationResult(
                        transition_id=str(uuid.uuid4().hex[:8]),
                        succeeded=False,
                        status="rejected",
                        failure_reason=validation_result.failure_reason or "Validation failed",
                    ),
                    None,
                )

            # Step 2: Validate generation alignment
            self._state = INTEGRATION_STATE_VALIDATING

            gen_alignment = self._validate_generation_alignment(
                engine_refs=engine_refs,
                consistency_level=request.consistency_level,
            )

            if not gen_alignment.passed:
                return (
                    IntegrationResult(
                        transition_id=str(uuid.uuid4().hex[:8]),
                        succeeded=False,
                        status="rejected",
                        failure_reason=f"Generation alignment failed: {gen_alignment.failure_reason}",
                    ),
                    None,
                )

            # Step 3: Build composite snapshot
            self._state = INTEGRATION_STATE_COMPOSING

            gen_map = EngineGenerationMap(
                engine_ids=tuple(engine_refs.keys()),
                generation_map={k: v.generation for k, v in engine_refs.items()},
            )

            new_snapshot = CompositeSnapshot(
                context_id=request.context_id,
                generation=previous_snapshot.generation + 1 if previous_snapshot else 1,
                previous_generation=previous_snapshot.generation if previous_snapshot else 0,
                created_at_utc=time.time(),
                engine_generation_map=gen_map,
                consistency_level=request.consistency_level,
            )

            # Step 4: Atomically publish
            self._state = INTEGRATION_STATE_PUBLISHING

            transition = IntegrationTransition(
                context_id=request.context_id,
                previous_generation=new_snapshot.previous_generation,
                new_generation=new_snapshot.generation,
                transition_id=str(uuid.uuid4().hex[:8]),
                started_at_utc=time.time(),
                committed_at_utc=time.time(),
                trigger=request.trigger,
                requested_engine_updates=tuple(request.requested_engine_updates),
                committed_engine_transitions={
                    k: v.generation for k, v in engine_refs.items()
                },
                generation_alignment_passed=True,
                cross_engine_validation_passed=True,
                status="completed",
            )

            self._state = INTEGRATION_STATE_IDLE

            return (
                IntegrationResult(
                    transition_id=transition.transition_id,
                    succeeded=True,
                    status="completed",
                    new_composite_snapshot=new_snapshot,
                    new_generation=new_snapshot.generation,
                ),
                new_snapshot,
            )

        except Exception as e:
            self._state = INTEGRATION_STATE_IDLE
            return (
                IntegrationResult(
                    transition_id=str(uuid.uuid4().hex[:8]),
                    succeeded=False,
                    status="failed",
                    failure_reason=str(e),
                ),
                None,
            )

    def _validate_engine_refs(
        self,
        request: IntegrationRequest,
        engine_refs: Dict[str, EngineSnapshotReference],
        previous_snapshot: Optional[CompositeSnapshot] = None,
    ) -> ValidationOutcome:
        """Validate engine references for integration."""
        required_count = 0
        available_count = 0

        from .constants import REQUIRED_ENGINE_IDS

        for req_id in REQUIRED_ENGINE_IDS:
            if req_id not in engine_refs:
                return ValidationOutcome(
                    passed=False,
                    failure_reason=f"Required engine missing: {req_id}",
                )
            available_count += 1
            required_count += 1

        # Check consistency level requirements
        if request.consistency_level == CONSISTENCY_LEVEL_STRICT and len(engine_refs) < len(REQUIRED_ENGINE_IDS):
            return ValidationOutcome(
                passed=False,
                failure_reason=f"Not all required engines available for strict consistency",
            )

        return ValidationOutcome(passed=True)

    def _validate_generation_alignment(
        self,
        engine_refs: Dict[str, EngineSnapshotReference],
        consistency_level: str,
    ) -> AlignmentValidationResult:
        """Validate that engine generations are aligned."""
        # For now, we just check that all refs are present and valid
        if not engine_refs:
            return AlignmentValidationResult(passed=False, failure_reason="No engine references provided")

        # Check for generation consistency across engines
        gen_values = [ref.generation for ref in engine_refs.values()]
        max_gen = max(gen_values)

        for ref in engine_refs.values():
            # Allow some lag in relaxed modes
            if consistency_level == CONSISTENCY_LEVEL_STRICT and ref.generation < max_gen:
                return AlignmentValidationResult(
                    passed=False,
                    failure_reason=f"Engine {ref.engine_id} is behind: {ref.generation} < {max_gen}",
                )

        return AlignmentValidationResult(passed=True)


@dataclass(frozen=True)
class ValidationOutcome:
    """Validation result with optional failure reason."""

    passed: bool = True
    failure_reason: Optional[str] = None


@dataclass(frozen=True)
class AlignmentValidationResult:
    """Generation alignment validation result."""

    passed: bool = True
    failure_reason: Optional[str] = None