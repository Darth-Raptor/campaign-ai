"""Runtime world model seeded from a completed map index."""

from __future__ import annotations

import json
import math
from copy import deepcopy
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from . import config
from .schemas import StateError, ValidationError, as_float, as_int, require_dict, from_sqf


@dataclass(frozen=True)
class DensityProfile:
    minimum: int
    maximum: int
    km2_per_objective: float
    spacing: float


DENSITY_PROFILES = {
    "SPARSE": DensityProfile(minimum=8, maximum=75, km2_per_objective=6.0, spacing=1800.0),
    "BALANCED": DensityProfile(minimum=12, maximum=120, km2_per_objective=4.0, spacing=1400.0),
    "DENSE": DensityProfile(minimum=20, maximum=180, km2_per_objective=2.75, spacing=1000.0),
}


@dataclass
class WorldModelState:
    initialized: bool = False
    world_name: str = ""
    mission_name: str = ""
    world_size: float = 0.0
    index_path: str = ""
    density: str = "BALANCED"
    minimum_score: float = 40.0
    initialized_at_utc: str = ""
    objectives: list[dict[str, Any]] = field(default_factory=list)
    source_candidate_count: int = 0
    eligible_candidate_count: int = 0
    target_objective_count: int = 0


_STATE = WorldModelState()


def init_world_model(payload: Any) -> dict[str, Any]:
    data = require_dict(payload, "init_world_model payload")
    mission_root, index_path = _resolve_index_path(data)
    index_data = _load_index(index_path)
    _validate_index(index_data, data)

    density = _normalize_density(data.get("density"))
    minimum_score = max(0.0, min(as_float(data.get("minimumScore"), 40.0), 100.0))
    world = index_data.get("world", {})
    mission = index_data.get("mission", {})
    world_size = as_float(world.get("worldSize"), as_float(data.get("worldSize"), 0.0))

    candidates = [
        item
        for item in _as_dict_list(index_data.get("objectiveCandidates", []))
        if item.get("objectiveEligible", False) and as_float(item.get("score"), 0.0) >= minimum_score
    ]
    sorted_candidates = sorted(candidates, key=lambda item: (-as_float(item.get("score"), 0.0), str(item.get("candidateId", ""))))
    target_count = _target_objective_count(world_size, density, len(sorted_candidates))
    selected = _select_score_and_spread(sorted_candidates, target_count, world_size, density)
    objectives = _build_runtime_objectives(selected)

    global _STATE
    _STATE = WorldModelState(
        initialized=True,
        world_name=str(world.get("worldName") or data.get("worldName") or ""),
        mission_name=str(mission.get("missionName") or data.get("missionName") or ""),
        world_size=world_size,
        index_path=str(index_path),
        density=density,
        minimum_score=minimum_score,
        initialized_at_utc=_utc_now(),
        objectives=objectives,
        source_candidate_count=len(_as_dict_list(index_data.get("objectiveCandidates", []))),
        eligible_candidate_count=len(sorted_candidates),
        target_objective_count=target_count,
    )

    return get_world_model_summary()


def get_world_model_summary() -> dict[str, Any]:
    if not _STATE.initialized:
        raise StateError("Runtime world model is not initialized")
    return {
        "initialized": _STATE.initialized,
        "worldName": _STATE.world_name,
        "missionName": _STATE.mission_name,
        "worldSize": _STATE.world_size,
        "indexPath": _STATE.index_path,
        "density": _STATE.density,
        "minimumScore": _STATE.minimum_score,
        "sourceCandidateCount": _STATE.source_candidate_count,
        "eligibleCandidateCount": _STATE.eligible_candidate_count,
        "targetObjectiveCount": _STATE.target_objective_count,
        "seededObjectiveCount": len(_STATE.objectives),
        "initializedAtUtc": _STATE.initialized_at_utc,
    }


def get_world_debug_markers(payload: Any | None = None) -> dict[str, Any]:
    if not _STATE.initialized:
        raise StateError("Runtime world model is not initialized")
    data = from_sqf(payload or {})
    if not isinstance(data, dict):
        data = {}
    limit = max(1, min(as_int(data.get("limit"), len(_STATE.objectives) or 1), 500))
    markers = [_objective_marker(item) for item in _STATE.objectives[:limit]]
    return {
        "markerCount": len(markers),
        "markers": markers,
        "summary": get_world_model_summary(),
    }


