from abc import ABC, abstractmethod
from typing import Optional
from app.schemas.comparison import LLMResult


class BaseLLMProvider(ABC):
    """
    Abstract Common Provider Interface for LLM Model Adapters.
    
    Every vendor adapter (OpenAI, Anthropic, Gemini, Mock) implements this interface,
    normalizing provider-specific responses into the common LLMResult schema.
    """

    @property
    @abstractmethod
    def provider_name(self) -> str:
        """Normalized vendor identifier: 'openai', 'anthropic', 'gemini'"""
        pass

    @abstractmethod
    async def generate(
        self,
        prompt: str,
        model: str,
        system_prompt: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 2048,
    ) -> LLMResult:
        """
        Execute an asynchronous completion request against the provider SDK.
        
        Must:
        - Measure elapsed latency using time.perf_counter().
        - Normalize raw provider tokens into TokenMetrics.
        - Catch vendor-specific exceptions internally and return LLMResult(status='error', error=...).
        """
        pass
