"""Public Pythia API for Campaign AI."""

from __future__ import annotations

from typing import Any, Callable

from . import __version__, combat, commanders, config, logging as cai_logging, persistence_json, schemas, state


def _envelope(success: bool, status_code: str, payload: Any, logs: list[str] | None = None) -> list[Any]:
    return [success, status_code, schemas.to_sqf(payload), logs or []]


def _call(status_code: str, callback: Callable[[], Any], success_log: str) -> list[Any]:
    logs: list[str] = []
    try:
        payload = callback()
        logs.append(cai_logging.info(success_log))
        return _envelope(True, status_code, payload, logs)
    except schemas.CAIError as exc:
        logs.append(cai_logging.error(str(exc)))
        return _envelope(False, exc.status_code, [], logs)
    except Exception as exc:  # Pythia must never receive an uncaught Python exception.
        logs.append(cai_logging.error(f"Unhandled exception: {exc}"))
        return _envelope(False, "PY_UNHANDLED_EXCEPTION", [], logs)


def ping() -> list[Any]:
    return _envelope(
        True,
        "OK",
        {
            "package": config.PACKAGE_NAME,
            "version": __version__,
            "systemsEnabled": True,
        },
        [cai_logging.info("Ping successful")],
    )


def init_state(payload: Any) -> list[Any]:
    return _call(
        "OK",
        lambda: state.init_campaign(schemas.normalize_init_payload(payload)),
        "State initialized",
    )


def get_state_summary() -> list[Any]:
    return _call("OK", state.get_state_summary, "State summary returned")


def save_snapshot(payload: Any | None = None) -> list[Any]:
    return _call("OK", lambda: persistence_json.save_snapshot(payload), "Snapshot saved")


def load_snapshot(payload: Any | None = None) -> list[Any]:
    return _call("OK", lambda: persistence_json.load_snapshot(payload), "Snapshot loaded")


def get_debug_snapshot(payload: Any | None = None) -> list[Any]:
    return _call(
        "OK",
        lambda: state.get_debug_snapshot(schemas.normalize_debug_payload(payload)),
        "Debug snapshot returned",
    )


def commander_cycle(payload: Any) -> list[Any]:
    return _call("OK", lambda: commanders.commander_cycle(payload), "Commander cycle completed")


def resolve_combat_batch(payload: Any) -> list[Any]:
    return _call("OK", lambda: combat.resolve_combat_batch(payload), "Combat batch resolved")

