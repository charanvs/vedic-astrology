from datetime import timedelta

from app.astrology.constants import NAKSHATRAS, NAKSHATRA_LORDS
from app.astrology.formatting import normalize_degrees
from app.astrology.nakshatra import nakshatra_for_longitude
from app.astrology.panchang.constants import MOVABLE_KARANAS, TITHI_NAMES, YOGA_NAMES
from app.astrology.panchang.constants import VARAS


def tithi_for_elongation(elongation: float) -> dict:
    number = int(normalize_degrees(elongation) / 12.0) + 1
    paksha = "Shukla Paksha" if number <= 15 else "Krishna Paksha"
    within = number if number <= 15 else number - 15
    if number == 30:
        name = "Amavasya"
    else:
        name = TITHI_NAMES[within - 1]
    return {"number": number, "name": name, "display_name": f"{paksha.replace(' Paksha', '')} {name}", "paksha": paksha}


def nakshatra_for_moon(longitude: float) -> dict:
    return nakshatra_for_longitude(longitude)


def yoga_for_sum(longitude_sum: float) -> dict:
    number = int(normalize_degrees(longitude_sum) / (360.0 / 27.0)) + 1
    return {"number": number, "name": YOGA_NAMES[number - 1]}


def karana_name(position: int) -> str:
    if not 0 <= position < 60:
        raise ValueError("Karana position must be between 0 and 59")
    if position == 0:
        return "Kimstughna"
    if position <= 56:
        return MOVABLE_KARANAS[(position - 1) % 7]
    return ("Shakuni", "Chatushpada", "Naga")[position - 57]


def karana_for_elongation(elongation: float) -> dict:
    position = int(normalize_degrees(elongation) / 6.0)
    return {
        "position": position + 1,
        "name": karana_name(position),
        "tithi_number": position // 2 + 1,
        "half": "first" if position % 2 == 0 else "second",
    }


def next_nakshatra(number: int) -> dict:
    next_number = number % 27 + 1
    return {"number": next_number, "name": NAKSHATRAS[next_number - 1], "lord": NAKSHATRA_LORDS[(next_number - 1) % 9]}


def vara_for_instant(instant_local, sunrise_for_civil_date) -> dict:
    effective_date = instant_local.date()
    if instant_local < sunrise_for_civil_date:
        effective_date -= timedelta(days=1)
    english, name, hindi = VARAS[effective_date.weekday()]
    return {"english_name": english, "name": name, "hindi_name": hindi, "effective_date": effective_date}
