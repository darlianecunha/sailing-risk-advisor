"""Vercel serverless entry point: serves the live navigability dashboard.

Vercel's Python runtime looks for a top-level WSGI/ASGI app called ``app``.
This Flask app fetches the latest forecast on each request, runs the risk
engine, and returns the HTML report. The command-line tool (main.py) is
unaffected; this file is only used for the web deployment.
"""

import os
import sys

# Make the project root importable (config.py and the src package live there).
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from flask import Flask  # noqa: E402

from src import fetch, report, risk  # noqa: E402

app = Flask(__name__)


@app.route("/")
def index():
    try:
        periods = risk.assess(fetch.period_summary())
        return report.build_html(periods)
    except Exception as exc:  # keep the page from 500-ing on an API hiccup
        return (
            f"<h1>Indisponível no momento</h1><p>Não foi possível obter a "
            f"previsão agora. Tente recarregar em instantes.</p><pre>{exc}</pre>",
            503,
        )
