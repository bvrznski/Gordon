# Gordon Phase 5.7.2-I: Experiential Field Normalization
# ===============================================================================
#
# Contribution normalization for the experiential field.
#

"""
Contribution normalization module for Experiential Field Builder.

This module handles normalizing contributions into canonical internal form:
    - Source-specific kind mapping to canonical kinds
    - ID normalization
    - Timestamp normalization  
    - Privacy/trust classification normalization
    - Payload reference standardization
"""

from __future__ import annotations

import time
from dataclasses import dataclass, field
from typing import Tuple, Optional


@dataclass(frozen=True)
class NormalizationAction:
    """
    Record of an action taken during normalization.
    
    Used for diagnostics and auditing of the normalization process.
    """
    
    action: str
    """Type of action taken."""
    
    source_field: Optional[str] = None
    """Field that was normalized (if applicable)."""
    
    original_value: Optional[str] = None
    """Original value before normalization."""
    
    normalized_value: Optional[str] = None
    """Value after normalization."""
    
    reason: Optional[str] = None
    """Reason for the action (optional)."""


@dataclass
class ContributionNormalizer:
    """
    Normalizes contributions to canonical internal form.
    
    The normalizer transforms various source-specific contribution formats
    into a consistent internal representation while preserving provenance
    and classification integrity.
    
    Important: Normalization does not:
        - Infer truth (original claims preserved)
        - Upgrade trust (original classification maintained)
        - Invent missing data
        - Rewrite semantic meaning
    """
    
    # Configuration
    canonical_content_kinds: Tuple[str, ...] = field(default_factory=lambda: (
        "workspace", "perceptual", "memory", "working_memory",
        "salience", "attention", "personality", "motivation",
        "cognition", "action_feedback"
    ))
    """Set of content kinds this normalizer supports."""
    
    # Source-to-kind mappings
    source_kind_mappings: dict[str, str] = field(default_factory=dict)
    """Map from source-specific kinds to canonical kinds."""
    
    def __post_init__(self):
        """Initialize after construction."""
        if isinstance(self.canonical_content_kinds, tuple):
            self.canonical_content_kinds = self.canonical_content_kinds
        else:
            self.canonical_content_kinds = tuple(self.canonical_content_kinds)
        
        # Build default mappings for common sources
        if not self.source_kind_mappings:
            self.source_kind_mappings = {
                "workspace:candidate": "workspace",
                "perception:detected_object": "perceptual",
                "memory:retrieved_item": "memory",
                "working_memory:active_task": "working_memory",
            }
    
    def normalize_source_id(self, source_id: str) -> Tuple[str, NormalizationAction]:
        """
        Normalize a source ID to canonical form.
        
        Args:
            source_id: Source ID from contribution
            
        Returns:
            Tuple of (normalized_id, action_record)
        """
        # In this implementation, source IDs are kept as-is
        return source_id, NormalizationAction(
            action="source_id_preserved",
            source_field="source_id",
            original_value=source_id,
            normalized_value=source_id,
        )
    
    def normalize_kind(self, kind: str, source_id: str) -> Tuple[str, NormalizationAction]:
        """
        Normalize a content kind to canonical form.
        
        Args:
            kind: Content kind from contribution
            source_id: Source submitting the contribution
            
        Returns:
            Tuple of (canonical_kind, action_record)
        """
        # Check if there's a source-specific mapping
        mapping_key = f"{source_id}:{kind}" if source_id else kind
        
        if mapping_key in self.source_kind_mappings:
            canonical = self.source_kind_mappings[mapping_key]
            return canonical, NormalizationAction(
                action="kind_mapped",
                source_field="content_kind",
                original_value=kind,
                normalized_value=canonical,
                reason=f"Source-specific mapping: {mapping_key}",
            )
        
        # Check if kind is already canonical
        if kind in self.canonical_content_kinds:
            return kind, NormalizationAction(
                action="kind_preserved",
                source_field="content_kind",
                original_value=kind,
                normalized_value=kind,
            )
        
        # Fall back to generic
        return "generic", NormalizationAction(
            action="kind_fallback",
            source_field="content_kind",
            original_value=kind,
            normalized_value="generic",
            reason=f"Kind not in canonical set, mapped to 'generic'",
        )
    
    def normalize_privacy(self, privacy: str) -> Tuple[str, NormalizationAction]:
        """
        Normalize privacy classification.
        
        This preserves the original classification without upgrading.
        """
        valid = ("public", "internal", "restricted", "private")
        
        if privacy in valid:
            return privacy, NormalizationAction(
                action="privacy_preserved",
                source_field="privacy_classification",
                original_value=privacy,
                normalized_value=privacy,
            )
        
        # Downgrade to internal as safe default
        return "internal", NormalizationAction(
            action="privacy_downgraded",
            source_field="privacy_classification",
            original_value=privacy or "unknown",
            normalized_value="internal",
            reason="Privacy classification not recognized, downgraded to 'internal'",
        )
    
    def normalize_trust(self, trust: str) -> Tuple[str, NormalizationAction]:
        """
        Normalize trust classification.
        
        This preserves the original classification without upgrading.
        """
        valid = ("untrusted", "low_confidence", "medium", "high", "internal_trusted")
        
        if trust in valid:
            return trust, NormalizationAction(
                action="trust_preserved",
                source_field="trust_classification",
                original_value=trust,
                normalized_value=trust,
            )
        
        # Downgrade to untrusted as safe default
        return "untrusted", NormalizationAction(
            action="trust_downgraded",
            source_field="trust_classification",
            original_value=trust or "unknown",
            normalized_value="untrusted",
            reason="Trust classification not recognized, downgraded to 'untrusted'",
        )
    
    def normalize_timestamp(self, timestamp: Optional[float]) -> Tuple[float, NormalizationAction]:
        """
        Normalize a UTC timestamp.
        
        Args:
            timestamp: Unix timestamp (seconds since epoch)
            
        Returns:
            Tuple of (normalized_timestamp, action_record)
        """
        if timestamp is None or timestamp <= 0:
            normalized = time.time()
            return normalized, NormalizationAction(
                action="timestamp_defaulted",
                source_field="freshness_utc",
                original_value=str(timestamp),
                normalized_value=str(normalized),
                reason="Timestamp was invalid or missing, defaulted to current time",
            )
        
        return timestamp, NormalizationAction(
            action="timestamp_preserved",
            source_field="freshness_utc",
            original_value=str(timestamp),
            normalized_value=str(timestamp),
        )
    
    def normalize(self, kind: str, privacy: str, trust: str) -> Tuple[dict, tuple]:
        """
        Run all normalizations and return the result.
        
        Args:
            kind: Content kind from contribution
            privacy: Privacy classification
            trust: Trust classification
            
        Returns:
            Tuple of (normalized_values_dict, tuple_of_action_records)
        """
        # Get normalized values
        norm_kind, kind_action = self.normalize_kind(kind, "unknown_source")
        norm_privacy, privacy_action = self.normalize_privacy(privacy)
        norm_trust, trust_action = self.normalize_trust(trust)
        
        actions: Tuple[NormalizationAction, ...] = (
            kind_action,
            privacy_action,
            trust_action,
        )
        
        return {
            "content_kind": norm_kind,
            "privacy_classification": norm_privacy,
            "trust_classification": norm_trust,
        }, actions


# =============================================================================
# EXPORTS
# =============================================================================

__all__: tuple[str, ...] = (
    "NormalizationAction",
    "ContributionNormalizer",
)