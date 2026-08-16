# Integration Contract - Phase 5.1.7 Canonical Integration Interface
# ====================================================================

"""
Memory Integration Contract: Defines the interface for subsystem communication.

Every subsystem that needs to interact with Memory must:
    1. Obtain a valid contract through the integration layer
    2. Send requests following the request contract
    3. Handle responses according to the response contract
    4. Respect version compatibility requirements

Contract Laws:
    CONTRACT-LAW-001: Every consumer must use an explicit contract
    CONTRACT-LAW-002: Contracts define supported requests and responses
    CONTRACT-LAW-003: Contracts specify version information
    CONTRACT-LAW-004: Contracts guarantee deterministic behavior
    CONTRACT-LAW-005: Contracts preserve semantic integrity
    CONTRACT-LAW-006: Contracts expose health and diagnostics
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Tuple, Optional, Any, Callable
from enum import Enum, auto
import time
import uuid


# =============================================================================
# INTEGRATION CONTRACT TYPES - What kind of integration?
# =============================================================================


class IntegrationContractType(Enum):
    """
    Types of integration contracts.
    
    | Type         | Description                                         |
    |--------------|-----------------------------------------------------|
    | PERCEPTION   | Observation and signal exchange                     |
    | WORKSPACE    | Active context and working memory                   |
    | KNOWLEDGE    | Semantic information exchange                       |
    | LEARNING     | Behavior improvement and policy proposals           |
    | IDENTITY     | Autobiographical continuity                         |
    | COORDINATION | Synchronization of activities                       |
    | REASONING    | Online reasoning support                            |
    | WORLD_MODEL  | Environmental modeling                              |
    """
    
    PERCEPTION = "perception"
    WORKSPACE = "workspace"
    KNOWLEDGE = "knowledge"
    LEARNING = "learning"
    IDENTITY = "identity"
    COORDINATION = "coordination"
    REASONING = "reasoning"
    WORLD_MODEL = "world_model"


# =============================================================================
# COMPATIBILITY STATES
# =============================================================================


class CompatibilityState(Enum):
    """
    Compatibility status between consumer and Memory.
    
    | State       | Description                                        |
    |-------------|----------------------------------------------------|
    | COMPATIBLE  | Full compatibility, all features work              |
    | DEPRECATED  | Works but some features deprecated                 |
    | PARTIAL     | Partial compatibility, limited functionality       |
    | INCOMPATIBLE| Cannot communicate                                 |
    """
    
    COMPATIBLE = "compatible"
    DEPRECATED = "deprecated"
    PARTIAL = "partial"
    INCOMPATIBLE = "incompatible"


# =============================================================================
# VERSION INFORMATION
# =============================================================================


@dataclass(frozen=True)
class VersionInfo:
    """
    Version information for contract compatibility.
    
    Fields:
        major:         Major version (breaking changes increment this)
        minor:         Minor version (backwards compatible additions)
        patch:         Patch version (bug fixes only)
        
        # Compatibility range
        min_supported: Minimum compatible version
        max_supported: Maximum compatible version
        
        # Status
        is_stable:     Is this a stable release?
    """
    
    major: int = 1
    minor: int = 0
    patch: int = 0
    
    min_supported: int = 0
    max_supported: int = 999
    
    is_stable: bool = True
    
    def __str__(self) -> str:
        return f"{self.major}.{self.minor}.{self.patch}"
    
    def satisfies(self, required_min: int, required_max: int) -> bool:
        """Check if this version satisfies the given range."""
        return required_min <= self.major <= required_max


# =============================================================================
# INTEGRATION CONTRACT
# =============================================================================


@dataclass(frozen=True)
class MemoryIntegrationContract:
    """
    Integration contract between a subsystem and Memory.
    
    Every interaction must go through a contract. The contract defines:
        - Which requests are supported
        - What responses to expect
        - Version compatibility guarantees
        - Semantic integrity constraints
    
    Fields:
        consumer:           Which subsystem is the consumer?
        contract_type:      Type of integration
        
        # Supported operations
        supported_requests: List of request types supported
        supported_responses: List of response formats produced
        
        # Version info
        version:            Current contract version
        compatibility:      Compatibility guarantee level
        
        # Guarantees
        semantic_integrity: Is semantic integrity guaranteed?
        determinism:        Is behavior deterministic?
        
        # Diagnostics
        health_status:      Overall health status
        last_validation:    When was this contract validated?
        validation_errors:  Any recent validation errors?
    """
    
    consumer: str                           # Consumer subsystem name
    
    contract_type: IntegrationContractType = IntegrationContractType.PERCEPTION
    
    # Supported operations
    supported_requests: Tuple[str, ...] = field(default_factory=tuple)
    supported_responses: Tuple[str, ...] = field(default_factory=tuple)
    
    # Version info
    version: VersionInfo = field(default_factory=VersionInfo)
    compatibility: CompatibilityState = CompatibilityState.COMPATIBLE
    
    # Guarantees
    semantic_integrity: bool = True
    determinism: bool = True
    
    # Diagnostics
    health_status: str = "healthy"
    last_validation: float = field(default_factory=time.time)
    validation_errors: Tuple[str, ...] = field(default_factory=tuple)
    
    def is_compatible(self, other_version: VersionInfo) -> CompatibilityState:
        """
        Check compatibility with another version.
        
        Returns COMPATIBLE if both versions support each other's ranges.
        """
        if (other_version.min_supported <= self.version.major <= other_version.max_supported and
            self.version.min_supported <= other_version.major <= self.version.max_supported):
            return CompatibilityState.COMPATIBLE
        
        if (other_version.major == self.version.major and
            other_version.minor >= self.version.minor):
            return CompatibilityState.DEPRECATED
        
        return CompatibilityState.INCOMPATIBLE
    
    def validate_request(self, request_type: str) -> bool:
        """Check if the given request type is supported."""
        return request_type in self.supported_requests
    
    def validate_response(self, response_format: str) -> bool:
        """Check if the given response format is produced."""
        return response_format in self.supported_responses


# =============================================================================
# CONTRACT MANAGER
# =============================================================================


class ContractManager:
    """
    Manager for integration contracts.
    
    Provides contract lookup, validation, and version negotiation.
    
    Contract Laws:
        CONTRACT-LAW-007: Contracts are versioned and versionable
        CONTRACT-LAW-008: Version negotiation is deterministic
    """
    
    def __init__(self):
        self._contracts: Dict[str, MemoryIntegrationContract] = {}
        self._version_registry: Dict[str, List[VersionInfo]] = {}
    
    def register_contract(self, contract: MemoryIntegrationContract) -> None:
        """Register a new integration contract."""
        key = f"{contract.consumer}:{contract.contract_type.value}"
        self._contracts[key] = contract
        
        # Register version
        consumer_key = contract.consumer
        if consumer_key not in self._version_registry:
            self._version_registry[consumer_key] = []
        self._version_registry[consumer_key].append(contract.version)
    
    def get_contract(self, consumer: str, 
                     contract_type: IntegrationContractType) -> Optional[MemoryIntegrationContract]:
        """Get the contract for a specific consumer and type."""
        key = f"{consumer}:{contract_type.value}"
        return self._contracts.get(key)
    
    def negotiate_version(self, consumer: str,
                          requested_version: VersionInfo) -> Tuple[VersionInfo, CompatibilityState]:
        """
        Negotiate compatible version with consumer.
        
        Returns: (compatible_version, compatibility_state)
        """
        if consumer not in self._version_registry:
            return (requested_version, CompatibilityState.INCOMPATIBLE)
        
        # Find a compatible version
        for available_version in sorted(self._version_registry[consumer], 
                                        key=lambda v: (v.major, v.minor), 
                                        reverse=True):
            compatibility = requested_version.satisfies(available_version.min_supported,
                                                       available_version.max_supported)
            if compatibility != CompatibilityState.INCOMPATIBLE:
                return (available_version, compatibility)
        
        # No compatible version found
        return (requested_version, CompatibilityState.INCOMPATIBLE)
    
    def validate_contract(self, consumer: str) -> Tuple[bool, Tuple[str, ...]]:
        """
        Validate all contracts for a consumer.
        
        Returns: (is_valid, errors)
        """
        errors = []
        
        # Find all contracts for this consumer
        consumer_contracts = {
            k: v for k, v in self._contracts.items()
            if k.startswith(f"{consumer}:")
        }
        
        for contract in consumer_contracts.values():
            # Check semantic integrity
            if not contract.semantic_integrity:
                errors.append(f"Contract {contract.contract_type.value} violates semantic integrity")
            
            # Check determinism
            if not contract.determinism:
                errors.append(f"Contract {contract.contract_type.value} is non-deterministic")
        
        return (len(errors) == 0, tuple(errors))
    
    def list_contracts(self) -> Dict[str, MemoryIntegrationContract]:
        """List all registered contracts."""
        return dict(self._contracts)