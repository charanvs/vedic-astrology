import math
from dataclasses import dataclass
from datetime import UTC, datetime

from app.astrology.exceptions import UnsupportedDateError

MINIMUM_YEAR = 1600
MAXIMUM_YEAR = 2399


@dataclass(frozen=True)
class JulianDayResult:
    julian_day_ut: float
    utc_datetime: datetime
    calendar: str
    time_scale_note: str


def utc_to_julian_day(value: datetime, calendar: str = "proleptic Gregorian") -> JulianDayResult:
    if value.tzinfo is None or value.utcoffset() is None:
        raise UnsupportedDateError("UTC datetime must be timezone-aware")
    utc_value = value.astimezone(UTC)
    if not MINIMUM_YEAR <= utc_value.year <= MAXIMUM_YEAR:
        raise UnsupportedDateError(f"Supported Gregorian years are {MINIMUM_YEAR} through {MAXIMUM_YEAR}")
    if calendar != "proleptic Gregorian":
        raise UnsupportedDateError("Only the proleptic Gregorian calendar is supported")
    year, month = utc_value.year, utc_value.month
    if month <= 2:
        year -= 1
        month += 12
    century = math.floor(year / 100)
    correction = 2 - century + math.floor(century / 4)
    seconds = (
        utc_value.hour * 3600
        + utc_value.minute * 60
        + utc_value.second
        + utc_value.microsecond / 1_000_000
    )
    jd = (
        math.floor(365.25 * (year + 4716))
        + math.floor(30.6001 * (month + 1))
        + utc_value.day
        + correction
        - 1524.5
        + seconds / 86400.0
    )
    return JulianDayResult(
        julian_day_ut=jd,
        utc_datetime=utc_value,
        calendar=calendar,
        time_scale_note="Julian Day UT is supplied to calc_ut; Swiss Ephemeris applies its Delta-T model internally.",
    )
