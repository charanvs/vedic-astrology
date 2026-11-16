def normalize_degrees(value: float) -> float:
    normalized = value % 360.0
    return 0.0 if normalized == 0.0 else normalized


def degrees_to_dms(value: float) -> str:
    value = normalize_degrees(value)
    degrees = int(value)
    minutes_total = (value - degrees) * 60.0
    minutes = int(minutes_total)
    seconds = (minutes_total - minutes) * 60.0
    if seconds >= 59.9995:
        seconds = 0.0
        minutes += 1
    if minutes >= 60:
        minutes = 0
        degrees = (degrees + 1) % 360
    return f"{degrees}° {minutes:02d}′ {seconds:06.3f}″"
