from datetime import UTC

from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy import select
from sqlalchemy.orm import Session, joinedload

from app.astrology.calculations import AstrologyCalculationService, CalculationInput
from app.astrology.divisional import build_divisional_chart
from app.astrology.divisional.constants import SUPPORTED_CHARTS
from app.astrology.exceptions import AstrologyError, EphemerisUnavailableError
from app.db.session import get_db
from app.models import BirthProfile, User
from app.core.security import current_user
from app.schemas.divisional import DivisionalCalculationRequest, DivisionalChartResponse, DivisionalConfigResponse
from app.services.birth_time import BirthTimeError, resolve_birth_time
from app.core.security import rate_limit

router = APIRouter(prefix="/divisional", tags=["divisional charts"])


def _calculate(data: CalculationInput, chart_type: str) -> dict:
    try:
        d1 = AstrologyCalculationService().calculate(data)
        return build_divisional_chart(d1, chart_type)
    except EphemerisUnavailableError as exc:
        raise HTTPException(503, str(exc)) from exc
    except (AstrologyError, ValueError) as exc:
        raise HTTPException(422, str(exc)) from exc


def _profile_input(profile: BirthProfile) -> CalculationInput:
    if profile.birth_time_unknown or profile.birth_time is None:
        raise HTTPException(422, "Exact birth time is required for divisional Lagna and house calculations")
    if profile.timezone_resolution_status in {"pending", "ambiguous"} or profile.birth_time_utc is None:
        raise HTTPException(422, "Birth profile timezone resolution must be completed before calculation")
    return CalculationInput(
        utc_datetime=profile.birth_time_utc.replace(tzinfo=UTC),
        local_datetime=f"{profile.birth_date.isoformat()}T{profile.birth_time.isoformat()}",
        timezone=profile.location.timezone, resolution_status=profile.timezone_resolution_status,
        latitude=float(profile.location.latitude), longitude=float(profile.location.longitude),
        city=profile.location.city, state=profile.location.state, country=profile.location.country,
    )


@router.get("/config", response_model=DivisionalConfigResponse)
def config():
    return {
        "supported_charts": [{"chart_type": key, "name": value["name"], "division": value["division"],
                              "segment_degrees": float(value["segment_degrees"]), "primary_use": value["primary_use"]}
                             for key, value in SUPPORTED_CHARTS.items()],
        "system": "Parashari", "zodiac": "sidereal", "ayanamsa": "Lahiri",
        "node_convention": "mean", "house_system": "whole_sign",
        "boundary_policy": "Half-open intervals; an exact boundary begins the next division. Proximity warnings do not alter classification.",
        "public_deployment_blocked": False,
    }


@router.post("/calculate", response_model=DivisionalChartResponse)
def calculate(payload: DivisionalCalculationRequest, request: Request, db: Session = Depends(get_db)):
    rate_limit(db,request,"divisional_calculate",20,3600)
    try:
        resolution = resolve_birth_time(payload.birth_date, payload.birth_time, payload.timezone, payload.timezone_fold)
    except BirthTimeError as exc:
        raise HTTPException(422, str(exc)) from exc
    if resolution.utc_datetime is None:
        raise HTTPException(422, "Ambiguous local time requires an explicit timezone_fold")
    return _calculate(CalculationInput(
        utc_datetime=resolution.utc_datetime, local_datetime=resolution.local_datetime.isoformat(),
        timezone=payload.timezone, resolution_status=resolution.status,
        latitude=payload.latitude, longitude=payload.longitude, city=payload.city,
        state=payload.state, country=payload.country,
    ), payload.chart_type)


def _saved_chart(profile_id: int, chart_type: str, request: Request, db: Session, user: User) -> dict:
    profile = db.scalar(select(BirthProfile).options(joinedload(BirthProfile.location)).where(BirthProfile.id == profile_id, BirthProfile.user_id == user.id))
    if not profile:
        raise HTTPException(404, "Birth profile not found")
    return _calculate(_profile_input(profile), chart_type)


@router.get("/birth-profiles/{profile_id}/d9", response_model=DivisionalChartResponse)
def d9_profile(profile_id: int, request: Request, user: User = Depends(current_user), db: Session = Depends(get_db)):
    return _saved_chart(profile_id, "D9", request, db, user)


@router.get("/birth-profiles/{profile_id}/d10", response_model=DivisionalChartResponse)
def d10_profile(profile_id: int, request: Request, user: User = Depends(current_user), db: Session = Depends(get_db)):
    return _saved_chart(profile_id, "D10", request, db, user)
