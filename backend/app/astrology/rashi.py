from app.astrology.constants import RASHIS
from app.astrology.formatting import normalize_degrees


def rashi_for_longitude(longitude: float) -> dict:
    normalized = normalize_degrees(longitude)
    index = min(int(normalized // 30.0), 11)
    sanskrit, english, hindi = RASHIS[index]
    return {
        "number": index + 1,
        "name": sanskrit,
        "english_name": english,
        "hindi_name": hindi,
        "longitude_within": normalized - index * 30.0,
    }


def whole_sign_house(planet_rashi_number: int, lagna_rashi_number: int) -> int:
    return ((planet_rashi_number - lagna_rashi_number) % 12) + 1


def whole_sign_houses(lagna_rashi_number: int) -> list[dict]:
    return [
        {"house": house, "rashi": ((lagna_rashi_number + house - 2) % 12) + 1}
        for house in range(1, 13)
    ]
