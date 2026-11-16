from dataclasses import dataclass, field
from datetime import UTC, datetime, timedelta
from decimal import Decimal, ROUND_HALF_EVEN, localcontext

from app.astrology.dasha.constants import DASHA_YEARS, PLANET_IDENTIFIERS, sequence_from
from app.astrology.dasha.settings import SECONDS_PER_DAY

MICROSECONDS_PER_SECOND = Decimal(1_000_000)
MICROSECONDS_PER_DAY = Decimal(86_400_000_000)


@dataclass
class DashaPeriod:
    level: str
    lord: str
    start_utc: datetime
    end_utc: datetime
    duration_years: Decimal
    parent_lord: str | None = None
    children: list["DashaPeriod"] = field(default_factory=list)


def decimal_seconds_to_timedelta(seconds: Decimal) -> timedelta:
    microseconds = int((seconds * MICROSECONDS_PER_SECOND).to_integral_value(rounding=ROUND_HALF_EVEN))
    return timedelta(microseconds=microseconds)


def period_at_fraction(start: datetime, end: datetime, numerator: Decimal, denominator: Decimal) -> datetime:
    delta = end - start
    total_microseconds = Decimal(
        delta.days * 86_400_000_000 + delta.seconds * 1_000_000 + delta.microseconds
    )
    offset = int((total_microseconds * numerator / denominator).to_integral_value(rounding=ROUND_HALF_EVEN))
    return start + timedelta(microseconds=offset)


def partition_period(parent: DashaPeriod, child_level: str) -> list[DashaPeriod]:
    sequence = sequence_from(parent.lord)
    children: list[DashaPeriod] = []
    cumulative = Decimal(0)
    with localcontext() as context:
        context.prec = 40
        for index, lord in enumerate(sequence):
            next_cumulative = cumulative + DASHA_YEARS[lord]
            start = period_at_fraction(parent.start_utc, parent.end_utc, cumulative, Decimal(120))
            end = parent.end_utc if index == 8 else period_at_fraction(
                parent.start_utc, parent.end_utc, next_cumulative, Decimal(120)
            )
            children.append(DashaPeriod(
                level=child_level, lord=lord, start_utc=start, end_utc=end,
                duration_years=parent.duration_years * DASHA_YEARS[lord] / Decimal(120),
                parent_lord=parent.lord,
            ))
            cumulative = next_cumulative
    return children


def period_contains(period: DashaPeriod, instant: datetime) -> bool:
    return period.start_utc <= instant < period.end_utc


def find_active(periods: list[DashaPeriod], instant: datetime) -> DashaPeriod | None:
    return next((period for period in periods if period_contains(period, instant)), None)


def duration_days(period: DashaPeriod) -> Decimal:
    delta = period.end_utc - period.start_utc
    microseconds = Decimal(
        delta.days * 86_400_000_000 + delta.seconds * 1_000_000 + delta.microseconds
    )
    return microseconds / MICROSECONDS_PER_DAY


def duration_seconds(start: datetime, end: datetime) -> Decimal:
    delta = end - start
    return Decimal(
        delta.days * 86_400_000_000 + delta.seconds * 1_000_000 + delta.microseconds
    ) / MICROSECONDS_PER_SECOND


def period_payload(period: DashaPeriod, timezone, birth_utc: datetime, reference_utc: datetime) -> dict:
    return {
        "level": period.level, "lord": period.lord,
        "planet_identifier": PLANET_IDENTIFIERS[period.lord], "parent_lord": period.parent_lord,
        "start_utc": period.start_utc.astimezone(UTC), "end_utc": period.end_utc.astimezone(UTC),
        "start_local": period.start_utc.astimezone(timezone), "end_local": period.end_utc.astimezone(timezone),
        "duration_dasha_years": period.duration_years, "duration_days": duration_days(period),
        "active_at_birth": period_contains(period, birth_utc),
        "active_at_reference": period_contains(period, reference_utc), "children": [],
    }
