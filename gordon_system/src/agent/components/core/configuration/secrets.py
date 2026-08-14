# Secret & Sensitive Configuration - Phase 3.18
# ==============================================
"""
Secure configuration handling for secrets and sensitive values.

Architectural Principles:
-------------------------
1. SECRETS ARE REFERENCES, NOT VALUES - Store secret identifiers, not plaintext
2. SECRET BOUNDARIES ARE ENFORCED - Secrets never appear in diagnostics/logs
3. SECRET PROVISIONING IS SECURE - Runtime injection with audit trail
4. REDACTION IS AUTOMATIC - Sensitive values automatically filtered

Secret Types:
-------------
- Credentials (passwords, API keys)
- Authentication tokens
- Authorization tokens  
- Encryption keys
- Certificates
- Private data

Configuration Pattern:
----------------------
Instead of storing plaintext secrets:

    ❌ BAD: secret_key = "sk_live_123abc"
    
    ✅ GOOD: secret_key = SecretReference(
        provider="vault",
        path="production/api_keys/gordon"
    )

Secret Resolution Flow:
-----------------------
    1. Configuration contains SecretReference
    2. Runtime calls SecretProvider with authorization
    3. Provider validates access and returns value
    4. Value is used but never persisted in config
"""
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Tuple
from enum import Enum
import time


# =============================================================================
# Secret Reference (NOT the secret itself)
# =============================================================================

@dataclass(frozen=True)
class SecretReference:
    """
    A reference to a secret value stored externally.
    
    Configuration should store SECRET REFERENCES, not plaintext values.
    
    The actual secret is resolved at runtime by a SecretProvider with
    appropriate authorization and audit logging.
    """
    provider: str  # e.g., "vault", "secrets_manager", "aws_secrets"
    path: str      # Secret path/identifier in provider (e.g., "prod/gordon/api_key")
    
    @property
    def resolved(self) -> bool:
        """A secret reference is not resolved until runtime."""
        return False
    
    def resolve_with(self, value: str) -> "SecretValue":
        """
        Resolve this reference with an actual value.
        
        Args:
            value: The actual secret value (should be temporary)
            
        Returns:
            SecretValue containing the resolved value
        """
        return SecretValue(
            reference=self,
            value=value,
            resolved_at=time.monotonic()
        )


# =============================================================================
# Resolved Secret Value (runtime only)
# =============================================================================

@dataclass(frozen=True)
class SecretValue:
    """
    A resolved secret value (for runtime use only).
    
    NEVER store these in configuration files or persist them.
    This exists only during runtime execution.
    """
    reference: SecretReference
    value: str  # The actual secret - should be cleared after use!
    resolved_at: float = field(default_factory=time.monotonic)
    
    def redacted(self) -> str:
        """Return a redacted representation for logging/diagnostics."""
        return "***SECRET***"
    
    def mask(self, keep_prefix: int = 0, keep_suffix: int = 0) -> str:
        """
        Return masked version with configurable visible characters.
        
        Args:
            keep_prefix: Number of characters to show at start
            keep_suffix: Number of characters to show at end
            
        Returns:
            Masked string like "sk_live_****1234"
        """
        value = self.value
        if len(value) <= keep_prefix + keep_suffix:
            return "*" * len(value)
        
        visible_start = value[:keep_prefix]
        visible_end = value[-keep_suffix:] if keep_suffix > 0 else ""
        masked_length = len(value) - keep_prefix - keep_suffix
        
        return f"{visible_start}{'*' * masked_length}{visible_end}"


# =============================================================================
# Secret Provider Interface
# =============================================================================

class SecretProviderType(Enum):
    """Types of secret providers."""
    VAULT = "vault"
    AWS_SECRETS_MANAGER = "aws_secrets_manager"
    AZURE_KEY_VAULT = "azure_key_vault"
    GCP_SECRET_MANAGER = "gcp_secret_manager"
    LOCAL_FILE = "local_file"
    ENVIRONMENT = "environment"


@dataclass(frozen=True)
class SecretProviderConfig:
    """Configuration for a secret provider."""
    provider_type: SecretProviderType
    endpoint: Optional[str] = None  # For remote providers
    auth_mode: str = "service_account"  # service_account, iam_role, etc.
    credentials_path: Optional[str] = None


class SecretProvider:
    """
    Interface for secret retrieval.
    
    Providers are responsible for:
    - Authenticating with the secret store
    - Authorizing access to secrets
    - Auditing secret access
    - Returning resolved secret values
    
    Invariants:
    - Provider is read-only (never modifies secrets)
    - All access is audited
    - Values are returned temporarily (not stored)
    """
    
    def __init__(self, config: SecretProviderConfig):
        self._config = config
        self._connected = False
    
    @property
    def config(self) -> SecretProviderConfig:
        return self._config
    
    def connect(self) -> bool:
        """Establish connection to secret provider."""
        self._connected = True
        return True
    
    def disconnect(self) -> None:
        """Disconnect from secret provider."""
        self._connected = False
    
    def get_secret(self, reference: SecretReference) -> Optional[SecretValue]:
        """
        Retrieve a secret value by reference.
        
        Args:
            reference: Secret reference with provider and path
            
        Returns:
            Resolved SecretValue or None if not found
        """
        raise NotImplementedError("Subclasses must implement get_secret()")
    
    def list_secrets(self, prefix: Optional[str] = None) -> Tuple[SecretReference, ...]:
        """List available secret references."""
        raise NotImplementedError("Subclasses must implement list_secrets()")


# =============================================================================
# Secret Manager (Runtime Authority)
# =============================================================================

