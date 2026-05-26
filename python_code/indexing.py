"""Map indexing session storage, normalization, and JSON writing."""

from __future__ import annotations

import json
import math
import tempfile
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from . import config
from .schemas import StateError, ValidationError, as_bool, as_float, as_int, require_dict, from_sqf


TACTICAL_CATEGORIES = {
    "BUNKER": "military",
    "FORTRESS": "military",
    "TRANSMITTER": "communications",
    "VIEW-TOWER": "observation",
    "FUELSTATION": "logistics",
    "HOSPITAL": "civilian",
    "WATERTOWER": "infrastructure",
    "POWER LINES": "infrastructure",
    "POWERSOLAR": "infrastructure",
    "POWERWIND": "infrastructure",
    "POWERWAVE": "infrastructure",
    "RAILWAY": "transport",
    "QUAY": "port",
    "CHURCH": "civilian",
    "CHAPEL": "civilian",
    "LIGHTHOUSE": "navigation",
    "SHIPWRECK": "maritime",
}


@dataclass
class IndexSession:
    index_id: str
    world_name: str
    mission_name: str
    world_size: float
    mission_root: Path
    output_path: Path
    settings: dict[str, Any]
    locations: dict[str, dict[str, Any]] = field(default_factory=dict)
    terrain_cells: dict[str, dict[str, Any]] = field(default_factory=dict)
    roads: dict[str, dict[str, Any]] = field(default_factory=dict)
    tactical_sites: dict[str, dict[str, Any]] = field(default_factory=dict)
    batch_count: int = 0
    started_at_utc: str = field(default_factory=lambda: _utc_now())


_SESSIONS: dict[str, IndexSession] = {}


def begin_map_index(payload: Any) -> dict[str, Any]:
    data = require_dict(payload, "begin_map_index payload")
    index_id = str(data.get("indexId") or f"{data.get('worldName', 'world')}_{data.get('missionName', 'mission')}")
    world_name = str(data.get("worldName") or "")
    mission_name = str(data.get("missionName") or "")
    world_size = as_float(data.get("worldSize"), 0.0)
    mission_root, output_path = _resolve_output_paths(data)

    settings = {
        "cellSize": as_int(data.get("cellSize"), 500),
        "roadScanRadius": as_int(data.get("roadScanRadius"), 350),
        "objectScanRadius": as_int(data.get("objectScanRadius"), 300),
        "debugMarkers": as_bool(data.get("debugMarkers"), True),
    }
    force_reindex = as_bool(data.get("forceReindex"), False)

    if output_path.exists() and not force_reindex:
        existing = _load_existing_index(output_path)
        if existing and _existing_matches(existing, world_name, world_size, settings):
            return {
                "indexId": index_id,
                "skipScan": True,
                "outputPath": str(output_path),
                "summary": existing.get("summary", {}),
            }

    _SESSIONS[index_id] = IndexSession(
        index_id=index_id,
        world_name=world_name,
        mission_name=mission_name,
        world_size=world_size,
        mission_root=mission_root,
        output_path=output_path,
        settings=settings,
    )

    return {
        "indexId": index_id,
        "skipScan": False,
        "outputPath": str(output_path),
        "settings": settings,
    }


def add_map_index_batch(payload: Any) -> dict[str, Any]:
    data = require_dict(payload, "add_map_index_batch payload")
    index_id = str(data.get("indexId") or "")
    session = _get_session(index_id)
    session.batch_count += 1

    for item in _as_dict_list(data.get("locations", [])):
        location_id = str(item.get("locationId") or _position_key("loc", item.get("position", []), item.get("type", "")))
        session.locations[location_id] = _normalize_location(location_id, item)

    for item in _as_dict_list(data.get("terrainCells", [])):
        cell_id = str(item.get("cellId") or _position_key("cell", item.get("center", [])))
        session.terrain_cells[cell_id] = _normalize_terrain_cell(cell_id, item)

    for item in _as_dict_list(data.get("roads", [])):
        road_id = str(item.get("roadId") or _position_key("road", item.get("position", [])))
        session.roads[road_id] = _normalize_road(road_id, item)

    for item in _as_dict_list(data.get("tacticalSites", [])):
        site_id = str(item.get("siteId") or _position_key("site", item.get("position", []), item.get("type", "")))
        session.tactical_sites[site_id] = _normalize_tactical_site(site_id, item)

    return {
        "indexId": index_id,
        "batchCount": session.batch_count,
        "locationCount": len(session.locations),
        "terrainCellCount": len(session.terrain_cells),
        "roadCount": len(session.roads),
        "tacticalSiteCount": len(session.tactical_sites),
    }


