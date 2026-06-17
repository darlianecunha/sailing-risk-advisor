"""Entry point: fetch the forecast, assess risk, print and export the result.

Usage:
    python main.py            # console table + HTML report
    python main.py --json     # also print the assessment as JSON
"""

from __future__ import annotations

import argparse
import json
import os

from src import fetch, report, risk


def run(export_json: bool = False) -> list[dict]:
    days = fetch.daily_summary()
    assessed = risk.assess(days)

    print(report.to_console(assessed))

    out_dir = os.path.join(os.path.dirname(__file__), "output")
    os.makedirs(out_dir, exist_ok=True)
    html_path = os.path.join(out_dir, "navegabilidade.html")
    report.to_html(assessed, html_path)
    print(f"\nRelatório HTML salvo em: {html_path}")

    if export_json:
        print("\n" + json.dumps(assessed, ensure_ascii=False, indent=2))
    return assessed


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Sailing advisor for São Marcos Bay (São Luís).")
    parser.add_argument("--json", action="store_true", help="also print JSON output")
    args = parser.parse_args()
    run(export_json=args.json)
