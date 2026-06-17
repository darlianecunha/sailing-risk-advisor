"""Data collection from the Open-Meteo public APIs.

Open-Meteo is a free, third-party weather service (no API key required). This
module only *consumes* it; it does not implement any forecasting itself.

Two endpoints are used:
  * Weather forecast  -> wind, gusts, precipitation, visibility
  * Marine forecast   -> significant wave height, wave period

Hourly values are aggregated into daily extremes, which feed the risk engine.
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


def _day(ts: str) -> str:
    """Extract the YYYY-MM-DD date part from an ISO timestamp."""
    return ts[:10]


def daily_summary() -> list[dict]:
    """Combine both forecasts into one record per day with daily extremes.

    Returns a list of dicts sorted by date, each containing the worst-case
    value of the day for every monitored variable.
    """
    weather = fetch_weather()["hourly"]
    marine = fetch_marine()["hourly"]

    # Group hourly values per calendar day.
    per_day: dict[str, dict] = defaultdict(lambda: defaultdict(list))

    for i, ts in enumerate(weather["time"]):
        d = _day(ts)
        per_day[d]["wind_speed"].append(weather["wind_speed_10m"][i])
        per_day[d]["wind_gusts"].append(weather["wind_gusts_10m"][i])
        per_day[d]["precip"].append(weather["precipitation"][i])
        # Open-Meteo returns visibility in metres; convert to km.
        vis = weather["visibility"][i]
        per_day[d]["visibility"].append(vis / 1000.0 if vis is not None else None)

    for i, ts in enumerate(marine["time"]):
        d = _day(ts)
        per_day[d]["wave"].append(marine["wave_height"][i])

    def _max(values):
        clean = [v for v in values if v is not None]
        return max(clean) if clean else None

    def _min(values):
        clean = [v for v in values if v is not None]
        return min(clean) if clean else None

    summary = []
    for d in sorted(per_day):
        rec = per_day[d]
        summary.append(
            {
                "date": d,
                "weekday": dt.date.fromisoformat(d).strftime("%a"),
                "wind_speed_kmh": _max(rec["wind_speed"]),
                "wind_gusts_kmh": _max(rec["wind_gusts"]),
                "wave_height_m": _max(rec["wave"]),
                "precipitation_mm": sum(v for v in rec["precip"] if v is not None),
                "visibility_km": _min(rec["visibility"]),
            }
        )
    return summary


if __name__ == "__main__":
    for row in daily_summary():
        print(row)