def finalize_map_index(payload: Any) -> dict[str, Any]:
    data = require_dict(payload, "finalize_map_index payload")
    index_id = str(data.get("indexId") or "")
    session = _get_session(index_id)
    road_edges = _build_road_edges(session.roads)
    derived = _derive_map_products(session)
    summary = _summary(session, road_edges, derived)
    index_data = {
        "schemaVersion": config.MAP_INDEX_SCHEMA_VERSION,
        "generatedAtUtc": _utc_now(),
        "world": {
            "worldName": session.world_name,
            "worldSize": session.world_size,
        },
        "mission": {
            "missionName": session.mission_name,
        },
        "settings": session.settings,
        "locations": _sorted_values(session.locations, "locationId"),
        "roadNodes": _sorted_values(session.roads, "roadId"),
        "roadEdges": road_edges,
        "terrainCells": _sorted_values(session.terrain_cells, "cellId"),
        "tacticalSites": _sorted_values(session.tactical_sites, "siteId"),
        "objectiveCandidates": derived["objectiveCandidates"],
        "terrainFeatureCandidates": derived["terrainFeatureCandidates"],
        "infrastructureCorridors": derived["infrastructureCorridors"],
        "dataQuality": derived["dataQuality"],
        "summary": summary,
    }

    _write_json_atomic(session.output_path, index_data)
    del _SESSIONS[index_id]

    return {
        "indexId": index_id,
        "outputPath": str(session.output_path),
        "summary": summary,
    }


def get_map_index_debug_markers(payload: Any) -> dict[str, Any]:
    data = require_dict(payload, "get_map_index_debug_markers payload")
    _mission_root, output_path = _resolve_output_paths(data)
    marker_mode = str(data.get("markerMode") or "OBJECTIVES").upper()
    limit = max(1, min(as_int(data.get("limit"), config.DEFAULT_MAP_INDEX_DEBUG_MARKER_LIMIT), 500))
    index_data = _load_existing_index(output_path)
    if not index_data:
        raise ValidationError(f"Map index JSON not found or unreadable: {output_path}")
    if int(index_data.get("schemaVersion", 0)) < 2:
        raise ValidationError("Map index debug markers require schema version 2 or newer")

    objective_candidates = [item for item in index_data.get("objectiveCandidates", []) if item.get("objectiveEligible", False)]
    terrain_features = index_data.get("terrainFeatureCandidates", [])
    corridors = index_data.get("infrastructureCorridors", [])

    if marker_mode == "OBJECTIVES_CONTEXT":
        objective_limit = min(70, limit)
        remaining = limit - objective_limit
        terrain_limit = remaining // 2
        corridor_limit = remaining - terrain_limit
        selected = (
            _marker_records(objective_candidates[:objective_limit], "objective")
            + _marker_records(terrain_features[:terrain_limit], "terrain")
            + _marker_records(corridors[:corridor_limit], "corridor")
        )
        if len(selected) < limit:
            selected.extend(_marker_records(objective_candidates[objective_limit:limit], "objective"))
    else:
        marker_mode = "OBJECTIVES"
        selected = _marker_records(objective_candidates[:limit], "objective")

    return {
        "markerMode": marker_mode,
        "limit": limit,
        "markerCount": min(len(selected), limit),
        "markers": selected[:limit],
        "summary": {
            "objectiveCandidateCount": len(objective_candidates),
            "terrainFeatureCandidateCount": len(terrain_features),
            "infrastructureCorridorCount": len(corridors),
        },
    }


