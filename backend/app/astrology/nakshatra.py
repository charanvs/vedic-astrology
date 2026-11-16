from app.astrology.constants import NAKSHATRAS, NAKSHATRA_LORDS
from app.astrology.formatting import normalize_degrees

NAKSHATRA_SPAN = 360.0 / 27.0
PADA_SPAN = NAKSHATRA_SPAN / 4.0


def nakshatra_for_longitude(longitude: float) -> dict:
    normalized = normalize_degrees(longitude)
    index = min(int(normalized / NAKSHATRA_SPAN), 26)
    longitude_within = normalized - index * NAKSHATRA_SPAN
    pada = min(int(longitude_within / PADA_SPAN), 3) + 1
    return {
        "number": index + 1,
        "name": NAKSHATRAS[index],
        "pada": pada,
        "longitude_within": longitude_within,
        "lord": NAKSHATRA_LORDS[index % len(NAKSHATRA_LORDS)],
    }
