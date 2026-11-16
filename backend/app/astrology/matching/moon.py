from datetime import UTC, date, datetime, time, timedelta
from decimal import Decimal
from zoneinfo import ZoneInfo

from app.astrology.config import CalculationSettings, get_calculation_settings
from app.astrology.ephemeris import Ephemeris
from app.astrology.julian import utc_to_julian_day
from app.astrology.matching.calculator import PartnerMoon
from app.astrology.matching.exceptions import IndeterminateMoonError
from app.astrology.nakshatra import nakshatra_for_longitude
from app.astrology.rashi import rashi_for_longitude


class ProfileMoonResolver:
    def __init__(self, settings: CalculationSettings | None = None):
        self.settings = settings or get_calculation_settings()
        self.ephemeris = Ephemeris(self.settings)

    def longitude_at(self, instant: datetime) -> Decimal:
        julian = utc_to_julian_day(instant.astimezone(UTC), self.settings.calendar)
        values, _, _ = self.ephemeris.calculate_ut(julian.julian_day_ut, "MOON")
        return Decimal(str(float(values[0]) % 360.0))

    def exact(self, instant: datetime, role: str, profile_id: int, name: str) -> PartnerMoon:
        return self._build(self.longitude_at(instant), role, "exact", profile_id, name)

    def unknown_time(self, birth_date: date, timezone_name: str, role: str,
                     profile_id: int, name: str) -> PartnerMoon:
        zone = ZoneInfo(timezone_name)
        local_start = datetime.combine(birth_date, time.min, tzinfo=zone)
        local_end = datetime.combine(birth_date + timedelta(days=1), time.min, tzinfo=zone)
        start_utc, end_utc = local_start.astimezone(UTC), local_end.astimezone(UTC)
        span = end_utc - start_utc
        samples = []
        # Half-hour sampling is conservative for a Moon that traverses roughly one
        # Nakshatra daily and avoids silently substituting a fabricated birth time.
        steps = max(1, int(span.total_seconds() // 1800))
        span_microseconds = span.days * 86_400_000_000 + span.seconds * 1_000_000 + span.microseconds
        for step in range(steps + 1):
            instant = start_utc + timedelta(microseconds=span_microseconds * step // steps)
            if instant >= end_utc:
                instant = end_utc - timedelta(microseconds=1)
            longitude = self.longitude_at(instant)
            rashi = rashi_for_longitude(float(longitude))
            nakshatra = nakshatra_for_longitude(float(longitude))
            samples.append((longitude, rashi["number"], nakshatra["number"], nakshatra["pada"]))
        placements = {(item[1], item[2]) for item in samples}
        if len(placements) != 1:
            labels = sorted({f"Rashi {rashi}, Nakshatra {nakshatra}" for rashi, nakshatra in placements})
            raise IndeterminateMoonError(
                "Unknown birth time crosses a Moon Rashi or Nakshatra boundary; definitive matching is unavailable. Possible placements: " + "; ".join(labels)
            )
        representative = samples[len(samples)//2][0]
        return self._build(representative, role, "date_unambiguous", profile_id, name,
            start_utc.isoformat(), end_utc.isoformat())

    @staticmethod
    def _build(longitude: Decimal, role: str, precision: str, profile_id: int, name: str,
               start: str | None = None, end: str | None = None) -> PartnerMoon:
        rashi, nakshatra = rashi_for_longitude(float(longitude)), nakshatra_for_longitude(float(longitude))
        return PartnerMoon(role=role, longitude=longitude, rashi_number=rashi["number"],
            nakshatra_number=nakshatra["number"], pada=nakshatra["pada"], precision=precision,
            uncertainty_start_utc=start, uncertainty_end_utc=end, profile_id=profile_id, name=name)