def _resolve_output_paths(data: dict[str, Any]) -> tuple[Path, Path]:
    mission_root_raw = str(data.get("missionRoot") or "").strip()
    output_raw = str(data.get("outputPath") or config.DEFAULT_MAP_INDEX_FILE).strip()
    if not mission_root_raw:
        raise ValidationError("Map index requires missionRoot from SQF getMissionPath")
    if not output_raw:
        raise ValidationError("Map index requires a non-empty outputPath")

    mission_root = Path(mission_root_raw).expanduser().resolve()
    output_path = Path(output_raw).expanduser()
    if not output_path.is_absolute():
        output_path = mission_root / output_path
    output_path = output_path.resolve()

    try:
        output_path.relative_to(mission_root)
    except ValueError as exc:
        raise ValidationError("Map index outputPath must remain inside the mission folder") from exc

    if output_path.suffix.lower() != ".json":
        raise ValidationError("Map index output file must be a .json file")

    return mission_root, output_path


def _marker_records(items: list[dict[str, Any]], marker_kind: str) -> list[dict[str, Any]]:
    records = []
    for index, item in enumerate(items, start=1):
        records.append(_marker_record(item, marker_kind, index))
    return records


def _marker_record(item: dict[str, Any], marker_kind: str, index: int) -> dict[str, Any]:
    source_type = str(item.get("sourceType") or item.get("candidateType") or item.get("corridorType") or "UNKNOWN")
    name = str(item.get("name") or source_type)
    score = as_float(item.get("score"), 0.0)
    position = _position(item.get("position"))
    safe_source = _safe_id(str(item.get("candidateId") or item.get("corridorId") or item.get("sourceId") or index))[:32]
    if not safe_source:
        safe_source = str(index)

    if marker_kind == "terrain":
        marker_type = "mil_triangle"
        marker_color = "ColorOrange"
        label = f"CAI TERR {score:.0f} {name}"
    elif marker_kind == "corridor":
        marker_type = "mil_box"
        marker_color = "ColorYellow"
        label = f"CAI CORR {score:.0f} {name}"
    else:
        marker_type = "mil_dot"
        marker_color = _objective_marker_color(source_type)
        label = f"CAI OBJ {score:.0f} {name}"

    return {
        "markerId": f"CAI_IDX_{marker_kind.upper()}_{index:03d}_{safe_source}",
        "kind": marker_kind,
        "position": position,
        "markerType": marker_type,
        "markerColor": marker_color,
        "markerText": label[:63],
        "score": score,
        "sourceType": source_type,
        "sourceId": str(item.get("sourceId") or item.get("candidateId") or item.get("corridorId") or ""),
        "reasons": item.get("reasons", []),
    }


def _objective_marker_color(source_type: str) -> str:
    if source_type in {"NameCity", "NameCityCapital", "NameVillage", "NameLocal", "CityCenter"}:
        return "ColorGreen"
    if source_type in {"BUNKER", "FORTRESS", "StrongpointArea"}:
        return "ColorRed"
    if source_type in {"TRANSMITTER", "VIEW-TOWER"}:
        return "ColorBlue"
    if source_type in {"FUELSTATION", "RAILWAY", "QUAY"}:
        return "ColorYellow"
    return "ColorWhite"


def _load_existing_index(path: Path) -> dict[str, Any] | None:
    try:
        with path.open("r", encoding="utf-8") as handle:
            data = json.load(handle)
        return data if isinstance(data, dict) else None
    except (OSError, json.JSONDecodeError):
        return None


def _existing_matches(data: dict[str, Any], world_name: str, world_size: float, settings: dict[str, Any]) -> bool:
    world = data.get("world", {})
    existing_settings = data.get("settings", {})
    return (
        data.get("schemaVersion") == config.MAP_INDEX_SCHEMA_VERSION
        and world.get("worldName") == world_name
        and abs(float(world.get("worldSize", -1)) - world_size) < 0.01
        and all(existing_settings.get(key) == value for key, value in settings.items())
    )


