"""Weighted offscreen virtual combat resolution."""

from __future__ import annotations

import math
import random
from typing import Any

from . import config, state
from .schemas import ValidationError, from_sqf, normalize_combat_payload


def resolve_combat_batch(payload: Any) -> dict[str, Any]:
    data = normalize_combat_payload(payload)
    campaign = state.ensure_initialized()
    engagements = data["engagements"]
    if data["autoDetect"]:
        engagements = engagements + _auto_detect_engagements()
    results = []
    logs = []
    for raw in engagements:
        engagement = from_sqf(raw)
        if not isinstance(engagement, dict):
            continue
        if bool(engagement.get("playersNearby", False)):
            logs.append("Skipped engagement because SQF reported players nearby")
            continue
        result = _resolve_single(engagement, data["randomness"], data["gameTime"])
        results.append(result)
        campaign.combat_history.append(result)
    return {
        "gameTime": data["gameTime"],
        "results": results,
        "logs": logs,
        "summary": state.get_state_summary(),
    }


def _auto_detect_engagements() -> list[dict[str, Any]]:
    campaign = state.ensure_initialized()
    groups = list(campaign.virtual_groups.values())
    engagements: list[dict[str, Any]] = []
    for attacker in groups:
        if attacker.get("strength", 0) <= 0:
            continue
        for defender in groups:
            if attacker is defender or defender.get("strength", 0) <= 0:
                continue
            if attacker.get("side") == defender.get("side"):
                continue
            if _distance_2d(attacker.get("position", [0, 0, 0]), defender.get("position", [0, 0, 0])) <= 500:
                engagements.append(
                    {
                        "attackerGroupId": attacker["groupId"],
                        "defenderGroupId": defender["groupId"],
                        "objectiveId": attacker.get("currentObjectiveId") or defender.get("currentObjectiveId", ""),
                    }
                )
                break
    return engagements


def _resolve_single(engagement: dict[str, Any], randomness: str, game_time: float) -> dict[str, Any]:
    campaign = state.ensure_initialized()
    attacker_id = str(engagement.get("attackerGroupId", ""))
    defender_id = str(engagement.get("defenderGroupId", ""))
    attacker = campaign.virtual_groups.get(attacker_id)
    defender = campaign.virtual_groups.get(defender_id)
    if not attacker or not defender:
        raise ValidationError("Combat engagement references unknown groups")
    if attacker.get("side") == defender.get("side"):
        raise ValidationError("Combat engagement groups are on the same side")

    objective_id = str(engagement.get("objectiveId", ""))
    objective = campaign.objectives.get(objective_id) if objective_id else None

    attacker_power = _combat_power(attacker, "ATTACK", objective, randomness)
    defender_power = _combat_power(defender, "DEFEND", objective, randomness)
    ratio = attacker_power / max(0.01, defender_power)
    outcome = _outcome_for_ratio(ratio)
    losses = _losses_for_outcome(outcome)

    _apply_group_damage(attacker, losses["attackerLossPercent"], losses["attackerReadinessDelta"], losses["attackerMoraleDelta"])
    _apply_group_damage(defender, losses["defenderLossPercent"], losses["defenderReadinessDelta"], losses["defenderMoraleDelta"])
    if objective:
        objective["control"] = max(0, min(100, float(objective.get("control", 50)) + losses["objectiveControlDelta"]))
        if objective["control"] >= 90:
            objective["owner"] = attacker.get("side", objective.get("owner", "UNKNOWN"))
        elif objective["control"] <= 10:
            objective["owner"] = defender.get("side", objective.get("owner", "UNKNOWN"))

    return {
        "engagementId": state.next_engagement_id(),
        "gameTime": game_time,
        "objectiveId": objective_id,
        "attackerGroupId": attacker_id,
        "defenderGroupId": defender_id,
        "attackerPower": round(attacker_power, 2),
        "defenderPower": round(defender_power, 2),
        "ratio": round(ratio, 2),
        "outcome": outcome,
        "attackerLossPercent": losses["attackerLossPercent"],
        "defenderLossPercent": losses["defenderLossPercent"],
        "attackerReadinessDelta": losses["attackerReadinessDelta"],
        "defenderReadinessDelta": losses["defenderReadinessDelta"],
        "attackerMoraleDelta": losses["attackerMoraleDelta"],
        "defenderMoraleDelta": losses["defenderMoraleDelta"],
        "objectiveControlDelta": losses["objectiveControlDelta"],
        "generatedContactReports": [],
        "reason": _reason(attacker, defender, objective, outcome),
    }


