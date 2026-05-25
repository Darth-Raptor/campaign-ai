"""Weighted offscreen virtual combat resolution."""

from __future__ import annotations

import math
import random
from typing import Any

from . import config, state
from .schemas import ValidationError, as_bool, as_position, from_sqf, normalize_combat_payload


def resolve_combat_batch(payload: Any) -> dict[str, Any]:
    data = normalize_combat_payload(payload)
    campaign = state.ensure_initialized()
    engagements = data["engagements"]
    if data["autoDetect"]:
        engagements = engagements + _auto_detect_engagements()
    results = []
    skipped = []
    logs = []
    for raw in engagements:
        try:
            engagement = _normalize_engagement(raw)
        except ValidationError as exc:
            skipped.append(_skip_report(raw, str(exc)))
            logs.append(f"Skipped malformed engagement: {exc}")
            continue

        if engagement["playersNearby"]:
            skipped.append(_skip_report(engagement, "players nearby"))
            logs.append(
                "Skipped engagement "
                f"{engagement['attackerGroupId']} vs {engagement['defenderGroupId']} because SQF reported players nearby"
            )
            continue

        try:
            result = _resolve_single(engagement, data["randomness"], data["gameTime"])
        except ValidationError as exc:
            skipped.append(_skip_report(engagement, str(exc)))
            logs.append(
                "Skipped engagement "
                f"{engagement['attackerGroupId']} vs {engagement['defenderGroupId']}: {exc}"
            )
            continue

        results.append(result)
        campaign.combat_history.append(result)
    return {
        "gameTime": data["gameTime"],
        "results": results,
        "skipped": skipped,
        "logs": logs,
        "summary": state.get_state_summary(),
    }


def _normalize_engagement(raw: Any) -> dict[str, Any]:
    data = from_sqf(raw)
    if not isinstance(data, dict):
        raise ValidationError("Combat engagement must be a mapping or SQF key/value array")

    attacker_id = str(data.get("attackerGroupId", "")).strip()
    defender_id = str(data.get("defenderGroupId", "")).strip()
    if not attacker_id or not defender_id:
        raise ValidationError("Combat engagement requires attackerGroupId and defenderGroupId")
    if attacker_id == defender_id:
        raise ValidationError("Combat engagement attacker and defender must be different groups")

    return {
        "attackerGroupId": attacker_id,
        "defenderGroupId": defender_id,
        "objectiveId": str(data.get("objectiveId", "")).strip(),
        "position": _optional_position(data.get("position")),
        "playersNearby": as_bool(data.get("playersNearby", False)),
    }


def _optional_position(value: Any) -> list[float]:
    raw = from_sqf(value)
    if isinstance(raw, list) and len(raw) >= 2:
        return as_position(raw)
    return []


def _skip_report(raw: Any, reason: str) -> dict[str, Any]:
    data = from_sqf(raw)
    if not isinstance(data, dict):
        data = {}
    return {
        "attackerGroupId": str(data.get("attackerGroupId", "")),
        "defenderGroupId": str(data.get("defenderGroupId", "")),
        "objectiveId": str(data.get("objectiveId", "")),
        "reason": reason,
    }


