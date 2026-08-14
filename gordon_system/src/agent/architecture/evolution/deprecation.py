# Gordon Core: Deprecation Architecture (Phase 3.33)
"""
Deprecation Architecture - Provides canonical deprecation policies and
lifecycles for all artifacts in the Gordon Core.
"""

from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from typing import Dict, List, Any, Optional


# ============================================================================
# DEPRECATION POLICY MODEL
# ============================================================================

@dataclass(frozen=True)
class DeprecationPolicy:
    """
    Immutable deprecation policy for an artifact.
    
    Defines the rules and timeline for deprecating an artifact:
    - When deprecation begins
    - How long before removal
    - What replacement is recommended
    - What compatibility guarantees are provided
    """
    
    # Policy identity
    id: str                        # Unique policy identifier
    
    # Artifact information
    artifact_id: str              # ID of artifact being deprecated
    reason: str                   # Reason for deprecation
    
    # Timeline
    effective_from: datetime      # When deprecation takes effect
    removal_at: datetime          # When artifact will be removed
    
    # Replacement information
    replacement_artifact: Optional[str] = None  # Recommended replacement
    compatibility_mode: str = "rolling"         # How compatibility is maintained
    
    # Policy properties
    is_active: bool = True        # Whether policy is currently active
    requires_migration: bool = False  # Whether migration is required
    
    @property
    def warning_period_days(self) -> int:
        """Get the number of days before removal when warnings start."""
        return (self.removal_at - self.effective_from).days // 2
    
    @property
    def warning_start_date(self) -> datetime:
        """Get the date when warnings should begin."""
        return self.removal_at - timedelta(days=self.warning_period_days)
    
    @property
    def is_warning_period(self, at: datetime = None) -> bool:
        """Check if current time is in warning period."""
        check_date = at or datetime.now()
        return check_date >= self.warning_start_date
    
    @property
    def days_until_removal(self, at: datetime = None) -> int:
        """Get the number of days until removal."""
        check_date = at or datetime.now()
        return (self.removal_at - check_date).days
    
    @property
    def is_ready_for_removal(self, at: datetime = None) -> bool:
        """Check if artifact can be removed."""
        check_date = at or datetime.now()
        return check_date >= self.removal_at


# ============================================================================
# DEPRECATION TIMELINE MODEL
# ============================================================================

@dataclass(frozen=True)
class DeprecationTimeline:
    """
    Immutable deprecation timeline showing all milestones.
    """
    
    # Timeline identity
    id: str                        # Unique timeline identifier
    
    # Milestones (ordered chronologically)
    milestones: List[Dict[str, Any]] = field(default_factory=list)
    
    def add_milestone(
        self,
        date: datetime,
        event_type: str,
        description: str,
        required_action: Optional[str] = None
    ) -> "DeprecationTimeline":
        """Add a milestone to the timeline."""
        new_milestones = list(self.milestones)
        new_milestones.append({
            "date": date,
            "type": event_type,
            "description": description,
            "action": required_action
        })
        
        # Sort by date
        new_milestones.sort(key=lambda m: m["date"])
        
        return DeprecationTimeline(
            id=self.id,
            milestones=new_milestones
        )
    
    def get_next_milestone(self, at: datetime = None) -> Optional[Dict[str, Any]]:
        """Get the next milestone after a given date."""
        check_date = at or datetime.now()
        
        for milestone in self.milestones:
            if milestone["date"] > check_date:
                return milestone
        
        return None
    
    def get_completed_milestones(self, at: datetime = None) -> List[Dict[str, Any]]:
        """Get all milestones completed before a given date."""
        check_date = at or datetime.now()
        
        return [
            m for m in self.milestones
            if m["date"] <= check_date
        ]


# ============================================================================
# DEPRECATION NOTICE MODEL
# ============================================================================

@dataclass(frozen=True)
class DeprecationNotice:
    """
    Immutable deprecation notice generated from a policy.
    
    Represents the actual notice that would be presented to consumers of a
    deprecated artifact.
    """
    
    # Notice identity
    id: str                        # Unique notice identifier
    
    # Artifact being deprecated
    artifact_id: str              # ID of the deprecated artifact
    current_version: str          # Current version
    
    # Deprecation information
    policy: Optional[DeprecationPolicy] = None  # Underlying policy (optional)
    reason: str                   # Reason for deprecation
    replacement_artifact: Optional[str] = None  # Recommended replacement
    
    # Timeline
    effective_from: datetime      # When deprecation takes effect
    removal_at: datetime          # When artifact will be removed
    days_until_removal: int       # Days until removal
    
    # Status
    is_active: bool = True        # Whether notice is currently active
    is_warning_period: bool = False  # In warning period?
    
    # Consumers (optional - who needs to act)
    affected_consumers: List[str] = field(default_factory=list)
    
    @property
    def severity(self) -> str:
        """Get the severity of the deprecation notice."""
        if self.days_until_removal <= 7:
            return "critical"
        elif self.days_until_removal <= 30:
            return "high"
        elif self.is_warning_period:
            return "medium"
        else:
            return "low"


# ============================================================================
# DEPRECATION NOTIFIER
# ============================================================================

