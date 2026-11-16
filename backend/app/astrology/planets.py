from app.astrology.config import CalculationSettings
from app.astrology.constants import GRAHAS
from app.astrology.ephemeris import Ephemeris
from app.astrology.formatting import degrees_to_dms, normalize_degrees
from app.astrology.nakshatra import nakshatra_for_longitude
from app.astrology.rashi import rashi_for_longitude


def motion_from_speed(speed: float, threshold: float) -> str:
    if abs(speed) <= threshold:
        return "stationary"
    return "retrograde" if speed < 0 else "direct"


def _position(
    identifier: str,
    english: str,
    sanskrit: str,
    hindi: str,
    longitude: float,
    latitude: float | None,
    speed: float | None,
    settings: CalculationSettings,
    flags: int | None,
    source: str,
) -> dict:
    normalized = normalize_degrees(longitude)
    rashi = rashi_for_longitude(normalized)
    nakshatra = nakshatra_for_longitude(normalized)
    return {
        "identifier": identifier,
        "english_name": english,
        "sanskrit_name": sanskrit,
        "hindi_name": hindi,
        "longitude": normalized,
        "longitude_formatted": degrees_to_dms(normalized),
        "latitude": latitude,
        "longitude_speed": speed,
        "motion": motion_from_speed(speed, settings.stationary_threshold) if speed is not None else "derived",
        "retrograde": speed < -settings.stationary_threshold if speed is not None else None,
        "rashi": rashi,
        "nakshatra": nakshatra,
        "house": None,
        "calculation_flags": flags,
        "ephemeris_source": source,
        "convention": "geocentric sidereal Lahiri; apparent ecliptic longitude",
    }


def calculate_planets(
    julian_day_ut: float,
    ephemeris: Ephemeris,
    settings: CalculationSettings,
) -> list[dict]:
    positions = []
    for identifier, english, sanskrit, hindi, body_name in GRAHAS:
        values, flags, source = ephemeris.calculate_ut(julian_day_ut, body_name)
        positions.append(
            _position(
                identifier, english, sanskrit, hindi,
                values[0], values[1], values[3], settings, flags, source,
            )
        )
    rahu = positions[-1]
    positions.append(
        _position(
            "ketu", "Ketu", "Ketu", "केतु",
            rahu["longitude"] + 180.0,
            None,
            None,
            settings,
            rahu["calculation_flags"],
            rahu["ephemeris_source"],
        )
    )
    positions[-1]["convention"] = "derived point exactly opposite mean Rahu; no independent latitude or speed"
    return positions
