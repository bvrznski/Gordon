# Phase 3.11.13 - Input Selection Implementation
# ==============================================
"""
Deterministic input selection from committed stream records for stage consumption.
"""

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Tuple
import time
import uuid

from . import (
    StageInputSelectionId,
    InputSnapshotId,
    StreamRecordReference,
    SelectedRecord,
    InputSelectionPolicy,
    InputSelectionResult,
    SelectionStatus,
    AlignmentPolicy,
    StageInputSnapshot,
)


@dataclass
class DeterministicSelector:
    """
    Deterministic input selector for stage consumption.
    
    Selection is deterministic given the same state inputs:
        - Thread revision at cycle start
        - Stream positions (cursor snapshots)
        - Policy configuration
        - Available records in streams
    
    This selector implements:
        - Many-to-many stream/stage selection
        - Bounded fan-in from multiple streams
        - Deterministic ordering within each stream
        - Correlation/causation based alignment
        - Freshness window enforcement
    """
    
    # Configuration (immutable once set)
    policy: InputSelectionPolicy
    
    def select_records(
        self,
        stage_id: str,
        cycle_id: str,
        available_streams: Dict[str, List[Dict[str, Any]]],  # stream_id → list of records
        cursor_positions: Dict[str, int],                     # stream_id → current position
        correlation_context: Optional[Dict[str, Any]] = None,
    ) -> InputSelectionResult:
        """
        Select records from available streams for the stage.
        
        This is the deterministic selection logic that produces the input
        selection result. It does NOT advance cursors or activate networks.
        
        Args:
            stage_id: The stage requesting input
            cycle_id: The parent cycle
            available_streams: Records available in each stream (after cursor)
            cursor_positions: Current cursor positions per stream
            correlation_context: Optional context for alignment
            
        Returns:
            Deterministic input selection result
        """
        selected_records = []
        excluded_records = {}
        cursor_snapshots = dict(cursor_positions)
        
        # Process each stream according to policy
        for stream_id, records in sorted(available_streams.items()):
            # Sort records deterministically by position (should already be sorted)
            records = list(sorted(records, key=lambda r: r.get("position", 0)))
            
            # Apply cursor filter - only select records after current position
            start_pos = cursor_positions.get(stream_id, 0)
            available_after_cursor = [
                r for r in records if r.get("position", 0) > start_pos
            ]
            
            # Limit to max_records_per_stream policy
            limited_records = available_after_cursor[:self.policy.max_records_per_stream]
            
            # Process each record
            for record in limited_records:
                selection_result = self._evaluate_record_eligibility(
                    stream_id=stream_id,
                    record=record,
                    cursor_positions=cursor_positions,
                    correlation_context=correlation_context,
                )
                
                if selection_result.is_eligible:
                    selected_records.append(selection_result.selected)
                else:
                    excluded_records[record.get("id", "unknown")] = (
                        selection_result.exclusion_reason
                    )
        
        # Sort selected records deterministically for consistency
        selected_records.sort(
            key=lambda r: (r.reference.stream_id, r.reference.position)
        )
        
        return InputSelectionResult(
            selection_id=StageInputSelectionId.generate(),
            stage_id=stage_id,
            cycle_id=cycle_id,
            selected_record_references=selected_records,
            excluded_records=excluded_records,
            cursor_snapshots=cursor_snapshots,
            created_at_utc=time.time(),
            correlation_id=correlation_context.get("correlation_id") if correlation_context else None,
            causation_id=correlation_context.get("causation_id") if correlation_context else None,
            provenance="deterministic_selection",
        )

    def _evaluate_record_eligibility(
        self,
        stream_id: str,
        record: Dict[str, Any],
        cursor_positions: Dict[str, int],
        correlation_context: Optional[Dict[str, Any]],
    ) -> "SelectionEvaluation":
        """
        Evaluate if one record is eligible for stage consumption.
        
        Returns evaluation result with eligibility decision and exclusion reason if needed.
        """
        # Check basic requirements
        record_position = record.get("position", 0)
        current_cursor = cursor_positions.get(stream_id, 0)
        
        # Record must be after current cursor position
        if record_position <= current_cursor:
            return SelectionEvaluation(
                is_eligible=False,
                exclusion_reason="record_at_or_before_cursor"
            )
        
        # Check freshness if configured
        if self.policy.freshness_window_seconds > 0:
            record_time = record.get("timestamp_utc", 0)
            now = time.time()
            age = now - record_time
            
            if age > self.policy.freshness_window_seconds:
                return SelectionEvaluation(
                    is_eligible=False,
                    exclusion_reason="record_expired_outside_freshness_window"
                )
        
        # Check correlation alignment if context provided
        if correlation_context and "alignment_keys" in correlation_context:
            record_correlation = record.get("correlation_id")
            alignment_keys = correlation_context["alignment_keys"]
            
            if record_correlation and record_correlation not in alignment_keys:
                return SelectionEvaluation(
                    is_eligible=False,
                    exclusion_reason="record_missing_alignment_key"
                )
        
        # Record passes all checks
        selected_record = SelectedRecord(
            reference=StreamRecordReference(
                record_id=record.get("id", ""),
                stream_id=stream_id,
                position=record_position,
                generation_id=record.get("generation_id", ""),
            ),
            provenance="deterministic_selection",
            alignment_key=record.get("correlation_id"),
        )
        
        return SelectionEvaluation(is_eligible=True, selected=selected_record)


