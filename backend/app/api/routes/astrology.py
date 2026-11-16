from datetime import UTC

from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy import select
from sqlalchemy.orm import Session, joinedload

from app.astrology.calculations import AstrologyCalculationService, CalculationInput
from app.astrology.config import get_calculation_settings
from app.astrology.ephemeris import Ephemeris
from app.astrology.exceptions import AstrologyError, EphemerisUnavailableError
from app.db.session import get_db
from app.models import BirthProfile, User
from app.core.security import current_user
from app.schemas.astrology import (
    AstronomyCalculationResponse, AstrologyConfigResponse, CalculationRequest,
)
from app.services.birth_time import BirthTimeError, resolve_birth_time
from app.core.security import rate_limit

router = APIRouter(prefix="/astrology", tags=["astrology"])


def _run(data: CalculationInput) -> dict:
    try:
        return AstrologyCalculationService().calculate(data)
    except EphemerisUnavailableError as exc:
        raise HTTPException(503, str(exc)) from exc
    except AstrologyError as exc:
        raise HTTPException(422, str(exc)) from exc


@router.get("/config", response_model=AstrologyConfigResponse)
def astrology_config():
    settings = get_calculation_settings()
    engine_available = True
    try:
        engine = Ephemeris(settings).metadata()
    except AstrologyError as exc:
        engine_available = False
        engine = {
            "engine": "Swiss Ephemeris",
            "binding": "pyswisseph",
            "status": "unavailable",
            "detail": str(exc),
            "ephemeris_source": settings.ephemeris_source,
        }
    return {
        "settings": settings,
        "engine_available": engine_available,
        "engine": engine,
        "supported_bodies": ["Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn", "Rahu", "Ketu"],
        "public_deployment_blocked": False,
    }


@router.post("/calculate", response_model=AstronomyCalculationResponse)
def calculate(payload: CalculationRequest, request: Request, db: Session = Depends(get_db)):
    rate_limit(db,request,"astrology_calculate",30,3600)
    try:
        resolution = resolve_birth_time(
            payload.birth_date, payload.birth_time, payload.timezone, payload.timezone_fold
        )
    except BirthTimeError as exc:
        raise HTTPException(422, str(exc)) from exc
    if resolution.utc_datetime is None:
        raise HTTPException(422, "Ambiguous local time requires an explicit timezone_fold")
    return _run(CalculationInput(
        utc_datetime=resolution.utc_datetime,
        local_datetime=resolution.local_datetime.isoformat(),
        timezone=payload.timezone,
        resolution_status=resolution.status,
        latitude=payload.latitude,
        longitude=payload.longitude,
        city=payload.city,
        state=payload.state,
        country=payload.country,
    ))


@router.get("/birth-profiles/{profile_id}/calculate", response_model=AstronomyCalculationResponse)
def calculate_profile(profile_id: int, request: Request, user: User = Depends(current_user), db: Session = Depends(get_db)):
    profile = db.scalar(
        select(BirthProfile)
        .options(joinedload(BirthProfile.location))
        .where(BirthProfile.id == profile_id, BirthProfile.user_id == user.id)
    )
    if not profile:
        raise HTTPException(404, "Birth profile not found")
    if profile.birth_time_unknown or profile.birth_time is None:
        raise HTTPException(422, "Exact birth time is required for Lagna and house calculations")
    if profile.timezone_resolution_status in {"pending", "ambiguous"} or profile.birth_time_utc is None:
        raise HTTPException(422, "Birth profile timezone resolution must be completed before calculation")
    utc_value = profile.birth_time_utc.replace(tzinfo=UTC)
    return _run(CalculationInput(
        utc_datetime=utc_value,
        local_datetime=f"{profile.birth_date.isoformat()}T{profile.birth_time.isoformat()}",
        timezone=profile.location.timezone,
        resolution_status=profile.timezone_resolution_status,
        latitude=float(profile.location.latitude),
        longitude=float(profile.location.longitude),
        city=profile.location.city,
        state=profile.location.state,
        country=profile.location.country,
    ))
