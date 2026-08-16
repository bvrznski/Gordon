# Audit Configuration - Gordon Executive Network Audit Subsystem
# ================================================================

"""
Configuration for the Executive Audit subsystem.
"""

from dataclasses import dataclass, field
from typing import Optional
import time


@dataclass(frozen=True)
class AuditConfig:
    """
    Configuration for the Executive Audit subsystem.
    
    All values are immutable and established at instantiation. Changes require
    creating a new instance with updated values.
    """
    
    # Session bounds
    max_findings_per_session: int = 100
    """Maximum findings per audit session."""
    
    max_recommendations_per_session: int = 50
    """Maximum recommendations per audit session."""
    
    max_evidence_per_session: int = 1000
    """Maximum evidence items per audit session."""
    
    # Time bounds
    default_timeout_seconds: float = 30.0
    """Default timeout for audit sessions."""
    
    min_audit_interval_seconds: float = 1.0
    """Minimum interval between automated audits."""
    
    max_audit_interval_seconds: float = 3600.0
    """Maximum interval between automated audits."""
    
    # History bounds
    max_reports_per_history: int = 1000
    """Maximum reports to retain in history."""
    
    max_findings_per_history: int = 10000
    """Maximum findings to retain in history."""
    
    max_recommendations_per_history: int = 5000
    """Maximum recommendations to retain in history."""
    
    # Severity thresholds
    critical_severity_threshold: float = 0.95
    """Threshold for critical severity findings (0-1)."""
    
    high_severity_threshold: float = 0.80
    """Threshold for high severity findings (0-1)."""
    
    medium_severity_threshold: float = 0.60
    """Threshold for medium severity findings (0-1)."""
    
    low_severity_threshold: float = 0.40
    """Threshold for low severity findings (0-1)."""
    
    # Risk level thresholds
    high_risk_score_threshold: int = 80
    """Score threshold for high risk."""
    
    medium_risk_score_threshold: int = 50
    """Score threshold for medium risk."""
    
    # Degradation
    enable_degraded_mode: bool = True
    """Whether to continue in degraded mode when components unavailable."""
    
    max_consecutive_failures: int = 10
    """Maximum consecutive failures before declaring subsystem unhealthy."""
    
    # Evidence collection
    collect_execution_trace: bool = True
    """Whether to collect execution traces for evidence."""
    
    collect_state_snapshots: bool = True
    """Whether to collect state snapshots for evidence."""
    
    collect_context_projections: bool = True
    """Whether to collect context projections for evidence."""
    
    # Reporting
    include_evidence_in_report: bool = False
    """Whether to include full evidence in reports (can be large)."""
    
    max_report_size_bytes: int = 1_000_000
    """Maximum size of report before truncation."""
    
    @classmethod
    def default(cls) -> "AuditConfig":
        """
        Create a default audit configuration.
        
        Returns:
            AuditConfig with sensible defaults for production use.
        """
        return cls()
    
    @classmethod
    def strict(cls) -> "AuditConfig":
        """
        Create a strict audit configuration for security-sensitive deployments.
        
        Returns:
            AuditConfig with stricter bounds and higher thresholds.
        """
        return cls(
            max_findings_per_session=200,
            max_recommendations_per_session=100,
            critical_severity_threshold=0.95,
            high_severity_threshold=0.85,
            medium_severity_threshold=0.70,
            low_severity_threshold=0.50,
        )
    
    @classmethod
    def permissive(cls) -> "AuditConfig":
        """
        Create a permissive audit configuration for development/testing.
        
        Returns:
            AuditConfig with relaxed bounds and lower thresholds.
        """
        return cls(
            max_findings_per_session=1000,
            max_recommendations_per_session=500,
            max_evidence_per_session=10_000,
            critical_severity_threshold=0.85,
            high_severity_threshold=0.70,
            medium_severity_threshold=0.50,
            low_severity_threshold=0.30,
        )
    
    @property
    def is_strict(self) -> bool:
        """Check if config uses strict thresholds."""
        return (
            self.critical_severity_threshold >= 0.90 and
            self.max_findings_per_session <= 200
        )
    
    def get_severity_level(self, score: float) -> str:
        """
        Determine the severity level for a given score.
        
        Args:
            score: Severity score from 0.0 to 1.0
            
        Returns:
            Severity level string: 'critical', 'high', 'medium', 'low', or 'info'
        """
        if score >= self.critical_severity_threshold:
            return "critical"
        elif score >= self.high_severity_threshold:
            return "high"
        elif score >= self.medium_severity_threshold:
            return "medium"
        elif score >= self.low_severity_threshold:
            return "low"
        return "info"
    
    def get_risk_level(self, score: int) -> str:
        """
        Determine the risk level for a given score.
        
        Args:
            score: Risk score from 0 to 100
            
        Returns:
            Risk level string: 'high', 'medium', 'low', or 'negligible'
        """
        if score >= self.high_risk_score_threshold:
            return "high"
        elif score >= self.medium_risk_score_threshold:
            return "medium"
        elif score > 0:
            return "low"
        return "negligible"


def create_audit_config(**kwargs) -> AuditConfig:
    """
    Create an audit configuration with optional overrides.
    
    Args:
        **kwargs: Configuration values to override
        
    Returns:
        New AuditConfig instance with overridden values
    """
    default = AuditConfig.default()
    return dataclass_replace(default, **kwargs)


def dataclass_replace(dataclass_instance, **kwargs):
    """Simple dataclass replace without requiring dataclasses.replace."""
    import dataclasses
    
    fields = dataclasses.fields(dataclass_instance)
    new_values = {}
    
    for field in fields:
        if field.name in kwargs:
            new_values[field.name] = kwargs[field.name]
        else:
            new_values[field.name] = getattr(dataclass_instance, field.name)
    
    return type(dataclass_instance)(**new_values)