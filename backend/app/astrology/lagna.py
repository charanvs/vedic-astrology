from app.astrology.ephemeris import Ephemeris
from app.astrology.formatting import degrees_to_dms
from app.astrology.rashi import rashi_for_longitude, whole_sign_houses


def calculate_lagna(
    julian_day_ut: float,
    latitude: float,
    longitude: float,
    ephemeris: Ephemeris,
) -> dict:
    ascendant = ephemeris.ascendant_ut(julian_day_ut, latitude, longitude)
    rashi = rashi_for_longitude(ascendant)
    return {
        "longitude": ascendant,
        "longitude_formatted": degrees_to_dms(ascendant),
        "rashi": rashi,
        "method": "Swiss Ephemeris houses_ex sidereal ascendant with SIDM_LAHIRI",
        "whole_sign_houses": whole_sign_houses(rashi["number"]),
    }
