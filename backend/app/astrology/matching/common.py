from decimal import Decimal


def payload(identifier: str, name: str, score: Decimal, maximum: Decimal,
            first: str, second: str, explanation: str, rule_id: str,
            details: dict | None = None, directional: bool = False) -> dict:
    if not Decimal(0) <= score <= maximum:
        raise ValueError(f"{identifier} score is outside its allowed range")
    return {"id": identifier, "name": name, "score": score, "maximum": maximum,
        "partner_one_classification": first, "partner_two_classification": second,
        "explanation": explanation, "rule_id": rule_id, "details": details or {},
        "directional": directional}
