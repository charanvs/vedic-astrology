"""Sidereal sign-ingress timelines for slow-moving planets (Gochara).

Positions come from the same Lahiri-configured Ephemeris facade as the natal chart.
Signs are scanned daily and each change is bisected to one minute, so retrograde
re-entries into a previous sign appear as separate segments.
"""
from dataclasses import dataclass
from datetime import UTC, datetime, timedelta

from app.astrology.config import CalculationSettings, get_calculation_settings
from app.astrology.ephemeris import Ephemeris
from app.astrology.julian import utc_to_julian_day

BODIES = {"jupiter": "JUPITER", "saturn": "SATURN", "rahu": "MEAN_NODE"}
SCAN_MARGIN = timedelta(days=1300)
STEP = timedelta(days=1)
PRECISION = timedelta(minutes=1)


@dataclass(frozen=True)
class SignSegment:
    planet: str
    sign: int
    start_utc: datetime
    end_utc: datetime


class TransitCalculator:
    def __init__(self, settings: CalculationSettings | None = None):
        self.settings = settings or get_calculation_settings()
        self.ephemeris = Ephemeris(self.settings)

    def sign_at(self, planet: str, instant: datetime) -> int:
        julian = utc_to_julian_day(instant.astimezone(UTC), self.settings.calendar)
        values, _, _ = self.ephemeris.calculate_ut(julian.julian_day_ut, BODIES[planet])
        return int((float(values[0]) % 360.0) // 30) + 1

    def _boundary(self, planet: str, inside: datetime, outside: datetime, sign: int) -> datetime:
        while outside - inside > PRECISION:
            middle = inside + (outside - inside) / 2
            if self.sign_at(planet, middle) == sign: inside = middle
            else: outside = middle
        return outside

    def segments(self, planet: str, start: datetime, end: datetime) -> list[SignSegment]:
        """Complete sign segments overlapping [start, end), with true ingress and egress instants."""
        cursor, limit = start - SCAN_MARGIN, end + SCAN_MARGIN
        current, segment_start, found = self.sign_at(planet, cursor), None, []
        while cursor < limit:
            following = cursor + STEP
            sign = self.sign_at(planet, following)
            if sign != current:
                boundary = self._boundary(planet, cursor, following, current)
                if segment_start is not None: found.append(SignSegment(planet, current, segment_start, boundary))
                segment_start, current = boundary, sign
            cursor = following
        overlapping = [segment for segment in found if segment.end_utc > start and segment.start_utc < end]
        if not overlapping or overlapping[-1].end_utc < end:
            raise ValueError(f"Transit scan for {planet} did not cover the requested window")
        return overlapping
