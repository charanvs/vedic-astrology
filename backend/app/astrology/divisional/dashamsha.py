from decimal import Decimal

from app.astrology.divisional.boundaries import decimal_degrees


def dashamsha_position(longitude: float | Decimal) -> dict:
    source = decimal_degrees(longitude)
    sign_index = int(source // Decimal(30))
    degree_in_sign = source - Decimal(sign_index * 30)
    division_index = int(degree_in_sign // Decimal(3))
    degree = (degree_in_sign % Decimal(3)) * Decimal(10)
    start = sign_index if sign_index % 2 == 0 else (sign_index + 8) % 12
    sign = (start + division_index) % 12
    return {"division_number": division_index + 1, "sign_number": sign + 1,
            "degree": degree, "longitude": Decimal(sign * 30) + degree}
