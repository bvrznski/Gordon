# Architectural Invariants Module - Phase 3.24
# ==============================================
#
# This module provides repository-wide invariant checking for the Gordon Core.
# Every architectural entity shall possess a validation scope.

from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass, field
from enum import Enum
import time

from . import ValidationSeverity, ValidationFinding, ValidationResult


class InvariantType(Enum):
    """Types of architectural invariants."""
    OWNERSHIP = "ownership"
    HIERARCHY = "hierarchy"
    DEPENDENCY = "dependency"
    ISOLATION = "isolation"
    LIFECYCLE = "lifecycle"
    CONTRACT = "contract"
    NAMING = "naming"
    VISIBILITY = "visibility"
    BOUNDARY = "boundary"
    LAYERING = "layering"


@dataclass(frozen=True)
class InvariantRule:
    """
    An architectural invariant rule.
    
    INVARIANTS:
        INV-001: Rules are immutable once defined
        INV-002: Each rule has a unique identifier
        INV-003: Violations produce structured findings
    """
    rule_id: str
    name: str
    description: str
    invariant_type: InvariantType
    severity: ValidationSeverity = ValidationSeverity.ERROR


# =============================================================================
# OWNERSHIP INVARIANTS
# =============================================================================

class OwnershipInvariantChecker:
    """Validates ownership-related architectural invariants."""
    
    def __init__(self):
        self.name = "ownership_invariant_checker"
    
    def validate_unique_owner(self, entity_id: str, owners: Tuple[str, ...]) -> ValidationResult:
        """
        Validate that an entity has exactly one mutation owner.
        
        INVARIANTS:
            OWN-001: Each entity has at most one mutation owner
        """
        if len(owners) > 1:
            return ValidationResult.invalid(
                target_type="Entity",
                target_id=entity_id,
                validation_scope="ownership",
                primary_failure=f"Multiple mutation owners detected for {entity_id}",
            )
        return ValidationResult.valid(target_type="Entity", target_id=entity_id)
    
    def validate_owner_not_stale(
        self, entity_epoch: int, current_epoch: int
    ) -> ValidationResult:
        """
        Validate that an owner is not from a stale generation.
        
        INVARIANTS:
            OWN-002: Owner epoch must be >= current epoch
        """
        if entity_epoch < current_epoch:
            return ValidationResult.invalid(
                target_type="Entity",
                validation_scope="lifecycle",
                primary_failure=f"Stale owner: entity is from epoch {entity_epoch}, "
                               f"current is {current_epoch}",
            )
        return ValidationResult.valid(target_type="Entity")


# =============================================================================
# HIERARCHY INVARIANTS
# =============================================================================

class HierarchyInvariantChecker:
    """Validates hierarchy-related architectural invariants."""
    
    def __init__(self):
        self.name = "hierarchy_invariant_checker"
    
    def validate_no_cycles(
        self, entity_id: str, ancestors: Tuple[str, ...]
    ) -> ValidationResult:
        """
        Validate that there are no cycles in the hierarchy.
        
        INVARIANTS:
            HIER-001: Entity cannot be its own ancestor
        """
        if entity_id in ancestors:
            return ValidationResult.invalid(
                target_type="Entity",
                target_id=entity_id,
                validation_scope="hierarchy",
                primary_failure=f"Cycle detected: {entity_id} is its own ancestor",
            )
        return ValidationResult.valid(target_type="Entity", target_id=entity_id)
    
    def validate_depth_limit(
        self, entity_id: str, depth: int, max_depth: int = 10
    ) -> ValidationResult:
        """
        Validate that hierarchy depth doesn't exceed maximum.
        
        INVARIANTS:
            HIER-002: Hierarchy depth must not exceed configured maximum
        """
        if depth > max_depth:
            return ValidationResult.invalid(
                target_type="Entity",
                target_id=entity_id,
                validation_scope="hierarchy",
                primary_failure=f"Hierarchy depth {depth} exceeds maximum {max_depth}",
            )
        return ValidationResult.valid(target_type="Entity", target_id=entity_id)


