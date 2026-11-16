from decimal import Decimal
from app.astrology.matching.common import payload
from app.astrology.matching.constants import KOOTA_MAXIMA, VASHYA_BY_RASHI, VASHYA_CLASSES, VASHYA_MATRIX

def calculate(bride, groom, first_is_bride: bool) -> dict:
    bride_class, groom_class = VASHYA_BY_RASHI[bride.rashi_number-1], VASHYA_BY_RASHI[groom.rashi_number-1]
    score = Decimal(VASHYA_MATRIX[VASHYA_CLASSES.index(bride_class)][VASHYA_CLASSES.index(groom_class)])
    first, second = (bride_class, groom_class) if first_is_bride else (groom_class, bride_class)
    return payload("vashya", "Vashya", score, KOOTA_MAXIMA["vashya"], first, second,
        "The selected Muhurta Chintamani four-class Moon-sign matrix is applied with bride as row and groom as column.",
        "MC-JOSHI-V23-VASHYA", {"bride": bride_class, "groom": groom_class, "bride_degree_in_rashi": bride.degree_in_rashi, "groom_degree_in_rashi": groom.degree_in_rashi}, True)
