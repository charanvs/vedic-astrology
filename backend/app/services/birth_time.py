from dataclasses import dataclass
from datetime import UTC, date, datetime, time
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError


class BirthTimeError(ValueError):
    """A local civil time cannot be interpreted safely."""


@dataclass(frozen=True)
class BirthTimeResolution:
    local_datetime: datetime
    utc_datetime: datetime | None
    utc_offset_minutes: int | None
    timezone: str
    status: str
    fold: int | None
    candidate_offset_minutes: tuple[int, ...] = ()


def resolve_birth_time(birth_date: date, birth_time: time, timezone_name: str, fold: int | None = None) -> BirthTimeResolution:
    if fold not in (None, 0, 1):
        raise BirthTimeError("fold must be 0 or 1")
    try:
        zone = ZoneInfo(timezone_name)
    except ZoneInfoNotFoundError as exc:
        raise BirthTimeError("timezone must be a valid IANA identifier") from exc

    local_naive = datetime.combine(birth_date, birth_time.replace(tzinfo=None))
    candidates: dict[int, datetime] = {}
    for candidate_fold in (0, 1):
        aware = local_naive.replace(tzinfo=zone, fold=candidate_fold)
        utc_value = aware.astimezone(UTC)
        round_trip = utc_value.astimezone(zone).replace(tzinfo=None)
        if round_trip == local_naive:
            offset = aware.utcoffset()
            if offset is not None:
                candidates[int(offset.total_seconds() // 60)] = utc_value

    if not candidates:
        raise BirthTimeError("local time does not exist because of a daylight-saving clock change")

    offsets = tuple(sorted(candidates))
    if len(candidates) > 1 and fold is None:
        return BirthTimeResolution(local_naive, None, None, timezone_name, "ambiguous", None, offsets)

    chosen_fold = fold if len(candidates) > 1 else 0
    aware = local_naive.replace(tzinfo=zone, fold=chosen_fold)
    chosen_offset = int(aware.utcoffset().total_seconds() // 60)  # type: ignore[union-attr]
    if chosen_offset not in candidates:
        raise BirthTimeError("the selected fold is not valid for this local time")
    status = "resolved_ambiguous" if len(candidates) > 1 else "resolved"
    return BirthTimeResolution(local_naive, candidates[chosen_offset], chosen_offset, timezone_name, status, chosen_fold if len(candidates) > 1 else None, offsets)
