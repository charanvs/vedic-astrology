from dataclasses import asdict, dataclass
from datetime import datetime
from time import perf_counter

from app.astrology.ayanamsa import calculate_lahiri_ayanamsa
from app.astrology.config import CalculationSettings, get_calculation_settings
from app.astrology.ephemeris import Ephemeris
from app.astrology.julian import utc_to_julian_day
from app.astrology.lagna import calculate_lagna
from app.astrology.planets import calculate_planets
from app.astrology.rashi import rashi_for_longitude, whole_sign_house


@dataclass(frozen=True)
class CalculationInput:
    utc_datetime: datetime
    local_datetime: str
    timezone: str
    resolution_status: str
    latitude: float
    longitude: float
    city: str
    state: str | None
    country: str


class AstrologyCalculationService:
    def __init__(self, settings: CalculationSettings | None = None):
        self.settings = settings or get_calculation_settings()
        self.ephemeris = Ephemeris(self.settings)

    def calculate(self, data: CalculationInput) -> dict:
        started = perf_counter()
        julian = utc_to_julian_day(data.utc_datetime, self.settings.calendar)
        ayanamsa = calculate_lahiri_ayanamsa(julian.julian_day_ut, self.ephemeris)
        lagna = calculate_lagna(
            julian.julian_day_ut, data.latitude, data.longitude, self.ephemeris
        )
        planets = calculate_planets(julian.julian_day_ut, self.ephemeris, self.settings)
        for planet in planets:
            planet["house"] = whole_sign_house(
                planet["rashi"]["number"], lagna["rashi"]["number"]
            )
        houses = []
        for assignment in lagna["whole_sign_houses"]:
            rashi = rashi_for_longitude((assignment["rashi"] - 1) * 30.0)
            houses.append({
                "house_number": assignment["house"],
                "rashi_number": rashi["number"],
                "rashi_name": rashi["name"],
                "rashi_english_name": rashi["english_name"],
                "rashi_hindi_name": rashi["hindi_name"],
                "planet_identifiers": [
                    planet["identifier"] for planet in planets
                    if planet["house"] == assignment["house"]
                ],
                "is_lagna": assignment["house"] == 1,
            })
        engine = self.ephemeris.metadata()
        engine["calculation_duration_ms"] = round((perf_counter() - started) * 1000.0, 3)
        return {
            "birth_datetime": {
                "local_datetime": data.local_datetime,
                "utc_datetime": julian.utc_datetime.isoformat().replace("+00:00", "Z"),
                "timezone": data.timezone,
                "resolution_status": data.resolution_status,
            },
            "location": {
                "city": data.city,
                "state": data.state,
                "country": data.country,
                "latitude": data.latitude,
                "longitude": data.longitude,
            },
            "settings": asdict(self.settings),
            "julian_day_ut": julian.julian_day_ut,
            "julian_day_calendar": julian.calendar,
            "ayanamsa": ayanamsa,
            "lagna": lagna,
            "planets": planets,
            "houses": houses,
            "whole_sign_houses": lagna["whole_sign_houses"],
            "engine": engine,
            "warnings": [
                julian.time_scale_note,
                "Whole-sign houses are sign-relative assignments, not quadrant cusps.",
                "Astronomical output is not a predictive interpretation.",
            ],
        }
