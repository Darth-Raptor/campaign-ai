"""Manual validation and SQF-safe conversion helpers."""

from __future__ import annotations

import math
import re
from typing import Any, Mapping


class CAIError(Exception):
    status_code = "PY_ERROR"


class ValidationError(CAIError):
    status_code = "PY_VALIDATION_ERROR"


class StateNotInitializedError(CAIError):
    status_code = "PY_STATE_NOT_INITIALIZED"


def from_sqf(value: Any) -> Any:
    if isinstance(value, Mapping):
        return {str(k): from_sqf(v) for k, v in value.items()}
    if isinstance(value, tuple):
        value = list(value)
    if isinstance(value, list):
        if all(isinstance(item, (list, tuple)) and len(item) >= 2 and isinstance(item[0], str) for item in value):
            return {str(item[0]): from_sqf(item[1]) for item in value}
        return [from_sqf(item) for item in value]
    return value


def to_sqf(value: Any) -> Any:
    if isinstance(value, Mapping):
        return [[str(k), to_sqf(v)] for k, v in value.items()]
    if isinstance(value, tuple):
        return [to_sqf(item) for item in value]
    if isinstance(value, list):
        return [to_sqf(item) for item in value]
    if value is None:
        return ""
    if isinstance(value, (str, int, float, bool)):
        return value
    return str(value)


def clamp_number(value: Any, minimum: float, maximum: float, default: float) -> float:
    try:
        number = float(value)
    except (TypeError, ValueError):
        number = default
    if math.isnan(number) or math.isinf(number):
        number = default
    return max(minimum, min(maximum, number))


def as_bool(value: Any, default: bool = False) -> bool:
    if isinstance(value, bool):
        return value
    if isinstance(value, str):
        lowered = value.strip().lower()
        if lowered in {"true", "1", "yes", "y"}:
            return True
        if lowered in {"false", "0", "no", "n"}:
            return False
    if isinstance(value, (int, float)):
        return bool(value)
    return default


def as_position(value: Any, default: list[float] | None = None) -> list[float]:
    if default is None:
        default = [0.0, 0.0, 0.0]
    value = from_sqf(value)
    if not isinstance(value, list) or len(value) < 2:
        return list(default)
    return [
        clamp_number(value[0], -1000000.0, 1000000.0, default[0]),
        clamp_number(value[1], -1000000.0, 1000000.0, default[1]),
        clamp_number(value[2] if len(value) > 2 else 0.0, -1000000.0, 1000000.0, default[2]),
    ]


def require_id(data: Mapping[str, Any], *keys: str) -> str:
    for key in keys:
        raw = data.get(key)
        if raw is not None and str(raw).strip():
            return sanitize_identifier(str(raw))
    raise ValidationError(f"Missing required identifier. Expected one of: {', '.join(keys)}")


def sanitize_identifier(value: str) -> str:
    cleaned = re.sub(r"[^A-Za-z0-9_\-:.]", "_", value.strip())
    if not cleaned:
        raise ValidationError("Identifier resolved to an empty value")
    return cleaned[:96]


def sanitize_save_name(value: Any, default: str = "autosave") -> str:
    raw = str(value or default).strip()
    cleaned = re.sub(r"[^A-Za-z0-9_\-.]", "_", raw)
    return (cleaned or default)[:80]


def normalize_objective(raw: Any) -> dict[str, Any]:
    data = from_sqf(raw)
    if not isinstance(data, Mapping):
        raise ValidationError("Objective must be a mapping or SQF key/value array")
    objective_id = require_id(data, "objectiveId", "id")
    owner = str(data.get("owner", data.get("initialOwner", "UNKNOWN")) or "UNKNOWN").upper()
    control = clamp_number(data.get("control", 100 if owner != "UNKNOWN" else 50), 0, 100, 50)
    return {
        "objectiveId": objective_id,
        "name": str(data.get("name", data.get("objectiveName", objective_id))),
        "objectiveType": str(data.get("objectiveType", data.get("type", "generic"))),
        "owner": owner,
        "control": control,
        "priority": int(clamp_number(data.get("priority", 50), 0, 100, 50)),
        "radius": clamp_number(data.get("radius", 300), 1, 10000, 300),
        "size": str(data.get("size", "medium")),
        "terrainType": str(data.get("terrainType", "mixed")),
        "garrisonSlots": int(clamp_number(data.get("garrisonSlots", 0), 0, 1000, 0)),
        "position": as_position(data.get("position")),
        "debugEnabled": as_bool(data.get("debugEnabled", False)),
    }


