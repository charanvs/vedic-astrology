from decimal import Decimal
from app.astrology.matching.common import payload
from app.astrology.matching.constants import GRAHA_MAITRI_MATRIX, KOOTA_MAXIMA, PLANETS, RASHI_LORDS
RELATIONSHIP = {"5":"same lord or mutual friendship", "4":"friend and neutral", "3":"mutual neutrality", "1":"friend and enemy", "0.5":"neutral and enemy", "0":"mutual enmity"}

def calculate(bride, groom, first_is_bride: bool) -> dict:
    bride_lord, groom_lord = RASHI_LORDS[bride.rashi_number-1], RASHI_LORDS[groom.rashi_number-1]
    raw = GRAHA_MAITRI_MATRIX[PLANETS.index(bride_lord)][PLANETS.index(groom_lord)]
    first, second = (bride_lord, groom_lord) if first_is_bride else (groom_lord, bride_lord)
    return payload("graha_maitri", "Graha Maitri", Decimal(raw), KOOTA_MAXIMA["graha_maitri"], first, second,
        f"Natural friendship of the classical Moon-sign lords: {RELATIONSHIP[raw]}.",
        "MC-JOSHI-V27-28-MAITRI", {"bride_lord": bride_lord, "groom_lord": groom_lord, "relationship": RELATIONSHIP[raw]}, True)
