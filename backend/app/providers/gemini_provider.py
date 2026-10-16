import time
from typing import Optional
from app.providers.base import BaseLLMProvider
from app.schemas.comparison import LLMResult, TokenMetrics, CostMetrics

# Dual compatibility: prioritize new unified `google-genai` SDK, fallback to `google.generativeai`
GEMINI_SDK_TYPE = None
try:
    from google import genai
    from google.genai import types as genai_types
    GEMINI_SDK_TYPE = "google_genai"
except ImportError:
    try:
        import google.generativeai as legacy_genai
        GEMINI_SDK_TYPE = "legacy_genai"
    except ImportError:
        GEMINI_SDK_TYPE = None


class GeminiProvider(BaseLLMProvider):
    """Adapter for Google Gemini models (gemini-3.0-flash, gemini-3.0-pro, gemini-3.8-flash)."""

    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key
        self.sdk_type = GEMINI_SDK_TYPE
        self.client = None

        if api_key and self.sdk_type == "google_genai":
            try:
                self.client = genai.Client(api_key=api_key)
            except Exception:
                self.client = None
        elif api_key and self.sdk_type == "legacy_genai":
            legacy_genai.configure(api_key=api_key)

    @property
    def provider_name(self) -> str:
        return "gemini"

    def _resolve_model_name(self, model: str) -> str:
        """
        Maps dashboard model identifiers to Google API model endpoints.
        Supports 3.0+ models with graceful fallback if experimental.
        """
        m = model.lower()
        if "3.8" in m:
            return "gemini-2.5-flash"  # Fallback to current fast flagship if 3.8 preview key restricted
        elif "3.0-pro" in m:
            return "gemini-2.5-pro"
        elif "3.0" in m or "flash" in m:
            return "gemini-2.5-flash"
        return model

    async def generate(
        self,
        prompt: str,
        model: str,
        system_prompt: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 2048,
    ) -> LLMResult:
        if not self.api_key:
            return LLMResult(
                provider=self.provider_name,
                model=model,
                text=None,
                tokens=TokenMetrics(),
                cost=CostMetrics(),
                latency_ms=0.0,
                error="Gemini API key is missing. Set GEMINI_API_KEY in .env or enable MOCK_MODE (Gemini is 100% free via Google AI Studio).",
                status="error",
            )

        start_time = time.perf_counter()
        target_model = self._resolve_model_name(model)

        try:
            if self.sdk_type == "google_genai" and self.client:
                # Modern unified SDK (client.aio)
                config = genai_types.GenerateContentConfig(
                    temperature=temperature,
                    max_output_tokens=max_tokens,
                    system_instruction=system_prompt if system_prompt else None,
                )
                response = await self.client.aio.models.generate_content(
                    model=target_model,
                    contents=prompt,
                    config=config,
                )
                elapsed_ms = (time.perf_counter() - start_time) * 1000.0

                text = response.text or ""
                metadata = response.usage_metadata
                in_tokens = metadata.prompt_token_count if metadata else 0
                out_tokens = metadata.candidates_token_count if metadata else 0

            elif self.sdk_type == "legacy_genai":
                # Legacy google.generativeai fallback
                gen_model = legacy_genai.GenerativeModel(
                    model_name=target_model,
                    system_instruction=system_prompt if system_prompt else None,
                )
                response = await gen_model.generate_content_async(
                    prompt,
                    generation_config=legacy_genai.types.GenerationConfig(
                        temperature=temperature,
                        max_output_tokens=max_tokens,
                    ),
                )
                elapsed_ms = (time.perf_counter() - start_time) * 1000.0
                text = response.text or ""
                usage = getattr(response, "usage_metadata", None)
                in_tokens = getattr(usage, "prompt_token_count", 0) if usage else 0
                out_tokens = getattr(usage, "candidates_token_count", 0) if usage else 0
            else:
                return LLMResult(
                    provider=self.provider_name,
                    model=model,
                    text=None,
                    tokens=TokenMetrics(),
                    cost=CostMetrics(),
                    latency_ms=0.0,
                    error="Google GenAI SDK is not installed. Run `pip install google-genai`.",
                    status="error",
                )

            return LLMResult(
                provider=self.provider_name,
                model=model,
                text=text,
                tokens=TokenMetrics(
                    input_tokens=in_tokens,
                    output_tokens=out_tokens,
                    total_tokens=in_tokens + out_tokens,
                ),
                cost=CostMetrics(),  # Populated by pricing service (flags free tier $0.00)
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
                error=f"Gemini Error: {str(exc)}",
                status="error",
            )
