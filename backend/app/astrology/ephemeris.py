from importlib import metadata
from pathlib import Path
from threading import RLock
from typing import Any

from app.astrology.config import CalculationSettings, ephemeris_directory
from app.astrology.exceptions import CalculationError, EphemerisUnavailableError

_LOCK = RLock()


def _load_swe() -> Any:
    try:
        import swisseph as swe
        return swe
    except Exception as exc:
        raise EphemerisUnavailableError(
            "Swiss Ephemeris native binding is unavailable on this server"
        ) from exc


def binding_distribution() -> str:
    for package in ("pyswisseph", "pysweph"):
        try:
            metadata.version(package)
            return package
        except metadata.PackageNotFoundError:
            continue
    return "unavailable"

def binding_version() -> str:
    package = binding_distribution()
    return metadata.version(package) if package != "unavailable" else "unavailable"


class Ephemeris:
    """Synchronized facade around Swiss Ephemeris process-global state."""

    def __init__(self, settings: CalculationSettings):
        self.settings = settings

    def _configure(self, swe: Any) -> tuple[int, str]:
        swe.set_sid_mode(swe.SIDM_LAHIRI, 0.0, 0.0)
        if self.settings.ephemeris_source == "swiss":
            directory = ephemeris_directory()
            if directory is None or not directory.is_dir():
                raise EphemerisUnavailableError("Configured Swiss ephemeris directory is unavailable")
            if not any(Path(directory).glob("*.se1")):
                raise EphemerisUnavailableError("Configured Swiss ephemeris directory contains no .se1 files")
            swe.set_ephe_path(str(directory))
            return swe.FLG_SWIEPH, "Swiss Ephemeris files"
        swe.set_ephe_path("")
        return swe.FLG_MOSEPH, "Moshier analytical ephemeris"

    def metadata(self) -> dict:
        swe = _load_swe()
        with _LOCK:
            _, source_label = self._configure(swe)
            return {
                "engine": "Swiss Ephemeris",
                "engine_version": str(swe.version),
                "binding": binding_distribution(),
                "binding_version": binding_version(),
                "ephemeris_source": source_label,
            }

    def calculate_ut(self, julian_day_ut: float, body_name: str) -> tuple[tuple[float, ...], int, str]:
        swe = _load_swe()
        with _LOCK:
            source_flag, source_label = self._configure(swe)
            body = getattr(swe, body_name)
            requested = source_flag | swe.FLG_SIDEREAL | swe.FLG_SPEED
            try:
                values, returned = swe.calc_ut(julian_day_ut, body, requested)
            except Exception as exc:
                raise CalculationError(f"Swiss Ephemeris could not calculate {body_name.lower()}") from exc
            if not returned & source_flag:
                raise EphemerisUnavailableError(
                    f"Swiss Ephemeris did not use the configured {self.settings.ephemeris_source} source"
                )
            return values, returned, source_label

    def ayanamsa_ut(self, julian_day_ut: float) -> float:
        swe = _load_swe()
        with _LOCK:
            self._configure(swe)
            try:
                return float(swe.get_ayanamsa_ut(julian_day_ut))
            except Exception as exc:
                raise CalculationError("Lahiri ayanamsa calculation failed") from exc

    def ascendant_ut(self, julian_day_ut: float, latitude: float, longitude: float) -> float:
        swe = _load_swe()
        with _LOCK:
            self._configure(swe)
            try:
                _, ascmc = swe.houses_ex(
                    julian_day_ut, latitude, longitude, b"P", swe.FLG_SIDEREAL
                )
            except Exception as exc:
                raise CalculationError("Sidereal ascendant calculation failed for this location") from exc
            if not ascmc:
                raise CalculationError("Swiss Ephemeris returned no ascendant")
            return float(ascmc[0]) % 360.0

    def rise_set_ut(
        self,
        julian_day_ut: float,
        latitude: float,
        longitude: float,
        elevation: float,
        event: str,
    ) -> float | None:
        """Return the next apparent upper-limb solar event, or None if circumpolar."""
        swe = _load_swe()
        with _LOCK:
            source_flag, _ = self._configure(swe)
            event_flag = swe.CALC_RISE if event == "rise" else swe.CALC_SET
            try:
                result, times = swe.rise_trans(
                    julian_day_ut,
                    swe.SUN,
                    event_flag,
                    (longitude, latitude, elevation),
                    0.0,
                    15.0,
                    source_flag,
                )
            except Exception as exc:
                raise CalculationError(f"Swiss Ephemeris solar {event} calculation failed") from exc
            if result == -2:
                return None
            if result != 0 or not times:
                raise CalculationError(f"Swiss Ephemeris returned an invalid solar {event} result")
            return float(times[0])
