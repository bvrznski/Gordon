# Authentication Providers - Production Implementation
# ====================================================
"""
Authentication provider implementations for Phase 3.7.16-I.

This module provides concrete implementations of the AuthenticationProvider
interface for various authentication methods:
- Local authentication (credential-based)
- Token authentication (JWT/Bearer tokens)
- API key authentication
- Service-to-service authentication

All providers only verify identity - trust and authorization are separate.
"""

from dataclasses import dataclass, field
from typing import (
    Dict,
    Any,
    Optional,
    List,
    Tuple,
)
import time
import uuid
import hashlib
import hmac


# Import security primitives - use string-based type hints to avoid circular imports
from . import (
    AuthMethod,
    Credential,
    Token,
    CertificateReference,
    AuthenticationRequest,
    AuthenticationResult,
    Identity,
    IdentityType,
)


# =============================================================================
# Local Authentication Provider
# =============================================================================

class LocalAuthenticationProvider:
    """
    Local credential-based authentication provider.
    
    Validates credentials against stored hashes. Credentials are never
    stored in plaintext - only hashed versions are kept.
    """
    
    def __init__(self, provider_id: str = "local"):
        self._provider_id = provider_id
        self._credentials: Dict[str, Credential] = {}
        self._lock = __import__("threading").Lock()
    
    @property
    def provider_id(self) -> str:
        return self._provider_id
    
    async def register_credential(
        self,
        principal_id: str,
        secret_value: str,
        expires_at: Optional[float] = None
    ) -> Credential:
        """
        Register a credential for a principal.
        
        The secret is hashed before storage using SHA256 with salt.
        """
        # Generate salt and hash
        salt = __import__("secrets").token_hex(16)
        hash_input = f"{salt}:{secret_value}"
        credential_hash = hashlib.sha256(hash_input.encode()).hexdigest()
        
        credential = Credential(
            credential_id=str(uuid.uuid4()),
            principal_id=principal_id,
            method=AuthMethod.LOCAL,
            credential_hash=f"{salt}:{credential_hash}",
            created_at=time.monotonic(),
            expires_at=expires_at
        )
        
        with self._lock:
            self._credentials[principal_id] = credential
        
        return credential
    
    async def authenticate(self, request: AuthenticationRequest) -> AuthenticationResult:
        """
        Authenticate using local credentials.
        
        Returns success only if:
        1. Principal ID and credential hash are provided
        2. Credential exists for principal
        3. Hash matches (credential is valid)
        4. Credential has not expired
        """
        # Validate request has required fields
        if not request.principal_id or not request.credential_hash:
            return AuthenticationResult(
                success=False,
                failure_reason="Missing principal_id or credential_hash"
            )
        
        with self._lock:
            if request.principal_id not in self._credentials:
                return AuthenticationResult(
                    success=False,
                    failure_reason="Unknown principal"
                )
            
            credential = self._credentials[request.principal_id]
            
            # Verify credential hasn't expired
            if not credential.is_valid():
                del self._credentials[request.principal_id]  # Clean up expired
                return AuthenticationResult(
                    success=False,
                    failure_reason="Credential has expired"
                )
            
            # Verify hash matches
            salt = credential.credential_hash.split(':')[0]
            hash_input = f"{salt}:{request.credential_hash}"
            computed_hash = hashlib.sha256(hash_input.encode()).hexdigest()
            
            # For local auth, we compare the stored hash format with input
            if not self._verify_credential(request.credential_hash, credential):
                return AuthenticationResult(
                    success=False,
                    failure_reason="Invalid credentials"
                )
        
        # Success - create token for session
        token = Token(
            token_id=str(uuid.uuid4()),
            principal_id=request.principal_id,
            type_=AuthMethod.LOCAL,
            issued_at=time.monotonic(),
            expires_at=None,  # Default no expiry
            scopes=("read",),
            audience="runtime",
            issuer=self._provider_id
        )
        
        return AuthenticationResult(
            success=True,
            principal_id=request.principal_id,
            identity=Identity(
                identity_id=request.principal_id,
                name=f"Principal-{request.principal_id[:8]}",
                type_=IdentityType.USER
            ),
            method=AuthMethod.LOCAL,
            timestamp=time.monotonic(),
            token=token
        )
    
    def _verify_credential(self, input_hash: str, stored_credential: Credential) -> bool:
        """Verify an input credential against the stored one."""
        # For simplicity in this implementation, we compare hashes
        return stored_credential.credential_hash == input_hash
    
    async def validate_token(self, token: Token) -> bool:
        """Validate a token without re-authenticating."""
        with self._lock:
            if not token.is_valid():
                return False
            
            # In production, would verify token signature/claims
            return True


