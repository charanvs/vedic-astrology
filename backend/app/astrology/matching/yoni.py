from decimal import Decimal
from app.astrology.matching.common import payload
from app.astrology.matching.constants import KOOTA_MAXIMA, YONI_BY_NAKSHATRA, YONI_CLASSES, YONI_MATRIX
RELATIONSHIP = {4:"same", 3:"friendly", 2:"neutral", 1:"enemy", 0:"great enemy"}

def calculate(bride, groom, first_is_bride: bool) -> dict:
    bride_yoni, groom_yoni = YONI_BY_NAKSHATRA[bride.nakshatra_number-1], YONI_BY_NAKSHATRA[groom.nakshatra_number-1]
    points = YONI_MATRIX[YONI_CLASSES.index(bride_yoni)][YONI_CLASSES.index(groom_yoni)]
    first, second = (bride_yoni, groom_yoni) if first_is_bride else (groom_yoni, bride_yoni)
    return payload("yoni", "Yoni", Decimal(points), KOOTA_MAXIMA["yoni"], first, second,
        f"The ordered animal-symbol matrix classifies this pairing as {RELATIONSHIP[points]}.",
        "MC-JOSHI-YONI-P335", {"bride": bride_yoni, "groom": groom_yoni, "relationship": RELATIONSHIP[points]}, True)