def _get_session(index_id: str) -> IndexSession:
    if not index_id or index_id not in _SESSIONS:
        raise StateError(f"Map index session not found: {index_id}")
    return _SESSIONS[index_id]


def _as_dict_list(value: Any) -> list[dict[str, Any]]:
    converted = from_sqf(value)
    if not isinstance(converted, list):
        return []
    return [item for item in converted if isinstance(item, dict)]


def _normalize_location(location_id: str, item: dict[str, Any]) -> dict[str, Any]:
    return {
        "locationId": location_id,
        "name": str(item.get("name") or ""),
        "type": str(item.get("type") or "UNKNOWN"),
        "category": str(item.get("category") or "terrain"),
        "position": _position(item.get("position")),
        "source": str(item.get("source") or "nearestLocations"),
    }


def _normalize_terrain_cell(cell_id: str, item: dict[str, Any]) -> dict[str, Any]:
    return {
        "cellId": cell_id,
        "center": _position(item.get("center")),
        "cellSize": as_float(item.get("cellSize"), 0.0),
        "heightASL": as_float(item.get("heightASL"), 0.0),
        "surfaceType": str(item.get("surfaceType") or ""),
        "isWater": as_bool(item.get("isWater"), False),
        "slopeEstimate": as_float(item.get("slopeEstimate"), 0.0),
        "roadDensity": as_int(item.get("roadDensity"), 0),
        "structureDensity": as_int(item.get("structureDensity"), 0),
        "terrainCategory": str(item.get("terrainCategory") or "open"),
    }


def _normalize_road(road_id: str, item: dict[str, Any]) -> dict[str, Any]:
    return {
        "roadId": road_id,
        "position": _position(item.get("position")),
        "roadInfo": from_sqf(item.get("roadInfo", [])),
        "connectedRoadIds": [str(value) for value in from_sqf(item.get("connectedRoadIds", [])) if str(value)],
        "source": str(item.get("source") or "nearRoads"),
    }


def _normalize_tactical_site(site_id: str, item: dict[str, Any]) -> dict[str, Any]:
    site_type = str(item.get("type") or "UNKNOWN")
    return {
        "siteId": site_id,
        "type": site_type,
        "category": TACTICAL_CATEGORIES.get(site_type, "other"),
        "position": _position(item.get("position")),
        "confidence": as_float(item.get("confidence"), 1.0),
        "source": str(item.get("source") or "nearestTerrainObjects"),
    }


def _position(value: Any) -> list[float]:
    converted = from_sqf(value)
    if not isinstance(converted, list):
        return [0.0, 0.0, 0.0]
    out = [as_float(item, 0.0) for item in converted[:3]]
    while len(out) < 3:
        out.append(0.0)
    return out


def _position_key(prefix: str, position: Any, extra: Any = "") -> str:
    pos = _position(position)
    return f"{prefix}_{extra}_{round(pos[0] * 10)}_{round(pos[1] * 10)}"


def _build_road_edges(roads: dict[str, dict[str, Any]]) -> list[dict[str, Any]]:
    edges: dict[str, dict[str, Any]] = {}
    for road_id, road in roads.items():
        for connected_id in road.get("connectedRoadIds", []):
            if connected_id == road_id or connected_id not in roads:
                continue
            edge_id = "__".join(sorted([road_id, connected_id]))
            if edge_id in edges:
                continue
            edges[edge_id] = {
                "edgeId": edge_id,
                "from": road_id,
                "to": connected_id,
                "distance": _distance_2d(road["position"], roads[connected_id]["position"]),
                "routeType": "road",
            }
    return sorted(edges.values(), key=lambda item: item["edgeId"])


def _derive_map_products(session: IndexSession) -> dict[str, Any]:
    terrain_features = _build_terrain_feature_candidates(session.locations)
    corridors = _build_infrastructure_corridors(session.tactical_sites)
    objective_candidates = _build_objective_candidates(session, corridors)
    data_quality = _build_data_quality(session, objective_candidates, terrain_features, corridors)
    return {
        "objectiveCandidates": objective_candidates,
        "terrainFeatureCandidates": terrain_features,
        "infrastructureCorridors": corridors,
        "dataQuality": data_quality,
    }


