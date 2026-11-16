from decimal import Decimal

DASHA_SEQUENCE = (
    "Ketu", "Venus", "Sun", "Moon", "Mars", "Rahu", "Jupiter", "Saturn", "Mercury",
)
DASHA_YEARS = {
    "Ketu": Decimal("7"), "Venus": Decimal("20"), "Sun": Decimal("6"),
    "Moon": Decimal("10"), "Mars": Decimal("7"), "Rahu": Decimal("18"),
    "Jupiter": Decimal("16"), "Saturn": Decimal("19"), "Mercury": Decimal("17"),
}
PLANET_IDENTIFIERS = {lord: lord.lower() for lord in DASHA_SEQUENCE}
NAKSHATRA_SPAN = Decimal(40) / Decimal(3)
TOTAL_DASHA_YEARS = sum(DASHA_YEARS.values(), Decimal(0))
if TOTAL_DASHA_YEARS != Decimal(120):
    raise RuntimeError("Vimshottari Dasha durations must total 120 years")


def sequence_from(lord: str) -> tuple[str, ...]:
    index = DASHA_SEQUENCE.index(lord)
    return DASHA_SEQUENCE[index:] + DASHA_SEQUENCE[:index]
