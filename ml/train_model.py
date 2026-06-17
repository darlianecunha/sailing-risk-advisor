"""Optional ML module: learn a daily risk classifier from historical data.

This is a *practice* extension to the rule-based engine. It:

  1. Downloads ~3 years of historical hourly weather for São Luís from the
     Open-Meteo Archive API (free, no key).
  2. Aggregates it into daily features (max wind, max gusts, total rain, etc.).
  3. Creates a binary label "risky day" using the same safety thresholds.
  4. Trains a RandomForest classifier and reports accuracy + feature importance.
  5. Saves the trained model to ml/model.joblib.

The point is not to beat the rule engine (the labels come from the rules), but
to practise a full supervised-learning pipeline on real data and to lay the
groundwork for richer labels later (e.g. real incident logs from the vessel).

Run:
    python ml/train_model.py
Requires: scikit-learn, pandas, joblib  (see requirements.txt)
"""

from __future__ import annotations

import datetime as dt
import json
import os
import sys
import urllib.parse
import urllib.request

# Allow "import config" when run from the project root.
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import config  # noqa: E402

ARCHIVE_URL = "https://archive-api.open-meteo.com/v1/archive"


def download_history(years: int = 3) -> dict:
    """Download daily historical weather aggregates for São Luís."""
    end = dt.date.today() - dt.timedelta(days=5)  # archive lags a few days
    start = end - dt.timedelta(days=365 * years)
    params = {
        "latitude": config.WEATHER_LAT,
        "longitude": config.WEATHER_LON,
        "start_date": start.isoformat(),
        "end_date": end.isoformat(),
        "daily": "wind_speed_10m_max,wind_gusts_10m_max,precipitation_sum,"
                 "shortwave_radiation_sum",
        "wind_speed_unit": "kmh",
        "timezone": config.TIMEZONE,
    }
    url = f"{ARCHIVE_URL}?{urllib.parse.urlencode(params)}"
    with urllib.request.urlopen(url, timeout=60) as resp:
        return json.load(resp)


def build_dataset():
    """Return a pandas DataFrame of daily features plus a 'risky' label."""
    import pandas as pd

    raw = download_history()["daily"]
    df = pd.DataFrame(raw)
    df = df.rename(
        columns={
            "wind_speed_10m_max": "wind_speed_kmh",
            "wind_gusts_10m_max": "wind_gusts_kmh",
            "precipitation_sum": "precipitation_mm",
            "shortwave_radiation_sum": "radiation",
        }
    )
    df = df.dropna()

    # Label: a day is "risky" if it would trip an amber/red rule.
    t = config.THRESHOLDS
    df["risky"] = (
        (df["wind_gusts_kmh"] >= t["wind_gusts_kmh"]["amber"])
        | (df["wind_speed_kmh"] >= t["wind_speed_kmh"]["amber"])
        | (df["precipitation_mm"] >= t["precipitation_mm"]["amber"])
    ).astype(int)
    return df


def train():
    from joblib import dump
    from sklearn.ensemble import RandomForestClassifier
    from sklearn.metrics import classification_report
    from sklearn.model_selection import train_test_split

    df = build_dataset()
    features = ["wind_speed_kmh", "wind_gusts_kmh", "precipitation_mm", "radiation"]
    x, y = df[features], df["risky"]

    print(f"Dataset: {len(df)} dias | dias de risco: {int(y.sum())} "
          f"({100 * y.mean():.1f}%)")

    x_train, x_test, y_train, y_test = train_test_split(
        x, y, test_size=0.25, random_state=42, stratify=y
    )
    model = RandomForestClassifier(n_estimators=200, random_state=42, class_weight="balanced")
    model.fit(x_train, y_train)

    print("\n--- Avaliação no conjunto de teste ---")
    print(classification_report(y_test, model.predict(x_test), digits=3))

    print("--- Importância das variáveis ---")
    for name, imp in sorted(zip(features, model.feature_importances_),
                            key=lambda p: -p[1]):
        print(f"  {name:18s} {imp:.3f}")

    out = os.path.join(os.path.dirname(os.path.abspath(__file__)), "model.joblib")
    dump({"model": model, "features": features}, out)
    print(f"\nModelo salvo em: {out}")


if __name__ == "__main__":
    train()
