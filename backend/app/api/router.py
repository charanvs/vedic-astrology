from fastapi import APIRouter
from app.api.routes.system import router as system_router
from app.api.routes.database import router as database_router
from app.api.routes.astrology import router as astrology_router
from app.api.routes.panchang import router as panchang_router
from app.api.routes.dasha import router as dasha_router
from app.api.routes.matching import router as matching_router
from app.api.routes.divisional import router as divisional_router
from app.api.routes.reports import router as reports_router
from app.api.routes.auth import router as auth_router
from app.api.routes.geocoding import router as geocoding_router
from app.api.routes.admin import router as admin_router
api_router = APIRouter(prefix="/api")
api_router.include_router(auth_router)
api_router.include_router(system_router)
api_router.include_router(database_router)
api_router.include_router(geocoding_router)
api_router.include_router(admin_router)
api_router.include_router(astrology_router)
api_router.include_router(panchang_router)
api_router.include_router(dasha_router)
api_router.include_router(matching_router)
api_router.include_router(divisional_router)
api_router.include_router(reports_router)
