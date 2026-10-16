from fastapi import APIRouter, HTTPException, status
from app.config import settings
from app.schemas.comparison import (
    CompareRequest,
    CompareResponse,
    ModelsCatalogResponse,
)
from app.services.comparison import comparison_service
from app.services.pricing import pricing_service

router = APIRouter(prefix="/api", tags=["LLM Comparison"])


@router.get("/health", summary="Service Health and Provider Status")
async def health_check():
    """Returns application health status and currently available provider keys."""
    return {
        "status": "healthy",
        "mock_mode": settings.mock_mode,
        "providers_configured": {
            "openai": bool(settings.openai_api_key),
            "anthropic": bool(settings.anthropic_api_key),
            "gemini": bool(settings.gemini_api_key),
        },
    }


@router.get(
    "/models",
    response_model=ModelsCatalogResponse,
    summary="List Supported Next-Gen Models and Pricing",
)
async def list_models():
    """Returns catalog of supported next-gen models, pricing rates, and Free-Tier eligibility."""
    catalog = pricing_service.get_models_catalog()
    return ModelsCatalogResponse(models=catalog)


@router.post(
    "/compare",
    response_model=CompareResponse,
    summary="Benchmark Prompt Across Selected Models Concurrently",
)
async def compare_models(request: CompareRequest):
    """
    Validates input prompt, executes async tasks concurrently across all selected models,
    and returns normalized text, token counts, latency, and estimated cost metrics.
    """
    if not request.models:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="At least one model must be selected for comparison.",
        )

    try:
        response = await comparison_service.run_comparison(request)
        return response
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Comparison pipeline error: {str(exc)}",
        )
