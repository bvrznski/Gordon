# Gordon Core: Repository Evolution Metrics (Phase 3.33)
"""
Repository Evolution Metrics - Provides canonical architectural metrics for
tracking evolution, migration, upgrade, and drift across the Gordon Core.
"""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Dict, List, Any, Optional


# ============================================================================
# EVOLUTION METRICS MODEL
# ============================================================================

@dataclass(frozen=True)
class EvolutionMetrics:
    """
    Immutable metrics for evolution activities across the repository.
    
    Provides quantitative measurements of all evolution, migration, upgrade,
    and deprecation activities in the Gordon Core.
    """
    
    # Metrics identity
    id: str                        # Unique identifier
    
    # Timeline
    period_start: datetime        # Start of measurement period
    period_end: datetime          # End of measurement period
    
    # Evolution counts by type
    evolution_count_by_type: Dict[str, int] = field(default_factory=dict)
    
    # Migration metrics
    migration_count: int = 0       # Total migrations planned/executed
    migration_success_rate: float = 1.0  # Percentage successful
    
    # Upgrade metrics
    upgrade_count: int = 0         # Total upgrades
    upgrade_success_rate: float = 1.0  # Percentage successful
    
    # Deprecation metrics
    deprecation_count: int = 0     # Deprecated artifacts
    deprecation_with_replacement: int = 0  # With recommended replacement
    
    # Drift metrics
    drift_detection_count: int = 0  # Total drift detections
    drift_by_severity: Dict[str, int] = field(default_factory=dict)
    
    # Technical debt metrics
    technical_debt_items: int = 0   # Active debt items
    critical_debt_items: int = 0    # Critical priority items
    
    @property
    def total_evolution_count(self) -> int:
        """Get total evolution count across all types."""
        return sum(self.evolution_count_by_type.values())
    
    @property
    def can_deploy(self) -> bool:
        """Check if repository is ready to deploy."""
        return (
            self.migration_success_rate >= 0.95 and
            self.upgrade_success_rate >= 0.95 and
            self.critical_debt_items == 0 and
            self.drift_by_severity.get("high", 0) == 0
        )


# ============================================================================
# REPOSITORY EVOLUTION SCORE MODEL
# ============================================================================

@dataclass(frozen=True)
class RepositoryEvolutionScore:
    """
    Immutable score for repository evolution health.
    
    Combines multiple metrics into a single health score (0.0 to 1.0,
    where 1.0 is healthy and ready for evolution).
    """
    
    # Score identity
    id: str                        # Unique identifier
    
    # Component scores (0.0 to 1.0 each)
    evolution_score: float = 1.0   # Evolution activity health
    migration_score: float = 1.0   # Migration success rate
    upgrade_score: float = 1.0     # Upgrade success rate
    compatibility_score: float = 1.0  # Compatibility health
    debt_score: float = 1.0        # Technical debt score
    drift_score: float = 1.0       # Drift detection effectiveness
    
    # Timestamp
    scored_at: datetime = field(default_factory=datetime.now)
    
    @property
    def composite_score(self) -> float:
        """Calculate overall repository evolution health score."""
        weights = {
            "evolution": 0.2,
            "migration": 0.15,
            "upgrade": 0.15,
            "compatibility": 0.2,
            "debt": 0.2,
            "drift": 0.1
        }
        
        score = (
            self.evolution_score * weights["evolution"] +
            self.migration_score * weights["migration"] +
            self.upgrade_score * weights["upgrade"] +
            self.compatibility_score * weights["compatibility"] +
            self.debt_score * weights["debt"] +
            self.drift_score * weights["drift"]
        )
        
        return round(score, 3)
    
    @property
    def status(self) -> str:
        """Get overall status based on composite score."""
        if self.composite_score >= 0.9:
            return "EXCELLENT"
        elif self.composite_score >= 0.75:
            return "GOOD"
        elif self.composite_score >= 0.6:
            return "NEEDS_ATTENTION"
        else:
            return "CRITICAL"


# ============================================================================
# EVOLUTION METRICS CALCULATOR
# ============================================================================