def normalize_commander(raw: Any) -> dict[str, Any]:
    data = from_sqf(raw)
    if not isinstance(data, Mapping):
        raise ValidationError("Commander must be a mapping or SQF key/value array")
    commander_id = require_id(data, "commanderId", "id")
    return {
        "commanderId": commander_id,
        "name": str(data.get("name", data.get("commanderName", commander_id))),
        "side": str(data.get("side", "EAST")).upper(),
        "faction": str(data.get("faction", "")),
        "commanderType": str(data.get("commanderType", "conventional")),
        "posture": str(data.get("posture", "BALANCED")).upper(),
        "aoMarker": str(data.get("aoMarker", "")),
        "hqPosition": as_position(data.get("hqPosition")),
        "cycleTime": clamp_number(data.get("cycleTime", 120), 30, 3600, 120),
        "aggression": clamp_number(data.get("aggression", 50), 0, 100, 50),
        "reservePercentage": clamp_number(data.get("reservePercentage", 20), 0, 100, 20),
        "attackThreshold": clamp_number(data.get("attackThreshold", 1.25), 0.1, 10, 1.25),
        "reinforcementThreshold": clamp_number(data.get("reinforcementThreshold", 60), 0, 100, 60),
        "debugEnabled": as_bool(data.get("debugEnabled", False)),
        "persistenceEnabled": as_bool(data.get("persistenceEnabled", True), True),
        "paused": as_bool(data.get("paused", False)),
    }


def normalize_virtual_group(raw: Any) -> dict[str, Any]:
    data = from_sqf(raw)
    if not isinstance(data, Mapping):
        raise ValidationError("Virtual group must be a mapping or SQF key/value array")
    group_id = require_id(data, "groupId", "id")
    force_size = str(data.get("forceSize", "platoon")).lower()
    default_strength = {"platoon": 40, "company": 120, "battalion": 400}.get(force_size, 40)
    return {
        "groupId": group_id,
        "name": str(data.get("name", group_id)),
        "side": str(data.get("side", "EAST")).upper(),
        "faction": str(data.get("faction", "")),
        "commanderId": str(data.get("commanderId", "")),
        "forceSize": force_size,
        "unitType": str(data.get("unitType", data.get("mobility", "infantry"))).lower(),
        "mobility": str(data.get("mobility", "foot")).lower(),
        "position": as_position(data.get("position")),
        "initialObjective": str(data.get("initialObjective", "")),
        "currentObjectiveId": str(data.get("currentObjectiveId", data.get("initialObjective", ""))),
        "strength": int(clamp_number(data.get("strength", default_strength), 0, 5000, default_strength)),
        "readiness": clamp_number(data.get("readiness", 100), 0, 100, 100),
        "morale": clamp_number(data.get("morale", 100), 0, 100, 100),
        "posture": str(data.get("posture", "READY")).upper(),
        "status": str(data.get("status", "IDLE")).upper(),
        "manualOverride": as_bool(data.get("manualOverride", False)),
        "assignedOrder": from_sqf(data.get("assignedOrder", {})),
        "debugEnabled": as_bool(data.get("debugEnabled", False)),
    }


def normalize_init_payload(payload: Any) -> dict[str, Any]:
    data = from_sqf(payload)
    if not isinstance(data, Mapping):
        raise ValidationError("init_state payload must be a mapping or SQF key/value array")
    campaign_id = require_id(data, "campaignId")
    objectives = [normalize_objective(item) for item in data.get("objectives", [])]
    commanders = [normalize_commander(item) for item in data.get("commanders", [])]
    virtual_groups = [normalize_virtual_group(item) for item in data.get("virtualGroups", [])]
    settings = from_sqf(data.get("settings", {}))
    if not isinstance(settings, Mapping):
        settings = {}
    return {
        "campaignId": campaign_id,
        "worldName": str(data.get("worldName", "")),
        "missionName": str(data.get("missionName", "")),
        "objectives": objectives,
        "commanders": commanders,
        "virtualGroups": virtual_groups,
        "settings": dict(settings),
    }


def normalize_commander_cycle_payload(payload: Any) -> dict[str, Any]:
    data = from_sqf(payload)
    if not isinstance(data, Mapping):
        raise ValidationError("commander_cycle payload must be a mapping or SQF key/value array")
    return {
        "commanderId": require_id(data, "commanderId"),
        "gameTime": clamp_number(data.get("gameTime", 0), 0, 10**9, 0),
        "observedEvents": from_sqf(data.get("observedEvents", [])),
    }


def normalize_debug_payload(payload: Any | None) -> dict[str, Any]:
    data = from_sqf(payload or {})
    if not isinstance(data, Mapping):
        data = {}
    return {
        "debugMode": str(data.get("debugMode", "BOTH")).upper(),
        "commanderId": str(data.get("commanderId", "")),
        "gameTime": clamp_number(data.get("gameTime", 0), 0, 10**9, 0),
    }


def normalize_combat_payload(payload: Any) -> dict[str, Any]:
    data = from_sqf(payload)
    if not isinstance(data, Mapping):
        raise ValidationError("resolve_combat_batch payload must be a mapping or SQF key/value array")
    engagements = from_sqf(data.get("engagements", []))
    if not isinstance(engagements, list):
        raise ValidationError("engagements must be an array")
    return {
        "gameTime": clamp_number(data.get("gameTime", 0), 0, 10**9, 0),
        "engagements": engagements,
        "autoDetect": as_bool(data.get("autoDetect", False)),
        "randomness": str(data.get("randomness", "NORMAL")).upper(),
    }

