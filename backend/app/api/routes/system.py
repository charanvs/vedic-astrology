from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import RedirectResponse
from app.schemas.system import HealthResponse, VersionResponse
router = APIRouter(tags=["system"])

@router.get("/health", response_model=HealthResponse)
async def health() -> HealthResponse:
    return HealthResponse(status="ok", application="vedic-astrology", service="backend")

@router.get("/version", response_model=VersionResponse)
async def version(request: Request) -> VersionResponse:
    settings = request.app.state.settings
    return VersionResponse(application=settings.application_name, version=settings.application_version, environment=settings.environment)

@router.get("/source", include_in_schema=False)
async def source_code(request: Request):
    # AGPL-3.0 section 13: offer the corresponding source to every network user.
    url = request.app.state.settings.source_code_url
    if not url: raise HTTPException(404, "The source code location has not been configured yet")
    return RedirectResponse(url, status_code=302)
