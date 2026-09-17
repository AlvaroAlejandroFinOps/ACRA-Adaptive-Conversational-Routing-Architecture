"""ACRA Providers Package.

Exposes provider interfaces, protocols, and concrete adapters.
"""

from src.core.providers.anthropic import AnthropicAdapter
from src.core.providers.base import (
    ProviderAdapter,
    ProviderResponse,
)
from src.core.providers.google import GoogleGenAIAdapter
from src.core.providers.local import LocalAdapter
from src.core.providers.openai import OpenAIAdapter
from src.core.providers.stub import (
    DeterministicStubProvider,
)

__all__ = [
    "ProviderAdapter",
    "ProviderResponse",
    "DeterministicStubProvider",
    "GoogleGenAIAdapter",
    "AnthropicAdapter",
    "OpenAIAdapter",
    "LocalAdapter",
]