class DeprecationNotifier:
    """
    Notifier for deprecation events.
    
    Generates and manages deprecation notices based on policies and timelines.
    """
    
    def __init__(self):
        self._notices: Dict[str, DeprecationNotice] = {}
        self._policies: Dict[str, DeprecationPolicy] = {}
    
    def register_policy(self, policy: DeprecationPolicy) -> None:
        """Register a deprecation policy."""
        self._policies[policy.id] = policy
    
    def generate_notice(
        self,
        artifact_id: str,
        current_version: str,
        reason: str,
        replacement_artifact: Optional[str] = None,
        effective_from: datetime = None,
        removal_at: datetime = None
    ) -> DeprecationNotice:
        """Generate a deprecation notice for an artifact."""
        policy = self._policies.get(artifact_id)
        
        if policy:
            # Use policy values
            notice = DeprecationNotice(
                id=f"notice-{artifact_id}",
                artifact_id=artifact_id,
                current_version=current_version,
                policy=policy,
                reason=reason or policy.reason,
                replacement_artifact=replacement_artifact or policy.replacement_artifact,
                effective_from=policy.effective_from,
                removal_at=policy.removal_at,
                days_until_removal=policy.days_until_removal(),
                is_active=policy.is_active,
                is_warning_period=policy.is_warning_period()
            )
        else:
            # Create new notice with provided values
            effective = effective_from or datetime.now()
            removal = removal_at or (effective + timedelta(days=90))
            
            notice = DeprecationNotice(
                id=f"notice-{artifact_id}",
                artifact_id=artifact_id,
                current_version=current_version,
                reason=reason,
                replacement_artifact=replacement_artifact,
                effective_from=effective,
                removal_at=removal,
                days_until_removal=(removal - datetime.now()).days,
                is_active=True,
                is_warning_period=False
            )
        
        self._notices[artifact_id] = notice
        return notice
    
    def get_notice(self, artifact_id: str) -> Optional[DeprecationNotice]:
        """Get the deprecation notice for an artifact."""
        return self._notices.get(artifact_id)
    
    def list_active_notices(self) -> List[DeprecationNotice]:
        """List all active deprecation notices."""
        return [
            n for n in self._notices.values()
            if n.is_active
        ]
    
    def get_critical_notices(self) -> List[DeprecationNotice]:
        """Get all critical priority notices (<= 7 days until removal)."""
        return [
            n for n in self._notices.values()
            if n.severity == "critical"
        ]


# ============================================================================
# DEPRECATION POLICY BUILDER
# ============================================================================

class DeprecationPolicyBuilder:
    """
    Builder for constructing deprecation policies.
    
    Provides a fluent API for creating complex deprecation policies with
    multiple timelines and replacement strategies.
    """
    
    def __init__(self):
        self._id: str = ""
        self._artifact_id: str = ""
        self._reason: str = ""
        self._effective_from: datetime = None
        self._removal_at: datetime = None
        self._replacement_artifact: Optional[str] = None
        self._requires_migration: bool = False
    
    def with_id(self, policy_id: str) -> "DeprecationPolicyBuilder":
        """Set the policy ID."""
        self._id = policy_id
        return self
    
    def for_artifact(self, artifact_id: str) -> "DeprecationPolicyBuilder":
        """Set the artifact being deprecated."""
        self._artifact_id = artifact_id
        return self
    
    def with_reason(self, reason: str) -> "DeprecationPolicyBuilder":
        """Set the deprecation reason."""
        self._reason = reason
        return self
    
    def effective_from(self, date: datetime) -> "DeprecationPolicyBuilder":
        """Set when deprecation takes effect."""
        self._effective_from = date
        return self
    
    def until_removal(self, date: datetime) -> "DeprecationPolicyBuilder":
        """Set when artifact will be removed."""
        self._removal_at = date
        return self
    
    def with_replacement(self, replacement_id: str) -> "DeprecationPolicyBuilder":
        """Set the recommended replacement artifact."""
        self._replacement_artifact = replacement_id
        return self
    
    def requires_migration(self, requires: bool = True) -> "DeprecationPolicyBuilder":
        """Specify whether migration is required."""
        self._requires_migration = requires
        return self
    
    def build(self) -> DeprecationPolicy:
        """Build the deprecation policy."""
        if not all([
            self._id,
            self._artifact_id,
            self._effective_from,
            self._removal_at
        ]):
            raise ValueError("All required fields must be set")
        
        return DeprecationPolicy(
            id=self._id,
            artifact_id=self._artifact_id,
            reason=self._reason,
            effective_from=self._effective_from,
            removal_at=self._removal_at,
            replacement_artifact=self._replacement_artifact,
            requires_migration=self._requires_migration
        )


# ============================================================================
# UTILITY FUNCTIONS
# ============================================================================

def get_deprecation_severity(days_until_removal: int) -> str:
    """Get the severity level based on days until removal."""
    if days_until_removal <= 7:
        return "critical"
    elif days_until_removal <= 30:
        return "high"
    elif days_until_removal <= 90:
        return "medium"
    else:
        return "low"


def create_default_timeline(
    artifact_id: str,
    effective_from: datetime = None,
    removal_at: datetime = None
) -> DeprecationTimeline:
    """Create a default deprecation timeline with standard milestones."""
    if effective_from is None:
        effective_from = datetime.now()
    
    if removal_at is None:
        removal_at = effective_from + timedelta(days=90)
    
    warning_start = removal_at - timedelta(days=30)
    critical_start = removal_at - timedelta(days=7)
    
    timeline = DeprecationTimeline(
        id=f"timeline-{artifact_id}",
        milestones=[
            {
                "date": effective_from,
                "type": "deprecation-effective",
                "description": "Deprecation takes effect"
            },
            {
                "date": warning_start,
                "type": "warning-start",
                "description": "Warnings begin for consumers",
                "action": "Review deprecation notice and plan migration"
            },
            {
                "date": critical_start,
                "type": "critical-warning",
                "description": "Critical warning period begins",
                "action": "Migrate to replacement immediately"
            },
            {
                "date": removal_at,
                "type": "removal",
                "description": "Artifact is removed from codebase",
                "action": "Artifact no longer available"
            }
        ]
    )
    
    return timeline