def export_world_model() -> dict[str, Any]:
    if not _STATE.initialized:
        raise StateError("Runtime world model is not initialized")
    return {
        "summary": get_world_model_summary(),
        "objectives": deepcopy(_STATE.objectives),
    }


def _resolve_index_path(data: dict[str, Any]) -> tuple[Path, Path]:
    mission_root_raw = str(data.get("missionRoot") or "").strip()
    index_raw = str(data.get("indexPath") or config.DEFAULT_MAP_INDEX_FILE).strip()
    if not mission_root_raw:
        raise ValidationError("World model requires missionRoot from SQF getMissionPath")
    if not index_raw:
        raise ValidationError("World model requires a non-empty indexPath")

    mission_root = Path(mission_root_raw).expanduser().resolve()
    index_path = Path(index_raw).expanduser()
    if not index_path.is_absolute():
        index_path = mission_root / index_path
    index_path = index_path.resolve()

    try:
        index_path.relative_to(mission_root)
    except ValueError as exc:
        raise ValidationError("World model indexPath must remain inside the mission folder") from exc

    if index_path.suffix.lower() != ".json":
        raise ValidationError("World model index file must be a .json file")

    return mission_root, index_path


def _load_index(index_path: Path) -> dict[str, Any]:
    if not index_path.exists():
        raise ValidationError(f"Map index JSON not found: {index_path}")
    try:
        with index_path.open("r", encoding="utf-8") as handle:
            data = json.load(handle)
    except (OSError, json.JSONDecodeError) as exc:
        raise ValidationError(f"Map index JSON could not be read: {index_path}") from exc
    if not isinstance(data, dict):
        raise ValidationError("Map index JSON root must be an object")
    return data


def _validate_index(index_data: dict[str, Any], payload: dict[str, Any]) -> None:
    if int(index_data.get("schemaVersion", 0)) != config.MAP_INDEX_SCHEMA_VERSION:
        raise ValidationError(f"World model requires map index schema version {config.MAP_INDEX_SCHEMA_VERSION}")

    world = index_data.get("world", {})
    if not isinstance(world, dict):
        raise ValidationError("Map index is missing world metadata")

    expected_world = str(payload.get("worldName") or "")
    index_world = str(world.get("worldName") or "")
    if expected_world and index_world and expected_world != index_world:
        raise ValidationError(f"Map index world mismatch: expected {expected_world}, found {index_world}")

    expected_size = as_float(payload.get("worldSize"), 0.0)
    index_size = as_float(world.get("worldSize"), 0.0)
    if expected_size > 0 and index_size > 0 and abs(expected_size - index_size) > 1.0:
        raise ValidationError(f"Map index world size mismatch: expected {expected_size}, found {index_size}")


def _normalize_density(value: Any) -> str:
    density = str(value or "BALANCED").upper()
    return density if density in DENSITY_PROFILES else "BALANCED"


def _target_objective_count(world_size: float, density: str, candidate_count: int) -> int:
    if candidate_count <= 0:
        return 0
    profile = DENSITY_PROFILES[density]
    area_km2 = max(1.0, (world_size * world_size) / 1_000_000.0)
    scaled = math.ceil(area_km2 / profile.km2_per_objective)
    target = max(profile.minimum, min(profile.maximum, scaled))
    return min(target, candidate_count)


def _select_score_and_spread(
    candidates: list[dict[str, Any]],
    target_count: int,
    world_size: float,
    density: str,
) -> list[dict[str, Any]]:
    if target_count <= 0:
        return []
    profile = DENSITY_PROFILES[density]
    initial_spacing = max(350.0, min(profile.spacing, max(world_size, 1.0) / 8.0))
    spacing_passes = [initial_spacing, initial_spacing * 0.75, initial_spacing * 0.5, 0.0]
    selected: list[dict[str, Any]] = []
    selected_ids: set[str] = set()

    for spacing in spacing_passes:
        for candidate in candidates:
            candidate_id = str(candidate.get("candidateId") or "")
            if candidate_id in selected_ids:
                continue
            if spacing <= 0.0 or _is_spread_enough(candidate, selected, spacing):
                selected.append(candidate)
                selected_ids.add(candidate_id)
                if len(selected) >= target_count:
                    return selected

    return selected


