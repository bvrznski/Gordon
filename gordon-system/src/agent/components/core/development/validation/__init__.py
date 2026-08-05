# Validation Pipeline Infrastructure
# ==================================
"""
Validation pipeline infrastructure for Gordon development tooling.

This module provides canonical abstractions for:
- Syntax validation
- Type validation  
- Architecture validation
- Dependency validation
- Contract validation

ARCHITECTURAL PRINCIPLES:
- Generated artifacts are reproducible
- Validation precedes integration
- Migrations are reversible where practical
- Refactoring preserves observable behavior
- Maintenance workflows are idempotent
- Architecture validation is mandatory
- Generated code is traceable
"""
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from core.development.validation import pipeline, checks, schemas

__all__ = [
    "pipeline",
    "checks", 
    "schemas",
]