def _build_objective_candidates(session: IndexSession, corridors: list[dict[str, Any]]) -> list[dict[str, Any]]:
    candidates: list[dict[str, Any]] = []
    settlement_scores = {
        "NameCityCapital": 95,
        "NameCity": 85,
        "CityCenter": 75,
        "NameVillage": 70,
        "Airport": 90,
        "Strategic": 65,
        "StrongpointArea": 75,
    }

    for location in session.locations.values():
        location_type = str(location.get("type", "UNKNOWN"))
        name = str(location.get("name", ""))
        if location_type == "NameLocal" and name:
            base_score = 45
        elif location_type in settlement_scores:
            base_score = settlement_scores[location_type]
        else:
            continue

        position = _position(location.get("position"))
        score, reasons = _score_candidate(
            base_score,
            position,
            session.roads,
            session.tactical_sites,
            session.terrain_cells,
            [f"Location type {location_type}"],
        )
        candidates.append(
            {
                "candidateId": f"cand_location_{location['locationId']}",
                "candidateType": "settlement" if location_type.startswith("Name") or location_type == "CityCenter" else "strategic_location",
                "sourceId": location["locationId"],
                "sourceType": location_type,
                "name": name,
                "position": position,
                "score": score,
                "objectiveEligible": True,
                "reasons": reasons,
            }
        )

    tactical_scores = {
        "BUNKER": 70,
        "FORTRESS": 75,
        "FUELSTATION": 55,
        "TRANSMITTER": 60,
        "VIEW-TOWER": 45,
        "HOSPITAL": 40,
        "WATERTOWER": 35,
        "QUAY": 60,
    }
    excluded_individual_sites = {"POWER LINES", "RAILWAY"}

    for site in session.tactical_sites.values():
        site_type = str(site.get("type", "UNKNOWN"))
        if site_type in excluded_individual_sites or site_type not in tactical_scores:
            continue
        position = _position(site.get("position"))
        score, reasons = _score_candidate(
            tactical_scores[site_type],
            position,
            session.roads,
            session.tactical_sites,
            session.terrain_cells,
            [f"Tactical site type {site_type}"],
        )
        candidates.append(
            {
                "candidateId": f"cand_site_{site['siteId']}",
                "candidateType": str(site.get("category", "tactical_site")),
                "sourceId": site["siteId"],
                "sourceType": site_type,
                "name": "",
                "position": position,
                "score": score,
                "objectiveEligible": True,
                "reasons": reasons,
            }
        )

    for corridor in corridors:
        if not corridor.get("objectiveEligible", False):
            continue
        candidates.append(
            {
                "candidateId": f"cand_{corridor['corridorId']}",
                "candidateType": "transport_corridor",
                "sourceId": corridor["corridorId"],
                "sourceType": corridor["sourceType"],
                "name": corridor["name"],
                "position": corridor["position"],
                "score": corridor["score"],
                "objectiveEligible": True,
                "reasons": corridor["reasons"],
            }
        )

    return sorted(candidates, key=lambda item: (-float(item["score"]), item["candidateId"]))


def _build_terrain_feature_candidates(locations: dict[str, dict[str, Any]]) -> list[dict[str, Any]]:
    mounts = [item for item in locations.values() if item.get("type") == "Mount"]
    clusters = _cluster_spatial_items(mounts, threshold=750.0, id_prefix="terrain_mount")
    candidates = []
    for cluster in clusters:
        count = int(cluster["sourceCount"])
        score = min(35, 10 + count)
        candidates.append(
            {
                "candidateId": cluster["clusterId"],
                "candidateType": "terrain_feature",
                "sourceType": "Mount",
                "name": "High ground cluster",
                "position": cluster["position"],
                "sourceCount": count,
                "sampleSourceIds": cluster["sampleSourceIds"],
                "score": score,
                "objectiveEligible": False,
                "reasons": [
                    f"Aggregated {count} Mount records",
                    "Downranked terrain feature; not objective-eligible by default",
                ],
            }
        )
    return sorted(candidates, key=lambda item: (-int(item["sourceCount"]), item["candidateId"]))


