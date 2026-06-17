"""Output: console table and a self-contained HTML report.

Records are per (day, period). Both renderers group the periods under their day
so each day shows a manhã / tarde / noite traffic light.
"""

from __future__ import annotations

import datetime as dt
from itertools import groupby


def _by_day(periods: list[dict]):
    """Yield (date, [period records]) preserving input order."""
    for date, group in groupby(periods, key=lambda r: r["date"]):
        yield date, list(group)


def to_console(periods: list[dict]) -> str:
    """Build a readable console table grouped by day and period."""
    lines = []
    lines.append("=" * 66)
    lines.append("  PREVISÃO DE NAVEGABILIDADE - BAÍA DE SÃO MARCOS (São Luís/MA)")
    lines.append("  Por período: manhã / tarde / noite")
    lines.append("=" * 66)
    for date, day in _by_day(periods):
        nice = dt.date.fromisoformat(date).strftime("%d/%m (%a)")
        lines.append(f"\n{nice}")
        for p in day:
            lines.append(f"  {p['emoji']}  {p['period_label']:<6} → {p['label'].upper()}")
            for r in p["reasons"]:
                lines.append(f"        - {r}")
    lines.append("\n" + "=" * 66)
    return "\n".join(lines)


def build_html(periods: list[dict]) -> str:
    """Return a self-contained HTML report as a string."""
    colours = {"GREEN": "#1a9850", "AMBER": "#f0a500", "RED": "#d73027"}

    cards = []
    for date, day in _by_day(periods):
        d = dt.date.fromisoformat(date).strftime("%d/%m")
        weekday = dt.date.fromisoformat(date).strftime("%A")

        rows = []
        for p in day:
            reasons = "".join(f"<li>{r}</li>" for r in p["reasons"])
            wave = "-" if p["wave_height_m"] is None else f"{p['wave_height_m']:.1f} m"
            vis = "-" if p["visibility_km"] is None else f"{p['visibility_km']:.0f} km"
            rows.append(
                f"""
                <div class="period" style="border-left:5px solid {colours[p['level']]}">
                  <div class="phead">
                    <span class="pname">{p['period_label']}</span>
                    <span class="pstatus" style="color:{colours[p['level']]}">{p['emoji']} {p['label']}</span>
                  </div>
                  <ul class="reasons">{reasons}</ul>
                  <div class="metrics">
                    <span>Rajadas {p['wind_gusts_kmh']:.0f} km/h</span>
                    <span>Onda {wave}</span>
                    <span>Chuva {p['precipitation_mm']:.0f} mm</span>
                    <span>Visib. {vis}</span>
                  </div>
                </div>"""
            )

        cards.append(
            f"""
            <div class="card">
              <div class="date">{d}<span>{weekday}</span></div>
              {''.join(rows)}
            </div>"""
        )

    generated = dt.datetime.now().strftime("%d/%m/%Y %H:%M")
    html = f"""<!DOCTYPE html>
<html lang="pt-BR">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Navegabilidade - Baía de São Marcos</title>
<style>
  * {{ box-sizing: border-box; }}
  body {{ font-family: system-ui, sans-serif; margin: 0; background:#f5f7fa; color:#1f2937; }}
  header {{ background:#0b3d5c; color:#fff; padding:24px 20px; }}
  header h1 {{ margin:0; font-size:20px; }}
  header p {{ margin:6px 0 0; opacity:.85; font-size:13px; }}
  .grid {{ display:grid; gap:14px; padding:20px;
           grid-template-columns:repeat(auto-fill,minmax(250px,1fr)); }}
  .card {{ background:#fff; border-radius:10px; padding:16px;
           box-shadow:0 1px 4px rgba(0,0,0,.08); }}
  .date {{ font-size:18px; font-weight:700; margin-bottom:10px; }}
  .date span {{ display:block; font-size:12px; font-weight:400; color:#6b7280; text-transform:capitalize; }}
  .period {{ padding:8px 10px; margin:8px 0; background:#fafbfc; border-radius:6px; }}
  .phead {{ display:flex; justify-content:space-between; align-items:center; }}
  .pname {{ font-weight:700; font-size:14px; }}
  .pstatus {{ font-size:13px; font-weight:700; }}
  .reasons {{ font-size:11px; color:#374151; padding-left:16px; margin:6px 0; }}
  .reasons li {{ margin:1px 0; }}
  .metrics {{ display:flex; flex-wrap:wrap; gap:5px; margin-top:6px; }}
  .metrics span {{ font-size:10px; background:#eef2f7; padding:2px 7px; border-radius:6px; }}
  footer {{ padding:10px 20px 30px; font-size:11px; color:#6b7280; }}
</style>
</head>
<body>
<header>
  <h1>Previsão de navegabilidade · Baía de São Marcos · São Luís (MA)</h1>
  <p>Por período (manhã / tarde / noite) · gerado em {generated} · fonte: Open-Meteo</p>
</header>
<div class="grid">{''.join(cards)}</div>
<footer>
  Semáforo por período baseado em limiares de segurança configuráveis (vento, onda, chuva, visibilidade).
  Ferramenta de apoio à decisão; não substitui avaliação de navegação nem boletins oficiais da Marinha.
</footer>
</body>
</html>"""
    return html


def to_html(periods: list[dict], path: str) -> None:
    """Write a self-contained HTML report to ``path``."""
    with open(path, "w", encoding="utf-8") as f:
        f.write(build_html(periods))
