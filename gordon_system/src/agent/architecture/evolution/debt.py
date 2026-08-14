# Gordon Core: Technical Debt Architecture (Phase 3.33)
"""
Technical Debt Architecture - Provides canonical framework for managing,
tracking, and retiring architectural technical debt in the Gordon Core.
"""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Dict, List, Any, Optional


# ============================================================================
# DEBT CLASSIFICATION ENUMERATION
# ============================================================================

class DebtClassification(Enum):
    """
    Canonical classifications of technical debt.
    
    - ARCHITECTURAL: Architecture decisions that limit future options
    - CODE: Code-level issues (technical debt in implementation)
    - TEST: Missing or insufficient test coverage
    - DOCUMENTATION: Incomplete or outdated documentation
    - CONFIGURATION: Suboptimal configuration choices
    - DEPENDENCY: Outdated dependencies with known issues
    - SECURITY: Security-related technical debt
    """
    
    ARCHITECTURAL = "architectural"   # Architectural limitations
    CODE = "code"                     # Implementation issues
    TEST = "test"                     # Test coverage gaps
    DOCUMENTATION = "documentation"   # Documentation gaps
    CONFIGURATION = "configuration"   # Configuration debt
    DEPENDENCY = "dependency"         # Dependency debt
    SECURITY = "security"             # Security-related debt


# ============================================================================
# DEBT PRIORITY ENUMERATION
# ============================================================================

class DebtPriority(Enum):
    """
    Canonical priority levels for technical debt.
    
    - CRITICAL: Blocks development or releases, must be fixed immediately
    - HIGH: Impacts quality significantly, should be addressed soon
    - MEDIUM: Noticeable impact but not blocking, planned for future
    - LOW: Minor issues, can be deferred to next cycle
    """
    
    CRITICAL = "critical"           # Must fix now
    HIGH = "high"                   # Fix soon
    MEDIUM = "medium"               # Planned future
    LOW = "low"                     # Deferred


# ============================================================================
# DEBT METRICS MODEL
# ============================================================================

@dataclass(frozen=True)
class DebtMetrics:
    """
    Immutable metrics for technical debt.
    
    Provides quantitative measures of technical debt across the repository.
    """
    
    # Metrics identity
    id: str                        # Unique metrics identifier
    
    # Debt counts by classification
    total_debt_items: int = 0
    debt_by_classification: Dict[str, int] = field(default_factory=dict)
    
    # Debt counts by priority
    debt_by_priority: Dict[str, int] = field(default_factory=dict)
    
    # Monetary estimates (if available)
    estimated_remediation_cost: float = 0.0  # Estimated effort points
    
    # Metrics
    avg_age_days: int = 0          # Average age of debt items in days
    open_debt_ratio: float = 0.0   # Ratio of open to total debt
    
    # Trend data
    new_this_period: int = 0       # New debt items in this period
    resolved_this_period: int = 0  # Resolved debt items in this period
    
    @property
    def critical_debt_count(self) -> int:
        """Get the count of critical priority debt."""
        return self.debt_by_priority.get("critical", 0)
    
    @property
    def high_priority_debt_count(self) -> int:
        """Get the count of high priority debt."""
        return self.debt_by_priority.get("high", 0)
    
    @property
    def can_deploy(self) -> bool:
        """Check if repository is ready to deploy (no critical debt)."""
        return self.critical_debt_count == 0
    
    @property
    def debt_score(self) -> float:
        """Calculate overall debt score (0.0 to 1.0, where 1.0 is worse)."""
        if self.total_debt_items == 0:
            return 0.0
        
        # Weight by priority
        weights = {
            "critical": 4,
            "high": 3,
            "medium": 2,
            "low": 1
        }
        
        total_weight = sum(
            self.debt_by_priority.get(priority, 0) * weight
            for priority, weight in weights.items()
        )
        
        max_possible = self.total_debt_items * 4  # If all were critical
        
        return min(total_weight / max_possible if max_possible > 0 else 0.0, 1.0)


# ============================================================================
# TECHNICAL DEBT ITEM MODEL
# ============================================================================

@dataclass(frozen=True)
class TechnicalDebtItem:
    """
    Immutable technical debt item record.
    
    Represents a single piece of technical debt with its full context and
    remediation plan.
    """
    
    # Item identity
    id: str                        # Unique identifier
    
    # Item information
    artifact_id: str              # ID of affected artifact
    classification: DebtClassification  # Type of debt
    priority: DebtPriority        # Priority level
    
    # Description and context
    description: str              # Human-readable description
    impact: str                   # Impact on system/development
    root_cause: Optional[str] = None  # Root cause analysis (optional)
    
    # Timeline
    identified_at: datetime       # When debt was identified
    estimated_resolution_at: Optional[datetime] = None  # Target resolution date
    
    # Remediation
    remediation_plan: Optional[str] = None  # How to fix it
    owner: Optional[str] = None   # Person responsible for remediation
    is_resolved: bool = False     # Whether debt has been resolved
    
    @property
    def age_days(self) -> int:
        """Get the age of this debt item in days."""
        return (datetime.now() - self.identified_at).days
    
    @property
    def days_until_estimated_resolution(self) -> Optional[int]:
        """Get days until estimated resolution date."""
        if not self.estimated_resolution_at:
            return None
        
        return (self.estimated_resolution_at - datetime.now()).days


