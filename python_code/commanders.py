"""Predictable V1 conventional commander logic."""

from __future__ import annotations

import math
from typing import Any

from . import config, intel, objectives, state, virtual_groups
from .schemas import ValidationError, normalize_commander_cycle_payload


def commander_cycle(payload: Any) -> dict[str, Any]:
    data = normalize_commander_cycle_payload(payload)
    campaign = state.ensure_initialized()
    commander_id = data["commanderId"]
    commander = campaign.commanders.get(commander_id)
    if not commander:
        raise ValidationError(f"Unknown commander: {commander_id}")
    if commander.get("paused"):
        return {
            "commanderId": commander_id,
            "cycleTime": data["gameTime"],
            "orders": [],
            "debugReasoning": [f"Commander {commander_id} is paused"],
            "summary": state.get_state_summary(),
        }

    logs = intel.record_observed_events(commander_id, data["observedEvents"], data["gameTime"])
    intel.decay_contacts(commander_id, data["gameTime"])
    logs.extend(virtual_groups.update_virtual_positions(data["gameTime"]))

    side = commander.get("side", "UNKNOWN")
    groups = [
        group
        for group in campaign.virtual_groups.values()
        if group.get("commanderId") == commander_id and group.get("side") == side and not group.get("manualOverride")
    ]
    idle_groups = [group for group in groups if _is_available(group)]
    reasoning = [f"Commander {commander_id} evaluating {len(groups)} controlled groups"]
    orders: list[dict[str, Any]] = []

    if not groups:
        reasoning.append("No controlled groups available")
        return _result(commander_id, data["gameTime"], orders, reasoning + logs)

    friendly_objectives, enemy_objectives = _knowledge_objectives(commander_id, side)

    for objective in sorted(friendly_objectives, key=lambda item: objectives.defensive_need(item, groups), reverse=True):
        if not idle_groups:
            break
        defenders = _groups_assigned_to_objective(groups, objective["objectiveId"], {"DEFEND", "REINFORCE", "RESERVE"})
        if defenders:
            continue
        group = idle_groups.pop(0)
        orders.append(
            _assign_order(
                group,
                "DEFEND",
                objective,
                data["gameTime"],
                int(objective.get("priority", 50)),
                "High-priority friendly objective underdefended",
            )
        )
        reasoning.append(f"Assigned {group['groupId']} to defend {objective['objectiveId']}")

    reserve_target = _reserve_target(commander, friendly_objectives)
    needed_reserves = math.ceil(len(groups) * float(commander.get("reservePercentage", 20)) / 100.0)
    current_reserves = len([group for group in groups if _order_type(group) == "RESERVE"])
    while idle_groups and current_reserves < needed_reserves:
        group = idle_groups.pop(0)
        orders.append(
            _assign_order(
                group,
                "RESERVE",
                reserve_target,
                data["gameTime"],
                40,
                "Reserve percentage below commander setting",
            )
        )
        current_reserves += 1
        reasoning.append(f"Assigned {group['groupId']} to reserve")

    if idle_groups and enemy_objectives:
        attack_target = max(enemy_objectives, key=lambda item: objectives.attack_value(item, commander))
        attack_group = idle_groups.pop(0)
        orders.append(
            _assign_order(
                attack_group,
                "ATTACK",
                attack_target,
                data["gameTime"],
                int(objectives.attack_value(attack_target, commander)),
                "Known enemy objective has favorable priority/aggression score",
            )
        )
        reasoning.append(f"Assigned {attack_group['groupId']} to attack {attack_target['objectiveId']}")

    patrol_target = reserve_target
    while idle_groups:
        group = idle_groups.pop(0)
        orders.append(
            _assign_order(
                group,
                "PATROL",
                patrol_target,
                data["gameTime"],
                25,
                "No higher-priority task available",
            )
        )
        reasoning.append(f"Assigned {group['groupId']} to patrol")

    return _result(commander_id, data["gameTime"], orders, reasoning + logs)


def _result(commander_id: str, game_time: float, orders: list[dict[str, Any]], reasoning: list[str]) -> dict[str, Any]:
    return {
        "commanderId": commander_id,
        "cycleTime": game_time,
        "orders": orders,
        "debugReasoning": reasoning,
        "summary": state.get_state_summary(),
    }


def _knowledge_objectives(commander_id: str, side: str) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    campaign = state.ensure_initialized()
    knowledge = campaign.knowledge.get(commander_id, {}).get("objectives", {})
    friendly: list[dict[str, Any]] = []
    enemy: list[dict[str, Any]] = []
    for objective_id, known in knowledge.items():
        objective = campaign.objectives.get(objective_id)
        if not objective:
            continue
        known_owner = str(known.get("knownOwner", "UNKNOWN")).upper()
        if known_owner == side:
            friendly.append(objective)
        elif known_owner != "UNKNOWN":
            enemy.append(objective)
    return friendly, enemy


def _is_available(group: dict[str, Any]) -> bool:
    if group.get("strength", 0) <= 0:
        return False
    order = group.get("assignedOrder")
    if not isinstance(order, dict) or not order:
        return True
    return str(order.get("orderType", "")).upper() in {"", "PATROL", "RESERVE"}


def _order_type(group: dict[str, Any]) -> str:
    order = group.get("assignedOrder")
    if isinstance(order, dict):
        return str(order.get("orderType", "")).upper()
    return ""


def _groups_assigned_to_objective(groups: list[dict[str, Any]], objective_id: str, order_types: set[str]) -> list[dict[str, Any]]:
    assigned = []
    for group in groups:
        order = group.get("assignedOrder")
        if not isinstance(order, dict):
            continue
        if order.get("targetObjectiveId") == objective_id and str(order.get("orderType", "")).upper() in order_types:
            assigned.append(group)
    return assigned


def _reserve_target(commander: dict[str, Any], friendly_objectives: list[dict[str, Any]]) -> dict[str, Any]:
    if friendly_objectives:
        return max(friendly_objectives, key=lambda item: item.get("priority", 0))
    return {
        "objectiveId": "",
        "name": "HQ",
        "position": commander.get("hqPosition", [0, 0, 0]),
        "priority": 0,
    }


def _assign_order(
    group: dict[str, Any],
    order_type: str,
    objective: dict[str, Any],
    game_time: float,
    priority: int,
    reason: str,
) -> dict[str, Any]:
    order = {
        "orderId": state.next_order_id(),
        "groupId": group["groupId"],
        "orderType": order_type,
        "targetObjectiveId": objective.get("objectiveId", ""),
        "targetPosition": list(objective.get("position", [0, 0, 0])),
        "priority": max(0, min(100, int(priority))),
        "reason": reason,
        "expiresAt": game_time + 300,
    }
    group["assignedOrder"] = order
    group["status"] = order_type
    group["targetObjectiveId"] = str(objective.get("objectiveId", ""))
    group["targetPosition"] = list(objective.get("position", [0, 0, 0]))
    group["currentOrderType"] = order_type
    group["distanceToTarget"] = round(
        virtual_groups.distance_2d(list(group.get("position", [0, 0, 0])), order["targetPosition"]),
        2,
    )
    group["movementState"] = "ARRIVED" if group["distanceToTarget"] <= 5 else "MOVING"
    return order
