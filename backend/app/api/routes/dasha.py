from datetime import UTC, datetime

from fastapi import APIRouter, Depends, HTTPException, Query, Request
from sqlalchemy import select
from sqlalchemy.orm import Session, joinedload

from app.astrology.config import get_calculation_settings
from app.astrology.dasha import DashaInput, DashaYearConvention, DetailLevel, VimshottariDashaService
from app.astrology.dasha.constants import DASHA_SEQUENCE, DASHA_YEARS, TOTAL_DASHA_YEARS
from app.astrology.dasha.exceptions import DashaError
from app.astrology.ephemeris import Ephemeris
from app.astrology.exceptions import AstrologyError
from app.db.session import get_db
from app.models import BirthProfile, User
from app.core.security import current_user
from app.schemas.dasha import (
    CurrentDashaResponse, DashaCalculationRequest, DashaConfigResponse, DashaTimelineResponse,
)
from app.services.birth_time import BirthTimeError, resolve_birth_time
from app.core.security import rate_limit

router = APIRouter(prefix="/dasha", tags=["dasha"])


def _calculate(data: DashaInput) -> dict:
    try:
        return VimshottariDashaService().calculate(data)
    except DashaError as exc:
        raise HTTPException(422, str(exc)) from exc
    except AstrologyError as exc:
        raise HTTPException(503, str(exc)) from exc


def _validate_reference(value: datetime | None) -> datetime | None:
    if value is not None and value.utcoffset() is None:
        raise HTTPException(422, "reference_datetime must include a UTC offset")
    return value


def _profile_data(
    profile_id: int,
    db: Session,
    year_convention: DashaYearConvention,
    reference_datetime: datetime | None,
    detail_level: DetailLevel,
    user: User,
) -> DashaInput:
    profile = db.scalar(
        select(BirthProfile).options(joinedload(BirthProfile.location)).where(BirthProfile.id == profile_id, BirthProfile.user_id == user.id)
    )
    if not profile:
        raise HTTPException(404, "Birth profile not found")
    if profile.birth_time_unknown or profile.birth_time is None:
        raise HTTPException(422, "Exact birth time is required for Vimshottari Dasha calculation")
    if profile.birth_time_utc is None or profile.timezone_resolution_status in {"pending", "ambiguous"}:
        raise HTTPException(422, "Birth profile timezone resolution must be completed before calculation")
    return DashaInput(
        birth_utc=profile.birth_time_utc.replace(tzinfo=UTC), timezone=profile.location.timezone,
        latitude=float(profile.location.latitude), longitude=float(profile.location.longitude),
        city=profile.location.city, state=profile.location.state, country=profile.location.country,
        full_name=profile.full_name, profile_id=profile.id, year_convention=year_convention,
        reference_utc=_validate_reference(reference_datetime), detail_level=detail_level,
    )


@router.post("/calculate", response_model=DashaTimelineResponse)
def calculate_dasha(payload: DashaCalculationRequest, request: Request, db: Session = Depends(get_db)):
    rate_limit(db,request,"dasha_calculate",20,3600)
    try:
        resolution = resolve_birth_time(
            payload.birth_date, payload.birth_time, payload.timezone, payload.timezone_fold
        )
    except BirthTimeError as exc:
        raise HTTPException(422, str(exc)) from exc
    if resolution.utc_datetime is None:
        raise HTTPException(422, "Ambiguous local time requires an explicit timezone_fold")
    return _calculate(DashaInput(
        birth_utc=resolution.utc_datetime, timezone=payload.timezone,
        latitude=payload.latitude, longitude=payload.longitude, city=payload.city,
        state=payload.state, country=payload.country, full_name=payload.full_name,
        year_convention=payload.year_convention, reference_utc=payload.reference_datetime,
        detail_level=payload.detail_level,
    ))


@router.get("/birth-profiles/{profile_id}", response_model=DashaTimelineResponse)
def profile_dasha(
    profile_id: int, request: Request,
    year_convention: DashaYearConvention = Query(DashaYearConvention.TROPICAL_365_25),
    reference_datetime: datetime | None = Query(None),
    detail_level: DetailLevel = Query(DetailLevel.PRATYANTARDASHA),
    user: User = Depends(current_user),
    db: Session = Depends(get_db),
):
    return _calculate(_profile_data(
        profile_id, db, year_convention, reference_datetime, detail_level, user
    ))


@router.get("/birth-profiles/{profile_id}/current", response_model=CurrentDashaResponse)
def current_dasha(
    profile_id: int, request: Request,
    year_convention: DashaYearConvention = Query(DashaYearConvention.TROPICAL_365_25),
    reference_datetime: datetime | None = Query(None),
    user: User = Depends(current_user),
    db: Session = Depends(get_db),
):
    result = _calculate(_profile_data(
        profile_id, db, year_convention, reference_datetime, DetailLevel.MAHADASHA, user
    ))
    return {key: result[key] for key in (
        "profile", "birth_moon", "reference", "current", "settings", "engine", "metadata", "warnings"
    )}


@router.get("/config", response_model=DashaConfigResponse)
def dasha_config():
    settings = get_calculation_settings()
    try:
        engine = Ephemeris(settings).metadata()
    except AstrologyError as exc:
        engine = {"engine": "Swiss Ephemeris", "status": "unavailable", "detail": str(exc)}
    return {
        "available_year_conventions": [
            {"id": convention.value, "label": convention.label, "days": convention.days}
            for convention in DashaYearConvention
        ],
        "default_year_convention": DashaYearConvention.TROPICAL_365_25.value,
        "planetary_sequence": list(DASHA_SEQUENCE), "mahadasha_durations": DASHA_YEARS,
        "total_cycle_years": TOTAL_DASHA_YEARS,
        "supported_detail_levels": [level.value for level in DetailLevel],
        "ayanamsa": settings.ayanamsa, "zodiac": settings.zodiac, "engine": engine,
        "interval_semantics": "[start, end)", "public_deployment_blocked": False,
    }