def _is_spread_enough(candidate: dict[str, Any], selected: list[dict[str, Any]], spacing: float) -> bool:
    position = _position(candidate.get("position"))
    return all(_distance_2d(position, _position(item.get("position"))) >= spacing for item in selected)


def _build_runtime_objectives(candidates: list[dict[str, Any]]) -> list[dict[str, Any]]:
    sorted_selected = sorted(candidates, key=lambda item: (-as_float(item.get("score"), 0.0), str(item.get("candidateId", ""))))
    objectives = []
    for index, candidate in enumerate(sorted_selected, start=1):
        score = as_float(candidate.get("score"), 0.0)
        source_type = str(candidate.get("sourceType") or "UNKNOWN")
        candidate_type = str(candidate.get("candidateType") or "generic")
        name = str(candidate.get("name") or source_type or f"Objective {index}")
        reasons = [str(item) for item in from_sqf(candidate.get("reasons", [])) if str(item)]
        objectives.append(
            {
                "objectiveId": f"obj_seed_{index:03d}",
                "name": name,
                "objectiveType": _objective_type(candidate_type, source_type),
                "sourceCandidateId": str(candidate.get("candidateId") or ""),
                "sourceType": source_type,
                "position": _position(candidate.get("position")),
                "radius": _objective_radius(candidate_type, source_type, score),
                "priority": round(score),
                "score": round(score, 2),
                "tier": _objective_tier(score),
                "initialOwner": "NONE",
                "owner": "NONE",
                "control": 0,
                "reasons": reasons,
                "reasonText": "; ".join(reasons[:3]),
            }
        )
    return objectives


def _objective_type(candidate_type: str, source_type: str) -> str:
    if candidate_type:
        return candidate_type
    if source_type in {"NameCity", "NameCityCapital", "NameVillage", "NameLocal", "CityCenter"}:
        return "settlement"
    return "generic"


def _objective_radius(candidate_type: str, source_type: str, score: float) -> int:
    if source_type in {"NameCityCapital", "NameCity", "Airport"}:
        return 500
    if source_type in {"NameVillage", "CityCenter"}:
        return 350
    if candidate_type in {"military", "strategic_location"}:
        return 350
    if candidate_type in {"transport_corridor", "logistics", "port"}:
        return 300
    if score >= 85:
        return 400
    return 250


def _objective_tier(score: float) -> str:
    if score >= 90:
        return "strategic"
    if score >= 70:
        return "major"
    if score >= 50:
        return "minor"
    return "local"


def _objective_marker(objective: dict[str, Any]) -> dict[str, Any]:
    objective_id = str(objective.get("objectiveId") or "obj_seed")
    tier = str(objective.get("tier") or "local")
    priority = as_int(objective.get("priority"), 0)
    name = str(objective.get("name") or objective_id)
    return {
        "markerId": f"CAI_WORLD_{objective_id.upper()}",
        "kind": "seeded_objective",
        "objectiveId": objective_id,
        "position": _position(objective.get("position")),
        "markerType": "mil_objective",
        "markerColor": _tier_marker_color(tier),
        "markerText": f"CAI OBJ {priority} {name}"[:63],
        "tier": tier,
        "priority": priority,
        "score": as_float(objective.get("score"), 0.0),
    }


def _tier_marker_color(tier: str) -> str:
    if tier == "strategic":
        return "ColorRed"
    if tier == "major":
        return "ColorOrange"
    if tier == "minor":
        return "ColorYellow"
    return "ColorGreen"


def _as_dict_list(value: Any) -> list[dict[str, Any]]:
    converted = from_sqf(value)
    if not isinstance(converted, list):
        return []
    return [item for item in converted if isinstance(item, dict)]


def _position(value: Any) -> list[float]:
    converted = from_sqf(value)
    if not isinstance(converted, list):
        return [0.0, 0.0, 0.0]
    out = [as_float(item, 0.0) for item in converted[:3]]
    while len(out) < 3:
        out.append(0.0)
    return out


def _distance_2d(a: list[float], b: list[float]) -> float:
    return math.sqrt((a[0] - b[0]) ** 2 + (a[1] - b[1]) ** 2)


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
