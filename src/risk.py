"""Risk engine: turn daily weather extremes into a go/no-go traffic light.

Each variable is compared against the amber and red thresholds in config.py.
The day's overall level is the worst level triggered by any variable, and the
engine records a plain-language reason for every flag so the output is
explainable rather than a black box.
"""

from __future__ import annotations

import config


def _level_for(variable: str, value: float | None) -> tuple[str, str | None]:
    """Return (level, reason) for a single variable value."""
    if value is None:
        return "GREEN", None

    limits = config.THRESHOLDS[variable]

    # Visibility is inverted: lower values are worse.
    if variable == "visibility_km":
        if value <= limits["red"]:
            return "RED", f"Visibilidade {value:.1f} km (neblina, abaixo de {limits['red']} km)"
        if value <= limits["amber"]:
            return "AMBER", f"Visibilidade {value:.1f} km (atenção, abaixo de {limits['amber']} km)"
        return "GREEN", None

    if value >= limits["red"]:
        return "RED", f"{_name(variable)} {value:.1f} {_unit(variable)} (acima de {limits['red']})"
    if value >= limits["amber"]:
        return "AMBER", f"{_name(variable)} {value:.1f} {_unit(variable)} (acima de {limits['amber']})"
    return "GREEN", None


def _name(variable: str) -> str:
    return {
        "wind_gusts_kmh": "Rajadas",
        "wind_speed_kmh": "Vento",
        "wave_height_m": "Onda",
        "precipitation_mm": "Chuva",
        "visibility_km": "Visibilidade",
    }[variable]


def _unit(variable: str) -> str:
    return {
        "wind_gusts_kmh": "km/h",
        "wind_speed_kmh": "km/h",
        "wave_height_m": "m",
        "precipitation_mm": "mm",
        "visibility_km": "km",
    }[variable]


def assess_day(day: dict) -> dict:
    """Add an overall risk level and list of reasons to a daily record."""
    reasons: list[str] = []
    worst = "GREEN"

    for variable in config.THRESHOLDS:
        level, reason = _level_for(variable, day.get(variable))
        if reason:
            reasons.append(reason)
        if config.LEVELS[level]["rank"] > config.LEVELS[worst]["rank"]:
            worst = level

    result = dict(day)
    result["level"] = worst
    result["label"] = config.LEVELS[worst]["label"]
    result["emoji"] = config.LEVELS[worst]["emoji"]
    result["reasons"] = reasons or ["Condições dentro dos limites seguros"]
    return result


def assess(days: list[dict]) -> list[dict]:
    """Assess a list of daily records."""
    return [assess_day(d) for d in days]
