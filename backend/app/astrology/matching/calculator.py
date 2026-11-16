from dataclasses import dataclass
from decimal import Decimal

from app.astrology.constants import NAKSHATRAS
from app.astrology.matching import bhakoot, gana, graha_maitri, nadi, tara, varna, vashya, yoni
from app.astrology.matching.constants import (
    CALCULATION_VERSION, GANA_BY_NAKSHATRA, KOOTA_MAXIMA, NADI_BY_NAKSHATRA,
    RASHI_LORDS, RASHI_NAMES, RULESET_ID, YONI_BY_NAKSHATRA,
)
from app.astrology.matching.dosha_notes import observations
from app.astrology.matching.rulesets import get_ruleset


@dataclass(frozen=True)
class PartnerMoon:
    role: str
    longitude: Decimal
    rashi_number: int
    nakshatra_number: int
    pada: int
    precision: str = "exact"
    uncertainty_start_utc: str | None = None
    uncertainty_end_utc: str | None = None
    profile_id: int | None = None
    name: str | None = None

    @property
    def degree_in_rashi(self) -> Decimal:
        return self.longitude % Decimal(30)

    def __post_init__(self):
        if self.role not in {"bride", "groom"}:
            raise ValueError("role must be bride or groom")
        if not Decimal(0) <= self.longitude < Decimal(360):
            raise ValueError("Moon longitude must be in [0, 360)")
        if not 1 <= self.rashi_number <= 12 or not 1 <= self.nakshatra_number <= 27 or not 1 <= self.pada <= 4:
            raise ValueError("Invalid Moon classification")


class AshtakootaMatchingService:
    def calculate(self, first: PartnerMoon, second: PartnerMoon, ruleset: str = RULESET_ID) -> dict:
        selected = get_ruleset(ruleset)
        if {first.role, second.role} != {"bride", "groom"}:
            raise ValueError("Partners must have distinct bride and groom calculation roles")
        bride, groom = (first, second) if first.role == "bride" else (second, first)
        first_is_bride = first.role == "bride"
        kootas = [
            varna.calculate(bride, groom, first_is_bride),
            vashya.calculate(bride, groom, first_is_bride),
            tara.calculate(bride, groom, first_is_bride),
            yoni.calculate(bride, groom, first_is_bride),
            graha_maitri.calculate(bride, groom, first_is_bride),
            gana.calculate(bride, groom, first_is_bride),
            bhakoot.calculate(bride, groom, first_is_bride),
            nadi.calculate(bride, groom, first_is_bride),
        ]
        total = sum((item["score"] for item in kootas), Decimal(0))
        if total > Decimal(36):
            raise ValueError("Matching total exceeds 36")
        warnings = [
            "Compatibility scores represent traditional astrological beliefs and are not scientifically validated predictions of relationship success.",
            "No marriage, separation, medical, fertility, or relationship outcome should be inferred from this score.",
            "Dosha exceptions are not applied to the base score in this release.",
        ]
        if any(partner.precision == "date_unambiguous" for partner in (first, second)):
            warnings.append(
                "At least one birth time is unknown. Its displayed Moon longitude is representative; "
                "the score is definitive only because the Moon's rashi and nakshatra do not change "
                "during that profile's full local birth date."
            )
        return {
            "status": "definitive", "ruleset": selected, "partners": [self._partner(first), self._partner(second)],
            "kootas": kootas, "total_score": total, "maximum_score": Decimal(36),
            "percentage": total * Decimal(100) / Decimal(36),
            "threshold": {
                "value": Decimal(18), "met": total >= Decimal(18),
                "label": "At or above a commonly used traditional threshold" if total >= Decimal(18) else "Below a commonly used traditional threshold",
            },
            "observations": observations(kootas),
            "metadata": {
                "calculation_version": CALCULATION_VERSION, "ruleset_id": ruleset,
                "maximums": dict(KOOTA_MAXIMA), "ayanamsa": "Lahiri (Chitrapaksha)",
                "zodiac": "sidereal", "moon_reference": "geocentric",
                "arithmetic": "Decimal scores; no intermediate rounding",
            },
            "warnings": warnings,
        }

    @staticmethod
    def _partner(partner: PartnerMoon) -> dict:
        index = partner.nakshatra_number - 1
        return {
            "profile_id": partner.profile_id, "name": partner.name, "role": partner.role,
            "moon": {
                "sidereal_longitude": partner.longitude, "degree_in_rashi": partner.degree_in_rashi,
                "rashi_number": partner.rashi_number, "rashi": RASHI_NAMES[partner.rashi_number-1],
                "rashi_lord": RASHI_LORDS[partner.rashi_number-1],
                "nakshatra_number": partner.nakshatra_number, "nakshatra": NAKSHATRAS[index],
                "pada": partner.pada, "yoni": YONI_BY_NAKSHATRA[index],
                "gana": GANA_BY_NAKSHATRA[index], "nadi": NADI_BY_NAKSHATRA[index],
                "precision": partner.precision, "uncertainty_start_utc": partner.uncertainty_start_utc,
                "uncertainty_end_utc": partner.uncertainty_end_utc,
            },
        }
