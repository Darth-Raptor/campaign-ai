"""Virtual group movement and state helpers."""

from __future__ import annotations

import math
from typing import Any

from . import config, state


def update_virtual_positions(game_time: float) -> list[str]:
    campaign = state.ensure_initialized()
    logs: list[str] = []
    if campaign.last_update_time <= 0:
        campaign.last_update_time = game_time
        return logs
    dt = max(0.0, min(600.0, game_time - campaign.last_update_time))
    campaign.last_update_time = game_time
    if dt <= 0:
        return logs
    for group in campaign.virtual_groups.values():
        order = group.get("assignedOrder")
        if not isinstance(order, dict):
            continue
        target = order.get("targetPosition")
        if not isinstance(target, list) or len(target) < 2:
            target_objective_id = order.get("targetObjectiveId")
            objective = campaign.objectives.get(str(target_objective_id))
            if not objective:
                continue
            target = objective.get("position", [0, 0, 0])
        speed = config.MOBILITY_SPEED_MPS.get(str(group.get("mobility", "foot")).lower(), 1.2)
        if speed <= 0:
            continue
        old_position = list(group.get("position", [0, 0, 0]))
        new_position = _move_toward(old_position, target, speed * dt)
        group["position"] = new_position
        if _distance_2d(new_position, target) <= 5:
            group["currentObjectiveId"] = str(order.get("targetObjectiveId", group.get("currentObjectiveId", "")))
        logs.append(f"Moved {group.get('groupId')} toward {order.get('orderType', 'ORDER')}")
    return logs


def _move_toward(position: list[float], target: list[float], max_distance: float) -> list[float]:
    distance = _distance_2d(position, target)
    if distance <= max_distance or distance <= 0:
        return [float(target[0]), float(target[1]), float(target[2] if len(target) > 2 else 0)]
    ratio = max_distance / distance
    return [
        float(position[0]) + (float(target[0]) - float(position[0])) * ratio,
        float(position[1]) + (float(target[1]) - float(position[1])) * ratio,
        float(position[2] if len(position) > 2 else 0),
    ]


def _distance_2d(a: list[Any], b: list[Any]) -> float:
    return math.hypot(float(a[0]) - float(b[0]), float(a[1]) - float(b[1]))

