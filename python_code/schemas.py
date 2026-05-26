"""Shared data conversion and validation helpers."""

from __future__ import annotations

from pathlib import Path
from typing import Any


class CAIError(Exception):
    status_code = "CAI_ERROR"


class ValidationError(CAIError):
    status_code = "VALIDATION_ERROR"


class StateError(CAIError):
    status_code = "STATE_ERROR"


def from_sqf(value: Any) -> Any:
    """Convert SQF pair arrays into Python dictionaries recursively."""
    if isinstance(value, tuple):
        value = list(value)
    if isinstance(value, list):
        if all(isinstance(item, (list, tuple)) and len(item) == 2 and isinstance(item[0], str) for item in value):
            return {str(key): from_sqf(item_value) for key, item_value in value}
        return [from_sqf(item) for item in value]
    return value


def to_sqf(value: Any) -> Any:
    """Convert Python dictionaries into SQF-safe pair arrays recursively."""
    if isinstance(value, dict):
        return [[str(key), to_sqf(item_value)] for key, item_value in value.items()]
    if isinstance(value, (list, tuple)):
        return [to_sqf(item) for item in value]
    if isinstance(value, Path):
        return str(value)
    return value


def require_dict(value: Any, context: str) -> dict[str, Any]:
    converted = from_sqf(value)
    if not isinstance(converted, dict):
        raise ValidationError(f"{context} must be an SQF key/value payload")
    return converted


def as_bool(value: Any, default: bool = False) -> bool:
    if isinstance(value, bool):
        return value
    if isinstance(value, str):
        return value.strip().lower() in {"1", "true", "yes", "on"}
    if isinstance(value, (int, float)):
        return bool(value)
    return default


def as_float(value: Any, default: float) -> float:
    try:
        return float(value)
    except (TypeError, ValueError):
        return default


def as_int(value: Any, default: int) -> int:
    try:
        return int(float(value))
    except (TypeError, ValueError):
        return default

