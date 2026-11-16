from collections.abc import Callable
from dataclasses import dataclass
from datetime import UTC, datetime, timedelta
import math

from app.astrology.exceptions import TransitionSearchError
from app.astrology.formatting import normalize_degrees


@dataclass(frozen=True)
class AngularTransition:
    at_utc: datetime
    boundary_index: int


def _root(
    left: datetime,
    right: datetime,
    left_angle: float,
    left_unwrapped: float,
    target: float,
    angle_at: Callable[[datetime], float],
) -> datetime:
    for _ in range(60):
        if (right - left).total_seconds() <= 0.25:
            return left + (right - left) / 2
        middle = left + (right - left) / 2
        middle_angle = normalize_degrees(angle_at(middle))
        middle_unwrapped = left_unwrapped + ((middle_angle - left_angle) % 360.0)
        if middle_unwrapped < target:
            left, left_angle, left_unwrapped = middle, middle_angle, middle_unwrapped
        else:
            right = middle
    raise TransitionSearchError("Panchang transition solver did not converge")


def find_angular_transitions(
    start_utc: datetime,
    end_utc: datetime,
    span_degrees: float,
    angle_at: Callable[[datetime], float],
    step: timedelta = timedelta(hours=2),
) -> list[AngularTransition]:
    if start_utc.tzinfo is None or end_utc.tzinfo is None or end_utc <= start_utc:
        raise TransitionSearchError("Transition interval must contain ordered timezone-aware datetimes")
    left = start_utc.astimezone(UTC)
    end = end_utc.astimezone(UTC)
    left_angle = normalize_degrees(angle_at(left))
    unwrapped = left_angle
    next_boundary = (math.floor(unwrapped / span_degrees) + 1) * span_degrees
    transitions: list[AngularTransition] = []
    while left < end:
        right = min(left + step, end)
        right_angle = normalize_degrees(angle_at(right))
        delta = (right_angle - left_angle) % 360.0
        if delta > 90.0:
            raise TransitionSearchError("Angular transition search encountered a non-continuous interval")
        right_unwrapped = unwrapped + delta
        while next_boundary <= right_unwrapped + 1e-10:
            moment = _root(left, right, left_angle, unwrapped, next_boundary, angle_at)
            transitions.append(AngularTransition(moment, int(round(next_boundary / span_degrees)) % int(round(360.0 / span_degrees))))
            next_boundary += span_degrees
        left, left_angle, unwrapped = right, right_angle, right_unwrapped
    return transitions