@dataclass
class SelectionEvaluation:
    """Result of evaluating one record's eligibility."""
    is_eligible: bool
    selected: Optional[SelectedRecord] = None
    exclusion_reason: str = ""


# =============================================================================
# Multi-Stream Fan-In Selector
# =============================================================================


@dataclass
class FanInSelector:
    """
    Selector that implements bounded fan-in from multiple streams.
    
    Implements policies for:
        - Required vs optional stream handling
        - Minimum records required across all streams
        - Maximum total records across all streams
        - Alignment of records from different streams
    """
    
    policy: InputSelectionPolicy
    
    def select_with_fan_in(
        self,
        stage_id: str,
        cycle_id: str,
        stream_records: Dict[str, List[Dict[str, Any]]],  # stream_id → records
        cursor_positions: Dict[str, int],
        required_streams: Optional[List[str]] = None,
    ) -> Tuple[InputSelectionResult, List[str]]:
        """
        Select records with multi-stream fan-in policy.
        
        Args:
            stage_id: The stage requesting input
            cycle_id: Parent cycle ID
            stream_records: Records from each stream (after cursor)
            cursor_positions: Current cursor positions per stream
            required_streams: Optional list of streams that MUST have at least one record
            
        Returns:
            Tuple of (selection result, missing_stream_ids_if_any)
        """
        # Determine which streams are required
        all_streams = set(stream_records.keys())
        if required_streams is None:
            required_streams = []
        
        missing_required = [
            s for s in required_streams 
            if s not in all_streams or len(stream_records.get(s, [])) == 0
        ]
        
        # If required streams are missing and policy doesn't allow skipping,
        # return empty result
        if missing_required and not self.policy.optional_streams_allowed:
            return (
                InputSelectionResult(
                    selection_id=StageInputSelectionId.generate(),
                    stage_id=stage_id,
                    cycle_id=cycle_id,
                    selected_record_references=[],
                    excluded_records={},
                    cursor_snapshots=dict(cursor_positions),
                    status=SelectionStatus.PENDING,
                    created_at_utc=time.time(),
                    correlation_id=None,
                ),
                missing_required
            )
        
        # Use deterministic selector for each stream
        selector = DeterministicSelector(policy=self.policy)
        
        # Combine records from all streams, tracking which came from where
        combined_selections: Dict[Tuple[str, int], SelectedRecord] = {}
        
        for stream_id in all_streams:
            if stream_id not in stream_records:
                continue
                
            # Get cursor position for this stream
            stream_cursor = cursor_positions.get(stream_id, 0)
            
            # Process records from this stream
            for record in sorted(
                stream_records[stream_id],
                key=lambda r: r.get("position", 0)
            ):
                if record.get("position", 0) <= stream_cursor:
                    continue
                    
                ref = StreamRecordReference(
                    record_id=record.get("id", ""),
                    stream_id=stream_id,
                    position=record.get("position", 0),
                    generation_id=record.get("generation_id", ""),
                )
                
                key = (stream_id, record.get("position", 0))
                if key not in combined_selections:
                    combined_selections[key] = SelectedRecord(
                        reference=ref,
                        provenance=f"fan_in_from_{stream_id}",
                    )
        
        # Convert to list and sort deterministically
        selected_records = sorted(
            combined_selections.values(),
            key=lambda r: (r.reference.stream_id, r.reference.position)
        )
        
        return (
            InputSelectionResult(
                selection_id=StageInputSelectionId.generate(),
                stage_id=stage_id,
                cycle_id=cycle_id,
                selected_record_references=selected_records[:self.policy.max_records_per_stream],
                excluded_records={},
                cursor_snapshots=dict(cursor_positions),
                status=SelectionStatus.COMPLETE if selected_records else SelectionStatus.PENDING,
                created_at_utc=time.time(),
                correlation_id=None,
            ),
            []
        )


# =============================================================================
# Alignment-Aware Selector
# =============================================================================


