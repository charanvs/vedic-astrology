from decimal import Decimal
from app.astrology.matching.common import payload
from app.astrology.matching.constants import KOOTA_MAXIMA, VARNA_BY_RASHI, VARNA_RANK

def calculate(bride, groom, first_is_bride: bool) -> dict:
    bride_varna, groom_varna = VARNA_BY_RASHI[bride.rashi_number-1], VARNA_BY_RASHI[groom.rashi_number-1]
    score = Decimal(1) if VARNA_RANK[groom_varna] >= VARNA_RANK[bride_varna] else Decimal(0)
    first, second = (bride_varna, groom_varna) if first_is_bride else (groom_varna, bride_varna)
    return payload("varna", "Varna", score, KOOTA_MAXIMA["varna"], first, second,
        "One point when the groom-role category is equal to or above the bride-role category in this traditional table. These are symbolic chart labels, not social identity.",
        "MC-JOSHI-V22-VARNA", {"bride": bride_varna, "groom": groom_varna}, True)
