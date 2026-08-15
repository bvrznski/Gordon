# Default Network Path Selector
# ============================

"""
Path selection logic for the Default Network.

This module provides:
    • DefaultNetworkPathSelector: Deterministic path selection based on request
    
The selector uses explicit rules and configuration to determine which semantic
coordination path is most appropriate for a given request. Selection must be
deterministic - no randomness, no runtime load factors, no hidden inference.

PHASE 4.3.12: Path Selector
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Tuple, Optional


@dataclass(frozen=True)
class DefaultNetworkPathSelection:
    """
    Record of path selection reasoning.
    
    Explains which path was chosen and why others were excluded.
    """
    
    # Required fields (no defaults) - must come first
    selected_path: str  # DefaultNetworkPath.*
    """Which path was selected."""
    
    considered_paths: Tuple[str, ...]
    """Paths that were considered."""
    
    exclusion_reasons: Tuple[str, ...]
    """Reasons why other paths were not selected."""
    
    missing_prerequisites: Tuple[str, ...]
    """Prerequisites that would be needed for this path."""
    
    # Optional fields with defaults - must come after required fields
    confidence: float = 0.5
    """Confidence in the selection (0.0 to 1.0)."""
    
    provenance_ref: Optional[str] = None
    
    @classmethod
    def select(
        cls,
        selected_path: str,
        confidence: float,
        considered_paths: Tuple[str, ...],
        exclusion_reasons: Tuple[str, ...],
    ) -> DefaultNetworkPathSelection:
        """Create a path selection record."""
        return cls(
            selected_path=selected_path,
            confidence=confidence,
            considered_paths=considered_paths,
            exclusion_reasons=exclusion_reasons,
            missing_prerequisites=(),
            provenance_ref=None,
        )


class DefaultNetworkPathSelector:
    """
    Deterministic path selector for Default Network coordination.
    
    Given a request, the selector determines which semantic coordination
    path is most appropriate. Selection is based on explicit rules and
    configuration - never on randomness or runtime factors.
    
    ARCHITECTURAL INVARIANTS:
        DEFAULT-PATH-SELECTOR-INV-001: Selection is deterministic for same inputs
        DEFAULT-PATH-SELECTOR-INV-002: No random choice in selection
        DEFAULT-PATH-SELECTOR-INV-003: No runtime load or resource factors
        DEFAULT-PATH-SELECTOR-INV-004: All reasoning is explicit and documented
        
    PROCESSING:
        • select_path: Determine the most appropriate path for a request
        
    NOT RESPONSIBLE FOR:
        • Executing the selected path
        • Loading handler implementations
        • Making runtime scheduling decisions
    """
    
    def __init__(
        self,
        supported_paths: Tuple[str, ...] | None = None,
        default_path_by_purpose: dict[str, str] | None = None,
    ):
        """
        Initialize the selector.
        
        Args:
            supported_paths: Paths this selector can choose from
            default_path_by_purpose: Default path for each purpose
        """
        self._supported_paths = supported_paths or ()
        self._default_path_by_purpose = default_path_by_purpose or {}
    
    def select_path(
        self,
        purpose: str,
        subject: Optional[str] = None,
        requested_path: Optional[str] = None,
        context_available: dict[str, bool] | None = None,
    ) -> DefaultNetworkPathSelection:
        """
        Select the most appropriate path for a request.
        
        Args:
            purpose: The semantic coordination goal
            subject: What is being processed (optional)
            requested_path: Explicitly requested path (optional)
            context_available: Available context types
            
        Returns:
            Path selection record with reasoning
        """
        context_available = context_available or {}
        
        # If a specific path was explicitly requested and it's supported,
        # use that as the first choice
        if requested_path is not None:
            if self._is_supported(requested_path):
                return DefaultNetworkPathSelection.select(
                    selected_path=requested_path,
                    confidence=0.95,
                    considered_paths=(requested_path,),
                    exclusion_reasons=(),
                )
        
        # Determine candidate paths based on purpose
        candidates = self._candidate_paths_for_purpose(purpose)
        
        if not candidates:
            return DefaultNetworkPathSelection.select(
                selected_path="thought_generation",
                confidence=0.5,
                considered_paths=self._supported_paths or (),
                exclusion_reasons=("No suitable path found for purpose",),
            )
        
        # Filter to supported paths only
        supported_candidates = tuple(p for p in candidates if self._is_supported(p))
        
        if not supported_candidates:
            return DefaultNetworkPathSelection.select(
                selected_path=self._supported_paths[0] if self._supported_paths else "thought_generation",
                confidence=0.5,
                considered_paths=candidates,
                exclusion_reasons=("No candidate paths are supported",),
            )
        
        # Apply priority rules to select from candidates
        selected = self._apply_priority_rules(
            purpose=purpose,
            subject=subject or "",
            candidates=supported_candidates,
            context_available=context_available,
        )
        
        return DefaultNetworkPathSelection.select(
            selected_path=selected,
            confidence=self._calculate_confidence(selected, purpose),
            considered_paths=candidates,
            exclusion_reasons=self._build_exclusion_reasons(candidates, selected),
        )
    
    def _is_supported(self, path: str) -> bool:
        """Check if a path is in the supported paths list."""
        if not self._supported_paths:
            return True  # All paths supported if list is empty
        return path in self._supported_paths
    
    def _candidate_paths_for_purpose(self, purpose: str) -> Tuple[str, ...]:
        """
        Get candidate paths for a given purpose.
        
        Each purpose maps to one or more candidate paths based on
        the coordination requirements.
        """
        # Purpose to candidate path mapping
        purpose_candidates = {
            "generate_internal_thought": ("thought_generation",),
            "continue_internal_episode": ("thought_generation", "reflection"),
            "coordinate_reflection": ("reflection",),
            "coordinate_simulation": ("simulation",),
            "coordinate_counterfactual": ("counterfactual",),
            "coordinate_narrative": ("narrative",),
            "integrate_identity": ("identity",),
            "integrate_memory": ("memory",),
            "integrate_prediction": ("predictive",),
            "prepare_workspace_candidate": ("workspace",),
            "review_internal_context": ("context_review",),
            "integrate_external_result": (
                "thought_generation",
                "reflection",
            ),
            "resolve_internal_conflict": (
                "reflection",
                "counterfactual",
            ),
            "assess_internal_continuation": ("thought_generation", "reflection"),
            "general_internal_cognition": ("thought_generation",),
        }
        
        return purpose_candidates.get(purpose, ("thought_generation",))
    
    def _apply_priority_rules(
        self,
        purpose: str,
        subject: str,
        candidates: Tuple[str, ...],
        context_available: dict[str, bool],
    ) -> str:
        """
        Apply priority rules to select among candidate paths.
        
        Uses explicit deterministic rules based on:
            - Purpose
            - Subject type
            - Available context
            - Configuration preferences
        
        Returns the selected path.
        """
        if not candidates:
            return "thought_generation"
        
        # Priority 1: If a specific subject is mentioned, use the matching path
        subject_to_path = {
            "unresolved_contradiction": "reflection",
            "missing_evidence": "simulation",
            "goal_relevance": "predictive",
            "narrative_gap": "narrative",
            "identity_conflict": "identity",
            "prediction_error": "predictive",
        }
        
        if subject in subject_to_path:
            path = subject_to_path[subject]
            if path in candidates:
                return path
        
        # Priority 2: Use the first candidate (deterministic ordering)
        return candidates[0]
    
    def _calculate_confidence(
        self,
        selected_path: str,
        purpose: str,
    ) -> float:
        """
        Calculate confidence in a path selection.
        
        Based on:
            - How strongly the purpose maps to the path
            - Whether an explicit path was requested
            - Context availability
        """
        # Default base confidence
        confidence = 0.5
        
        # Increase if purpose has strong mapping to selected path
        if purpose == "coordinate_reflection" and selected_path == "reflection":
            confidence += 0.3
        elif purpose == "coordinate_simulation" and selected_path == "simulation":
            confidence += 0.3
        elif purpose == "coordinate_narrative" and selected_path == "narrative":
            confidence += 0.3
        
        # Cap at maximum
        return min(1.0, max(0.0, confidence))
    
    def _build_exclusion_reasons(
        self,
        candidates: Tuple[str, ...],
        selected: str,
    ) -> Tuple[str, ...]:
        """Build human-readable reasons why other paths were excluded."""
        reasons = []
        
        for path in candidates:
            if path != selected:
                reasons.append(f"Lower priority than {selected}")
        
        return tuple(reasons)

# =============================================================================
# BUILT-IN PATH SELECTOR FACTORY
# =============================================================================

def create_default_path_selector() -> DefaultNetworkPathSelector:
    """
    Create a default path selector with standard configuration.
    
    Returns:
        Selector with sensible defaults for production use
    """
    # All canonical paths are supported by default
    supported_paths = (
        "thought_generation",
        "reflection",
        "simulation",
        "counterfactual",
        "narrative",
        "identity",
        "memory",
        "predictive",
        "workspace",
        "context_review",
    )
    
    return DefaultNetworkPathSelector(
        supported_paths=supported_paths,
        default_path_by_purpose={
            "general_internal_cognition": "thought_generation",
        },
    )