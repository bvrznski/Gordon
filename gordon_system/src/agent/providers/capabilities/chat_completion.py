# Chat Completion Provider Interface
# ====================================
"""
Chat completion provider interface for language models.

This defines the contract for providers that support conversational AI
interactions through chat-based interfaces.
"""

from dataclasses import dataclass, field
from typing import Protocol, List, Optional, Dict, Any, AsyncIterator
from enum import Enum

from ..exceptions import ProviderError, ProviderRequestError
from ..types import CapabilityDeclaration


class MessageRole(Enum):
    """Roles in a message exchange."""
    SYSTEM = "system"
    USER = "user"
    ASSISTANT = "assistant"
    FUNCTION = "function"  # For tool/function calling results


@dataclass(frozen=True)
class ChatMessage:
    """
    A single chat message.
    
    Args:
        role: The sender's role (system, user, assistant, function)
        content: Text content of the message
        name: Optional name for function messages or multi-turn context
        tool_call_id: Optional ID for tool call responses
        tool_calls: Optional list of tool calls in this message
    """
    role: MessageRole
    content: str
    name: Optional[str] = None
    tool_call_id: Optional[str] = None
    tool_calls: List["ToolCall"] = field(default_factory=list)


@dataclass(frozen=True)
class ToolCall:
    """
    A tool call requested by the model.
    
    Args:
        id: Unique identifier for this tool call
        type: Type of tool (e.g., "function")
        function: Function name and arguments
    """
    id: str
    type: str = "function"
    function: Optional["ToolFunction"] = None


@dataclass(frozen=True)
class ToolFunction:
    """
    A function to be called.
    
    Args:
        name: Function name
        arguments: JSON string of function arguments
    """
    name: str
    arguments: str


@dataclass(frozen=True)
class ChatCompletionRequest:
    """
    Request for chat completion.
    
    Args:
        messages: Conversation history
        system_prompt: Optional system instruction (alternative to system message)
        temperature: Sampling temperature (0.0 = deterministic, 1.0 = random)
        max_tokens: Maximum output tokens
        top_p: Nucleus sampling parameter
        stop_sequences: List of sequences that stop generation
        tools: Available tool definitions for tool calling
        tool_choice: Tool selection strategy ("auto", "none", or specific name)
        stream: Whether to stream results
        model: Optional model override
    """
    messages: List[ChatMessage]
    system_prompt: Optional[str] = None
    temperature: float = 0.7
    max_tokens: Optional[int] = None
    top_p: float = 1.0
    stop_sequences: List[str] = field(default_factory=list)
    tools: List["ToolDefinition"] = field(default_factory=list)
    tool_choice: Optional[str] = None
    stream: bool = False
    model: Optional[str] = None


@dataclass(frozen=True)
class ToolDefinition:
    """
    A callable tool definition.
    
    Args:
        type: Tool type (e.g., "function")
        function: Function details including name, description, and parameters
    """
    type: str = "function"
    function: Optional["ToolFunctionDefinition"] = None


@dataclass(frozen=True)
class ToolFunctionDefinition:
    """
    A function tool definition.
    
    Args:
        name: Function name
        description: Description of what the function does
        parameters: JSON schema for function arguments
        required: List of required parameter names
    """
    name: str
    description: Optional[str] = None
    parameters: Dict[str, Any] = field(default_factory=dict)
    required: List[str] = field(default_factory=list)


@dataclass(frozen=True)
class ChatCompletionChoice:
    """
    A single completion choice.
    
    Args:
        message: The assistant's response message
        finish_reason: Why generation stopped (stop, length, tool_calls, etc.)
        index: Position of this choice in the response
        logprobs: Log probabilities if requested
        tool_calls: Any tool calls made by the model
    """
    message: ChatMessage
    finish_reason: str = "stop"
    index: int = 0
    logprobs: Optional[Dict[str, Any]] = None
    tool_calls: List[ToolCall] = field(default_factory=list)


@dataclass(frozen=True)
class ChatCompletionUsage:
    """
    Token usage statistics.
    
    Args:
        prompt_tokens: Tokens in the input
        completion_tokens: Tokens in the output
        total_tokens: Total tokens used
        reasoning_tokens: Optional reasoning tokens (e.g., for some models)
    """
    prompt_tokens: int
    completion_tokens: int
    total_tokens: int
    reasoning_tokens: Optional[int] = None


