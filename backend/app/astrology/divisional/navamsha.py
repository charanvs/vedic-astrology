from decimal import Decimal

from app.astrology.divisional.boundaries import decimal_degrees


def navamsha_position(longitude: float | Decimal) -> dict:
    source = decimal_degrees(longitude)
    sign_index = int(source // Decimal(30))
    degree_in_sign = source - Decimal(sign_index * 30)
    scaled = degree_in_sign * Decimal(9)
    division_index = int(scaled // Decimal(30))
    degree = scaled % Decimal(30)
    modality_offset = (0, 8, 4)[sign_index % 3]
    sign = (sign_index + modality_offset + division_index) % 12
    return {"division_number": division_index + 1, "sign_number": sign + 1,
            "degree": degree, "longitude": Decimal(sign * 30) + degree}
