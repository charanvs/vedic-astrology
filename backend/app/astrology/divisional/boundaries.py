from decimal import Decimal, InvalidOperation
import math

from app.astrology.divisional.constants import BOUNDARY_WARNING_DEGREES


def decimal_degrees(value: float | Decimal) -> Decimal:
    if isinstance(value, float) and not math.isfinite(value):
        raise ValueError("Longitude must be finite")
    try:
        result = value if isinstance(value, Decimal) else Decimal(str(value))
    except (InvalidOperation, ValueError) as exc:
        raise ValueError("Longitude must be numeric") from exc
    if not result.is_finite():
        raise ValueError("Longitude must be finite")
    normalized = result % Decimal(360)
    return Decimal(0) if normalized == 0 else normalized


def boundary_distance(degree_in_sign: Decimal, divisions: int) -> Decimal:
    scaled = degree_in_sign * divisions
    remainder = scaled % Decimal(30)
    return min(remainder, Decimal(30) - remainder) / Decimal(divisions)


def is_boundary_near(degree_in_sign: Decimal, divisions: int) -> bool:
    return boundary_distance(degree_in_sign, divisions) <= BOUNDARY_WARNING_DEGREES
