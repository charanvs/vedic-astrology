"""Offline city search backed by a bundled GeoNames export.

No external geocoding provider or API key is used. See
scripts/build_geocoding_dataset.py for how app/data/geocoding_cities.csv is built.
"""
from __future__ import annotations
import csv
from dataclasses import dataclass
from pathlib import Path

DATA_PATH = Path(__file__).resolve().parents[1] / "data" / "geocoding_cities.csv"


@dataclass(frozen=True)
class GeocodingCity:
    name: str
    state: str
    country: str
    country_code: str
    latitude: str
    longitude: str
    timezone: str
    search_key: str


def _load() -> list[GeocodingCity]:
    with DATA_PATH.open(encoding="utf-8") as handle:
        rows = []
        for row in csv.DictReader(handle):
            name, state, country = row["name"], row["state"], row["country"]
            rows.append(GeocodingCity(name, state, country, row["country_code"], row["latitude"], row["longitude"], row["timezone"], f"{name} {state} {country}".lower()))
        return rows


_CITIES = _load()


def search(query: str, limit: int = 10) -> list[GeocodingCity]:
    term = query.strip().lower()
    if len(term) < 2:
        return []
    matches = [city for city in _CITIES if term in city.search_key]
    return matches[:limit]