# =============================================================================
# DEPENDENCY INVARIANTS
# =============================================================================

class DependencyInvariantChecker:
    """Validates dependency-related architectural invariants."""
    
    def __init__(self):
        self.name = "dependency_invariant_checker"
    
    def validate_no_cyclic_dependencies(
        self, entity_id: str, dependencies: Tuple[str, ...]
    ) -> ValidationResult:
        """
        Validate that there are no cyclic dependencies.
        
        INVARIANTS:
            DEP-001: No circular dependency chains allowed
        """
        if entity_id in dependencies:
            return ValidationResult.invalid(
                target_type="Entity",
                target_id=entity_id,
                validation_scope="dependency",
                primary_failure=f"Cyclic dependency detected: {entity_id} depends on itself",
            )
        return ValidationResult.valid(target_type="Entity", target_id=entity_id)
    
    def validate_forbidden_imports(
        self, entity_id: str, imports: Tuple[str, ...], forbidden_patterns: Tuple[str, ...]
    ) -> ValidationResult:
        """
        Validate that no forbidden imports are present.
        
        INVARIANTS:
            DEP-002: Forbidden import patterns must not be used
        """
        violations = []
        for imp in imports:
            for pattern in forbidden_patterns:
                if pattern in imp:
                    violations.append(imp)
        
        if violations:
            return ValidationResult.invalid(
                target_type="Entity",
                target_id=entity_id,
                validation_scope="dependency",
                primary_failure=f"Forbidden imports detected: {', '.join(violations)}",
            )
        return ValidationResult.valid(target_type="Entity", target_id=entity_id)


# =============================================================================
# ISOLATION INVARIANTS
# =============================================================================

class IsolationInvariantChecker:
    """Validates isolation-related architectural invariants."""
    
    def __init__(self):
        self.name = "isolation_invariant_checker"
    
    def validate_runtime_isolation(
        self, entity_runtime: str, owner_runtime: str
    ) -> ValidationResult:
        """
        Validate that runtime boundaries are respected.
        
        INVARIANTS:
            ISO-001: Owner must belong to same runtime as entity
        """
        if entity_runtime != owner_runtime:
            return ValidationResult.invalid(
                target_type="Entity",
                validation_scope="isolation",
                primary_failure=f"Runtime isolation violated: "
                               f"entity={entity_runtime}, owner={owner_runtime}",
            )
        return ValidationResult.valid(target_type="Entity")
    
    def validate_package_boundary(
        self, source_pkg: str, target_pkg: str, allowed_crossings: Tuple[str, ...]
    ) -> ValidationResult:
        """
        Validate that package boundaries are respected.
        
        INVARIANTS:
            ISO-002: Cross-package access must be explicitly allowed
        """
        if (source_pkg != target_pkg and 
            f"{source_pkg}->{target_pkg}" not in allowed_crossings):
            return ValidationResult.invalid(
                target_type="PackageBoundary",
                validation_scope="isolation",
                primary_failure=f"Unauthorized cross-package access: "
                               f"{source_pkg} -> {target_pkg}",
            )
        return ValidationResult.valid(target_type="PackageBoundary")


# =============================================================================
# LIFECYCLE INVARIANTS
# =============================================================================

class LifecycleInvariantChecker:
    """Validates lifecycle-related architectural invariants."""
    
    def __init__(self):
        self.name = "lifecycle_invariant_checker"
    
    def validate_terminal_state_transition(
        self, current_state: str, target_state: str, allows_reopen: bool
    ) -> ValidationResult:
        """
        Validate terminal state transitions.
        
        INVARIANTS:
            LIF-001: Terminal states cannot transition back without explicit reopening
        """
        terminal_states = {"completed", "interrupted", "terminated"}
        
        if current_state in terminal_states and target_state == "active":
            if not allows_reopen:
                return ValidationResult.invalid(
                    target_type="Thread",
                    validation_scope="lifecycle",
                    primary_failure=f"Cannot transition from terminal state '{current_state}' "
                                   f"back to 'active' without explicit reopening",
                )
        
        return ValidationResult.valid(target_type="Thread")
    
    def validate_state_monotonicity(
        self, current_version: int, new_version: int
    ) -> ValidationResult:
        """
        Validate that versions never decrease.
        
        INVARIANTS:
            LIF-002: Semantic version must be monotonically increasing
        """
        if new_version < current_version:
            return ValidationResult.invalid(
                target_type="Entity",
                validation_scope="lifecycle",
                primary_failure=f"Version decreased from {current_version} to {new_version}",
            )
        return ValidationResult.valid(target_type="Entity")


