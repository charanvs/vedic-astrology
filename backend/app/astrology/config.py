import os
from dataclasses import dataclass
from pathlib import Path

from app.astrology.exceptions import EphemerisUnavailableError


@dataclass(frozen=True)
class CalculationSettings:
    zodiac: str = "sidereal"
    ayanamsa: str = "Lahiri (Chitrapaksha)"
    ayanamsa_mode: str = "SIDM_LAHIRI"
    planetary_reference: str = "geocentric"
    node_convention: str = "mean lunar node"
    house_system: str = "whole-sign from ascendant Rashi"
    calendar: str = "proleptic Gregorian"
    ephemeris_source: str = "moshier"
    stationary_threshold: float = 0.0001


def get_calculation_settings() -> CalculationSettings:
    source = os.getenv("ASTROLOGY_EPHEMERIS_SOURCE", "moshier").strip().lower()
    if source not in {"swiss", "moshier"}:
        raise EphemerisUnavailableError("ASTROLOGY_EPHEMERIS_SOURCE must be 'swiss' or 'moshier'")
    threshold = float(os.getenv("ASTROLOGY_STATIONARY_THRESHOLD", "0.0001"))
    if threshold <= 0:
        raise EphemerisUnavailableError("ASTROLOGY_STATIONARY_THRESHOLD must be positive")
    return CalculationSettings(ephemeris_source=source, stationary_threshold=threshold)


def ephemeris_directory() -> Path | None:
    raw = os.getenv("ASTROLOGY_EPHE_PATH", "").strip()
    return Path(raw).expanduser().resolve() if raw else None
