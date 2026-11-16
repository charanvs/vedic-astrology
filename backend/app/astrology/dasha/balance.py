from dataclasses import dataclass
from decimal import Decimal, localcontext

from app.astrology.constants import NAKSHATRAS, NAKSHATRA_LORDS
from app.astrology.dasha.constants import DASHA_YEARS


@dataclass(frozen=True)
class NakshatraBalance:
    moon_longitude: Decimal
    nakshatra_number: int
    nakshatra_name: str
    pada: int
    lord: str
    position_degrees: Decimal
    elapsed_fraction: Decimal
    remaining_fraction: Decimal
    full_years: Decimal
    elapsed_years: Decimal
    remaining_years: Decimal


def calculate_nakshatra_balance(moon_longitude: float | Decimal) -> NakshatraBalance:
    with localcontext() as context:
        context.prec = 40
        longitude = Decimal(str(moon_longitude)) % Decimal(360)
        # Work in an exact fraction of the full zodiac. This avoids accumulating
        # the repeating decimal representation of 13°20' at every boundary.
        scaled = longitude * Decimal(27) / Decimal(360)
        nearest_boundary = scaled.to_integral_value()
        if abs(scaled - nearest_boundary) < Decimal("1e-25"):
            scaled = nearest_boundary
        index = min(int(scaled), 26)
        elapsed = scaled - Decimal(index)
        position = elapsed * Decimal(360) / Decimal(27)
        remaining = Decimal(1) - elapsed
        lord = NAKSHATRA_LORDS[index % 9]
        full_years = DASHA_YEARS[lord]
        pada = min(int(elapsed * Decimal(4)), 3) + 1
        return NakshatraBalance(
            moon_longitude=longitude, nakshatra_number=index + 1,
            nakshatra_name=NAKSHATRAS[index], pada=pada, lord=lord,
            position_degrees=position, elapsed_fraction=elapsed,
            remaining_fraction=remaining, full_years=full_years,
            elapsed_years=full_years * elapsed, remaining_years=full_years * remaining,
        )
