from datetime import UTC, date, datetime, time, timedelta
from zoneinfo import ZoneInfo

from app.astrology.ephemeris import Ephemeris
from app.astrology.julian import utc_to_julian_day

J2000 = datetime(2000, 1, 1, 12, tzinfo=UTC)


def julian_day_to_utc(julian_day: float) -> datetime:
    return J2000 + timedelta(days=julian_day - 2451545.0)


def solar_event(
    civil_date: date,
    timezone: ZoneInfo,
    latitude: float,
    longitude: float,
    elevation: float,
    event: str,
    ephemeris: Ephemeris,
) -> datetime | None:
    local_midnight = datetime.combine(civil_date, time.min, timezone)
    start_utc = local_midnight.astimezone(UTC)
    event_jd = ephemeris.rise_set_ut(
        utc_to_julian_day(start_utc).julian_day_ut,
        latitude,
        longitude,
        elevation,
        event,
    )
    if event_jd is None:
        return None
    result = julian_day_to_utc(event_jd).astimezone(timezone)
    return result if result.date() == civil_date else None
