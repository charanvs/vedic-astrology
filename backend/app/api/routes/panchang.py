from datetime import date

from fastapi import APIRouter, Depends, HTTPException, Query, Request
from sqlalchemy.orm import Session

from app.astrology.config import get_calculation_settings
from app.astrology.ephemeris import Ephemeris
from app.astrology.exceptions import AstrologyError, EphemerisUnavailableError
from app.astrology.julian import MAXIMUM_YEAR, MINIMUM_YEAR
from app.astrology.panchang import DailyPanchangService, PanchangInput
from app.db.session import get_db
from app.models import Location
from app.schemas.panchang import (
    DailyPanchangResponse, PanchangConfigResponse, PanchangRequest, validate_panchang_date,
)
from app.core.security import rate_limit

router = APIRouter(prefix="/panchang", tags=["panchang"])


def _calculate(data: PanchangInput) -> dict:
    try:
        return DailyPanchangService().calculate(data)
    except EphemerisUnavailableError as exc:
        raise HTTPException(503, str(exc)) from exc
    except AstrologyError as exc:
        raise HTTPException(422, str(exc)) from exc


@router.get("/daily", response_model=DailyPanchangResponse)
def daily_panchang(
    request: Request,
    date_value: date = Query(alias="date"),
    location_id: int = Query(ge=1),
    db: Session = Depends(get_db),
):
    rate_limit(db,request,"panchang",60,3600)
    try:
        validate_panchang_date(date_value)
    except ValueError as exc:
        raise HTTPException(422, str(exc)) from exc
    location = db.get(Location, location_id)
    if not location:
        raise HTTPException(404, "Location not found")
    return _calculate(PanchangInput(
        civil_date=date_value, latitude=float(location.latitude), longitude=float(location.longitude),
        timezone=location.timezone, city=location.city, state=location.state,
        country=location.country, location_id=location.id,
    ))


@router.post("/calculate", response_model=DailyPanchangResponse)
def calculate_panchang(payload: PanchangRequest, request: Request, db: Session = Depends(get_db)):
    rate_limit(db,request,"panchang",60,3600)
    return _calculate(PanchangInput(
        civil_date=payload.date, latitude=payload.latitude, longitude=payload.longitude,
        timezone=payload.timezone, city=payload.city, state=payload.state,
        country=payload.country, elevation=payload.elevation,
    ))


@router.get("/config", response_model=PanchangConfigResponse)
def panchang_config():
    settings = get_calculation_settings()
    try:
        engine = Ephemeris(settings).metadata()
    except AstrologyError as exc:
        engine = {"engine": "Swiss Ephemeris", "status": "unavailable", "detail": str(exc)}
    return {
        "method": "Drik Ganita",
        "zodiac": settings.zodiac,
        "ayanamsa": settings.ayanamsa,
        "ephemeris": engine,
        "sunrise_convention": "apparent upper solar limb with standard atmospheric refraction",
        "supported_date_range": {"minimum_year": MINIMUM_YEAR, "maximum_year": MAXIMUM_YEAR},
        "timezone_handling": "IANA zoneinfo with historical UTC offsets",
        "panchang_day_definition": "local sunrise to next local sunrise; elements evaluated at sunrise",
        "public_deployment_blocked": False,
    }
