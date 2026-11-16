from app.astrology.ephemeris import Ephemeris
from app.astrology.formatting import degrees_to_dms


def calculate_lahiri_ayanamsa(julian_day_ut: float, ephemeris: Ephemeris) -> dict:
    degrees = ephemeris.ayanamsa_ut(julian_day_ut)
    return {
        "degrees": degrees,
        "formatted": degrees_to_dms(degrees),
        "mode": "SIDM_LAHIRI",
        "name": "Lahiri (Chitrapaksha)",
    }
