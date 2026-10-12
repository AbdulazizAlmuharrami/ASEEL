import re


def normalize_code(value):
    return " ".join((value or "").strip().upper().split())


def slug_code(value, limit=16):
    cleaned = re.sub(r"[^A-Z0-9]+", "-", (value or "").upper()).strip("-")
    return (cleaned or "UNIT")[:limit]


def parse_threshold(value, default=5):
    try:
        number = int(value)
    except (TypeError, ValueError):
        return default
    return number if number > 0 else default
