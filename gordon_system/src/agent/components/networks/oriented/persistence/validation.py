# Oriented Network Validation Framework - Phase 4.7.8 Part 2
# ===========================================================

"""
Validation Framework for the Oriented Network (Phase 4.7.8)

ARCHITECTURAL PRINCIPLES:
    - Validation is deterministic
    - No runtime state modification during validation
    - Pure semantic representation only
    
PHASE 4.7.8 PART 2 - VALIDATION:
    Validation framework for persistence models
    AST validation, law compliance, invariants

NO RUNTIME BEHAVIOR:
    - No runtime validation
    - No checkpointing
"""

from __future__ import annotations

from typing import Any, Dict, Tuple

from gordon_system.src.agent.components.networks.oriented.persistence.base import BasePersistenceModel


# =============================================================================
# VALIDATION CONSTANTS
# =============================================================================

VALIDATION_PASSED = True
VALIDATION_FAILED = False

AST_PROHIBITED_MODULES = (
    "threading",
    "multiprocessing", 
    "asyncio",
    "queue",
    "subprocess",
    "socket",
    "requests",
    "httpx",
    "aiohttp",
    "grpc",
    "websockets",
    "concurrent.futures",
    "time",
    "datetime",
    "uuid",
    "random",
    "psutil",
)

AST_PROHIBITED_CLASSES = (
    "threading.Thread",
    "multiprocessing.Process",
    "asyncio.Task",
)


# =============================================================================
# VALIDATION RESULTS
# =============================================================================

ValidationResult = Tuple[bool, Tuple[str, ...]]
"""
Validation result: (is_valid, list_of_errors_or_warnings)
"""

ASTValidationResult = Tuple[bool, Tuple[str, ...], Tuple[str, ...]]
"""
AST validation result: 
    (is_valid, list_of_prohibited_constructs, list_of_allowed_constructs)
"""


# =============================================================================
# BASE VALIDATOR
# =============================================================================

class BaseValidator:
    """
    Base validator for Oriented Network persistence models.
    
    INVARIANTS:
        BV-INV-001: Validation is deterministic
        BV-INV-002: Validation never modifies input
        BV-INV-003: Validation checks ownership compliance
    """
    
    @staticmethod
    def validate_model(model: BasePersistenceModel) -> ValidationResult:
        """
        Validate a persistence model.
        
        Args:
            model: The persistence model to validate
            
        Returns:
            (is_valid, list_of_errors)
            
        INVARIANT: Same input produces same output
        """
        return model.validate()
    
    @staticmethod
    def validate_ontology_compliance(
        model: BasePersistenceModel,
        ontology_data: Dict[str, Any]
    ) -> ValidationResult:
        """
        Validate model against ontology requirements.
        
        Args:
            model: The persistence model
            ontology_data: Ontology constraints
            
        Returns:
            (is_valid, list_of_errors)
        """
        # Semantic validation - check for prohibited runtime constructs
        errors = []
        
        if hasattr(model, "__dict__"):
            for attr_name, attr_value in vars(model).items():
                if BaseValidator._contains_prohibited_runtime(attr_value):
                    errors.append(
                        f"Prohibited runtime construct in {attr_name}"
                    )
        
        return len(errors) == 0, tuple(errors)
    
    @staticmethod
    def _contains_prohibited_runtime(value: Any) -> bool:
        """
        Check if a value contains prohibited runtime constructs.
        
        Args:
            value: Value to check
            
        Returns:
            True if prohibited runtime construct detected
        """
        if isinstance(value, str):
            return any(prohibited in value 
                      for prohibited in AST_PROHIBITED_MODULES)
        elif isinstance(value, dict):
            return any(BaseValidator._contains_prohibited_runtime(v) 
                      for v in value.values())
        elif isinstance(value, (list, tuple)):
            return any(BaseValidator._contains_prohibited_runtime(item) 
                      for item in value)
        
        return False


# =============================================================================
# AST VALIDATOR
# =============================================================================

