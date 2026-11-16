from decimal import Decimal
from app.astrology.matching.common import payload
from app.astrology.matching.constants import GANA_BY_NAKSHATRA, GANA_CLASSES, GANA_MATRIX, KOOTA_MAXIMA

def calculate(bride, groom, first_is_bride: bool) -> dict:
    bride_gana, groom_gana = GANA_BY_NAKSHATRA[bride.nakshatra_number-1], GANA_BY_NAKSHATRA[groom.nakshatra_number-1]
    score = Decimal(GANA_MATRIX[GANA_CLASSES.index(bride_gana)][GANA_CLASSES.index(groom_gana)])
    first, second = (bride_gana, groom_gana) if first_is_bride else (groom_gana, bride_gana)
    return payload("gana", "Gana", score, KOOTA_MAXIMA["gana"], first, second,
        "The directional bride-row/groom-column symbolic Gana matrix is applied. Labels describe traditional categories, not a person's moral character.",
        "MC-JOSHI-V29-30-GANA", {"bride": bride_gana, "groom": groom_gana}, True)
