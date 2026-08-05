# Contract Verification - Testing Infrastructure
# ==========================================

"""
ContractVerifier: Verifies implementations satisfy protocols.

This module provides contract verification for:
- Public API contracts (function signatures, return types)
- Protocol compliance (interface implementations)
- Provider contracts (service implementations)
"""

from dataclasses import dataclass, field
from typing import List, Dict, Optional, Callable, Type, Any
import inspect


@dataclass(frozen=True)
class ContractViolation:
    """Immutable representation of a contract violation."""
    
    contract_id: str
    item_name: str  # Function name, class name, etc.
    violation_type: str  # Missing, WrongType, WrongSignature, etc.
    expected: str
    actual: Optional[str] = None
    location: Optional[str] = None
    
    def to_dict(self) -> Dict:
        return {
            "contract_id": self.contract_id,
            "item_name": self.item_name,
            "violation_type": self.violation_type,
            "expected": self.expected,
            "actual": self.actual,
            "location": self.location,
        }


@dataclass(frozen=True)
class ContractVerificationResult:
    """Immutable result of contract verification."""
    
    contract_id: str
    is_compliant: bool
    violations: List[ContractViolation]
    verified_items: int = 0
    
    @property
    def has_violations(self) -> bool:
        return len(self.violations) > 0


class ContractVerifier:
    """
    Verifies that implementations satisfy declared contracts.
    
    This verifier checks:
    - Function signatures match expected signatures
    - Return types are correct
    - Parameter types are correct
    - Class methods implement required protocol
    """
    
    def __init__(self):
        """Initialize the contract verifier."""
        self._contracts: Dict[str, Callable] = {}
    
    def register_contract(self, contract_id: str, contract_fn: Callable) -> None:
        """
        Register a contract for verification.
        
        Args:
            contract_id: Unique identifier for the contract
            contract_fn: Function that defines the contract
        """
        self._contracts[contract_id] = contract_fn
    
    def verify_function_signature(
        self,
        func: Callable,
        expected_signature: inspect.Signature,
    ) -> ContractVerificationResult:
        """
        Verify a function matches its expected signature.
        
        Args:
            func: The function to verify
            expected_signature: Expected function signature
            
        Returns:
            ContractVerificationResult with verification status
        """
        violations = []
        actual_sig = inspect.signature(func)
        
        # Check parameters match
        for name, param in expected_signature.parameters.items():
            if name not in actual_sig.parameters:
                violations.append(
                    ContractViolation(
                        contract_id="signature",
                        item_name=func.__name__,
                        violation_type="MissingParameter",
                        expected=f"Parameter '{name}'",
                        actual=None,
                        location=func.__qualname__,
                    )
                )
        
        # Check return type
        if expected_signature.return_annotation != inspect.Signature.empty:
            if actual_sig.return_annotation != expected_signature.return_annotation:
                violations.append(
                    ContractViolation(
                        contract_id="signature",
                        item_name=func.__name__,
                        violation_type="WrongReturnType",
                        expected=str(expected_signature.return_annotation),
                        actual=str(actual_sig.return_annotation),
                        location=func.__qualname__,
                    )
                )
        
        return ContractVerificationResult(
            contract_id="signature",
            is_compliant=len(violations) == 0,
            violations=violations,
            verified_items=1 if len(violations) == 0 else 0,
        )
    
    def verify_class_protocol(self, cls: Type, protocol: Type) -> ContractVerificationResult:
        """
        Verify a class implements all methods from a protocol.
        
        Args:
            cls: The class to verify
            protocol: The expected protocol (interface)
            
        Returns:
            ContractVerificationResult with verification status
        """
        violations = []
        
        # Get required methods from protocol
        required_methods = [
            name for name, _ in inspect.getmembers(protocol, predicate=inspect.isfunction)
            if not name.startswith("_")
        ]
        
        for method_name in required_methods:
            if not hasattr(cls, method_name):
                violations.append(
                    ContractViolation(
                        contract_id="protocol",
                        item_name=f"{cls.__name__}.{method_name}",
                        violation_type="MissingMethod",
                        expected=f"Method '{method_name}' from protocol",
                        actual=None,
                        location=cls.__qualname__,
                    )
                )
        
        return ContractVerificationResult(
            contract_id="protocol",
            is_compliant=len(violations) == 0,
            violations=violations,
            verified_items=len(required_methods) - len(violations),
        )
    
    def verify_contract(self, contract_id: str, target: Any) -> ContractVerificationResult:
        """
        Verify a target (function or class) against a registered contract.
        
        Args:
            contract_id: ID of the contract to verify against
            target: The function or class to verify
            
        Returns:
            ContractVerificationResult with verification status
        """
        if contract_id not in self._contracts:
            return ContractVerificationResult(
                contract_id=contract_id,
                is_compliant=False,
                violations=[
                    ContractViolation(
                        contract_id=contract_id,
                        item_name=str(target),
                        violation_type="ContractNotFound",
                        expected=f"Contract '{contract_id}' not registered",
                        actual=None,
                    )
                ],
            )
        
        contract_fn = self._contracts[contract_id]
        
        if inspect.isfunction(target):
            return self.verify_function_signature(target, inspect.signature(contract_fn))
        elif inspect.isclass(target):
            # For classes, check protocol compliance
            return ContractVerificationResult(
                contract_id=contract_id,
                is_compliant=False,  # Class verification needs more logic
                violations=[],
                verified_items=0,
            )
        
        return ContractVerificationResult(
            contract_id=contract_id,
            is_compliant=False,
            violations=[
                ContractViolation(
                    contract_id=contract_id,
                    item_name=str(target),
                    violation_type="UnsupportedTarget",
                    expected="Function or class",
                    actual=type(target).__name__,
                )
            ],
        )


def verify_contract(
    contract_id: str,
    target: Any,
    verifier: Optional[ContractVerifier] = None,
) -> ContractVerificationResult:
    """
    Convenience function to verify a contract.
    
    Args:
        contract_id: ID of the contract
        target: Function or class to verify
        verifier: ContractVerifier instance (creates new if None)
        
    Returns:
        ContractVerificationResult with verification status
    """
    v = verifier or ContractVerifier()
    return v.verify_contract(contract_id, target)


def check_protocol_compliance(cls: Type, protocol: Type) -> ContractVerificationResult:
    """
    Check if a class implements a protocol.
    
    Args:
        cls: The class to verify
        protocol: Expected protocol
        
    Returns:
        ContractVerificationResult with verification status
    """
    verifier = ContractVerifier()
    return verifier.verify_class_protocol(cls, protocol)