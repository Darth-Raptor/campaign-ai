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
SAME_KIND_GROUP_RADIUS = 100.0
MIXED_KIND_GROUP_RADIUS = 200.0

SIGNIFICANCE_SCORES = {
    "HIGH": 95,
    "MEDIUM": 75,
    "LOW": 55,
}

CUSTOM_OBJECTIVE_TYPES = {"military", "civilian", "industrial", "other"}
CUSTOM_OBJECTIVE_DESCRIPTIONS = {
    "fob",
    "cop",
    "airfield",
    "power_plant",
    "dam",
    "religious_site",
    "tv_radio_station",
    "port",
    "depot",
    "factory",
    "hospital",
    "town_center",
    "bridge",
    "road_junction",
    "observation_post",
    "other",
}
OWNER_ALIASES = {
    "GUER": "INDEPENDENT",
    "GUERRILA": "INDEPENDENT",
    "GUERRILLA": "INDEPENDENT",
    "RESISTANCE": "INDEPENDENT",
}
VALID_OWNERS = {"EAST", "WEST", "INDEPENDENT", "CIVILIAN", "NONE"}
CUSTOM_SUPPRESSION_MIN_RADIUS = {
    "airfield": 2000.0,
    "port": 1200.0,
    "power_plant": 1000.0,
    "factory": 900.0,
    "depot": 900.0,
    "fob": 750.0,
    "cop": 600.0,
    "tv_radio_station": 600.0,
}
CUSTOM_SUPPORT_CANDIDATE_TYPES = {
    "airfield": {"communications", "infrastructure", "logistics", "military", "transport_corridor"},
    "port": {"communications", "infrastructure", "logistics", "transport_corridor"},
    "power_plant": {"communications", "infrastructure", "logistics"},
    "factory": {"communications", "infrastructure", "logistics"},
    "depot": {"communications", "infrastructure", "logistics", "military", "transport_corridor"},
    "fob": {"communications", "infrastructure", "military", "observation"},
    "cop": {"communications", "infrastructure", "military", "observation"},
    "tv_radio_station": {"communications", "infrastructure"},
}
CUSTOM_SUPPORT_SOURCE_TYPES = {
    "TRANSMITTER",
    "VIEW-TOWER",
    "VIEWTOWER",
    "WATERTOWER",
    "FUELSTATION",
    "BUNKER",
    "FORTRESS",
    "RADAR",
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
    custom_objective_count: int = 0
    derived_objective_count: int = 0
    suppressed_candidate_count: int = 0
    grouped_candidate_count: int = 0
    objective_group_count: int = 0


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

    custom_inputs = _normalize_custom_objectives(data.get("customObjectives", []))
    custom_objectives = _build_custom_runtime_objectives(custom_inputs)

    candidates = [
        item
        for item in _as_dict_list(index_data.get("objectiveCandidates", []))
        if item.get("objectiveEligible", False) and as_float(item.get("score"), 0.0) >= minimum_score
    ]
    sorted_candidates = sorted(candidates, key=lambda item: (-as_float(item.get("score"), 0.0), str(item.get("candidateId", ""))))
    unsuppressed_candidates, suppressed_count = _suppress_candidates_near_custom_objectives(sorted_candidates, custom_objectives)
    grouped_candidates, grouped_candidate_count, objective_group_count = _group_objective_candidates(unsuppressed_candidates)
    target_count = _target_objective_count(world_size, density, len(custom_objectives) + len(grouped_candidates))
    derived_slots = max(0, target_count - len(custom_objectives))
    selected = _select_score_and_spread(grouped_candidates, derived_slots, world_size, density)
    derived_objectives = _build_derived_runtime_objectives(selected)
    objectives = custom_objectives + derived_objectives

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
        custom_objective_count=len(custom_objectives),
        derived_objective_count=len(derived_objectives),
        suppressed_candidate_count=suppressed_count,
        grouped_candidate_count=grouped_candidate_count,
        objective_group_count=objective_group_count,
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
        "customObjectiveCount": _STATE.custom_objective_count,
        "derivedObjectiveCount": _STATE.derived_objective_count,
        "suppressedCandidateCount": _STATE.suppressed_candidate_count,
        "groupedCandidateCount": _STATE.grouped_candidate_count,
        "objectiveGroupCount": _STATE.objective_group_count,
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


def _group_objective_candidates(candidates: list[dict[str, Any]]) -> tuple[list[dict[str, Any]], int, int]:
    same_kind_groups = _cluster_candidate_groups(
        candidates,
        SAME_KIND_GROUP_RADIUS,
        group_mode="same_kind",
        require_same_kind=True,
    )
    same_kind_candidates = [_merge_candidate_group(group, "same_kind", SAME_KIND_GROUP_RADIUS) for group in same_kind_groups]
    mixed_groups = _cluster_candidate_groups(
        same_kind_candidates,
        MIXED_KIND_GROUP_RADIUS,
        group_mode="mixed",
        require_same_kind=False,
    )
    grouped_candidates = [_merge_candidate_group(group, "mixed", MIXED_KIND_GROUP_RADIUS) for group in mixed_groups]
    grouped_candidates = sorted(grouped_candidates, key=lambda item: (-as_float(item.get("score"), 0.0), str(item.get("candidateId", ""))))
    grouped_candidate_count = max(0, len(candidates) - len(grouped_candidates))
    objective_group_count = sum(1 for item in grouped_candidates if as_int(item.get("mergedCandidateCount"), 1) > 1)
    return grouped_candidates, grouped_candidate_count, objective_group_count


def _cluster_candidate_groups(
    candidates: list[dict[str, Any]],
    threshold: float,
    group_mode: str,
    require_same_kind: bool,
) -> list[dict[str, Any]]:
    groups: list[dict[str, Any]] = []
    sorted_candidates = sorted(candidates, key=lambda item: (-as_float(item.get("score"), 0.0), str(item.get("candidateId", ""))))

    for candidate in sorted_candidates:
        position = _position(candidate.get("position"))
        candidate_key = _candidate_kind_key(candidate)
        nearest_index = -1
        nearest_distance = threshold
        for index, group in enumerate(groups):
            if require_same_kind and group["kindKey"] != candidate_key:
                continue
            distance = _distance_2d(position, group["position"])
            if distance <= nearest_distance:
                nearest_index = index
                nearest_distance = distance

        if nearest_index < 0:
            weight = _candidate_group_weight(candidate)
            groups.append(
                {
                    "items": [candidate],
                    "position": position,
                    "sourceWeight": weight,
                    "kindKey": candidate_key if require_same_kind else group_mode,
                }
            )
        else:
            group = groups[nearest_index]
            weight = _candidate_group_weight(candidate)
            old_weight = as_int(group.get("sourceWeight"), 1)
            total_weight = old_weight + weight
            group["position"] = [
                ((group["position"][0] * old_weight) + (position[0] * weight)) / total_weight,
                ((group["position"][1] * old_weight) + (position[1] * weight)) / total_weight,
                ((group["position"][2] * old_weight) + (position[2] * weight)) / total_weight,
            ]
            group["sourceWeight"] = total_weight
            group["items"].append(candidate)

    return groups


def _merge_candidate_group(group: dict[str, Any], group_mode: str, threshold: float) -> dict[str, Any]:
    items = sorted(group["items"], key=lambda item: (-as_float(item.get("score"), 0.0), str(item.get("candidateId", ""))))
    best = deepcopy(items[0])
    if len(items) == 1:
        return best
    merged_ids = _merged_candidate_ids(items)
    source_types = sorted({str(item.get("sourceType") or "UNKNOWN") for item in _flatten_group_items(items)})
    candidate_types = sorted({str(item.get("candidateType") or "generic") for item in _flatten_group_items(items)})
    merged_count = len(merged_ids)
    if merged_count <= 1:
        return best

    reasons = [str(item) for item in from_sqf(best.get("reasons", [])) if str(item)]
    reasons.append(f"Grouped {merged_count} nearby objectives within {round(threshold)}m ({group_mode.replace('_', ' ')})")
    best["position"] = _position(group.get("position"))
    best["mergedCandidateCount"] = merged_count
    best["mergedCandidateIds"] = merged_ids
    best["mergedSourceTypes"] = source_types
    best["mergedCandidateTypes"] = candidate_types
    best["groupingMode"] = group_mode
    best["groupingRadius"] = round(threshold)
    best["reasons"] = reasons
    return best


def _flatten_group_items(items: list[dict[str, Any]]) -> list[dict[str, Any]]:
    flattened = []
    for item in items:
        nested_items = item.get("mergedCandidateItems")
        if isinstance(nested_items, list):
            flattened.extend([nested for nested in nested_items if isinstance(nested, dict)])
        else:
            flattened.append(item)
    return flattened


def _merged_candidate_ids(items: list[dict[str, Any]]) -> list[str]:
    merged_ids = []
    for item in items:
        raw_ids = from_sqf(item.get("mergedCandidateIds", []))
        ids = raw_ids if isinstance(raw_ids, list) and raw_ids else [item.get("candidateId", "")]
        for candidate_id in ids:
            candidate_id = str(candidate_id)
            if candidate_id and candidate_id not in merged_ids:
                merged_ids.append(candidate_id)
    return merged_ids


def _candidate_group_weight(candidate: dict[str, Any]) -> int:
    return max(1, as_int(candidate.get("mergedCandidateCount"), 1))


def _candidate_kind_key(candidate: dict[str, Any]) -> tuple[str, str]:
    return (str(candidate.get("candidateType") or "generic"), str(candidate.get("sourceType") or "UNKNOWN"))


def _normalize_custom_objectives(value: Any) -> list[dict[str, Any]]:
    custom_items = _as_dict_list(value)
    normalized = []
    for index, item in enumerate(custom_items, start=1):
        custom_id = str(item.get("customObjectiveId") or f"custom_objective_{index:03d}")
        objective_type = str(item.get("objectiveType") or "other").lower()
        if objective_type not in CUSTOM_OBJECTIVE_TYPES:
            objective_type = "other"

        description = str(item.get("objectiveDescription") or "other").lower()
        if description not in CUSTOM_OBJECTIVE_DESCRIPTIONS:
            description = "other"

        significance = str(item.get("significance") or "MEDIUM").upper()
        if significance not in SIGNIFICANCE_SCORES:
            significance = "MEDIUM"

        owner = _normalize_owner(item.get("initialOwner"))
        radius = max(100, min(round(as_float(item.get("radius"), 300.0)), 1000))
        suppression_radius = _custom_suppression_radius(description, radius)
        position = _position(item.get("position"))
        name = str(item.get("name") or "").strip() or f"Custom Objective {index:03d}"
        normalized.append(
            {
                "customObjectiveId": custom_id,
                "name": name,
                "objectiveType": objective_type,
                "objectiveDescription": description,
                "radius": radius,
                "suppressionRadius": suppression_radius,
                "initialOwner": owner,
                "significance": significance,
                "score": SIGNIFICANCE_SCORES[significance],
                "position": position,
            }
        )

    return sorted(
        normalized,
        key=lambda item: (
            -int(item["score"]),
            str(item["name"]).lower(),
            float(item["position"][0]),
            float(item["position"][1]),
            str(item["customObjectiveId"]),
        ),
    )


def _normalize_owner(value: Any) -> str:
    owner = str(value or "NONE").upper()
    owner = OWNER_ALIASES.get(owner, owner)
    return owner if owner in VALID_OWNERS else "NONE"


def _custom_suppression_radius(description: str, radius: int) -> int:
    minimum = CUSTOM_SUPPRESSION_MIN_RADIUS.get(description, float(radius))
    return round(max(float(radius), minimum))


def _build_custom_runtime_objectives(custom_items: list[dict[str, Any]]) -> list[dict[str, Any]]:
    objectives = []
    for index, item in enumerate(custom_items, start=1):
        score = as_float(item.get("score"), 75.0)
        owner = str(item.get("initialOwner") or "NONE")
        radius = as_int(item.get("radius"), 300)
        suppression_radius = as_int(item.get("suppressionRadius"), radius)
        reasons = [
            "Custom objective placed in Eden",
            f"Significance {item.get('significance', 'MEDIUM')}",
        ]
        if suppression_radius > radius:
            reasons.append(f"{item.get('objectiveDescription', 'other')} support footprint {suppression_radius}m")
        objectives.append(
            {
                "objectiveId": f"obj_custom_{index:03d}",
                "name": str(item.get("name") or f"Custom Objective {index:03d}"),
                "objectiveType": str(item.get("objectiveType") or "other"),
                "objectiveDescription": str(item.get("objectiveDescription") or "other"),
                "sourceCandidateId": str(item.get("customObjectiveId") or ""),
                "sourceType": "CUSTOM",
                "position": _position(item.get("position")),
                "radius": radius,
                "suppressionRadius": suppression_radius,
                "priority": round(score),
                "score": round(score, 2),
                "tier": _objective_tier(score),
                "initialOwner": owner,
                "owner": owner,
                "control": 0 if owner == "NONE" else 100,
                "significance": str(item.get("significance") or "MEDIUM"),
                "isCustom": True,
                "reasons": reasons,
                "reasonText": "; ".join(reasons),
            }
        )
    return objectives


def _suppress_candidates_near_custom_objectives(
    candidates: list[dict[str, Any]],
    custom_objectives: list[dict[str, Any]],
) -> tuple[list[dict[str, Any]], int]:
    if not custom_objectives:
        return candidates, 0

    kept = []
    suppressed_count = 0
    for candidate in candidates:
        if any(_should_suppress_candidate_for_custom(candidate, custom) for custom in custom_objectives):
            suppressed_count += 1
            continue
        kept.append(candidate)

    return kept, suppressed_count


def _should_suppress_candidate_for_custom(candidate: dict[str, Any], custom: dict[str, Any]) -> bool:
    distance = _distance_2d(_position(candidate.get("position")), _position(custom.get("position")))
    radius = as_float(custom.get("radius"), 300.0)
    if distance <= radius:
        return True

    support_radius = as_float(custom.get("suppressionRadius"), radius)
    return distance <= support_radius and _is_support_candidate_for_custom(candidate, custom)


def _is_support_candidate_for_custom(candidate: dict[str, Any], custom: dict[str, Any]) -> bool:
    description = str(custom.get("objectiveDescription") or "other").lower()
    candidate_type = str(candidate.get("candidateType") or "").lower()
    source_type = str(candidate.get("sourceType") or "").upper()
    candidate_name = str(candidate.get("name") or "").lower()
    support_types = CUSTOM_SUPPORT_CANDIDATE_TYPES.get(description, set())
    if description == "airfield" and ("airfield" in candidate_name or "airport" in candidate_name or source_type == "AIRPORT"):
        return True
    return candidate_type in support_types or source_type in CUSTOM_SUPPORT_SOURCE_TYPES


def _build_derived_runtime_objectives(candidates: list[dict[str, Any]]) -> list[dict[str, Any]]:
    sorted_selected = sorted(candidates, key=lambda item: (-as_float(item.get("score"), 0.0), str(item.get("candidateId", ""))))
    objectives = []
    for index, candidate in enumerate(sorted_selected, start=1):
        score = as_float(candidate.get("score"), 0.0)
        source_type = str(candidate.get("sourceType") or "UNKNOWN")
        candidate_type = str(candidate.get("candidateType") or "generic")
        name = str(candidate.get("name") or source_type or f"Objective {index}")
        reasons = [str(item) for item in from_sqf(candidate.get("reasons", [])) if str(item)]
        objective = {
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
            "isCustom": False,
            "reasons": reasons,
            "reasonText": "; ".join(reasons[:3]),
        }
        merged_count = as_int(candidate.get("mergedCandidateCount"), 1)
        if merged_count > 1:
            objective["mergedCandidateCount"] = merged_count
            objective["mergedCandidateIds"] = from_sqf(candidate.get("mergedCandidateIds", []))
            objective["mergedSourceTypes"] = from_sqf(candidate.get("mergedSourceTypes", []))
            objective["mergedCandidateTypes"] = from_sqf(candidate.get("mergedCandidateTypes", []))
            objective["groupingMode"] = str(candidate.get("groupingMode") or "")
            objective["groupingRadius"] = as_int(candidate.get("groupingRadius"), 0)
            objective["reasonText"] = "; ".join(reasons[:2] + reasons[-1:])
        objectives.append(objective)
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
    is_custom = bool(objective.get("isCustom", False))
    merged_count = as_int(objective.get("mergedCandidateCount"), 1)
    grouped_suffix = f" x{merged_count}" if (not is_custom and merged_count > 1) else ""
    return {
        "markerId": f"CAI_WORLD_{objective_id.upper()}",
        "kind": "custom_objective" if is_custom else "seeded_objective",
        "objectiveId": objective_id,
        "position": _position(objective.get("position")),
        "markerType": "mil_objective",
        "markerColor": _owner_marker_color(str(objective.get("owner") or "NONE")) if is_custom else _tier_marker_color(tier),
        "markerText": (f"CAI CUSTOM {priority} {name}" if is_custom else f"CAI OBJ {priority} {name}{grouped_suffix}")[:63],
        "tier": tier,
        "priority": priority,
        "score": as_float(objective.get("score"), 0.0),
        "isCustom": is_custom,
        "mergedCandidateCount": merged_count,
    }


def _tier_marker_color(tier: str) -> str:
    if tier == "strategic":
        return "ColorRed"
    if tier == "major":
        return "ColorOrange"
    if tier == "minor":
        return "ColorYellow"
    return "ColorGreen"


def _owner_marker_color(owner: str) -> str:
    if owner == "EAST":
        return "ColorRed"
    if owner == "WEST":
        return "ColorBlue"
    if owner == "INDEPENDENT":
        return "ColorGreen"
    return "ColorWhite"


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
