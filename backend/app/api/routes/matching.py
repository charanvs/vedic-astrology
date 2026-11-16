from datetime import UTC
from decimal import Decimal

from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy import select
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session, joinedload

from app.astrology.config import get_calculation_settings
from app.astrology.ephemeris import Ephemeris
from app.astrology.exceptions import AstrologyError, EphemerisUnavailableError
from app.astrology.matching.calculator import AshtakootaMatchingService, PartnerMoon
from app.astrology.matching.constants import (
    GANA_BY_NAKSHATRA, GANA_MATRIX, KOOTA_MAXIMA, NADI_BY_NAKSHATRA,
    RULESET_ID, VARNA_BY_RASHI, VASHYA_BY_RASHI, VASHYA_MATRIX,
    YONI_BY_NAKSHATRA, YONI_MATRIX,
)
from app.astrology.matching.exceptions import MatchingError
from app.astrology.matching.moon import ProfileMoonResolver
from app.astrology.matching.rulesets import RULESET
from app.db.session import get_db
from app.models import BirthProfile, User
from app.core.security import rate_limit, require_csrf
from app.schemas.matching import (
    MatchingConfigResponse, MatchingRequest, MatchingResult, MatchingRulesResponse,
    SavedProfilesMatchingRequest,
)

router = APIRouter(prefix="/matching", tags=["matching"])


def _from_longitude(longitude: Decimal, role: str, name: str | None) -> PartnerMoon:
    normalized = longitude % Decimal(360)
    rashi = int(normalized // Decimal(30)) + 1
    scaled = normalized * Decimal(27) / Decimal(360)
    nakshatra = min(int(scaled), 26) + 1
    pada = min(int((scaled - int(scaled)) * Decimal(4)), 3) + 1
    return PartnerMoon(role=role, longitude=normalized, rashi_number=rashi,
        nakshatra_number=nakshatra, pada=pada, name=name)


def _calculate(first: PartnerMoon, second: PartnerMoon, ruleset: str) -> dict:
    try:
        return AshtakootaMatchingService().calculate(first, second, ruleset)
    except MatchingError as exc:
        raise HTTPException(422, str(exc)) from exc
    except ValueError as exc:
        raise HTTPException(422, str(exc)) from exc


def _profile_moon(profile: BirthProfile, role: str, resolver: ProfileMoonResolver) -> PartnerMoon:
    if profile.birth_time_unknown or profile.birth_time is None:
        return resolver.unknown_time(profile.birth_date, profile.location.timezone, role, profile.id, profile.full_name)
    if profile.birth_time_utc is None or profile.timezone_resolution_status in {"pending", "ambiguous"}:
        raise HTTPException(422, f"Timezone resolution is incomplete for profile {profile.id}")
    return resolver.exact(profile.birth_time_utc.replace(tzinfo=UTC), role, profile.id, profile.full_name)


@router.post("/calculate", response_model=MatchingResult)
def calculate_matching(payload: MatchingRequest, request: Request, db: Session = Depends(get_db)):
    rate_limit(db,request,"matching_calculate",30,3600)
    return _calculate(
        _from_longitude(payload.partner_one.moon_sidereal_longitude, payload.partner_one.role, payload.partner_one.name),
        _from_longitude(payload.partner_two.moon_sidereal_longitude, payload.partner_two.role, payload.partner_two.name),
        payload.ruleset,
    )


@router.post("/birth-profiles", response_model=MatchingResult)
def match_birth_profiles(payload: SavedProfilesMatchingRequest, request: Request, context = Depends(require_csrf), db: Session = Depends(get_db)):
    try:
        profiles = db.scalars(select(BirthProfile).options(joinedload(BirthProfile.location)).where(
            BirthProfile.id.in_([payload.partner_one_profile_id, payload.partner_two_profile_id]), BirthProfile.user_id == context.user.id
        )).unique().all()
    except SQLAlchemyError as exc:
        raise HTTPException(503, "Matching profiles could not be loaded") from exc
    by_id = {item.id: item for item in profiles}
    if payload.partner_one_profile_id not in by_id or payload.partner_two_profile_id not in by_id:
        raise HTTPException(404, "One or both birth profiles were not found")
    try:
        resolver = ProfileMoonResolver()
        first = _profile_moon(by_id[payload.partner_one_profile_id], payload.partner_one_role, resolver)
        second = _profile_moon(by_id[payload.partner_two_profile_id], payload.partner_two_role, resolver)
        return _calculate(first, second, payload.ruleset)
    except EphemerisUnavailableError as exc:
        raise HTTPException(503, str(exc)) from exc
    except AstrologyError as exc:
        raise HTTPException(422, str(exc)) from exc
    except MatchingError as exc:
        raise HTTPException(422, str(exc)) from exc


@router.get("/config", response_model=MatchingConfigResponse)
def matching_config():
    settings = get_calculation_settings()
    try:
        engine = Ephemeris(settings).metadata()
    except AstrologyError as exc:
        engine = {"engine": "Swiss Ephemeris", "status": "unavailable", "detail": str(exc)}
    return {"supported_rulesets": [RULESET], "default_ruleset": RULESET_ID,
        "koota_maximums": KOOTA_MAXIMA, "total_maximum": Decimal(36),
        "roles": ["bride", "groom"], "engine": engine, "ayanamsa": settings.ayanamsa,
        "public_deployment_blocked": False}


@router.get("/rules", response_model=MatchingRulesResponse)
def matching_rules():
    return {
        "ruleset": RULESET,
        "classifications": {"varna_by_rashi": VARNA_BY_RASHI, "vashya_by_rashi": VASHYA_BY_RASHI,
            "yoni_by_nakshatra": YONI_BY_NAKSHATRA, "gana_by_nakshatra": GANA_BY_NAKSHATRA,
            "nadi_by_nakshatra": NADI_BY_NAKSHATRA},
        "matrices": {"vashya": VASHYA_MATRIX, "yoni": YONI_MATRIX, "gana": GANA_MATRIX},
        "conventions": {"roles": "bride row, groom column", "tara_count": "inclusive modulo nine",
            "bhakoot_zero_pairs": ["2/12", "5/9", "6/8"], "exceptions_change_score": False},
        "sources": [
            {"title": "Muhurta Chintamani, Joshi edition", "detail": "Vivaha Prakarana verses 21–37, pp. 329–355"},
            {"title": "Bharatiya Jyotish", "detail": "Nemichandra Shastri, 1970, chapter 5, pp. 608–617"},
            {"title": "Muhurtha", "detail": "B. V. Raman, 1948, pp. 82–92"},
        ],
    }
