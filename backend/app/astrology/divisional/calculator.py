from decimal import Decimal

from app.astrology.constants import RASHIS
from app.astrology.divisional.boundaries import decimal_degrees, is_boundary_near
from app.astrology.divisional.constants import SUPPORTED_CHARTS
from app.astrology.divisional.dashamsha import dashamsha_position
from app.astrology.divisional.navamsha import navamsha_position
from app.astrology.formatting import degrees_to_dms
from app.astrology.rashi import whole_sign_house


def _rashi(number: int, degree: Decimal) -> dict:
    name, english_name, hindi_name = RASHIS[number - 1]
    return {"number": number, "name": name, "english_name": english_name,
            "hindi_name": hindi_name, "longitude_within": float(degree)}


def _houses(lagna_sign: int, planets: list[dict]) -> list[dict]:
    result = []
    for house_number in range(1, 13):
        sign_number = ((lagna_sign + house_number - 2) % 12) + 1
        name, english_name, hindi_name = RASHIS[sign_number - 1]
        result.append({
            "house_number": house_number, "rashi_number": sign_number,
            "rashi_name": name, "rashi_english_name": english_name,
            "rashi_hindi_name": hindi_name,
            "planet_identifiers": [p["identifier"] for p in planets if p["house"] == house_number],
            "is_lagna": house_number == 1,
        })
    return result


def build_divisional_chart(d1: dict, chart_type: str) -> dict:
    key = chart_type.upper()
    if key not in SUPPORTED_CHARTS:
        raise ValueError("Supported divisional charts are D9 and D10")
    transform = navamsha_position if key == "D9" else dashamsha_position
    divisions = SUPPORTED_CHARTS[key]["division"]
    warnings = list(d1.get("warnings", []))

    lagna_source = decimal_degrees(d1["lagna"]["longitude"])
    lagna_result = transform(lagna_source)
    lagna_original_sign = int(lagna_source // Decimal(30)) + 1
    lagna_near = is_boundary_near(lagna_source % Decimal(30), divisions)
    if lagna_near:
        warnings.append(f"Lagna is within 1 arcminute of a {key} division boundary; verify the recorded birth time.")
    lagna = {
        "longitude": float(lagna_result["longitude"]),
        "longitude_formatted": degrees_to_dms(float(lagna_result["longitude"])),
        "rashi": _rashi(lagna_result["sign_number"], lagna_result["degree"]),
        "method": f"Parashari {SUPPORTED_CHARTS[key]['name']} transformation of the D1 Lagna",
        "whole_sign_houses": [{"house": house, "rashi": ((lagna_result["sign_number"] + house - 2) % 12) + 1} for house in range(1, 13)],
        "original_longitude": float(lagna_source),
        "original_rashi_number": lagna_original_sign,
        "division_number": lagna_result["division_number"],
        "boundary_near": lagna_near,
    }

    planets = []
    for original in d1["planets"]:
        source = decimal_degrees(original["longitude"])
        result = transform(source)
        original_sign = int(source // Decimal(30)) + 1
        sign_number = result["sign_number"]
        near = is_boundary_near(source % Decimal(30), divisions)
        if near:
            warnings.append(f"{original['english_name']} is within 1 arcminute of a {key} division boundary.")
        planet = dict(original)
        planet.update({
            "longitude": float(result["longitude"]),
            "longitude_formatted": degrees_to_dms(float(result["longitude"])),
            "rashi": _rashi(sign_number, result["degree"]),
            "house": whole_sign_house(sign_number, lagna_result["sign_number"]),
            "original_longitude": float(source),
            "original_longitude_formatted": original["longitude_formatted"],
            "original_rashi": original["rashi"],
            "division_number": result["division_number"],
            "vargottama": key == "D9" and original_sign == sign_number,
            "boundary_near": near,
        })
        planets.append(planet)

    metadata = SUPPORTED_CHARTS[key]
    return {
        "chart_type": key, "chart_name": metadata["name"], "primary_use": metadata["primary_use"],
        "birth_datetime": d1["birth_datetime"], "location": d1["location"],
        "settings": d1["settings"], "julian_day_ut": d1["julian_day_ut"],
        "julian_day_calendar": d1["julian_day_calendar"], "ayanamsa": d1["ayanamsa"],
        "lagna": lagna, "planets": planets,
        "houses": _houses(lagna_result["sign_number"], planets),
        "whole_sign_houses": lagna["whole_sign_houses"], "engine": d1["engine"],
        "warnings": warnings,
        "calculation": {"system": "Parashari", "division": divisions,
            "segment_degrees": float(metadata["segment_degrees"]),
            "interval_semantics": "half-open [start, end); an exact boundary begins the next division",
            "boundary_warning_degrees": 1 / 60},
    }
