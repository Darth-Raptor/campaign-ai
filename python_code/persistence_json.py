"""Versioned local JSON snapshot persistence."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from . import config, state
from .schemas import ValidationError, from_sqf, sanitize_save_name


def _snapshot_path(campaign_id: str, save_name: str) -> Path:
    save_dir = config.get_save_dir()
    save_dir.mkdir(parents=True, exist_ok=True)
    file_name = f"{sanitize_save_name(campaign_id)}_{sanitize_save_name(save_name)}.json"
    return save_dir / file_name


def save_snapshot(payload: Any | None = None) -> dict[str, Any]:
    campaign = state.ensure_initialized()
    data = from_sqf(payload or {})
    if not isinstance(data, dict):
        data = {}
    campaign_id = str(data.get("campaignId", campaign.campaign_id) or campaign.campaign_id)
    save_name = str(data.get("saveName", "autosave") or "autosave")
    path = _snapshot_path(campaign_id, save_name)
    snapshot = state.export_state()
    tmp_path = path.with_suffix(path.suffix + ".tmp")
    with tmp_path.open("w", encoding="utf-8") as handle:
        json.dump(snapshot, handle, indent=2, sort_keys=True)
    tmp_path.replace(path)
    state.set_last_save_time(snapshot.get("savedAt"))
    return {
        "campaignId": campaign_id,
        "saveName": save_name,
        "path": str(path),
        "summary": state.get_state_summary(),
    }


def load_snapshot(payload: Any | None = None) -> dict[str, Any]:
    data = from_sqf(payload or {})
    if not isinstance(data, dict):
        data = {}
    campaign_id = str(data.get("campaignId", state.current().campaign_id) or state.current().campaign_id)
    save_name = str(data.get("saveName", "autosave") or "autosave")
    if not campaign_id:
        raise ValidationError("load_snapshot requires campaignId when no state is initialized")
    path = _snapshot_path(campaign_id, save_name)
    if not path.exists():
        raise ValidationError(f"Snapshot not found: {path}")
    with path.open("r", encoding="utf-8") as handle:
        snapshot = json.load(handle)
    if int(snapshot.get("schemaVersion", 0)) != config.SNAPSHOT_SCHEMA_VERSION:
        raise ValidationError("Snapshot schema version is not supported")
    summary = state.import_state(snapshot)
    return {
        "campaignId": campaign_id,
        "saveName": save_name,
        "path": str(path),
        "summary": summary,
    }

