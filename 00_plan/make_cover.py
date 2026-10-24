"""Generate Medium cover images for 100 Days of Polars.

Usage:  python 00_plan/make_cover.py 0 1        # writes assets/day_NNN/cover.svg
Add a new entry to COVERS for each post. PNG export: see render_png() or open the
SVG in a browser and screenshot at 1400x788.
"""
from html import escape
from pathlib import Path
import sys

W, H = 1400, 788
INK, MUTED, LINE, FILL, ACCENT, ACCENT_SOFT = "#1f2328", "#57606a", "#d0d7de", "#eaeef2", "#0b6bcb", "#dbeafe"

PHASES = {
    0: "Series intro", 1: "Foundations", 2: "Expressions", 3: "Data types",
    4: "Aggregation and windows", 5: "Joins and combining", 6: "Lazy engine and optimizer",
    7: "IO at scale", 8: "Performance and internals", 9: "Production pipelines",
    10: "Migration and extending",
}

COVERS = {
    0: dict(
        phase=0,
        title=["100 Days of Polars:", "the plan"],
        points=["10 phases, from foundations to production",
                "Real data: Olist e-commerce, then NYC taxi",
                "One idea per post, runnable code on GitHub",
                "3–4 posts a week, with a live series index"],
        chips_label="CORE IDEAS",
        apis=["expressions", "lazy plans", "Arrow memory", "streaming"],
    ),
    1: dict(
        phase=1,
        title=["Why Polars exists:", "where pandas hurts at scale"],
        points=["Load 9 CSVs: 12.9x faster",
                "4-table query: 3.4x faster",
                "Same query, lazy: 8.5x faster than pandas",
                "4 design choices behind the speed"],
        apis=["pl.read_csv", "pl.scan_csv", ".collect()"],
    ),
    2: dict(
        phase=1,
        title=["Arrow columnar memory:", "why Polars is fast"],
        points=["Text column: 5.90 MB as objects, 1.82 MB in Arrow",
                "Pointers vs buffers, in plain words",
                "3 buffers: validity bitmap, offsets, data",
                "Chunks: why vstack gave me 57"],
        apis=[".to_arrow()", ".estimated_size()", ".n_chunks()", ".rechunk()"],
    ),
}


def t(x, y, s, size, weight=400, fill=INK, anchor="start", spacing=0, family=None):
    fam = f" font-family='{family}'" if family else ""
    ls = f" letter-spacing='{spacing}'" if spacing else ""
    return (f"<text x='{x}' y='{y}' font-size='{size}' font-weight='{weight}' fill='{fill}' "
            f"text-anchor='{anchor}'{ls}{fam}>{escape(s)}</text>")


def cover(day: int) -> str:
    c = COVERS[day]
    o = [f"<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 {W} {H}' width='{W}' height='{H}' "
         f"font-family='Inter, Segoe UI, Helvetica, Arial, sans-serif' role='img' "
         f"aria-label='100 Days of Polars, Day {day}: {escape(' '.join(c['title']))}'>",
         f"<rect width='{W}' height='{H}' fill='#ffffff'/>",
         f"<rect width='{W}' height='10' fill='{ACCENT}'/>"]

    # header: series name (left), phase (right)
    o.append(t(80, 92, "100 DAYS OF POLARS", 22, 700, ACCENT, spacing=3))
    ph = c["phase"]
    o.append(t(W - 80, 92, PHASES[ph] if ph == 0 else f"Phase {ph} · {PHASES[ph]}", 22, 500, MUTED, "end"))

    # day block
    o.append(f"<rect x='80' y='140' width='220' height='220' rx='20' fill='{ACCENT}'/>")
    o.append(t(190, 200, "DAY", 26, 600, "#ffffff", "middle", spacing=4))
    o.append(t(190, 322, f"{day:02d}", 120, 800, "#ffffff", "middle"))

    # title
    for i, line in enumerate(c["title"]):
        o.append(t(350, 222 + i * 70, line, 58, 750, INK))

    # topics
    y0 = 450
    for i, p in enumerate(c["points"]):
        y = y0 + i * 56
        o.append(f"<rect x='80' y='{y - 22}' width='8' height='30' rx='2' fill='{ACCENT}'/>")
        o.append(t(110, y, p, 30, 500, INK))

    # API chips (right column)
    o.append(t(W - 80, y0 - 4, c.get("chips_label", "APIs IN THIS POST"), 16, 700, MUTED, "end", spacing=2))
    y = y0 + 30
    for a in c["apis"]:
        w = 24 + 15.6 * len(a)
        o.append(f"<rect x='{W - 80 - w}' y='{y - 28}' width='{w}' height='42' rx='21' "
                 f"fill='{ACCENT_SOFT}'/>")
        o.append(t(W - 80 - w / 2, y + 1, a, 24, 500, ACCENT, "middle",
                   family="JetBrains Mono, Consolas, DejaVu Sans Mono, monospace"))
        y += 56

    # footer: 100-day progress strip + repo
    fy = H - 92
    cw, gap = 10.0, 2.4
    for i in range(100):
        x = 80 + i * (cw + gap)
        done = i < day
        o.append(f"<rect x='{x:.1f}' y='{fy}' width='{cw}' height='18' rx='2' "
                 f"fill='{ACCENT if done else FILL}'/>")
    o.append(t(80, fy + 52, f"{day} / 100", 18, 600, MUTED))
    o.append(t(W - 80, fy + 52, "github.com/double-espresso-data/100-days-of-polars", 18, 500, MUTED, "end"))
    o.append("</svg>")
    return "".join(o)


if __name__ == "__main__":
    root = Path(__file__).resolve().parent.parent
    for d in map(int, sys.argv[1:] or COVERS):
        out = root / "assets" / f"day_{d:03d}" / "cover.svg"
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(cover(d), encoding="utf-8")
        print("wrote", out)