# ============================================================================
# TECHNICAL DEBT MANAGER CLASS
# ============================================================================

class TechnicalDebtManager:
    """
    Manager for technical debt tracking and remediation.
    
    Provides operations for identifying, tracking, prioritizing, and
    retiring technical debt items.
    """
    
    def __init__(self):
        self._debt_items: Dict[str, TechnicalDebtItem] = {}
        self._metrics: DebtMetrics = None
    
    def add_debt_item(
        self,
        item_id: str,
        artifact_id: str,
        classification: DebtClassification,
        priority: DebtPriority,
        description: str,
        impact: str
    ) -> TechnicalDebtItem:
        """Add a new debt item."""
        item = TechnicalDebtItem(
            id=item_id,
            artifact_id=artifact_id,
            classification=classification,
            priority=priority,
            description=description,
            impact=impact,
            identified_at=datetime.now()
        )
        
        self._debt_items[item_id] = item
        return item
    
    def get_debt_item(self, item_id: str) -> Optional[TechnicalDebtItem]:
        """Get a debt item by ID."""
        return self._debt_items.get(item_id)
    
    def resolve_debt_item(
        self,
        item_id: str,
        resolved_at: datetime = None
    ) -> TechnicalDebtItem:
        """Mark a debt item as resolved."""
        item = self._debt_items.get(item_id)
        
        if not item:
            raise ValueError(f"Debt item '{item_id}' not found")
        
        item = TechnicalDebtItem(
            id=item.id,
            artifact_id=item.artifact_id,
            classification=item.classification,
            priority=item.priority,
            description=item.description,
            impact=item.impact,
            root_cause=item.root_cause,
            identified_at=item.identified_at,
            estimated_resolution_at=item.estimated_resolution_at,
            remediation_plan=item.remediation_plan,
            owner=item.owner,
            is_resolved=True
        )
        
        self._debt_items[item_id] = item
        return item
    
    def list_debt_items(
        self,
        classification: DebtClassification = None,
        priority: DebtPriority = None
    ) -> List[TechnicalDebtItem]:
        """List debt items, optionally filtered."""
        items = list(self._debt_items.values())
        
        if classification:
            items = [i for i in items if i.classification == classification]
        
        if priority:
            items = [i for i in items if i.priority == priority]
        
        # Sort by priority (critical first)
        priority_order = {
            DebtPriority.CRITICAL: 0,
            DebtPriority.HIGH: 1,
            DebtPriority.MEDIUM: 2,
            DebtPriority.LOW: 3
        }
        
        items.sort(key=lambda i: priority_order.get(i.priority, 4))
        
        return items
    
    def get_metrics(self) -> DebtMetrics:
        """Get current debt metrics."""
        if not self._debt_items:
            return DebtMetrics(id="metrics-empty")
        
        # Calculate counts by classification
        by_classification = {}
        for item in self._debt_items.values():
            key = item.classification.value
            by_classification[key] = by_classification.get(key, 0) + 1
        
        # Calculate counts by priority
        by_priority = {"critical": 0, "high": 0, "medium": 0, "low": 0}
        for item in self._debt_items.values():
            key = item.priority.value
            if key in by_priority:
                by_priority[key] += 1
        
        # Calculate average age
        total_age = sum(item.age_days for item in self._debt_items.values())
        avg_age = total_age // len(self._debt_items) if self._debt_items else 0
        
        # Calculate open ratio
        open_count = sum(1 for i in self._debt_items.values() if not i.is_resolved)
        
        return DebtMetrics(
            id=f"metrics-{datetime.now().isoformat()}",
            total_debt_items=len(self._debt_items),
            debt_by_classification=by_classification,
            debt_by_priority=by_priority,
            avg_age_days=avg_age,
            open_debt_ratio=open_count / len(self._debt_items) if self._debt_items else 0.0
        )
    
    def get_critical_debt(self) -> List[TechnicalDebtItem]:
        """Get all critical priority debt items."""
        return [
            item for item in self._debt_items.values()
            if item.priority == DebtPriority.CRITICAL and not item.is_resolved
        ]
    
    def get_high_priority_debt(self) -> List[TechnicalDebtItem]:
        """Get all high priority debt items."""
        return [
            item for item in self._debt_items.values()
            if item.priority == DebtPriority.HIGH and not item.is_resolved
        ]