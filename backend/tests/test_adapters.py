import pytest
from app.providers.mock_provider import MockProvider
from app.providers.openai_provider import OpenAIProvider
from app.providers.anthropic_provider import AnthropicProvider
from app.providers.gemini_provider import GeminiProvider


@pytest.mark.asyncio
async def test_mock_provider_generation():
    """Verify MockProvider generates well-formed LLMResult with realistic metadata."""
    provider = MockProvider("gemini")
    result = await provider.generate(
        prompt="Explain quantum entanglement",
        model="gemini-3.0-flash",
    )
    assert result.status == "success"
    assert result.provider == "gemini"
    assert result.model == "gemini-3.0-flash"
    assert len(result.text) > 0
    assert result.tokens.input_tokens > 0
    assert result.tokens.output_tokens > 0
    assert result.latency_ms > 0.0
    assert result.error is None


@pytest.mark.asyncio
async def test_missing_api_keys_safe_error():
    """Verify live providers return clean LLMResult error instead of crashing if keys are missing."""
    openai_p = OpenAIProvider(api_key=None)
    res_oai = await openai_p.generate(prompt="Test", model="o3-mini")
    assert res_oai.status == "error"
    assert "missing" in res_oai.error.lower()

    anthropic_p = AnthropicProvider(api_key=None)
    res_ant = await anthropic_p.generate(prompt="Test", model="claude-3-7-sonnet")
    assert res_ant.status == "error"
    assert "missing" in res_ant.error.lower()

    gemini_p = GeminiProvider(api_key=None)
    res_gem = await gemini_p.generate(prompt="Test", model="gemini-3.0-flash")
    assert res_gem.status == "error"
    assert "missing" in res_gem.error.lower()


def test_openai_reasoning_model_detection():
    """Verify reasoning models (o1, o3, o3-mini) are detected properly."""
    provider = OpenAIProvider(api_key="sk-dummy")
    assert provider._is_reasoning_model("o1") is True
    assert provider._is_reasoning_model("o3-mini") is True
    assert provider._is_reasoning_model("gpt-4.5-preview") is False
