"""Output: console table and a self-contained HTML report."""

from __future__ import annotations

import datetime as dt


def to_console(days: list[dict]) -> str:
    """Build a readable console table of the 7-day outlook."""
    lines = []
    lines.append("=" * 64)
    lines.append("  NAVIO ESCOLA - PREVISÃO DE NAVEGABILIDADE (São Luís/MA)")
    lines.append("=" * 64)
    for d in days:
        date = dt.date.fromisoformat(d["date"]).strftime("%d/%m (%a)")
        lines.append(f"\n{d['emoji']}  {date}  ->  {d['label'].upper()}")
        for r in d["reasons"]:
            lines.append(f"      - {r}")
    lines.append("\n" + "=" * 64)
    return "\n".join(lines)


def build_html(days: list[dict]) -> str:
    """Return a self-contained HTML report as a string."""
    colours = {"GREEN": "#1a9850", "AMBER": "#f0a500", "RED": "#d73027"}
    cards = []
    for d in days:
        date = dt.date.fromisoformat(d["date"]).strftime("%d/%m")
        weekday = dt.date.fromisoformat(d["date"]).strftime("%A")
        reasons = "".join(f"<li>{r}</li>" for r in d["reasons"])
        wave = "-" if d["wave_height_m"] is None else f"{d['wave_height_m']:.1f} m"
        vis = "-" if d["visibility_km"] is None else f"{d['visibility_km']:.0f} km"
        cards.append(
            f"""
            <div class="card" style="border-top:6px solid {colours[d['level']]}">
              <div class="date">{date}<span>{weekday}</span></div>
              <div class="status" style="color:{colours[d['level']]}">
                {d['emoji']} {d['label']}
              </div>
              <ul class="reasons">{reasons}</ul>
              <div class="metrics">
                <span>Rajadas {d['wind_gusts_kmh']:.0f} km/h</span>
                <span>Onda {wave}</span>
                <span>Chuva {d['precipitation_mm']:.0f} mm</span>
                <span>Visib. {vis}</span>
              </div>
            </div>"""
        )

    generated = dt.datetime.now().strftime("%d/%m/%Y %H:%M")
    html = f"""<!DOCTYPE html>
<html lang="pt-BR">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Navio Escola - Navegabilidade São Luís</title>
<style>
  * {{ box-sizing: border-box; }}
  body {{ font-family: system-ui, sans-serif; margin: 0; background:#f5f7fa; color:#1f2937; }}
  header {{ background:#0b3d5c; color:#fff; padding:24px 20px; }}
  header h1 {{ margin:0; font-size:20px; }}
  header p {{ margin:6px 0 0; opacity:.85; font-size:13px; }}
  .grid {{ display:grid; gap:14px; padding:20px;
           grid-template-columns:repeat(auto-fill,minmax(220px,1fr)); }}
  .card {{ background:#fff; border-radius:10px; padding:16px;
           box-shadow:0 1px 4px rgba(0,0,0,.08); }}
  .date {{ font-size:18px; font-weight:700; }}
  .date span {{ display:block; font-size:12px; font-weight:400; color:#6b7280; text-transform:capitalize; }}
  .status {{ font-size:16px; font-weight:700; margin:10px 0; }}
  .reasons {{ font-size:12px; color:#374151; padding-left:16px; margin:8px 0; }}
  .reasons li {{ margin:2px 0; }}
  .metrics {{ display:flex; flex-wrap:wrap; gap:6px; margin-top:10px; }}
  .metrics span {{ font-size:11px; background:#eef2f7; padding:3px 8px; border-radius:6px; }}
  footer {{ padding:10px 20px 30px; font-size:11px; color:#6b7280; }}
</style>
</head>
<body>
<header>
  <h1>Navio Escola · Previsão de navegabilidade · São Luís (MA)</h1>
  <p>Baía de São Marcos · gerado em {generated} · fonte: Open-Meteo</p>
</header>
<div class="grid">{''.join(cards)}</div>
<footer>
  Semáforo baseado em limiares de segurança configuráveis (vento, onda, chuva, visibilidade).
  Ferramenta de apoio à decisão; não substitui avaliação do comandante nem boletins oficiais da Marinha.
</footer>
</body>
</html>"""
    return html


def to_html(days: list[dict], path: str) -> None:
    """Write a self-contained HTML report to ``path``."""
    with open(path, "w", encoding="utf-8") as f:
        f.write(build_html(days))
