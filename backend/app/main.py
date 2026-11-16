import logging
import uuid
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.trustedhost import TrustedHostMiddleware
from fastapi.responses import JSONResponse
from sqlalchemy.exc import SQLAlchemyError
from app.api.router import api_router
from app.core.config import Settings, get_settings
from app.frontend import mount_frontend
logger = logging.getLogger(__name__)

def create_app(settings: Settings | None = None) -> FastAPI:
    app_settings = settings or get_settings()
    application = FastAPI(title="Vedic Astrology API", version=app_settings.application_version, docs_url="/docs" if app_settings.environment == "development" else None, redoc_url="/redoc" if app_settings.environment == "development" else None)
    application.state.settings = app_settings
    application.add_middleware(TrustedHostMiddleware, allowed_hosts=app_settings.trusted_hosts)
    application.add_middleware(CORSMiddleware, allow_origins=app_settings.allowed_origins, allow_credentials=True, allow_methods=["GET","POST","PATCH","DELETE","OPTIONS"], allow_headers=["Accept","Content-Type","X-CSRF-Token"], expose_headers=["X-Request-ID","X-Total-Count"])
    application.include_router(api_router)
    @application.middleware("http")
    async def security_headers(request: Request, call_next):
        request.state.request_id=request.headers.get("X-Request-ID") or str(uuid.uuid4())
        response=await call_next(request)
        response.headers["X-Request-ID"]=request.state.request_id
        response.headers["X-Content-Type-Options"]="nosniff"
        response.headers["Referrer-Policy"]="strict-origin-when-cross-origin"
        response.headers["Permissions-Policy"]="camera=(), microphone=(), geolocation=()"
        response.headers["Content-Security-Policy"]="default-src 'self'; base-uri 'self'; frame-ancestors 'none'; object-src 'none'; img-src 'self' data: blob:; font-src 'self' data:; connect-src 'self'; style-src 'self' 'unsafe-inline'"
        if app_settings.environment=="production":
            response.headers["Strict-Transport-Security"]="max-age=31536000"
        return response
    @application.exception_handler(SQLAlchemyError)
    async def database_exception_handler(request: Request, exc: SQLAlchemyError) -> JSONResponse:
        logger.exception("Database operation failed for %s", request.url.path, exc_info=exc)
        return JSONResponse(status_code=503, content={"detail": "Database unavailable", "request_id":getattr(request.state,"request_id",None)})
    @application.exception_handler(Exception)
    async def unhandled_exception_handler(request: Request, exc: Exception) -> JSONResponse:
        logger.exception("Unhandled error while processing %s", request.url.path, exc_info=exc)
        return JSONResponse(status_code=500, content={"detail": "Internal server error", "request_id":getattr(request.state,"request_id",None)})
    if app_settings.frontend_dist:
        mount_frontend(application, app_settings.frontend_dist)
    return application

app = create_app()