class SecretManager:
    """
    Canonical authority for all secret operations.
    
    Responsibilities:
    - Track active secret references in configuration
    - Coordinate secret resolution with providers
    - Enforce secret redaction policies
    - Audit secret access
    
    Invariants:
    - No plaintext secrets in configuration files
    - All secret access is audited
    - Secrets are cleared after use when possible
    """
    
    def __init__(self):
        self._providers: Dict[str, SecretProvider] = {}
        self._resolved_secrets: Dict[str, SecretValue] = {}
        self._access_log: List[Dict[str, Any]] = []
        self._lock = _import_threading().Lock()
    
    def register_provider(self, provider: SecretProvider) -> None:
        """Register a secret provider."""
        with self._lock:
            config = provider.config
            key = f"{config.provider_type.value}_{config.endpoint or 'default'}"
            self._providers[key] = provider
            if not config.provider_type == SecretProviderType.LOCAL_FILE:
                provider.connect()
    
    def get_secret(self, reference: SecretReference) -> Optional[SecretValue]:
        """
        Get a secret by reference.
        
        Args:
            reference: The secret reference
            
        Returns:
            Resolved value or None
        """
        with self._lock:
            # Check cache first
            if reference.path in self._resolved_secrets:
                return self._resolved_secrets[reference.path]
            
            # Try to resolve via provider
            provider_key = reference.provider
            provider = self._providers.get(provider_key)
            
            if provider is None:
                return None
            
            value = provider.get_secret(reference)
            
            if value:
                self._resolved_secrets[reference.path] = value
                
                # Log access for audit trail
                self._access_log.append({
                    "timestamp": time.monotonic(),
                    "path": reference.path,
                    "action": "read",
                    "redacted_at_end": False  # Will be redacted before storage
                })
            
            return value
    
    def redact_configuration(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """
        Recursively redact all secret values from a configuration dictionary.
        
        Args:
            config: Configuration dictionary (may contain secret references)
            
        Returns:
            Redacted configuration with ***FILTERED*** for secrets
        """
        result = {}
        secret_patterns = ("password", "secret", "token", "key", "credential")
        
        for key, value in config.items():
            if isinstance(value, dict):
                result[key] = self.redact_configuration(value)
            elif isinstance(value, SecretReference):
                result[key] = "***SECRET_REFERENCE***"
            elif isinstance(value, SecretValue):
                result[key] = value.redacted()
            elif any(pattern in key.lower() for pattern in secret_patterns):
                # Check if this looks like a secret field
                result[key] = "***FILTERED***"
            else:
                result[key] = value
        
        return result
    
    def get_access_log(self) -> Tuple[Dict[str, Any], ...]:
        """Get audit log entries (without actual secret values)."""
        with self._lock:
            # Redact sensitive data from logs
            redacted_log = []
            for entry in self._access_log:
                redacted_entry = {
                    "timestamp": entry["timestamp"],
                    "path": entry.get("path", "")[:10] + "...",  # Only first 10 chars
                    "action": entry.get("action", ""),
                }
                redacted_log.append(redacted_entry)
            
            return tuple(redacted_log)


# =============================================================================
# Sensitive Field Detection
# =============================================================================

def is_sensitive_field_name(name: str) -> bool:
    """
    Check if a field name suggests it contains sensitive data.
    
    Args:
        name: Field name to check
        
    Returns:
        True if the field likely contains secrets
    """
    sensitive_patterns = (
        "password", "secret", "token", "key", "credential",
        "api_key", "private_key", "auth_token", "bearer_token",
        "encryption_key", "signing_key", "client_secret"
    )
    
    name_lower = name.lower()
    return any(pattern in name_lower for pattern in sensitive_patterns)


@dataclass(frozen=True)
class SensitiveField:
    """A field that contains sensitive data."""
    path: str           # Dot-notation path (e.g., "database.password")
    field_type: str     # Field type hint
    redaction_policy: str = "full"  # full, prefix_4, suffix_4


def detect_sensitive_fields(data: Dict[str, Any], prefix: str = "") -> Tuple[SensitiveField, ...]:
    """
    Detect fields that likely contain sensitive data.
    
    Args:
        data: Data dictionary to analyze
        prefix: Path prefix for nested fields
        
    Returns:
        Tuple of detected sensitive fields
    """
    sensitive = []
    
    for key, value in data.items():
        path = f"{prefix}.{key}" if prefix else key
        
        if is_sensitive_field_name(key):
            field_type = _infer_field_type(value)
            sensitive.append(SensitiveField(
                path=path,
                field_type=field_type
            ))
        
        # Recurse into nested dicts
        if isinstance(value, dict):
            sensitive.extend(detect_sensitive_fields(value, path))
    
    return tuple(sensitive)


def _infer_field_type(value: Any) -> str:
    """Infer the type of a value."""
    if isinstance(value, str):
        return "string"
    elif isinstance(value, int):
        return "integer"
    elif isinstance(value, float):
        return "float"
    elif isinstance(value, bool):
        return "boolean"
    elif isinstance(value, (list, tuple)):
        return "array"
    elif isinstance(value, dict):
        return "object"
    else:
        return "unknown"


# =============================================================================
# Public API
# =============================================================================

__all__ = [
    # References & Values
    "SecretReference",
    "SecretValue",
    
    # Provider
    "SecretProviderType",
    "SecretProviderConfig",
    "SecretProvider",
    
    # Manager
    "SecretManager",
    
    # Detection
    "is_sensitive_field_name",
    "SensitiveField",
    "detect_sensitive_fields",
]


def _import_threading():
    """Import threading module lazily."""
    import threading
    return threading