"""RPT-friendly Python log string helpers."""

from __future__ import annotations


def info(message: str) -> str:
    return f"[CAIPY] {message}"


def error(message: str) -> str:
    return f"[CAIPY ERROR] {message}"