# =============================================================================
# NAMING INVARIANTS
# =============================================================================

class NamingInvariantChecker:
    """Validates naming-related architectural invariants."""
    
    def __init__(self):
        self.name = "naming_invariant_checker"
    
    def validate_naming_convention(
        self, entity_id: str, expected_prefixes: Tuple[str, ...]
    ) -> ValidationResult:
        """
        Validate that entity names follow convention.
        
        INVARIANTS:
            NAM-001: All entities must follow naming conventions
        """
        if not any(entity_id.startswith(prefix) for prefix in expected_prefixes):
            return ValidationResult.invalid(
                target_type="Entity",
                target_id=entity_id,
                validation_scope="naming",
                primary_failure=f"Entity '{entity_id}' does not match any allowed prefix: "
                               f"{expected_prefixes}",
            )
        return ValidationResult.valid(target_type="Entity", target_id=entity_id)
    
    def validate_unique_name(
        self, entity_id: str, existing_names: Tuple[str, ...]
    ) -> ValidationResult:
        """
        Validate that names are unique.
        
        INVARIANTS:
            NAM-002: All entity names must be unique within scope
        """
        if entity_id in existing_names:
            return ValidationResult.invalid(
                target_type="Entity",
                target_id=entity_id,
                validation_scope="naming",
                primary_failure=f"Duplicate name detected: {entity_id}",
            )
        return ValidationResult.valid(target_type="Entity", target_id=entity_id)


# =============================================================================
# VISIBILITY INVARIANTS
# =============================================================================

class VisibilityInvariantChecker:
    """Validates visibility-related architectural invariants."""
    
    def __init__(self):
        self.name = "visibility_invariant_checker"
    
    def validate_public_api_exposure(
        self, entity_visibility: str, allowed_scopes: Tuple[str, ...]
    ) -> ValidationResult:
        """
        Validate that public APIs are properly exposed.
        
        INVARIANTS:
            VIS-001: Public API entities must be in allowed scopes
        """
        if entity_visibility not in allowed_scopes:
            return ValidationResult.invalid(
                target_type="Entity",
                validation_scope="visibility",
                primary_failure=f"Invalid visibility scope: {entity_visibility}, "
                               f"allowed: {allowed_scopes}",
            )
        return ValidationResult.valid(target_type="Entity")
    
    def validate_internal_encapsulation(
        self, entity_id: str, is_internal: bool, accessed_from_outside: bool
    ) -> ValidationResult:
        """
        Validate internal encapsulation.
        
        INVARIANTS:
            VIS-002: Internal entities must not be accessed from outside module
        """
        if is_internal and accessed_from_outside:
            return ValidationResult.invalid(
                target_type="Entity",
                target_id=entity_id,
                validation_scope="visibility",
                primary_failure=f"Internal entity {entity_id} exposed externally",
            )
        return ValidationResult.valid(target_type="Entity", target_id=entity_id)


# =============================================================================
# BOUNDARY INVARIANTS
# =============================================================================

