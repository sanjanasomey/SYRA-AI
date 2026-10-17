"""
SYRA AI - Settings & Provider Router
Module: backend/routers/settings.py

Provides provider status, available models, and defaults without exposing keys.
"""

from fastapi import APIRouter
from backend.core.config import settings
from backend.models.schemas import ProvidersResponse, ProviderStatus
from backend.services.llm_service import SUPPORTED_PROVIDERS, check_api_status

router = APIRouter(prefix="/api", tags=["Settings & Providers"])


@router.get("/providers", response_model=ProvidersResponse)
async def get_providers():
    """Return supported providers, available models, and safe key status."""
    statuses = check_api_status()
    result = {}
    for prov_key, prov_info in SUPPORTED_PROVIDERS.items():
        st = statuses.get(prov_key, {})
        result[prov_key] = ProviderStatus(
            name=prov_info["name"],
            default_model=prov_info["default_model"],
            models=prov_info["models"],
            configured=st.get("configured", False),
            masked_key=st.get("masked_key", "Not Configured"),
            env_var=st.get("env_var", prov_info["env_var"])
        )

    return ProvidersResponse(
        providers=result,
        default_provider=settings.default_provider
    )
