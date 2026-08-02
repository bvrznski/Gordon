# Bootstrap Package Metadata
# ===========================

"""
Declarative metadata for the core bootstrap package.
"""

from typing import Dict, Any, List, Optional

META: Dict[str, Any] = {
    "canonical_name": "core.bootstrap",
    "semantic_owner": "Core Team",
    "purpose": (
        "Provides domain-neutral startup preparation infrastructure for Gordon agent. "
        "Implements explicit, deterministic, reversible bootstrap pipeline including "
        "request normalization, configuration acquisition, environment fact collection, "
        "preflight validation, controlled discovery, loading plans, materialization, "
        "initialization orchestration, rollback handling, and handoff preparation."
    ),
    "status": "alpha",
    "maturity": "experimental",
    "version": "1.0.0-alpha.1",
    "dependencies": [
        "core.types",      # EntityId, RuntimeId, Timestamp
        "core.contracts",  # LifecycleState, LifecycleEntity protocols
    ],
    "documentation_reference": (
        "docs/agent/architecture/phase-3.3-bootstrap-preflight-loading-report.md"
    ),
    "excluded_concepts": [
        "cognitive semantics",
        "domain-specific policy decisions",
        "runtime activation (handled by kernel)",
        "network coordination",
        "global service location",
    ],
}

__all__ = ["META"]