def _build_infrastructure_corridors(tactical_sites: dict[str, dict[str, Any]]) -> list[dict[str, Any]]:
    corridors = []
    for site_type in ["POWER LINES", "RAILWAY"]:
        sites = [item for item in tactical_sites.values() if item.get("type") == site_type]
        clusters = _cluster_spatial_items(sites, threshold=500.0, id_prefix=f"corridor_{_safe_id(site_type)}")
        for cluster in clusters:
            count = int(cluster["sourceCount"])
            is_rail = site_type == "RAILWAY"
            corridors.append(
                {
                    "corridorId": cluster["clusterId"],
                    "corridorType": "transport" if is_rail else "infrastructure",
                    "sourceType": site_type,
                    "name": "Rail corridor" if is_rail else "Power-line corridor",
                    "position": cluster["position"],
                    "sourceCount": count,
                    "sampleSourceIds": cluster["sampleSourceIds"],
                    "score": min(65, 35 + count) if is_rail else min(35, 10 + count),
                    "objectiveEligible": is_rail,
                    "reasons": [
                        f"Aggregated {count} {site_type} records",
                        "Transport corridor candidate" if is_rail else "Infrastructure source only; individual power-line objects are not objectives",
                    ],
                }
            )
    return sorted(corridors, key=lambda item: (item["sourceType"], -int(item["sourceCount"]), item["corridorId"]))


def _build_data_quality(
    session: IndexSession,
    objective_candidates: list[dict[str, Any]],
    terrain_features: list[dict[str, Any]],
    corridors: list[dict[str, Any]],
) -> dict[str, Any]:
    mount_count = sum(1 for item in session.locations.values() if item.get("type") == "Mount")
    power_line_count = sum(1 for item in session.tactical_sites.values() if item.get("type") == "POWER LINES")
    railway_count = sum(1 for item in session.tactical_sites.values() if item.get("type") == "RAILWAY")
    warnings = []
    if mount_count:
        warnings.append(f"{mount_count} raw Mount records were clustered/downranked for derived consumers")
    if power_line_count:
        warnings.append(f"{power_line_count} raw POWER LINES records were aggregated into corridors")
    if railway_count:
        warnings.append(f"{railway_count} raw RAILWAY records were aggregated into corridors")

    return {
        "rawMountCount": mount_count,
        "rawPowerLineCount": power_line_count,
        "rawRailwayCount": railway_count,
        "objectiveCandidateCount": len(objective_candidates),
        "terrainFeatureCandidateCount": len(terrain_features),
        "infrastructureCorridorCount": len(corridors),
        "warnings": warnings,
    }


def _score_candidate(
    base_score: float,
    position: list[float],
    roads: dict[str, dict[str, Any]],
    tactical_sites: dict[str, dict[str, Any]],
    terrain_cells: dict[str, dict[str, Any]],
    reasons: list[str],
) -> tuple[float, list[str]]:
    score = float(base_score)
    road_count = _nearby_count(position, roads.values(), "position", 500.0)
    tactical_count = _nearby_count(position, tactical_sites.values(), "position", 500.0)
    terrain = _nearest_item(position, terrain_cells.values(), "center")
    road_bonus = min(15, road_count * 2)
    tactical_bonus = min(10, tactical_count)
    if road_bonus:
        score += road_bonus
        reasons.append(f"Nearby road access bonus +{road_bonus}")
    if tactical_bonus:
        score += tactical_bonus
        reasons.append(f"Nearby tactical-site density bonus +{tactical_bonus}")
    if terrain:
        terrain_category = str(terrain.get("terrainCategory", "open"))
        if terrain_category == "urban":
            score += 5
            reasons.append("Urban terrain bonus +5")
        elif terrain_category == "roadside":
            score += 3
            reasons.append("Roadside terrain bonus +3")
        elif terrain_category in {"rough", "water"}:
            score -= 5
            reasons.append(f"{terrain_category} terrain penalty -5")
    return round(max(0, min(100, score)), 2), reasons


