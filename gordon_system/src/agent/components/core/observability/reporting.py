# Core Reporting Framework
# =========================

"""
Reporting framework for observability data.

This module provides:
- Scheduled reports and on-demand reports
- Report templates and formatting
- Dashboard generation
- Data export capabilities
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Dict, List, Any, Optional, Callable
from enum import Enum, auto
import time
import uuid
import json


# =============================================================================
# REPORT TYPES
# =============================================================================

class ReportType(Enum):
    """Types of reports."""
    
    # Operational reports
    OPERATIONAL = "operational"         # Current system status
    HEALTH_SUMMARY = "health_summary"   # Health status overview
    
    # Performance reports
    PERFORMANCE = "performance"         # Performance metrics summary
    LATENCY_DISTRIBUTION = "latency_distribution"
    THROUGHPUT_ANALYSIS = "throughput_analysis"
    
    # Analytics reports
    TREND_ANALYSIS = "trend_analysis"   # Trends over time
    ANOMALY_REPORT = "anomaly_report"   # Detected anomalies
    
    # System reports
    RESOURCE_USAGE = "resource_usage"   # Resource consumption
    ERROR_SUMMARY = "error_summary"     # Error statistics
    TRACE_SUMMARY = "trace_summary"     # Distributed trace analysis


@dataclass(frozen=True)
class ReportSchedule:
    """Configuration for scheduled report generation."""
    
    schedule_id: str = field(default_factory=lambda: f"sched_{uuid.uuid4().hex[:8]}")
    
    report_type: ReportType
    name: str
    
    # Schedule configuration
    interval_seconds: float = 3600.0  # Default hourly
    next_run_utc: Optional[float] = None
    enabled: bool = True


# =============================================================================
# REPORT DEFINITION
# =============================================================================

@dataclass(frozen=True)
class ReportDefinition:
    """
    Definition for a report type.
    
    Specifies what data to collect and how to format it.
    """
    
    definition_id: str
    name: str
    description: str
    
    # Report characteristics
    report_type: ReportType
    frequency_seconds: float  # How often this report should be generated
    
    # Data sources
    required_metrics: List[str]      # Metrics needed for this report
    optional_metrics: List[str] = field(default_factory=list)
    
    # Format configuration
    format: str = "structured"        # "structured", "markdown", "json"
    include_timestamps: bool = True
    
    # Aggregation window
    aggregation_window_seconds: float = 300.0  # Default 5 minutes


# =============================================================================
# REPORT OUTPUT
# =============================================================================

class ReportOutputFormat(Enum):
    """Supported output formats."""
    
    JSON = "json"              # Machine-readable JSON
    MARKDOWN = "markdown"      # Human-readable markdown
    HTML = "html"              # HTML for web dashboards
    TEXT = "text"              # Plain text for console


@dataclass(frozen=True)
class ReportOutput:
    """
    Output of a report generation.
    
    Contains the report data in multiple formats.
    """
    
    output_id: str = field(default_factory=lambda: f"output_{uuid.uuid4().hex[:8]}")
    
    report_type: ReportType
    generated_at_utc: float
    
    # Data content
    data: Dict[str, Any]            # Structured data
    summary: str                    # Human-readable summary
    
    # Format variants
    json_output: Optional[str] = None
    markdown_output: Optional[str] = None
    html_output: Optional[str] = None


# =============================================================================
# REPORT GENERATOR
# =============================================================================

class ReportGenerator(ABC):
    """Abstract base class for report generators."""
    
    @abstractmethod
    def generate(
        self,
        data: Dict[str, Any],
        options: Optional[Dict[str, Any]] = None
    ) -> ReportOutput:
        """
        Generate a report from the provided data.
        
        Args:
            data: The telemetry/data to include in the report
            options: Optional formatting/config options
            
        Returns:
            Generated report output
        """
        ...
    
    @abstractmethod
    def get_supported_formats(self) -> List[ReportOutputFormat]:
        """Get list of supported output formats."""
        ...


# =============================================================================
# STRUCTURED REPORT GENERATOR
# =============================================================================

class StructuredReportGenerator(ReportGenerator):
    """Generates structured JSON reports from telemetry data."""
    
    def __init__(
        self,
        runtime_id: str,
        include_metadata: bool = True,
        max_summary_lines: int = 100,
    ) -> None:
        self.runtime_id = runtime_id
        self._include_metadata = include_metadata
        self._max_summary_lines = max_summary_lines
    
    def generate(
        self,
        data: Dict[str, Any],
        options: Optional[Dict[str, Any]] = None
    ) -> ReportOutput:
        """Generate a structured report."""
        options = options or {}
        
        # Build report metadata
        report_id = f"report_{uuid.uuid4().hex[:12]}"
        now_utc = time.time()
        
        # Extract summary info from data
        summary_parts = self._build_summary(data, options)
        summary_text = "\n".join(summary_parts[:self._max_summary_lines])
        
        # Build structured output
        report_data = {
            "report_id": report_id,
            "runtime_id": self.runtime_id,
            "generated_at_utc": now_utc,
            "report_type": options.get("report_type", ReportType.OPERATIONAL.value),
            "data": data,
            "metadata": {},
        }
        
        if self._include_metadata:
            report_data["metadata"] = {
                "generated_by": "StructuredReportGenerator",
                "format_version": "1.0.0",
            }
        
        # Format outputs
        json_str = json.dumps(report_data, default=str)
        markdown_str = self._to_markdown(report_data)
        html_str = self._to_html(report_data)
        
        return ReportOutput(
            output_id=report_id,
            report_type=options.get("report_type", ReportType.OPERATIONAL),
            generated_at_utc=now_utc,
            data=data,
            summary=summary_text,
            json_output=json_str,
            markdown_output=markdown_str,
            html_output=html_str,
        )
    
    def _build_summary(self, data: Dict[str, Any], options: Dict[str, Any]) -> List[str]:
        """Build human-readable summary from data."""
        lines = []
        
        if "metrics" in data:
            metrics = data["metrics"]
            for name, values in metrics.items():
                count = values.get("count", 0)
                avg = values.get("avg", 0)
                min_v = values.get("min", 0)
                max_v = values.get("max", 0)
                
                if isinstance(avg, (int, float)):
                    lines.append(f"{name}: avg={avg:.2f}, min={min_v:.2f}, max={max_v:.2f}, count={count}")
        
        if "kpis" in data:
            for kpi_id, kpi_data in data["kpis"].items():
                status = kpi_data.get("status", "unknown")
                value = kpi_data.get("value", 0)
                lines.append(f"{kpi_id}: {status} (value={value})")
        
        if "health_score" in data:
            score = data.get("health_score", 1.0)
            status = data.get("status", "unknown")
            lines.append(f"Health: {status} ({score:.1%})")
        
        return lines
    
    def _to_markdown(self, data: Dict[str, Any]) -> str:
        """Convert report to markdown format."""
        parts = []
        
        # Header
        parts.append(f"# {data.get('report_type', 'Report')}")
        parts.append("")
        parts.append(f"**Report ID:** {data.get('report_id', 'N/A')}")
        parts.append(f"**Generated:** {time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(data.get('generated_at_utc', 0)))}")
        parts.append("")
        
        # Data sections
        if "metrics" in data:
            parts.append("## Metrics")
            parts.append("")
            
            for name, values in data["metrics"].items():
                parts.append(f"### {name}")
                parts.append("")
                
                if isinstance(values, dict):
                    for key, value in values.items():
                        parts.append(f"- **{key}:** {value}")
                else:
                    parts.append(f"- **Value:** {values}")
                
                parts.append("")
        
        if "health_score" in data:
            score = data.get("health_score", 0)
            status = data.get("status", "unknown")
            
            parts.append("## Health Status")
            parts.append("")
            parts.append(f"- **Score:** {score:.1%}")
            parts.append(f"- **Status:** {status.upper()}")
            parts.append("")
        
        return "\n".join(parts)
    
    def _to_html(self, data: Dict[str, Any]) -> str:
        """Convert report to HTML format."""
        parts = []
        
        parts.append("<!DOCTYPE html>")
        parts.append("<html><head><title>Report</title></head><body>")
        
        # Header
        report_type = data.get("report_type", "Report")
        report_id = data.get("report_id", "N/A")
        generated_at = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(data.get('generated_at_utc', 0)))
        
        parts.append(f"<h1>{report_type}</h1>")
        parts.append(f"<p><strong>Report ID:</strong> {report_id} | <strong>Generated:</strong> {generated_at}</p>")
        parts.append("")
        
        # Data sections
        if "metrics" in data:
            parts.append("<section><h2>Metrics</h2><table>")
            
            for name, values in data["metrics"].items():
                parts.append(f"<tr><td>{name}</td><td>")
                
                if isinstance(values, dict):
                    for key, value in values.items():
                        parts.append(f"<strong>{key}:</strong> {value}<br/>")
                else:
                    parts.append(str(value))
                
                parts.append("</td></tr>")
            
            parts.append("</table></section>")
        
        if "health_score" in data:
            score = data.get("health_score", 0)
            status = data.get("status", "unknown")
            
            color = "#4CAF50" if score >= 0.9 else ("#FFC107" if score >= 0.8 else "#F44336")
            
            parts.append("<section><h2>Health Status</h2>")
            parts.append(f"<p style='font-size: 2em; color: {color};'>Score: {score:.1%}</p>")
            parts.append(f"<p>Status: <strong>{status.upper()}</strong></p>")
            parts.append("</section>")
        
        parts.append("</body></html>")
        
        return "\n".join(parts)
    
    def get_supported_formats(self) -> List[str]:
        """Get list of supported formats."""
        return [ReportOutputFormat.JSON.value, ReportOutputFormat.MARKDOWN.value, ReportOutputFormat.HTML.value]


# =============================================================================
# REPORT SCHEDULER
# =============================================================================

class ReportScheduler:
    """
    Scheduler for report generation.
    
    Manages scheduled reports and can generate on-demand reports.
    """
    
    def __init__(
        self,
        runtime_id: str,
        generator: Optional[ReportGenerator] = None,
    ) -> None:
        self.runtime_id = runtime_id
        self._generator = generator or StructuredReportGenerator(runtime_id)
        
        # Scheduled reports
        self._schedules: Dict[str, ReportSchedule] = {}
        
        # Last generation time by schedule
        self._last_run_utc: Dict[str, float] = {}
    
    def add_schedule(self, schedule: ReportSchedule) -> "ReportScheduler":
        """Add a scheduled report."""
        self._schedules[schedule.schedule_id] = schedule
        
        if schedule.next_run_utc is None:
            # Set next run to now + interval
            schedule.next_run_utc = time.time() + schedule.interval_seconds
        
        return self
    
    def remove_schedule(self, schedule_id: str) -> "ReportScheduler":
        """Remove a scheduled report."""
        self._schedules.pop(schedule_id, None)
        self._last_run_utc.pop(schedule_id, None)
        
        return self
    
    def should_generate(self, schedule_id: str) -> bool:
        """
        Check if a scheduled report should be generated now.
        
        Args:
            schedule_id: ID of the scheduled report
            
        Returns:
            True if it's time to generate
        """
        schedule = self._schedules.get(schedule_id)
        if not schedule or not schedule.enabled:
            return False
        
        next_run = schedule.next_run_utc or 0
        return time.time() >= next_run
    
    def get_next_run(self, schedule_id: str) -> Optional[float]:
        """Get the next scheduled run time."""
        schedule = self._schedules.get(schedule_id)
        if schedule:
            return schedule.next_run_utc
        return None
    
    def generate_scheduled_reports(
        self,
        data: Dict[str, Any],
        options: Optional[Dict[str, Any]] = None
    ) -> List[ReportOutput]:
        """Generate all reports that are due."""
        outputs = []
        
        for schedule_id, schedule in self._schedules.items():
            if self.should_generate(schedule_id) and schedule.enabled:
                output = self._generator.generate(data, {
                    **(options or {}),
                    "report_type": schedule.report_type,
                })
                
                # Update last run time
                self._last_run_utc[schedule_id] = time.time()
                
                # Set next run
                schedule.next_run_utc = time.time() + schedule.interval_seconds
                
                outputs.append(output)
        
        return outputs
    
    def generate_on_demand(
        self,
        report_type: ReportType,
        data: Dict[str, Any],
        options: Optional[Dict[str, Any]] = None
    ) -> ReportOutput:
        """Generate a report on demand."""
        options = options or {}
        options["report_type"] = report_type
        
        return self._generator.generate(data, options)


# =============================================================================
# DASHBOARD CONFIGURATION
# =============================================================================

class DashboardType(Enum):
    """Types of dashboards."""
    
    OPERATIONAL = "operational"       # System health overview
    PERFORMANCE = "performance"       # Performance metrics
    RESOURCE = "resource"             # Resource utilization
    ERROR_ANALYSIS = "error_analysis" # Error tracking and analysis
    CUSTOM = "custom"                 # Custom dashboard


@dataclass(frozen=True)
class DashboardDefinition:
    """
    Definition for a dashboard layout.
    
    Specifies widgets, their positions, and what data they display.
    """
    
    definition_id: str
    name: str
    
    dashboard_type: DashboardType
    
    # Layout configuration (grid-based)
    grid_width: int = 12        # Total columns in grid
    rows: int = 6               # Total rows in grid
    
    # Widgets in this dashboard
    widgets: List[Dict[str, Any]] = field(default_factory=list)  # Widget definitions


@dataclass(frozen=True)
class DashboardWidget:
    """
    A widget that displays data in a dashboard.
    
    Defines the layout and data source for one display element.
    """
    
    widget_id: str
    title: str
    
    position: Dict[str, int]   # x, y, width, height in grid
    data_source: str           # Data field this widget displays
    widget_type: str = "metric"  # metric, chart, gauge, table


# =============================================================================
# DASHBOARD GENERATOR
# =============================================================================

class DashboardGenerator:
    """
    Generator for dashboard layouts from telemetry data.
    
    Creates dashboard configurations and renders them to output formats.
    """
    
    def __init__(
        self,
        runtime_id: str,
    ) -> None:
        self.runtime_id = runtime_id
    
    def generate_dashboard(
        self,
        definition: DashboardDefinition,
        data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Generate a dashboard from its definition and current data.
        
        Args:
            definition: The dashboard definition
            data: Current telemetry data
            
        Returns:
            Dashboard configuration with rendered content
        """
        widgets = []
        
        for widget_def in definition.widgets:
            widget_data = self._get_widget_data(widget_def, data)
            
            widgets.append({
                "widget_id": widget_def.widget_id,
                "title": widget_def.title,
                "position": widget_def.position,
                "data_source": widget_def.data_source,
                "value": widget_data.get("value"),
                "unit": widget_data.get("unit"),
                "timestamp_utc": time.time(),
            })
        
        return {
            "dashboard_id": f"dash_{uuid.uuid4().hex[:12]}",
            "definition_id": definition.definition_id,
            "name": definition.name,
            "runtime_id": self.runtime_id,
            "generated_at_utc": time.time(),
            "grid_width": definition.grid_width,
            "rows": definition.rows,
            "widgets": widgets,
        }
    
    def _get_widget_data(
        self,
        widget_def: DashboardWidget,
        data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Get the data value for a widget."""
        # Navigate to the data field
        parts = widget_def.data_source.split(".")
        
        current = data
        for part in parts:
            if isinstance(current, dict):
                current = current.get(part)
            else:
                return {"value": None}
        
        return {
            "value": current,
            "unit": self._infer_unit(widget_def.widget_type),
        }
    
    def _infer_unit(self, widget_type: str) -> str:
        """Infer the unit based on widget type."""
        units = {
            "metric": "",
            "gauge": "%",
            "chart": "",
            "table": "",
        }
        return units.get(widget_type, "")


# =============================================================================
# EXPORT CONFIGURATION
# =============================================================================

class ExportFormat(Enum):
    """Supported export formats."""
    
    JSON = "json"           # JSON format
    CSV = "csv"             # CSV format
    PROMETHEUS = "prometheus"  # Prometheus text format
    OPENTELEMETRY = "opentelemetry"  # OpenTelemetry protobuf


@dataclass(frozen=True)
class ExportConfig:
    """Configuration for data export."""
    
    config_id: str = field(default_factory=lambda: f"export_{uuid.uuid4().hex[:8]}")
    
    format: ExportFormat
    destination: str        # URL, file path, or other destination
    
    # Filtering
    metric_filter: Optional[List[str]] = None  # List of metrics to include
    time_range_start_utc: Optional[float] = None
    time_range_end_utc: Optional[float] = None
    
    # Compression
    compression: str = "none"  # none, gzip, zstd


__all__ = [
    # Report types
    "ReportType",
    "ReportSchedule",
    
    # Definitions and output
    "ReportDefinition",
    "ReportOutputFormat",
    "ReportOutput",
    
    # Generators
    "ReportGenerator",
    "StructuredReportGenerator",
    "ReportScheduler",
    
    # Dashboard
    "DashboardType",
    "DashboardDefinition",
    "DashboardWidget",
    "DashboardGenerator",
    
    # Export
    "ExportFormat",
    "ExportConfig",
]