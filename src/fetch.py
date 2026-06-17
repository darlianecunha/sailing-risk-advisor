"""Data collection from the Open-Meteo public APIs.

Open-Meteo is a free, third-party weather service (no API key required). This
module only *consumes* it; it does not implement any forecasting itself.

Two endpoints are used:
  * Weather forecast  -> wind, gusts, precipitation, visibility
  * Marine forecast   -> significant wave height, wave period

Hourly values are aggregated into per-period extremes (manhã / tarde / noite,
defined in config.PERIODS), which feed the risk engine.
"""

from __future__ import annotations

import datetime as dt
import json
import urllib.parse
import urllib.request
from collections import defaultdict

import config

WEATHER_URL = "https://api.open-meteo.com/v1/forecast"
MARINE_URL = "https://marine-api.open-meteo.com/v1/marine"


def _get(url: str, params: dict) -> dict:
    """Perform a GET request and return parsed JSON."""
    query = urllib.parse.urlencode(params)
    with urllib.request.urlopen(f"{url}?{query}", timeout=30) as resp:
        return json.load(resp)


def fetch_weather() -> dict:
    """Return hourly weather forecast for the São Luís land/port point."""
    return _get(
        WEATHER_URL,
        {
            "latitude": config.WEATHER_LAT,
            "longitude": config.WEATHER_LON,
            "hourly": "wind_speed_10m,wind_gusts_10m,precipitation,visibility",
            "wind_speed_unit": "kmh",
            "timezone": config.TIMEZONE,
            "forecast_days": config.FORECAST_DAYS,
        },
    )


def fetch_marine() -> dict:
    """Return hourly marine forecast for the offshore point in the bay."""
    return _get(
        MARINE_URL,
        {
            "latitude": config.MARINE_LAT,
            "longitude": config.MARINE_LON,
            "hourly": "wave_height,wave_period",
            "timezone": config.TIMEZONE,
            "forecast_days": config.FORECAST_DAYS,
        },
    )


def _hour_to_period(hour: int) -> str | None:
    """Map an hour (0–23) to a period key, or None if unused."""
    for period in config.PERIODS:
        if hour in period["hours"]:
            return period["key"]
    return None


def period_summary() -> list[dict]:
    """Combine both forecasts into one record per (day, period).

    Returns a list of dicts sorted by date and period order, each holding the
    worst-case value of that period for every monitored variable.
    """
    weather = fetch_weather()["hourly"]
    marine = fetch_marine()["hourly"]

    # Group hourly values per (date, period).
    buckets: dict[tuple, dict] = defaultdict(lambda: defaultdict(list))

    def _add(ts: str, key: str, value):
        date = ts[:10]
        hour = int(ts[11:13])
        period = _hour_to_period(hour)
        if period is None:
            return
        buckets[(date, period)][key].append(value)

    for i, ts in enumerate(weather["time"]):
        _add(ts, "wind_speed", weather["wind_speed_10m"][i])
        _add(ts, "wind_gusts", weather["wind_gusts_10m"][i])
        _add(ts, "precip", weather["precipitation"][i])
        vis = weather["visibility"][i]
        _add(ts, "visibility", vis / 1000.0 if vis is not None else None)

    for i, ts in enumerate(marine["time"]):
        _add(ts, "wave", marine["wave_height"][i])

    def _max(values):
        clean = [v for v in values if v is not None]
        return max(clean) if clean else None

    def _min(values):
        clean = [v for v in values if v is not None]
        return min(clean) if clean else None

    order = {p["key"]: i for i, p in enumerate(config.PERIODS)}
    labels = {p["key"]: p["label"] for p in config.PERIODS}

    summary = []
    for (date, period) in sorted(buckets, key=lambda k: (k[0], order[k[1]])):
        rec = buckets[(date, period)]
        summary.append(
            {
                "date": date,
                "weekday": dt.date.fromisoformat(date).strftime("%a"),
                "period": period,
                "period_label": labels[period],
                "wind_speed_kmh": _max(rec["wind_speed"]),
                "wind_gusts_kmh": _max(rec["wind_gusts"]),
                "wave_height_m": _max(rec["wave"]),
                "precipitation_mm": sum(v for v in rec["precip"] if v is not None),
                "visibility_km": _min(rec["visibility"]),
            }
        )
    return summary


if __name__ == "__main__":
    for row in period_summary():
        print(row)
