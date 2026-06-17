# São Marcos Bay Sailing Advisor ⚓

A go/no-go decision tool for navigation in São Marcos Bay (Baía de São Marcos),
São Luís, Maranhão, Brazil. It pulls the marine and weather forecast for the
next seven days, splits each day into **three periods — morning, afternoon and
night (manhã / tarde / noite)** — scores each period against configurable safety
thresholds, and produces a simple traffic-light recommendation:

| Light | Meaning |
|-------|---------|
| 🟢 Green | Safe to sail |
| 🟡 Amber | Borderline conditions, exercise caution |
| 🔴 Red | Do not sail |

Each recommendation comes with a plain-language reason (e.g. *"gusts 52 km/h
above 50"*, *"wave height 2.6 m above 2.5"*), so the output is explainable
rather than a black box.

## Why this project

It reframes a classic port climate-risk analysis (threat × exposure × critical
threshold) as a forward-looking, daily operational decision for one of Brazil's
most weather-exposed bays. The risk logic is original; the weather data comes
from the free, public [Open-Meteo](https://open-meteo.com/) APIs, which the tool
only consumes.

## How it works

```
Open-Meteo forecast  ──►  daily extremes  ──►  threshold rules  ──►  🟢🟡🔴 + reasons
 (weather + marine)        (src/fetch.py)      (src/risk.py)        (src/report.py)
```

- **Weather endpoint** – wind speed, wind gusts, precipitation, visibility (fog).
- **Marine endpoint** – significant wave height and wave period.

Hourly values are aggregated into daily worst-case figures, compared against the
amber/red limits in `config.py`, and the worst level triggered on a given day
becomes that day's overall recommendation.

## Quick start

The core advisor uses only the Python standard library:

```bash
python main.py            # console table + HTML report in output/
python main.py --json     # also print the assessment as JSON
```

The HTML report (`output/navegabilidade.html`) is a self-contained dashboard you
can open in any browser.

## Live deployment (Vercel)

The repository ships with a thin web layer so the dashboard can be hosted live:

- `api/index.py` — a Flask app (the `app` object Vercel's Python runtime needs)
  that fetches the forecast on each request and returns the HTML dashboard.
- `vercel.json` — routes every request to that function.
- `requirements.txt` — declares Flask, the only runtime dependency.

Import the GitHub repository into Vercel and deploy; no build configuration is
required. The command-line tool (`main.py`) is independent and is not used by
the deployment.

## Configuration

All thresholds and coordinates live in `config.py`. The defaults are a
conservative starting point loosely informed by the ANTAQ critical-threshold
report for Brazilian ports. **They should be calibrated to the operating limits
of the vessel in use.**

```python
THRESHOLDS = {
    "wind_gusts_kmh":   {"amber": 35.0, "red": 50.0},
    "wave_height_m":    {"amber": 1.5,  "red": 2.5},
    "precipitation_mm": {"amber": 20.0, "red": 50.0},
    "visibility_km":    {"amber": 5.0,  "red": 2.0},   # lower is worse
    ...
}
```

## Optional: machine-learning module

`ml/train_model.py` is a practice pipeline that downloads ~3 years of historical
weather from the Open-Meteo Archive, builds daily features, labels risky days,
and trains a RandomForest classifier:

```bash
pip install -r ml/requirements.txt
python ml/train_model.py
```

It reports accuracy and feature importance and saves the model to
`ml/model.joblib`. In its current form the labels are derived from the rules, so
the classifier learns to reproduce them; the value is the end-to-end ML workflow
and the foundation it provides for richer labels later (e.g. real incident logs
from the bay).

## Project structure

```
sao-marcos-sailing-advisor/
├── main.py              # command-line entry point
├── config.py            # location + safety thresholds
├── src/
│   ├── fetch.py         # Open-Meteo data collection, aggregated per period
│   ├── risk.py          # threshold rules → traffic light
│   └── report.py        # console + HTML output
├── api/
│   └── index.py         # Flask app for the live (Vercel) dashboard
├── ml/
│   ├── train_model.py   # optional RandomForest practice pipeline
│   └── requirements.txt # ML-only dependencies
├── vercel.json          # deployment routing
├── requirements.txt     # web runtime dependency (Flask)
├── LICENSE              # MIT
└── README.md
```

## Roadmap ideas

- Calibrate thresholds with real operating limits for the bay.
- Add tide and storm-surge data for São Marcos Bay.
- Replace rule-based labels with a log of real incidents to train a genuine
  predictive model.
- Wrap the output in a Streamlit dashboard.

## Disclaimer

This is a decision-support tool. It does not replace professional navigational
judgement or official bulletins from the Brazilian Navy (Marinha do Brasil).

## Author

**Darliane Ribeiro Cunha, PhD** — research on sustainability governance,
maritime decarbonisation and environmental analytics.

## Licence

MIT — see [LICENSE](LICENSE).
