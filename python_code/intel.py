"""Commander knowledge and observed event handling."""

from __future__ import annotations

from typing import Any

from . import state
from .schemas import from_sqf


def record_observed_events(commander_id: str, observed_events: Any, game_time: float) -> list[str]:
    campaign = state.ensure_initialized()
    knowledge = campaign.knowledge.setdefault(
        commander_id,
        {"commanderId": commander_id, "objectives": {}, "contacts": {}, "suspectedAreas": [], "lastUpdated": 0.0},
    )
    logs: list[str] = []
    events = from_sqf(observed_events)
    if not isinstance(events, list):
        return logs
    for event in events:
        if not isinstance(event, dict):
            continue
        event_type = str(event.get("eventType", "")).upper()
        if event_type == "CONTACT":
            contact_id = str(event.get("contactId", event.get("groupId", "")))
            if not contact_id:
                continue
            knowledge["contacts"][contact_id] = {
                "contactId": contact_id,
                "side": str(event.get("side", "UNKNOWN")).upper(),
                "position": event.get("position", [0, 0, 0]),
                "confidence": float(event.get("confidence", 0.75)),
                "lastSeen": game_time,
                "source": str(event.get("source", "observedEvent")),
            }
            logs.append(f"Recorded contact {contact_id} for {commander_id}")
        elif event_type == "OBJECTIVE_OWNER":
            objective_id = str(event.get("objectiveId", ""))
            if not objective_id:
                continue
            knowledge["objectives"][objective_id] = {
                "objectiveId": objective_id,
                "knownOwner": str(event.get("owner", "UNKNOWN")).upper(),
                "confidence": float(event.get("confidence", 0.75)),
                "lastUpdated": game_time,
                "source": str(event.get("source", "observedEvent")),
                "position": event.get("position", [0, 0, 0]),
                "priority": event.get("priority", 50),
            }
            logs.append(f"Updated objective knowledge {objective_id} for {commander_id}")
    knowledge["lastUpdated"] = game_time
    return logs


def decay_contacts(commander_id: str, game_time: float) -> None:
    campaign = state.ensure_initialized()
    knowledge = campaign.knowledge.get(commander_id)
    if not knowledge:
        return
    contacts = knowledge.get("contacts", {})
    for contact in contacts.values():
        age = max(0.0, game_time - float(contact.get("lastSeen", game_time)))
        contact["confidence"] = max(0.05, float(contact.get("confidence", 0.75)) - age / 7200.0)