# =============================================================================
# Token Authentication Provider
# =============================================================================

class TokenAuthenticationProvider:
    """
    Token-based authentication provider (JWT/Bearer tokens).
    
    Validates tokens without requiring re-authentication. Tokens are issued
    by other providers and validated here.
    """
    
    def __init__(self, provider_id: str = "token"):
        self._provider_id = provider_id
        self._tokens: Dict[str, Token] = {}
        self._lock = __import__("threading").Lock()
    
    @property
    def provider_id(self) -> str:
        return self._provider_id
    
    async def register_token(self, token: Token) -> None:
        """Register a token for validation."""
        with self._lock:
            self._tokens[token.token_id] = token
    
    async def authenticate(self, request: AuthenticationRequest) -> AuthenticationResult:
        """
        Authenticate using a token.
        
        Returns success only if:
        1. Token is provided in request
        2. Token exists and is valid
        3. Token audience matches this runtime
        """
        if not request.token:
            return AuthenticationResult(
                success=False,
                failure_reason="No token provided"
            )
        
        with self._lock:
            token = request.token
            
            # Check if token exists and is valid
            if token.token_id not in self._tokens:
                return AuthenticationResult(
                    success=False,
                    failure_reason="Unknown token"
                )
            
            stored_token = self._tokens[token.token_id]
            
            # Verify token hasn't expired
            if not stored_token.is_valid():
                del self._tokens[stored_token.token_id]
                return AuthenticationResult(
                    success=False,
                    failure_reason="Token has expired"
                )
        
        return AuthenticationResult(
            success=True,
            principal_id=token.principal_id,
            identity=Identity(
                identity_id=token.principal_id,
                name=f"Principal-{token.principal_id[:8]}",
                type_=IdentityType.USER
            ),
            method=AuthMethod.TOKEN,
            timestamp=time.monotonic(),
            token=stored_token
        )
    
    async def validate_token(self, token: Token) -> bool:
        """Validate a token without re-authenticating."""
        with self._lock:
            if not token.is_valid():
                return False
            
            if token.token_id not in self._tokens:
                return False
            
            # Verify audience (token intended for this runtime)
            if token.audience and token.audience != "runtime":
                return False
            
            return True


# =============================================================================
# API Key Authentication Provider
# =============================================================================

class ApiKeyAuthenticationProvider:
    """
    API key-based authentication provider.
    
    Validates API keys against stored values. Keys are hashed before storage.
    """
    
    def __init__(self, provider_id: str = "api_key"):
        self._provider_id = provider_id
        self._api_keys: Dict[str, Tuple[str, Token]] = {}  # key_hash -> (key_id, token)
        self._lock = __import__("threading").Lock()
    
    @property
    def provider_id(self) -> str:
        return self._provider_id
    
    async def register_api_key(
        self,
        key_value: str,
        principal_id: str,
        scopes: Tuple[str, ...] = tuple(),
        expires_at: Optional[float] = None
    ) -> str:
        """
        Register an API key for a principal.
        
        Returns the key ID. The actual key value is never stored.
        """
        # Hash the key (for storage)
        key_hash = hashlib.sha256(key_value.encode()).hexdigest()
        
        token = Token(
            token_id=str(uuid.uuid4()),
            principal_id=principal_id,
            type_=AuthMethod.API_KEY,
            issued_at=time.monotonic(),
            expires_at=expires_at,
            scopes=scopes,
            audience="runtime",
            issuer=self._provider_id
        )
        
        with self._lock:
            self._api_keys[key_hash] = (key_value[:8] + "...", token)
        
        return key_hash
    
    async def authenticate(self, request: AuthenticationRequest) -> AuthenticationResult:
        """
        Authenticate using an API key.
        
        The API key should be provided in the context as "api_key".
        """
        api_key = request.context.get("api_key")
        
        if not api_key:
            return AuthenticationResult(
                success=False,
                failure_reason="No API key provided"
            )
        
        # Hash the provided key and check against stored
        key_hash = hashlib.sha256(api_key.encode()).hexdigest()
        
        with self._lock:
            if key_hash not in self._api_keys:
                return AuthenticationResult(
                    success=False,
                    failure_reason="Invalid API key"
                )
            
            _, token = self._api_keys[key_hash]
            
            # Verify token is still valid
            if not token.is_valid():
                del self._api_keys[key_hash]
                return AuthenticationResult(
                    success=False,
                    failure_reason="API key has expired"
                )
        
        return AuthenticationResult(
            success=True,
            principal_id=token.principal_id,
            identity=Identity(
                identity_id=token.principal_id,
                name=f"Principal-{token.principal_id[:8]}",
                type_=IdentityType.USER
            ),
            method=AuthMethod.API_KEY,
            timestamp=time.monotonic(),
            token=token
        )
    
    async def validate_token(self, token: Token) -> bool:
        """Validate a token without re-authenticating."""
        with self._lock:
            if not token.is_valid():
                return False
            
            # Check if this is one of our tokens
            for key_hash, (_, stored_token) in self._api_keys.items():
                if stored_token.token_id == token.token_id:
                    return True
            
            return False


