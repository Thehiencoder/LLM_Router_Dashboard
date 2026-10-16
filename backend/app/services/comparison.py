import asyncio
import time
from typing import Dict, List, Optional
from app.config import settings
from app.schemas.comparison import (
    CompareRequest,
    CompareResponse,
    LLMResult,
    TokenMetrics,
    CostMetrics,
)
from app.providers.base import BaseLLMProvider
from app.providers.openai_provider import OpenAIProvider
from app.providers.anthropic_provider import AnthropicProvider
from app.providers.gemini_provider import GeminiProvider
from app.providers.mock_provider import MockProvider
from app.services.pricing import PricingService, pricing_service


class ComparisonService:
    """
    Orchestrates concurrent multi-model inference benchmarking.
    
    Guarantees:
    - Non-blocking concurrent query execution via asyncio.
    - Fault isolation: individual model failures never abort neighboring models.
    - Accurate wall-clock timing via time.perf_counter().
    - Automated cost enrichment through PricingService.
    """

    def __init__(
        self,
        provider_registry: Optional[Dict[str, BaseLLMProvider]] = None,
        pricing: Optional[PricingService] = None,
    ):
        self.pricing = pricing or pricing_service

        if provider_registry is not None:
            self.providers = provider_registry
        else:
            self.providers = self._init_default_providers()

    def _init_default_providers(self) -> Dict[str, BaseLLMProvider]:
        """Initializes vendor adapters with environment keys, using MockProvider when in mock mode or keys missing."""
        if settings.mock_mode:
            return {
                "openai": MockProvider("openai"),
                "anthropic": MockProvider("anthropic"),
                "gemini": MockProvider("gemini"),
            }

        providers: Dict[str, BaseLLMProvider] = {}

        # OpenAI Adapter (or Mock fallback if key missing)
        if settings.openai_api_key:
            providers["openai"] = OpenAIProvider(api_key=settings.openai_api_key)
        else:
            providers["openai"] = MockProvider("openai")

        # Anthropic Adapter (or Mock fallback if key missing)
        if settings.anthropic_api_key:
            providers["anthropic"] = AnthropicProvider(api_key=settings.anthropic_api_key)
        else:
            providers["anthropic"] = MockProvider("anthropic")

        # Gemini Adapter (or Mock fallback if key missing)
        if settings.gemini_api_key:
            providers["gemini"] = GeminiProvider(api_key=settings.gemini_api_key)
        else:
            providers["gemini"] = MockProvider("gemini")

        return providers

    async def _safe_execute(
        self,
        provider: BaseLLMProvider,
        model: str,
        prompt: str,
        system_prompt: Optional[str],
        temperature: float,
        max_tokens: int,
    ) -> LLMResult:
        """
        Executes an inference request within an isolated error-shielding boundary.
        Any exception thrown by an adapter is caught and converted to an error result.
        """
        task_start = time.perf_counter()
        try:
            result = await provider.generate(
                prompt=prompt,
                model=model,
                system_prompt=system_prompt,
                temperature=temperature,
                max_tokens=max_tokens,
            )

            # Enrich result with pricing metrics
            if result.status == "success":
                result.cost = self.pricing.calculate_cost(
                    provider=result.provider,
                    model=result.model,
                    input_tokens=result.tokens.input_tokens,
                    output_tokens=result.tokens.output_tokens,
                    reasoning_tokens=result.tokens.reasoning_tokens or 0,
                )
            return result
        except Exception as exc:
            elapsed_ms = (time.perf_counter() - task_start) * 1000.0
            return LLMResult(
                provider=provider.provider_name,
                model=model,
                text=None,
                tokens=TokenMetrics(),
                cost=CostMetrics(),
                latency_ms=round(elapsed_ms, 2),
                error=f"{type(exc).__name__}: {str(exc)}",
                status="error",
            )

    async def run_comparison(self, request: CompareRequest) -> CompareResponse:
        """
        Validates request and concurrently queries all selected models.
        """
        master_start = time.perf_counter()

        tasks = []
        for item in request.models:
            provider = self.providers.get(item.provider)
            if not provider:
                # If unknown provider, wrap with mock or return error
                provider = MockProvider(item.provider)

            tasks.append(
                self._safe_execute(
                    provider=provider,
                    model=item.model,
                    prompt=request.prompt,
                    system_prompt=request.system_prompt,
                    temperature=request.temperature or 0.7,
                    max_tokens=request.max_tokens or 2048,
                )
            )

        # Run concurrently using Python 3.13 asyncio
        results: List[LLMResult] = await asyncio.gather(*tasks)
        total_latency_ms = (time.perf_counter() - master_start) * 1000.0

        return CompareResponse(
            prompt=request.prompt,
            total_latency_ms=round(total_latency_ms, 2),
            results=results,
        )


# Default singleton instance
comparison_service = ComparisonService()
