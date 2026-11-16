"""Rule-based traditional readings keyed by verified calculation results.

Each reading is selected deterministically from app/reports/interpretations/<lang>.json
using the engine's stable identifiers, so the text can never contradict the chart.
"""
import json
from datetime import datetime
from decimal import Decimal
from functools import lru_cache
from zoneinfo import ZoneInfo
from app.reports.config import INTERPRETATION_ROOT, SUPPORTED_LANGUAGES
from app.reports.localization import MissingTranslationError

PLANETS = ("sun", "moon", "mars", "mercury", "jupiter", "venus", "saturn", "rahu", "ketu")
HOUSES = tuple(str(number) for number in range(1, 13))
REQUIRED_KEYS = {
    "lagna": set(HOUSES),
    "moon_rashi": set(HOUSES),
    "nakshatra": {str(number) for number in range(1, 28)},
    "mahadasha": set(PLANETS),
    "matching_bands": {"excellent", "good", "average", "low"},
}
KOOTAS = ("varna", "vashya", "tara", "yoni", "graha_maitri", "gana", "bhakoot", "nadi")
KOOTA_STATES = ("full", "partial", "none")
TRANSIT_PLANETS = ("jupiter", "saturn", "rahu")
GOCHARA_BODIES = ("jupiter", "saturn", "rahu", "ketu")
TEMPLATES = {"house_title": ("{planet}", "{house}"), "antardasha_title": ("{maha}", "{antar}"),
    "antardasha_house_template": ("{planet}", "{house}", "{focus}"), "transit_title": ("{planet}", "{sign}", "{house}"),
    "node_transit_title": ("{rahu_sign}", "{rahu_house}", "{ketu_sign}", "{ketu_house}")}


@lru_cache(maxsize=3)
def readings(language: str) -> dict:
    if language not in SUPPORTED_LANGUAGES: raise ValueError(f"Unsupported report language: {language}")
    values = json.loads((INTERPRETATION_ROOT / f"{language}.json").read_text(encoding="utf-8"))
    for group, keys in REQUIRED_KEYS.items():
        entries = values.get(group, {})
        missing = sorted(key for key in keys if not (entries.get(key, {}).get("title") and entries.get(key, {}).get("text")))
        if missing: raise MissingTranslationError(f"Missing {language} interpretation entries in {group}: {', '.join(missing)}")
    names, ordinals, houses = values.get("planet_names", {}), values.get("house_ordinals", {}), values.get("planet_house", {})
    missing = [f"planet_names.{p}" for p in PLANETS if not names.get(p)] + [f"house_ordinals.{h}" for h in HOUSES if not ordinals.get(h)]
    missing += [f"planet_house.{p}.{h}" for p in PLANETS for h in HOUSES if not houses.get(p, {}).get(h)]
    kootas = values.get("matching_kootas", {})
    missing += [f"matching_kootas.{k}.{f}" for k in KOOTAS for f in ("title", *KOOTA_STATES) if not kootas.get(k, {}).get(f)]
    missing += [f"{group}.{h}" for group in ("sign_names", "house_focus") for h in HOUSES if not values.get(group, {}).get(h)]
    missing += [f"antardasha.{p}" for p in PLANETS if not values.get("antardasha", {}).get(p)]
    missing += [f"gochara.{p}.{h}" for p in GOCHARA_BODIES for h in HOUSES if not values.get("gochara", {}).get(p, {}).get(h)]
    missing += [key for key, placeholders in TEMPLATES.items() if not all(p in values.get(key, "") for p in placeholders)]
    if missing: raise MissingTranslationError(f"Missing {language} interpretation entries: {', '.join(missing)}")
    return values


def build_interpretation(d1: dict, dasha: dict, language: str) -> list[dict]:
    values = readings(language)
    moon = next(planet for planet in d1["planets"] if planet["identifier"] == "moon")
    mahadasha = dasha["current"]["mahadasha"]
    return [
        {"label_key": "lagna", **values["lagna"][str(d1["lagna"]["rashi"]["number"])]},
        {"label_key": "moon_rashi", **values["moon_rashi"][str(moon["rashi"]["number"])]},
        {"label_key": "birth_nakshatra", **values["nakshatra"][str(moon["nakshatra"]["number"])]},
        {"label_key": "current_mahadasha", **values["mahadasha"][mahadasha["planet_identifier"]], "period": (mahadasha["start_local"].date(), mahadasha["end_local"].date())},
    ]