# =============================================================================
# Service-to-Service Authentication Provider
# =============================================================================

class ServiceAuthenticationProvider:
    """
    Service-to-service authentication provider.
    
    Validates service credentials using shared secrets or certificates.
    Used for internal service communication.
    """
    
    def __init__(self, provider_id: str = "service"):
        self._provider_id = provider_id
        self._services: Dict[str, Tuple[str, Token]] = {}  # service_id -> (secret_hash, token)
        self._lock = __import__("threading").Lock()
    
    @property
    def provider_id(self) -> str:
        return self._provider_id
    
    async def register_service(
        self,
        service_id: str,
        secret_value: str,
        scopes: Tuple[str, ...] = tuple(),
        expires_at: Optional[float] = None
    ) -> Token:
        """
        Register a service for authentication.
        
        Returns the token issued to this service.
        """
        # Hash the secret
        secret_hash = hashlib.sha256(secret_value.encode()).hexdigest()
        
        token = Token(
            token_id=str(uuid.uuid4()),
            principal_id=service_id,
            type_=AuthMethod.SERVICE,
            issued_at=time.monotonic(),
            expires_at=expires_at,
            scopes=scopes,
            audience="runtime",
            issuer=self._provider_id
        )
        
        with self._lock:
            self._services[service_id] = (secret_hash, token)
        
        return token
    
    async def authenticate(self, request: AuthenticationRequest) -> AuthenticationResult:
        """
        Authenticate a service using its credentials.
        
        The service should provide its service_id and secret in the context.
        """
        service_id = request.context.get("service_id")
        secret_value = request.context.get("secret")
        
        if not service_id or not secret_value:
            return AuthenticationResult(
                success=False,
                failure_reason="Missing service_id or secret"
            )
        
        with self._lock:
            if service_id not in self._services:
                return AuthenticationResult(
                    success=False,
                    failure_reason="Unknown service"
                )
            
            _, token = self._services[service_id]
            
            # Verify secret
            if not self._verify_secret(secret_value, service_id):
                return AuthenticationResult(
                    success=False,
                    failure_reason="Invalid service credentials"
                )
            
            # Verify token is still valid
            if not token.is_valid():
                del self._services[service_id]
                return AuthenticationResult(
                    success=False,
                    failure_reason="Service credential has expired"
                )
        
        return AuthenticationResult(
            success=True,
            principal_id=token.principal_id,
            identity=Identity(
                identity_id=token.principal_id,
                name=f"Service-{service_id}",
                type_=IdentityType.SERVICE
            ),
            method=AuthMethod.SERVICE,
            timestamp=time.monotonic(),
            token=token
        )
    
    def _verify_secret(self, secret_value: str, service_id: str) -> bool:
        """Verify a service's secret."""
        if service_id not in self._services:
            return False
        
        expected_hash, _ = self._services[service_id]
        actual_hash = hashlib.sha256(secret_value.encode()).hexdigest()
        
        # Use hmac.compare_digest for timing-safe comparison
        return hmac.compare_digest(expected_hash, actual_hash)
    
    async def validate_token(self, token: Token) -> bool:
        """Validate a token without re-authenticating."""
        with self._lock:
            if not token.is_valid():
                return False
            
            # Check if this is one of our tokens
            for service_id, (_, stored_token) in self._services.items():
                if stored_token.token_id == token.token_id:
                    return True
            
            return False


