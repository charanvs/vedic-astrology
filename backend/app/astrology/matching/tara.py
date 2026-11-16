from decimal import Decimal
from app.astrology.matching.common import payload
from app.astrology.matching.constants import KOOTA_MAXIMA, TARA_NAMES, UNFAVOURABLE_TARAS

def _direction(start: int, end: int) -> tuple[int, int, str, Decimal]:
    count = ((end - start) % 27) + 1
    category = ((count - 1) % 9) + 1
    return count, category, TARA_NAMES[category-1], Decimal("0") if category in UNFAVOURABLE_TARAS else Decimal("1.5")

def calculate(bride, groom, first_is_bride: bool) -> dict:
    bg, gb = _direction(bride.nakshatra_number, groom.nakshatra_number), _direction(groom.nakshatra_number, bride.nakshatra_number)
    bride_class, groom_class = f"{bg[1]} — {bg[2]}", f"{gb[1]} — {gb[2]}"
    first, second = (bride_class, groom_class) if first_is_bride else (groom_class, bride_class)
    return payload("tara", "Tara (Dina)", bg[3]+gb[3], KOOTA_MAXIMA["tara"], first, second,
        "Inclusive Nakshatra counts are reduced modulo nine; Vipat, Pratyari and Vadha score zero in their direction, all others score 1.5.",
        "MC-JOSHI-V24-TARA", {"bride_to_groom_count": bg[0], "groom_to_bride_count": gb[0], "bride_directional_points": bg[3], "groom_directional_points": gb[3]}, True)
