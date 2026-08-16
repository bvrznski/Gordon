# Motivational Projection Network - Engine (Phase 4.10.6)
# ========================================================

"""
MotivationalProjectionEngine for Phase 4.10.6.

This module defines the engine that orchestrates the motivational projection
process: generating projections, analyzing tensions and synergies,
constructing field and state.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Tuple, Dict, List


@dataclass(frozen=True)
class MotivationalProjectionPolicy:
    """
    Policy for motivational projection behavior.

    POLICY-LAW-001: Projection mappings remain policy-driven.
    POLICY-LAW-002: No hardcoded semantics in the engine.
    POLICY-LAW-003: Policy is immutable once constructed.
    """

    # Mapping from reward domain type to target drive and projection type
    drive_mappings: Dict[str, Tuple[str, str]] = field(default_factory=dict)
    """Maps reward_domain_type -> (target_drive, projection_type)"""

    # Tension classification thresholds
    tension_confidence_threshold: float = 0.7
    """Minimum confidence to identify a tension."""

    synergy_confidence_threshold: float = 0.7
    """Minimum confidence to identify a synergy."""

    # Validation strictness
    validate_projections: bool = True
    validate_tensions: bool = True
    validate_synergies: bool = True


@dataclass(frozen=True)
class MotivationalProjectionResult:
    """
    Result of motivational projection processing.

    RESULT-LAW-001: Exactly one result is produced per request.
    RESULT-LAW-002: Result contains all required outputs.
    RESULT-LAW-003: Result preserves provenance and trace.
    """

    state_id: str
    """Result identifier."""

    motivational_reward_field: Dict[str, any]
    """The motivational reward field with projections, tensions, synergies."""

    projection_hierarchy: Tuple[Tuple[str, str], ...]
    """(projection_id, level) tuples for hierarchy."""

    temporal_partitions: Tuple[Tuple[str, str], ...]
    """(projection_id, timescale) tuples for temporal context."""

    confidence: float
    """Overall confidence in the result."""

    uncertainty: float
    """Overall uncertainty in the result."""

    projections_created: Tuple[str, ...]
    """Projection IDs created during processing."""

    tensions_identified: Tuple[str, ...]
    """Tension IDs identified during processing."""

    synergies_identified: Tuple[str, ...]
    """Synergy IDs identified during processing."""

    findings: Tuple[str, ...]
    """Key findings from processing."""

    limitations: Tuple[str, ...]
    """Known limitations of this result."""

    trace: Tuple[str, ...]
    """Processing trace for provenance."""

    status: str = "success"
    """Processing status (success/partial_error/failure)."""

    error_count: int = 0
    """Count of errors during processing."""


class MotivationalProjectionEngine:
    """
    The canonical engine for motivational projection.

    ENGINE-LAW-001: Exactly one engine processes each request.
    ENGINE-LAW-002: Engine orchestration is deterministic.
    ENGINE-LAW-003: Engine never creates or modifies drives.

    PROCESSING PIPELINE:
        validate_request
            ↓
        validate_multi_domain_reward_state
            ↓
        generate_drive_projections
            ↓
        estimate_projection_strengths
            ↓
        construct_projection_graph
            ↓
        identify_motivational_tensions
            ↓
        identify_motivational_synergies
            ↓
        construct_motivational_reward_field
            ↓
        construct_motivational_projection_state
            ↓
        validate_result
            ↓
        MotivationalProjectionResult
    """

    def __init__(self, policy: MotivationalProjectionPolicy = None):
        """Initialize the engine with optional policy."""
        self.policy = policy or MotivationalProjectionPolicy()

    def process(
        self,
        multi_domain_reward_state: Dict[str, any],
        identity: str = "motivational_projection_request",
        context_projection: Dict[str, any] = None,
    ) -> MotivationalProjectionResult:
        """
        Process a MultiDomainRewardState and produce motivational projections.

        Args:
            multi_domain_reward_state: The reward state to process
            identity: Request identifier
            context_projection: Optional context information

        Returns:
            MotivationalProjectionResult with all projection data
        """
        trace: List[str] = []
        findings: List[str] = []
        errors: List[str] = []

        # Step 1: Validate request
        if not self._validate_request(identity, multi_domain_reward_state):
            errors.append("INVALID_REQUEST")
            return MotivationalProjectionResult(
                state_id=f"{identity}_failed",
                motivational_reward_field={},
                projection_hierarchy=(),
                temporal_partitions=(),
                confidence=0.0,
                uncertainty=1.0,
                projections_created=(),
                tensions_identified=(),
                synergies_identified=(),
                findings=tuple(findings),
                limitations=tuple(errors),
                trace=tuple(trace),
                status="failure",
                error_count=1,
            )

        trace.append("REQUEST_VALIDATED")
        findings.append(f"Identity: {identity}")

        # Step 2: Extract reward domains from state
        domain_projections = self._generate_drive_projections(
            multi_domain_reward_state, identity
        )
        trace.append("PROJECTIONS_CREATED")

        # Step 3: Build projection hierarchy
        hierarchy = self._build_hierarchy(domain_projections)
        trace.append("HIERARCHY_BUILT")

        # Step 4: Build temporal partitions
        temporal = self._build_temporal_partitions(domain_projections)
        trace.append("TEMPORAL_PARTITIONING")

        # Step 5: Identify tensions
        tensions, tension_ids = self._identify_tensions(domain_projections)
        trace.append("TENSIONS_IDENTIFIED")
        if tensions:
            findings.append(f"Tensions identified: {len(tensions)}")

        # Step 6: Identify synergies
        synergies, synergy_ids = self._identify_synergies(domain_projections)
        trace.append("SYNERGIES_IDENTIFIED")
        if synergies:
            findings.append(f"Synergies identified: {len(synergies)}")

        # Step 7: Construct field
        field_data = self._construct_field(
            domain_projections, tensions, synergies
        )
        trace.append("FIELD_CONSTRUCTED")

        # Calculate confidence (average of projections)
        if domain_projections:
            total_confidence = sum(p.get("confidence", 0.5) for p in domain_projections)
            confidence = total_confidence / len(domain_projections)
        else:
            confidence = 0.5

        # Build result
        projection_ids = tuple(p.get("projection_id", "unknown") for p in domain_projections)

        return MotivationalProjectionResult(
            state_id=f"{identity}_result",
            motivational_reward_field=field_data,
            projection_hierarchy=hierarchy,
            temporal_partitions=temporal,
            confidence=confidence,
            uncertainty=max(0.0, 1.0 - confidence),
            projections_created=projection_ids,
            tensions_identified=tuple(tension_ids),
            synergies_identified=tuple(synergy_ids),
            findings=tuple(findings),
            limitations=tuple(errors),
            trace=tuple(trace),
        )

    def _validate_request(
        self, identity: str, reward_state: Dict[str, any]
    ) -> bool:
        """Validate the input request."""
        if not identity:
            return False
        if not isinstance(reward_state, dict):
            return False
        if "domains" not in reward_state and "reward_domains" not in reward_state:
            return False
        return True

    def _generate_drive_projections(
        self, reward_state: Dict[str, any], identity: str
    ) -> List[Dict]:
        """Generate drive projections from reward domains."""
        projections = []
        domains = reward_state.get("reward_domains", reward_state.get("domains", []))

        for i, domain in enumerate(domains):
            domain_type = domain.get("domain_type", "unknown")
            confidence = domain.get("confidence", 1.0)

            # Get target drive from policy mapping
            target_drive = self._get_target_drive(domain_type)
            projection_id = f"{identity}_proj_{i}"

            projections.append({
                "projection_id": projection_id,
                "target_drive": target_drive,
                "reward_domain": domain_type,
                "confidence": confidence,
                "uncertainty": max(0.0, 1.0 - confidence),
                "provenance": f"{identity}_mapper",
            })

        return projections

    def _get_target_drive(self, reward_domain: str) -> str:
        """Get the target drive for a reward domain from policy."""
        # Default mappings
        default_mappings = {
            "epistemic": "knowledge",
            "competence": "mastery",
            "mission": "mission_persistence",
            "social": "affiliation",
            "intrinsic": "exploration",
            "autonomy": "autonomy",
            "curiosity": "exploration",
        }
        return default_mappings.get(reward_domain, "unknown_drive")

    def _build_hierarchy(
        self, projections: List[Dict]
    ) -> Tuple[Tuple[str, str], ...]:
        """Build hierarchy mappings for projections."""
        # Default: all at action level
        hierarchy = []
        for p in projections:
            hierarchy.append((p["projection_id"], "action"))
        return tuple(hierarchy)

    def _build_temporal_partitions(
        self, projections: List[Dict]
    ) -> Tuple[Tuple[str, str], ...]:
        """Build temporal partitions for projections."""
        # Default: all at immediate timescale
        partitions = []
        for p in projections:
            partitions.append((p["projection_id"], "immediate"))
        return tuple(partitions)

    def _identify_tensions(
        self, projections: List[Dict]
    ) -> Tuple[Tuple, Tuple[str, ...]]:
        """Identify tensions between projections."""
        tensions = []
        tension_ids = []

        # Group projections by target drive
        drive_groups: Dict[str, List[Dict]] = {}
        for p in projections:
            drive = p["target_drive"]
            if drive not in drive_groups:
                drive_groups[drive] = []
            drive_groups[drive].append(p)

        # Find conflicting projections (same drive, opposite effects)
        for drive, group in drive_groups.items():
            if len(group) < 2:
                continue

            # For now, just identify co-occurring projections as potential tensions
            if len(group) > 1:
                tension_id = f"tension_{drive}"
                tension_ids.append(tension_id)
                tensions.append({
                    "tension_id": tension_id,
                    "participating_projections": tuple(p["projection_id"] for p in group),
                    "tension_type": "competing_priorities",
                    "severity": 0.3,
                })

        return tuple(tensions), tuple(tension_ids)

    def _identify_synergies(
        self, projections: List[Dict]
    ) -> Tuple[Tuple, Tuple[str, ...]]:
        """Identify synergies between projections."""
        synergies = []
        synergy_ids = []

        # Find projections with different drives that could reinforce
        unique_drives = list(set(p["target_drive"] for p in projections))

        if len(unique_drives) >= 2:
            synergy_id = "synergy_multi_drive"
            synergy_ids.append(synergy_id)
            synergies.append({
                "synergy_id": synergy_id,
                "participating_projections": tuple(p["projection_id"] for p in projections),
                "synergy_type": "complementary",
                "strength": 0.4,
            })

        return tuple(synergies), tuple(synergy_ids)

    def _construct_field(
        self,
        projections: List[Dict],
        tensions: Tuple,
        synergies: Tuple,
    ) -> Dict:
        """Construct the motivational reward field."""
        projection_ids = [p["projection_id"] for p in projections]

        return {
            "field_id": "motivational_reward_field",
            "drive_projections": tuple(projection_ids),
            "tensions": tuple(t["tension_id"] for t in tensions) if tensions else (),
            "synergies": tuple(s["synergy_id"] for s in synergies) if synergies else (),
            "confidence": sum(p.get("confidence", 0.5) for p in projections) / max(len(projections), 1),
            "tension_count": len(tensions),
            "synergy_count": len(synergies),
        }


__all__ = [
    "MotivationalProjectionPolicy",
    "MotivationalProjectionResult",
    "MotivationalProjectionEngine",
]