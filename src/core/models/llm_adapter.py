"""
Adaptador abstracto para interactuar con modelos de lenguaje (APIs reales o simuladores locales).
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
from pydantic import BaseModel, Field


class LLMResponse(BaseModel):
    content: str
    tokens_prompt: int
    tokens_completion: int
    latency_ms: float
    model_name: str
    metadata: Dict[str, Any] = Field(default_factory=dict)


class BaseLLMAdapter(ABC):
    """Contrato base para cualquier motor de inferencia conectado a ACRA."""

    def __init__(self, model_name: str, temperature: float = 0.0):
        self.model_name = model_name
        self.temperature = temperature

    @abstractmethod
    def generate(self, prompt: str, **kwargs: Any) -> LLMResponse:
        """Genera una respuesta a partir de un prompt."""
        pass
