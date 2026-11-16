"""Build the bundled offline geocoding dataset from a local GeoNames export.

This script does not download anything. Fetch and extract, into one directory,
these three files from https://download.geonames.org/export/dump/ :
cities15000.zip (unzip to cities15000.txt), admin1CodesASCII.txt, countryInfo.txt.
GeoNames data is licensed CC BY 4.0 (https://www.geonames.org/export/).

Usage: python scripts/build_geocoding_dataset.py --source <geonames_dir>
"""
from __future__ import annotations
import argparse
import csv
from pathlib import Path
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

OUTPUT = Path(__file__).resolve().parents[1] / "app" / "data" / "geocoding_cities.csv"


def load_admin1_names(path: Path) -> dict[str, str]:
    mapping: dict[str, str] = {}
    with path.open(encoding="utf-8") as handle:
        for line in handle:
            fields = line.rstrip("\n").split("\t")
            if len(fields) >= 2:
                mapping[fields[0]] = fields[1]
    return mapping


def load_country_names(path: Path) -> dict[str, str]:
    mapping: dict[str, str] = {}
    with path.open(encoding="utf-8") as handle:
        for line in handle:
            if line.startswith("#") or not line.strip():
                continue
            fields = line.rstrip("\n").split("\t")
            if len(fields) >= 5:
                mapping[fields[0]] = fields[4]
    return mapping


def build_rows(source: Path) -> list[tuple[str, str, str, str, str, str, str, int]]:
    admin1_names = load_admin1_names(source / "admin1CodesASCII.txt")
    country_names = load_country_names(source / "countryInfo.txt")
    rows: list[tuple[str, str, str, str, str, str, str, int]] = []
    with (source / "cities15000.txt").open(encoding="utf-8") as handle:
        for line in handle:
            fields = line.rstrip("\n").split("\t")
            if len(fields) < 19:
                continue
            name, latitude, longitude = fields[1], fields[4], fields[5]
            country_code, admin1_code, population, timezone = fields[8], fields[10], fields[14], fields[17]
            if not (name and latitude and longitude and country_code and timezone):
                continue
            try:
                ZoneInfo(timezone)
            except ZoneInfoNotFoundError:
                continue
            state = admin1_names.get(f"{country_code}.{admin1_code}", "") if admin1_code else ""
            country = country_names.get(country_code, country_code)
            rows.append((name, state, country, country_code, latitude, longitude, timezone, int(population or 0)))
    rows.sort(key=lambda row: row[7], reverse=True)
    return rows


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", required=True, type=Path, help="Directory containing the extracted GeoNames files")
    args = parser.parse_args()
    rows = build_rows(args.source)
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    with OUTPUT.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.writer(handle)
        writer.writerow(["name", "state", "country", "country_code", "latitude", "longitude", "timezone", "population"])
        writer.writerows(rows)
    print(f"Wrote {len(rows)} cities to {OUTPUT}")


if __name__ == "__main__":
    main()
