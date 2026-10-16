import asyncio
import time
from typing import Optional
from app.providers.base import BaseLLMProvider
from app.schemas.comparison import LLMResult, TokenMetrics, CostMetrics


class MockProvider(BaseLLMProvider):
    """
    Simulation provider for offline development, UI benchmarking, and automated testing.
    Produces model-characteristic responses, realistic token usage, and simulated latencies.
    """

    def __init__(self, target_provider: str):
        self._provider = target_provider

    @property
    def provider_name(self) -> str:
        return self._provider

    async def generate(
        self,
        prompt: str,
        model: str,
        system_prompt: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 2048,
    ) -> LLMResult:
        start_time = time.perf_counter()

        # Simulate provider-specific network latencies
        if self._provider == "gemini":
            simulated_delay = 0.35 + (len(prompt) % 5) * 0.05
        elif self._provider == "openai":
            simulated_delay = 0.65 + (len(prompt) % 7) * 0.08
        else:  # anthropic
            simulated_delay = 0.85 + (len(prompt) % 6) * 0.07

        await asyncio.sleep(simulated_delay)
        elapsed_ms = (time.perf_counter() - start_time) * 1000.0

        # Generate realistic markdown content tailored to the requested model
        if self._provider == "gemini":
            text = (
                f"### Analysis from {model} (Google)\n\n"
                f"Here is a streamlined solution for your inquiry:\n\n"
                f"1. **Core Concept:** Addressing `{prompt[:40]}...` with optimal performance.\n"
                f"2. **Implementation Strategy:** High throughput, low latency architecture.\n"
                f"3. **Efficiency:** Utilizes linear context scaling with minimal compute footprint.\n\n"
                f"```python\n"
                f"# Gemini High-Efficiency Routine\n"
                f"def process_query(prompt: str) -> dict:\n"
                f"    return {{\n"
                f"        'status': 'optimized',\n"
                f"        'model': '{model}',\n"
                f"        'free_tier': True\n"
                f"    }}\n"
                f"```\n"
            )
            in_tokens = max(15, len(prompt.split()) * 2)
            out_tokens = 145
            reasoning_tokens = 0

        elif self._provider == "anthropic":
            text = (
                f"> *[Claude Thought Stream]*\n"
                f"> 1. Deconstructing user request: \"{prompt[:35]}...\"\n"
                f"> 2. Synthesizing structural nuances and safety constraints.\n"
                f"> 3. Structuring clear, verifiable output with full explanatory depth.\n\n"
                f"### Comprehensive Evaluation — {model}\n\n"
                f"To tackle this effectively, consider the trade-offs involved:\n\n"
                f"- **Precision:** Maintaining sound architectural invariants.\n"
                f"- **Resilience:** Gracefully shielding errors across distributed boundaries.\n"
                f"- **Scalability:** Ensuring asynchronous operations avoid head-of-line blocking.\n\n"
                f"```typescript\n"
                f"// Claude Robust Orchestrator Pattern\n"
                f"export async function benchmark<T>(task: () => Promise<T>): Promise<T> {{\n"
                f"  const start = performance.now();\n"
                f"  try {{\n"
                f"    return await task();\n"
                f"  }} finally {{\n"
                f"    console.info(`Completed in ${{performance.now() - start}}ms`);\n"
                f"  }}\n"
                f"}}\n"
                f"```\n"
            )
            in_tokens = max(18, len(prompt.split()) * 2)
            out_tokens = 220
            reasoning_tokens = 45

        else:  # openai
            text = (
                f"### Resolution via {model} (OpenAI)\n\n"
                f"Below is a direct, robust implementation addressing your request:\n\n"
                f"- **Step 1:** Validate prompt schemas against strictly typed contracts.\n"
                f"- **Step 2:** Execute asynchronous coroutines concurrently with TaskGroup.\n"
                f"- **Step 3:** Normalize usage metadata and compute unit cost per million tokens.\n\n"
                f"```python\n"
                f"# OpenAI Next-Gen Verification Routine\n"
                f"class ModelBenchmark:\n"
                f"    def __init__(self, model_name: str = '{model}'):\n"
                f"        self.model = model_name\n"
                f"        self.verified = True\n"
                f"```\n"
            )
            in_tokens = max(20, len(prompt.split()) * 2)
            out_tokens = 185
            reasoning_tokens = 60

        return LLMResult(
            provider=self.provider_name,
            model=model,
            text=text,
            tokens=TokenMetrics(
                input_tokens=in_tokens,
                output_tokens=out_tokens,
                total_tokens=in_tokens + out_tokens,
                reasoning_tokens=reasoning_tokens,
            ),
            cost=CostMetrics(),  # Populated by pricing service
            latency_ms=round(elapsed_ms, 2),
            status="success",
        )
