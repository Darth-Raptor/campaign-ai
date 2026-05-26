"""Public Pythia API for Campaign AI Core."""

from __future__ import annotations

from typing import Any, Callable

from . import __version__, config, indexing, logging as cai_logging, schemas, world_model


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
    except Exception as exc:
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


def begin_map_index(payload: Any) -> list[Any]:
    return _call("OK", lambda: indexing.begin_map_index(payload), "Map index session prepared")


def add_map_index_batch(payload: Any) -> list[Any]:
    return _call("OK", lambda: indexing.add_map_index_batch(payload), "Map index batch accepted")


def finalize_map_index(payload: Any) -> list[Any]:
    return _call("OK", lambda: indexing.finalize_map_index(payload), "Map index finalized")


def get_map_index_debug_markers(payload: Any) -> list[Any]:
    return _call("OK", lambda: indexing.get_map_index_debug_markers(payload), "Map index debug markers returned")


def init_world_model(payload: Any) -> list[Any]:
    return _call("OK", lambda: world_model.init_world_model(payload), "Runtime world model initialized")


def get_world_model_summary() -> list[Any]:
    return _call("OK", world_model.get_world_model_summary, "Runtime world model summary returned")


def get_world_debug_markers(payload: Any | None = None) -> list[Any]:
    return _call("OK", lambda: world_model.get_world_debug_markers(payload), "Runtime world model debug markers returned")
