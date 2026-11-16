from decimal import Decimal
from app.astrology.matching.common import payload
from app.astrology.matching.constants import KOOTA_MAXIMA, RASHI_NAMES

def calculate(bride, groom, first_is_bride: bool) -> dict:
    bride_to_groom = ((groom.rashi_number - bride.rashi_number) % 12) + 1
    groom_to_bride = ((bride.rashi_number - groom.rashi_number) % 12) + 1
    pair = tuple(sorted((bride_to_groom, groom_to_bride)))
    dosha = pair in {(2,12),(5,9),(6,8)}
    relationship = {(2,12):"2/12 — Dwirdwadasha", (5,9):"5/9 — Navapanchama", (6,8):"6/8 — Shashtashtaka"}.get(pair, f"{pair[0]}/{pair[1]}")
    bride_rashi, groom_rashi = RASHI_NAMES[bride.rashi_number-1], RASHI_NAMES[groom.rashi_number-1]
    first, second = (bride_rashi, groom_rashi) if first_is_bride else (groom_rashi, bride_rashi)
    return payload("bhakoot", "Bhakoot", Decimal(0 if dosha else 7), KOOTA_MAXIMA["bhakoot"], first, second,
        f"The inclusive cyclic Moon-sign relationship is {relationship}; base points are {'zero' if dosha else 'seven'}.",
        "MC-JOSHI-V31-BHAKOOT", {"bride_to_groom": bride_to_groom, "groom_to_bride": groom_to_bride, "relationship": relationship, "dosha": dosha}, False)
