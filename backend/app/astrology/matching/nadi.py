from decimal import Decimal
from app.astrology.matching.common import payload
from app.astrology.matching.constants import KOOTA_MAXIMA, NADI_BY_NAKSHATRA

def calculate(bride, groom, first_is_bride: bool) -> dict:
    bride_nadi, groom_nadi = NADI_BY_NAKSHATRA[bride.nakshatra_number-1], NADI_BY_NAKSHATRA[groom.nakshatra_number-1]
    same = bride_nadi == groom_nadi
    first, second = (bride_nadi, groom_nadi) if first_is_bride else (groom_nadi, bride_nadi)
    return payload("nadi", "Nadi", Decimal(0 if same else 8), KOOTA_MAXIMA["nadi"], first, second,
        "Different traditional Nadi groups score eight; the same group scores zero. This is not a medical or genetic assessment.",
        "MC-JOSHI-V34-NADI", {"bride": bride_nadi, "groom": groom_nadi, "dosha": same}, False)