class EvolutionMetricsCalculator:
    """
    Calculator for repository evolution metrics.
    
    Aggregates data from various sources to produce comprehensive metrics
    about the repository's evolution health and readiness.
    """
    
    def __init__(self):
        self._evolution_data: Dict[str, Any] = {}
        self._metrics: EvolutionMetrics = None
    
    def record_evolution(
        self,
        type_name: str,
        success: bool = True
    ) -> None:
        """Record an evolution event."""
        current_count = self._evolution_data.get(f"evolutions_{type_name}", 0)
        self._evolution_data[f"evolutions_{type_name}"] = current_count + 1
    
    def record_migration(
        self,
        success: bool = True
    ) -> None:
        """Record a migration event."""
        if success:
            self._evolution_data["migrations_success"] = (
                self._evolution_data.get("migrations_success", 0) + 1
            )
        
        self._evolution_data["migrations_total"] = (
            self._evolution_data.get("migrations_total", 0) + 1
        )
    
    def record_upgrade(
        self,
        success: bool = True
    ) -> None:
        """Record an upgrade event."""
        if success:
            self._evolution_data["upgrades_success"] = (
                self._evolution_data.get("upgrades_success", 0) + 1
            )
        
        self._evolution_data["upgrades_total"] = (
            self._evolution_data.get("upgrades_total", 0) + 1
        )
    
    def record_deprecation(
        self,
        with_replacement: bool = False
    ) -> None:
        """Record a deprecation event."""
        if with_replacement:
            self._evolution_data["deprecations_with_replacement"] = (
                self._evolution_data.get("deprecations_with_replacement", 0) + 1
            )
        
        self._evolution_data["deprecations_total"] = (
            self._evolution_data.get("deprecations_total", 0) + 1
        )
    
    def record_drift(
        self,
        severity: str = "low"
    ) -> None:
        """Record a drift detection."""
        severity_key = f"drift_{severity}"
        self._evolution_data[severity_key] = (
            self._evolution_data.get(severity_key, 0) + 1
        )
        
        self._evolution_data["drift_total"] = (
            self._evolution_data.get("drift_total", 0) + 1
        )
    
    def record_debt_item(
        self,
        priority: str = "low"
    ) -> None:
        """Record a debt item."""
        if priority == "critical":
            self._evolution_data["debt_critical"] = (
                self._evolution_data.get("debt_critical", 0) + 1
            )
        
        self._evolution_data["debt_total"] = (
            self._evolution_data.get("debt_total", 0) + 1
        )
    
    def calculate_metrics(self, period_start: datetime, period_end: datetime) -> EvolutionMetrics:
        """Calculate evolution metrics for a period."""
        # Build evolution count by type
        evolution_types = ["module", "interface", "schema", "config"]
        evolutions_by_type = {}
        
        for ev_type in evolution_types:
            key = f"evolutions_{ev_type}"
            evolutions_by_type[ev_type] = self._evolution_data.get(key, 0)
        
        # Calculate migration success rate
        migrations_success = self._evolution_data.get("migrations_success", 0)
        migrations_total = self._evolution_data.get("migrations_total", 1)
        migration_rate = migrations_success / migrations_total if migrations_total > 0 else 1.0
        
        # Calculate upgrade success rate
        upgrades_success = self._evolution_data.get("upgrades_success", 0)
        upgrades_total = self._evolution_data.get("upgrades_total", 1)
        upgrade_rate = upgrades_success / upgrades_total if upgrades_total > 0 else 1.0
        
        # Build drift by severity
        drift_by_severity = {
            "low": self._evolution_data.get("drift_low", 0),
            "medium": self._evolution_data.get("drift_medium", 0),
            "high": self._evolution_data.get("drift_high", 0)
        }
        
        return EvolutionMetrics(
            id=f"metrics-{period_start.isoformat()}-{period_end.isoformat()}",
            period_start=period_start,
            period_end=period_end,
            evolution_count_by_type=evolutions_by_type,
            migration_count=migrations_total,
            migration_success_rate=migration_rate,
            upgrade_count=upgrades_total,
            upgrade_success_rate=upgrade_rate,
            deprecation_count=self._evolution_data.get("deprecations_total", 0),
            deprecation_with_replacement=self._evolution_data.get("deprecations_with_replacement", 0),
            drift_detection_count=self._evolution_data.get("drift_total", 0),
            drift_by_severity=drift_by_severity,
            technical_debt_items=self._evolution_data.get("debt_total", 0),
            critical_debt_items=self._evolution_data.get("debt_critical", 0)
        )
    
    def calculate_score(self, metrics: EvolutionMetrics) -> RepositoryEvolutionScore:
        """Calculate repository evolution health score from metrics."""
        # Calculate component scores
        evolution_score = min(1.0, metrics.total_evolution_count / 10 + 0.5) if metrics.total_evolution_count > 0 else 0.5
        
        migration_score = metrics.migration_success_rate
        upgrade_score = metrics.upgrade_success_rate
        compatibility_score = 0.95 if not any(
            s > 0 for s in [metrics.drift_by_severity.get("high", 0)]
        ) else 0.8
        
        # Debt score (inverse of debt ratio)
        debt_items = metrics.technical_debt_items
        critical_ratio = (
            metrics.critical_debt_items / debt_items 
            if debt_items > 0 else 0
        )
        debt_score = max(0.0, 1.0 - critical_ratio * 2)
        
        # Drift score (based on severity distribution)
        drift_high = metrics.drift_by_severity.get("high", 0)
        drift_total = metrics.drift_detection_count
        drift_score = (
            max(0.0, 1.0 - drift_high) 
            if drift_total > 0 else 1.0
        )
        
        return RepositoryEvolutionScore(
            id=f"score-{metrics.id}",
            evolution_score=evolution_score,
            migration_score=migration_score,
            upgrade_score=upgrade_score,
            compatibility_score=compatibility_score,
            debt_score=debt_score,
            drift_score=drift_score
        )


# ============================================================================
# UTILITY FUNCTIONS
# ============================================================================

def get_evolution_status(score: RepositoryEvolutionScore) -> Dict[str, Any]:
    """Get detailed status from evolution score."""
    return {
        "composite_score": score.composite_score,
        "status": score.status,
        "evolution_score": score.evolution_score,
        "migration_score": score.migration_score,
        "upgrade_score": score.upgrade_score,
        "compatibility_score": score.compatibility_score,
        "debt_score": score.debt_score,
        "drift_score": score.drift_score
    }


def get_evolution_recommendations(score: RepositoryEvolutionScore) -> List[str]:
    """Get recommendations based on evolution scores."""
    recommendations = []
    
    if score.migration_score < 0.9:
        recommendations.append("Improve migration success rate to >= 90%")
    
    if score.upgrade_score < 0.9:
        recommendations.append("Improve upgrade success rate to >= 90%")
    
    if score.debt_score < 0.8:
        recommendations.append("Reduce technical debt, especially critical items")
    
    if score.drift_score < 0.9:
        recommendations.append("Address architectural drift detection gaps")
    
    return recommendations