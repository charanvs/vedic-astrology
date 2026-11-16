from dataclasses import asdict, dataclass
from datetime import UTC, date, datetime, timedelta
from time import perf_counter
from zoneinfo import ZoneInfo

from app.astrology.config import CalculationSettings, get_calculation_settings
from app.astrology.ephemeris import Ephemeris
from app.astrology.exceptions import SunEventUnavailableError
from app.astrology.julian import utc_to_julian_day
from app.astrology.panchang.constants import ELEMENT_EXPLANATIONS, VARAS
from app.astrology.panchang.elements import (
    karana_for_elongation, nakshatra_for_moon, next_nakshatra,
    tithi_for_elongation, yoga_for_sum,
)
from app.astrology.panchang.sunrise import solar_event
from app.astrology.panchang.transitions import AngularTransition, find_angular_transitions


@dataclass(frozen=True)
class PanchangInput:
    civil_date: date
    latitude: float
    longitude: float
    timezone: str
    city: str
    state: str | None
    country: str
    location_id: int | None = None
    elevation: float = 0.0


class DailyPanchangService:
    def __init__(self, settings: CalculationSettings | None = None):
        self.settings = settings or get_calculation_settings()
        self.ephemeris = Ephemeris(self.settings)
        self._position_cache: dict[tuple[str, datetime], float] = {}

    def _longitude(self, body: str, instant: datetime) -> float:
        utc = instant.astimezone(UTC)
        key = (body, utc)
        if key not in self._position_cache:
            jd = utc_to_julian_day(utc).julian_day_ut
            values, _, _ = self.ephemeris.calculate_ut(jd, body)
            self._position_cache[key] = float(values[0]) % 360.0
        return self._position_cache[key]

    def _elongation(self, instant: datetime) -> float:
        return (self._longitude("MOON", instant) - self._longitude("SUN", instant)) % 360.0

    def _yoga_angle(self, instant: datetime) -> float:
        return (self._longitude("MOON", instant) + self._longitude("SUN", instant)) % 360.0

    @staticmethod
    def _stamp(instant: datetime, timezone: ZoneInfo) -> dict:
        return {"utc": instant.astimezone(UTC), "local": instant.astimezone(timezone)}

    def _element(
        self,
        name: str,
        sunrise_utc: datetime,
        next_sunrise_utc: datetime,
        timezone: ZoneInfo,
        span: float,
        angle_at,
        describe,
    ) -> tuple[dict, list[dict]]:
        transitions = find_angular_transitions(
            sunrise_utc - timedelta(days=3), next_sunrise_utc, span, angle_at
        )
        previous = [item for item in transitions if item.at_utc <= sunrise_utc]
        future = [item for item in transitions if item.at_utc > sunrise_utc]
        if not previous or not future:
            raise SunEventUnavailableError(f"Could not bracket the {name} active at sunrise")
        start, end = previous[-1], future[0]
        current = describe(angle_at(sunrise_utc))
        next_value = describe(angle_at(end.at_utc + timedelta(seconds=1)))
        daily = [item for item in future if item.at_utc <= next_sunrise_utc]
        transition_payloads = []
        for item in daily:
            before = describe(angle_at(item.at_utc - timedelta(seconds=1)))
            after = describe(angle_at(item.at_utc + timedelta(seconds=1)))
            transition_payloads.append({
                "element": name,
                "from_name": before["name"],
                "to_name": after["name"],
                **self._stamp(item.at_utc, timezone),
            })
        result = {
            **current,
            "active_at_sunrise": True,
            "start": self._stamp(start.at_utc, timezone),
            "end": self._stamp(end.at_utc, timezone),
            "next": next_value,
            "transitions": transition_payloads,
            "explanation": ELEMENT_EXPLANATIONS[name],
        }
        return result, transition_payloads

    def calculate(self, data: PanchangInput) -> dict:
        started = perf_counter()
        timezone = ZoneInfo(data.timezone)
        sunrise = solar_event(data.civil_date, timezone, data.latitude, data.longitude, data.elevation, "rise", self.ephemeris)
        next_sunrise = solar_event(data.civil_date + timedelta(days=1), timezone, data.latitude, data.longitude, data.elevation, "rise", self.ephemeris)
        sunset = solar_event(data.civil_date, timezone, data.latitude, data.longitude, data.elevation, "set", self.ephemeris)
        if sunrise is None:
            raise SunEventUnavailableError("Sunrise is unavailable for this location and local civil date")
        if next_sunrise is None:
            raise SunEventUnavailableError("Next sunrise is unavailable, so the Panchang day cannot be bounded")
        sunrise_utc, next_sunrise_utc = sunrise.astimezone(UTC), next_sunrise.astimezone(UTC)

        tithi, tithi_events = self._element("tithi", sunrise_utc, next_sunrise_utc, timezone, 12.0, self._elongation, tithi_for_elongation)
        nakshatra, nakshatra_events = self._element("nakshatra", sunrise_utc, next_sunrise_utc, timezone, 360.0 / 27.0, lambda instant: self._longitude("MOON", instant), nakshatra_for_moon)
        yoga, yoga_events = self._element("yoga", sunrise_utc, next_sunrise_utc, timezone, 360.0 / 27.0, self._yoga_angle, yoga_for_sum)
        karana, karana_events = self._element("karana", sunrise_utc, next_sunrise_utc, timezone, 6.0, self._elongation, karana_for_elongation)
        nakshatra["next"] = {**next_nakshatra(nakshatra["number"]), "pada": 1}

        weekday = VARAS[sunrise.weekday()]
        vara = {
            "english_name": weekday[0], "name": weekday[1], "hindi_name": weekday[2],
            "local_civil_date": data.civil_date,
            "day_start": self._stamp(sunrise_utc, timezone),
            "day_end": self._stamp(next_sunrise_utc, timezone),
            "explanation": ELEMENT_EXPLANATIONS["vara"],
        }
        solar = {
            "sunrise": self._stamp(sunrise_utc, timezone),
            "sunset": self._stamp(sunset.astimezone(UTC), timezone) if sunset else None,
            "next_sunrise": self._stamp(next_sunrise_utc, timezone),
            "day_duration_seconds": round((sunset - sunrise).total_seconds()) if sunset else None,
            "status": "complete" if sunset else "sunset_unavailable",
            "convention": "Swiss Ephemeris apparent upper solar limb with standard atmospheric refraction; pressure estimated from elevation, temperature 15°C",
        }
        timeline = [
            {"event_type": "sunrise", "label": "Sunrise", **self._stamp(sunrise_utc, timezone)},
            *[{"event_type": event["element"], "label": f"{event['from_name']} → {event['to_name']}", "utc": event["utc"], "local": event["local"]} for event in (*tithi_events, *nakshatra_events, *yoga_events, *karana_events)],
        ]
        if sunset:
            timeline.append({"event_type": "sunset", "label": "Sunset", **self._stamp(sunset.astimezone(UTC), timezone)})
        timeline.append({"event_type": "next_sunrise", "label": "Next sunrise", **self._stamp(next_sunrise_utc, timezone)})
        timeline.sort(key=lambda item: item["utc"])

        engine = self.ephemeris.metadata()
        engine["calculation_duration_ms"] = round((perf_counter() - started) * 1000.0, 3)
        return {
            "civil_date": data.civil_date,
            "location": {
                "id": data.location_id, "city": data.city, "state": data.state,
                "country": data.country, "latitude": data.latitude,
                "longitude": data.longitude, "timezone": data.timezone,
                "elevation": data.elevation,
            },
            "panchang_day": {"start": self._stamp(sunrise_utc, timezone), "end": self._stamp(next_sunrise_utc, timezone), "definition": "local sunrise to next local sunrise"},
            "solar": solar,
            "tithi": tithi, "vara": vara, "nakshatra": nakshatra, "yoga": yoga, "karana": karana,
            "timeline": timeline,
            "settings": {
                **asdict(self.settings),
                "method": "Drik Ganita",
                "evaluation_instant": "local sunrise",
                "sun_moon_reference": "geocentric apparent ecliptic longitude",
            },
            "engine": engine,
            "warnings": [
                "Civil date changes at midnight; the traditional Panchang day changes at local sunrise.",
                "Panchang elements are astronomical calendar values, not personal predictions.",
            ],
        }
