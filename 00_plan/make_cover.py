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
    3: dict(
        phase=1,
        title=["Installing Polars:", "the choices nobody mentions"],
        points=["Reproducible setup with uv and a lock file",
                "Extras, builds and pl.show_versions()",
                "Engines: in-memory, streaming, GPU, and auto",
                "Spilling to disk when RAM runs out"],
        apis=["pl.show_versions()", "pl.thread_pool_size()", "collect(engine=)", "pl.Config"],
    ),
    4: dict(
        phase=1,
        title=["Series and DataFrame:", "strict types, no index"],
        points=["One column, one type: no silent object columns",
                "Nulls for every type, even integers",
                "The schema is the contract",
                "No index: what replaces .loc and alignment"],
        apis=["pl.Series", "pl.DataFrame", ".schema", ".glimpse()"],
    ),
    5: dict(
        phase=1,
        title=["read vs scan:", "the choice before any code runs"],
        points=["read_csv is just scan_csv + collect",
                "Fix types at read time: zip codes, dates",
                "Parquet: 3x smaller, 4.6x faster to read",
                "Pushdown: 3 of 8 columns read, filter in the scan"],
        apis=["pl.read_csv", "pl.scan_parquet", "schema_overrides", ".explain()"],
    ),
    6: dict(
        phase=1,
        title=["The four contexts where", "every expression lives"],
        points=["select: choose and compute columns",
                "with_columns: add columns, keep everything",
                "filter: keep rows (never adds columns)",
                "group_by().agg(): one row per group"],
        apis=[".select()", ".with_columns()", ".filter()", ".group_by().agg()"],
    ),
    7: dict(
        phase=1,
        title=["Eager vs lazy", "in one picture"],
        points=["Same query, two words changed",
                "Projection pushdown: 4 of 8 columns read",
                "Predicate pushdown: filter moved into the scan",
                "Lazy streaming 2x faster; row order not promised"],
        apis=["pl.scan_csv", ".explain()", ".collect()", ".lazy()"],
    ),
    9: dict(
        phase=2,
        title=["What an expression", "really is"],
        points=["A recipe for a column: no data, no work",
                "One expression, four contexts, four shapes",
                "Build big expressions from small ones",
                "Strings are column names: use pl.lit"],
        apis=["pl.col", "pl.lit", ".meta"],
    ),
    10: dict(
        phase=2,
        title=["Selecting columns:", "names, regex, dtypes"],
        points=["One pl.col, three kinds of input",
                "Regex only inside ^...$",
                "Every datetime column in one line",
                "Chain once, apply to every match"],
        apis=['pl.col("a", "b")', 'pl.col("^x_.*$")', "pl.col(pl.Int64)"],
    ),
    11: dict(
        phase=2,
        title=["Column selectors:", "set logic for columns"],
        points=["Pick by dtype, name or position",
                "Combine with |, &, - and ~",
                "Works in select, drop and agg",
                "Polars 2.0: no more pl.col coercion"],
        apis=["cs.numeric()", "cs.ends_with()", "cs.by_name()", "expand_selector"],
    ),
    12: dict(
        phase=2,
        title=["Arithmetic, comparison", "and boolean logic"],
        points=["Operators on whole columns, in Rust",
                "Booleans sum to counts, mean to shares",
                "Trap: & binds tighter than >",
                "Trap: != silently drops nulls"],
        apis=["&  |  ~", ".is_between()", ".is_in()", "any_horizontal"],
    ),
    13: dict(
        phase=2,
        title=["Conditional logic:", "when / then / otherwise"],
        points=["CASE WHEN as one expression",
                "Top to bottom, first match wins",
                "Strings in then() are column names",
                "Lookups: replace_strict instead"],
        apis=["pl.when()", ".then()", ".otherwise()", "replace_strict"],
    ),
    14: dict(
        phase=2,
        title=["Expression expansion:", "one expression, many columns"],
        points=["pl.col(a, b).sum() is two expressions",
                "Profile a whole table in one line",
                "Down columns vs across rows",
                "Why expansion causes DuplicateError"],
        apis=["pl.all()", ".exclude()", "sum_horizontal", "has_multiple_outputs"],
    ),
    15: dict(
        phase=2,
        title=["Naming outputs:", "alias, suffix, map"],
        points=["Default name: the leftmost column",
                "One rule for many columns",
                "Fix a typo in every column name at once",
                "with_columns overwrites without warning"],
        apis=[".alias()", ".name.suffix()", ".name.map()", ".name.keep()"],
    ),
    16: dict(
        phase=2,
        title=["Casting:", "strict vs non-strict"],
        points=["Strict by default: one bad value fails",
                "strict=False: failures become nulls",
                "Find the rows a cast threw away",
                "Polars 2.0: str.to_date, not cast"],
        apis=[".cast()", "strict=False", "wrap_numerical", "str.to_datetime"],
    ),
    17: dict(
        phase=2,
        title=["Nulls:", "fill, drop, detect"],
        points=["One null for every dtype",
                "Read what a null means first",
                "len() counts rows, count() non-nulls",
                "!= filters drop missing rows"],
        apis=[".fill_null()", "pl.coalesce", ".drop_nulls()", ".ne_missing()"],
    ),
    18: dict(
        phase=2,
        title=["Filtering inside", "aggregations"],
        points=["filter as an expression, not a context",
                "5 conditional totals, one group_by",
                "Row-wise checks with sum_horizontal",
                "filter vs when: same sum, other mean"],
        apis=[".filter() in agg", "sum_horizontal", ".n_unique()"],
    ),
    19: dict(
        phase=2,
        title=["Sorting and top-k"],
        points=["Sort rows, sort within groups, or top-k",
                "Top product per order with sort_by",
                "Top 3 per seller without a full sort",
                "Trap: Expr.sort breaks row alignment"],
        apis=[".sort()", ".sort_by()", ".top_k()", ".top_k_by()"],
    ),
    20: dict(
        phase=2,
        title=["Uniques and duplicates"],
        points=["Check a key before you trust it",
                "customer_id is not the customer",
                "Keep the latest row, deliberately",
                "Default keep=\"any\" is not stable"],
        apis=[".n_unique()", ".is_duplicated()", ".unique(keep=)", ".value_counts()"],
    ),
    21: dict(
        phase=2,
        title=["Reusable expression", "functions"],
        points=["Functions that return pl.Expr",
                "Pipelines of named steps with pipe",
                "Metrics as a dict of expressions",
                "Test the logic on a 4-row frame"],
        apis=["-> pl.Expr", "DataFrame.pipe", "Expr.pipe", "assert_frame_equal"],
    ),
    22: dict(
        phase=2,
        title=["Why map_elements", "is the last resort"],
        points=["Python per value: no cores, no optimizer",
                "3 tasks, native vs map_elements",
                "Polars warns you, for free",
                "A 5-step ladder before you reach for it"],
        apis=[".map_elements()", ".map_batches()", "str.normalize"],
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
