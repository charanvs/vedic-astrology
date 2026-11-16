def observations(kootas: list[dict]) -> list[dict]:
    by_id = {item["id"]: item for item in kootas}
    nadi, bhakoot, gana = by_id["nadi"], by_id["bhakoot"], by_id["gana"]
    return [
        {
            "id": "nadi_dosha", "name": "Nadi observation",
            "triggered": nadi["score"] == 0, "triggering_rule": nadi["rule_id"],
            "inputs": nadi["details"], "exception_evaluated": False,
            "explanation": "The selected tradition flags matching Nadi groups. This is a belief-based classification and is not medical, genetic, fertility, or health evidence.",
        },
        {
            "id": "bhakoot_dosha", "name": "Bhakoot observation",
            "triggered": bhakoot["score"] == 0, "triggering_rule": bhakoot["rule_id"],
            "inputs": bhakoot["details"], "exception_evaluated": False,
            "explanation": "A 2/12, 5/9, or 6/8 Moon-sign relationship is flagged by the base table. Cancellation rules are not applied to the score.",
        },
        {
            "id": "gana_observation", "name": "Gana observation",
            "triggered": gana["score"] <= 1, "triggering_rule": gana["rule_id"],
            "inputs": gana["details"], "exception_evaluated": False,
            "explanation": "A low directional Gana-table value is shown as a traditional observation. It is not a judgement of either person's character.",
        },
    ]
