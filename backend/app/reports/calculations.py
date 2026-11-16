from datetime import UTC, datetime, timedelta

from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session, joinedload

from app.astrology.calculations import AstrologyCalculationService, CalculationInput
from app.astrology.dasha import DashaInput, DashaYearConvention, DetailLevel, VimshottariDashaService
from app.astrology.divisional import build_divisional_chart
from app.astrology.matching.calculator import AshtakootaMatchingService
from app.astrology.matching.moon import ProfileMoonResolver
from app.astrology.panchang import DailyPanchangService, PanchangInput
from app.astrology.panchang.elements import karana_for_elongation, tithi_for_elongation, yoga_for_sum
from app.astrology.transits import TransitCalculator
from app.models import BirthProfile
from app.reports.interpretation import TRANSIT_PLANETS

FORECAST_SPAN=timedelta(days=1096)

def load_profile(db: Session, profile_id: int) -> BirthProfile:
    profile=db.scalar(select(BirthProfile).options(joinedload(BirthProfile.location)).where(BirthProfile.id==profile_id))
    if not profile: raise HTTPException(404,"Birth profile not found")
    return profile

def require_exact(profile: BirthProfile):
    if profile.birth_time_unknown or profile.birth_time is None: raise HTTPException(422,"Exact birth time is required for this report")
    if profile.birth_time_utc is None or profile.timezone_resolution_status in {"pending","ambiguous"}: raise HTTPException(422,"Birth profile timezone resolution must be completed before report generation")

def calculation_input(profile: BirthProfile) -> CalculationInput:
    require_exact(profile)
    return CalculationInput(profile.birth_time_utc.replace(tzinfo=UTC),f"{profile.birth_date.isoformat()}T{profile.birth_time.isoformat()}",profile.location.timezone,profile.timezone_resolution_status,float(profile.location.latitude),float(profile.location.longitude),profile.location.city,profile.location.state,profile.location.country)

def collect_kundli(profile: BirthProfile, report_type: str, sections: set[str], year_convention: str, reference_datetime):
    d1=AstrologyCalculationService().calculate(calculation_input(profile))
    data={"d1":d1}
    if "d9_chart" in sections: data["d9"]=build_divisional_chart(d1,"D9")
    if "d10_chart" in sections: data["d10"]=build_divisional_chart(d1,"D10")
    if "panchang" in sections:
        daily=DailyPanchangService().calculate(PanchangInput(profile.birth_date,float(profile.location.latitude),float(profile.location.longitude),profile.location.timezone,profile.location.city,profile.location.state,profile.location.country,profile.location.id))
        by_id={p["identifier"]:p for p in d1["planets"]}; sun=by_id["sun"]["longitude"]; moon=by_id["moon"]["longitude"]; elongation=(moon-sun)%360
        data["panchang"]={"daily":daily,"birth":{"tithi":tithi_for_elongation(elongation),"nakshatra":by_id["moon"]["nakshatra"],"yoga":yoga_for_sum((sun+moon)%360),"karana":karana_for_elongation(elongation),"vara":daily["vara"]}}
    reference=reference_datetime or datetime.now(UTC)
    if sections & {"dasha","interpretation","forecast"}:
        convention=DashaYearConvention(year_convention)
        data["dasha"]=VimshottariDashaService().calculate(DashaInput(profile.birth_time_utc.replace(tzinfo=UTC),profile.location.timezone,float(profile.location.latitude),float(profile.location.longitude),profile.location.city,profile.location.state,profile.location.country,profile.full_name,profile.id,convention,reference,DetailLevel.ANTARDASHA))
    if "forecast" in sections:
        window=(reference.astimezone(UTC),reference.astimezone(UTC)+FORECAST_SPAN)
        calculator=TransitCalculator()
        data["forecast_window"]=window
        data["transits"]={planet:calculator.segments(planet,*window) for planet in TRANSIT_PLANETS}
    return data

def collect_matching(db: Session, first_id: int, second_id: int, first_role: str, second_role: str, ruleset: str):
    first,second=load_profile(db,first_id),load_profile(db,second_id); resolver=ProfileMoonResolver()
    def moon(profile,role):
        if profile.birth_time_unknown or profile.birth_time is None: return resolver.unknown_time(profile.birth_date,profile.location.timezone,role,profile.id,profile.full_name)
        require_exact(profile); return resolver.exact(profile.birth_time_utc.replace(tzinfo=UTC),role,profile.id,profile.full_name)
    return first,second,AshtakootaMatchingService().calculate(moon(first,first_role),moon(second,second_role),ruleset)
