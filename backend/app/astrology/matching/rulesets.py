from app.astrology.matching.constants import CALCULATION_VERSION, RULESET_ID
from app.astrology.matching.exceptions import UnsupportedRulesetError

RULESET = {
    "id": RULESET_ID, "name": "Muhurta Chintamani — Kedar Datt Joshi charts",
    "version": CALCULATION_VERSION, "tradition": "North Indian Ashtakoota Guna Milan",
    "source": "Muhurta Chintamani, Vivaha Prakarana verses 21–37, Joshi edition pp. 329–355",
    "role_order": "bride row, groom column",
    "vashya_variant": "Muhurta Chintamani four-class whole-sign chart",
    "yoni_variant": "Muhurta Chintamani chart with two documented corrections",
}


def get_ruleset(identifier: str) -> dict:
    if identifier != RULESET_ID:
        raise UnsupportedRulesetError(f"Unsupported matching ruleset: {identifier}")
    return RULESET
