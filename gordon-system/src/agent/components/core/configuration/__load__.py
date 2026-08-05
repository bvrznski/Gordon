"""Configuration component descriptor.

Phase 3.7.31: Agent Component Loading Architecture
===================================================

Declarative load metadata for configuration components.
Exported as LOAD per canonical __load__.py convention.
"""

from __future__ import annotations

# Configuration component - provides configuration resolution
LOAD = {
    # Identity fields (required)
    "component_id": "configuration",
    "component_kind": "infrastructure",
    "package_id": "src.agent.components.core.configuration",
    "implementation_path": "src.agent.components.core.configuration.effective_config:EffectiveConfigResolver",
    
    # Phase and ordering
    "load_phase": "core_contracts",
    "priority": 500,
    
    # Versioning
    "schema_version": "1.0.0",
    
    # Dependencies
    "required_dependencies": ("core-agent",),
    
    # Lifecycle policy
    "required": True,
    "eager": True,
    
    # Runtime configuration
    "runtime_scope": "runtime",
    "lifecycle_scope": "agent",
}

# This file is declarative - no side effects at import time