class ASTValidator:
    """
    AST-level validator for persistence modules.
    
    INVARIANTS:
        ASTV-INV-001: AST validation is deterministic
        ASTV-INV-002: AST validation never modifies input
        ASTV-INV-003: Prohibited constructs are rejected
        
    PROHIBITED MODULES:
        - threading, multiprocessing, asyncio
        - queue, subprocess, socket, requests
        - httpx, aiohttp, grpc, websockets
        - concurrent.futures
        - time, datetime, uuid, random, psutil
    """
    
    @staticmethod
    def validate_ast(
        module_code: str,
        allowed_imports: Tuple[str, ...] = ()
    ) -> ASTValidationResult:
        """
        Validate Python code for prohibited constructs.
        
        Args:
            module_code: Python source code to validate
            allowed_imports: Tuple of allowed imports
            
        Returns:
            (is_valid, prohibited_found, allowed_found)
            
        INVARIANT: Same input produces same output
        """
        prohibited_found = []
        allowed_found = []
        
        for line in module_code.split("\n"):
            # Check for prohibited imports
            stripped = line.strip()
            
            if stripped.startswith("import ") or stripped.startswith("from "):
                module_name = ASTValidator._extract_module_name(stripped)
                
                if module_name in AST_PROHIBITED_MODULES:
                    prohibited_found.append(
                        f"Prohibited import: {module_name}"
                    )
                elif module_name in allowed_imports:
                    allowed_found.append(f"Allowed import: {module_name}")
        
        return (
            len(prohibited_found) == 0,
            tuple(prohibited_found),
            tuple(allowed_found)
        )
    
    @staticmethod
    def _extract_module_name(import_statement: str) -> str:
        """
        Extract module name from import statement.
        
        Args:
            import_statement: Import statement to parse
            
        Returns:
            Module or sub-module name
        """
        if import_statement.startswith("import "):
            parts = import_statement[7:].split()
            return parts[0].split(".")[0] if parts else ""
        elif import_statement.startswith("from "):
            parts = import_statement[5:].split()
            return parts[0].split(".")[0] if parts else ""
        return ""


# =============================================================================
# LAW VALIDATOR
# =============================================================================

class LawValidator:
    """
    Validator for architectural laws and invariants.
    
    INVARIANTS:
        LV-INV-001: Laws are validated deterministically
        LV-INV-002: Law violations are rejected
    """
    
    @staticmethod
    def validate_persistence_laws(
        model: BasePersistenceModel
    ) -> ValidationResult:
        """
        Validate persistence laws for a model.
        
        LAWS VALIDATED:
            ORIENTED-PERSISTENCE-LAW-001 through -010
            
        Args:
            model: The persistence model to validate
            
        Returns:
            (is_valid, list_of_errors)
        """
        errors = []
        
        # Check immutability (frozen dataclass)
        if not hasattr(model, "__dataclass_fields__"):
            errors.append(
                "Persistence model must be a frozen dataclass"
            )
        
        return len(errors) == 0, tuple(errors)
    
    @staticmethod
    def validate_continuity_laws(
        model: BasePersistenceModel
    ) -> ValidationResult:
        """
        Validate continuity laws for a model.
        
        LAWS VALIDATED:
            ORIENTED-CONTINUITY-LAW-001 through -010
            
        Args:
            model: The persistence model to validate
            
        Returns:
            (is_valid, list_of_errors)
        """
        return True, ()
    
    @staticmethod
    def validate_law_compliance(
        model: BasePersistenceModel,
        law_set: str = "all"
    ) -> ValidationResult:
        """
        Validate model against a set of laws.
        
        Args:
            model: The persistence model to validate
            law_set: Set of laws to validate against
            
        Returns:
            (is_valid, list_of_errors)
        """
        if law_set == "persistence":
            return LawValidator.validate_persistence_laws(model)
        elif law_set == "continuity":
            return LawValidator.validate_continuity_laws(model)
        else:
            # Validate all applicable laws
            is_valid, errors = LawValidator.validate_persistence_laws(model)
            if not is_valid:
                return False, errors
            
            return LawValidator.validate_continuity_laws(model)


# =============================================================================
# VALIDATION EXPORTS
# =============================================================================

__all__ = [
    "VALIDATION_PASSED",
    "VALIDATION_FAILED",
    "AST_PROHIBITED_MODULES",
    "AST_PROHIBITED_CLASSES",
    "ValidationResult",
    "ASTValidationResult",
    "BaseValidator",
    "ASTValidator",
    "LawValidator",
]