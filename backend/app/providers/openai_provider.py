import time
from typing import Optional
from app.providers.base import BaseLLMProvider
from app.schemas.comparison import LLMResult, TokenMetrics, CostMetrics

try:
    from openai import AsyncOpenAI, APIError, AuthenticationError, RateLimitError
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False


class OpenAIProvider(BaseLLMProvider):
    """Adapter for OpenAI models (gpt-4.5-preview, o3-mini, o1)."""

    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key
        self.client = AsyncOpenAI(api_key=api_key) if api_key and OPENAI_AVAILABLE else None

    @property
    def provider_name(self) -> str:
        return "openai"

    def _is_reasoning_model(self, model: str) -> bool:
        """Check if model belongs to the o-series reasoning family (o1, o3, o3-mini)."""
        m = model.lower()
        return m.startswith("o1") or m.startswith("o3") or "reasoning" in m

    async def generate(
        self,
        prompt: str,
        model: str,
        system_prompt: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 2048,
    ) -> LLMResult:
        if not self.api_key or not self.client:
            return LLMResult(
                provider=self.provider_name,
                model=model,
                text=None,
                tokens=TokenMetrics(),
                cost=CostMetrics(),
                latency_ms=0.0,
                error="OpenAI API key is missing. Set OPENAI_API_KEY in .env or enable MOCK_MODE.",
                status="error",
            )

        start_time = time.perf_counter()
        is_reasoning = self._is_reasoning_model(model)

        # Build messages payload
        messages = []
        if system_prompt:
            # Reasoning models prefer 'developer' role for system instructions
            role = "developer" if is_reasoning else "system"
            messages.append({"role": role, "content": system_prompt})
        messages.append({"role": "user", "content": prompt})

        # Sanitize parameters: reasoning models disallow temperature and prefer max_completion_tokens
        kwargs = {"model": model, "messages": messages}
        if is_reasoning:
            kwargs["max_completion_tokens"] = max_tokens
        else:
            kwargs["temperature"] = temperature
            kwargs["max_tokens"] = max_tokens

        try:
            response = await self.client.chat.completions.create(**kwargs)
            elapsed_ms = (time.perf_counter() - start_time) * 1000.0

            content = response.choices[0].message.content or ""
            usage = response.usage

            # Extract standard and reasoning token counts
            in_tokens = usage.prompt_tokens if usage else 0
            out_tokens = usage.completion_tokens if usage else 0
            reasoning_tokens = 0
            if usage and hasattr(usage, "completion_tokens_details") and usage.completion_tokens_details:
                reasoning_tokens = getattr(usage.completion_tokens_details, "reasoning_tokens", 0) or 0

            return LLMResult(
                provider=self.provider_name,
                model=model,
                text=content,
                tokens=TokenMetrics(
                    input_tokens=in_tokens,
                    output_tokens=out_tokens,
                    total_tokens=in_tokens + out_tokens,
                    reasoning_tokens=reasoning_tokens,
                ),
                cost=CostMetrics(),  # Will be populated by pricing service
                latency_ms=round(elapsed_ms, 2),
                status="success",
            )
        except Exception as exc:
            elapsed_ms = (time.perf_counter() - start_time) * 1000.0
            return LLMResult(
                provider=self.provider_name,
                model=model,
                text=None,
                tokens=TokenMetrics(),
                cost=CostMetrics(),
                latency_ms=round(elapsed_ms, 2),
                error=f"OpenAI Error: {str(exc)}",
                status="error",
            )
