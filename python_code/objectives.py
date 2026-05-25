"""Objective scoring helpers."""

from __future__ import annotations

from typing import Any


def defensive_need(objective: dict[str, Any], friendly_groups: list[dict[str, Any]]) -> float:
    priority = float(objective.get("priority", 50))
    control = float(objective.get("control", 100))
    defenders = sum(1 for group in friendly_groups if group.get("currentObjectiveId") == objective.get("objectiveId"))
    underdefended_bonus = 35.0 if defenders == 0 else max(0.0, 15.0 - defenders * 5.0)
    contested_bonus = 25.0 if control < 85 else 0.0
    return priority + underdefended_bonus + contested_bonus


def attack_value(objective: dict[str, Any], commander: dict[str, Any]) -> float:
    priority = float(objective.get("priority", 50))
    aggression = float(commander.get("aggression", 50))
    control = float(objective.get("control", 50))
    foothold_bonus = 20.0 if 25 < control < 75 else 0.0
    return priority + aggression * 0.35 + foothold_bonus