@dataclass
class AlignmentAwareSelector:
    """
    Selector that implements cross-stream record alignment.
    
    Alignment policies:
        - CORRELATION_ID: Group records with same correlation ID
        - CAUSATION_ID: Follow causation chains
        - EVENT_TIME_WINDOW: Select within time window
        - CANONICAL_SEQUENCE: Align by sequence number position
    """
    
    policy: InputSelectionPolicy
    
    def select_with_alignment(
        self,
        stage_id: str,
        cycle_id: str,
        stream_records: Dict[str, List[Dict[str, Any]]],
        cursor_positions: Dict[str, int],
    ) -> Tuple[InputSelectionResult, Dict[str, str]]:
        """
        Select records with alignment policy applied.
        
        Returns:
            Tuple of (selection result, alignment_summary)
        """
        # First pass: collect all records and their alignment keys
        records_by_alignment_key: Dict[str, List[Tuple[str, SelectedRecord]]] = {}
        
        selector = DeterministicSelector(policy=self.policy)
        
        for stream_id in sorted(stream_records.keys()):
            if stream_id not in cursor_positions:
                continue
                
            current_cursor = cursor_positions[stream_id]
            
            for record in sorted(
                stream_records[stream_id],
                key=lambda r: r.get("position", 0)
            ):
                if record.get("position", 0) <= current_cursor:
                    continue
                
                # Evaluate eligibility
                eval_result = selector._evaluate_record_eligibility(
                    stream_id=stream_id,
                    record=record,
                    cursor_positions=cursor_positions,
                    correlation_context=None,
                )
                
                if not eval_result.is_eligible:
                    continue
                
                selected = eval_result.selected
                alignment_key = record.get("correlation_id", "")
                
                key = (alignment_key, stream_id, record.get("position", 0))
                
                if alignment_key not in records_by_alignment_key:
                    records_by_alignment_key[alignment_key] = []
                
                records_by_alignment_key[alignment_key].append((stream_id, selected))
        
        # Apply alignment policy
        final_selections: List[SelectedRecord] = []
        
        if self.policy.alignment_policy == AlignmentPolicy.CORRELATION_ID:
            # For correlation ID alignment, select one record per key
            for alignment_key in sorted(records_by_alignment_key.keys()):
                records_for_key = records_by_alignment_key[alignment_key]
                if records_for_key:
                    # Select first (deterministic tie-breaking by stream_id)
                    final_selections.append(records_for_key[0][1])
        
        elif self.policy.alignment_policy == AlignmentPolicy.NONE:
            # No alignment - just combine all eligible records
            for key in sorted(records_by_alignment_key.keys()):
                for _, record in records_by_alignment_key[key]:
                    final_selections.append(record)
        
        else:
            # Default: no special alignment
            for key in sorted(records_by_alignment_key.keys()):
                for _, record in records_by_alignment_key[key]:
                    final_selections.append(record)
        
        return (
            InputSelectionResult(
                selection_id=StageInputSelectionId.generate(),
                stage_id=stage_id,
                cycle_id=cycle_id,
                selected_record_references=final_selections,
                excluded_records={},
                cursor_snapshots=dict(cursor_positions),
                status=SelectionStatus.COMPLETE if final_selections else SelectionStatus.PENDING,
                created_at_utc=time.time(),
            ),
            self._build_alignment_summary(records_by_alignment_key)
        )
    
    def _build_alignment_summary(
        self,
        records_by_key: Dict[str, List[Tuple[str, SelectedRecord]]]
    ) -> str:
        """Build human-readable alignment summary."""
        if not records_by_key:
            return "no_records_aligned"
        
        keys = list(records_by_key.keys())
        total_records = sum(len(v) for v in records_by_key.values())
        
        return f"{len(keys)} alignment groups, {total_records} total records"


# =============================================================================
# Input Snapshot Builder
# =============================================================================


class InputSnapshotBuilder:
    """
    Builds immutable stage input snapshots from selection results.
    
    This builder creates bounded snapshots that preserve cursor positions
    at snapshot time without copying large payloads.
    """
    
    def build_snapshot(
        self,
        selection_result: InputSelectionResult,
        thread_id: str,
        loop_id: str,
        cycle_id: str,
        stage_id: str,
        deadline: Optional[float] = None,
    ) -> InputSnapshotId:
        """
        Build an immutable input snapshot from a selection result.
        
        Args:
            selection_result: The output of deterministic selection
            thread_id, loop_id, cycle_id, stage_id: Execution context
            
        Returns:
            Snapshot ID (snapshot object stored in caller's state)
        """
        # Generate snapshot ID
        snapshot_id = InputSnapshotId.generate()
        
        # Create the snapshot (caller stores it)
        _ = StageInputSnapshot(
            snapshot_id=snapshot_id,
            thread_id=thread_id,
            loop_id=loop_id,
            cycle_id=cycle_id,
            stage_id=stage_id,
            selected_records=selection_result.selected_record_references,
            cursor_snapshots=selection_result.cursor_snapshots,
            alignment_summary=f"Selected {selection_result.record_count} records from "
                             f"{selection_result.stream_count} streams",
            created_at_utc=selection_result.created_at_utc,
            deadline=deadline,
            correlation_id=selection_result.correlation_id,
            causation_id=selection_result.causation_id,
        )
        
        return snapshot_id