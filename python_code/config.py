"""Configuration constants for Campaign AI."""

from __future__ import annotations

import os
from pathlib import Path

PACKAGE_NAME = "CAIPython"
VERSION = "0.1.0"
SNAPSHOT_SCHEMA_VERSION = 1
DEFAULT_SAVE_FOLDER = "CampaignAI_Saves"

ALLOWED_ORDER_TYPES = {"DEFEND", "PATROL", "RESERVE", "ATTACK", "REINFORCE"}
ALLOWED_COMBAT_OUTCOMES = {
    "ATTACKER_DECISIVE_VICTORY",
    "ATTACKER_VICTORY",
    "ATTACKER_COSTLY_VICTORY",
    "ATTACKER_GAINED_GROUND",
    "STALEMATE",
    "DEFENDER_HOLD",
    "DEFENDER_SUCCESSFUL_DEFENSE",
    "ATTACKER_REPULSED",
    "ATTACKER_ROUTED",
    "DEFENDER_WITHDRAWAL",
    "BOTH_SIDES_BREAK_CONTACT",
}

MOBILITY_SPEED_MPS = {
    "foot": 1.2,
    "motorized": 6.0,
    "mechanized": 5.0,
    "armor": 4.0,
    "static": 0.0,
}

UNIT_TYPE_MODIFIERS = {
    "infantry": 1.0,
    "motorized": 1.15,
    "mechanized": 1.35,
    "armor": 1.6,
    "recon": 0.75,
    "static": 1.1,
}

RANDOMNESS_BANDS = {
    "NONE": (1.0, 1.0),
    "LOW": (0.90, 1.10),
    "NORMAL": (0.85, 1.15),
    "HIGH": (0.75, 1.25),
    "CHAOTIC": (0.65, 1.35),
}


def get_save_dir() -> Path:
    raw = os.environ.get("CAI_SAVE_DIR")
    base = Path(raw) if raw else Path.cwd() / DEFAULT_SAVE_FOLDER
    return base.resolve()