def build_house_readings(d1: dict, language: str) -> list[dict]:
    values = readings(language)
    by_planet = {planet["identifier"]: planet for planet in d1["planets"]}
    items = []
    for identifier in PLANETS:
        house = str(by_planet[identifier]["house"])
        title = values["house_title"].format(planet=values["planet_names"][identifier], house=values["house_ordinals"][house])
        items.append({"planet": identifier, "house": int(house), "title": title, "text": values["planet_house"][identifier][house]})
    return items


def score_band(total: Decimal) -> str:
    if total >= 33: return "excellent"
    if total >= 25: return "good"
    if total >= 18: return "average"
    return "low"


def koota_state(score: Decimal, maximum: Decimal) -> str:
    if score >= maximum: return "full"
    return "partial" if score > 0 else "none"


def build_matching_interpretation(result: dict, language: str) -> dict:
    values = readings(language)
    by_id = {koota["id"]: koota for koota in result["kootas"]}
    kootas = []
    for identifier in KOOTAS:
        koota, entry = by_id[identifier], values["matching_kootas"][identifier]
        kootas.append({"id": identifier, "title": entry["title"], "score": koota["score"], "maximum": koota["maximum"], "text": entry[koota_state(koota["score"], koota["maximum"])]})
    return {"band": values["matching_bands"][score_band(Decimal(result["total_score"]))], "kootas": kootas}


def build_forecast(d1: dict, dasha: dict, transits: dict, window: tuple[datetime, datetime], timezone: str, language: str) -> dict:
    values, zone, (start, end) = readings(language), ZoneInfo(timezone), window
    names, ordinals = values["planet_names"], values["house_ordinals"]
    houses = {planet["identifier"]: str(planet["house"]) for planet in d1["planets"]}
    moon_sign = next(planet for planet in d1["planets"] if planet["identifier"] == "moon")["rashi"]["number"]
    periods = []
    for mahadasha in dasha["mahadashas"]:
        for antardasha in mahadasha["children"]:
            if antardasha["end_utc"] <= start or antardasha["start_utc"] >= end: continue
            lord, house = antardasha["planet_identifier"], houses[antardasha["planet_identifier"]]
            focus = values["antardasha_house_template"].format(planet=names[lord], house=ordinals[house], focus=values["house_focus"][house])
            periods.append({"title": values["antardasha_title"].format(maha=names[mahadasha["planet_identifier"]], antar=names[lord]),
                "start": antardasha["start_local"].date(), "end": antardasha["end_local"].date(),
                "current": antardasha["start_utc"] <= start < antardasha["end_utc"], "text": f"{values['antardasha'][lord]} {focus}"})
    items = []
    for planet in TRANSIT_PLANETS:
        for segment in transits[planet]:
            house = str((segment.sign - moon_sign) % 12 + 1)
            item = {"planet": planet, "sign": segment.sign, "house": int(house),
                "start": segment.start_utc.astimezone(zone).date(), "end": segment.end_utc.astimezone(zone).date(),
                "current": segment.start_utc <= start < segment.end_utc}
            if planet == "rahu":
                ketu_sign = (segment.sign + 5) % 12 + 1
                ketu_house = str((ketu_sign - moon_sign) % 12 + 1)
                item.update(ketu_sign=ketu_sign, ketu_house=int(ketu_house), text=f"{values['gochara']['rahu'][house]} {values['gochara']['ketu'][ketu_house]}",
                    title=values["node_transit_title"].format(rahu_sign=values["sign_names"][str(segment.sign)], rahu_house=ordinals[house],
                        ketu_sign=values["sign_names"][str(ketu_sign)], ketu_house=ordinals[ketu_house]))
            else:
                item.update(text=values["gochara"][planet][house],
                    title=values["transit_title"].format(planet=names[planet], sign=values["sign_names"][str(segment.sign)], house=ordinals[house]))
            items.append(item)
    items.sort(key=lambda item: (item["start"], TRANSIT_PLANETS.index(item["planet"])))
    return {"periods": periods, "transits": items}
