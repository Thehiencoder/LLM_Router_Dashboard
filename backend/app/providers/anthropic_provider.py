import time
from typing import Optional
from app.providers.base import BaseLLMProvider
from app.schemas.comparison import LLMResult, TokenMetrics, CostMetrics

try:
    from anthropic import AsyncAnthropic, APIError, AuthenticationError, RateLimitError
    ANTHROPIC_AVAILABLE = True
except ImportError:
    ANTHROPIC_AVAILABLE = False


class AnthropicProvider(BaseLLMProvider):
    """Adapter for Anthropic models (claude-3-7-sonnet, claude-3-7-sonnet-thought, claude-4-sonnet)."""

    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key
        self.client = AsyncAnthropic(api_key=api_key) if api_key and ANTHROPIC_AVAILABLE else None

    @property
    def provider_name(self) -> str:
        return "anthropic"

    def _resolve_model_id(self, model: str) -> tuple[str, bool]:
        """Resolves internal Anthropic model ID and whether thinking mode is requested."""
        m = model.lower()
        if "thought" in m or "thinking" in m:
            # claude-3-7-sonnet with thinking enabled
            return "claude-3-7-sonnet-20250219", True
        elif "3-7" in m or "3.7" in m:
            return "claude-3-7-sonnet-20250219", False
        elif "4" in m:
            return "claude-3-7-sonnet-20250219", False  # Fallback to current 3.7 flagship if 4 is preview
        return model, False

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
                error="Anthropic API key is missing. Set ANTHROPIC_API_KEY in .env or enable MOCK_MODE.",
                status="error",
            )

        start_time = time.perf_counter()
        actual_model, enable_thinking = self._resolve_model_id(model)

        kwargs = {
            "model": actual_model,
            "max_tokens": max(max_tokens, 1024),
            "messages": [{"role": "user", "content": prompt}],
        }

        if system_prompt:
            kwargs["system"] = system_prompt

        # Configure thinking parameters if requested
        if enable_thinking:
            budget = min(1024, max(512, max_tokens // 2))
            kwargs["thinking"] = {"type": "enabled", "budget_tokens": budget}
            # When thinking is enabled in Anthropic, temperature must be 1.0 or omitted
        else:
            kwargs["temperature"] = temperature

        try:
            response = await self.client.messages.create(**kwargs)
            elapsed_ms = (time.perf_counter() - start_time) * 1000.0

            # Extract text blocks and thinking blocks
            text_blocks = []
            thinking_blocks = []
            for block in response.content:
                if block.type == "text":
                    text_blocks.append(block.text)
                elif block.type == "thinking":
                    thinking_blocks.append(getattr(block, "thinking", ""))

            combined_text = "\n\n".join(text_blocks)
            if thinking_blocks:
                combined_text = f"> *[Claude Thought Process]*\n> " + "\n> ".join(
                    "\n".join(thinking_blocks).splitlines()
                ) + f"\n\n{combined_text}"

            usage = response.usage
            in_tokens = usage.input_tokens if usage else 0
            out_tokens = usage.output_tokens if usage else 0

            return LLMResult(
                provider=self.provider_name,
                model=model,
                text=combined_text,
                tokens=TokenMetrics(
                    input_tokens=in_tokens,
                    output_tokens=out_tokens,
                    total_tokens=in_tokens + out_tokens,
                    reasoning_tokens=len(thinking_blocks),
                ),
                cost=CostMetrics(),  # Populated by pricing service
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
                error=f"Anthropic Error: {str(exc)}",
                status="error",
            )