@dataclass(frozen=True)
class ChatCompletionResponse:
    """
    Complete chat completion response.
    
    Args:
        id: Response identifier (for tracing)
        choices: List of completion choices
        created: Timestamp of creation
        model: Model that generated this response
        system_fingerprint: System fingerprint for version tracking
        usage: Token usage statistics
        service_tier: Optional service tier info
        system_message: Optional system message from provider
    """
    id: str
    choices: List[ChatCompletionChoice]
    created: int  # Unix timestamp
    model: str
    system_fingerprint: Optional[str] = None
    usage: Optional[ChatCompletionUsage] = None
    service_tier: Optional[str] = None
    system_message: Optional[str] = None


class ChatCompletionProvider(Protocol):
    """
    Protocol for chat completion providers.
    
    Provides the ability to generate conversational responses from language models.
    
    Usage:
        # Create a provider
        provider = MyLLMProvider(config)
        
        # Prepare messages
        messages = [
            ChatMessage(role=MessageRole.SYSTEM, content="You are a helpful assistant."),
            ChatMessage(role=MessageRole.USER, content="Hello!")
        ]
        
        # Get completion
        response = await provider.chat_completion(
            ChatCompletionRequest(messages=messages)
        )
    """
    
    async def chat_completion(
        self,
        request: ChatCompletionRequest
    ) -> ChatCompletionResponse:
        """
        Generate a chat completion.
        
        Args:
            request: The chat completion request
            
        Returns:
            Complete chat completion response
            
        Raises:
            ProviderNotReadyError: If provider is not ready
            ProviderRequestError: If request is invalid
            ProviderCapabilityError: If tool calling not supported when requested
        """
        ...
    
    async def chat_completion_stream(
        self,
        request: ChatCompletionRequest
    ) -> AsyncIterator[ChatCompletionResponse]:
        """
        Stream a chat completion token by token.
        
        Args:
            request: The chat completion request
            
        Yields:
            Partial responses as they arrive
            
        Raises:
            ProviderNotReadyError: If provider is not ready
            ProviderRequestError: If request is invalid
            ProviderCapabilityError: If streaming not supported
        """
        ...
    
    @property
    def capabilities(self) -> CapabilityDeclaration:
        """Return capabilities declaration."""
        ...


# Request validation utilities

def validate_chat_request(request: ChatCompletionRequest) -> List[str]:
    """
    Validate a chat completion request.
    
    Returns:
        List of validation errors (empty if valid)
    """
    errors = []
    
    # Check messages exist and are non-empty
    if not request.messages:
        errors.append("At least one message is required")
        return errors
    
    # Check message order (system should come first, then alternating user/assistant)
    expected_role: Optional[MessageRole] = None
    for i, msg in enumerate(request.messages):
        if i == 0 and msg.role not in (MessageRole.SYSTEM, MessageRole.USER):
            errors.append(f"First message must be system or user role, got {msg.role.value}")
        
        # Check for consecutive same-role messages
        if expected_role is not None and msg.role != expected_role:
            errors.append(
                f"Expected {expected_role.value} role at position {i}, "
                f"got {msg.role.value}"
            )
        
        # Update expected next role
        if msg.role == MessageRole.USER:
            expected_role = MessageRole.ASSISTANT
        elif msg.role == MessageRole.ASSISTANT:
            expected_role = MessageRole.USER
    
    # Validate temperature range
    if not (0.0 <= request.temperature <= 2.0):
        errors.append(f"Temperature must be between 0 and 2, got {request.temperature}")
    
    # Validate max_tokens if specified
    if request.max_tokens is not None and request.max_tokens <= 0:
        errors.append(f"max_tokens must be positive, got {request.max_tokens}")
    
    return errors


__all__ = [
    # Enums
    "MessageRole",
    
    # Data classes - Messages
    "ChatMessage",
    "ToolCall",
    "ToolFunction",
    
    # Data classes - Requests
    "ChatCompletionRequest",
    "ToolDefinition",
    "ToolFunctionDefinition",
    
    # Data classes - Responses
    "ChatCompletionChoice",
    "ChatCompletionUsage",
    "ChatCompletionResponse",
    
    # Protocols
    "ChatCompletionProvider",
    
    # Validation
    "validate_chat_request",
]