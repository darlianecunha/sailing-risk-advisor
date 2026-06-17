"""Configuration: location and safety thresholds.

Thresholds are an initial, conservative baseline for small-vessel navigation in
São Marcos Bay, which is more sensitive to weather than large commercial
shipping. They are loosely informed by the ANTAQ critical-threshold report for
Brazilian ports. Adjust them to the operating limits of the vessel in use.
"""

# --- Location: São Luís (MA), Baía de São Marcos ---------------------------
# Weather point: over the city/port area.
WEATHER_LAT = -2.53
WEATHER_LON = -44.30

# Marine point: slightly offshore in the bay, where wave data is meaningful.
MARINE_LAT = -2.45
MARINE_LON = -44.35

TIMEZONE = "America/Fortaleza"  # São Luís local time (UTC-3, no DST)
FORECAST_DAYS = 7

# --- Safety thresholds ------------------------------------------------------
# A day is flagged RED if any "red" limit is exceeded, AMBER if any "amber"
# limit is reached, otherwise GREEN. Values are daily extremes.
THRESHOLDS = {
    "wind_gusts_kmh": {"amber": 35.0, "red": 50.0},      # wind gusts at 10 m
    "wind_speed_kmh": {"amber": 28.0, "red": 40.0},      # sustained wind at 10 m
    "wave_height_m": {"amber": 1.5, "red": 2.5},         # significant wave height
    "precipitation_mm": {"amber": 20.0, "red": 50.0},    # daily rainfall total
    "visibility_km": {"amber": 5.0, "red": 2.0},         # lower is worse (fog)
}

# Labels and colours for the three risk levels.
LEVELS = {
    "GREEN": {"label": "Pode sair", "emoji": "🟢", "rank": 0},
    "AMBER": {"label": "Atenção", "emoji": "🟡", "rank": 1},
    "RED": {"label": "Não sair", "emoji": "🔴", "rank": 2},
}
