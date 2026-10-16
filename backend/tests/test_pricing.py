import pytest
from app.services.pricing import PricingService


@pytest.fixture
def pricing():
    return PricingService()


def test_o3_mini_cost_calculation(pricing):
    """Verify exact formula calculation on paid OpenAI reasoning model."""
    # o3-mini: $1.10 per 1M in, $4.40 per 1M out
    # 10,000 input tokens, 5,000 output tokens
    # Cost = (10,000 * 1.10 + 5,000 * 4.40) / 1,000,000 = (11,000 + 22,000) / 1,000,000 = 0.033
    cost = pricing.calculate_cost(
        provider="openai",
        model="o3-mini",
        input_tokens=10_000,
        output_tokens=5_000,
    )
    assert not cost.is_free_tier
    assert cost.actual_cost_usd == pytest.approx(0.033, abs=1e-5)
    assert cost.estimated_list_cost_usd == pytest.approx(0.033, abs=1e-5)
    assert cost.input_cost_usd == pytest.approx(0.011, abs=1e-5)
    assert cost.output_cost_usd == pytest.approx(0.022, abs=1e-5)


def test_gemini_flash_free_tier(pricing):
    """Verify Gemini AI Studio free tier returns $0.00 actual cost and accurate commercial list value."""
    # gemini-3.0-flash: $0.15 per 1M in, $0.60 per 1M out
    # 10,000 in, 5,000 out
    # List cost = (10,000 * 0.15 + 5,000 * 0.60) / 1,000,000 = (1,500 + 3,000) / 1,000,000 = 0.0045
    cost = pricing.calculate_cost(
        provider="gemini",
        model="gemini-3.0-flash",
        input_tokens=10_000,
        output_tokens=5_000,
    )
    assert cost.is_free_tier is True
    assert cost.actual_cost_usd == 0.0
    assert cost.estimated_list_cost_usd == pytest.approx(0.0045, abs=1e-5)
    assert cost.input_cost_usd == pytest.approx(0.0015, abs=1e-5)
    assert cost.output_cost_usd == pytest.approx(0.003, abs=1e-5)


def test_gemini_commercial_override(pricing):
    """Verify Gemini with paid tier override calculates non-zero actual invoice cost."""
    cost = pricing.calculate_cost(
        provider="gemini",
        model="gemini-3.0-flash",
        input_tokens=10_000,
        output_tokens=5_000,
        force_paid_tier=True,
    )
    assert cost.is_free_tier is False
    assert cost.actual_cost_usd == pytest.approx(0.0045, abs=1e-5)


def test_claude_3_7_sonnet(pricing):
    """Verify Claude 3.7 Sonnet pricing."""
    # claude-3-7-sonnet: $3.00 in, $15.00 out
    cost = pricing.calculate_cost(
        provider="anthropic",
        model="claude-3-7-sonnet",
        input_tokens=1_000,
        output_tokens=2_000,
    )
    expected_cost = (1000 * 3.0 + 2000 * 15.0) / 1_000_000
    assert cost.actual_cost_usd == pytest.approx(expected_cost, abs=1e-5)


def test_unknown_model_fallback(pricing):
    """Verify unknown model does not throw exception and uses reasonable fallback."""
    cost = pricing.calculate_cost(
        provider="openai",
        model="unreleased-gpt-future",
        input_tokens=500,
        output_tokens=500,
    )
    assert cost.estimated_list_cost_usd > 0.0


def test_models_catalog_completeness(pricing):
    """Verify catalog lists models for all 3 providers and default selections."""
    catalog = pricing.get_models_catalog()
    providers = {m.provider for m in catalog}
    assert "openai" in providers
    assert "anthropic" in providers
    assert "gemini" in providers

    defaults = [m for m in catalog if m.is_default]
    assert len(defaults) >= 3  # At least one default per provider
