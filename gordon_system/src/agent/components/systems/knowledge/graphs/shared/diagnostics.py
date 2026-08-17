"""Graph Diagnostics - Phase 6.8 Part 2 Section 25.

Diagnostics remain descriptive and observational.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Tuple, Optional, Any
import time
import uuid


@dataclass(frozen=True)
class GraphDiagnostic:
    """A single diagnostic finding for a Knowledge Graph."""

    diagnostic_identity: str
    severity: str = "info"
    category: str = "general"
    message: str = ""
    graph: Dict[str, Any] = field(default_factory=dict)
    provenance: Tuple[Dict[str, Any], ...] = field(default_factory=tuple)
    created_at_utc: float = field(default_factory=time.time)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "diagnostic_identity": self.diagnostic_identity,
            "severity": self.severity,
            "category": self.category,
            "message": self.message,
            "graph": dict(self.graph),
            "provenance": [p for p in self.provenance],
            "created_at_utc": self.created_at_utc,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "GraphDiagnostic":
        return cls(
            diagnostic_identity=data.get("diagnostic_identity", str(uuid.uuid4())),
            severity=data.get("severity", "info"),
            category=data.get("category", "general"),
            message=data.get("message", ""),
            graph=dict(data.get("graph", {})),
            provenance=tuple(data.get("provenance", [])),
            created_at_utc=float(data.get("created_at_utc", time.time())),
        )


@dataclass(frozen=True)
class GraphDiagnosticsReport:
    """Aggregate diagnostics report for Knowledge Graphs."""

    report_identity: str
    evaluated_graphs: Tuple[Dict[str, Any], ...] = field(default_factory=tuple)
    diagnostics: Tuple[GraphDiagnostic, ...] = field(default_factory=tuple)
    info_count: int = 0
    warning_count: int = 0
    error_count: int = 0
    overall_status: str = "healthy"
    provenance: Tuple[Dict[str, Any], ...] = field(default_factory=tuple)
    created_at_utc: float = field(default_factory=time.time)

    @property
    def is_healthy(self) -> bool:
        return self.error_count == 0

    @classmethod
    def create_initial(cls, graph_refs: Optional[List[Dict[str, Any]]] = None) -> "GraphDiagnosticsReport":
        report_id = f"diag_report:{uuid.uuid4().hex[:16]}"
        initial_provenance = (
            {
                "provenance_identity": f"provenance:{uuid.uuid4().hex[:16]}",
                "originating_request": "Diagnostics report initialization",
                "originating_system": "knowledge-graph-system",
                "originating_revision": 1,
                "evidence_references": [],
                "grounding_references": [],
                "revision_chain": [report_id],
                "authority": "system",
                "timestamp_utc": time.time(),
            },
        )
        return cls(
            report_identity=report_id,
            evaluated_graphs=tuple(graph_refs or []),
            provenance=initial_provenance,
            created_at_utc=time.time(),
        )

    def add_diagnostic(self, diagnostic: GraphDiagnostic) -> "GraphDiagnosticsReport":
        info = self.info_count + (1 if diagnostic.severity == "info" else 0)
        warning = self.warning_count + (1 if diagnostic.severity == "warning" else 0)
        error = self.error_count + (1 if diagnostic.severity == "error" else 0)
        overall = "healthy" if error == 0 else "unhealthy"
        return GraphDiagnosticsReport(
            report_identity=self.report_identity,
            evaluated_graphs=self.evaluated_graphs,
            diagnostics=tuple(self.diagnostics + (diagnostic,)),
            info_count=info,
            warning_count=warning,
            error_count=error,
            overall_status=overall,
            provenance=self._append_provenance(f"Added diagnostic: {diagnostic.category}"),
            created_at_utc=self.created_at_utc,
        )

    def _append_provenance(self, request: str) -> Tuple[Dict[str, Any], ...]:
        last_chain = list(self.provenance[-1].get("revision_chain", [])) if self.provenance else []
        return tuple(self.provenance) + (
            {
                "provenance_identity": f"provenance:{uuid.uuid4().hex[:16]}",
                "originating_request": request,
                "originating_system": "knowledge-graph-system",
                "originating_revision": 1,
                "evidence_references": [],
                "grounding_references": [],
                "revision_chain": last_chain + [self.report_identity],
                "authority": "system",
                "timestamp_utc": time.time(),
            },
        )

    def to_dict(self) -> Dict[str, Any]:
        return {
            "report_identity": self.report_identity,
            "evaluated_graphs": [dict(g) for g in self.evaluated_graphs],
            "diagnostics": [d.to_dict() for d in self.diagnostics],
            "info_count": self.info_count,
            "warning_count": self.warning_count,
            "error_count": self.error_count,
            "overall_status": self.overall_status,
            "provenance": [p for p in self.provenance],
            "created_at_utc": self.created_at_utc,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "GraphDiagnosticsReport":
        diagnostics = []
        for d_data in data.get("diagnostics", []):
            if isinstance(d_data, dict):
                diagnostics.append(GraphDiagnostic.from_dict(d_data))
        return cls(
            report_identity=data.get("report_identity", str(uuid.uuid4())),
            evaluated_graphs=tuple(data.get("evaluated_graphs", [])),
            diagnostics=tuple(diagnostics),
            info_count=int(data.get("info_count", 0)),
            warning_count=int(data.get("warning_count", 0)),
            error_count=int(data.get("error_count", 0)),
            overall_status=data.get("overall_status", "healthy"),
            provenance=tuple(data.get("provenance", [])),
            created_at_utc=float(data.get("created_at_utc", time.time())),
        )


__all__ = ["GraphDiagnostic", "GraphDiagnosticsReport"]
