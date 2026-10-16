import pytest
from httpx import AsyncClient, ASGITransport
from app.main import app
from app.services.comparison import comparison_service
from app.providers.mock_provider import MockProvider


@pytest.fixture(autouse=True)
def setup_mock_providers():
    """Ensure test runs use MockProviders so no external API keys or credits are consumed."""
    comparison_service.providers = {
        "openai": MockProvider("openai"),
        "anthropic": MockProvider("anthropic"),
        "gemini": MockProvider("gemini"),
    }


@pytest.mark.asyncio
async def test_health_endpoint():
    """Verify /api/health returns 200 OK and health status."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.get("/api/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert "providers_configured" in data


@pytest.mark.asyncio
async def test_models_endpoint():
    """Verify /api/models returns next-gen models catalog."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.get("/api/models")
        assert response.status_code == 200
        data = response.json()
        assert "models" in data
        assert len(data["models"]) >= 6

        # Check Gemini Free Tier indicator
        gemini_flash = next(m for m in data["models"] if m["id"] == "gemini-3.0-flash")
        assert gemini_flash["pricing"]["is_free_tier_eligible"] is True


@pytest.mark.asyncio
async def test_compare_endpoint_success():
    """Verify /api/compare executes concurrent comparison across 3 models."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        payload = {
            "prompt": "Compare quicksort vs mergesort in two sentences.",
            "models": [
                {"provider": "openai", "model": "o3-mini"},
                {"provider": "anthropic", "model": "claude-3-7-sonnet"},
                {"provider": "gemini", "model": "gemini-3.0-flash"},
            ],
            "temperature": 0.7,
            "max_tokens": 1024,
        }
        response = await client.post("/api/compare", json=payload)
        assert response.status_code == 200
        data = response.json()

        assert data["prompt"] == payload["prompt"]
        assert data["total_latency_ms"] > 0
        assert len(data["results"]) == 3

        for res in data["results"]:
            assert res["status"] == "success"
            assert len(res["text"]) > 0
            assert res["tokens"]["total_tokens"] > 0
            assert res["latency_ms"] > 0

        # Verify Gemini Free Tier flag in response cost
        gemini_res = next(r for r in data["results"] if r["provider"] == "gemini")
        assert gemini_res["cost"]["is_free_tier"] is True
        assert gemini_res["cost"]["actual_cost_usd"] == 0.0
        assert gemini_res["cost"]["estimated_list_cost_usd"] > 0.0


@pytest.mark.asyncio
async def test_compare_validation_error():
    """Verify empty prompt or missing models returns 422 Unprocessable Entity."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        # Empty prompt
        res1 = await client.post("/api/compare", json={"prompt": "", "models": []})
        assert res1.status_code == 422
