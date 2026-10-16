from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.config import settings
from app.api.routes import router as api_router

app = FastAPI(
    title="LLM Router Dashboard API",
    description=(
        "Production-grade backend for concurrent multi-model inference benchmarking. "
        "Compares GPT-4.5/o3-mini, Claude 3.7/4, and Gemini 3.0/3.8 side-by-side "
        "with token counts, latency, and estimated cost calculations."
    ),
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

# Configure CORS for local development and production frontends
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register API Router
app.include_router(api_router)


@app.get("/", summary="Root Endpoint")
async def root():
    return {
        "service": "LLM Router Dashboard API",
        "status": "online",
        "version": "1.0.0",
        "documentation": "/docs",
        "health": "/api/health",
        "models": "/api/models",
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host=settings.backend_host,
        port=settings.backend_port,
        reload=True,
    )