def _cluster_spatial_items(items: list[dict[str, Any]], threshold: float, id_prefix: str) -> list[dict[str, Any]]:
    clusters: list[dict[str, Any]] = []
    for item in items:
        position = _position(item.get("position"))
        nearest_index = -1
        nearest_distance = threshold
        for index, cluster in enumerate(clusters):
            distance = _distance_2d(position, cluster["position"])
            if distance <= nearest_distance:
                nearest_index = index
                nearest_distance = distance
        if nearest_index < 0:
            clusters.append(
                {
                    "position": position,
                    "sourceCount": 1,
                    "sampleSourceIds": [str(item.get("locationId") or item.get("siteId") or "")],
                }
            )
        else:
            cluster = clusters[nearest_index]
            count = int(cluster["sourceCount"])
            cluster["position"] = [
                ((cluster["position"][0] * count) + position[0]) / (count + 1),
                ((cluster["position"][1] * count) + position[1]) / (count + 1),
                ((cluster["position"][2] * count) + position[2]) / (count + 1),
            ]
            cluster["sourceCount"] = count + 1
            if len(cluster["sampleSourceIds"]) < 25:
                cluster["sampleSourceIds"].append(str(item.get("locationId") or item.get("siteId") or ""))

    for index, cluster in enumerate(clusters, start=1):
        cluster["clusterId"] = f"{id_prefix}_{index:03d}"
    return clusters


def _nearby_count(position: list[float], items: Any, position_key: str, radius: float) -> int:
    radius_sq = radius * radius
    count = 0
    for item in items:
        other = _position(item.get(position_key))
        if ((position[0] - other[0]) ** 2 + (position[1] - other[1]) ** 2) <= radius_sq:
            count += 1
    return count


def _nearest_item(position: list[float], items: Any, position_key: str) -> dict[str, Any] | None:
    nearest = None
    nearest_distance = float("inf")
    for item in items:
        other = _position(item.get(position_key))
        distance = _distance_2d(position, other)
        if distance < nearest_distance:
            nearest = item
            nearest_distance = distance
    return nearest


def _safe_id(value: str) -> str:
    return "".join(char.lower() if char.isalnum() else "_" for char in value).strip("_")


def _distance_2d(a: list[float], b: list[float]) -> float:
    return math.sqrt((a[0] - b[0]) ** 2 + (a[1] - b[1]) ** 2)


def _summary(session: IndexSession, road_edges: list[dict[str, Any]], derived: dict[str, Any]) -> dict[str, Any]:
    data_quality = derived["dataQuality"]
    return {
        "worldName": session.world_name,
        "missionName": session.mission_name,
        "locationCount": len(session.locations),
        "terrainCellCount": len(session.terrain_cells),
        "roadNodeCount": len(session.roads),
        "roadEdgeCount": len(road_edges),
        "tacticalSiteCount": len(session.tactical_sites),
        "objectiveCandidateCount": data_quality["objectiveCandidateCount"],
        "terrainFeatureCandidateCount": data_quality["terrainFeatureCandidateCount"],
        "infrastructureCorridorCount": data_quality["infrastructureCorridorCount"],
        "rawMountCount": data_quality["rawMountCount"],
        "rawPowerLineCount": data_quality["rawPowerLineCount"],
        "batchCount": session.batch_count,
        "outputPath": str(session.output_path),
    }


def _sorted_values(items: dict[str, dict[str, Any]], key: str) -> list[dict[str, Any]]:
    return sorted(items.values(), key=lambda item: str(item.get(key, "")))


def _write_json_atomic(path: Path, data: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile("w", encoding="utf-8", dir=path.parent, delete=False, suffix=".tmp") as handle:
        json.dump(data, handle, indent=2, sort_keys=True)
        tmp_path = Path(handle.name)
    tmp_path.replace(path)


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
