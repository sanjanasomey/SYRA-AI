"""
SYRA AI - FastAPI Main Application
Module: backend/main.py

FastAPI entrypoint setting up CORS, health check, router mounting,
and lifecycle hooks for the SYRA AI backend.
"""

from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.core.config import settings
from backend.models.schemas import StatusResponse, ProviderStatus
from backend.services.llm_service import check_api_status
from backend.services.evaluation import eval_repo

# Import API routers
from backend.routers.settings import router as settings_router
from backend.routers.chat import router as chat_router
from backend.routers.comparison import router as comparison_router
from backend.routers.evaluation import router as evaluation_router
from backend.routers.faq import router as faq_router
from backend.routers.export import router as export_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup actions
    print(f"SYRA AI Backend starting up (v{settings.app_version})")
    yield
    # Shutdown actions
    print("SYRA AI Backend shutting down")


app = FastAPI(
    title=settings.app_title,
    version=settings.app_version,
    description="Intelligent Chatbot & Prompt Engineering Workbench API",
    lifespan=lifespan
)

# Configure CORS for Vite React frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origin_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount all routers
app.include_router(settings_router)
app.include_router(chat_router)
app.include_router(comparison_router)
app.include_router(evaluation_router)
app.include_router(faq_router)
app.include_router(export_router)


@app.get("/health", tags=["Health"])
async def health_check():
    """Simple health check endpoint."""
    return {"status": "healthy", "service": "syra-ai-backend"}


@app.get("/api/status", response_model=StatusResponse, tags=["Status"])
async def get_system_status():
    """Return backend status, configured providers, and session count."""
    providers_status = check_api_status()
    typed_providers = {
        name: ProviderStatus(
            name=name.capitalize(),
            default_model=info.get("default_model", "unknown"),
            models=[],
            configured=info["configured"],
            masked_key=info["masked_key"],
            env_var=info["env_var"]
        )
        for name, info in providers_status.items()
    }
    return StatusResponse(
        app_name=settings.app_title,
        version=settings.app_version,
        tagline="Think clearly. Prompt brilliantly.",
        providers=typed_providers,
        active_sessions=eval_repo.get_active_session_count()
    )