def _combat_power(group: dict[str, Any], posture: str, objective: dict[str, Any] | None, randomness: str) -> float:
    strength = max(0.0, float(group.get("strength", 0)))
    unit_modifier = config.UNIT_TYPE_MODIFIERS.get(str(group.get("unitType", "infantry")).lower(), 1.0)
    readiness = max(0.1, float(group.get("readiness", 100)) / 100.0)
    morale = max(0.1, float(group.get("morale", 100)) / 100.0)
    posture_modifier = 1.15 if posture == "DEFEND" else 1.0
    terrain_modifier = 1.0
    if objective and str(objective.get("terrainType", "")).lower() in {"urban", "forest", "mountain"} and posture == "DEFEND":
        terrain_modifier = 1.2
    low, high = config.RANDOMNESS_BANDS.get(randomness, config.RANDOMNESS_BANDS["NORMAL"])
    friction = random.uniform(low, high)
    return strength * unit_modifier * readiness * morale * posture_modifier * terrain_modifier * friction


def _outcome_for_ratio(ratio: float) -> str:
    if ratio >= 3.0:
        return "ATTACKER_DECISIVE_VICTORY"
    if ratio >= 2.0:
        return "ATTACKER_VICTORY"
    if ratio >= 1.25:
        return "ATTACKER_COSTLY_VICTORY"
    if ratio >= 0.8:
        return "STALEMATE"
    if ratio >= 0.5:
        return "ATTACKER_REPULSED"
    return "ATTACKER_ROUTED"


def _losses_for_outcome(outcome: str) -> dict[str, int]:
    table = {
        "ATTACKER_DECISIVE_VICTORY": (8, 35, -8, -35, 10, -25, 70),
        "ATTACKER_VICTORY": (12, 25, -12, -25, 5, -15, 45),
        "ATTACKER_COSTLY_VICTORY": (20, 22, -20, -20, -8, -10, 25),
        "STALEMATE": (15, 15, -15, -15, -5, -5, 0),
        "ATTACKER_REPULSED": (25, 8, -30, -10, -20, 5, -35),
        "ATTACKER_ROUTED": (40, 5, -45, -5, -35, 10, -60),
    }
    attacker_loss, defender_loss, attacker_ready, defender_ready, attacker_morale, defender_morale, control = table[outcome]
    return {
        "attackerLossPercent": attacker_loss,
        "defenderLossPercent": defender_loss,
        "attackerReadinessDelta": attacker_ready,
        "defenderReadinessDelta": defender_ready,
        "attackerMoraleDelta": attacker_morale,
        "defenderMoraleDelta": defender_morale,
        "objectiveControlDelta": control,
    }


def _apply_group_damage(group: dict[str, Any], loss_percent: int, readiness_delta: int, morale_delta: int) -> None:
    group["strength"] = int(max(0, round(float(group.get("strength", 0)) * (1.0 - loss_percent / 100.0))))
    group["readiness"] = max(0, min(100, float(group.get("readiness", 100)) + readiness_delta))
    group["morale"] = max(0, min(100, float(group.get("morale", 100)) + morale_delta))


def _reason(attacker: dict[str, Any], defender: dict[str, Any], objective: dict[str, Any] | None, outcome: str) -> str:
    terrain = objective.get("terrainType", "mixed") if objective else "open"
    return f"{outcome} based on strength, unit type, readiness, morale, posture, terrain {terrain}, and random friction"


def _distance_2d(a: list[Any], b: list[Any]) -> float:
    return math.hypot(float(a[0]) - float(b[0]), float(a[1]) - float(b[1]))