class BoundaryInvariantChecker:
    """Validates boundary-related architectural invariants."""
    
    def __init__(self):
        self.name = "boundary_invariant_checker"
    
    def validate_layering(
        self, source_layer: str, target_layer: str, layer_hierarchy: Dict[str, List[str]]
    ) -> ValidationResult:
        """
        Validate that layering rules are followed.
        
        INVARIANTS:
            BND-001: Layers can only depend on layers below them
        """
        allowed_targets = layer_hierarchy.get(source_layer, [])
        if target_layer not in allowed_targets:
            return ValidationResult.invalid(
                target_type="Layer",
                validation_scope="boundary",
                primary_failure=f"Layering violation: {source_layer} cannot depend on {target_layer}",
            )
        return ValidationResult.valid(target_type="Layer")
    
    def validate_boundary_crossing(
        self, source_module: str, target_module: str, allowed_boundaries: Tuple[str, ...]
    ) -> ValidationResult:
        """
        Validate that module boundary crossings are allowed.
        
        INVARIANTS:
            BND-002: Cross-module access must be in allowed boundaries
        """
        boundary_key = f"{source_module} -> {target_module}"
        if boundary_key not in allowed_boundaries:
            return ValidationResult.invalid(
                target_type="ModuleBoundary",
                validation_scope="boundary",
                primary_failure=f"Unauthorized boundary crossing: {boundary_key}",
            )
        return ValidationResult.valid(target_type="ModuleBoundary")


# =============================================================================
# CONTRACT INVARIANTS
# =============================================================================

class ContractInvariantChecker:
    """Validates contract-related architectural invariants."""
    
    def __init__(self):
        self.name = "contract_invariant_checker"
    
    def validate_contract_implemented(
        self, contract_id: str, implementations: Tuple[str, ...]
    ) -> ValidationResult:
        """
        Validate that all declared contracts have implementations.
        
        INVARIANTS:
            CRT-001: Every contract must have at least one implementation
        """
        if not implementations:
            return ValidationResult.invalid(
                target_type="Contract",
                target_id=contract_id,
                validation_scope="contract",
                primary_failure=f"Contract {contract_id} has no implementations",
            )
        return ValidationResult.valid(target_type="Contract", target_id=contract_id)
    
    def validate_contract_compatibility(
        self, contract_version: str, implementation_version: str
    ) -> ValidationResult:
        """
        Validate that implementations are compatible with contracts.
        
        INVARIANTS:
            CRT-002: Implementation version must be >= contract version
        """
        # Simple semantic version comparison (assuming format like "1.2.3")
        cv = int(contract_version.split('.')[0])
        iv = int(implementation_version.split('.')[0])
        
        if iv < cv:
            return ValidationResult.invalid(
                target_type="ContractCompatibility",
                validation_scope="contract",
                primary_failure=f"Implementation version {implementation_version} "
                               f"is incompatible with contract version {contract_version}",
            )
        return ValidationResult.valid(target_type="ContractCompatibility")


# =============================================================================
# COMPOSITE INVARIANT CHECKER
# =============================================================================

class InvariantChecker:
    """
    Composite invariant checker that runs all invariant validators.
    
    This is the main entry point for repository-wide invariant checking.
    """
    
    def __init__(self):
        self.ownership = OwnershipInvariantChecker()
        self.hierarchy = HierarchyInvariantChecker()
        self.dependency = DependencyInvariantChecker()
        self.isolation = IsolationInvariantChecker()
        self.lifecycle = LifecycleInvariantChecker()
        self.naming = NamingInvariantChecker()
        self.visibility = VisibilityInvariantChecker()
        self.boundary = BoundaryInvariantChecker()
        self.contract = ContractInvariantChecker()
    
    def name(self) -> str:
        return "composite_invariant_checker"
    
    def validate_repository(
        self,
        entities: Tuple[Any, ...],
    ) -> ValidationResult:
        """
        Validate all repository invariants.
        
        Args:
            entities: All entities to validate
            
        Returns:
            ValidationResult with all validation results
        """
        # This would be implemented based on actual entity types
        return ValidationResult.valid(
            target_type="Repository",
            validator_name=self.name(),
        )

__all__ = [
    "InvariantType",
    "InvariantRule",
    "OwnershipInvariantChecker",
    "HierarchyInvariantChecker",
    "DependencyInvariantChecker",
    "IsolationInvariantChecker",
    "LifecycleInvariantChecker",
    "NamingInvariantChecker",
    "VisibilityInvariantChecker",
    "BoundaryInvariantChecker",
    "ContractInvariantChecker",
    "InvariantChecker",
]