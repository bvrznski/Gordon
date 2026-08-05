"""Core agent component descriptor.

Phase 3.7.31: Agent Component Loading Architecture
===================================================

Declarative load metadata for core components.
Exported as LOAD per canonical __load__.py convention.
"""

from __future__ import annotations

# Core Agent component - foundational authority
LOAD = {
    # Identity fields (required)
    "component_id": "core-agent",
    "component_kind": "core_authority",
    "package_id": "src.agent.components.core",
    "implementation_path": "src.agent.components.core.kernel.builder:CoreBuilder",
    
    # Phase and ordering
    "load_phase": "foundation",
    "priority": 1000,
    
    # Versioning
    "schema_version": "1.0.0",
    
    # Lifecycle policy
    "required": True,
    "eager": True,
    
    # Runtime configuration
    "runtime_scope": "runtime",
    "lifecycle_scope": "agent",
}

# This file is declarative - no side effects at import time