def _auto_detect_engagements() -> list[dict[str, Any]]:
    campaign = state.ensure_initialized()
    groups = list(campaign.virtual_groups.values())
    engagements: list[dict[str, Any]] = []
    for index, attacker in enumerate(groups):
        if attacker.get("strength", 0) <= 0:
            continue
        for defender in groups[index + 1 :]:
            if defender.get("strength", 0) <= 0:
                continue
            if attacker.get("side") == defender.get("side"):
                continue
            if _distance_2d(attacker.get("position", [0, 0, 0]), defender.get("position", [0, 0, 0])) <= 500:
                engagements.append(
                    {
                        "attackerGroupId": attacker["groupId"],
                        "defenderGroupId": defender["groupId"],
                        "objectiveId": attacker.get("currentObjectiveId") or defender.get("currentObjectiveId", ""),
                        "position": _midpoint(
                            attacker.get("position", [0, 0, 0]),
                            defender.get("position", [0, 0, 0]),
                        ),
                        "playersNearby": False,
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
    if objective_id and not objective:
        raise ValidationError(f"Combat engagement references unknown objective: {objective_id}")

    position = engagement.get("position") or _engagement_position(attacker, defender, objective)

    attacker_power = _combat_power(attacker, "ATTACK", objective, randomness)
    defender_power = _combat_power(defender, "DEFEND", objective, randomness)
    ratio = attacker_power / max(0.01, defender_power)
    outcome = _outcome_for_ratio(ratio)
    losses = _losses_for_outcome(outcome)

    attacker_before = _group_update(attacker)
    defender_before = _group_update(defender)
    objective_before = _objective_update(objective) if objective else {}

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
        "position": position,
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
        "attackerBefore": attacker_before,
        "defenderBefore": defender_before,
        "objectiveBefore": objective_before,
        "groupUpdates": [_group_update(attacker), _group_update(defender)],
        "objectiveUpdate": _objective_update(objective) if objective else {},
        "generatedContactReports": [
            {
                "type": "COMBAT_RESOLVED",
                "objectiveId": objective_id,
                "position": position,
                "summary": f"{attacker_id} vs {defender_id}: {outcome}",
            }
        ],
        "combatReport": _combat_report(attacker_id, defender_id, objective_id, outcome, losses),
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


def _group_update(group: dict[str, Any]) -> dict[str, Any]:
    return {
        "groupId": str(group.get("groupId", "")),
        "side": str(group.get("side", "UNKNOWN")),
        "strength": int(max(0, round(float(group.get("strength", 0))))),
        "readiness": round(max(0, min(100, float(group.get("readiness", 100)))), 2),
        "morale": round(max(0, min(100, float(group.get("morale", 100)))), 2),
        "position": list(group.get("position", [0, 0, 0])),
        "currentObjectiveId": str(group.get("currentObjectiveId", "")),
        "status": str(group.get("status", "IDLE")),
    }


def _objective_update(objective: dict[str, Any] | None) -> dict[str, Any]:
    if not objective:
        return {}
    return {
        "objectiveId": str(objective.get("objectiveId", "")),
        "owner": str(objective.get("owner", "UNKNOWN")),
        "control": round(max(0, min(100, float(objective.get("control", 50)))), 2),
    }


def _engagement_position(
    attacker: dict[str, Any],
    defender: dict[str, Any],
    objective: dict[str, Any] | None,
) -> list[float]:
    if objective:
        return as_position(objective.get("position", [0, 0, 0]))
    return _midpoint(attacker.get("position", [0, 0, 0]), defender.get("position", [0, 0, 0]))


def _midpoint(a: list[Any], b: list[Any]) -> list[float]:
    a_pos = as_position(a)
    b_pos = as_position(b)
    return [
        (a_pos[0] + b_pos[0]) / 2.0,
        (a_pos[1] + b_pos[1]) / 2.0,
        (a_pos[2] + b_pos[2]) / 2.0,
    ]


def _combat_report(
    attacker_id: str,
    defender_id: str,
    objective_id: str,
    outcome: str,
    losses: dict[str, int],
) -> str:
    objective_text = objective_id or "open terrain"
    return (
        f"{attacker_id} vs {defender_id} at {objective_text}: {outcome}; "
        f"losses A/D {losses['attackerLossPercent']}%/{losses['defenderLossPercent']}%; "
        f"control delta {losses['objectiveControlDelta']}"
    )


def _reason(attacker: dict[str, Any], defender: dict[str, Any], objective: dict[str, Any] | None, outcome: str) -> str:
    terrain = objective.get("terrainType", "mixed") if objective else "open"
    return f"{outcome} based on strength, unit type, readiness, morale, posture, terrain {terrain}, and random friction"


def _distance_2d(a: list[Any], b: list[Any]) -> float:
    return math.hypot(float(a[0]) - float(b[0]), float(a[1]) - float(b[1]))