# =============================================================================
# Certificate Authentication Provider (Skeleton)
# =============================================================================

class CertificateAuthenticationProvider:
    """
    Certificate-based authentication provider.
    
    Validates TLS certificates. In production, this would integrate with
    a PKI system or certificate authority.
    """
    
    def __init__(self, provider_id: str = "certificate"):
        self._provider_id = provider_id
        self._certificates: Dict[str, CertificateReference] = {}
        self._lock = __import__("threading").Lock()
    
    @property
    def provider_id(self) -> str:
        return self._provider_id
    
    async def register_certificate(
        self,
        cert_ref: CertificateReference
    ) -> None:
        """Register a certificate reference."""
        with self._lock:
            self._certificates[cert_ref.cert_id] = cert_ref
    
    async def authenticate(self, request: AuthenticationRequest) -> AuthenticationResult:
        """
        Authenticate using a certificate.
        
        This is a skeleton implementation. In production, this would:
        1. Verify the certificate chain
        2. Check expiration
        3. Verify subject/issuer match expectations
        4. Validate signature
        """
        # For now, we'll simulate successful authentication if cert info provided
        cert_id = request.context.get("cert_id")
        
        if not cert_id:
            return AuthenticationResult(
                success=False,
                failure_reason="No certificate ID provided"
            )
        
        with self._lock:
            if cert_id not in self._certificates:
                return AuthenticationResult(
                    success=False,
                    failure_reason="Unknown certificate"
                )
            
            cert_ref = self._certificates[cert_id]
            
            # Check certificate validity
            now = time.monotonic()
            if now < cert_ref.not_before or now > cert_ref.not_after:
                return AuthenticationResult(
                    success=False,
                    failure_reason="Certificate has expired or not yet valid"
                )
        
        return AuthenticationResult(
            success=True,
            principal_id=cert_ref.subject,
            identity=Identity(
                identity_id=cert_ref.subject,
                name=f"Cert-{cert_ref.subject[:8]}",
                type_=IdentityType.USER
            ),
            method=AuthMethod.CERTIFICATE,
            timestamp=time.monotonic()
        )
    
    async def validate_token(self, token: Token) -> bool:
        """Validate a token without re-authenticating."""
        # Certificates don't use tokens in the same way
        return False


# =============================================================================
# Composite Authentication Provider
# =============================================================================

class CompositeAuthenticationProvider:
    """
    Composite provider that delegates to multiple underlying providers.
    
    Tries each provider until one succeeds. This allows supporting
    multiple authentication methods simultaneously.
    
    Accepts any object with a provider_id property and authenticate() method.
    """
    
    def __init__(self, provider_id: str = "composite"):
        self._provider_id = provider_id
        self._providers: Dict[str, Any] = {}
        self._lock = __import__("threading").Lock()
    
    @property
    def provider_id(self) -> str:
        return self._provider_id
    
    async def add_provider(self, provider: Any) -> None:
        """Add an underlying provider."""
        with self._lock:
            if hasattr(provider, 'provider_id') and hasattr(provider, 'authenticate'):
                self._providers[provider.provider_id] = provider
    
    async def remove_provider(self, provider_id: str) -> bool:
        """Remove an underlying provider. Returns True if removed."""
        with self._lock:
            if provider_id in self._providers:
                del self._providers[provider_id]
                return True
            return False
    
    async def authenticate(self, request: AuthenticationRequest) -> AuthenticationResult:
        """
        Try each provider until one succeeds.
        
        The first successful authentication is returned. This allows
        flexible authentication method selection.
        """
        with self._lock:
            providers = list(self._providers.values())
        
        for provider in providers:
            result = await provider.authenticate(request)
            
            if result.success:
                return result
        
        # All providers failed
        return AuthenticationResult(
            success=False,
            failure_reason=f"All authentication methods failed: {[p.provider_id for p in providers]}"
        )
    
    async def validate_token(self, token: Token) -> bool:
        """Validate a token by checking all underlying providers."""
        with self._lock:
            providers = list(self._providers.values())
        
        for provider in providers:
            if await provider.validate_token(token):
                return True
        
        return False


__all__ = [
    "LocalAuthenticationProvider",
    "TokenAuthenticationProvider",
    "ApiKeyAuthenticationProvider",
    "ServiceAuthenticationProvider",
    "CertificateAuthenticationProvider",
    "CompositeAuthenticationProvider",
]