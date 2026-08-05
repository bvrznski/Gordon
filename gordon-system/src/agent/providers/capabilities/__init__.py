# Capability Protocols - Provider Interfaces
# ============================================
"""
Capability protocols define the interfaces that providers must implement.

Each capability protocol covers a specific type of external functionality:
- Chat completion (LLM)
- Embeddings
- Vision-language processing (VLM)
- OCR
- Speech recognition (ASR)
- Speech synthesis (TTS)
- And more...

Usage:
    from gordon_system.src.agent.providers.capabilities import chat_completion
    
    # Use the protocol for type hints
    async def use_provider(provider: ChatCompletionProvider):
        response = await provider.chat_completion(request)
"""

# Import all capability protocols
from .chat_completion import (
    MessageRole,
    ChatMessage,
    ToolCall,
    ToolFunction,
    ChatCompletionRequest,
    ToolDefinition,
    ToolFunctionDefinition,
    ChatCompletionChoice,
    ChatCompletionUsage,
    ChatCompletionResponse,
    ChatCompletionProvider,
    validate_chat_request,
)

__all__ = [
    # chat_completion
    "MessageRole",
    "ChatMessage",
    "ToolCall",
    "ToolFunction",
    "ChatCompletionRequest",
    "ToolDefinition",
    "ToolFunctionDefinition",
    "ChatCompletionChoice",
    "ChatCompletionUsage",
    "ChatCompletionResponse",
    "ChatCompletionProvider",
    "validate_chat_request",
]