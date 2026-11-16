from decimal import Decimal

SUPPORTED_CHARTS = {
    "D9": {"name": "Navamsha", "division": 9, "segment_degrees": Decimal(30) / Decimal(9), "primary_use": "Dharma, marriage, and planetary strength"},
    "D10": {"name": "Dashamsha", "division": 10, "segment_degrees": Decimal(3), "primary_use": "Career, status, and public work"},
}

# Informational only: classification always uses the exact supplied longitude.
BOUNDARY_WARNING_DEGREES = Decimal(1) / Decimal(60)
