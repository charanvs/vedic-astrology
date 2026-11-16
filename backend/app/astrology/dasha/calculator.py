from dataclasses import dataclass
from datetime import UTC, datetime
from decimal import Decimal, localcontext
from time import perf_counter
from zoneinfo import ZoneInfo

from app.astrology.config import CalculationSettings, get_calculation_settings
from app.astrology.dasha.balance import calculate_nakshatra_balance
from app.astrology.dasha.constants import DASHA_YEARS, TOTAL_DASHA_YEARS, sequence_from
from app.astrology.dasha.exceptions import DashaReferenceOutOfRange
from app.astrology.dasha.settings import DashaYearConvention, DetailLevel, SECONDS_PER_DAY
from app.astrology.dasha.timeline import (
    DashaPeriod,
    decimal_seconds_to_timedelta,
    duration_seconds,
    find_active,
    partition_period,
    period_payload,
)
from app.astrology.ephemeris import Ephemeris
from app.astrology.julian import utc_to_julian_day
from app.astrology.rashi import rashi_for_longitude


@dataclass(frozen=True)
class DashaInput:
    birth_utc: datetime
    timezone: str
    latitude: float
    longitude: float
    city: str
    state: str | None
    country: str
    full_name: str | None = None
    profile_id: int | None = None
    year_convention: DashaYearConvention = DashaYearConvention.TROPICAL_365_25
    reference_utc: datetime | None = None
    detail_level: DetailLevel = DetailLevel.ANTARDASHA


class VimshottariDashaService:
    def __init__(self, settings: CalculationSettings | None = None):
        self.settings = settings or get_calculation_settings()
        self.ephemeris = Ephemeris(self.settings)

    def _moon_longitude(self, birth_utc: datetime) -> float:
        julian = utc_to_julian_day(birth_utc, self.settings.calendar)
        values, _, _ = self.ephemeris.calculate_ut(julian.julian_day_ut, "MOON")
        return float(values[0]) % 360.0

    def calculate(self, data: DashaInput, moon_longitude: float | None = None) -> dict:
        started = perf_counter()
        timezone = ZoneInfo(data.timezone)
        birth_utc = data.birth_utc.astimezone(UTC)
        reference_utc = (data.reference_utc or datetime.now(UTC)).astimezone(UTC)
        balance = calculate_nakshatra_balance(
            self._moon_longitude(birth_utc) if moon_longitude is None else moon_longitude
        )
        year_seconds = data.year_convention.days * SECONDS_PER_DAY
        with localcontext() as context:
            context.prec = 40
            first_start = birth_utc - decimal_seconds_to_timedelta(balance.elapsed_years * year_seconds)
            periods: list[DashaPeriod] = []
            cursor = first_start
            for lord in sequence_from(balance.lord):
                years = DASHA_YEARS[lord]
                end = cursor + decimal_seconds_to_timedelta(years * year_seconds)
                period = DashaPeriod("mahadasha", lord, cursor, end, years)
                if data.detail_level in {DetailLevel.ANTARDASHA, DetailLevel.PRATYANTARDASHA}:
                    period.children = partition_period(period, "antardasha")
                    if data.detail_level is DetailLevel.PRATYANTARDASHA:
                        for antardasha in period.children:
                            antardasha.children = partition_period(antardasha, "pratyantardasha")
                periods.append(period)
                cursor = end

        if not periods[0].start_utc <= reference_utc < periods[-1].end_utc:
            raise DashaReferenceOutOfRange(
                f"Reference instant must be within {periods[0].start_utc.isoformat()} and {periods[-1].end_utc.isoformat()}"
            )
        active_maha = find_active(periods, reference_utc)
        if active_maha is None:
            raise DashaReferenceOutOfRange("No Mahadasha covers the selected reference instant")
        active_antardashas = active_maha.children or partition_period(active_maha, "antardasha")
        active_antar = find_active(active_antardashas, reference_utc)
        if active_antar is None:
            raise DashaReferenceOutOfRange("No Antardasha covers the selected reference instant")
        active_pratyantardashas = active_antar.children or partition_period(
            active_antar, "pratyantardasha"
        )
        active_pratyantar = find_active(active_pratyantardashas, reference_utc)
        if active_pratyantar is None:
            raise DashaReferenceOutOfRange("No Pratyantardasha covers the selected reference instant")

        def serialize(period: DashaPeriod) -> dict:
            payload = period_payload(period, timezone, birth_utc, reference_utc)
            payload["children"] = [serialize(child) for child in period.children]
            return payload

        rashi = rashi_for_longitude(float(balance.moon_longitude))
        engine = self.ephemeris.metadata()
        engine["calculation_duration_ms"] = round((perf_counter() - started) * 1000, 3)
        return {
            "profile": {
                "id": data.profile_id, "full_name": data.full_name, "birth_utc": birth_utc,
                "birth_local": birth_utc.astimezone(timezone), "timezone": data.timezone,
                "location": {"city": data.city, "state": data.state, "country": data.country,
                             "latitude": data.latitude, "longitude": data.longitude},
            },
            "birth_moon": {
                "sidereal_longitude": balance.moon_longitude, "rashi": rashi,
                "nakshatra_number": balance.nakshatra_number, "nakshatra": balance.nakshatra_name,
                "pada": balance.pada, "lord": balance.lord,
                "position_within_degrees": balance.position_degrees,
                "elapsed_fraction": balance.elapsed_fraction, "remaining_fraction": balance.remaining_fraction,
            },
            "balance": {
                "starting_lord": balance.lord, "full_duration_years": balance.full_years,
                "elapsed_years": balance.elapsed_years, "remaining_years": balance.remaining_years,
                "elapsed_days": balance.elapsed_years * data.year_convention.days,
                "remaining_days": balance.remaining_years * data.year_convention.days,
                "theoretical_start_utc": periods[0].start_utc,
                "theoretical_start_local": periods[0].start_utc.astimezone(timezone),
                "first_mahadasha_end_utc": periods[0].end_utc,
                "first_mahadasha_end_local": periods[0].end_utc.astimezone(timezone),
            },
            "reference": {"utc": reference_utc, "local": reference_utc.astimezone(timezone)},
            "current": {
                "mahadasha": period_payload(active_maha, timezone, birth_utc, reference_utc),
                "antardasha": period_payload(active_antar, timezone, birth_utc, reference_utc),
                "pratyantardasha": period_payload(active_pratyantar, timezone, birth_utc, reference_utc),
                "remaining_seconds": duration_seconds(reference_utc, active_pratyantar.end_utc),
            },
            "mahadashas": [serialize(period) for period in periods],
            "settings": {
                "year_convention": data.year_convention.value,
                "year_convention_label": data.year_convention.label,
                "days_per_dasha_year": data.year_convention.days, "seconds_per_day": SECONDS_PER_DAY,
                "detail_level": data.detail_level.value, "interval_semantics": "[start, end)",
                "total_cycle_years": TOTAL_DASHA_YEARS, "ayanamsa": self.settings.ayanamsa,
                "zodiac": self.settings.zodiac, "planetary_reference": self.settings.planetary_reference,
            },
            "engine": engine,
            "metadata": {
                "moon_source": "Step 6 Swiss Ephemeris Lahiri sidereal geocentric longitude",
                "arithmetic": "Decimal proportional offsets rounded half-even to nearest microsecond",
                "timezone": data.timezone,
            },
            "warnings": [
                "Vimshottari Dasha is a traditional astrological timing system, not a scientific prediction model.",
                "Changing the fixed Dasha-year convention changes period boundary dates.",
            ],
        }
