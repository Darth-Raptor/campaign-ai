"""Virtual group movement and state helpers."""

from __future__ import annotations

import math
from typing import Any

from . import config, state


def update_virtual_positions(game_time: float) -> list[str]:
    campaign = state.ensure_initialized()
    logs: list[str] = []
    if campaign.last_update_time <= 0:
        dt = max(0.0, min(600.0, game_time))
    else:
        dt = max(0.0, min(600.0, game_time - campaign.last_update_time))
    campaign.last_update_time = game_time
    if dt <= 0:
        return logs

    for group in campaign.virtual_groups.values():
        order = group.get("assignedOrder")
        if not isinstance(order, dict):
            group["movementState"] = "IDLE"
            continue

        if group.get("manualOverride") or group.get("strength", 0) <= 0:
            group["movementState"] = "HELD"
            continue

        expires_at = float(order.get("expiresAt", 0) or 0)
        if expires_at > 0 and expires_at < game_time:
            group["movementState"] = "ORDER_EXPIRED"
            continue

        target = _resolve_order_target(order, campaign.objectives)
        if target is None:
            group["movementState"] = "NO_TARGET"
            continue

        speed = config.MOBILITY_SPEED_MPS.get(str(group.get("mobility", "foot")).lower(), 1.2)
        if speed <= 0:
            group["movementState"] = "STATIC"
            continue

        old_position = list(group.get("position", [0, 0, 0]))
        new_position = _move_toward(old_position, target, speed * dt)
        distance_remaining = distance_2d(new_position, target)

        group["position"] = new_position
        group["targetPosition"] = list(target)
        group["targetObjectiveId"] = str(order.get("targetObjectiveId", ""))
        group["currentOrderType"] = str(order.get("orderType", "")).upper()
        group["distanceToTarget"] = round(distance_remaining, 2)
        group["lastMovementTime"] = game_time
        group["lastMovementDelta"] = round(dt, 2)
        group["speedMps"] = speed

        if distance_remaining <= 5:
            group["position"] = [float(target[0]), float(target[1]), float(target[2] if len(target) > 2 else 0)]
            group["movementState"] = "ARRIVED"
            target_objective_id = str(order.get("targetObjectiveId", ""))
            if target_objective_id:
                group["currentObjectiveId"] = target_objective_id
        else:
            group["movementState"] = "MOVING"

        logs.append(
            f"Moved {group.get('groupId')} toward {order.get('orderType', 'ORDER')} "
            f"for {dt:.1f}s; {distance_remaining:.1f}m remaining"
        )
    return logs


def _resolve_order_target(order: dict[str, Any], objectives: dict[str, dict[str, Any]]) -> list[float] | None:
    target = order.get("targetPosition")
    if isinstance(target, list) and len(target) >= 2:
        return [
            float(target[0]),
            float(target[1]),
            float(target[2] if len(target) > 2 else 0),
        ]

    target_objective_id = order.get("targetObjectiveId")
    objective = objectives.get(str(target_objective_id))
    if not objective:
        return None

    position = objective.get("position", [0, 0, 0])
    if not isinstance(position, list) or len(position) < 2:
        return None

    return [
        float(position[0]),
        float(position[1]),
        float(position[2] if len(position) > 2 else 0),
    ]


def _move_toward(position: list[float], target: list[float], max_distance: float) -> list[float]:
    distance = distance_2d(position, target)
    if distance <= max_distance or distance <= 0:
        return [float(target[0]), float(target[1]), float(target[2] if len(target) > 2 else 0)]
    ratio = max_distance / distance
    return [
        float(position[0]) + (float(target[0]) - float(position[0])) * ratio,
        float(position[1]) + (float(target[1]) - float(position[1])) * ratio,
        float(position[2] if len(position) > 2 else 0),
    ]


def distance_2d(a: list[Any], b: list[Any]) -> float:
    return math.hypot(float(a[0]) - float(b[0]), float(a[1]) - float(b[1]))


def _distance_2d(a: list[Any], b: list[Any]) -> float:
    return distance_2d(a, b)
