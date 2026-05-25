"""Python-owned Campaign AI state."""

from __future__ import annotations

from copy import deepcopy
from dataclasses import dataclass, field
from time import time
from typing import Any

from . import config
from .schemas import StateNotInitializedError


@dataclass
class CampaignState:
    initialized: bool = False
    campaign_id: str = ""
    world_name: str = ""
    mission_name: str = ""
    objectives: dict[str, dict[str, Any]] = field(default_factory=dict)
    commanders: dict[str, dict[str, Any]] = field(default_factory=dict)
    virtual_groups: dict[str, dict[str, Any]] = field(default_factory=dict)
    knowledge: dict[str, dict[str, Any]] = field(default_factory=dict)
    combat_history: list[dict[str, Any]] = field(default_factory=list)
    settings: dict[str, Any] = field(default_factory=dict)
    last_save_time: float = 0.0
    last_update_time: float = 0.0
    order_counter: int = 0
    engagement_counter: int = 0


_STATE = CampaignState()


def current() -> CampaignState:
    return _STATE


def ensure_initialized() -> CampaignState:
    if not _STATE.initialized:
        raise StateNotInitializedError("State is not initialized")
    return _STATE


def init_campaign(payload: dict[str, Any]) -> dict[str, Any]:
    global _STATE
    _STATE = CampaignState(
        initialized=True,
        campaign_id=payload["campaignId"],
        world_name=payload.get("worldName", ""),
        mission_name=payload.get("missionName", ""),
        objectives={item["objectiveId"]: deepcopy(item) for item in payload.get("objectives", [])},
        commanders={item["commanderId"]: deepcopy(item) for item in payload.get("commanders", [])},
        virtual_groups={item["groupId"]: deepcopy(item) for item in payload.get("virtualGroups", [])},
        settings=deepcopy(payload.get("settings", {})),
        last_update_time=0.0,
    )
    _STATE.knowledge = _build_initial_knowledge(_STATE)
    return get_state_summary()


def _build_initial_knowledge(campaign: CampaignState) -> dict[str, dict[str, Any]]:
    knowledge: dict[str, dict[str, Any]] = {}
    for commander_id, commander in campaign.commanders.items():
        objective_knowledge = {}
        for objective_id, objective in campaign.objectives.items():
            objective_knowledge[objective_id] = {
                "objectiveId": objective_id,
                "knownOwner": objective.get("owner", "UNKNOWN"),
                "confidence": 0.65,
                "lastUpdated": 0.0,
                "source": "initialBriefing",
                "position": list(objective.get("position", [0, 0, 0])),
                "priority": objective.get("priority", 50),
            }
        knowledge[commander_id] = {
            "commanderId": commander_id,
            "side": commander.get("side", "UNKNOWN"),
            "objectives": objective_knowledge,
            "contacts": {},
            "suspectedAreas": [],
            "lastUpdated": 0.0,
        }
    return knowledge


def get_state_summary() -> dict[str, Any]:
    campaign = current()
    groups = list(campaign.virtual_groups.values())
    commanders = list(campaign.commanders.values())
    objectives = list(campaign.objectives.values())
    return {
        "package": config.PACKAGE_NAME,
        "version": config.VERSION,
        "initialized": campaign.initialized,
        "campaignId": campaign.campaign_id,
        "worldName": campaign.world_name,
        "missionName": campaign.mission_name,
        "objectiveCount": len(objectives),
        "commanderCount": len(commanders),
        "virtualGroupCount": len(groups),
        "combatHistoryCount": len(campaign.combat_history),
        "lastSaveTime": campaign.last_save_time,
        "systemsEnabled": campaign.initialized,
        "featureFlags": {
            "backendEnabled": False,
            "sqliteEnabled": False,
            "clientPythonEnabled": False,
            "liveSpawnLifecycleEnabled": False,
        },
    }


def next_order_id() -> str:
    campaign = ensure_initialized()
    campaign.order_counter += 1
    return f"ord_{campaign.order_counter:04d}"


def next_engagement_id() -> str:
    campaign = ensure_initialized()
    campaign.engagement_counter += 1
    return f"eng_{campaign.engagement_counter:04d}"


def set_last_save_time(value: float | None = None) -> None:
    ensure_initialized().last_save_time = float(value if value is not None else time())


def export_state() -> dict[str, Any]:
    campaign = ensure_initialized()
    return {
        "schemaVersion": config.SNAPSHOT_SCHEMA_VERSION,
        "savedAt": time(),
        "campaign": {
            "initialized": campaign.initialized,
            "campaignId": campaign.campaign_id,
            "worldName": campaign.world_name,
            "missionName": campaign.mission_name,
            "objectives": deepcopy(campaign.objectives),
            "commanders": deepcopy(campaign.commanders),
            "virtualGroups": deepcopy(campaign.virtual_groups),
            "knowledge": deepcopy(campaign.knowledge),
            "combatHistory": deepcopy(campaign.combat_history),
            "settings": deepcopy(campaign.settings),
            "lastSaveTime": campaign.last_save_time,
            "lastUpdateTime": campaign.last_update_time,
            "orderCounter": campaign.order_counter,
            "engagementCounter": campaign.engagement_counter,
        },
    }


def import_state(snapshot: dict[str, Any]) -> dict[str, Any]:
    global _STATE
    campaign_data = snapshot.get("campaign")
    if not isinstance(campaign_data, dict):
        raise StateNotInitializedError("Snapshot does not contain campaign data")
    _STATE = CampaignState(
        initialized=bool(campaign_data.get("initialized", True)),
        campaign_id=str(campaign_data.get("campaignId", "")),
        world_name=str(campaign_data.get("worldName", "")),
        mission_name=str(campaign_data.get("missionName", "")),
        objectives=deepcopy(campaign_data.get("objectives", {})),
        commanders=deepcopy(campaign_data.get("commanders", {})),
        virtual_groups=deepcopy(campaign_data.get("virtualGroups", {})),
        knowledge=deepcopy(campaign_data.get("knowledge", {})),
        combat_history=deepcopy(campaign_data.get("combatHistory", [])),
        settings=deepcopy(campaign_data.get("settings", {})),
        last_save_time=float(campaign_data.get("lastSaveTime", 0.0) or 0.0),
        last_update_time=float(campaign_data.get("lastUpdateTime", 0.0) or 0.0),
        order_counter=int(campaign_data.get("orderCounter", 0) or 0),
        engagement_counter=int(campaign_data.get("engagementCounter", 0) or 0),
    )
    return get_state_summary()


def get_debug_snapshot(payload: dict[str, Any]) -> dict[str, Any]:
    campaign = ensure_initialized()
    mode = payload.get("debugMode", "BOTH")
    commander_id = payload.get("commanderId", "")
    knowledge = []
    if mode in {"BOTH", "COMMANDER_KNOWLEDGE"}:
        if commander_id:
            item = campaign.knowledge.get(commander_id)
            if item:
                knowledge.append(deepcopy(item))
        else:
            knowledge = [deepcopy(item) for item in campaign.knowledge.values()]
    return {
        "campaignId": campaign.campaign_id,
        "gameTime": payload.get("gameTime", 0),
        "debugMode": mode,
        "objectives": [deepcopy(item) for item in campaign.objectives.values()],
        "groups": [deepcopy(item) for item in campaign.virtual_groups.values()],
        "commanders": [deepcopy(item) for item in campaign.commanders.values()],
        "knowledge": knowledge,
        "combatHistory": deepcopy(campaign.combat_history[-20:]),
        "summary": get_state_summary(),
    }

